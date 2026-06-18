# sources/distributed-fs/ceph-client/fs/smb/client/smb2glob.h

## Purpose

This header provides small shared SMB2 definitions used by multiple SMB2 client implementation files. Its main roles are to enumerate compound-operation identifiers consumed by `smb2inode.c`, define flags for chained/related request construction, and define the status-to-POSIX-error mapping record used by `smb2maperror.c`.

## Important APIs, types, and constants

- `enum smb2_compound_ops` assigns stable integer identifiers for open-operation-close compounds: set-delete, set-info, query-info, query-dir, mkdir, rename, hardlink, set-eof, unlink, POSIX query-info, set/get reparse point, WSL EA query, and open-query.
- `CHAINED_REQUEST`, `START_OF_CHAIN`, `END_OF_CHAIN`, and `RELATED_REQUEST` are request-construction flags for chained SMB2 read/request sequencing.
- `struct status_to_posix_error` stores an SMB2/NT status code, a Linux negative errno value, and a printable status string. It is shared by the generated mapping table and KUnit exports.

## Control flow

The header has no runtime control flow. Its values drive switch statements and table lookups in implementation files. Most notably, `smb2_compound_op()` switches on `enum smb2_compound_ops` to decide which SMB2 request initializer to add to a compound chain, and `smb2maperror.c` uses `struct status_to_posix_error` as the element type for binary search.

## State and persistence behavior

No state is stored here. The enum values are part of an internal source-level ABI between SMB2 client files; changing values or adding entries without updating switch handling can break compound operation behavior.

## Dependencies and integration points

The header relies on Linux integer typedefs such as `__u32`. It is included by `smb2inode.c`, `smb2maperror.c`, `smb2maperror_test.c`, and other SMB2 client files that need shared operation IDs or mapping types.

## Risks and edge cases

The main risk is enum drift: adding an `SMB2_OP_*` value requires corresponding request construction, response parsing/freeing, tracepoints, and final status handling in `smb2_compound_op()`. Because `SMB2_OP_SET_DELETE` and `SMB2_OP_QUERY_DIR` appear in the enum but are not handled in the observed `smb2_compound_op()` switch, callers must not pass unsupported values there unless the implementation is extended. Mapping records expose `char *status_string`; generated table storage must outlive all users.

## Test signals

Compile coverage catches missing type definitions. Functional coverage comes from callers of compound operations and from `smb2maperror_test.c`, which validates every generated `struct status_to_posix_error` entry can be found through the exported lookup wrapper.
