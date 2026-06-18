# sources/distributed-fs/ceph-client/include/linux/io_uring/cmd.h

Purpose: This header defines the in-kernel uring command interface used by drivers, notably block and device drivers, to implement `IORING_OP_URING_CMD` style operations.

Important APIs, types, and functions: `struct io_uring_cmd` carries file, SQE pointer, command opcode, flags, and a 32-byte private data area. Helpers include `io_uring_sqe_cmd`, `io_uring_sqe128_cmd`, `io_uring_cmd_to_pdu`, fixed-buffer import functions, `__io_uring_cmd_done`, task-work scheduling helpers, cancelable marking, blocking issue, multishot buffer selection/CQE posting, `io_uring_cmd_get_task`, context handle access, `io_uring_cmd_done`, `io_uring_cmd_done32`, and bvec buffer registration.

Control flow: Drivers parse command payloads from the SQE, optionally import fixed buffers, issue work inline/blocking/task-work, mark commands cancelable if needed, and complete through CQE posting helpers. Disabled io_uring builds return `-EOPNOTSUPP` or no-op as appropriate.

State and persistence: Command state is embedded in the io_uring request. Driver private state fits in `pdu` or external allocations. Context handles point back to the ring context for per-ring driver resources.

Dependencies and integration points: Depends on io_uring core types, UAPI SQE layout, block multiqueue requests, iov iterators, task work, and buffer selection infrastructure.

Risks: Payload size macros use build-time checks but drivers must choose the right 64-byte or 128-byte SQE mode. Completion must use issue flags supplied by core, not hard-coded values. Multishot commands must manage buffer lifetime and CQE32 mode correctly.

Test signals: Validate command payload parsing, PDU size checks, fixed buffer import, cancellation, deferred task completions, CQE32 completion, multishot buffer recycling, disabled-config behavior, and bvec register/unregister lifetimes.
