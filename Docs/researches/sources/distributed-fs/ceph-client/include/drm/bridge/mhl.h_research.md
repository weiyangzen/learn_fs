# sources/distributed-fs/ceph-client/include/drm/bridge/mhl.h

Purpose: central Mobile High-Definition Link protocol definition header for device capability/status registers, interrupts, MSC commands, remote-control messages, burst payloads, and MHL3 infoframes.

Important APIs/types/functions: no functions. Main definitions include `MHL_DCAP_*`, `MHL_XDC_*`, `MHL_DST_*`, `MHL_XDS_*`, `MHL_INT_*`, MSC command IDs such as `MHL_WRITE_STAT`, `MHL_SET_INT`, `MHL_MSC_MSG`, message types for RCP/RAP/RBP/UCP/USB/HID/BIST, `enum mhl_burst_id`, packed burst structures, and `struct mhl3_infoframe`.

Control flow: bridge drivers use the constants to read capabilities/status, handle CBUS interrupts, issue MSC transactions, exchange remote-control messages, parse write-burst data, and build MHL3 metadata.

State and persistence: no mutable header state. Protocol state is in hardware and driver state machines; packed structs and endian annotations are wire-format contracts.

Dependencies and integration points: Linux fixed-width/endian types, MHL CBUS controllers, DRM bridges, remote input handling, and HDMI-like infoframe paths.

Risks and test signals: bit drift from spec, packed-layout mistakes, endian misuse, and unsupported message handling are risks. Test capability parsing, path/HPD flows, interrupt decoding, remote-control messages, write-burst payloads, and malformed replies.
