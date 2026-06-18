<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/xilinx/Makefile -->
# sources/distributed-fs/ceph-client/drivers/clk/xilinx/Makefile

## Purpose

The Xilinx Makefile maps Xilinx clock Kconfig symbols to driver objects.

## Important APIs, Types, And Functions

`CONFIG_XILINX_VCU` builds `xlnx_vcu.o`; `CONFIG_COMMON_CLK_XLNX_CLKWZRD` builds `clk-xlnx-clock-wizard.o`.

## Control Flow

Kbuild links selected platform drivers according to tristate values.

## State And Persistence Behavior

No runtime state exists. The Makefile determines module object composition.

## Dependencies And Integration Points

It integrates Xilinx VCU and Clocking Wizard drivers with common clock builds.

## Risks And Test Signals

Risks are minimal beyond config mismatch. Build both objects as built-in and modules and verify module names match Kconfig help.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/xilinx/Makefile -->
