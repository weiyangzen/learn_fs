# Research: subset-b-003761

Worker-produced research for the VC4 HDMI, HVS, IRQ, and KMS files listed in subset `subset-b-003761`. Each section is source-tree aligned and wrapped for reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_hdmi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_hdmi.c

## Purpose

`vc4_hdmi.c` is the main HDMI controller driver for Broadcom VC4/VC5/VC6 Raspberry Pi display hardware. It binds the platform HDMI component into DRM, exposes an HDMI connector and TMDS encoder, programs video timing/CSC/infoframe/packet RAM state, handles hotplug and SCDC scrambling, provides HDMI audio through ASoC and the DRM HDMI audio helper, optionally registers CEC, manages runtime PM and clocks, and selects SoC-specific behavior through `struct vc4_hdmi_variant`.

## Important APIs, Types, and Functions

- Connector entry points: `vc4_hdmi_connector_detect_ctx()`, `vc4_hdmi_connector_get_modes()`, `vc4_hdmi_connector_atomic_check()`, `vc4_hdmi_connector_reset()`, and `vc4_hdmi_connector_init()` integrate with DRM connector, HDMI state helper, EDID/DDC, TV margins, colorspace, broadcast RGB, audio, and mode validation.
- HDMI infoframe support is implemented through `vc4_hdmi_clear_infoframe()`, `vc4_hdmi_write_infoframe()`, and typed wrappers for AVI, vendor HDMI, audio, HDR DRM, and SPD frames. `vc4_hdmi_hdmi_connector_funcs` wires these into the DRM HDMI connector helper.
- Encoder operations are split across the VC4 encoder staging hooks: `vc4_hdmi_encoder_pre_crtc_configure()` powers the block and configures clocks/PHY/timings, `vc4_hdmi_encoder_pre_crtc_enable()` applies CSC and FIFO mode, `vc4_hdmi_encoder_post_crtc_enable()` enables video, packet RAM, infoframes, FIFO recentering, and scrambling, while `vc4_hdmi_encoder_post_crtc_disable()` and `vc4_hdmi_encoder_post_crtc_powerdown()` blank/disable video, scrambling, PHY, clocks, and runtime PM.
- Clock, timing, and format helpers include `vc4_hdmi_mode_needs_scrambling()`, `vc4_hdmi_connector_clock_valid()`, `vc4_hdmi_encoder_atomic_check()`, `vc4_hdmi_encoder_mode_valid()`, `vc4_hdmi_set_timings()`, `vc5_hdmi_set_timings()`, `vc4_hdmi_csc_setup()`, and `vc5_hdmi_csc_setup()`.
- Audio support is implemented through `vc4_hdmi_audio_startup()`, `vc4_hdmi_audio_prepare()`, `vc4_hdmi_audio_shutdown()`, `vc4_hdmi_audio_init()`, `vc4_hdmi_audio_set_mai_clock()`, `vc4_hdmi_set_n_cts()`, `sample_rate_to_mai_fmt()`, channel-map helpers, ASoC DAI/card setup, and DRM HDMI audio callbacks.
- Optional CEC support under `CONFIG_DRM_VC4_HDMI_CEC` includes threaded IRQ handlers, message packing/unpacking, `vc4_hdmi_cec_enable()`, `vc4_hdmi_cec_disable()`, `vc4_hdmi_cec_adap_log_addr()`, `vc4_hdmi_cec_adap_transmit()`, `vc4_hdmi_cec_init()`, and `vc4_hdmi_cec_register()`.
- Resource/probe paths include `vc4_hdmi_init_resources()` for BCM2835-style register maps, `vc5_hdmi_init_resources()` for named VC5/VC6 register regions, `vc4_hdmi_runtime_suspend()`, `vc4_hdmi_runtime_resume()`, `vc4_hdmi_bind()`, `vc4_hdmi_dev_probe()`, `vc4_hdmi_dev_remove()`, and the exported `vc4_hdmi_driver`.
- Variant records for BCM2835, BCM2711 HDMI0/HDMI1, and BCM2712 HDMI0/HDMI1 provide register tables, max pixel clocks, lane mapping, PHY functions, reset/timing/CSC callbacks, odd horizontal timing restrictions, HPD path, HDR support, audio card names, and IRQ-controller topology.

## Control Flow

Component bind allocates `struct vc4_hdmi`, initializes locks and delayed scrambling work, resolves resources through the variant, acquires DDC and optional HPD GPIO, enables runtime PM, initializes encoder and connector objects, registers hotplug IRQs, CEC, and audio. Runtime resume enables HSM/audio clocks, verifies HSM is nonzero to avoid CPU stalls on uninitialized firmware clock state, resets the hardware, and initializes CEC divider/masks.

