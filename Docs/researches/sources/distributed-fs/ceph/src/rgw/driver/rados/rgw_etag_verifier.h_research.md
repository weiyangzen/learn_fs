# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_etag_verifier.h

## Purpose
`rgw_etag_verifier.h` declares the ETag verifier data processors used during RGW put-object flows, especially multisite sync verification.

## Important APIs, Types, And Functions
`ETagVerifier` derives from `rgw::putobj::Pipe`, owns `CephContext`, an MD5 hash, and the calculated ETag string, and requires `calculate_etag()`. `ETagVerifier_Atomic` implements single-hash ETags. `ETagVerifier_MPU` stores part offsets, current and next part indexes, and a second MD5 for the aggregate MPU ETag.

`etag_verifier_ptr` is a `ceph::static_ptr` sized to the larger verifier type, avoiding heap polymorphic allocation. `create_etag_verifier()` constructs the correct concrete verifier into that static storage.

## Control Flow
Consumers call `create_etag_verifier()` with a manifest, optional compression info, and the next data processor. They stream data through the resulting `Pipe`, then call `calculate_etag()` and compare `get_calculated_etag()` to expected metadata.

## State And Persistence Behavior
The classes are transient stream processors. Their state is the in-progress hash context, part indexes, part offset vector, and final string. No persistent state is written.

## Dependencies And Integration Points
The header depends on RGW put-object pipe abstractions, RGW operation types, Ceph `static_ptr`, MD5, manifests, and compression metadata through the factory signature.

## Risks And Edge Cases
Because `etag_verifier_ptr` uses static storage, `max_etag_verifier_size` must be updated if a verifier class grows in a way the `std::max` expression does not cover. `ETagVerifier_MPU` initializes `next_part_index` to 1 and expects `part_ofs` to contain at least one offset with MPU semantics.

## Test Signals
Tests should instantiate both verifier types through the factory, verify static pointer lifetime and destruction behavior, and assert correct ETag strings for known atomic and MPU payloads.
