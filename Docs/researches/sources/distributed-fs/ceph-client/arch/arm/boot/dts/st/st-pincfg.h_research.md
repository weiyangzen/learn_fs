<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/st/st-pincfg.h -->
# sources/distributed-fs/ceph-client/arch/arm/boot/dts/st/st-pincfg.h

## Purpose
Devicetree include header defining ST pin-control bit encodings for alternate functions, direction, pull-up/open-drain behavior, clock retiming, and retime clock selection. Board DTS files include it to express pin mux and electrical configuration in readable macros.

## Important APIs/types/functions
- Alternate function constants: `ALT1` through `ALT7`.
- Direction and electrical flags: `OE`, `PU`, `OD`, `IN`, `IN_PU`, `OUT`, `BIDIR`, `BIDIR_PU`.
- Retime/clock flags: `RT`, `INVERTCLK`, `CLKNOTDATA`, `DOUBLE_EDGE`, `CLK_A` through `CLK_D`, `BYPASS`, `SE_NICLK_IO`, `SE_ICLK_IO`, `DE_IO`, `ICLK`, and `NICLK`.

## Control flow
No executable flow. The C preprocessor substitutes macros into DTS pin configuration cells before DTC encodes them into the DTB.

## State and persistence behavior
The header defines a persistent ABI between DTS files and ST pinctrl drivers: the encoded bit positions become values in built DTBs. Changing bit values would alter board pin behavior at boot.

## Dependencies and integration points
Used by ST pinctrl DTS nodes and consumed by the corresponding kernel pinctrl driver that interprets these bitfields. It depends only on preprocessor inclusion and the shared bit layout expected by firmware/kernel pin configuration code.

## Risks and edge cases
Bit overlap or value drift can silently misconfigure pins. The `CLK_A` value is zero, so absence of a clock-select macro may be indistinguishable from selecting clock A. User-friendly direction macros combine electrical flags but do not validate SoC-specific pin capabilities.

## Test signals
Compile all ST DTBs with `make ARCH=arm dtbs`; run `dtbs_check` against ST pinctrl bindings; boot affected boards and verify muxed peripherals, pull-ups, bidirectional buses, and retimed clock/data pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/st/st-pincfg.h -->