Hotplug detection resumes runtime PM, reads GPIO or hardware HPD, calls `drm_atomic_helper_connector_hdmi_hotplug()`, and, when connected, may call `vc4_hdmi_reset_link()`. The link reset path locks connection and CRTC state, checks whether the current active mode needs SCDC scrambling, compares sink SCDC status, and requests a full CRTC reset if the sink and source are out of sync.

The modeset enable path saves adjusted mode and HDMI output format in `atomic_mode_set`, then `pre_crtc_configure` raises runtime PM, sets HSM/pixel/BVB clocks, updates the CEC divider, initializes the PHY, enables manual scheduler format mode, and writes timing registers. `pre_crtc_enable` configures CSC and FIFO master/slave. `post_crtc_enable` enables video output, switches HDMI/DVI scheduler mode, enables packet RAM for HDMI sinks, updates infoframes, recenters the FIFO, and enables SCDC scrambling for HDMI 2.0 rates.

Disable runs in the reverse direction: packet RAM is marked disabled, video is blanked and optionally disabled, SCDC scrambling is disabled, PHY is disabled, pixel clocks are turned off, and runtime PM is released. Audio and CEC have their own enable/disable paths but share the same HDMI state and MMIO lock discipline.

## State and Persistence

Persistent driver state is in `struct vc4_hdmi`: connector/encoder objects, DDC adapter, MMIO bases, clocks, reset line, debugfs regsets, hotplug GPIO, CEC message/IRQ state, audio card state, delayed scrambling work, `saved_adjusted_mode`, packet RAM and SCDC state, output bpc/format, and the ALSA jack. State is not persisted to disk; it is live kernel device state reconstructed at bind/probe and runtime resume.

Concurrency is split between `mutex`, protecting cross-framework HDMI state used by KMS/ALSA/CEC, and `hw_lock`, a spinlock protecting register writes and many read-modify-write sequences. Most MMIO access is guarded by `drm_dev_enter()` and runtime PM; CEC interrupt paths explicitly rely on IRQ lifetime being tied to the platform device rather than the DRM device.

## Dependencies and Integration Points

This file depends heavily on DRM atomic helpers, DRM HDMI connector/audio/CEC helpers, EDID/DDC, SCDC, debugfs regsets, Linux component framework, runtime PM, clocks, resets, GPIO descriptors, OF device tree, ASoC, DMAEngine PCM, and local VC4 helpers in `vc4_drv.h`, `vc4_hdmi.h`, `vc4_hdmi_regs.h`, and `vc4_regs.h`. It integrates with `vc4_hdmi_phy.c` through variant PHY callbacks, with HVS/KMS through encoder hooks and mode validation, and with platform matching through `of_device_id`.

## Risks and Edge Cases

- Incorrect runtime PM or clock sequencing can stall the CPU, especially when firmware leaves HSM clock rate at zero.
- SCDC scrambling is stateful across source and sink; stale sink state is handled by forcing a full modeset, but races with hotplug and commits are delicate.
- Packet RAM writes require packet RAM enabled and packet idle polling; infoframe length or stale bytes can trigger analyzer checksum failures.
- Audio registration intentionally uses devm ASoC lifetimes while relying on DRM-managed `vc4_hdmi` lifetime plus `drm_dev_enter()` to avoid removed-device MMIO.
- CEC message packing reads/writes groups of four bytes; malformed lengths over 16 are rejected, but short messages rely on `cec_msg` storage being safe for grouped access.
- BCM2712 has a TODO around disabling `VID_CTL_ENABLE` after blanking because it can lock up.
- Odd horizontal timings, WiFi coexistence clock adjustment, HDMI 2.0 core-clock enable flags, and 4096x2160 limits are hardware/platform policy embedded in atomic validation.

## Test Signals

Useful signals include DRM/KUnit tests for PV muxing and mock KMS paths elsewhere in the vc4 tree, debugfs register dumps from `*_regs`, `hvs_underrun` interactions for display stability, EDID/mode probing with HDMI 1.4 vs HDMI 2.0 clocks, hotplug/CEC IRQ exercise, ALSA playback through HDMI with 2/8-channel PCM and HBR status, SCDC scrambling status at >340 MHz TMDS, and suspend/resume/remove races verified by lack of `drm_dev_enter()` failures or PM warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_hdmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_hdmi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_hdmi.h

## Purpose

`vc4_hdmi.h` defines the shared HDMI driver interface and state containers used by `vc4_hdmi.c` and `vc4_hdmi_phy.c`. It describes variant-specific behavior, live HDMI device state, audio substate, lane identifiers, container conversion helpers, and PHY function prototypes for VC4, VC5, and VC6 HDMI blocks.

