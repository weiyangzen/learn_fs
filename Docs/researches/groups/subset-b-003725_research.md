# subset-b-003725 Research

Grouped research for the listed Radeon R600 driver files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r600_cs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r600_cs.c

## Purpose

`r600_cs.c` validates and relocates user-submitted command streams for R600/R700 Radeon GPUs. It protects privileged GPU state by allowing only safe register writes, rewrites addresses through GEM/TTM relocation objects, validates color/depth/texture/streamout resource bounds, and parses both 3D PM4 packets and the R6xx/R7xx DMA command-stream format used by the CS ioctl. This file is a major security boundary between userspace drivers and hardware.

## Important APIs, Types, and Functions

- `struct r600_cs_track`: transient parser state for render targets, depth buffer, htile, streamout buffers, sample count, tiling geometry, and dirty flags. It mirrors enough GPU state to validate a draw packet when it appears.
- `color_formats_table` and helpers `r600_fmt_is_valid_color`, `r600_fmt_is_valid_texture`, `r600_fmt_get_blocksize`, `r600_fmt_get_nblocksx`, and `r600_fmt_get_nblocksy`: central format metadata used by render-target and texture bounds checks.
- `r600_get_array_mode_alignment`: derives pitch, height, depth, and base-address alignment requirements for linear, 1D tiled, and 2D tiled layouts using group size, banks, pipes, samples, and block size.
- `r600_cs_track_init`, `r600_cs_track_validate_cb`, `r600_cs_track_validate_db`, and `r600_cs_track_check`: initialize tracking defaults, validate color buffers, validate depth/htile state, and perform deferred validation before draw packets.
- `r600_cs_common_vline_parse`: handles the userspace VLINE wait sequence, maps a CRTC id relocation to the correct vline registers, and nops waits for disabled CRTCs.
- `r600_cs_check_reg` and `r600_is_safe_reg`: enforce the `r600_reg_safe_bm` allow/deny bitmap and implement special relocation/validation behavior for registers that reference BOs or tracked state.
- `r600_check_texture_resource` and `r600_texture_size`: validate texture resource descriptors, tiling-derived alignment, mip sizing, array/cube/MSAA dimensions, and base/mipmap BO bounds.
- `r600_packet3_check`: validates PM4 packet opcodes, packet counts, address relocations, register ranges, draw-time tracked state, CP DMA, events, waits, streamout updates, memory writes, copies, resources, samplers, and constants.
- `r600_cs_parse`: public 3D command-stream parser entry point. It allocates the tracker, walks all IB packets, dispatches by packet type, and frees the tracker on success or error.
- `r600_dma_cs_next_reloc` and `r600_dma_cs_parse`: parse R6xx/R7xx DMA IBs submitted through CS, consume relocations, rewrite packet addresses, and validate copy/write/fill bounds.

## Control Flow

For 3D CS parsing, `r600_cs_parse` creates `struct r600_cs_track`, fills ASIC tiling parameters from `rdev->config`, then loops until `p->idx` reaches `p->chunk_ib->length_dw`. Packet0 is restricted almost entirely to the special VLINE sequence; packet2 is a no-op; packet3 is delegated to `r600_packet3_check`. Any parser error frees `p->track` and returns an errno.

Most state validation is deferred. Register-setting packets update `r600_cs_track` fields and mark `cb_dirty`, `db_dirty`, or `streamout_dirty`. Draw packets call `r600_cs_track_check`, which verifies enabled streamout buffers, skips CB/DB checks when `SX_MISC` kills all primitives, verifies every enabled render target has a BO and valid geometry, and validates depth/htile state when z/stencil is active. CB validation computes pitch and height from `CB_COLOR*_SIZE`, derives alignment from array mode, validates base/frag/tile BO offsets, checks FMASK/CMASK sizes when tile modes require them, and can rewrite `CB_COLOR*_SIZE` in the IB. DB validation similarly validates format, base alignment, tile count, views, and htile surface size.

Register handling is relocation-heavy. For render-target, depth, streamout, shader, const-cache, and coherency base registers, `r600_cs_check_reg` consumes the next relocation and adds the BO GPU offset into the IB field. When userspace does not request `RADEON_CS_KEEP_TILING_FLAGS`, CB/DB/texture array modes are overwritten from BO tiling flags. Legacy compatibility paths reuse the last color base for old userspace that did not emit separate FMASK/CMASK relocations.

