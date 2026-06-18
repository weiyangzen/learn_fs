# sources/distributed-fs/ceph-client/net/ceph/ceph_hash.c

## Purpose
Implements Ceph string hash algorithms used by cluster metadata and protocol structures.

## Important APIs, Types, and Functions
Public APIs are `ceph_str_hash_rjenkins()`, `ceph_str_hash_linux()`, `ceph_str_hash()`, and `ceph_str_hash_name()`. The `mix()` macro implements Bob Jenkins' 32-bit mixing routine. Supported algorithm ids are `CEPH_STR_HASH_LINUX` and `CEPH_STR_HASH_RJENKINS`.

## Control Flow
`ceph_str_hash_rjenkins()` consumes input in 12-byte blocks, mixes three 32-bit accumulators, folds remaining bytes with fallthrough cases, mixes again, and returns accumulator `c`. `ceph_str_hash_linux()` applies the historical dcache-style byte loop. `ceph_str_hash()` dispatches by type and returns `-1` cast to unsigned for unknown types. `ceph_str_hash_name()` returns printable names.

## State and Persistence
No mutable state. Hash output stability is part of Ceph's distributed metadata contract.

## Dependencies and Integration Points
Depends on Ceph type constants and exports dispatcher/name functions to other libceph modules.

## Risks
Changing algorithm details would remap Ceph objects or metadata. Unknown hash types returning unsigned `-1` may be a sentinel but should not be used as a valid placement hash. Endianness is fixed by explicit byte assembly in the Jenkins path.

## Test Signals
Known-answer tests for both hash types, unknown-type behavior, empty and short strings, 12-byte boundary lengths, cross-endian consistency, and compatibility with userspace Ceph hash outputs.
