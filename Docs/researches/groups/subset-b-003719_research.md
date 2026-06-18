# Research Group subset-b-003719

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/evergreen_cs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/evergreen_cs.c

## Purpose
`evergreen_cs.c` is the Evergreen/Cayman Radeon command-submission validation layer. It parses userspace graphics and DMA command streams, patches buffer-object relocations into indirect buffers, rejects forbidden register writes, validates render/depth/texture/streamout surfaces against BO sizes and hardware tiling rules, and provides VM-era IB validators that check packet/register legality without doing CS relocation patching. The file is a security boundary because command streams originate from userspace and can otherwise program GPU DMA or render engines to access arbitrary memory or privileged registers.

## Important APIs, Types, And Functions
The central per-parse state is `struct evergreen_cs_track`. It tracks GPU tile configuration (`group_size`, `nbanks`, `npipes`, `row_size`), render-target state for up to 12 color buffers, depth/stencil BOs and offsets, htile BO metadata, streamout BOs, dirty flags, indirect draw buffer size, and the ASIC-specific safe-register bitmap.

Surface validation uses `struct eg_surface` plus helpers `evergreen_surface_check_linear()`, `evergreen_surface_check_linear_aligned()`, `evergreen_surface_check_1d()`, `evergreen_surface_check_2d()`, `evergreen_surface_value_conv_check()`, and `evergreen_surface_check()`. These convert register bitfields into byte-per-element, bank, split, alignment, and layer-size requirements. `evergreen_cs_track_validate_cb()`, `evergreen_cs_track_validate_depth()`, `evergreen_cs_track_validate_stencil()`, `evergreen_cs_track_validate_htile()`, and `evergreen_cs_track_validate_texture()` apply those checks to concrete BOs.

The main public parser entry points are `evergreen_cs_parse()` for graphics CS ioctl packets, `evergreen_dma_cs_parse()` for DMA CS ioctl packets, `evergreen_ib_parse()` for VM graphics IB validation, and `evergreen_dma_ib_parse()` for VM DMA IB validation. `evergreen_packet3_check()`, `evergreen_cs_handle_reg()`, `evergreen_packet0_check()`, `evergreen_cs_parse_packet0()`, and `evergreen_is_safe_reg()` make up the packet/register validation core. `evergreen_vm_packet3_check()` and `evergreen_vm_reg_valid()` are the VM-side equivalents.

## Control Flow
`evergreen_cs_parse()` lazily allocates and initializes `evergreen_cs_track`, selects `evergreen_reg_safe_bm` or `cayman_reg_safe_bm`, derives pipe/bank/group/row geometry from the ASIC tile config, then loops over the IB with `radeon_cs_packet_parse()`. Packet type 0 is restricted to the vline register path; type 2 is skipped; type 3 is sent to `evergreen_packet3_check()`. On any parse or validation error, the tracker is freed and `-EINVAL` or the helper error is returned.

`evergreen_packet3_check()` is a large opcode switch. It validates packet lengths, consumes relocations in the order implied by the packet stream, patches low/high GPU address words in `p->ib.ptr`, and runs `evergreen_cs_track_check()` before draw/dispatch packets that consume previously programmed state. State-setting packets validate register ranges, consult the safe bitmap, and dispatch special registers to `evergreen_cs_handle_reg()`. Resource packets distinguish texture and vertex-buffer descriptors: texture descriptors get tiling fields patched from relocation tiling flags and are size-checked through `evergreen_cs_track_validate_texture()`, while vertex buffers have GPU base addresses patched and oversized descriptors clamped to BO size.

`evergreen_cs_handle_reg()` owns stateful register interpretation. It records color/depth/stencil/streamout/htile register values, requires relocations for base-address registers, patches relocation GPU offsets, applies tiling overrides unless `RADEON_CS_KEEP_TILING_FLAGS` is set, rejects family-inappropriate Cayman/Evergreen registers, and marks dirty flags so validation is deferred until the next draw or dispatch.