## Important APIs, Types, and Functions

- `enum vc4_hdmi_phy_channel` names the three data lanes and clock lane used by lane-mapping tables.
- `struct vc4_hdmi_variant` is the key abstraction for hardware generations. It contains encoder identity, ALSA/debugfs names, max pixel clock, variant register table, lane mapping, hardware quirks, resource/reset/CSC/timing/PHY callbacks, channel-map callback, HDR flag, and HPD callback.
- `struct vc4_hdmi_audio` stores the ASoC card/link/component fields, DMA data, and streaming flag.
- `struct vc4_hdmi` stores the entire controller instance: audio must be first, followed by platform and variant references, VC4 encoder, DRM connector, delayed SCDC work, DDC, MMIO bases, GPIO HPD, coexistence flag, CEC state, clocks, reset, debugfs regsets, hardware lock, cross-framework mutex, saved mode/output state, packet RAM/SCDC flags, and HDMI jack.
- `connector_to_vc4_hdmi()` and `encoder_to_vc4_hdmi()` provide safe container conversions.
- Prototypes expose `vc4_hdmi_phy_*`, `vc5_hdmi_phy_*`, and `vc6_hdmi_phy_*` implementation functions.

## Control Flow

The header itself has no executable control flow beyond `encoder_to_vc4_hdmi()`. Its structure drives runtime control in the C files: bind selects a `vc4_hdmi_variant`, stores it in `struct vc4_hdmi`, then all major operations dispatch through variant callbacks for resource acquisition, reset, CSC, timings, PHY, RNG, channel map, and HPD.

## State and Persistence

All fields are volatile kernel state. The header documents the intended locking model: `hw_lock` protects register access, `mutex` protects state shared by KMS/ALSA/CEC, `saved_adjusted_mode`, `packet_ram_enabled`, `scdc_enabled`, `output_bpc`, and `output_format` are mutex-protected copies used outside immediate atomic commit context. No fields are persistent across driver unbind; device tree and platform match data reconstruct variant state.

## Dependencies and Integration Points

The header depends on DRM connector types, CEC messages, ASoC and DMAEngine audio types, and local `vc4_drv.h`. It is consumed by the HDMI core, PHY implementation, register accessors, and other VC4 files that need encoder/container conversion or PHY prototypes.

## Risks and Edge Cases

- `BUILD_BUG_ON()` assumptions in the audio init path require `struct vc4_hdmi_audio` and `struct vc4_hdmi` layout to keep audio/card at offset zero; moving fields would break the driver.
- Variant callbacks are mandatory for many paths but may be NULL for unsupported generation features, so new variants must fill fields carefully.
- Locking comments in this header are part of the contract; adding new users of saved mode, packet RAM, SCDC, or audio state without respecting `mutex` can create KMS/ALSA/CEC races.
- The VC5-only MMIO and debugfs fields are used by VC6 too through the same register-base enum names, so comments are historical rather than strict type separation.

## Test Signals

Compile-time layout checks, allmodconfig/build coverage, KUnit mock construction of VC4 devices, and variant probing on BCM2835/BCM2711/BCM2712 are the key signals. Any new field that changes layout or callback requirements should be validated by HDMI bind, audio registration, and PHY init paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_hdmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_hdmi_phy.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_hdmi_phy.c

## Purpose

`vc4_hdmi_phy.c` programs the HDMI transmit PHY for three hardware families. The original VC4 path performs basic reset/RNG toggling. The VC5 path computes PLL/VCO parameters, range measurement offsets, lane amplitude/termination settings, clock word selection, and lane swaps. The VC6 path programs a newer PHY with different PLL registers, lane current/termination bitfields, and power-up controls.

## Important APIs, Types, and Functions

- VC4 exports: `vc4_hdmi_phy_init()`, `vc4_hdmi_phy_disable()`, `vc4_hdmi_phy_rng_enable()`, and `vc4_hdmi_phy_rng_disable()`.
- VC5 exports: `vc5_hdmi_phy_init()`, `vc5_hdmi_phy_disable()`, `vc5_hdmi_phy_rng_enable()`, and `vc5_hdmi_phy_rng_disable()`.
- VC6 exports: `vc6_hdmi_phy_init()` and `vc6_hdmi_phy_disable()`. The disable function is currently empty.
- VC5 helpers: `phy_get_vco_freq()`, `phy_get_cp_current()`, `phy_get_rm_offset()`, `phy_get_vco_gain()`, `phy_get_settings()`, `phy_get_channel_settings()`, and `vc5_hdmi_reset_phy()`.
- VC6 helpers: `vc6_phy_get_vco_freq()`, `vc6_phy_get_settings()`, `vc6_phy_get_channel_settings()`, and `vc6_hdmi_reset_phy()`.
- Tuning tables: `vc5_hdmi_phy_settings[]` maps TMDS ranges to pre-emphasis/main driver/resistance/termination per data and clock lane; `vc6_hdmi_phy_settings[]` maps rates to packed lane current, FFE, slew, bias, source, tap, and termination fields.

