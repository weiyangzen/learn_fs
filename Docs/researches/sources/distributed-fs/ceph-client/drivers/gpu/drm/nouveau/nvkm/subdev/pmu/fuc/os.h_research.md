# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/fuc/os.h

## Purpose
Defines PMU falcon firmware process names, message identifiers, MEMX opcodes, and I2C message bitfield layouts shared by fuc firmware and host-side expectations.

## Important APIs, Types, And Functions
Defines process IDs `PROC_KERN`, `PROC_IDLE`, `PROC_HOST`, `PROC_MEMX`, `PROC_PERF`, `PROC_I2C_`, and `PROC_TEST`; message IDs such as `KMSG_FIFO`, `KMSG_ALARM`, `MEMX_MSG_INFO`, `MEMX_MSG_EXEC`; MEMX script opcodes; and I2C bitfield ranges.

## Control Flow
No executable C control flow exists.

## State And Persistence
No state is stored. The constants form a persistent ABI between generated firmware and driver message construction/parsing.

## Dependencies And Integration Points
Included by fuc assembly sources and reflected by host PMU/MEMX/I2C code. Changing values affects generated headers and runtime PMU protocol.

## Risks And Test Signals
Risks include ABI drift, bitfield range mistakes, and process ID mismatch. Test by regenerating all fuc firmware headers and running PMU MEMX/I2C command/reply paths.
