# sources/distributed-fs/ceph-client/include/uapi/linux/pg.h

Purpose: Defines the read/write buffer ABI for the generic parallel-port ATAPI packet driver `/dev/pgN`.

Important APIs/types/functions: Exports `PG_MAGIC`, `PG_RESET`, `PG_COMMAND`, `PG_MAX_DATA`, `struct pg_write_hdr`, and `struct pg_read_hdr`.

Control flow: Userspace writes a `pg_write_hdr` followed by optional outbound data. For `PG_COMMAND`, a successful write must be followed by a read that returns `pg_read_hdr`, device data, and status. For `PG_RESET`, no following read is expected. The driver assumes 12-byte ATAPI command packets and caps data transfer at `PG_MAX_DATA`.

State and persistence behavior: The ABI models one pending command per device. Runtime state includes command-in-progress, internal copy buffer, timeout, ATAPI packet, status, and command duration. The header defines no durable state.

Dependencies and integration points: Integrates with the old parallel port ATAPI `pg` driver, ATAPI devices, and userspace tools modeled loosely after generic SCSI but without ioctls.

Risks: The protocol is sequencing-sensitive: read without pending command or write while busy should fail. Fixed 12-byte packets and internal buffer copying require length validation. The magic byte is the only version marker.

Test signals: Send valid command/read pairs, reset operations without reads, invalid magic/function values, over-`PG_MAX_DATA` lengths, timeouts, concurrent command attempts, and offline/malfunctioning device cases.