## Control Flow

The top-level HDMI encoder enable path calls the variant `phy_init()` after clocks and runtime PM are ready. VC4 init toggles reset bits and leaves the PHY active; disable asserts reset. VC5 init computes VCO selection/divider from the TMDS character rate, resets and powers down RNG, releases lane resets, configures range measurement, PLL calibration, PLL control, RM format, TMDS word select, charge pump/VCO gain, per-lane amplitude and termination, lane swap routing from `variant->phy_lane_mapping`, then toggles PLL reset bits to start the PLL. VC5 disable resets the PHY; RNG helpers clear/set the RNG power-down bit.

VC6 init computes an 8-12 GHz VCO divider, resets/powers down the PHY, writes a fixed block of PLL misc calibration values, configures 54 MHz reference clock, reset state, RM offset, VCO divider, PLL post divider, per-lane control words for three data lanes and the clock lane, TMDS word select, HDMI lane/bias/LDO/background power-up, PLL power-up, and PLL reset release. VC6 disable currently does nothing, which leaves cleanup to higher-level blanking/power paths.

## State and Persistence

The file stores only static tuning tables and uses live state from `struct vc4_hdmi`, especially `variant->phy_lane_mapping`, `hw_lock`, and the connector state's `hdmi.tmds_char_rate`. All hardware state is persisted only in PHY MMIO registers until reset, runtime suspend, or power removal. Every exported function takes `hw_lock` around writes; helpers that write expect the lock to be held.

## Dependencies and Integration Points

This file depends on `vc4_hdmi.h`, `vc4_hdmi_regs.h`, and `vc4_regs.h` for state, register access, and bitfield helpers. It is not a standalone PHY framework driver; the HDMI core calls it through variant callbacks. It depends on the register base tables in `vc4_hdmi_regs.h` matching the selected SoC generation and on `vc4_hdmi.c` enabling clocks/runtime PM before PHY MMIO access.

## Risks and Edge Cases

- PHY programming is table-driven and frequency-sensitive; off-by-one TMDS ranges or bad fallback to the last table entry can affect signal integrity.
- `phy_get_vco_freq()` and `vc6_phy_get_vco_freq()` rely on simple divider search and multiplication by 10 for TMDS bit rate, so unusual rates should be checked for overflow and valid hardware range.
- Lane mapping differs between BCM2711 HDMI0 and HDMI1; wrong `phy_lane_mapping` silently swaps physical lanes.
- VC6 contains many fixed magic PLL constants with little local explanation; regression testing on real BCM2712 hardware is important.
- `vc6_hdmi_phy_disable()` is empty, so power leakage or stale PHY state could be hidden by other disable paths.
- MMIO access triggers KUnit failures through the register accessors, so unit tests must avoid calling these functions directly without mocks.

## Test Signals

Best signals are HDMI link stability across TMDS rates from low pixel clocks to 4K60, analyzer eye/clock behavior, hotplug after repeated enable/disable, audio startup/shutdown RNG toggling on VC5, lane mapping validation on both HDMI ports, and BCM2712-specific suspend/resume or blank/unblank tests. Build coverage should include all exported prototypes referenced by variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_hdmi_phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_hdmi_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_hdmi_regs.h

## Purpose

`vc4_hdmi_regs.h` provides the logical register map and inline MMIO accessors for the VC4/VC5/VC6 HDMI driver. It abstracts hardware-generation register offsets behind `enum vc4_hdmi_field` values so the main driver and PHY code can use logical register IDs while the selected `vc4_hdmi_variant` supplies the correct base block and offset table.

## Important APIs, Types, and Functions

