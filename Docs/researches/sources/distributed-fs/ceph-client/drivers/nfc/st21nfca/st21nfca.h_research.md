# sources/distributed-fs/ceph-client/drivers/nfc/st21nfca/st21nfca.h

## Purpose
`st21nfca.h` declares shared constants, state structures, and cross-file APIs for the HCI-based ST21NFCA driver.

## Important APIs, types, and constants
- Defines HCI LLC frame sizes, max payload, custom gates, eSE host id, ST OUI, factory-mode quirk bit, and device count.
- `struct st21nfca_se_status` carries platform-provided SE presence.
- `enum st21nfca_state` distinguishes COLD and READY.
- `enum nfc_vendor_cmds` defines userspace-visible vendor subcommands.
- `struct st21nfca_vendor_info`, `st21nfca_dep_info`, `st21nfca_se_info`, and `st21nfca_hci_info` store loopback, DEP, SE, and whole-device state.
- Prototypes expose HCI probe/remove, DEP helpers, SE event handlers/ops, loopback event handling, and vendor command init.

## Control flow and integration
All ST21NFCA implementation files include this header. The I2C physical layer calls the HCI probe/remove prototypes; `core.c` calls DEP/SE/vendor helpers; `dep.c`, `se.c`, and `vendor_cmds.c` access the shared `st21nfca_hci_info` state via HCI clientdata.

## State and persistence
The header models runtime state only. HCI session identity and device index are generated during probe, while platform SE presence comes from firmware properties.

## Dependencies and risks
The header depends on NFC HCI, sk_buffs, and workqueues. The vendor command enum is ABI-sensitive; changing order changes userspace subcommand numbers. `struct st21nfca_dep_info` is marked packed despite containing pointers/work_struct-like adjacent state in the parent structure, so layout changes should be made carefully.

## Test signals
Compile all users of the header and run ABI tests for vendor subcommands, frame-size bounds, and state initialization paths in DEP/SE/vendor modules.
