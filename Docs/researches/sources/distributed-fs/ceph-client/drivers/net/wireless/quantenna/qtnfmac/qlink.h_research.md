## sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/qlink.h

### Purpose
`qlink.h` is the Quantenna FMAC host/firmware wire-protocol contract. It defines QLINK protocol version 18.1, common message headers, command IDs, command payloads, response payloads, asynchronous event payloads, and TLV encodings used by the driver to translate Linux cfg80211/mac80211 operations into firmware messages.

### Important APIs, Types, And Functions
The file exports packed little-endian structures rather than functions. Core types are `struct qlink_msg_header`, `struct qlink_cmd`, `struct qlink_resp`, `struct qlink_event`, and many command-specific structures such as firmware init/deinit, interface management, scan/connect/AP/channel/regulatory/key/power/WoWLAN/network-device messages. It also defines capability enums, channel/chandef representations, authentication/encryption data, station state/statistics, regulatory rules, HE iftype data, WoWLAN capability containers, and `struct qlink_tlv_hdr` with a fixed `__struct_group()` header and flexible payload.

### Control Flow
Runtime control flow is external: command builders fill these layouts, bus code sends `QLINK_MSG_TYPE_CMD`, firmware answers with matching `QLINK_MSG_TYPE_CMDRSP`, and event code consumes `QLINK_MSG_TYPE_EVENT`. Variable sections are generally TLV arrays or raw IE payloads following fixed headers. Version negotiation starts with `QLINK_CMD_FW_INIT`; later feature use depends on hardware capability bitmaps and response TLVs.

### State, Persistence, And Dependencies
There is no in-memory state in this header. Persistence is the on-wire ABI shared with firmware, including byte order, packing, reserved fields, and alignment. It depends on kernel IEEE 802.11 definitions for HT/VHT/HE capabilities and Ethernet address sizing.

### Integration Points
The command layer, event parser, qlink utility conversion code, regulatory handling, scan/connect/AP setup, station/key management, WoWLAN, OWE/SAE/external-auth paths, and hardware bridge notifications all use these definitions.

### Risks
The ABI is fragile: structure packing, flexible-array offsets, endianness, enum values, and reserved padding must stay synchronized with firmware. Several payloads rely on counts matching trailing TLVs or arrays. Invalid lengths can lead to parser drift if callers do not validate before casting. New protocol fields must be appended, not inserted.

### Test Signals
Useful signals include firmware init version negotiation, parsing band/MAC/HW info TLVs, scan/connect/AP command construction with variable IEs, key and ACL payload lengths, regulatory rule round trips, event length validation, and compatibility tests against older firmware revisions.
