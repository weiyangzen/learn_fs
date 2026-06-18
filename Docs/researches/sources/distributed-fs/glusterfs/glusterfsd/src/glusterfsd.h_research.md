# sources/distributed-fs/glusterfs/glusterfsd/src/glusterfsd.h

Purpose: Private daemon header for default paths, CLI option keys, daemon constants, and cross-file function prototypes.

Important APIs and types: Defines default volfile paths, event-pool size, accepted log-level strings, daemon/debug flags, mempool sizing constants, and `GLUSTER_BRICK_GRACEFUL_CLEANUP`. `enum argp_option_keys` assigns stable short and numeric keys used by `argp` in `glusterfsd.c`. Prototypes expose `glusterfs_mgmt_init()`, `glusterfs_listener_init()`, `glusterfs_volfile_fetch()`, `glusterfs_process_volfp()`, `emancipate()`, and `cleanup_and_exit()`. Declares external `glusterfsd_ctx`.

Control flow: No executable flow. Its enum drives `parse_opts()` switch dispatch and therefore the entire CLI control path.

State and persistence: No direct state. Constants affect runtime defaults for config files, event-pool sizing, memory pools, and brick cleanup behavior. The `glusterfsd_ctx` declaration exposes the process-global context.

Dependencies and integration: Shared by `glusterfsd.c` and `glusterfsd-mgmt.c`. Assumes compile-time `CONFDIR` and related macros are provided by Automake flags.

Risks: Numeric argp keys must not collide. Changing default paths affects startup behavior and packaging. Changing mempool counts impacts memory footprint and allocation behavior. The global context declaration cements singleton daemon assumptions.

Test signals: Compile catches missing prototypes and duplicate enum symbols; CLI integration tests catch key/default regressions.
