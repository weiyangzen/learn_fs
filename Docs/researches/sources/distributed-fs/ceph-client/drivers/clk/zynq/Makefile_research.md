<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/zynq/Makefile -->
# sources/distributed-fs/ceph-client/drivers/clk/zynq/Makefile

## Purpose

The Zynq Makefile builds Zynq-specific clock controller and PLL support.

## Important APIs, Types, And Functions

It links `clkc.o` and `pll.o` unconditionally for the selected Zynq clock directory.

## Control Flow

Kbuild includes both the SLCR clock-controller setup and the Zynq PLL implementation so `clkc.c` can call `clk_register_zynq_pll()`.

## State And Persistence Behavior

No runtime state exists here. Object inclusion determines early boot clock availability.

## Dependencies And Integration Points

It integrates Zynq common clock support into the kernel build.

## Risks And Test Signals

The main risk is separating `pll.o` from `clkc.o`. Build Zynq configs and boot a `xlnx,ps7-clkc` DT to validate early clock init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/zynq/Makefile -->