`evergreen_dma_cs_parse()` separately walks DMA packet headers with `GET_DMA_CMD`, `GET_DMA_COUNT`, and `GET_DMA_SUB_CMD`. It supports write, copy, constant fill, and nop forms, consumes source/destination relocations, patches GPU addresses, validates BO bounds, and advances `p->idx` by the packet-specific encoded length. The VM parsers do not patch relocations; they reject packet0, enforce packet3 opcode/register allow-lists, and check DMA packet structure by advancing `idx`.

## State And Persistence Behavior
Parser state is transient per command submission. The tracker is allocated in `evergreen_cs_parse()`, attached to `p->track`, and freed before return. It persists only across packets within the same IB so later draw packets can validate state assembled by earlier register writes. The parser mutates the submitted IB in memory by adding relocation GPU offsets and, in one old-DDX compatibility path, by reducing `CB_COLOR*_SLICE` to a BO-fitting value. No durable kernel state is written here, but hardware-visible command buffers are deliberately rewritten before execution.

Dirty flags (`cb_dirty`, `db_dirty`, `streamout_dirty`) avoid revalidating unchanged state. `sx_misc_kill_all_prims` short-circuits draw validation when all primitives are killed. `indirect_draw_buffer_size` records the BO size supplied by `PACKET3_SET_BASE` and is later checked by indirect draw packets.

## Dependencies And Integration Points
The parser depends on Radeon core CS data structures and helpers from `radeon.h`, `radeon_asic.h`, `r600.h`, `evergreend.h`, `evergreen_reg_safe.h`, and `cayman_reg_safe.h`. It calls relocation helpers such as `radeon_cs_packet_next_reloc()` and `r600_dma_cs_next_reloc()`, BO sizing via `radeon_bo_size()`, format helpers such as `r600_fmt_get_blocksize()` and `r600_fmt_is_valid_texture()`, and tiling helpers such as `evergreen_tiling_fields()`. Display vline packet validation is delegated to `r600_cs_common_vline_parse()`.

Entry points are wired into the Radeon ASIC operation tables for Evergreen/Cayman graphics and DMA rings. The CS parser works with TTM/GEM BO relocation lists, CP packet definitions, family checks, and the generated safe-register bitmaps.

## Risks
The file handles untrusted command streams, so relocation-order mistakes, length miscalculation, unchecked high address bits, unsafe register allow-list entries, or integer overflow in surface size arithmetic can become memory corruption or privilege risks. Some partial Cayman DMA subcommands only patch addresses without full BO bounds checks, which appears intentional for legacy packet formats but is a high-risk area for future changes. The old DDX compatibility branch rewrites color slice state, so regressions there could hide BO underallocation bugs or break legacy userspace. Safe-register bitmap polarity is non-obvious: `evergreen_is_safe_reg()` returns true when the corresponding bitmap bit is clear, so audits must account for that convention.

## Test Signals
Useful tests include malicious CS streams for every packet length check, missing/extra relocation cases, texture/mipmap/depth/stencil/color BO underallocation, htile alignment for 1/2/4/8 pipes, streamout size checks, family-specific Cayman-only and Evergreen-only packets, CP DMA register/memory combinations, indirect draw without `SET_BASE`, and VM IB validation for forbidden registers. Runtime signals are `dev_warn_once()`/`dev_warn()` messages, `-EINVAL` from CS ioctl paths, GPU lockups after accepted streams, and userspace regressions in Mesa/old DDX workloads that rely on tiling patch-up.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/evergreen_cs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/evergreen_dma.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/evergreen_dma.c

## Purpose
`evergreen_dma.c` contains DMA-ring operational helpers for Evergreen through Southern Islands style Radeon ASIC support. Unlike the DMA command-stream parser in `evergreen_cs.c`, this file emits trusted kernel DMA ring packets for fences, indirect-buffer execution, TTM buffer moves, and lockup detection.

