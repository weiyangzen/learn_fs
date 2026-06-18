# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/include/grph_object_defs.h

Purpose: Provides shared graphics object definitions for connector slots, HPD/DDC source IDs, transmitter IDs, synchronization sources, FFE IDs, connector physical sizes, and board layout structures.

Important APIs and types: `enum hpd_source_id`, `enum channel_id`, `DECODE_CHANNEL_ID`, `enum transmitter`, `enum sync_source`, `enum tx_ffe_id`, connector size constants, `enum connector_layout_type`, `struct connector_layout_info`, `struct slot_layout_info`, and `struct board_layout_info`.

Control flow: This header is a type/constant vocabulary. BIOS and resource code use it to map abstract graphics object IDs to physical channels, HPD lines, DDC lines, board slots, connector dimensions, and synchronization sources.

State and persistence: No mutable state is present. The constants act as ABI-like values for hardware and firmware translation. Board layout structures hold cached physical connector metadata with validity bitfields for slots, sizes, offsets, and lengths.

Dependencies and integration points: Includes `grph_object_id.h`; consumed by GPIO, BIOS parser, display topology, connector reporting, and synchronization logic. `sync_source` is used by GPIO sync source queries and GSL/generic IO routing.

Risks: Enum values map directly to hardware or firmware concepts, so reordering can break translation. `DECODE_CHANNEL_ID` is a macro expression useful for logs but has repeated argument evaluation risk if passed side-effect expressions. Connector physical sizes are fixed approximations and should not be treated as precise board data when BIOS layout exists.

Test signals: Validate source ID translation, connector layout parsing, channel decode strings, and board layout validity flags against representative BIOS data.
