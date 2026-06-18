# sources/distributed-fs/ceph-client/include/uapi/linux/kcov.h

## Purpose
`kcov.h` defines ioctl controls and constants for kernel code coverage collection used by fuzzers and test harnesses.

## Important APIs, Types, and Functions
`struct kcov_remote_arg` configures remote coverage collection with trace mode, area size, handle count, and handle array pointer. Ioctls are `KCOV_INIT_TRACE`, `KCOV_ENABLE`, `KCOV_DISABLE`, and `KCOV_REMOTE_ENABLE`. Coverage modes include disabled, trace PC, and trace comparison. Comparison records use `KCOV_CMP_CONST`, `KCOV_CMP_SIZE`, and `KCOV_CMP_MASK`. `kcov_remote_handle(subsys, inst)` composes subsystem and instance bits, with common and USB subsystem constants.

## Control Flow
Userspace opens kcov, initializes an mmap-able trace area, enables a mode, runs target syscalls or remote work, then disables and reads coverage records from the shared buffer.

## State and Persistence
Coverage buffers and mode are per kcov fd/task or configured remote handle. State lasts until disabled or fd close; trace contents are transient and overwritten by subsequent runs.

## Dependencies and Integration Points
It includes `<linux/types.h>`. Integration points include syzkaller-style fuzzers, kernel instrumentation, USB/common remote coverage, and mmap shared buffers.

## Risks and Test Signals
Tests should cover buffer sizing, mode transitions, remote handle bit packing, max handle count, comparison record encoding, concurrent remote coverage, and cleanup on task/fd exit.
