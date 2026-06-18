# sources/distributed-fs/ceph-client/net/rds/info.h

## Purpose
`info.h` declares the RDS information snapshot framework used by `info.c` and provider modules. It defines the callback ABI and copy helpers for fixed-record getsockopt information sources.

## Important APIs, Types, and Functions
`struct rds_info_lengths` carries provider output shape: number of records and bytes per record. `struct rds_info_iterator` is opaque to providers except through helper functions. `rds_info_func` is the provider callback type. The header declares registration, deregistration, getsockopt dispatch, iterator copy, and iterator unmap functions.

## Control Flow
The intended control flow is: a subsystem registers an `rds_info_func` for an RDS info option; user space calls the RDS getsockopt; `info.c` pins/maps the destination; the provider fills `lens` and optionally copies fixed records using `rds_info_copy()`; the dispatcher returns the total required length and element size.

## State and Persistence
The header itself owns no state. It documents that providers must make the snapshot shape visible through `lens` and only copy when the caller's provided length can fit the snapshot.

## Dependencies and Integration Points
Included by `rds.h`, so the info API is visible throughout the RDS core and transports. It depends on kernel socket types and user pointer conventions supplied by including translation units.

## Risks
The callback contract is simple but strict. If providers copy more than `len`, report inconsistent `lens`, or sleep with an active iterator mapping, user-visible info calls can fail or trigger kernel bugs.

## Test Signals
Provider tests should verify record counts, `len` gating, and correct use of `rds_info_copy()`/`rds_info_iter_unmap()` across short and multi-page buffers.
