# Research: subset-b-003600

Grouped research report for Intel i915 SDVO and Synopsys PHY/HDMI PLL display files. Each section preserves the original source path and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_sdvo.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_sdvo.c

## Purpose
`intel_sdvo.c` implements the i915 SDVO encoder and connector support for legacy Intel display platforms. It discovers SDVO devices over the SDVO I2C command interface, initializes DVI/HDMI, VGA, TV, and LVDS connector variants, performs mode validation and mode computation, programs input/output detailed timings, manages SDVO port registers, handles EDID/DDC proxying through the SDVO control bus switch, exposes TV/LVDS enhancement properties, and controls HDMI infoframes/audio over SDVO host buffers.

## Important APIs, Types, And Functions
- Core private types: `struct intel_sdvo`, `struct intel_sdvo_connector`, `struct intel_sdvo_connector_state`, and `struct intel_sdvo_ddc`.
- Exported entry points: `intel_sdvo_init()` creates an SDVO encoder and connector set; `intel_sdvo_port_enabled()` reads SDVO register enable/pipe state for hardware readout.
- SDVO command transport: `intel_sdvo_read_byte()`, `__intel_sdvo_write_cmd()`, `intel_sdvo_write_cmd()`, `intel_sdvo_read_response()`, `intel_sdvo_set_value()`, and `intel_sdvo_get_value()`.
- Timing helpers: `intel_sdvo_get_dtd_from_mode()`, `intel_sdvo_get_mode_from_dtd()`, `intel_sdvo_set_input_timing()`, `intel_sdvo_set_output_timing()`, `intel_sdvo_get_preferred_input_mode()`, and `intel_sdvo_get_pixel_multiplier()`.
- Modeset hooks: `intel_sdvo_compute_config()`, `intel_sdvo_pre_enable()`, `intel_enable_sdvo()`, `intel_disable_sdvo()`, `pch_post_disable_sdvo()`, `intel_sdvo_get_hw_state()`, and `intel_sdvo_get_config()`.
- HDMI/audio helpers: `intel_sdvo_check_supp_encode()`, `intel_sdvo_set_encode()`, `intel_sdvo_set_colorimetry()`, `intel_sdvo_write_infoframe()`, `intel_sdvo_read_infoframe()`, `intel_sdvo_compute_avi_infoframe()`, `intel_sdvo_set_avi_infoframe()`, `intel_sdvo_enable_audio()`, and `intel_sdvo_disable_audio()`.
- Connector operations: `intel_sdvo_detect()`, `intel_sdvo_get_modes()`, `intel_sdvo_mode_valid()`, atomic property get/set/check callbacks, and state duplication.
- Initialization helpers: DVI/TV/analog/LVDS init functions, `intel_sdvo_output_setup()`, `intel_sdvo_select_i2c_bus()`, `intel_sdvo_select_ddc_bus()`, `intel_sdvo_init_ddc_proxy()`, and property creation helpers.

## Control Flow
Initialization starts in `intel_sdvo_init()`. The function validates the port, allocates `struct intel_sdvo`, initializes the DRM encoder, selects the target I2C address from VBT or defaults, forces bit-banged GMBUS, probes the first 0x40 SDVO registers, installs encoder hooks, reads device capabilities and colorimetry support, creates three DDC proxy adapters, and calls `intel_sdvo_output_setup()`. Output setup filters unsupported capability bits, probes outputs in a priority order, and creates connector objects by output type. It then reads the input clock range and leaves the encoder cloneable mask disabled because SDVO often requires special input timings.

SDVO command control is register-oriented over I2C. Write commands push argument bytes into descending SDVO argument registers, write an opcode, then poll the status register. `intel_sdvo_read_response()` handles pending and target-not-specified status with short microsecond retries followed by longer millisecond retries, then reads return registers. The DDC proxy path is lock-sensitive: `intel_sdvo_ddc_proxy_xfer()` must issue `SDVO_CMD_SET_CONTROL_BUS_SWITCH` immediately before forwarding the caller's I2C messages to the underlying GMBUS adapter.

