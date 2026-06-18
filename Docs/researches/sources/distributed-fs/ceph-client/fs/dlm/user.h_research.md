# sources/distributed-fs/ceph-client/fs/dlm/user.h

## Purpose
`user.h` declares the DLM userspace-device entry points and AST bridge used by lock code.

## Important APIs, Types, And Functions
It declares callback purge/add helpers, userspace device init/exit, per-lockspace device deregistration, and daemon availability probing.

## Control Flow
Lock code calls `dlm_user_add_ast()` when a user lock has an AST/BAST to deliver. Module init/exit registers/unregisters misc devices. Lockspace teardown calls `dlm_device_deregister()`.

## State And Persistence
No header-owned state. Implementations mutate per-lockspace misc device state and per-open user process structures.

## Dependencies And Integration Points
Used by lock, lockspace, main, and AST code. `dlm_purge_lkb_callbacks()` is declared here and implemented in callback handling code rather than `user.c`.

## Risks
The AST interface assumes valid LKB and user-args lifetime. Device deregistration must be coordinated with lockspace references and open files.

## Test Signals
Compile/link coverage plus userspace lock ABI tests validate the declarations.
