# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/glusterfs.h

## Purpose
Central libglusterfs umbrella header for global constants, xattr key contracts, command-line/runtime context structures, graph lifecycle APIs, lock structures, and process-wide configuration.

## APIs, Types, and Functions
The header defines numerous xattr and xdata keys for pathinfo, node UUIDs, GFIDs, bitrot, locks, quota, AFR/DHT/index/heal, cloudsync, FUSE options, logging defaults, network timeouts, lock modes, and internal FOP context. It defines `gf_boolean_t`, cloudsync object states, FOP priorities and `fop_pri_to_string()`, `xlator_cmdline_option_t`, `server_cmdline_t`, `cmd_args_t`, `glusterfs_graph_t`, `glusterfs_ctx_t`, `gf_volfile_t`, `gf_flock`, `lock_migration_info_t`, and attributes `GF_MUST_CHECK`/`GF_UNUSED`. Graph APIs include create/construct/init/prepare/activate/deactivate/reconfigure/attach/destroy/fini and leaf/parent helpers. Other APIs include `glusterfs_ctx_new()`, `gf_flock_copy()`, `gf_free_mig_locks()`, and `glusterfs_read_secure_access_file()`.

## Control Flow, State, and Persistence
`cmd_args_t` captures startup configuration; `glusterfs_ctx_t` is the main process context holding active graphs, pools, event/iobuf/log resources, locks, timers, management pointers, daemon pipes, SSL flags, stats, janitor/disk-check threads, and backtrace buffer. Graph functions manage volfile-derived translator graphs through activation, reconfiguration, and cleanup. Many xattr keys are persistent on-disk or over-the-wire contracts.

## Dependencies and Integration
Includes FOP enums, list, logging, lock owner, UUID, refcount, OpenSSL SHA, and POSIX headers. It is imported by most libglusterfs and xlator code.

## Risks and Test Signals
Risks include key string drift, global context initialization ordering, graph lifecycle races, SSL/security flag confusion, command-line option lifetime issues, and lock migration leaks. Test signals include graph reconfigure/attach tests, xattr compatibility tests, startup option parsing tests, context cleanup leak tests, and rolling-upgrade behavior around persistent keys.
