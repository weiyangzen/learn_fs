# sources/distributed-fs/ceph-client/fs/coda/coda_psdev.h

## Purpose
`coda_psdev.h` defines the kernel-to-Venus pseudo-device communication structures and declares all Venus upcall/downcall helpers used by the Coda VFS client.

## Important APIs, Types, And Functions
It defines `CODA_PSDEV_MAJOR`, `MAX_CODADEVS`, `struct upc_req`, request flags, and `struct venus_comm`. It declares `coda_vcp()`, all `venus_*` operations for rootfid/getattr/setattr/lookup/open/close/create/remove/rename/link/symlink/access/pioctl/fsync/statfs/access_intent, and `coda_downcall()`.

## Control Flow
The header itself only provides `coda_vcp()` to get `struct venus_comm` from `sb->s_fs_info`. Runtime upcall flow is implemented in psdev/upcall sources: VFS operations allocate requests, queue them to Venus, wait for userspace replies, and process downcalls.

## State, Persistence, And Dependencies
`venus_comm` tracks sequence numbers, waitqueue, pending and processing request lists, in-use state, associated superblock, and mutex. Request state is per-upcall in `struct upc_req`. Persistent Coda cache state lives in userspace Venus, not this header.

## Integration Points
All Coda VFS operation files call `venus_*` helpers. The psdev character device exposes queues to the Venus userspace cache manager.

## Risks
Queue lifetime, request abort handling, userspace daemon death, and size limits on upcall messages are key risks. `MAX_CODADEVS` fixes the number of concurrent device channels.

## Test Signals
Test Venus startup/shutdown, concurrent upcalls, interrupted waits, downcall invalidations, daemon death, mount per-device isolation, and every declared Venus operation through VFS workloads.
