# sources/distributed-fs/ceph-client/fs/ceph/locks.c

## Purpose
`locks.c` implements CephFS distributed POSIX byte-range locks and BSD flock locks. It translates Linux `struct file_lock` operations into MDS filelock requests, mirrors successful locks into the local VFS lock manager, handles interruptible blocking lock acquisition, and encodes local lock state for reconnect/session recovery.

## Important APIs, types, and functions
The externally used functions are `ceph_flock_init`, `ceph_lock`, `ceph_flock`, `ceph_count_locks`, `ceph_encode_locks_to_buffer`, and `ceph_locks_to_pagelist`. Internal helpers include `secure_addr`, `ceph_fl_copy_lock`, `ceph_fl_release_lock`, `ceph_lock_message`, `ceph_lock_wait_for_completion`, `try_unlock_file`, and `lock_to_ceph_filelock`.

Important state includes the boot-time random `lock_secret`, `struct file_lock_operations ceph_fl_lock_ops`, `ceph_inode_info::i_filelock_ref`, `CEPH_I_ERROR_FILELOCK`, local VFS lock contexts, MDS request filelock arguments, and encoded `struct ceph_filelock` arrays/pagelists.

## Control flow
`ceph_flock_init` seeds `lock_secret`. `secure_addr` XORs that secret with the Linux lock owner pointer and sets the high bit so the MDS can treat owner as sufficient identity. For set-lock operations, `ceph_lock_message` installs Ceph lock operations and takes an inode reference before request submission, builds a `CEPH_MDS_OP_SETFILELOCK` or `CEPH_MDS_OP_GETFILELOCK` request, converts Linux start/end to Ceph start/length, encodes owner/pid/type/wait, submits to the auth MDS, waits for completion, and decodes GETLK replies back into the caller's `file_lock`.

Blocking locks use `ceph_lock_wait_for_completion`. If the wait is interrupted before the original request completed, it marks the original request aborted under MDS client locking and, if the request had been sent, issues an interrupt-style unlock request (`CEPH_LOCK_FCNTL_INTR` or `CEPH_LOCK_FLOCK_INTR`). It then waits for the original safe completion so the MDS and client do not diverge.

`ceph_lock` handles POSIX locks. It rejects non-POSIX locks and shutdown inodes, converts GETLK/SETLKW semantics, checks sticky `CEPH_I_ERROR_FILELOCK`, short-circuits unlocks that do not exist locally, sends the MDS request, and only after MDS success installs the lock locally with `posix_lock_file`. If local deadlock detection fails after MDS success, it sends a compensating MDS unlock. `ceph_flock` follows the same pattern for flock locks using `locks_lock_file_wait`.

Reconnect encoding starts with `ceph_count_locks`, which counts POSIX and flock lists under the inode lock context spinlock. `ceph_encode_locks_to_buffer` converts each local lock into a contiguous `struct ceph_filelock` array and returns `-ENOSPC` if counts changed beyond the caller's allocation. `ceph_locks_to_pagelist` serializes counts and lock arrays into a Ceph pagelist in fcntl-then-flock order.

## State and persistence behavior
The authoritative distributed lock state lives in the MDS. The client mirrors successful locks in the local VFS lock lists so Linux semantics and conflict detection work locally. `i_filelock_ref` pins inode/cap state while locks exist and clears `CEPH_I_ERROR_FILELOCK` when all Ceph-backed locks are released. Lock owner values are process-local obfuscated identities derived from pointers and a random boot secret; they are stable enough for a client lifetime but not persistent across reboot.

## Dependencies and integration points
The file depends on Linux file-locking infrastructure, MDS client request APIs, Ceph pagelists, inode cap/error state, inode lifetime management, random bytes, and Ceph wire constants for filelock rules and commands. `super.h` exposes `ceph_lock` and `ceph_flock` to file operation tables, and reconnect/session recovery code can use the count/encode/pagelist helpers to replay lock state.

## Risks
The main risks are client/MDS divergence if a local lock install fails after MDS success, races during interrupted blocking locks, stale inode references from `fl_file` lifetime, lock count changes between count and encode, owner identity reuse after process/client lifetime changes, and sticky error handling that must not strand local locks. The code also relies on correct caller serialization where MDS reply handling can otherwise race with locks held by VFS callers.

## Test signals
Tests should include POSIX GETLK/SETLK/SETLKW and flock shared/exclusive/unlock across multiple clients, interrupted blocking locks, local deadlock failure forcing compensating unlock, nonexistent unlock behavior, MDS session reconnect with lock replay, error injection setting `CEPH_I_ERROR_FILELOCK`, inode release while locks remain, and lock count changes during encode returning `-ENOSPC`.
