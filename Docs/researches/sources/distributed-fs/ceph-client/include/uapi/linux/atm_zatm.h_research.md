<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atm_zatm.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/atm_zatm.h

## Purpose
Defines ZATM driver-specific free-buffer-pool ioctls and statistics/configuration structures.

## Important APIs, Types, And Functions
Ioctls include `ZATM_GETPOOL`, `ZATM_GETPOOLZ`, and `ZATM_SETPOOL`. `struct zatm_pool_info` contains ref counts, low/high watermarks, queue counters, alignment offsets, and timer repetition controls. `struct zatm_pool_req` selects a pool and carries info. Pool constants cover OAM, AAL0, AAL5 base, and last pool.

## Control Flow
Utilities query, read-and-zero, or update pool parameters via SAR-private ioctls. The driver copies pool info through an `atmif_sioc` pointer.

## State And Persistence
State is live ZATM buffer-pool configuration/counters. `GETPOOLZ` mutates counters by zeroing after read.

## Dependencies And Integration Points
Depends on ATM API alignment and ioctl ranges. Integrates with ZATM SAR driver buffer management.

## Risks And Edge Cases
Pool number bounds, read-and-zero races, and invalid watermarks/offsets can destabilize driver memory handling.

## Test Signals
Get/set pool round trips, zeroing counter behavior, invalid pool rejection, and traffic stress under configured low/high watermarks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atm_zatm.h -->
