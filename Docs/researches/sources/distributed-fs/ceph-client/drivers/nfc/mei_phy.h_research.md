# sources/distributed-fs/ceph-client/drivers/nfc/mei_phy.h

Purpose: Defines the private/public header for NFC-over-MEI physical-layer helpers used by MEI-backed NFC HCI drivers.

Important APIs, types, and functions: Provides `MEI_NFC_UUID`, `MEI_NFC_HEADER_SIZE`, `MEI_NFC_MAX_HCI_PAYLOAD`, `struct nfc_mei_phy`, exported `mei_phy_ops`, and prototypes for `nfc_mei_phy_alloc()` and `nfc_mei_phy_free()`.

Control flow: No executable flow. Consumers allocate a PHY for a `mei_cl_device`, pass `mei_phy_ops` into an HCI chipset driver, then free the PHY on MEI remove.

State and persistence behavior: The struct defines runtime-only fields for MEI client ownership, HCI device association, wait queue, firmware/vendor/radio metadata, request counters, powered state, and hard-fault status.

Dependencies and integration points: Includes MEI client bus, NFC HCI, and UUID definitions. It links the shared `mei_phy.c` transport with drivers such as `microread/mei.c`.

Risks: Constants are part of the transport contract; changing header size or payload limit without firmware support breaks framing. Exposed struct fields make consumers capable of direct mutation, so additions should preserve existing initialization assumptions.

Test signals: Compile MEI-backed NFC drivers, verify UUID autoload matching, and exercise allocation/free with MEI client data storage.
