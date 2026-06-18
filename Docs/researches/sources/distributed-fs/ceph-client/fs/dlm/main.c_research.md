# sources/distributed-fs/ceph-client/fs/dlm/main.c

## Purpose
`main.c` is the DLM module entry and exit point. It orders subsystem initialization, exports the public kernel DLM symbols, and tears subsystems down in reverse order.

## Important APIs, Types, And Functions
The central functions are `init_dlm()` and `exit_dlm()`. The module creates global workqueue `dlm_wq`, registers tracepoints, and exports `dlm_new_lockspace`, `dlm_release_lockspace`, `dlm_lock`, and `dlm_unlock`.

## Control Flow
Initialization creates memory caches, initializes midcomms/lowcomms state, initializes lockspace management and config, registers debugfs, registers userspace misc devices, registers the plock device, then allocates `dlm_wq`. Each failure label unwinds only the subsystems already initialized. Exit destroys `dlm_wq`, exits plock/user/config/lockspace/midcomms/debugfs/memory.

## State And Persistence
Module-global state consists of subsystem registrations, misc devices, config/debugfs state, memory caches, and `dlm_wq`. None persists after module unload.

## Dependencies And Integration Points
This file coordinates `memory.c`, `midcomms.c`, `lockspace`, `config`, debugfs, `user.c`, and `plock.c`. Public symbols are consumed by cluster filesystems such as GFS2.

## Risks
Initialization order matters because memory cache creation asks lowcomms/midcomms for cache constructors before those layers are started. Exit ordering assumes no live lockspaces or users remain. A failure to allocate `dlm_wq` happens late and must unwind all earlier registrations.

## Test Signals
Module load/unload tests should confirm every failure path unregisters devices and frees caches. Symbol export coverage is provided by building cluster filesystem users against the module.