Texture resource packets are validated descriptor-by-descriptor. Valid texture resources consume base and mip relocations, optionally patch tile mode from tiling flags, validate format and dimension, compute mip/layer/face byte sizes, and patch descriptor base fields. Buffer resources consume one relocation and clamp an oversized VBO size to the BO size in KMS mode.

The DMA CS parser is a separate loop over DMA packet headers. It consumes relocations for write, copy, and constant-fill packets, rewrites tiled and linear address fields according to R600 versus RV770 packet layouts, advances `p->idx` by packet-specific lengths, and rejects BO bounds overflows or unsupported packet types.

## State and Persistence Behavior

Parser state is transient and lives only for one submitted IB. Persistent effects are limited to rewriting `p->ib.ptr` before the IB is scheduled and advancing parser relocation indices. Hardware state is not directly programmed here; the validated and patched IB later executes on the GPU. `r600_nomm` is a file-scope integer passed into relocation helpers for older no-memory-manager behavior.

The tracker stores kernel BO pointers and GPU offsets obtained from relocation chunks, but it is freed after parsing. Dirty flags prevent repeated validation of unchanged state while ensuring draw packets see all register writes that came before them. The code mutates submitted IB words for address relocation, tiling mode correction, depth/color size correction, VLINE register remapping, htile width/height forcing, and no-oping disabled CRTC waits.

## Dependencies and Integration Points

This file depends on the Radeon CS parser (`struct radeon_cs_parser`, `radeon_cs_packet_parse`, `radeon_cs_packet_next_reloc`, `radeon_get_ib_value`), BO metadata (`struct radeon_bo`, `struct radeon_bo_list`, `radeon_bo_size`, relocation tiling flags), DRM CRTC lookup for vline relocation, ASIC family/config values, packet/register definitions from `r600.h` and `r600d.h`, and the safe-register bitmap in `r600_reg_safe.h`. It integrates with Mesa/UMD command submission, KMS relocation validation, render and DMA rings, and display vblank waiting.

## Risks and Edge Cases

- This is a security-sensitive parser. Missing bounds checks, incorrect safe-register bitmap semantics, or relocation count desynchronization can expose GPU memory or privileged registers.
- Many size computations use 32-bit `u32` temporaries for byte counts, tile counts, and mip sizes; malformed large descriptors should be considered overflow-sensitive.
- Several legacy compatibility paths intentionally allow or rewrite questionable userspace state, including linear CB oversizing and old FMASK/CMASK relocation omissions.
- The bitmap test names are easy to misread: `r600_cs_check_reg` treats a clear bit as safe, while set bits require special handling or rejection.
- `r600_check_texture_resource` warns but does not fail when `blevel > llevel`, and the mipmap BO-too-small check is effectively disabled by commented-out diagnostics.
- DMA packet parsing depends on exact packet length increments; a single malformed count/path mismatch can desynchronize parsing from later packets.
- VLINE parsing assumes a precise packet sequence and rewrites IB positions relative to that sequence.

## Test Signals

Useful signals include command-submission fuzzing with synthetic PM4/DMA IBs, IGT or DRM tests that submit legal and illegal register packets, Mesa workloads covering render targets, MSAA resolve, depth/htile, streamout, VBOs, textures, vline waits, CP DMA, and DMA copies, plus negative tests for missing relocations, oversized BO references, bad tiling, invalid formats, bad packet counts, and forbidden registers. Hardware smoke tests should cover R600, RV770/RV740, RS780/RS880, and no-writeback/legacy paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r600_cs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r600_dma.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r600_dma.c

## Purpose

`r600_dma.c` operates the asynchronous DMA engine present on R600 through Evergreen-era Radeon GPUs. It initializes and tears down the DMA ring, reads and writes hardware ring pointers, emits DMA fences and semaphores, schedules DMA indirect buffers, performs ring/IB self-tests, detects lockups, and implements the TTM copy callback used for BO moves.

## Important APIs, Types, and Functions

