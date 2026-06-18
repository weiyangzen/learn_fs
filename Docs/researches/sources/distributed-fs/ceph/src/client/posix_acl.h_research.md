# sources/distributed-fs/ceph/src/client/posix_acl.h

## Purpose
`posix_acl.h` declares Ceph's POSIX ACL EA wire format and helper functions.

## Important APIs, Types, and Functions
It defines ACL version, tag constants, xattr names (`system.posix_acl_access`, `system.posix_acl_default`), `acl_ea_entry`, `acl_ea_header`, and declarations for validation, mode equivalence, inheritance, chmod update, and permission evaluation.

## Control Flow
The header provides no executable flow; callers pass raw xattr buffers or mutable `bufferptr` instances to the implementation helpers.

## State and Persistence Behavior
The structs describe persisted xattr data in little-endian Ceph types. Helper declarations indicate which functions may mutate ACL buffers.

## Dependencies and Integration Points
It forward-declares `UserPerm` and expects Ceph type and `bufferptr` definitions from includers. Client permission code can use the constants and helpers to match Linux POSIX ACL behavior.

## Risks
The flexible-array member `a_entries[0]` is a C-style ABI pattern requiring careful allocation and size validation. Consumers must not assume native endianness.

## Test Signals
Compile tests should include the header with necessary Ceph type definitions. Runtime tests are the same ACL matrix as the implementation.
