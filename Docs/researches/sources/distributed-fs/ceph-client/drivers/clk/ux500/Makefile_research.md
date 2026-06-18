<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ux500/Makefile -->
# sources/distributed-fs/ceph-client/drivers/clk/ux500/Makefile

## Purpose

This Makefile builds all Ux500 clock-provider objects into the kernel when the parent directory selects the Ux500 clock support. It groups reusable clock types, reset support, U8500 DT clock definitions, and the ABX500 companion-clock driver.

## Important APIs, Types, And Functions

The object list is the contract: `clk-prcc.o`, `clk-prcmu.o`, and `clk-sysctrl.o` provide registration helpers; `reset-prcc.o` exposes PRCC reset control; `u8500_of_clk.o` creates the U8500 clock tree and DT providers; `abx500-clk.o` registers AB8500/AB8505 clocks.

## Control Flow

Kbuild links these objects unconditionally under this directory with `obj-y`. Runtime ordering is then controlled by initcall levels in the C files: OF clock declaration for U8500 core clocks and `arch_initcall()` for ABX500 clocks.

## State And Persistence Behavior

The Makefile has no runtime state. Its practical persistence effect is that all Ux500 clock and reset code is built in, not modular, so early boot consumers can depend on it.

## Dependencies And Integration Points

It integrates with the parent Linux clock-driver Kbuild. There are no per-symbol config switches here, so dependency control must happen above this directory.

## Risks And Test Signals

Removing any object can break exported helper references or DT provider registration. Build tests with Ux500 enabled should link all helper symbols; boot should show U8500 PRCMU/PRCC providers and ABX500 clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ux500/Makefile -->