Mode computation first forces RGB 8 bpc, handles PCH split pipe bpp, and for TV/LVDS asks the SDVO device to synthesize a preferred input timing from the desired output timing. TV modes also use fixed i9xx PLL parameters for supported clock ranges. HDMI detection affects audio, limited range, colorimetry, AVI infoframe generation, and pixel replication. Pre-enable then pushes TV/LVDS enhancement properties, maps SDVO input 0 to the selected output, programs output timing, chooses HDMI or DVI encoding, writes AVI infoframes, sets TV format when needed, programs input timing and clock rate multiplier, and writes the SDVO port register with pipe select and legacy hardware workaround bits. Enable turns on the port, waits two vblanks, checks trained inputs, and activates outputs. Disable clears active outputs and the SDVO enable bit, with an IBX transcoder-A workaround for disabled pipe-B ports.

Detection reads `GET_ATTACHED_DISPLAYS` after targeting the connector output. TMDS connectors additionally validate a digital EDID; other outputs use EDID matching when available and otherwise trust the attached-display response. Mode enumeration is EDID-driven for DVI/HDMI/VGA, panel-driven for LVDS, and command/table-driven for TV.

## State And Persistence
All state is in kernel memory and device registers. `struct intel_sdvo` stores the SDVO command address, selected I2C adapter, three DDC proxy adapters, device capabilities, colorimetry support, pixel clock limits, hotplug activation bits, and the saved `dtd_sdvo_flags` needed because SDVO flags are lost in mode-to-DTD round trips. Connector state stores TV enhancement values in the atomic connector state, while standard DRM TV state stores saturation/contrast/hue/brightness and selected TV legacy mode. Hardware state persists in SDVO command registers, SDVO port registers, host buffers, active outputs, and DDC bus switch state until reprogrammed or disabled.

## Dependencies And Integration Points
This file integrates with DRM connector/encoder helpers, i915 atomic modesetting, Intel display register access, GMBUS/I2C, VBT SDVO mappings, EDID helpers, HDMI infoframe helpers, audio ELD handling, panel fixed-mode helpers, hotplug support, FIFO underrun controls, and legacy platform display registers. It consumes definitions from `intel_sdvo_regs.h` and exposes only the declarations in `intel_sdvo.h`.

## Risks And Edge Cases
SDVO devices are old and often non-compliant, so the command path has retries, fallbacks, and debug logging. The control bus switch must immediately precede proxied DDC transfers; inserting other I2C traffic can break EDID reads. Mode computation has side effects because it programs output timings during atomic check to query preferred input timing. TV clock handling accepts only narrow fixed ranges. Pixel multiplier state differs by platform and is cross-checked against encoder state. The code deliberately falls back to bit-banged GMBUS because normal GMBUS is unreliable for SDVO. Connector cleanup on partial output setup is necessary because failed setup can leave registered connectors. HDMI support is inferred by probing encode support, so a broken response can affect connector type and audio/color property exposure.

## Test Signals
Useful test signals include SDVO detection on ports B/C and PCH-split systems, EDID reads through each proxied DDC bus, DVI/HDMI connector type selection, TV format enumeration, LVDS fixed-mode selection from VBT and EDID fallback, mode validation around min/max clocks and double-clock modes, HDMI AVI infoframe and ELD round trips, hotplug re-enable after one-shot interrupts, suspend/resume hardware readout, and state-verify warnings for pixel multiplier mismatch. Runtime logs to watch include failed SDVO commands, failed timing programming, missing capabilities, unknown output type, and PLL clock range errors for SDVO TV.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_sdvo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_sdvo.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_sdvo.h

## Purpose
`intel_sdvo.h` is the small public interface for i915 SDVO support. It declares the SDVO initialization and hardware-state query functions used by the rest of the display driver and provides no-op inline stubs when the i915 build guard is absent.

