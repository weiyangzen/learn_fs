# sources/distributed-fs/ceph-client/io_uring/uring_cmd.c

Purpose: implements the generic passthrough `uring_cmd` opcode used by drivers, including fixed-buffer import, cancellation, IOPOLL, multishot command support, and CQE32 completion.

Important APIs/types/functions: `io_uring_cmd_prep()`, `io_uring_cmd()`, `io_uring_cmd_sqe_copy()`, `io_uring_cmd_cleanup()`, `__io_uring_cmd_done()`, `io_uring_cmd_mark_cancelable()`, `io_uring_try_cancel_uring_cmd()`, `io_uring_cmd_import_fixed()`, `io_uring_cmd_import_fixed_vec()`, `io_uring_cmd_issue_blocking()`, `io_cmd_poll_multishot()`, `io_uring_cmd_buffer_select()`, `io_uring_mshot_cmd_post_cqe()`, and `io_uring_cmd_post_mshot_cqe32()`.

Control flow: prep validates command flags, fixed/multishot combinations, buffer selection requirements, command opcode, and allocates async command state. Issue checks file support and security, derives issue flags for SQE128/CQE32/compat/IOPOLL, calls the driver `file->f_op->uring_cmd()`, and interprets queued, reissue, multishot, and immediate completion returns. Driver completion removes cancelable state, sets result and optional CQE32 extra fields, recycles async state, and either marks IOPOLL completed, defers completion, or queues task_work.

State and persistence: state includes per-request command flags, copied SQE storage, async vector cache, cancelable hlist membership, fixed buffer node refs through import, IOPOLL flags, and multishot provided-buffer state. Driver side effects depend on the consuming file operation.

Dependencies/integration: integrates with driver `uring_cmd` and `uring_cmd_iopoll` file ops, LSM `security_uring_cmd`, fixed buffers from `rsrc`, provided buffers, poll, task_work, cancellation, CQE32/mixed CQE support, and io-wq blocking escalation.

Risks/test signals: risks include driver completion races with cancellation, unsupported IOPOLL cancellation, SQE lifetime if drivers need copied SQE, fixed-buffer range validation, and multishot buffer/CQE overflow behavior. Test with NVMe/driver passthrough, fixed and fixed-vector imports, cancelable commands, IOPOLL commands, CQE32 output, multishot poll commands, and security denial.
