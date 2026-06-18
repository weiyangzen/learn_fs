<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/main.c -->
# sources/distributed-fs/ceph-client/fs/afs/main.c

## Purpose
Module entry and per-network-namespace lifecycle for the kAFS client. It registers module parameters, allocates global workqueues, initializes per-net AFS state, creates the RxRPC transport, and registers the AFS filesystem.

## Important APIs, Types, And Functions
Exports `afs_wq`, `afs_debug`, `afs_init_sysname`, and `afs_net_id`. `afs_net_init()` initializes `afs_net` fields, cell/server/proc/sysname state, timers, and the RxRPC socket. `afs_net_exit()` tears this down. `afs_init()` allocates `afs`, `kafsd`, and `kafs_lockd` workqueues, registers pernet operations, registers the filesystem, and creates `/proc/fs/afs` symlink. `afs_exit()` reverses this.

## Control Flow
`late_initcall(afs_init)` runs after networking so a socket can be created. On namespace creation, `afs_net_init()` sets up bookkeeping, procfs, root cell data, and transport. On module exit, filesystem registration and pernet state are removed before workqueues and permit cache are cleaned.

## State And Persistence
State is in `struct afs_net` per net namespace plus global workqueues and proc symlink. `rootcell` and `debug` module parameters affect initialization and runtime debugging. No persistent disk state is written.

## Dependencies And Integration Points
Integrates with module loading, pernet operations, procfs, workqueues, key/security setup, cell management, fileserver probing, RxRPC socket setup, and filesystem registration in `super.c`.

## Risks And Edge Cases
Partial initialization must unwind in reverse order without leaving sockets, proc entries, cells, servers, or work items live. Namespace teardown depends on outstanding server and call counters reaching zero. Architecture-specific `afs_init_sysname` drives `@sys` substitution defaults.

## Test Signals
Module load/unload, namespace creation/destruction, rootcell module parameter handling, `/proc/net/afs` creation, workqueue allocation failure injection, and clean `rcu_barrier()`/outstanding-counter behavior are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/main.c -->
