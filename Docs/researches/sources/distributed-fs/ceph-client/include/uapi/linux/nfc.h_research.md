# sources/distributed-fs/ceph-client/include/uapi/linux/nfc.h

## Purpose

`nfc.h` defines the NFC generic netlink ABI, including device discovery, target management, LLCP, secure element, firmware, and vendor command attributes. The file is 320 lines and is part of the NFC generic netlink ABI UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`, `linux/socket.h`. Exported structures include `sockaddr_nfc`, `sockaddr_nfc_llcp`. Enumerations include `nfc_commands`, `nfc_attrs`, `nfc_sdp_attr`. Prominent attribute, command, flag, or constant names include `NFC_CMD_UNSPEC`, `NFC_CMD_GET_DEVICE`, `NFC_CMD_DEV_UP`, `NFC_CMD_DEV_DOWN`, `NFC_CMD_DEP_LINK_UP`, `NFC_CMD_DEP_LINK_DOWN`, `NFC_CMD_START_POLL`, `NFC_CMD_STOP_POLL`, `NFC_CMD_GET_TARGET`, `NFC_EVENT_TARGETS_FOUND`, `NFC_EVENT_DEVICE_ADDED`, `NFC_EVENT_DEVICE_REMOVED`, `NFC_EVENT_TARGET_LOST`, `NFC_EVENT_TM_ACTIVATED`, `NFC_EVENT_TM_DEACTIVATED`, `NFC_CMD_LLC_GET_PARAMS`, `NFC_CMD_LLC_SET_PARAMS`, `NFC_CMD_ENABLE_SE`, `NFC_CMD_DISABLE_SE`, `NFC_CMD_LLC_SDREQ`, `NFC_EVENT_LLC_SDRES`, `NFC_CMD_FW_DOWNLOAD`, and 45 more. Macros expose `__LINUX_NFC_H`, `NFC_GENL_NAME`, `NFC_GENL_VERSION`, `NFC_GENL_MCAST_EVENT_NAME`, `NFC_CMD_MAX`, `NFC_ATTR_MAX`, `NFC_SDP_ATTR_MAX`, `NFC_DEVICE_NAME_MAXSIZE`, `NFC_NFCID1_MAXSIZE`, `NFC_NFCID2_MAXSIZE`, `NFC_NFCID3_MAXSIZE`, `NFC_SENSB_RES_MAXSIZE`, `NFC_SENSF_RES_MAXSIZE`, `NFC_ATR_REQ_MAXSIZE`, `NFC_ATR_RES_MAXSIZE`, `NFC_ATR_REQ_GB_MAXSIZE`, `NFC_ATR_RES_GB_MAXSIZE`, `NFC_GB_MAXSIZE`, and 45 more. There are no executable functions; the API surface is message families, commands, attribute IDs, flags, and fixed structures for netlink serialization.

## Control Flow

NFC management flows through generic netlink commands: enumerate devices, start/stop polling, activate/deactivate targets, configure LLCP sockets and secure elements, and exchange vendor or firmware operations. Nested attributes carry device IDs, protocols, target metadata, and payloads.

## State and Persistence Behavior

The header has no storage of its own. State lives in netlink sockets, routing nexthop objects, NFC devices, or diagnostic snapshots maintained by kernel subsystems and userspace daemons. The declared numeric values and structure layouts are persistent UAPI contracts.

## Dependencies and Integration Points

It integrates with the NFC generic netlink family, NFC controller drivers, LLCP, secure element handling, and userspace NFC management daemons. It directly includes `linux/types.h`, `linux/socket.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; enum and attribute IDs must not be reused or renumbered; maximum-name, option, or attribute limits need bounds checks in producers and parsers; nested netlink attribute policies must reject missing, duplicate, overlong, or wrong-endian attributes. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; netlink policy tests covering every command, mandatory attribute, nested attribute, and malformed-length rejection; dump/notification compatibility tests with old and new userspace tools; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: Copyright (C) 2011 Instituto Nokia de Tecnologia; Lauro Ramos Venancio <lauro.venancio@openbossa.org>; Aloisio Almeida Jr <aloisio.almeida@openbossa.org>.
