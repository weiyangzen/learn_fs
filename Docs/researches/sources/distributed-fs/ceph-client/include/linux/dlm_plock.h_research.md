<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dlm_plock.h -->
# sources/distributed-fs/ceph-client/include/linux/dlm_plock.h

## Purpose
Declares the DLM POSIX lock bridge used to coordinate file-region locks across a distributed lockspace.

## Important APIs, Types, And Functions
The API consists of `dlm_posix_lock()`, `dlm_posix_unlock()`, `dlm_posix_cancel()`, and `dlm_posix_get()`. Each takes a `dlm_lockspace_t`, a numeric resource identifier, a `struct file`, and a `struct file_lock`, with `dlm_posix_lock()` also taking the POSIX lock command.

## Control Flow
Filesystem lock paths translate VFS file locks into DLM plock operations. Lock, unlock, cancel, and query calls communicate through the DLM plock subsystem and update or inspect the distributed POSIX lock state.

## State And Persistence
State is distributed lock state keyed by lockspace and resource number plus VFS file-lock metadata. No on-disk persistence is defined here.

## Dependencies And Integration Points
Depends on UAPI DLM plock definitions, `struct file`, `struct file_lock`, and clustered filesystem locking paths.

## Risks And Edge Cases
The resource number must map consistently to the filesystem object on all nodes. Cancellation and get operations must race correctly with blocked locks. File lifetime and lockspace lifetime must outlive the operation.

## Test Signals
Tests should cover shared/exclusive byte-range locks across nodes, unlock, cancel of blocking requests, `F_GETLK` semantics, lockspace failure, and concurrent process exit cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dlm_plock.h -->