- `r600_dma_get_rptr`, `r600_dma_get_wptr`, and `r600_dma_set_wptr`: ring pointer callbacks for the Radeon ring framework, using writeback memory for RPTR when enabled and MMIO registers otherwise.
- `r600_dma_resume`, `r600_dma_stop`, and `r600_dma_fini`: lifecycle management for DMA registers, ring base, writeback address, IB enablement, ring readiness, and ring allocation cleanup.
- `r600_dma_is_lockup`: checks GPU soft-reset bits and delegates to generic Radeon ring lockup tracking.
- `r600_dma_ring_test` and `r600_dma_ib_test`: write a sentinel through the DMA engine and poll writeback memory to verify ring and IB execution.
- `r600_dma_fence_ring_emit` and `r600_dma_semaphore_ring_emit`: emit synchronization packets understood by the DMA ring.
- `r600_dma_ring_ib_execute`: writes an indirect-buffer packet, pads to the DMA ring alignment requirement, and optionally writes `next_rptr` into writeback memory.
- `r600_copy_dma`: copies GPU pages for TTM moves by emitting one or more DMA copy packets, synchronizing with a reservation object, and returning a fence.

## Control Flow

Resume starts by clearing semaphore timers, programming ring size, endian swap flags, RPTR/WPTR, writeback addresses, ring base, and DMA IB control. It disables context-empty interrupts, sets `DMA_MODE` on RV770+, zeros the software write pointer, enables `DMA_RB_ENABLE`, marks the ring ready, and immediately runs `radeon_ring_test`. If the test fails, readiness is cleared and the error is returned. If this DMA ring is the active copy engine, visible VRAM limits are relaxed to real VRAM size after successful startup and reduced again on stop.

Ring and IB tests both write `0xDEADBEEF` to writeback memory. The ring test emits a direct `DMA_PACKET_WRITE` into the ring and polls for up to `rdev->usec_timeout`. The IB test allocates a 256-byte IB, fills it with the same write packet, schedules it, waits for the IB fence, then polls the writeback slot.

IB execution has an R600-specific alignment rule: the indirect-buffer packet must end on an 8-DW boundary. The function pads with DMA NOPs until `ring->wptr & 7` equals 5, then emits the IB packet address and length. When writeback is enabled, it first emits a DMA write of the predicted next read pointer.

`r600_copy_dma` creates a `radeon_sync`, locks enough ring space for chunked copies plus fence overhead, syncs against the reservation object and other rings, emits copy packets of at most `0xFFFE` dwords, emits a fence, commits the ring, and attaches the fence to the sync object. Error paths undo the ring lock or free sync state.

## State and Persistence Behavior

Persistent state is held in `rdev->ring[R600_RING_TYPE_DMA_INDEX]`, DMA MMIO registers, writeback memory, and fence driver memory. `ring->ready` gates whether the engine is usable. `ring->wptr` is software state mirrored to `DMA_RB_WPTR`; `rptr` can be read from writeback or `DMA_RB_RPTR`. `r600_copy_dma` leaves a fence object representing copy completion and updates BO move synchronization through `radeon_sync_free`.

## Dependencies and Integration Points

The file integrates with the generic Radeon ring, fence, IB, sync, and TTM move infrastructure. It depends on DMA packet macros and register definitions from `r600.h`/`r600d.h`, writeback slots such as `R600_WB_DMA_RPTR_OFFSET`, reset detection from `r600_gpu_check_soft_reset`, and `radeon_ttm_set_active_vram_size` when DMA is selected as the copy engine. It is paired with the DMA CS parser in `r600_cs.c`, but this file emits trusted kernel packets rather than validating userspace packets.

## Risks and Edge Cases

- Startup success depends on the ring test; failure must leave `ring->ready` false to avoid later scheduling onto a dead engine.
- Writeback and no-writeback paths can diverge; RPTR behavior should be tested in both modes.
- IB alignment is hardware-specific and easy to regress if ring padding changes.
- Copy chunks are limited by a 16-bit packet count; page-count math must avoid undercounting large moves.
- Error paths in `r600_dma_ib_test` return after fence wait failures without freeing the IB in the negative/timeout branches in this snapshot, which is worth auditing.
- Endian swap flags are compile-time conditional and need big-endian coverage if that platform matters.

## Test Signals

Primary tests are ring startup/shutdown, direct ring writeback tests, DMA IB tests, BO move/copy stress, fence interrupt delivery, semaphore waits/signals across rings, suspend/resume, GPU reset/lockup recovery, and large VRAM/GTT move workloads that force multi-packet copies. Regression testing should include R600 and RV770-family packet layouts and both writeback-enabled and MMIO-RPTR modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r600_dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r600_dpm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r600_dpm.c

