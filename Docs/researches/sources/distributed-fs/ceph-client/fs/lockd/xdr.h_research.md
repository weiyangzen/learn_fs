# sources/distributed-fs/ceph-client/fs/lockd/xdr.h

## Purpose

`sources/distributed-fs/ceph-client/fs/lockd/xdr.h` defines the common lockd XDR-facing data structures, constants, NLM status macros, and prototypes for hand-written NLM v1/v3 server encode/decode helpers. The source was read as a complete 106-line file for this report.

## Important APIs, Types, and Functions

Important constants are `SM_MAXSTRLEN`, `SM_PRIV_SIZE`, `NLM_MAXCOOKIELEN`, and `NLM_MAXSTRLEN`. Status macros include `nlm_granted`, `nlm_lck_denied`, `nlm_lck_denied_nolocks`, `nlm_lck_blocked`, and `nlm_lck_denied_grace_period`. Types are `struct nsm_private`, `struct nlm_lock`, `struct nlm_cookie`, `struct nlm_args`, `struct nlm_res`, and `struct nlm_reboot`. Function prototypes declare the `nlmsvc_decode_*` and `nlmsvc_encode_*` routines implemented in `xdr.c`.

## Control Flow

This header has no runtime flow. It defines the storage layout that RPC decode routines fill, procedure handlers consume, and encode routines serialize.

## State and Persistence Behavior

No storage is allocated here. Instances are per-RPC request or response objects owned by SUNRPC service buffers, with embedded VFS `struct file_lock` state used only during request processing.

## Dependencies and Integration Points

It includes Linux fs/filelock/NFS/SUNRPC XDR headers and is consumed by lockd procedure, XDR, and trace code through `lockd.h`. The definitions bridge network protocol fields and VFS locking structures.

## Risks and Edge Cases

The cookie buffer is a deliberate implementation limit smaller than the protocol maximum. `struct nlm_lock` contains both legacy range fields and a VFS `file_lock`, so callers must keep the fields they use synchronized. Status macros are big-endian values and must not be compared as host-order integers without conversion.

## Test Signals

Compile coverage for all lockd XDR users, static checks for structure layout assumptions in procedure storage, NLM v1/v3 RPC decode/encode smoke tests, and tests that compare wire status values to expected big-endian NLM codes.
