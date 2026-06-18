<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/misc.c -->
# sources/distributed-fs/ceph-client/fs/afs/misc.c

## Purpose
Shared error translation and cumulative error prioritisation for AFS operations.

## Important APIs, Types, And Functions
`afs_abort_to_error()` maps AFS/Vice, VLDB, UAE, RxKAD, RxGK, Kerberos, and RxRPC abort codes into Linux negative errno values. `afs_prioritise_error()` updates an `afs_error` accumulator based on response quality and failure precedence, including abort-derived errors and network reachability errors.

## Control Flow
RPC paths record per-call errors and abort codes. Rotation and VL code call `afs_prioritise_error()` as addresses and servers fail; final operation completion reports the selected accumulated errno. `-ECONNABORTED` is special: it is translated through `afs_abort_to_error()` and marks the accumulator as having received a server response.

## State And Persistence
The file mutates only caller-provided `struct afs_error` fields (`error`, `abort_code`, `responded`, `aborted`). It has no durable state.

## Dependencies And Integration Points
Depends on `afs_fs.h`, `protocol_uae.h`, RxKAD/RxGK constants, and Kerberos error constants. Used by fileserver rotation, VL probing, and operation wrappers.

## Risks And Edge Cases
Incorrect mappings leak protocol-specific aborts to userspace or cause wrong retry/failover behavior. Error precedence deliberately preserves stronger failures such as timeout, memory, no network, rfkill, and address reachability over weaker later errors; changing order can alter user-visible errno.

## Test Signals
Inject server aborts (`VNOVOL`, `VMOVED`, `VDISKFULL`, UAE errors), auth failures, unsupported opcodes, and network errors, then verify returned errno and retry/failover decisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/misc.c -->
