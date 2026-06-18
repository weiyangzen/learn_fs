# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/ref/gh100/dev_riscv_pri.h

## Purpose
Defines the GH100 RISC-V CPU control halted status bit.

## Important APIs, Types, And Functions
Exports `NV_PRISCV_RISCV_CPUCTL`, `NV_PRISCV_RISCV_CPUCTL_HALTED`, and true/false/init values.

## Control Flow
No executable flow. Firmware boot code polls or reads the halted bit to determine processor state.

## State And Persistence
The halted bit is live hardware state and changes as firmware starts, stops, or resets the RISC-V core.

## Dependencies And Integration Points
Integrated with Falcon/RISC-V/FSP boot code and low-level PRI register access.

## Risks
Polling this bit without timeouts can hang boot. Misinterpreting polarity can proceed while firmware is stopped or wait while it is running.

## Test Signals
Firmware startup logs, timeout handling, and CPUCTL register traces validate usage.
