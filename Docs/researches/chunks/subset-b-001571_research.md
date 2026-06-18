# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_8_0_sh_mask.h

Chunk: `subset-b-001571`
Covered source range: lines 1-4182 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_8_0_sh_mask.h`

## Purpose

This chunk is the opening portion of the generated AMD DCE 8.0 register field mask header. It is not executable code; it defines C preprocessor constants that describe bit masks and shift positions for 32-bit display-controller registers.

The covered range starts with the DCE 8.0 license and include guard, then defines 4,182 lines of `_MASK` and `__SHIFT` macros for roughly 553 register names. The chunk spans a broad set of DCE 8 display blocks:

- pipe power-gating and display power-gating control for `PIPE0..PIPE5`;
- adaptive backlight modulation and backlight PWM registers, including histogram/luma statistics and ACE thresholds;
- CRTC timing-generator fields for totals, blanking, syncs, trigger events, stereo, snapshots, interrupts, CRC, external sync, static-screen detection, 3D structure, and genlock/swaplock;
- analog DAC output, autodetect, CRC, comparator, power, and FIFO fields;
- performance counter and perfmon control/status/value fields;
- VGA pixel PLL fields and display clock generator fields;
- SMU/DMCU interrupts, clock gating, pixel-rate DTOs, soft resets, symbol clocks, UNIPHY/DCO resets, DVO clock skew, audio DTOs, and PLL programming/status fields;
- DMIF/DCI/MCIF address, arbitration, buffer, memory-power, XDMA, and debug fields;
- DCIO/UNIPHY/AUX impedance calibration, panel power sequencing, backlight PWM, GPU timer, DCIO debug, GPIO/DDC/HPD/power-sequence pad controls, and DVO pad strength/reference controls.

The requested range ends at `DVO_VREF_CONTROL__DVO_VREFSEL__SHIFT`, so this chunk does not include the final `#endif` for the whole header. The later merge lane should reconcile this with the remaining chunks for the same source file.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or runtime APIs in this range. The public interface is the generated macro naming convention used by AMDGPU display code:

- `<REGISTER>__<FIELD>_MASK` is the 32-bit mask for a register field.
- `<REGISTER>__<FIELD>__SHIFT` is the shift count for encoding or decoding that field.
- Companion address macros live in `dce_8_0_d.h` as `mm<REGISTER>` and, for many instance registers, `mm<BLOCK><ID>_<REGISTER>`.

Important macro families in this chunk include:

- `PIPE0_PG_*` through `PIPE5_PG_*`: pipe force-on, gate request, PGFSM read/status, desired/requested power state, and power status fields.
- `DC_IP_REQUEST_CNTL`, `DC_PGFSM_*`, `DC_PGCNTL_STATUS_REG`, and `DCPG_TEST_DEBUG_*`: display-controller power-gating request, configuration, status, and test-debug fields.
- `BL1_PWM_*` and `DC_ABM1_*`: PWM duty/ambient/user/target/current levels, ABM enable/source selection, ACE slope/offset/threshold programming, HGLS register locking/read progress, histogram bin/result registers, luma statistics, overscan pixel values, and ABM debug.
- `CRTC_*`: timing dimensions, sync polarity/control, vertical total selection, interrupt status/ack/mask fields, trigger controls, blanking, interlace/stereo/snapshot state, update locks, test pattern controls, CRC windows/data, external sync interrupts, static-screen control, 3D structure, and GSL genlock/swaplock controls.
- `DAC_*`: analog output enable/source, CRC, sync tristate, autodetect, force output, powerdown, comparator, power control, DFT, and FIFO calibration/status fields.
- `PERFCOUNTER_*` and `PERFMON_*`: event selection, increment/run/stop control, state, current-value comparison, interrupt controls, and high/low value registers.
- `VGA25_PPLL_*`, `VGA28_PPLL_*`, `VGA41_PPLL_*`, `PLL_*`, and `DENTIST_DISPCLK_CNTL`: pixel/display PLL divisors, spread-spectrum, delta-sigma, ID clock, lock/calibration/status, update lock/control, DTO controls, and display/ref clock divider change handshakes.
- `DCCG_*`, `DISPCLK_*`, `SCLK_*`, `PIXCLK*`, `DP_DTO*`, `SYMCLK*`, `DVOACLK*`, and audio DTO registers: clock gating, soft reset, pixel-rate selection, DP DTO phase/modulo, symbol-clock enable/source forcing, DVO clock skew, and audio DTO source/module/phase control.
- `DMIF_*`, `PIPE*_ARBITRATION_CONTROL3`, `PIPE*_MAX_REQUESTS`, `DCI_*`, `MCIF_*`, and `DC_XDMA_INTERFACE_CNTL`: display memory interface addressing, burst/arbitration, underflow/status, buffer allocation, MCIF buffer manager slots/addresses/status, memory power states, light sleep, and XDMA flip signaling.
- `UNIPHY_IMPCAL_*`, `AUXP_IMPCAL`, `AUXN_IMPCAL`, `DCIO_IMPCAL_*`, and `UNIPHY_IMPCAL_PSW_*`: impedance calibration enable/readback/error/override/period and per-link calibration values for physical display links and AUX pads.
- `LVTMA_PWRSEQ_*`, `BL_PWM_*`, `DC_GPU_TIMER_*`, `DCO_CLK_*`, `DCIO_DEBUG*`: panel power-sequence targets/delays/status, legacy backlight PWM controls, display GPU timer capture/read, DCO clock/ramp control, and debug mux/data fields.
- `DC_GPIO_*`: generic GPIO, DVO data, DDC1-6, DDCVGA, sync, genlock/swaplock, HPD, power-sequence, pad strength, I2C pad, and PHY AUX pad controls.
- `DVO_STRENGTH_CONTROL` and `DVO_VREF_CONTROL`: DVO pad drive strength, voltage mode, reference power, and reference select fields.

## Control Flow

This header has no internal control flow. It contributes constants that are compiled into DCE 8 register tables and read/modify/write helper paths.

The normal runtime flow in consumers is:

1. A DCE 8 source includes `dce_8_0_d.h` for register addresses and this header for field masks/shifts.
2. Per-block register tables combine `mm*` addresses with these mask/shift constants.
3. Generic register helpers encode values by shifting them by `__SHIFT`, clearing destination bits with `_MASK`, writing the resulting MMIO value, and sometimes polling or acknowledging status bits.

Concrete integration examples in this tree:

- `display/dc/resource/dce80/dce80_resource.c` includes this header and constructs DCE 8 timing-generator, stream-encoder, link-encoder, AUX, I2C, memory-input, transform, panel, clock-source, DMCU, ABM, and hardware-sequencer objects. Its `*_shift` and `*_mask` tables are populated with macro-list expansions such as `XFM_COMMON_MASK_SH_LIST_DCE80`, `SE_COMMON_MASK_SH_LIST_DCE80_100`, `DMCU_MASK_SH_LIST_DCE80`, `HWSEQ_DCE8_MASK_SH_LIST`, and `MI_DCE8_MASK_SH_LIST`.
- `display/dc/hwss/dce/dce_hwseq.h` maps `CRTC_DCFE_CLOCK_CONTROL__CRTC_DCFE_CLOCK_ENABLE` and DCE 8 pixel-rate fields into hardware-sequencer masks used when enabling clocks and programming pipe pixel rates.
- `display/dc/dce/dce_mem_input.h` maps DCE 8 memory-input and DMIF field masks through `MI_DCE8_MASK_SH_LIST`, then `dce80_resource.c` pairs those with `mmDMIF_PG*` and memory-controller registers.
- `display/dc/gpio/dce80/hw_factory_dce80.c` uses `DC_HPD1_INT_STATUS` and `DC_HPD1_TOGGLE_FILT_CNTL` shift/mask macros as the common HPD field layout for HPD1-6 register tables, and uses DDC/GPIO mask lists for DDC, I2C pad, and generic GPIO pins.
- `display/dc/irq/dce80/irq_service_dce80.c` includes this header while building DCE 8 interrupt source descriptions for vblank, HPD, HPD RX, and related display IRQs.
- Legacy non-DC paths such as `amdgpu/dce_v8_0.c`, `amdgpu/cik.c`, `amdgpu/gmc_v7_0.c`, `amdgpu/gfx_v7_0.c`, `pm/powerplay/smumgr/ci_smumgr.c`, and `pm/powerplay/hwmgr/ci_baco.c` include this header for direct MMIO programming on CIK/DCE8-era ASICs.