- `enum vc4_hdmi_regs` identifies register base regions: invalid, VC4 HDMI core, VC4 HD block, and VC5-style CEC/CSC/DVP/PHY/RAM/RM blocks.
- `enum vc4_hdmi_field` enumerates all logical HDMI registers used by the driver: audio packet/MAI registers, CEC control/data/interrupt registers, packet RAM, scheduler/timing, FIFO/video control, CSC, hotplug, scrambler, DVP/vector interface, PHY/PLL/RM registers, and format detection registers.
- `struct vc4_hdmi_register` maps a logical field to a base region and offset.
- `_VC4_REG()` and region macros construct register-table entries.
- Static register tables `vc4_hdmi_fields[]`, `vc5_hdmi_hdmi0_fields[]`, `vc5_hdmi_hdmi1_fields[]`, `vc6_hdmi_hdmi0_fields[]`, and `vc6_hdmi_hdmi1_fields[]` encode per-generation/per-port offsets.
- `__vc4_hdmi_get_field_base()` selects the MMIO base pointer from `struct vc4_hdmi`.
- `vc4_hdmi_read()` and `vc4_hdmi_write()` implement checked MMIO access. `HDMI_READ()` and `HDMI_WRITE()` are local convenience macros expecting a `vc4_hdmi` variable in scope.

## Control Flow

Driver code calls `HDMI_READ(field)` or `HDMI_WRITE(field, value)`. The inline accessor validates that runtime PM is not suspended, intentionally fails the current KUnit test if MMIO is attempted, checks the field index against `variant->num_registers`, resolves the `struct vc4_hdmi_register`, maps the base enum to an MMIO pointer, warns on invalid/unknown IDs, and performs `readl()` or `writel()`. Writes also assert `hw_lock` is held.

Resource init in `vc4_hdmi.c` builds debugfs regsets by iterating the same variant register table and filtering entries by base region, so this header is also the source of debugfs register visibility.

## State and Persistence

The header contains static constant register tables only. Live state is in `struct vc4_hdmi`: variant pointer, MMIO bases, platform device for PM status, and hardware lock. No persistent state exists; MMIO writes affect hardware registers until reset/power changes.

## Dependencies and Integration Points

The file includes runtime PM, `vc4_hdmi.h`, and relies on local bitfield helpers and the selected variant records in `vc4_hdmi.c`. It is used by both the HDMI control path and PHY path. Debugfs register dump construction also depends on table names and offsets remaining accurate.

## Risks and Edge Cases

- `enum vc4_hdmi_field` indexes directly into variant arrays; tables must include entries at the correct enum indexes or accesses will resolve to missing/incorrect registers.
- Some logical fields move between base regions by generation; missing MMIO base mapping causes runtime warnings and no-op reads/writes.
- Writes require `hw_lock`; adding write call sites without the lock trips lockdep and risks concurrent register modification.
- Runtime PM warnings catch suspended access but cannot make the access safe; callers must still hold PM references.
- KUnit tests intentionally fail on direct HDMI MMIO, so new tests need mocks or should validate higher-level state without invoking accessors.

## Test Signals

Useful checks include build-time coverage of all variant tables, debugfs regset completeness for each region, lockdep for writes, runtime PM warning absence during hotplug/audio/CEC/modesets, and KUnit tests that verify code avoids direct MMIO in mock contexts. Hardware smoke tests should compare debugfs register dumps against expected offsets for HDMI0/HDMI1 on BCM2711 and BCM2712.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_hdmi_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_hvs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_hvs.c

## Purpose

`vc4_hvs.c` manages the Hardware Video Scaler shared by VC4 display pipelines. The HVS composites/scales/converts framebuffer pixels into output FIFOs consumed by pixel valves or the transposer. This file owns HVS resource allocation, display-list and line-buffer memory managers, channel enable/disable, atomic display-list upload, gamma/LUT handling for older generations, underrun reporting, debugfs, generation-specific hardware initialization, COB allocation, component binding, and platform driver registration.

## Important APIs, Types, and Functions

- Debug and state helpers: `vc4_hvs_dump_state()`, `vc4_hvs_debugfs_underrun()`, `vc4_hvs_debugfs_dlist()`, `vc6_hvs_debugfs_dlist()`, `vc6_hvs_debugfs_upm_allocs()`, and `vc4_hvs_debugfs_init()`.
- Kernel/filter setup: `vc4_hvs_upload_linear_kernel()` installs the Mitchell/Netravali filter into display-list memory.
- Gamma helpers: `vc4_hvs_lut_load()` and `vc4_hvs_update_gamma_lut()` update VC4 gamma SRAM from DRM LUTs.
- FIFO/output helpers: `vc4_hvs_get_fifo_frame_count()` and `vc4_hvs_get_fifo_from_output()` report frame counters and map HVS outputs to FIFOs by generation.
- Channel lifecycle: `vc4_hvs_init_channel()`, `vc6_hvs_init_channel()`, `__vc4_hvs_stop_channel()`, `__vc6_hvs_stop_channel()`, and exported `vc4_hvs_stop_channel()`.
- Atomic hooks used by CRTC/TXP code: `vc4_hvs_atomic_check()`, `vc4_hvs_atomic_begin()`, `vc4_hvs_atomic_enable()`, `vc4_hvs_atomic_disable()`, and `vc4_hvs_atomic_flush()`.
- Underrun handling: `vc4_hvs_mask_underrun()`, `vc4_hvs_unmask_underrun()`, `vc4_hvs_report_underrun()`, and `vc4_hvs_irq_handler()`.
- Allocation/init: `__vc4_hvs_alloc()`, `vc4_hvs_hw_init()`, `vc6_hvs_hw_init()`, `vc4_hvs_cob_init()`, `vc4_hvs_bind()`, `vc4_hvs_unbind()`, and `vc4_hvs_driver`.

