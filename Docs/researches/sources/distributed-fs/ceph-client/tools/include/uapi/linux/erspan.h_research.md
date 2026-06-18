# sources/distributed-fs/ceph-client/tools/include/uapi/linux/erspan.h

Purpose: defines userspace metadata structures for ERSPAN tunnel metadata mode, covering ERSPAN version 1/type II and version 2/type III metadata passed between tunnel configuration/control paths and kernel networking.

Important APIs/types: `struct erspan_md2` represents version 2 metadata with big-endian timestamp and security group tag plus endian-sensitive bitfields for hardware ID, frame type, platform, overflow, granularity, and direction. `struct erspan_metadata` contains an integer `version` and a union of version 1 `index` or version 2 `md2`.

Control flow, state, and persistence: no executable flow. Userspace selects the union member by `version` and passes metadata to netlink/tunnel code; kernel tunnel code interprets it while encapsulating/decapsulating packets. State is per tunnel or per metadata-mode packet path, depending on the tunnel configuration.

Dependencies and integration points: depends on `<linux/types.h>` and `<asm/byteorder.h>`. Integration is with GRE/ERSPAN tunnel setup, metadata-mode tunnel devices, and tooling that configures mirrored traffic sessions.

Risks and test signals: risks are bitfield endian mistakes, selecting the wrong union member, and treating network-order fields as host-order. Tests should build on big- and little-endian targets, configure ERSPAN v1/v2 tunnels, inspect netlink payloads, and validate captured ERSPAN headers against expected metadata fields.