## State And Persistence Behavior

The header itself is stateless. It allocates no memory, performs no I/O, has no initialization order, and persists only as compiled constants.

The hardware fields represented here are persistent GPU register state until changed by the display driver, firmware/SMU, BIOS tables, a display block reset, a power-gating transition, suspend/resume, hot-plug activity, or a full ASIC reset. Major state categories include:

- pipe and display power-gating desired/requested/actual states;
- ABM/backlight state, double-buffer lock state, luma/histogram readback state, missed-frame latches, and PWM duty-cycle settings;
- timing-generator state including active timing, vtotal min/max control, interrupt latches/acks, stereo/3D frame state, CRC windows/results, static-screen status, and genlock/swaplock configuration;
- DAC analog output, autodetect, comparator, CRC, powerdown, and FIFO calibration state;
- clock-generation state including clock gates, soft resets, PLL divisors, spread spectrum, lock status, DTO phase/modulo, symbol-clock enable/source state, and clock-change handshakes;
- DMIF/DCI/MCIF state including memory-address configuration, buffer allocation, underflow/status flags, request limits, memory power state, MCIF buffer-manager slots, and XDMA flip-pending state;
- DCIO physical-link calibration state and AUX/DDC/HPD/GPIO pad state;
- panel power-sequence state, backlight GPIO/PWM state, HPD sense and DDC line direction/output/readback state.

Many status and interrupt fields are acknowledge or clear-style fields (`*_ACK`, `*_CLEAR`, `*_INT_CLEAR`, missed-frame clear, calibration error ack). This header does not encode access semantics; consumers must preserve the register specification's write-one-to-clear, lock/update, and polling requirements.

## Dependencies And Integration Points

The immediate dependency is the C preprocessor. Practical use requires the companion DCE 8 address header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_8_0_d.h`

Closely related generated headers are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_8_0_enum.h`
- neighboring DCE generation headers such as `dce_6_0_sh_mask.h`, `dce_10_0_sh_mask.h`, `dce_11_0_sh_mask.h`, and `dce_12_0_sh_mask.h`, which share many field names but can differ in register coverage and bit layout.

Primary local DCE 8 consumers include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce80/dce80_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce80/dce80_timing_generator.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce80/dce80_hwseq.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dce80/irq_service_dce80.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce80/hw_factory_dce80.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce80/hw_translate_dce80.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dce100/dce_clk_mgr.c`, whose comment notes that some register shifts and masks are used for both DCE100 and DCE80.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/dce_v8_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/cik.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v7_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v7_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/ci_smumgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/ci_baco.c`

Generic display helpers that consume these mask/shift tables include `reg_helper.h`, DCE timing-generator helpers, memory-input helpers, stream/link encoder helpers, AUX/I2C/GPIO helpers, ABM/panel helpers, clock-source helpers, and IRQ-service helpers. Those consumers provide the type checking and call flow; this generated header provides only numeric constants.

## Risks And Edge Cases

The highest risk is silent hardware misprogramming. These macros are untyped constants, so the compiler cannot verify that a mask is paired with the intended `mm*` register address, that a caller bounds a value before shifting, or that a status/ack/control bit is used with the correct access semantics.

Repeated instance blocks are especially error-prone. Pipe, CRTC, DP DTO, DMIF buffer, MCIF buffer, UNIPHY link, DDC, HPD, and GPIO register families use nearly identical field layouts across instances. A wrong prefix or register table index can compile cleanly while touching the wrong physical pipe, connector, AUX/DDC path, HPD pin, or buffer slot.

