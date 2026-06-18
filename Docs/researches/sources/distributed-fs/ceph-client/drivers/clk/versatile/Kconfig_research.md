<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/versatile/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/clk/versatile/Kconfig

## Purpose

This Kconfig menu exposes clock drivers for ARM reference designs: ICST VCO clocks, SP810 timer-clock muxes, and Versatile Express OSC generators.

## Important APIs, Types, And Functions

`CLK_ICST` selects `REGMAP_MMIO` for ICST-backed Integrator/RealView/Versatile clocks. `CLK_SP810` defaults on ARM Versatile Express and supports SP810 timer clock parent selection. `CLK_VEXPRESS_OSC` depends on `VEXPRESS_CONFIG`, selects `REGMAP_MMIO`, and can be built as a module.

## Control Flow

Kconfig controls which objects in the sibling Makefile are compiled. The menu depends on I/O memory and ARM/ARM64 or compile-test support.

## State And Persistence Behavior

No runtime state exists here. The selected symbols determine whether early `CLK_OF_DECLARE` providers and platform drivers are available.

## Dependencies And Integration Points

It integrates with Linux common clock Kconfig, ARM reference platform configs, and module/built-in selection for VExpress OSC.

## Risks And Test Signals

Risks are missing default selections for platforms that need early clocks and dependency mismatches around `VEXPRESS_CONFIG`. Test all three symbols with `COMPILE_TEST`, and boot affected Integrator, RealView, Versatile, and VExpress DTs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/versatile/Kconfig -->