## Purpose

`r600_dpm.c` provides shared dynamic power-management helpers for R600-family Radeon ASICs. It prints PowerPlay classifications, computes display timing and transition thresholds, programs clock/voltage/power-level registers, starts and stops DPM, configures thermal interrupt ranges, parses AtomBIOS PowerPlay extension tables into Radeon runtime structures, and exposes PCIe capability helpers.

## Important APIs, Types, and Functions

- `r600_utc` and `r600_dtc`: default up/down trend-control arrays sized by `R600_PM_NUMBER_OF_TC`.
- Diagnostic helpers `r600_dpm_print_class_info`, `r600_dpm_print_cap_info`, and `r600_dpm_print_ps_status`: log PowerPlay state metadata.
- Display helpers `r600_dpm_get_vblank_time` and `r600_dpm_get_vrefresh`: inspect enabled CRTCs to derive vblank duration and refresh rate.
- Transition math helpers `r600_calculate_u_and_p` and `r600_calculate_at`: compute bitfield parameters for bias/threshold programming.
- Register wrappers such as `r600_dynamicpm_enable`, `r600_enable_sclk_control`, `r600_enable_mclk_control`, `r600_set_bsp`, `r600_set_at`, `r600_set_tc`, `r600_engine_clock_entry_*`, `r600_vid_rt_*`, `r600_voltage_control_*`, and `r600_power_level_*`: small, named writes to DPM control registers.
- `r600_start_dpm` and `r600_stop_dpm`: enable/disable the hardware dynamic power manager around clock-control and SPLL-bypass sequencing.
- `r600_dpm_late_enable`: enables internal thermal interrupts after IRQ installation.
- `r600_parse_extended_power_table` and `r600_free_extended_power_table`: ingest and release optional PowerPlay fan, dependency, leakage, VCE/UVD/SAMU/ACP/PPM/PowerTune data.
- `r600_get_platform_caps`, `r600_get_pcie_gen_support`, `r600_get_pcie_lane_support`, and `r600_encode_pci_lane_width`: expose firmware/platform capability interpretation.

## Control Flow

Most register helpers are direct read-modify-write wrappers. Higher-level start/stop flow disables software clock controls, enables global DPM, waits for vblank on both CRTCs, toggles SPLL bypass twice while polling `SPLL_CHG_STATUS`, then re-enables SCLK and MCLK control. Stop simply clears global DPM enable.

Thermal late enable checks whether IRQs are installed and whether the configured thermal sensor is an internal type. If so, it clamps the supported range to `R600_TEMP_RANGE_MIN` and `R600_TEMP_RANGE_MAX`, writes high/low/DPM thermal thresholds, records the range in `rdev->pm.dpm.thermal`, sets `rdev->irq.dpm_thermal`, and updates IRQ programming.

Power table parsing starts from AtomBIOS `PowerPlayInfo`. `r600_get_platform_caps` reads platform caps and response times. `r600_parse_extended_power_table` conditionally parses structures based on `usTableSize`, table format, and extended-header size. It fills fan control parameters, SCLK/MCLK/VDDC/VDDCI/MVDD dependency tables, DC clock-voltage limits, phase-shedding limits, TDP and CAC fields, leakage entries, and extended VCE/UVD/SAMU/PPM/ACP/PowerTune tables. Each table uses BIOS offsets relative to `data_offset` and converts little-endian fields into host-order Radeon structures.

Allocation failures trigger partial cleanup either by freeing specific earlier dependency arrays or by calling `r600_free_extended_power_table`. Normal teardown calls `r600_free_extended_power_table`, which frees every dynamically allocated dependency table and optional structure.

## State and Persistence Behavior

The file persists parsed BIOS data into `rdev->pm.dpm`, especially `platform_caps`, response times, fan settings, thermal thresholds, power-control limits, media clock states, and `dyn_state` dependency tables. Register helpers persist state directly in GPU MMIO registers. `r600_power_level_get_current_index` and `r600_power_level_get_target_index` read current hardware profile state. Allocated BIOS-derived tables remain until explicitly freed.

## Dependencies and Integration Points