Power and clock fields are timing-sensitive. `PIPE*_PG_*`, `DCFE*_SOFT_RESET`, `DCI_SOFT_RESET`, `DCCG_*`, `PLL_*`, `SYMCLK*`, `DCO_*`, `DCI_MEM_PWR_*`, and `DCO_MEM_POWER_STATE*` fields can hang display bring-up, prevent clock changes, break resume, or lose display output if writes are reordered, not polled, or applied to an active pipe without the expected quiesce sequence.

Display timing fields have visible failure modes. Incorrect CRTC totals, blanking/sync fields, update locks, vtotal controls, stereo fields, CRC/test-pattern settings, or genlock/swaplock fields can cause modeset failure, unstable vblank timing, flicker, bad CRC capture, or multi-display synchronization faults.

Connector and pad controls affect external behavior. DDC, HPD, AUX pad, GPIO pull-up/down, drive-strength, and LVTMA power-sequence fields can cause EDID read failures, missing hot-plug events, IRQ storms, incorrect panel/backlight sequencing, or electrical-level problems on real connectors.

Memory-interface fields can corrupt display fetch behavior. DMIF address configuration, tiling/interleave fields, buffer allocation/status, request limits, underflow bits, MCIF buffer addresses, and XDMA flip fields must remain synchronized with framebuffer layout, memory-controller configuration, and pipe programming.

High-bit masks such as `0x80000000` require unsigned 32-bit treatment. Consumers should use existing register helper macros and fixed-width types rather than signed arithmetic or ad hoc shifts.

Because this chunk is generated register documentation, drift against `dce_8_0_d.h`, ASIC register specs, or neighboring generation headers may not be caught by normal compilation. A stale field value can build successfully and fail only on DCE 8 hardware or on specific connector/timing/power-management paths.

## Test Signals

Useful validation signals include:

- compile coverage for DCE 8 and shared DCE translation units that include `dce_8_0_sh_mask.h`, especially `dce80_resource.c`, `dce80_timing_generator.c`, `dce80_hwseq.c`, `irq_service_dce80.c`, `hw_factory_dce80.c`, `hw_translate_dce80.c`, `dce_clk_mgr.c`, `dce_v8_0.c`, `cik.c`, `gmc_v7_0.c`, `gfx_v7_0.c`, `ci_smumgr.c`, and `ci_baco.c`;
- generated-header consistency checks across the complete source file, ensuring every `_MASK` field has a matching `__SHIFT`, no duplicate macro definitions conflict, and every register family has a matching `mm*` address in `dce_8_0_d.h`;
- table-construction checks for DCE 8 resource objects, verifying that each mask/shift table entry comes from the intended register generation and that instance arrays have the expected six-pipe/six-connector coverage;
- modeset and vblank tests across all available CRTC instances, including timing programming, vtotal min/max, blanking/sync polarity, update locks, interrupts, CRC capture, test patterns, stereo/3D, and static-screen behavior;
- suspend/resume, runtime power, and BACO-style power-transition tests that exercise pipe power gating, display clock gating, soft resets, PLL lock/relock, memory light sleep, and display wakeup;
- HPD and DDC validation across every connector, covering connect/disconnect, delayed sense, debounce/toggle filter delays, HPD RX IRQs, rapid cable toggles, EDID reads, I2C-over-DDC GPIO direction/readback, and suspend/resume with monitors attached and detached;
- DisplayPort/DVI/HDMI link tests that cover symbol-clock selection, PLL/DTO programming, stream encoder source selection, PHY/UNIPHY calibration state, AUX pad behavior, and hot-plug paths;
- ABM, backlight, and panel-power tests on supported panels, checking PWM levels, ABM enable/source selection, register lock/update pending behavior, missed-frame clear paths, power-sequence delays, and BLON/DIGON/SYNCEN GPIO state;
- DMIF/MCIF stress tests with multi-pipe scanout, tiling/interleave variants, page flips, underflow detection, MCIF buffer switching, and XDMA flip-pending propagation;
- hardware readback tests after representative safe writes, confirming shifted values occupy only the intended masked bits and adjacent fields remain unchanged.
