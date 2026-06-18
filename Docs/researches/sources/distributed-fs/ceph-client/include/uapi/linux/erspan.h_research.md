## sources/distributed-fs/ceph-client/include/uapi/linux/erspan.h

Purpose: This header defines ERSPAN tunnel metadata structures for userspace configuring metadata-mode ERSPAN tunnels.

Important APIs and types: `struct erspan_md2` models ERSPAN version 2/type III metadata with timestamp, security group tag, and bitfields for hardware ID, frame type, platform-specific flag, overflow, granularity, and direction. Bitfield order is selected based on little or big endian bitfield macros from `<asm/byteorder.h>`. `struct erspan_metadata` carries a version and a union of version 1 index or version 2 metadata.

Control flow and state: Userspace or tunnel code selects ERSPAN metadata version and supplies either a v1 index or v2 metadata. The kernel encapsulation path serializes these fields into ERSPAN headers; decapsulation can report them back depending on tunnel mode.

Persistence and dependencies: Metadata is per packet or per tunnel configuration runtime state. The header depends on `<linux/types.h>` for big-endian integer types and `<asm/byteorder.h>` for bitfield layout.

Integration points: It integrates with GRE/ERSPAN tunnel netdevices, tc, iproute2 tunnel configuration, and packet mirroring/monitoring systems.

Risks and test signals: Risks include bitfield endian mistakes, version/union mismatch, network byte-order confusion, and metadata loss through tooling. Tests should configure v1 and v2 metadata tunnels, inspect captured ERSPAN headers on little- and big-endian builds, validate direction/granularity/hwid fields, and reject unsupported versions.
