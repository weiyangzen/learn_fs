# sources/distributed-fs/ceph-client/include/linux/pr.h

Purpose: declares block-device persistent reservation data structures and operation callbacks.

Important APIs and types: `struct pr_keys` carries generation, key count, and flexible key array. `struct pr_held_reservation` carries key, generation, and reservation type. `struct pr_ops` defines callbacks for register, reserve, release, preempt, clear, read keys, and read reservation.

Control flow: block-layer or filesystem management code invokes `pr_ops` on a `block_device` to manage SCSI/NVMe-style persistent reservations, and reads key/reservation state for reporting or retry sizing.

State and persistence: reservation keys and held reservation are persistent device-side state; the structs here are transient kernel buffers and callback tables.

Dependencies and integration points: integrates with block devices and UAPI persistent reservation types/flags. Implementations are supplied by lower block transports/drivers.

Risks and test signals: risks include key array sizing/retry bugs, generation mismatch handling, reservation type mismatches, preempt abort semantics, and incomplete driver callback coverage. Test PR register/reserve/release/preempt/clear, read-keys retry with too-small buffer, read-reservation generation/type, multipath/failover behavior, and unsupported-device errors.