## Important APIs, Types, And Functions
- Forward declarations: `enum pipe`, `enum port`, and `struct intel_display`.
- `intel_sdvo_port_enabled(struct intel_display *display, i915_reg_t sdvo_reg, enum pipe *pipe)` reads whether an SDVO port register is enabled and reports the selected pipe.
- `intel_sdvo_init(struct intel_display *display, i915_reg_t reg, enum port port)` probes and registers one SDVO encoder instance.
- The `#ifdef I915` section exposes real declarations for the driver build; the `#else` section returns `false` from both helpers.

## Control Flow
The header has no runtime control flow beyond compile-time selection. Callers can unconditionally reference SDVO helpers; non-i915 builds compile to disabled behavior through static inline stubs.

## State And Persistence
The header owns no state. It passes through `intel_display`, MMIO register, port, and pipe pointer arguments to the implementation.

## Dependencies And Integration Points
It depends on Linux integer types and `i915_reg_defs.h` for `i915_reg_t`. It is included by SDVO implementation code and by broader display initialization/readout code that probes legacy ports.

## Risks And Edge Cases
The stubbed functions always return false, so code compiled without `I915` must not expect SDVO hardware support. The `pipe` output in the real implementation is meaningful even when a port is disabled, but the stub does not write it; callers in stubbed builds must tolerate that.

## Test Signals
Build coverage should include both `I915` and non-`I915` configurations. Runtime testing is covered through `intel_sdvo.c`; this header's direct signal is successful compilation and correct call-site behavior when SDVO support is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_sdvo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_sdvo_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_sdvo_regs.h

## Purpose
`intel_sdvo_regs.h` defines the SDVO command protocol ABI used by `intel_sdvo.c`: output flag bits, packed command request/reply structures, SDVO I2C register offsets, command opcodes, status codes, timing structures, TV format/resolution structures, panel/enhancement structures, DDC bus switch bits, and HDMI/audio host-buffer command definitions.

## Important APIs, Types, And Functions
- Output bit definitions: `SDVO_OUTPUT_TMDS*`, `SDVO_OUTPUT_RGB*`, `SDVO_OUTPUT_CVBS0`, `SDVO_OUTPUT_SVID0`, `SDVO_OUTPUT_YPRPB0`, `SDVO_OUTPUT_LVDS*`, and `SDVO_OUTPUT_LAST`.
- Core packed structs: `struct intel_sdvo_caps`, `struct intel_sdvo_dtd`, `struct intel_sdvo_pixel_clock_range`, `struct intel_sdvo_preferred_input_timing_args`, `struct intel_sdvo_get_trained_inputs_response`, and `struct intel_sdvo_in_out_map`.
- Command transport registers: `SDVO_I2C_ARG_*`, `SDVO_I2C_OPCODE`, `SDVO_I2C_CMD_STATUS`, `SDVO_I2C_RETURN_*`, and `SDVO_I2C_VENDOR_BEGIN`.
- Command status codes: success, not supported, invalid argument, pending, target-not-specified, and scaling-not-supported.
- Timing and clock commands: target input/output, input/output timing part 1/2, preferred input timing, pixel clock ranges, and clock multiplier commands.
- TV/LVDS/enhancement structures: TV format bitfields, SDTV/HDTV resolution request/reply structures, panel power sequencing, backlight/ambient light replies, and enhancement limit/value commands.
- HDMI/audio host-buffer definitions: encode/colorimetry, pixel replication, audio state bits, host-buffer index/data/tx-rate commands, AVI/ELD buffer indices, and `SDVO_NEED_TO_STALL`.

## Control Flow
The header has no executable logic. Its structure mirrors the SDVO command interface: clients write arguments into `SDVO_I2C_ARG_*`, issue an opcode, poll `SDVO_I2C_CMD_STATUS`, and read `SDVO_I2C_RETURN_*`. Timing commands are split into part 1 and part 2 records, matching the packed `intel_sdvo_dtd` layout used by the implementation.

## State And Persistence
The file defines the wire/storage shape of SDVO state but does not own state. Most structs are `__packed` because their layout is directly exchanged with SDVO firmware over I2C. Bitfields represent persistent device capabilities, supported formats, selected power states, enhancement values, and host-buffer state once programmed.