Dependencies include `radeon_device`, DRM CRTC/mode structures, AtomBIOS table structures from `atom.h`, endian helpers, Radeon IRQ setup, Radeon mode info, and `r600d.h` register/bitfield macros. ASIC-specific DPM implementations call these shared helpers while building or switching power states. Display timing helpers integrate DPM decisions with active KMS CRTCs; video-state helpers classify UVD states; PCIe helpers feed link-speed/link-width selection.

## Risks and Edge Cases

- AtomBIOS offsets and table counts are trusted after limited size/header checks. Malformed BIOS data can point parsing beyond the image or create oversized allocations.
- Several hardware wait loops poll for up to `usec_timeout` but do not report timeout failure to callers.
- Partial allocation rollback is manual and nonuniform; newly added tables must be added to both failure cleanup and `r600_free_extended_power_table`.
- `r600_free_extended_power_table` frees pointers but does not null them or reset counts, so callers must avoid double-free or reuse after free.
- Thermal constants are marked with a comment questioning whether they are appropriate; wrong thresholds can affect reliability or fan behavior.
- Display helpers return the first enabled CRTC only, which may not reflect multi-display worst-case timing.
- Direct register wrappers assume callers supply valid enum indices and bitfield values.

## Test Signals

Test signals include boot/resume on R600/R700 boards with varied PowerPlay table revisions, DPM enable/disable traces, thermal interrupt delivery, fan-control behavior, power-state switching under 2D/3D/UVD/VCE loads, memory-leak testing around parse/free failure injection, malformed BIOS table fuzzing in a harness, and PCIe link-gen/lane negotiation checks. Runtime telemetry should confirm expected SCLK/MCLK/voltage transitions and no timeout-induced hangs during SPLL or power-level waits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r600_dpm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r600_dpm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r600_dpm.h

## Purpose

`r600_dpm.h` declares the shared R600 dynamic power-management interface and constants used by R600-family ASIC-specific DPM implementations. It defines default tuning values, table sizes, temperature bounds, power-level/display enums, exported default trend-control arrays, and prototypes for register programming, BIOS parsing, thermal, display-timing, and PCIe helper functions implemented by `r600_dpm.c`.

## Important APIs, Types, and Functions

- Default constants such as `R600_ASI_DFLT`, `R600_BSP_DFLT`, `R600_VOLTAGERESPONSETIME_DFLT`, SPLL/MPLL timing defaults, transition-control defaults, and `R600_PM_NUMBER_OF_*` sizes define expected array dimensions and fallback tuning values.
- `R600_TEMP_RANGE_MIN` and `R600_TEMP_RANGE_MAX` define the internal thermal interrupt range used by late DPM enable.
- `enum r600_power_level`, `enum r600_td`, `enum r600_display_watermark`, and `enum r600_display_gap` provide shared symbolic values for profile slots, trend direction, display watermark, and display-gap policy.
- `extern const u32 r600_utc[]` and `r600_dtc[]` expose the default up/down transition control tables.
- Function prototypes cover DPM diagnostics, vblank/vrefresh discovery, UVD-state classification, transition math, clock/voltage register programming, power-level control, DPM start/stop, thermal sensor classification, platform caps, extended PowerPlay table parsing/freeing, and PCIe speed/lane helpers.

## Control Flow

This header has no executable control flow. It shapes control flow by giving ASIC-specific source files a common call surface. Typical users parse platform and extended PowerPlay tables during initialization, program clock/voltage entries and power levels through the setters, call `r600_start_dpm` when ready, use display timing helpers while selecting power states, and call `r600_free_extended_power_table` during teardown.

## State and Persistence Behavior

The header itself stores no state, but its constants and enums define persistent ABI-like expectations between DPM modules. Array size macros must match `r600_utc`/`r600_dtc` definitions and hardware table capacities. The function prototypes mutate persistent GPU registers and `rdev->pm.dpm` state through their implementations.

## Dependencies and Integration Points

The header includes `radeon.h`, so it depends on Radeon core type definitions such as `struct radeon_device`, `struct radeon_ps`, `enum radeon_int_thermal_type`, and `enum radeon_pcie_gen`. It is included by `r600_dpm.c` and by ASIC-specific DPM files that share R600 helpers.

## Risks and Edge Cases

- Changing size macros can silently break array bounds or hardware table programming in implementation files.
- Temperature defaults affect interrupt thresholds and thermal protection behavior.
- The many register-wrapper prototypes expose low-level hardware programming; invalid caller-provided indices or values are not constrained at the type level.
- `enum r600_display_gap` uses spaces rather than the prevailing tab indentation style, a minor maintainability signal but not a runtime issue.
- Header/API drift between prototypes and implementation can break nonlocal ASIC-specific users.

