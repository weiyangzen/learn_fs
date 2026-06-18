# sources/distributed-fs/ceph-client/drivers/nfc/st21nfca/vendor_cmds.c

## Purpose
`vendor_cmds.c` exposes ST21NFCA proprietary HCI commands through the NFC vendor command interface, including factory mode, pipe clearing, device-management data operations, firmware load/reset, parameter readback, field generation, and loopback.

## Important APIs, types, and functions
- `st21nfca_vendor_cmds_init()` initializes loopback completion state and registers commands with `nfc_hci_set_vendor_cmds()`.
- Factory mode toggles `ST21NFCA_FACTORY_MODE` in `hdev->quirks`.
- HCI DM handlers proxy PUTDATA, UPDATE_AID, GETINFO, GETDATA, LOAD, RESET, and FIELD_GENERATOR to `ST21NFCA_DEVICE_MGNT_GATE`.
- `st21nfca_hci_get_param()` reads an arbitrary gate/parameter pair supplied by userspace.
- `st21nfca_hci_loopback_event_received()` captures loopback response data; `st21nfca_hci_loopback()` sends a POST_DATA event and waits for completion before replying.

## Control flow
Userspace calls an ST OUI vendor subcommand. Simple commands return HCI status. Data-returning commands allocate a vendor reply skb and attach the returned payload as `NFC_ATTR_VENDOR_DATA`. Reset sends an async device-management reset, then restarts the NFC LLC. Loopback reinitializes completion, sends a loopback event, waits for an HCI event to fill `vendor_info.rx_skb`, validates length, and replies with the echoed bytes.

## State and persistence
State is runtime-only: factory-mode quirk, loopback completion, and captured loopback skb. No persistent storage is used.

## Dependencies and integration points
The file depends on generic netlink/NFC vendor command APIs, NFC HCI command/event APIs, and NFC LLC stop/start. It is initialized from `core.c` after HCI registration.

## Risks
Userspace payload validation is minimal for most HCI DM commands. Loopback waits interruptibly without a timeout, so a lost event can block the caller until interrupted. Reset restarts LLC after sending an async reset, which depends on firmware timing. Reply allocation failures must free returned HCI skbs correctly, which the code generally does.

## Test signals
Test all vendor subcommands, invalid lengths, factory-mode effect on SE discovery, GETINFO/GETDATA reply payloads, reset with LLC restart failure, loopback success/mismatch/no-event interruption, and repeated loopback cleanup of `rx_skb`.
