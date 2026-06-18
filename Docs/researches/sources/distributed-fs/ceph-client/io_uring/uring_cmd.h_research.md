# sources/distributed-fs/ceph-client/io_uring/uring_cmd.h

Purpose: declares internal uring_cmd helpers and defines cached async command state.

Important APIs/types/functions: `struct io_async_cmd` stores an `iou_vec` and two SQE-sized slots for copied 128-byte SQEs. Prototypes cover command prep/issue, SQE copy, cleanup, cancel scanning, multishot CQE32 posting, cache free, and poll multishot arming.

Control flow: none in the header.

State and persistence: per-command async vector/copy state is defined here and freed through `io_cmd_cache_free()`.

Dependencies/integration: includes `linux/io_uring/cmd.h` and io_uring types; consumed by command opcode dispatch and driver-facing helper code.

Risks/test signals: struct sizing must handle SQE128 safely. Tests with `IORING_SETUP_SQE128`, fixed vector command imports, and command cleanup validate it.
