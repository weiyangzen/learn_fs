# sources/distributed-fs/ceph-client/include/linux/drbd.h

## Purpose
This header defines core DRBD public ABI constants and state encodings shared by the kernel module and user space. It covers policy enums, return codes, role/connection/disk state, state transition return values, metadata flags, UUID indices, notification types, peer state, write ordering, magic numbers, and metadata index constants.

## Important APIs, types, and functions
Important enums include `drbd_io_error_p`, `drbd_fencing_p`, `drbd_disconnect_p`, `drbd_after_sb_p`, `drbd_on_no_data`, `drbd_on_congestion`, `drbd_read_balancing`, `drbd_ret_code`, `drbd_role`, `drbd_conns`, `drbd_disk_state`, `drbd_state_rv`, `drbd_uuid_index`, `drbd_timeout_flag`, `drbd_notification_type`, `drbd_peer_state`, and `write_ordering_e`. `union drbd_state` packs role, peer role, connection state, local and peer disk state, and suspension flags into a 32-bit integer.

## Control flow, state, and persistence
The header has no executable control flow, but it defines persistent protocol and metadata values. `union drbd_state` is transmitted as a big-endian 32-bit value, while its bitfield layout is conditional on host bitfield endianness. Metadata flags such as `MDF_CONSISTENT`, `MDF_PRIMARY_IND`, `MDF_FULL_SYNC`, and `MDF_AL_CLEAN` persist on disk. UUID index constants define on-disk and netlink UUID vector positions.

## Dependencies and integration points
It is usable from both kernel and user space, selecting kernel types or libc/endian headers accordingly. It is included by DRBD generic-netlink definitions and admin tools. Magic values are used in metadata and network packets.

## Risks and test signals
The file warns not to reorder certain enums. ABI risks include inserting return codes in the wrong place, changing bitfield layout, or mismatching protocol version expectations. Tests should cover state serialization on little and big endian, user/kernel enum agreement, metadata magic recognition, and admin-tool decoding of every return code.