## Dependencies And Integration Points
It depends on Linux compiler and integer types. It is consumed by `intel_sdvo.c` and any SDVO command code needing exact opcode and layout definitions. The DTD layout intentionally aligns with EDID detailed timing concepts, and HDMI definitions integrate with DRM HDMI infoframe/audio handling through the implementation.

## Risks And Edge Cases
Packed bitfield layout is compiler- and endian-sensitive, so changes must be treated as ABI changes against SDVO firmware. Several comments indicate legacy typos or quirks, such as zero-based host-buffer size and output-function ordering assumptions. Command result lengths must match `BUILD_BUG_ON()` checks in the implementation. Adding new opcodes without debug-name coverage reduces diagnostic quality but not functionality.

## Test Signals
Compile-time `BUILD_BUG_ON()` checks in `intel_sdvo.c` validate key structure sizes. Runtime signals include successful capability reads, timing programming, TV format/resolution queries, enhancement property creation, HDMI AVI/ELD host-buffer transfers, and correct command-status handling for unsupported features.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_sdvo_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_snps_hdmi_pll.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_snps_hdmi_pll.c

## Purpose
`intel_snps_hdmi_pll.c` computes Synopsys HDMI TMDS PLL register state for i915 display PHYs. It contains fixed-point interpolation and curve-based charge-pump calculations, then emits either DG2-style `struct intel_mpllb_state` values or C10 PHY `struct intel_c10pll_state` byte fields for arbitrary HDMI pixel clocks.

## Important APIs, Types, And Functions
- `struct pll_output_params` is the internal normalized PLL result: spread settings, dividers, charge-pump values, refclk scalar, fractional-N fields, phase-mix enable, multiplier, V2I selection, and VCO frequency bucket.
- `interp()` performs scaled integer interpolation between curve points.
- `get_ana_cp_int_prop()` calculates and clamps analog charge-pump integer/proportional values from VCO frequency, reference clock, V2I point, and curve tables.
- `compute_hdmi_tmds_pll()` is the common algorithm that derives datarate, TX clock divider, VCO, fractional-N quotient/remainder/denominator, multiplier, VCO bucket, and charge-pump settings.
- `intel_snps_hdmi_pll_compute_mpllb()` fills `struct intel_mpllb_state` using DG2/SNPS register field macros and a 100 MHz reference clock.
- `intel_snps_hdmi_pll_compute_c10pll()` fills `struct intel_c10pll_state` using C10 PLL field macros and a 38.4 MHz reference clock.

## Control Flow
Both public compute functions supply PHY-specific curve tables and reference-clock constants, call `compute_hdmi_tmds_pll()`, then pack the normalized results into their target hardware state structure. The common algorithm multiplies `pixel_clock` by 10000 to get data rate, chooses V2I and TX divider based on whether the rate is below the roughly 10 GHz threshold, derives VCO and fractional-N values against the post-scaled reference clock, chooses a curve segment and VCO bucket, computes analog charge-pump values, and returns all register fields through `pll_output_params`.

## State And Persistence
The file has no static mutable state. It writes only into caller-provided PLL state structures. The resulting state persists later when other display code writes the fields to hardware registers; this file itself performs no MMIO.

## Dependencies And Integration Points
It depends on Linux math helpers, register field macros from `intel_cx0_phy_regs.h` and `intel_snps_phy_regs.h`, display PLL state types from `intel_display_types.h`, and the public declarations in `intel_snps_hdmi_pll.h`. `intel_snps_phy.c` calls the MPLLB calculator as a fallback when an HDMI pixel clock is not present in the precomputed DG2 table. C10 PHY code calls the C10 calculator for newer PHY state construction.