## Control Flow

Component bind maps registers, allocates `struct vc4_hvs`, initializes `drm_mm` allocators for display-list memory and LBM, initializes UPM tracking for VC6, selects debugfs regsets based on generation and hardware version, gets firmware/core/disp clocks on VC5+, determines HDMI 2.0/4096x2160 core-clock capability, enables clocks, locates the display-list memory base, initializes the HVS hardware, uploads the scaler kernel, programs COB partitions, and registers the underrun IRQ on pre-VC6 hardware.

Atomic check computes each CRTC's display-list word requirement from active planes, allocates a dlist block in `hvs->dlist_mm`, and stores it in `vc4_crtc_state->mm`. Atomic enable installs the dlist pointer, updates current dlist/event state, and starts the generation-specific HVS channel. Atomic flush writes plane display-list entries in normalized z-order, appends `SCALER_CTL0_END`, updates background-fill policy, updates the active dlist pointer for already-running CRTCs, and reloads gamma when color management changes. Atomic disable stops the assigned channel.

Underrun IRQs read status and control, honor software masking because hardware masks are not always honored, mask the offending channel, increment the underrun counter, log an error, and clear per-channel interrupt status. Debugfs paths expose register state, dlist contents, underrun count, load-tracker toggle, and VC6 UPM allocations.

## State and Persistence

`struct vc4_hvs` owns MMIO base, regset, platform device, core/disp clocks, `drm_mm` allocators for dlist/LBM/UPM, UPM handle/refcount state, display-list memory pointer, maximum core rate, HDMI capability flags, and uploaded filter allocation. `struct vc4_crtc_state` carries per-commit dlist allocation and assigned channel. State is live kernel/hardware state; display-list memory persists in HVS SRAM/MMIO until reallocated or reset, and bootloader display-list entries are intentionally preserved by starting allocation after `HVS_BOOTLOADER_DLIST_END`.

## Dependencies and Integration Points

This file depends on DRM atomic/vblank/debug helpers, Linux component/platform/clock APIs, Raspberry Pi firmware clock queries, `drm_mm`, local plane/CRTC helpers, HVS register macros in `vc4_regs.h`, and VC4 device structures in `vc4_drv.h`. It integrates with `vc4_kms.c` through HVS global state and channel assignment, with `vc4_crtc.c`/`vc4_txp.c` through atomic hooks, and with HDMI mode validation indirectly through HVS core clock capability flags.

## Risks and Edge Cases

- Display-list allocation must exactly match the words written during flush; mismatches trip `WARN_ON_ONCE` and can corrupt following dlist entries.
- Existing bootloader dlist memory is intentionally not overwritten to avoid boot display glitches; changing allocation start risks transition artifacts.
- VC6 uses mock sizes under KUnit because register access is unavailable; production register-size reads must remain outside tests.
- FIFO/output routing is generation-specific and returns `-EPIPE` for disabled/unroutable outputs; callers must handle it.
- Underrun interrupts may fire despite hardware masking, so software control checks are required.
- COB/LBM/UPM sizes are fixed or inferred and can limit high-resolution/multi-plane composition.
- VC6 D0 hardware is detected in bind and mutates `vc4->gen` from GEN_6_C to GEN_6_D, which affects later register paths.

## Test Signals

Signals include KUnit mock allocation paths, PV muxing tests in the VC4 test directory, atomic modesets with multiple planes/z-order/gamma, debugfs dlist/reg dumps, underrun counter behavior, HDMI 2.0 mode availability based on firmware core clock, repeated enable/disable preserving channel state, and real hardware coverage across GEN_4, GEN_5, GEN_6_C, and GEN_6_D.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_hvs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_irq.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_irq.c

## Purpose

`vc4_irq.c` handles V3D engine interrupts for original GEN_4 VC4. It acknowledges binning flush completion, render completion, and binner out-of-memory events; moves jobs between bin/render/done queues; signals fences and wait queues; schedules overflow memory allocation work; and provides install/uninstall/reset helpers used by the V3D platform driver.

