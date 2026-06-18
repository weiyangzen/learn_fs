# sources/distributed-fs/ceph-client/drivers/nfc/pn544/mei.c

Purpose: Provides the PN544 transport shim for Intel Management Engine Interface NFC devices.

Important APIs and functions: `pn544_mei_probe()` allocates an `nfc_mei_phy`, then calls `pn544_hci_probe()` with `mei_phy_ops`, LLC NOP, MEI NFC header size, and MEI max payload. `pn544_mei_remove()` removes the HCI device and frees the MEI PHY. `pn544_mei_tbl` matches the PN544 MEI client UUID and version.

Control flow: MEI bus probe creates the generic MEI NFC PHY and registers the PN544 HCI core. Remove reverses that order.

State and persistence: State is stored in the allocated `nfc_mei_phy`, including `hdev`. No durable persistence.

Dependencies and integration points: Depends on the MEI client bus, `../mei_phy.h`, NFC HCI, NFC LLC, and PN544 core exports. Firmware download callback is NULL, so firmware download is unsupported over this transport.

Risks: Probe failure must free the MEI PHY after PN544 registration failure. The transport relies on MEI PHY for enable/disable/write semantics and framing headroom. Test signals include MEI id matching, probe/remove, failure after `nfc_mei_phy_alloc()`, HCI open/close over MEI, and firmware download returning unsupported.
