<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/versatile/Makefile -->
# sources/distributed-fs/ceph-client/drivers/clk/versatile/Makefile

## Purpose

The Versatile Makefile maps Kconfig symbols to ARM reference-design clock objects.

## Important APIs, Types, And Functions

`CONFIG_CLK_ICST` builds the ICST math, ICST CCF wrapper, and legacy Versatile/Integrator setup. `CONFIG_INTEGRATOR_IMPD1` builds the IM-PD1 ICST driver. `CONFIG_CLK_SP810` builds the SP810 timer mux. `CONFIG_CLK_VEXPRESS_OSC` builds the VExpress OSC platform driver.

## Control Flow

Kbuild links the selected objects. Some are early built-in OF providers, while `clk-vexpress-osc.o` may be modular according to Kconfig.

## State And Persistence Behavior

No runtime state is held. The object grouping ensures `icst.o` is present whenever `clk-icst.o` needs its exported rate conversion functions.

## Dependencies And Integration Points

It integrates with common clock Kbuild and the ARM Integrator/Versatile/VExpress platform code.

## Risks And Test Signals

The key risk is separating `icst.o` from `clk-icst.o`, which would break symbol resolution. Build each config combination and check platform boot logs for clock provider registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/versatile/Makefile -->
