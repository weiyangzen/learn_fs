# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_dsa.c

Purpose: Encodes and decodes Prestera 16-byte DSA tags used to move packets between host CPU and switch firmware/hardware.

Important APIs/types/functions: `prestera_dsa_parse()` parses big-endian four-word DSA buffers into `struct prestera_dsa`; `prestera_dsa_build()` creates a FROM_CPU tag from destination device and port fields. Bit layouts are expressed with `GENMASK`, `BIT`, `FIELD_GET`, and `FIELD_PREP`.

Control flow: RX parsing converts four network-order words, rejects non-TO_CPU commands and missing extension bits, reconstructs VID, hardware device number, source port, VLAN metadata, and CPU code. TX building fills FROM_CPU command, split device fields, destination eport, required extension bits, and writes network-order words.

State and persistence: Stateless transformation of caller-provided buffers and structs. No allocation and no retained state.

Dependencies/integration: Used by Prestera RX/TX paths to strip or prepend proprietary tags. Depends on Linux bitfield helpers and the public structures in `prestera_dsa.h`.

Risks: Bitfield layout is firmware/hardware ABI-sensitive. Parsing casts an unaligned `u8 *` buffer to `__be32 *`, so platform alignment assumptions matter. Build path does not currently encode VLAN fields, so callers must understand tag limitations.

Test signals: Packet RX from multiple ports/devices with CPU codes, TX to specific eports, VLAN-tagged trap parsing, malformed DSA command rejection, extension-bit rejection, and endian validation on non-little-endian builds.
