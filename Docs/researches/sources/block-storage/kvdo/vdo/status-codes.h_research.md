# File Research: sources/block-storage/kvdo/vdo/status-codes.h

This header allocates VDO status-code ranges after the UDS error-code block and before a PRP block. It defines `VDO_SUCCESS` plus VDO-specific failures such as out-of-range, no space, bad configuration, component busy, unsupported version, checksum mismatch, read-only, corrupt journal, too many slabs, bad mapping, bad magic/nonce, journal overflow, invalid admin state, and sysfs-node creation failure.

It exports `vdo_status_list[]`, `vdo_register_status_codes()`, and `vdo_map_to_system_error()`. The enum comments document intended semantics and must stay in sync with `vdo_status_list[]`.
