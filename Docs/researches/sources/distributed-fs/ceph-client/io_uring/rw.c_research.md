# sources/distributed-fs/ceph-client/io_uring/rw.c

Purpose: implements io_uring read/write opcodes, including vectored IO, fixed-buffer IO, multishot reads, metadata/protection-information attributes, buffered retry, and IOPOLL completion.

Important APIs/types/functions: `struct io_rw` is the command payload. Prep entry points include `io_prep_read/write()`, `io_prep_readv/writev()`, fixed variants, and `io_read_mshot_prep()`. Issue/completion entry points include `io_read()`, `io_write()`, `io_read_fixed()`, `io_write_fixed()`, `io_read_mshot()`, `io_req_rw_complete()`, `io_rw_fail()`, `io_do_iopoll()`, and `io_rw_cache_free()`.

Control flow: prep allocates `io_async_rw`, imports user or fixed buffers, stores ioprio/rwf flags/position, and sets kiocb completion callbacks. Read/write issue initializes file mode and IOCB flags, applies NOWAIT/IOPOLL rules, verifies ranges, invokes `read_iter`/`write_iter` or legacy loops, then completes inline, queues async completion, returns `-EAGAIN` for io-wq retry, or arms buffered page wait retry. Partial reads restore iter state and may retry with `IOCB_WAITQ`; partial writes update `bytes_done` and reissue. IOPOLL walks `ctx->iopoll_list`, calls file or uring_cmd poll hooks, batches completions, and flushes CQEs.

State and persistence: request state includes `io_async_rw` iter/vector buffers, bytes completed, selected/provided buffers, metadata iter state, current file position, kiocb flags, iopoll timestamps, and cleanup/cache state. Persistent external effects are file reads/writes, file position updates, fsnotify notifications, and write accounting.

Dependencies/integration: depends on VFS iter IO, legacy file ops, fixed-buffer import from `rsrc`, provided-buffer `kbuf`, async poll, io-wq retry, block IOPOLL, fsnotify, ioprio/capability checks, and task_work completion.

Risks/test signals: major risks are iterator lifetime during io-wq completion, partial IO accounting, NOWAIT vs nonblocking semantics, fixed-vector validation, metadata/direct-IO constraints, multishot buffer recycling, and IOPOLL ordering. Test with buffered/direct files, sockets/pollable fds, fixed buffers/vectors, provided buffers, short reads/writes, RWF_NOWAIT, O_NONBLOCK, PI attributes, SQPOLL/IOPOLL/hybrid poll, and fault injection around async data allocation.