## Important APIs, Types, And Functions
`evergreen_dma_fence_ring_emit()` writes a DMA fence packet to the selected DMA ring, followed by a trap packet for interrupt generation and an SRBM write that flushes HDP coherency. `evergreen_dma_ring_ib_execute()` emits a DMA indirect-buffer packet, with optional writeback of the next read pointer and padding so the IB packet lands on the hardware-required 8-DW boundary. `evergreen_copy_dma()` is the copy callback used by Radeon TTM memory movement; it emits one or more DMA copy packets and returns a `struct radeon_fence *`. `evergreen_dma_is_lockup()` checks soft-reset status and updates or tests ring lockup state.

## Control Flow
Fence emission takes the fence ring, obtains the fence GPU address from `rdev->fence_drv`, writes the DMA fence packet/address/sequence, emits a trap, then writes `HDP_MEM_COHERENCY_FLUSH_CNTL` through an SRBM write packet.

IB execution optionally writes `ring->next_rptr_gpu_addr` when writeback is enabled, pads the ring write pointer until the DMA IB packet will end on the required modulo-8 position, then emits `DMA_PACKET_INDIRECT_BUFFER` with the IB base address and length. `evergreen_copy_dma()` creates a `radeon_sync`, computes the transfer length in dwords, splits the transfer into chunks no larger than `0xfffff` dwords, locks enough ring space, syncs against the reservation object and other rings, writes copy packets, emits a fence, commits the ring, and releases sync state. Error paths undo the ring lock when a fence cannot be emitted and return `ERR_PTR(r)`.

## State And Persistence Behavior
The functions mutate the DMA ring write stream and therefore persist work in GPU-visible ring memory until consumed by the engine. They update synchronization state through emitted fences and optional read-pointer writeback. No private static state is kept in this file. `evergreen_copy_dma()` advances source and destination offsets per emitted chunk and leaves completion state represented by the returned fence.

## Dependencies And Integration Points
The file depends on core Radeon ring, fence, sync, writeback, and ASIC reset helpers from `radeon.h`, `radeon_asic.h`, `evergreen.h`, and `evergreend.h`. It integrates with the ASIC copy callback (`rdev->asic->copy.dma_ring_index`), TTM reservation synchronization (`struct dma_resv`), fence drivers, and ring lock/unlock infrastructure. Hardware register and packet macros include `DMA_PACKET_*`, `HDP_MEM_COHERENCY_FLUSH_CNTL`, and `RADEON_RESET_DMA`.

## Risks
DMA packet formatting is low-level and alignment-sensitive. Incorrect padding in `evergreen_dma_ring_ib_execute()` can hang the DMA engine. Copy chunk sizing must match the packet count field width; the loop correctly caps at `0xfffff` dwords. Fence emission depends on a valid fence GPU address and ring index. Error handling around ring locks is important because a partially written but uncommitted ring could corrupt subsequent work if not undone.

## Test Signals
Tests should cover DMA ring fence signaling, interrupt delivery after trap packets, IB execution alignment, writeback-enabled and writeback-disabled execution, copy sizes at 0, one page, exactly `0xfffff` dwords, and multi-chunk transfers. Lockup tests should simulate soft-reset masks with and without `RADEON_RESET_DMA`. Runtime signals include ring test failures, fence timeouts, DMA reset events, and TTM buffer move errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/evergreen_dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/evergreen_hdmi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/evergreen_hdmi.c

## Purpose
`evergreen_hdmi.c` programs DCE4 HDMI and DisplayPort audio/video-infoframe hardware for the Radeon display driver. It enables audio pins, writes HDMI ACR values, speaker allocation, ELD/SAD codec descriptors, AVI/VBI/audio infoframes, DTO clock ratios, color depth, mute state, and HDMI/DP secondary stream enables.

