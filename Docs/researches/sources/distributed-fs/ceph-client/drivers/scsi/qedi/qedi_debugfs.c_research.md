# sources/distributed-fs/ceph-client/drivers/scsi/qedi/qedi_debugfs.c

Purpose: this file provides qedi's debugfs hierarchy and per-host diagnostic files when `CONFIG_DEBUG_FS` is enabled.

Important functions and data: `qedi_dbg_init` creates the driver root directory, `qedi_dbg_exit` removes it, `qedi_dbg_host_init` creates `host%u` directories and files from `qedi_debugfs_ops`, and `qedi_dbg_host_exit` removes host directories. `qedi_do_not_recover` is a global debug switch exposed through the `do_not_recover` file. `qedi_debugfs_ops` defines `gbl_ctx`, `do_not_recover`, and `io_trace`; `qedi_dbg_fops` binds each to seq or command file operations. `qedi_gbl_ctx_show` dumps CQ producer/consumer context per fastpath. `qedi_io_trace_show` dumps the circular I/O trace ring.

Control flow: host init walks the debugfs ops array and creates one file per named operation. Writing `enable` or `disable` to `do_not_recover` toggles the global flag. Reading `gbl_ctx` takes `hba_lock` per queue and prints status block producer and driver consumer indices. Reading `io_trace` takes `io_trace_lock` and emits all 2048 trace records starting at the current ring index.

State and persistence: debugfs state is transient. `qedi_do_not_recover` is runtime global state that can alter TMF/cleanup behavior in `qedi_fw.c` by suppressing cleanup/abort recovery work. Trace data is stored in `qedi_ctx->io_trace_buf`, not in debugfs.

Dependencies and integration points: the file depends on debugfs, seq_file, uaccess, qedi debug macros, `qedi_ctx`, fastpath queues, status blocks, and the I/O trace ring populated by `qedi_trace_io`.

Risks: debugfs is privileged diagnostics but still must avoid races with teardown. `qedi_gbl_ctx_show` assumes fastpath/status block arrays remain valid while the file is read. The write handler compares the user buffer with command strings via `strncmp` directly on a `__user` pointer, which is a kernel-user access risk in general kernel coding style. `qedi_do_not_recover` can intentionally prevent recovery and should not be enabled in normal operation.

Test signals: mount debugfs, probe qedi, verify `/sys/kernel/debug/qedi/hostN` files, read `gbl_ctx` during I/O, enable `io_tracing` and read `io_trace`, write `enable`/`disable` to `do_not_recover`, remove the device while files are open, and run sparse/smatch for user-pointer and lifetime warnings.
