# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_sh_mask.h lines 44554-47050

## Purpose

This chunk is generated AMD DCN 3.6 register field metadata. It contains no executable C logic; it publishes preprocessor constants for bit positions and bit masks inside DCN 3.6 MMIO registers. Runtime display code includes this file with the matching `dcn_3_6_0_offset.h` register-offset header, then uses helper macros to populate typed register/shift/mask tables for GPIO, DDC/AUX, panel power sequencing, DSC, IRQ, and DMUB register access.

The requested range covers the tail of `DC_GPIO_GENLK_MASK`, complete DC GPIO/HPD/AUX/DDC pad-control families, complete reserved UNIPHY macro-control fields for UNIPHY instances 1 through 4, complete `PWRSEQ0` and `PWRSEQ1` panel/backlight power-sequencer fields, complete DSC instance 0 DSCC/DSCCIF/top/perfmon fields, and the beginning of DSC instance 1 DSCC PPS range fields. It contains 2,094 `#define` lines, evenly paired as 1,047 `__SHIFT` macros and 1,047 `_MASK` macros.

Although this path is under a local `ceph-client` source mirror, the content is AMDGPU display-driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocation paths, or direct I/O calls in this range. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: the least significant bit position for a field inside a 32-bit register.
- `<REGISTER>__<FIELD>_MASK`: the unshifted register-bit mask for the same field.

Major macro families in this chunk:

- `DC_GPIO_GENLK_*`, `DC_GPIO_HPD_*`, `DC_GPIO_DRIVE_STRENGTH_S0/S1`, `DC_GPIO_DRIVE_TXIMPSEL`, `DC_GPIO_RXEN`, and `DC_GPIO_PULLUPEN`: GPIO field masks for genlock clock/vsync, swaplock lines, HPD pins 1-6, generic GPIO drive strength, transmit impedance selection, receive enables, and pull-up enables.
- `PHY_AUX_CNTL` and `DC_GPIO_AUX_CTRL_0` through `DC_GPIO_AUX_CTRL_5`: AUX/DDC electrical controls, including AUX pad wake and receive selection, fall slew selection, spike filter controls, comparator and bias selection, termination, DP/DN swap, hysteresis tuning, AUX control nibbles, voltage output tuning, DDC pad I2C mode, 1.2 V I2C rail enables, and DDC pad I2C control.
- `AUXI2C_PAD_ALL_PWR_OK`: per-PHY AUX/I2C pad power-good status bits for PHY1 through PHY6.
- `DCIO_UNIPHY{1,2,3,4}_UNIPHY_MACRO_CNTL_RESERVED0` through `...RESERVED57`: full-width reserved fields for the repeated UNIPHY macro-control register space. Each register is represented as one `UNIPHY_MACRO_CNTL_RESERVED` field with shift `0x0` and mask `0xFFFFFFFFL`.
- `PWRSEQ0_*` and `PWRSEQ1_*`: GPIO routing and pad control for `VARY_BL`, `DIGON`, and `BLON`, plus panel power-sequence enable/target/state/status, power-up and power-down delays, reference dividers, backlight PWM control, PWM period, double-buffer/register lock behavior, and spare fields.
- `DSCC0_*`: DSC compressor-client configuration, status, interrupt/status enable fields, DSC PPS programming registers 0-22, memory power control, squared-error counters, max absolute error counters, rate-buffer fullness counters, rate-control buffer fullness counters, and debug bus rotation fields.
- `DSCCIF0_*` and `DSC_TOP0_*`: DSC client-interface input format/dimensions/underflow status and top-level DSC clock/debug gating fields.
- `DC_PERFMON19_*`: DSC-local perf counter control, counter state, perfmon control, interrupt threshold control/status, and counter value registers.
- `DSCC1_*`: the beginning of the second DSC compressor-client field set, from config/status/interrupts through `DSCC1_DSCC_PPS_CONFIG21`; this chunk ends mid-register at `DSCC1_DSCC_PPS_CONFIG21__RANGE_MIN_QP11_MASK`.

