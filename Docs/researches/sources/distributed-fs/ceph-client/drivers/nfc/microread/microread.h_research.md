# sources/distributed-fs/ceph-client/drivers/nfc/microread/microread.h

Purpose: Declares the shared interface for Microread physical transports to register and unregister the common HCI chipset driver.

Important APIs, types, and functions: Defines `DRIVER_DESC`, declares `microread_probe()` with PHY id, `nfc_phy_ops`, LLC name, headroom/tailroom/payload constraints, and output HCI device pointer, plus `microread_remove()`.

Control flow: Transport drivers call `microread_probe()` during their bus probe and `microread_remove()` during remove.

State and persistence behavior: The header itself has no state. Its parameters determine runtime HCI allocation characteristics such as PHY framing room and max payload.

Dependencies and integration points: Includes NFC HCI core declarations and is consumed by `i2c.c`, `mei.c`, and implemented by `microread.c`.

Risks: The API assumes one HCI device per transport PHY and exposes no update path for runtime payload/headroom changes. Incorrect headroom/tailroom arguments can corrupt transport framing.

Test signals: Compile both transports against the header and verify probe/remove signatures stay synchronized with the core implementation.
