# sources/distributed-fs/ceph-client/drivers/nfc/st21nfca/core.c

## Purpose
`core.c` is the HCI-based ST21NFCA NFC driver. It creates the HCI device, loads dynamic pipe sessions, configures polling/card-emulation gates, translates discovered gates into NFC targets, handles data exchange dispatch, and wires DEP, secure-element, and vendor-command helpers.

## Important APIs, types, and functions
- `st21nfca_hci_probe()` allocates `struct st21nfca_hci_info`, builds HCI init data/gates/session id, allocates/registers `nfc_hci_dev`, and initializes DEP/SE/vendor support.
- `st21nfca_hci_remove()` deinitializes DEP/SE and unregisters/frees the HCI device.
- `st21nfca_hci_load_session()` queries device-management pipe lists and maps already-open dynamic pipes into HCI tables.
- `st21nfca_hci_open()`, `st21nfca_hci_close()`, `st21nfca_hci_ready()`, and `st21nfca_hci_xmit()` implement core lifecycle.
- Polling and target helpers include `st21nfca_hci_start_poll()`, `st21nfca_hci_stop_poll()`, `st21nfca_hci_target_from_gate()`, `st21nfca_hci_complete_target_discovered()`, `st21nfca_hci_im_transceive()`, and `st21nfca_hci_check_presence()`.
- `st21nfca_hci_ops` exposes HCI, DEP, SE, and vendor-event callbacks to the NFC HCI core.

## Control flow
Probe initializes a session id `"ST21AH%2x"` from a bitmap device number, registers with protocols Jewel/MIFARE/Felica/ISO14443 A/B/ISO15693/NFC-DEP, sets a short-clear HCI quirk, then initializes submodules. Open enables the physical layer and moves state from COLD to READY. Ready programs secure-element whitelist, enables NFC mode if needed, ends any reader-A operation, and logs software version. Start poll closes unused reader gates, configures Type F datarate and polling request, starts reader-A operation for initiator protocols, and configures card-F parameters for target-mode NFC-DEP. Events are dispatched by gate to admin, DEP card-F, connectivity, APDU reader, or loopback handlers.

## State and persistence
`struct st21nfca_hci_info` stores physical ops/id, HCI device, SE status pointer, state, mutex, async callback state, DEP state, SE state, and vendor loopback state. HCI session id is persistent from the HCI core's perspective but generated from an in-memory device bitmap. No files are written.

## Dependencies and integration points
The file depends on `net/nfc/hci.h`, physical `nfc_phy_ops`, SHDLC LLC name from I2C, ST21NFCA DEP/SE/vendor helpers, and NFC target/secure-element APIs.

## Risks
The device-number bitmap is set during probe but not visibly cleared on remove, so repeated probe/remove can exhaust IDs over time. Several gate/protocol checks use gate constants as bit masks against protocol sets, which is easy to misread and should be validated against HCI core conventions. `st21nfca_get_iso15693_inventory()` pulls two bytes before checking final length and then uses `data[1]` for DSFID, so malformed short inventory responses are risky. Async callback state is shared across operations.

## Test signals
Test HCI session load with preexisting dynamic pipes, open/close state transitions, ready path NFC_MODE programming, all polling protocol combinations, target discovery for Type F/A/ISO15693, DEP link up/down, transceive routing for reader gates, presence checks, admin hot-plug events, and probe/remove ID reuse.
