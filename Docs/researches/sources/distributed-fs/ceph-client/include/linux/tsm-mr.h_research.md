# sources/distributed-fs/ceph-client/include/linux/tsm-mr.h

## Purpose
Defines Trusted Security Module measurement-register descriptors and sysfs attribute-group creation helpers for confidential-computing guests.

## Important APIs, Types, And Functions
Key types are `struct tsm_measurement_register` and `struct tsm_measurements`. Flags include `TSM_MR_F_NOHASH`, `TSM_MR_F_WRITABLE`, `TSM_MR_F_READABLE`, `TSM_MR_F_LIVE`, and `TSM_MR_F_RTMR`. `TSM_MR_()` initializes readable hashed registers. APIs are `tsm_mr_create_attribute_group()` and `tsm_mr_free_attribute_group()`.

## Control Flow
Drivers provide an array of register descriptors plus optional `refresh()` and `write()` callbacks. Sysfs reads of live registers cause cache refresh; writes call the architecture-specific write/extend callback with exactly the register-sized data.

## State, Persistence, And Dependencies
Register names and value buffers must stay valid while the measurement set is in use. Runtime cache state is in driver-owned `mr_value` buffers. Dependency is hash algorithm metadata from `crypto/hash_info.h`.

## Integration Points
Used by TDX/SEV-SNP or other CC guest drivers that expose RTMR/MR state in sysfs and allow controlled extension of writable registers.

## Risks And Test Signals
Risks include dangling MR buffers, incorrect hash metadata, writable register semantics differing by architecture, and stale cache after live hardware changes. Test signals include sysfs read/write permissions, live refresh invocation, write-size enforcement, hash-name presentation, and attribute-group cleanup tests.