## Control Flow

This header has no runtime control flow. Its constants participate in generated register-table setup:

1. DCN 3.6 resource, IRQ, and DMUB code includes `dcn_3_6_0_offset.h` and `dcn_3_6_0_sh_mask.h`.
2. Register-list macros paste register and field names into symbols such as `DSCC0_DSCC_PPS_CONFIG0__DSC_VERSION_MINOR__SHIFT`, `DC_GPIO_AUX_CTRL_5__DDC_PAD1_I2CMODE_MASK`, or `PWRSEQ1_PANEL_PWRSEQ_CNTL__PANEL_BLON_MASK`.
3. Helper macros such as `FD_MASK`, `FD_SHIFT`, `DSC_REG_LIST_SH_MASK_DCN35`, `REG_FIELD_LIST`, and GPIO/DDC `*_MASK_SH_LIST_*` macros copy these compile-time constants into runtime register descriptors.
4. Driver code later uses those descriptors with register read/modify/write helpers to program AUX/DDC pads, HPD handling, panel power rails, backlight PWM, DSC PPS state, DSC memory power, DSC interrupts/status, and perf counters.

The macros do not encode ordering. Callers must still sequence pad power, AUX/DDC setup, HPD acknowledgment, panel power delays, PWM lock/update behavior, DSC clocking, PPS double-buffering, memory power, interrupt clear/enable, and suspend/resume restore paths correctly.

## State And Persistence Behavior

The chunk stores no software state and persists nothing itself. It describes fields in MMIO-backed hardware state.

Hardware state represented by the GPIO/AUX portion includes HPD mask/data/enable pins, genlock and swaplock GPIO pins, pad drive and impedance controls, receiver and pull-up enables, AUX electrical tuning, DDC I2C pad mode, DDC 1.2 V rail enables, and AUX/I2C PHY power-good status. These values affect connector detection, EDID/DDC transactions, DisplayPort AUX access, and external sync/swaplock signaling.

Hardware state represented by the power-sequencer portion includes panel power target state, actual panel power-sequence state bits, panel sync/digital/backlight output polarity and overrides, configurable power-up/power-down delays, reference time bases, backlight PWM duty and period, frame-start-synchronized PWM update behavior, and register lock/update-pending/readback behavior. These fields are persisted by hardware only while the relevant display block remains powered and not reset.