## Important APIs, Types, and Functions

- `vc4_overflow_mem_work()` allocates or rotates binner overflow memory and re-enables the OUTOMEM interrupt.
- `vc4_irq_finish_bin_job()` moves the first bin job to the render queue and may submit the next bin job if perfmon compatibility allows.
- `vc4_cancel_bin_job()` restarts binning after reset by stopping perfmon if needed, rotating the current bin job, and submitting the next one.
- `vc4_irq_finish_render_job()` moves the first render job to the done list, updates sequence/fence/wait state, controls perfmon stop/restart behavior, schedules job cleanup, and starts next render or bin work.
- `vc4_irq()` is the IRQ handler for `V3D_INT_OUTOMEM`, `V3D_INT_FLDONE`, and `V3D_INT_FRDONE`.
- Public lifecycle functions are `vc4_irq_enable()`, `vc4_irq_disable()`, `vc4_irq_install()`, `vc4_irq_uninstall()`, and `vc4_irq_reset()`.

## Control Flow

Install prepares wait queues/work items, clears stale interrupts, requests the IRQ, and enables FLDONE/FRDONE. The main IRQ handler reads and acknowledges `V3D_INTCTL`, disables OUTOMEM and schedules work if the binner needs more memory, handles bin completion under `job_lock`, and handles render completion under `job_lock`.

Overflow work runs outside IRQ context under `bin_bo_lock`, gets a free overflow slot, accounts for any previous overflow slot against the current bin job or last render job, writes `V3D_BPOA/BPOS`, clears OUTOMEM, and re-enables OUTOMEM. Render completion increments `finished_seqno`, moves the job to `job_done_list`, manages perfmon lifetimes, signals the DMA fence, wakes job waiters, and schedules deferred job cleanup. Reset acknowledges stale IRQs, enables all driver IRQs, cancels/requeues the current bin job, and finishes a render job if present.

## State and Persistence

State lives in `struct vc4_dev`: IRQ number, V3D presence, job lists, `job_lock`, `bin_bo_lock`, `bin_bo`, overflow allocation bitmaps, `finished_seqno`, wait queue, work items, and perfmon/job/fence references. Interrupt registers persist in V3D hardware until acknowledged or disabled. No disk persistence exists.

## Dependencies and Integration Points

The file depends on V3D register macros, VC4 job scheduler helpers (`vc4_first_bin_job()`, `vc4_move_job_to_render()`, `vc4_submit_next_*()`, etc.), BO allocation helpers, perfmon helpers, DMA fences, wait queues, workqueues, and tracepoints. It is invoked from `vc4_v3d.c` during V3D bind/remove/runtime power transitions and reset.

## Risks and Edge Cases

- Only GEN_4 is supported; every public path warns and returns for later generations.
- OUTOMEM stays asserted until memory is supplied, so the handler disables it and relies on workqueue completion to avoid interrupt storms.
- Overflow memory ownership is tied to in-flight bin/render jobs; wrong slot accounting can leak or prematurely reuse binner memory.
- Perfmon compatibility gates bin/render job submission; mishandling can collect wrong counters or stall queues.
- Fence signaling and job list moves happen under `job_lock`; missing locking would race userspace waits and cleanup work.
- `IRQ_NOTCONNECTED` is reported as `-ENOTCONN`, so probe paths must tolerate platforms without a connected interrupt.

## Test Signals

Signals include V3D job submission tests that observe bin/render completion, DMA fence signaling, wait queue wakeups, overflow-memory pressure scenarios, GPU reset paths invoking `vc4_irq_reset()`, runtime suspend/resume disabling/enabling IRQs, tracepoints for BCL/RCL end IRQs, and lockdep around `job_lock`/`bin_bo_lock`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_kms.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_kms.c

## Purpose

`vc4_kms.c` contains global KMS logic that is not owned by a single plane, CRTC, or encoder. It initializes DRM mode config, vblank, and private atomic objects; implements the global atomic check and commit tail; manages HVS FIFO/channel assignment and muxing; tracks HVS/memory load and core clock requirements; supports VC4 CTM constraints; handles VC4 framebuffer modifier fallback; and coordinates mode-setting order across HVS, pixel valves, HDMI, and planes.

## Important APIs, Types, and Functions

