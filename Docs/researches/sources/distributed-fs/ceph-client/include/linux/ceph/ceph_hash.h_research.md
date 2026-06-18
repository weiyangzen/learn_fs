# sources/distributed-fs/ceph-client/include/linux/ceph/ceph_hash.h

## Purpose

`ceph_hash.h` declares Ceph string hash algorithms used to map names into directory fragments and object placement inputs.

## Important APIs, Types, and Functions

It defines hash ids `CEPH_STR_HASH_LINUX` and `CEPH_STR_HASH_RJENKINS`, declares algorithm implementations `ceph_str_hash_linux()` and `ceph_str_hash_rjenkins()`, and exposes dispatcher/name helpers `ceph_str_hash()` and `ceph_str_hash_name()`.

## Control Flow

Callers select a hash id from metadata layout, then call `ceph_str_hash()` to dispatch to the matching implementation. The result is used by directory-fragment containment and lookup paths.

## State and Persistence Behavior

There is no local state, but hash algorithm ids are persistent metadata semantics. Changing an implementation would remap names and break directory lookup compatibility.

## Dependencies and Integration Points

It integrates with `ceph_frag.h`, `ceph_fs.h` directory layouts, MDS lookup/readdir operations, and any code interpreting `dl_dir_hash`.

## Risks and Edge Cases

Unknown hash ids must be handled by implementation code. The algorithm must be stable across architectures and builds. Name length must be passed explicitly, so embedded NUL bytes and non-NUL-terminated names depend on correct caller length handling.

## Test Signals

Test known vectors for both hash algorithms, unknown type behavior, hash name formatting, directory fragment mapping consistency, and cross-architecture result stability.