## Important APIs, Types, And Functions
Public hooks declared in `evergreen_hdmi.h` are implemented here. Audio enable and packet setup functions include `dce4_audio_enable()`, `dce4_set_audio_packet()`, and `dce4_set_mute()`. HDMI-specific configuration uses `evergreen_hdmi_update_acr()`, `evergreen_set_avi_packet()`, `dce4_hdmi_audio_set_dto()`, `dce4_hdmi_set_color_depth()`, and `evergreen_hdmi_enable()`. DP audio uses `dce4_dp_audio_set_dto()` and `evergreen_dp_enable()`. ELD/audio capability programming is handled by `dce4_afmt_write_latency_fields()`, `dce4_afmt_hdmi_write_speaker_allocation()`, `dce4_afmt_dp_write_speaker_allocation()`, and `evergreen_hdmi_write_sad_regs()`.

## Control Flow
Most functions are direct register-programming routines using `RREG32`, `WREG32`, `WREG32_OR`, `WREG32_AND`, `WREG32_P`, and endpoint codec accessors. `dce4_audio_enable()` updates `AZ_HOT_PLUG_CONTROL` based on an audio-pin enable mask, early-returning for a null pin. `evergreen_hdmi_update_acr()` selects hardware or software CTS behavior based on CRTC bits-per-color and writes 32/44.1/48 kHz CTS/N values.

Speaker allocation routines read the codec pin speaker register, clear the opposite transport mode and allocation mask, set HDMI or DP mode, and write either SADB byte 0 or a stereo fallback. `evergreen_hdmi_write_sad_regs()` maps CEA SAD formats to codec descriptor registers, selects the descriptor with the highest channel count for each type, and separately accumulates PCM stereo frequencies.

DTO setup chooses HDMI DTO0 or DP DTO1, programs source CRTC selection, and writes phase/module ratios. DP adjusts the module for DCE4.1 dentist divider when present. `evergreen_hdmi_enable()` checks the encoder's DIG AFMT block and connector audio capability, then enables AVI/audio infoframes and sample sending as appropriate; disable clears sample sending and infoframe control. `evergreen_dp_enable()` similarly enables DP secondary audio, timestamp, audio infoframe, and stream bits, with DP clock-dependent N-base multiplier programming on pre-DCE6 hardware.

## State And Persistence Behavior
The persistent state is hardware register state plus `dig->afmt->enabled`. The functions do not allocate memory or retain private software state. Register programming persists until mode set, disable, suspend/resume, or another encoder/audio path reprograms the same AFMT block. Connector-derived latency, SAD, and `display_info.has_audio` values are treated as current DRM/EDID state.

## Dependencies And Integration Points
This file integrates DRM encoder/connector/CRTC objects with Radeon private encoder structures (`radeon_encoder`, `radeon_encoder_atom_dig`, `radeon_connector_atom_dig`) and audio helpers from `radeon_audio.h`. It depends on CEA SAD definitions from DRM EDID/HDMI headers and on DCE4 register definitions in `evergreend.h`. The functions are called by Radeon mode-setting and audio setup paths when connectors are enabled, disabled, or reconfigured.

## Risks
Most risk is hardware sequencing and stale connector state rather than memory safety. Wrong AFMT offsets can program the wrong encoder. Enabling audio without valid connector capability can send unwanted packets. DTO ratio mistakes cause audio drift or silence. `evergreen_set_avi_packet()` assumes the supplied infoframe buffer has the expected HDMI header/payload layout; callers must provide a sufficiently sized encoded frame. DP DCE4.1 divider handling depends on correct `radeon_audio_decode_dfs_div()` behavior.

## Test Signals
Test signals include HDMI and DP audio presence in ALSA/ELD, correct speaker allocation for SADB-bearing and stereo-fallback sinks, stable audio at multiple pixel clocks, deep-color behavior at 8/10/12 bpc, mute bit toggling, AVI infoframe correctness, DP secondary stream enablement, and suspend/resume or hotplug reprogramming. Register traces around `HDMI_INFOFRAME_CONTROL0`, `AFMT_AUDIO_PACKET_CONTROL`, DTO registers, and `EVERGREEN_DP_SEC_CNTL` are useful when debugging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/evergreen_hdmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/evergreen_hdmi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/evergreen_hdmi.h