## Risks And Edge Cases
The algorithm is entirely fixed-point integer math with large constants, so overflow, unintended truncation, and off-by-one rounding are the main risks. `compute_hdmi_tmds_pll()` assumes the chosen VCO falls into one of the hardcoded curve segments; clocks outside the intended HDMI range could leave an invalid segment default. `do_div()` mutates its dividend, so surrounding calculations must use the intended post-division remainder semantics. The fractional remainder adjustment subtracts `(rem >> 15)`, which is hardware-specific and easy to regress. MPLLB and C10 packing use different field widths and shifts, so any common algorithm change requires verification against both targets.

## Test Signals
Good signals include golden-register tests for common HDMI clocks such as 25.175, 27, 74.25, 148.5, 297, and 594 MHz; comparison with the precomputed DG2 table where entries overlap; C10-specific register byte checks; HDMI modeset tests at table and non-table pixel clocks; and warnings or black-screen regressions around PLL lock failures in the caller.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_snps_hdmi_pll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_snps_hdmi_pll.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_snps_hdmi_pll.h

## Purpose
`intel_snps_hdmi_pll.h` declares the public Synopsys HDMI PLL calculators used by i915 display PHY code.

## Important APIs, Types, And Functions
- Forward declarations: `struct intel_c10pll_state` and `struct intel_mpllb_state`.
- `intel_snps_hdmi_pll_compute_mpllb(struct intel_mpllb_state *pll_state, u64 pixel_clock)` calculates DG2/SNPS MPLLB state for an HDMI pixel clock.
- `intel_snps_hdmi_pll_compute_c10pll(struct intel_c10pll_state *pll_state, u64 pixel_clock)` calculates C10 PLL state for an HDMI pixel clock.

## Control Flow
The header has no runtime control flow. It provides a narrow interface so callers can compute PLL state without depending on the internal curve tables and helper math in the C file.

## State And Persistence
The header owns no state. Its functions write into caller-owned state structures.

## Dependencies And Integration Points
It depends on Linux integer types. It is included by `intel_snps_hdmi_pll.c` and by PHY code that needs HDMI PLL fallback or C10 PLL programming.

## Risks And Edge Cases
The API does not return a status code, so callers assume the supplied pixel clock is in range and that the calculator can always produce a usable state. Any future validation failure would require an API shape change or a sentinel in the output state.

## Test Signals
Build coverage should ensure both callers see complete declarations. Runtime correctness is validated through the C file's golden PLL-state tests and HDMI modeset PLL-lock behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_snps_hdmi_pll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_snps_phy.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_snps_phy.c

## Purpose
`intel_snps_phy.c` implements i915 support for Synopsys display PHYs, primarily DG2-era PHYs with per-port MPLLB PLLs. It waits for PHY calibration, manages PSR lane power requests, programs lane signal levels, stores large precomputed MPLLB register tables for DP/eDP/HDMI link rates, selects or computes PLL state for a CRTC/encoder, enables/disables the MPLLB in the modeset sequence, reads back hardware state, derives port clock from register state, and verifies software state against hardware.

## Important APIs, Types, And Functions
- PHY utility entry points: `intel_snps_phy_wait_for_calibration()`, `intel_snps_phy_update_psr_power_state()`, and `intel_snps_phy_set_signal_levels()`.
- Precomputed table groups: `dg2_dp_100_tables`, `dg2_edp_tables`, and `dg2_hdmi_tables`, each containing `struct intel_mpllb_state` records for known link or pixel clocks.
- PLL selection and computation: `intel_mpllb_tables_get()` chooses the table family; `intel_mpllb_calc_state()` copies a matching table record or calls `intel_snps_hdmi_pll_compute_mpllb()` for unmatched HDMI clocks.
- PLL programming: `intel_mpllb_enable()` writes MPLLB CP, divider, SSC, and fractional-N registers, enables the platform PLL register, asserts force-enable, and waits for lock.
- PLL shutdown: `intel_mpllb_disable()` clears PLL enable, clears MPLLB force-enable, and waits for lock/ack clear.
- Readback and verification: `intel_mpllb_calc_port_clock()`, `intel_mpllb_readout_hw_state()`, and `intel_mpllb_state_verify()`.