## Test Signals

Build coverage across all Radeon ASIC DPM files is the primary signal for prototype and enum consistency. Runtime DPM tests should indirectly cover constants by validating parsed table sizes, programmed transition tables, thermal thresholds, and power-level slot usage. Static analysis can flag out-of-range enum or index usage by callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r600_dpm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r600_hdmi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r600_hdmi.c

## Purpose

`r600_hdmi.c` programs HDMI audio support for R600-era display engines. It reads the hardware audio pin status, updates HDMI audio infoframes and ACR values, configures audio packets, DTO clocks, AVI/VBI packets, mute state, HDMI stream routing, and AFMT IRQ enablement for digital encoders.

## Important APIs, Types, and Functions

- `enum r600_hdmi_color_format` and `enum r600_hdmi_iec_status_bits`: local symbolic values for HDMI color mode and IEC60958 channel-status bits.
- `r600_audio_status`: samples `R600_AUDIO_RATE_BPS_CHANNEL` and `R600_AUDIO_STATUS_BITS` into `struct r600_audio_pin` fields: channels, bits per sample, rate, status bits, and category code.
- `r600_audio_update_hdmi`: workqueue callback that detects audio-status changes and refreshes all digital HDMI-capable encoders when audio state or buffer fill status changes.
- `r600_audio_enable` and `r600_audio_get_pin`: enable audio pins through `AZ_HOT_PLUG_CONTROL`; R6xx-NI exposes one pin.
- `r600_hdmi_update_acr`: writes ACR CTS/N values for 32, 44.1, and 48 kHz families, using a DCE3-specific control register when needed.
- `r600_set_avi_packet`, `r600_hdmi_update_audio_infoframe`, `r600_set_vbi_packet`, and `r600_set_audio_packet`: program HDMI infoframe and packet-control registers.
- `r600_hdmi_buffer_status_changed`, `r600_hdmi_audio_set_dto`, `r600_set_mute`, `r600_hdmi_update_audio_settings`, and `r600_hdmi_enable`: manage audio buffer state, audio DTO selection, AVMUTE, infoframe refresh, HDMI routing, and AFMT IRQs.

## Control Flow

Audio polling begins in `r600_audio_update_hdmi`, which reads current audio hardware status and compares it with cached `rdev->audio.pin[0]`. If changed, it updates the cache. It then walks the DRM encoder list, skips non-digital encoders, and calls `r600_hdmi_update_audio_settings` when global audio fields changed or the per-encoder HDMI audio buffer fill status toggled.

HDMI audio settings update checks that the encoder has an enabled AFMT block, reads current audio status, initializes and packs a standard `hdmi_audio_infoframe`, disables HDMI audio test mode if set, acknowledges HDMI errors, selects software audio infoframe source, writes audio infoframe payload registers, and enables continuous audio infoframe update.

Enabling HDMI first validates `dig` and `dig->afmt`. On pre-DCE3 hardware it manually sets HDMI enable/routing bits based on the encoder object id for TMDSA, LVTMA, DDIA, or DVOA and writes `HDMI0_CONTROL`. If IRQs are installed, it enables or disables AFMT IRQs. Finally it records `dig->afmt->enabled`.

Packet setup helpers write fixed control bits for null/general-control packets, audio sample packets, audio infoframe line, generic packet disablement, and IEC60958 channel numbers. DTO setup chooses DTO0 or DTO1 based on `dig_encoder` and derives module from the pixel clock.

## State and Persistence Behavior

Cached audio state persists in `rdev->audio.pin[0]`. Per-encoder AFMT state includes `enabled` and `last_buffer_filled_status`. Hardware register state persists in HDMI, audio, DTO, hotplug, and encoder routing registers. No dynamic memory is allocated here; infoframe buffers are stack-local.

## Dependencies and Integration Points

This file depends on Linux HDMI infoframe helpers, DRM encoder/mode lists, Radeon encoder/private structures, Radeon audio state, AFMT IRQ helpers, DCE version macros, Atom encoder ids, and R600/DCE register definitions from `r600.h`/`r600d.h`. It integrates with the display mode-setting path, Radeon audio workqueue, hotplug/audio enable handling, and interrupt management.

