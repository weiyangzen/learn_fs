<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/sysctl.c -->
# sources/distributed-fs/ceph-client/net/sunrpc/sysctl.c

Purpose: Provides the optional `/proc/sys/sunrpc` sysctl interface for SUNRPC debug controls and a readable transport list when `CONFIG_SUNRPC_DEBUG` is enabled.

Important APIs/types/functions: Exports global debug flags `rpc_debug`, `nfs_debug`, `nfsd_debug`, and `nlm_debug`. `proc_dodebug()` implements read/write parsing for the debug flag sysctls. `proc_do_xprt()` formats registered service transports using `svc_print_xprts()`. `rpc_register_sysctl()` registers the `sunrpc` sysctl table and `rpc_unregister_sysctl()` removes it. `debug_table[]` defines `rpc_debug`, `nfs_debug`, `nfsd_debug`, `nlm_debug`, and read-only `transports`.

Control flow: On registration, the file installs the table once under `sunrpc`. Reads of debug flags format the stored integer as hex plus newline. Writes trim leading whitespace, copy a bounded input into a stack buffer, parse with base autodetection, validate trailing characters, store into the target global, and call `rpc_show_tasks(&init_net)` when `rpc_debug` is written. Reads of `transports` generate a bounded temporary report and copy it to userspace with `memory_read_from_buffer()`.

State and persistence behavior: State is only the four exported unsigned integer debug masks and the `sunrpc_table_header` registration pointer. Values persist only while the module/kernel is running. The interface is absent when `CONFIG_SUNRPC_DEBUG` is disabled, though the global debug symbols remain declared outside the conditional.

Dependencies and integration points: Integrates Linux sysctl helpers, uaccess-safe buffer copying, SUNRPC scheduler task display, stats/debug consumers, and service transport reporting. NFS, NFSD, NLM, and SUNRPC code can test the exported masks for conditional logging.

Risks: `proc_dodebug()` intentionally accepts numeric writes up to 19 bytes plus NUL; longer writes fail with `-EINVAL`. Debug state is global rather than per-network-namespace, while `rpc_show_tasks()` is hardwired to `init_net`. Heavy task dumping on every `rpc_debug` write can be noisy in production. The sysctl handlers are compiled out without `CONFIG_SUNRPC_DEBUG`, so tests must account for configuration-dependent presence.

Test signals: Validate debug sysctl read/write formatting, invalid trailing characters, oversized writes, empty/offset reads, `rpc_debug` task dump side effect, `transports` read truncation behavior, and idempotent register/unregister cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/sysctl.c -->