## Control Flow
At platform startup or resume, `intel_snps_phy_wait_for_calibration()` scans all PHYs and records any SNPS PHY whose DP TX acknowledgment bits fail to clear within 25 ms. During link setup, `intel_snps_phy_set_signal_levels()` asks the encoder for the buffer translation table, derives per-lane DDI levels, and writes main/pre/post cursor values to `SNPS_PHY_TX_EQ()`. PSR power transitions write the lane disable power-state request field only for SNPS encoders.

Modeset PLL state calculation first classifies the output as eDP, DP, or HDMI. DP/eDP require exact table matches by `crtc_state->port_clock`; HDMI first checks the table and then falls back to the algorithm in `intel_snps_hdmi_pll.c`. Enabling writes all MPLLB register fields before asserting PLL enable, then writes the divider register again with `SNPS_PHY_MPLLB_FORCE_EN` so the PLL stays running through lane programming and Type-C disconnect cases. Disabling reverses enable and force-enable, then waits for the lock bit to clear. Readout reads all programmed fields and masks out force-enable because software state intentionally excludes that runtime bit. Verification runs for active DG2 CRTC modeset/fastset commits, reads hardware state, and warns on mismatches for each MPLLB field including firmware-controlled ref range.

## State And Persistence
Most state is static const table data. Runtime mutable state lives in hardware registers, `crtc_state->dpll_hw_state.mpllb`, and `display->snps.phy_failed_calibration`. The MPLLB force-enable bit is a transient runtime addition to the divider register and is stripped during readout. `ref_control` is read for sanity checking but treated as firmware-controlled rather than directly programmed by this file.

## Dependencies And Integration Points
The file integrates with Intel DDI code, DDI buffer translation data, display register access, platform PLL enable registers, PHY/encoder mapping helpers, CRTC atomic state, SNPS register definitions, and the HDMI PLL calculator. It is part of the modeset path for outputs whose PHY uses MPLLB instead of the shared DPLL framework.

## Risks And Edge Cases
The register tables are large magic-value tables; incorrect values can cause PLL unlocks or link instability and are hard to diagnose from code review alone. DP/eDP reject unsupported clocks with `-EINVAL`, while HDMI accepts algorithm-generated values for non-table clocks, creating different failure modes by output type. The hardcoded `if (0)` branch in port-clock calculation means the current implementation always assumes a 100 MHz reference clock there, which must match supported hardware. Force-enable must be applied only after the PLL samples divider values. Calibration failure tracking prevents later output setup on affected PHYs, so false positives can disable working ports. Verification only runs for DG2 active modeset/fastset commits and will not catch every runtime drift.

## Test Signals
Signals include PHY calibration failure masks, per-lane signal level register writes for trained link levels, DP/eDP link-rate table selection at RBR/HBR/UHBR and eDP-specific rates, HDMI table selection and algorithm fallback, PLL lock success after enable, lock clear after disable, readout-derived port clock matching requested port clock, and `intel_mpllb_state_verify()` mismatch warnings. Hardware tests should cover DG2 DP, eDP, HDMI, and Type-C disconnect/reconnect paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_snps_phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_snps_phy.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_snps_phy.h

## Purpose
`intel_snps_phy.h` declares the i915 Synopsys PHY and MPLLB functions used across display initialization, modeset, PSR, and state verification code.

## Important APIs, Types, And Functions
- Forward declarations: `enum phy`, `struct intel_atomic_state`, `struct intel_crtc`, `struct intel_crtc_state`, `struct intel_display`, `struct intel_encoder`, and `struct intel_mpllb_state`.
- PHY helpers: `intel_snps_phy_wait_for_calibration()`, `intel_snps_phy_update_psr_power_state()`, and `intel_snps_phy_set_signal_levels()`.
- MPLLB lifecycle: `intel_mpllb_calc_state()`, `intel_mpllb_enable()`, `intel_mpllb_disable()`, and `intel_mpllb_readout_hw_state()`.
- Clock/state helpers: `intel_mpllb_calc_port_clock()` and `intel_mpllb_state_verify()`.

