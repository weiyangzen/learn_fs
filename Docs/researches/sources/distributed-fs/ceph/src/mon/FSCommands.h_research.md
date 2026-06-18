# sources/distributed-fs/ceph/src/mon/FSCommands.h

## Purpose
`FSCommands.h` declares the polymorphic command-handler interface used by `MDSMonitor` for CephFS administration commands.

## Important APIs, Types, and Functions
`FileSystemCommandHandler` stores a prefix, derives protectedly from `CommandHandler`, and exposes `can_handle()`, `is_op_allowed()`, static `load(Paxos*)`, and pure virtual `handle()`. Protected helpers are `_check_pool()` and `set_val()`. `fs_or_fscid` lets setting logic target either a new `Filesystem*` or an existing filesystem id.

## Control Flow
`can_handle()` performs exact prefix matching. Global `fs new` and `fs flag set` bypass per-FS authorization; other commands validate session FS write capability before concrete dispatch.

## State and Persistence
The header owns no durable state. Handlers receive mutable `FSMap` and monitor context; persistence is handled by `MDSMonitor` and OSD side effects.

## Dependencies and Integration Points
It depends on `MonOpRequest`, `CommandHandler`, CephFS id types, and forward-declared monitor/FS/OSD/Paxos classes. `errmsg_for_unhealthy_mds` is shared with risky fail-like commands.

## Risks
Prefix-based dispatch is string-sensitive. `fs_or_fscid` is convenient but could update the wrong object if callers confuse committed and uncommitted filesystem instances.

## Test Signals
Verify prefix matching, authorization bypasses, permission rejection, handler load coverage, and concrete behavior of `_check_pool()`/`set_val()` through command tests.