- Private state types: `struct vc4_ctm_state` stores one active CTM matrix and FIFO, while `struct vc4_load_tracker_state` stores aggregate HVS and memory-bus load.
- CTM helpers: `vc4_get_ctm_state()`, private object create/duplicate/destroy functions, `vc4_ctm_s31_32_to_s0_9()`, `vc4_ctm_atomic_check()`, and `vc4_ctm_commit()`.
- HVS global state helpers: `vc4_hvs_get_new_global_state()`, `vc4_hvs_get_old_global_state()`, `vc4_hvs_get_global_state()`, plus HVS private-object create/duplicate/destroy/print/init functions.
- Muxing commit functions: `vc4_hvs_pv_muxing_commit()`, `vc5_hvs_pv_muxing_commit()`, and `vc6_hvs_pv_muxing_commit()`.
- Atomic orchestration: `vc4_atomic_commit_setup()`, `vc4_atomic_commit_tail()`, `vc4_pv_muxing_atomic_check()`, `vc4_load_tracker_atomic_check()`, `vc4_core_clock_atomic_check()`, and `vc4_atomic_check()`.
- Framebuffer and load: `vc4_fb_create()` preserves legacy VC4 tiling behavior when userspace omits modifiers; `vc4_load_tracker_obj_init()` sets up the aggregate load state.
- Entry point: `vc4_kms_load()` configures DRM limits, funcs, helper funcs, vblank, private objects, mode reset, and polling.

## Control Flow

`vc4_kms_load()` enables VC4 load tracking by default on GEN_4, initializes vblank, sets max dimensions by generation, selects mode config funcs (`vc4_fb_create` only for GEN_4), installs atomic helper hooks, initializes CTM/load/HVS private objects, resets mode config, and starts connector polling.

Atomic check first reserves/updates HVS channel assignment in `vc4_pv_muxing_atomic_check()`, validates CTM singleton/range restrictions, runs the DRM atomic helper check, updates load tracker totals from plane state deltas, enforces GEN_4 load limits if enabled, and computes HVS core-clock rate from per-FIFO load and aggregate pixel load.

Commit setup stores pending commit references per active HVS FIFO. Commit tail waits for pending commits on previously used FIFOs, temporarily raises VC5 core/disp clocks for modeset, disables old modesets, commits CTM on GEN_4/5, programs generation-specific HVS/pixelvalve muxing, commits planes, enables modesets, fakes vblank if needed, marks hardware done, waits for flips, cleans up planes, and finally drops VC5 clocks to the new computed steady-state requirement.

## State and Persistence

State is held in DRM private objects: CTM manager, load tracker, and HVS channel manager. `vc4_hvs_state` keeps per-channel `in_use`, `fifo_load`, pending commit references, and `core_clock_rate`. Load tracker state keeps aggregate HVS and memory-bus load. CTM state keeps a pointer to the active DRM CTM blob data and a 1-based FIFO selector. This state is copied and committed through DRM atomic transactions; it does not persist across driver reload.

## Dependencies and Integration Points

This file depends on DRM atomic core/helper APIs, vblank, GEM framebuffer helpers, sorting, clocks, VC4 CRTC/plane state, HVS registers, and local helpers in `vc4_drv.h`/`vc4_regs.h`. It integrates with `vc4_hvs.c` for actual dlist/channel programming, `vc4_crtc.c` and `vc4_txp.c` through assigned channels and encoder topology, HDMI through encoder modeset ordering and HVS clock capability, and VC4 tests through exported HVS global-state helpers.

## Risks and Edge Cases

- HVS FIFO assignment must consider existing enabled CRTCs not touched by the current atomic state; the check avoids pulling inactive CRTCs into the state because that could create page-flip waits on vblanks that never happen.
- FIFO changes require pixelvalve disable/enable, so channels are retained while a CRTC remains enabled.
- The current FIFO assignment heuristic relies on supported routing topologies sorted by HVS output; future routing layouts may need a real matching algorithm.
- CTM hardware supports one FIFO at a time and S0.9 coefficients only; user matrices outside `[-1.0, 1.0]` are rejected.
- Commit tail waits on old FIFO pending commits to prevent reusing a FIFO before previous updates finish; missed references would cause visible glitches.
- VC5 clock boost/drop during commit must match computed load or display underruns/performance waste can result.
- GEN_4 framebuffer creation preserves legacy tiling side-channel state; using generic GEM FB creation there would lose implicit T-tiled modifiers.

## Test Signals

The strongest test signals are KUnit PV muxing tests in `drivers/gpu/drm/vc4/tests`, atomic modeset/page-flip tests across HDMI0/HDMI1/TXP combinations, CTM rejection/commit tests, load tracker debugfs toggling on GEN_4, core-clock rate debug logs on GEN_5, vblank completion under single- and dual-display updates, and legacy framebuffer creation with and without explicit modifiers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_kms.c -->