## Control Flow
The header has no runtime control flow. It groups related SNPS PHY operations so platform and encoder code can call into the implementation without depending on table internals.

## State And Persistence
The header owns no state. The declared functions operate on display-global state, encoder/CRTC atomic state, hardware registers, and caller-provided MPLLB state structures.

## Dependencies And Integration Points
It depends on Linux integer types and i915 display type declarations. It is included by SNPS PHY implementation and by modeset/encoder code that needs PHY calibration, signal-level programming, MPLLB programming, or verification.

## Risks And Edge Cases
Callers must respect modeset ordering: calculate state before enable, do not readout into uninitialized storage assumptions, and call verification only when an active new encoder exists. The header does not encode platform constraints; incorrect calls on non-SNPS encoders must be guarded by callers or implementation checks.

## Test Signals
Compile-time coverage catches signature mismatches. Runtime coverage comes from SNPS PHY modeset tests, PSR power-state tests, and MPLLB state verification paths declared here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_snps_phy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_snps_phy_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_snps_phy_regs.h

## Purpose
`intel_snps_phy_regs.h` defines MMIO address helpers and bitfield masks for Synopsys PHY MPLLB, reference control, PSR lane power requests, and per-lane TX equalization registers.

## Important APIs, Types, And Functions
- Base address helpers: `_SNPS_PHY_A_BASE`, `_SNPS_PHY_B_BASE`, `_SNPS_PHY(phy)`, `_SNPS2(phy, reg)`, `_MMIO_SNPS(phy, reg)`, and `_MMIO_SNPS_LN(ln, phy, reg)`.
- MPLLB registers and fields: `SNPS_PHY_MPLLB_CP`, `SNPS_PHY_MPLLB_DIV`, `SNPS_PHY_MPLLB_FRACN1`, `SNPS_PHY_MPLLB_FRACN2`, `SNPS_PHY_MPLLB_SSCEN`, `SNPS_PHY_MPLLB_SSCSTEP`, `SNPS_PHY_MPLLB_DIV2`, and fields for force enable, divider clocks, V2I, VCO bucket, PMIX, DP2 mode, word div2, TX clock divider, reference divider, multiplier, HDMI divider, fractional-N, and SSC.
- Reference control: `SNPS_PHY_REF_CONTROL` and `SNPS_PHY_REF_CONTROL_REF_RANGE`.
- PSR power request: `SNPS_PHY_TX_REQ` and `SNPS_PHY_TX_REQ_LN_DIS_PWR_STATE_PSR`.
- Per-lane TX EQ: `SNPS_PHY_TX_EQ(ln, phy)` with main, post-cursor, and pre-cursor fields.

## Control Flow
The header has no executable control flow. Its macros convert PHY and lane indices into MMIO registers and provide masks used with `REG_FIELD_PREP()`, `REG_FIELD_GET()`, and read-modify-write helpers in the PHY implementation.

## State And Persistence
The file defines persistent hardware register locations and bit layouts but owns no software state. Values written through these macros persist in display PHY registers until changed by software, firmware, or reset.

## Dependencies And Integration Points
It depends on `intel_display_reg_defs.h` for MMIO and register field macros. It is consumed by `intel_snps_phy.c`, `intel_snps_hdmi_pll.c`, and any i915 code packing or reading Synopsys PHY PLL/equalization state.

## Risks And Edge Cases
Incorrect base address arithmetic or field masks directly corrupts MMIO programming. Lane addressing assumes a 0x10 stride. Some fields are read for verification but firmware-controlled, so software must not assume ownership of every bit. The macros currently cover PHY A/B base mapping through `_PHY()` and need review if future platforms expose more SNPS PHY instances or different offsets.

## Test Signals
Signals include register read/write traces during MPLLB enable/disable, field round-trip checks through `REG_FIELD_GET()`, successful PLL lock, correct TX EQ values per lane, PSR request field transitions, and absence of `intel_mpllb_state_verify()` mismatch warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_snps_phy_regs.h -->
