# sources/distributed-fs/ceph-client/include/linux/rndis.h

## Purpose
`rndis.h` defines Remote NDIS protocol constants for USB/network gadget and host code. It covers message IDs, completion IDs, status values, packet flags, medium and hardware status values, packet filters, miniport/MAC options, many NDIS OIDs, power-management OIDs, and connection-oriented RNDIS messages.

## Important APIs, types, and functions
This header exports macros only. Important macro families are `REMOTE_NDIS_*_MSG`, `REMOTE_NDIS_*_CMPLT`, `RNDIS_STATUS_*`, `RNDIS_DF_*`, `RNDIS_MEDIUM_*`, `RNDIS_PACKET_TYPE_*`, `RNDIS_MINIPORT_*`, `RNDIS_MAC_OPTION_*`, `RNDIS_OID_GEN_*`, `RNDIS_OID_802_3_*`, `RNDIS_OID_802_11_*`, `RNDIS_OID_PNP_*`, and `REMOTE_CONDIS_*`. It does not define runtime structures or functions.

## Control flow, state, and persistence
RNDIS control flow is external to this header: USB control/bulk handlers decode `REMOTE_NDIS_INITIALIZE_MSG`, query/set OIDs, reset/halt, and packet messages using these numeric tags, then respond with matching completion/status values. State such as initialized media status, packet filters, multicast lists, power state, and statistics lives in the RNDIS device or host driver, not here.

## Dependencies and integration points
The header is self-contained and acts as the ABI vocabulary between Linux RNDIS implementations and Microsoft-compatible peers. It integrates with USB gadget Ethernet, USB RNDIS host support, NDIS OID emulation, link state notification, wake-on-LAN/power management, and 802.3/802.11 query paths.

## Risks and test signals
Risks include using a wrong completion code for a request, accepting unsupported OIDs without length validation, 32-bit little-endian protocol assumptions in users, exposing stale link/statistics values, and security-sensitive parsing of host-supplied control buffers. Test signals include enumeration with Windows/Linux RNDIS peers, OID query/set conformance, packet-filter transitions, reset/halt handling, malformed control-message fuzzing, and link/power-management notification tests.