## Purpose
`evergreen_hdmi.h` is the private Radeon header that exposes DCE4/Evergreen HDMI and DisplayPort audio/video-infoframe helper functions to the rest of the driver. It contains no implementation logic; it defines the cross-file API contract implemented by `evergreen_hdmi.c`.

## Important APIs, Types, And Functions
The header forward-declares DRM and Radeon types used by the prototypes: `struct drm_encoder`, `struct drm_connector`, `struct drm_display_mode`, `struct radeon_device`, `struct radeon_crtc`, `struct radeon_hdmi_acr`, `struct r600_audio_pin`, and CEA audio descriptor types. Declared functions include HDMI/DP enable hooks (`evergreen_hdmi_enable()`, `evergreen_dp_enable()`), audio pin control (`dce4_audio_enable()`), ACR programming (`evergreen_hdmi_update_acr()`), AVI packet writing (`evergreen_set_avi_packet()`), SAD/speaker/latency programming, DTO setup, VBI/audio packet setup, color depth selection, and mute control.

## Control Flow
As a header, it contributes compile-time linkage only. Source files include it to get type-checked prototypes before calling into `evergreen_hdmi.c`. Include guards prevent multiple declaration in one translation unit.

## State And Persistence Behavior
No runtime state is stored here. The declarations describe routines that mutate Radeon display/audio hardware state and AFMT software state in their implementation file.

## Dependencies And Integration Points
The header is private to the Radeon driver and intentionally uses forward declarations instead of including all DRM/Radeon definitions. This reduces include coupling while allowing mode-setting, audio, and encoder code to call the DCE4 HDMI/DP helpers.

## Risks
Prototype drift is the main risk: if implementation signatures change without updating this header or vice versa, callers may fail to build or call with wrong assumptions. Because it exposes low-level hardware hooks, unclear parameter units such as `offset`, `clock`, and `bpc` can lead to misuse by call sites.

## Test Signals
Build coverage is the primary signal. Runtime coverage comes indirectly from the functions declared here: HDMI/DP audio enablement, infoframe emission, DTO programming, mute control, and hotplug/modeset paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/evergreen_hdmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/evergreen_reg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/evergreen_reg.h

## Purpose
`evergreen_reg.h` is a register-definition header for Evergreen/Northern Islands display, graphics-surface, cursor, LUT, HDMI, DP, UNIPHY, clock, GPIO, audio, and SMC-indirect access blocks. It provides numeric MMIO offsets and bitfield construction macros used by Radeon display and low-level ASIC code.

## Important APIs, Types, And Functions
The file exports preprocessor constants only. Major groups include SMC indirect index/data registers (`TN_SMC_IND_INDEX_0`, `TN_SMC_IND_DATA_0`), PIF/CG indirect registers, VGA memory and D3-D6 VGA controls, spread-spectrum PLL controls, audio PLL/vendor/enable registers, graphics plane registers (`EVERGREEN_GRPH_*`) with format/tiling/depth/bank macros, cursor registers (`EVERGREEN_CUR_*`), LUT registers, vline/status registers, CRTC register offsets for six display controllers, HPD GPIO registers, HDMI/DIG offsets, DP secondary stream/audio timestamp registers, and NI UNIPHY controls.

## Control Flow
There is no executable control flow. Callers compose register values through macros such as `EVERGREEN_GRPH_DEPTH(x)`, `EVERGREEN_GRPH_NUM_BANKS(x)`, `EVERGREEN_GRPH_FORMAT(x)`, `EVERGREEN_GRPH_ARRAY_MODE(x)`, `EVERGREEN_CURSOR_MODE(x)`, `NI_DIG_FE_CNTL_SOURCE_SELECT(x)`, `EVERGREEN_DP_SEC_TIMESTAMP_MODE(x)`, and `EVERGREEN_DP_SEC_N_BASE_MULTIPLE(x)`, then pass those values to Radeon register read/write helpers.