Hardware state represented by the DSC portion includes DSC slice and PPS configuration, rate-control buffer model values, quantization and BPG ranges, memory low-power controls, error/statistic counters, rate-buffer fullness counters, top-level DSC clock/debug controls, underflow status, and perfmon counters. Status and interrupt fields may be sticky, read-only, write-one-to-clear, self-clearing, or double-buffered depending on the hardware register; this generated header does not distinguish those access semantics.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.6 register database and must match:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_offset.h` for the corresponding register addresses and base indices.
- Shared display register helpers such as `reg_helper.h`, `dmub_reg.h`, GPIO register-list macros, and DSC register-list macros that token-paste register and field names into these constants.

Concrete include sites and consumers visible in this tree:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn36/dcn36_resource.c` includes this header and initializes DSC shift/mask tables with `DSC_REG_LIST_SH_MASK_DCN35(__SHIFT)` and `DSC_REG_LIST_SH_MASK_DCN35(_MASK)`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn36.c` includes this header and fills DMUB DCN register masks/shifts through `DMUB_DCN35_FIELDS()`, `FD_MASK`, and `FD_SHIFT`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn36/irq_service_dcn36.c` includes the same offset/mask pair for DCN 3.6 IRQ register programming and HPD source handling.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/ddc_regs.h` consumes `PHY_AUX_CNTL` and `DC_GPIO_AUX_CTRL_5` field masks in `DDC_MASK_SH_LIST_DCN2`, especially `AUXn_PAD_RXSEL` and `DDC_PADn_I2CMODE`.
- DSC code shared with DCN 2.x/3.x consumes the `DSCC0_*` and `DSCC1_*` PPS/config/status masks when constructing `struct dcn20_dsc_registers`, shift tables, and mask tables.

The final per-file research should merge adjacent chunks before making complete claims about all DCN 3.6 GPIO, UNIPHY, PWRSEQ, DSC, or perfmon field coverage, because this range starts inside `DC_GPIO_GENLK_MASK` and ends inside `DSCC1_DSCC_PPS_CONFIG21`.

## Risks And Edge Cases

- Generated mask/shift drift is the main risk. These constants are untyped and compile cleanly even when a mask points at the wrong bit; failures surface as incorrect hardware programming.
- Shift/mask pairing must remain exact. Every visible field in this chunk has both a `__SHIFT` and `_MASK` macro; losing one half breaks token-pasted initialization paths or silently corrupts field encode/decode.
- HPD/AUX/DDC fields are connector-sensitive. Wrong pad mode, receive select, pull-up, power-good, or I2C-control masks can cause hotplug storms, missing displays, AUX timeouts, EDID read failures, or failures limited to one connector index.
- PWRSEQ fields are sequencing-sensitive. Incorrect panel delay, target-state, override, polarity, or PWM lock masks can cause blank internal panels, backlight flicker, unsafe rail timing, stuck update-pending bits, or resume regressions.
- DSC PPS fields are format-sensitive. Wrong BPP, slice geometry, native 4:2:0/4:2:2, rate-control, range QP, BPG offset, or memory-power masks can produce compressed-stream corruption, link bandwidth failures, or errors only at high pixel clocks.
- Status/interrupt fields require correct access semantics. This header names occurrence and enable bits but does not document read-only, sticky, W1C, or self-clearing behavior; callers must get that from hardware specs and established driver code.
- Reserved UNIPHY fields are full-width and repeated across many registers. Treating them as ordinary safe programming fields outside vendor-guided flows can alter undocumented PHY behavior.
- The chunk boundary is artificial. The first register block is incomplete from earlier lines, and the last `DSCC1` PPS block continues in the next chunk.

## Test Signals

Useful validation combines generated-header consistency checks with hardware behavior:

- Build AMDGPU/DC with DCN 3.6 support enabled; macro rename or deletion should fail in `dcn36_resource.c`, `dmub_dcn36.c`, IRQ service code, GPIO/DDC helpers, and DSC register-table initialization.
- Mechanically verify this range still contains paired `__SHIFT` and `_MASK` macros for each field and that the count remains balanced for generated DCN 3.6 metadata.
- Diff the chunk against AMD's authoritative DCN 3.6 register database and neighboring generated headers where equivalent DPCS/DCN blocks are expected to remain stable.
- Exercise connector paths that use HPD1-HPD6, DDC1-DDC6, AUX1-AUX6, and GPIO genlock/swaplock pins: hotplug, unplug, EDID reads, DP AUX DPCD reads/writes, suspend/resume, and low-power wake.
- Validate panel power and backlight behavior on embedded panels using PWRSEQ0/PWRSEQ1: power-up/power-down timing, digital/backlight enable polarity, PWM duty/period programming, frame-start synchronized updates, and resume restore.
- Enable DSC on capable displays and test modes that stress PPS programming: high resolution, high refresh, native 4:2:0/4:2:2 where supported, multi-slice modes, link-rate changes, and repeated modesets.
- Watch kernel logs and display diagnostics for HPD storms, AUX timeouts, EDID failures, stuck PWRSEQ or PWM update-pending status, underflow interrupts, DSC rate-buffer overflow/underflow, DSC end-of-frame errors, visual corruption, and resume failures.

## Cross-Chunk Notes

Earlier chunks own the beginning of `DC_GPIO_GENLK_MASK` and likely the broader DCIO/GPIO register field namespace before this line range. Later chunks continue `DSCC1_DSCC_PPS_CONFIG21` and the remaining DCN 3.6 mask namespace. The merge/reconciliation lane should combine this report with adjacent chunks before producing the final source-tree-aligned per-file research document for `dcn_3_6_0_sh_mask.h`.
