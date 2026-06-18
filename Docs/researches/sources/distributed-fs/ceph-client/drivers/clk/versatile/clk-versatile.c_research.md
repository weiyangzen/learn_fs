<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/versatile/clk-versatile.c -->
# sources/distributed-fs/ceph-client/drivers/clk/versatile/clk-versatile.c

## Purpose

`clk-versatile.c` provides early ICST auxiliary oscillator setup for ARM Integrator core modules and Versatile boards.

## Important APIs, Types, And Functions

It defines ICST parameter descriptors for Integrator core-module auxiliary oscillator and Versatile LCD auxiliary oscillator. `cm_osc_setup()` maps the parent core-module/system-controller base once, obtains the parent clock name, registers an ICST clock with `icst_clk_register()`, and adds a simple OF provider.

## Control Flow

Two `CLK_OF_DECLARE()` entries match `arm,integrator-cm-auxosc` and `arm,versatile-cm-auxosc`, each passing the relevant descriptor into `cm_osc_setup()`.

## State And Persistence Behavior

The static `cm_base` mapping persists for all such clocks. Hardware VCO and lock registers persist actual rate state.

## Dependencies And Integration Points

It depends on OF early clock setup, parent node MMIO mapping, CCF, and ICST helpers. It is the legacy non-syscon path for older reference-board DTs.

## Risks And Test Signals

Risks are missing parent nodes, one shared `cm_base` for multiple nodes, and descriptor offsets that differ by board. Test early boot on Integrator and Versatile boards and set/recalc auxiliary oscillator rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/versatile/clk-versatile.c -->