## State And Persistence Behavior
The header itself has no state. Its constants describe hardware state locations and bit layouts. Values written using these definitions persist in GPU display/audio hardware until reprogrammed or reset. The CRTC/DIG/DP offset constants encode the repeated-block layout used to address one of up to six controllers.

## Dependencies And Integration Points
`evergreen_reg.h` is consumed by Radeon display, audio, power, and ASIC setup code that needs direct Evergreen-family MMIO definitions. It complements broader generated or hand-written register headers such as `evergreend.h`; this file focuses on a subset of display/audio/graphics-plane definitions that other C files can include without embedding magic numbers.

## Risks
Register headers are fragile because a wrong offset or bit shift can silently program unrelated hardware. The macros do little validation beyond masking input width, so callers must pass valid enum values. Repeated block offsets must match actual ASIC layout; off-by-one controller offsets can affect the wrong CRTC, DIG, or DP block. Another risk is naming overlap with definitions in adjacent Radeon headers.

## Test Signals
Build tests catch duplicate or missing definitions. Functional signals include successful modeset across all CRTCs, cursor programming, LUT updates, page flips, HPD detection, HDMI/DP audio packet enablement, and UNIPHY enable/disable behavior. Register dumps comparing programmed values to expected bitfields are the most direct validation for this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/evergreen_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/evergreen_smc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/evergreen_smc.h

## Purpose
`evergreen_smc.h` defines Evergreen System Management Controller firmware table structures and firmware-header offsets used by Radeon power-management code. It extends the RV770 SMC definitions with Evergreen memory-controller register table layouts.

## Important APIs, Types, And Functions
The header includes `rv770_smc.h`, enables one-byte structure packing with `#pragma pack(push, 1)`, and defines `SMC_EVERGREEN_MC_REGISTER_ARRAY_SIZE` as 16. `struct SMC_Evergreen_MCRegisterAddress` stores two 16-bit address selectors (`s0`, `s1`). `struct SMC_Evergreen_MCRegisterSet` stores 16 32-bit register values. `struct SMC_Evergreen_MCRegisters` contains a `last` index byte, three reserved bytes, 16 register-address entries, and five register-value sets. Typedef aliases mirror the struct names. Firmware-header offsets identify `softRegisters`, `stateTable`, and `mcRegisterTable` fields relative to `EVERGREEN_SMC_FIRMWARE_HEADER_LOCATION`.

## Control Flow
There is no executable control flow. The header defines binary layouts that other code uses when parsing, constructing, or uploading SMC firmware tables.

## State And Persistence Behavior
The structures model persistent firmware-facing state rather than storing state themselves. Packing is critical because these structures map directly to SMC firmware memory layout; padding differences would corrupt table interpretation. Values loaded through these layouts persist in SMC-controlled firmware tables and influence memory-clock/power-state behavior.

## Dependencies And Integration Points
The file depends on RV770 base SMC definitions and standard fixed-width integer types supplied through included kernel headers. It integrates with Radeon Evergreen power-management and firmware-loading code that locates the SMC firmware header at `0x100` and follows the table offsets to program memory-controller registers for different power states.

## Risks
Binary layout drift is the main risk. Changing packing, array size, field order, or typedef names can break firmware communication. Offset constants must match the SMC firmware ABI; incorrect offsets can make power-management code read or write the wrong firmware table. Because these tables affect memory-controller setup, mistakes may cause hangs during clock changes or resume.

## Test Signals
Build coverage confirms the header remains syntactically compatible. Runtime signals include successful SMC firmware initialization, stable power-state transitions, memory clock changes without display corruption, suspend/resume stability, and absence of SMC table parsing errors in Radeon debug logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/evergreen_smc.h -->
