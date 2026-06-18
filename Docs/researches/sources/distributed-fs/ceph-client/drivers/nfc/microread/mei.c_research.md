# sources/distributed-fs/ceph-client/drivers/nfc/microread/mei.c

Purpose: Binds the Microread HCI NFC core to Intel MEI NFC devices through the shared MEI PHY helper.

Important APIs, types, and functions: `microread_mei_probe()` allocates `nfc_mei_phy` and calls `microread_probe()` with `mei_phy_ops`, `LLC_NOP_NAME`, MEI header headroom, and MEI payload limit. `microread_mei_remove()` unregisters the HCI device and frees the PHY. `microread_mei_tbl` matches `MEI_NFC_UUID` under the `microread` MEI client name.

Control flow: The MEI client bus calls probe on UUID match. Probe creates the PHY, registers the Microread HCI device with no LLC framing, and leaves runtime enable/disable to HCI open/close. Remove reverses registration and disables/frees the MEI PHY.

State and persistence behavior: No local persistent state; MEI client driver data points at `nfc_mei_phy`, which stores runtime transport state.

Dependencies and integration points: Depends on the MEI client bus, `mei_phy.h`, NFC HCI/LLC, and exported Microread core functions.

Risks: Probe must free the PHY if Microread core registration fails. The headroom/payload values must align with `mei_phy.c` framing. Autoload depends on the UUID/name table.

Test signals: MEI device match/autoload, probe failure cleanup, HCI open/close over MEI, remove after active device, and module unload.
