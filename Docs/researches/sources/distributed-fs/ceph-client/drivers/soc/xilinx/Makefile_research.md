# sources/distributed-fs/ceph-client/drivers/soc/xilinx/Makefile

## Purpose
This Makefile maps Xilinx SoC Kconfig options to object files.

## Important APIs, Types, And Functions
It builds `zynqmp_power.o` for `CONFIG_ZYNQMP_POWER` and `xlnx_event_manager.o` for `CONFIG_XLNX_EVENT_MANAGER`.

## Control Flow
Kbuild includes each object based on its config symbol.

## State And Persistence
There is no runtime state; the Makefile affects build selection only.

## Dependencies And Integration Points
It depends on Xilinx Kconfig symbols and matching source files.

## Risks And Test Signals
Risks are object/symbol drift. Test signals are expected object build under enabled configs.
