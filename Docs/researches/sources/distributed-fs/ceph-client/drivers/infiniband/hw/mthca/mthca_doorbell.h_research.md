# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_doorbell.h

## Purpose
`mthca_doorbell.h` defines doorbell register offsets and architecture-specific helpers for 64-bit MMIO doorbells and two-word host doorbell records.

## Important APIs, types, and functions
Offsets include `MTHCA_RD_DOORBELL`, `MTHCA_SEND_DOORBELL`, `MTHCA_RECEIVE_DOORBELL`, `MTHCA_CQ_DOORBELL`, and `MTHCA_EQ_DOORBELL`. On 64-bit systems, doorbell locking macros compile to no-ops and helpers use raw 64-bit writes. On 32-bit systems, the header declares/initializes a spinlock and serializes two 32-bit writes. `mthca_write_db_rec()` writes host-memory doorbell records with the required ordering.

## Control flow
Queue code builds high/low doorbell dwords and calls `mthca_write64()` against the mapped kernel access region. CQ/EQ/receive paths write host doorbell records before ringing MMIO doorbells where required.

## State and persistence
The header itself stores no state. On 32-bit builds it causes `struct mthca_dev` to include a doorbell spinlock. Device-visible persistent effects are MMIO doorbell writes and host doorbell record updates observed by hardware.

## Dependencies and integration points
It depends on Linux types, endian conversion, MMIO raw write functions, memory barriers, and `BITS_PER_LONG`. It is included by `mthca_dev.h` and used throughout QP, CQ, and EQ paths.

## Risks
Doorbell ordering is critical. On 32-bit systems, missing serialization can interleave high/low dwords from different doorbells. On all systems, missing barriers can let descriptor writes become visible after the doorbell. Raw writes intentionally avoid byteswapping beyond explicit conversion, so caller dword order matters.

## Test signals
Compile and sparse-test 32-bit and 64-bit builds, exercise send/receive/CQ/EQ doorbells under stress, run lockdep for 32-bit lock usage, and validate host doorbell record ordering with hardware or MMIO tracing.