## Risks and Edge Cases

- `r600_set_avi_packet` and `r600_hdmi_update_audio_infoframe` assume caller-provided buffers are large enough for the fixed byte offsets.
- Audio-rate decoding supports only the hardware register encoding this generation exposes; unknown sample-size encodings fall back to 16 bits with an error.
- `r600_hdmi_update_audio_settings` reads fresh hardware status instead of the cached pin, so workqueue ordering with audio changes matters.
- Manual pre-DCE3 routing depends on encoder ids; new or unusual encoder mappings can log an error and leave routing incomplete.
- AFMT IRQ enablement is conditional on IRQ installation, so polling/buffer-status behavior must remain correct without IRQs.
- DTO math multiplies by 100 and assumes clocks fit expected ranges.

## Test Signals

Signals include HDMI audio playback at 44.1/48 kHz families, channel-count changes, hotplug enable/disable, suspend/resume, mute toggling, AFMT interrupt delivery, buffer status changes, pre-DCE3 encoder routing across TMDS/LVTMA/DDI/DVO outputs, and infoframe validation with HDMI analyzers or receiver diagnostics. Regression tests should include no-IRQ fallback and disabled-encoder paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r600_hdmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r600_reg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r600_reg.h

## Purpose

`r600_reg.h` is a compact register-definition header for R600/R700 Radeon code. It names PCIe, RCU, UVD context, memory-controller aperture, RAM configuration, power-management GPIO, display swap, HDP, bus/configuration, ROM, SPLL, BIOS scratch, audio, and HDMI offset registers plus selected masks/shifts/bit values.

## Important APIs, Types, and Functions

This file declares macros rather than functions or types. Important groups include:

- Indexed register ports: `R600_PCIE_PORT_INDEX/DATA`, `R600_RCU_INDEX/DATA`, and `R600_UVD_CTX_INDEX/DATA`.
- Memory-controller aperture registers and masks for R600 and R700, including FB location, AGP top/bottom/base, system aperture low/high/default, and logical page masks.
- Display and memory configuration bits such as `R600_RAMCFG`, channel-size bits, `R600_D1GRPH_SWAP_CONTROL`, endian swap selectors, and channel crossbar selectors.
- Power and GPIO registers such as `R600_GENERAL_PWRMGT`, `R600_OPEN_DRAIN_PADS`, `R600_LOWER_GPIO_ENABLE`, and voltage GPIO control registers.
- Bus, config, blackout, ROM, SPLL, and BIOS scratch registers.
- Audio register addresses for HDA-like capabilities and current stream status.
- HDMI instance offsets for DCE2 and DCE3.2.

## Control Flow

There is no runtime control flow. Other source files include these macros and pass them into MMIO helpers such as `RREG32`, `WREG32`, and `WREG32_P`, or use masks/shifts to encode and decode register values.

## State and Persistence Behavior

The header stores no state. Its definitions describe persistent hardware registers that other code reads and writes. A wrong macro value can redirect MMIO operations to the wrong register and cause persistent hardware misconfiguration until reset or reprogramming.

## Dependencies and Integration Points

`r600_reg.h` is guarded by `__R600_REG_H__` and has no includes. It integrates broadly with Radeon R600 family code, especially memory-controller setup, BIOS scratch handling, audio/HDMI programming, power management, and display surface configuration. Some audio definitions are used alongside `r600_hdmi.c` and Radeon audio helpers.

## Risks and Edge Cases

- Register headers are low-level contracts with hardware; typos in addresses, masks, shifts, or enum-like values are difficult to detect at compile time.
- Comments note that audio registers were reverse engineered and naming may be inaccurate, so semantic assumptions should be verified against behavior.
- R600 and R700 memory-controller register layouts differ; callers must select the correct macro family for the ASIC.
- HDMI offsets differ for DCE2 versus DCE3.2; using the wrong offset can program the wrong instance.
- Because macros have no type safety, expressions with side effects or incorrect width can produce bad bitfield values.

## Test Signals

Build tests only prove macro names resolve. Real signals are hardware init success, correct VRAM/aperture setup, working BIOS scratch communication, display scanout with expected channel swizzles/endian settings, DPM GPIO programming, HDMI/audio operation on DCE2 and DCE3.2, and register dumps matching known-good traces for R600/R700 boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r600_reg.h -->
