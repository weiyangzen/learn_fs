# sources/distributed-fs/ceph-client/drivers/nfc/nxp-nci/nxp-nci.h

Purpose: Shared private header for the NXP NCI core, firmware downloader, and transport drivers.

Important APIs and types: Defines firmware framing constants `NXP_NCI_FW_HDR_LEN`, `NXP_NCI_FW_CRC_LEN`, and `NXP_NCI_FW_FRAME_LEN_MASK`; `enum nxp_nci_mode`; `struct nxp_nci_phy_ops`; `struct nxp_nci_fw_info`; and `struct nxp_nci_info`. Declares firmware and probe/remove functions used across `core.c`, `firmware.c`, and `i2c.c`.

Control flow: No executable flow. The mode enum controls transport behavior: cold, normal NCI, and firmware download. The PHY ops provide the only hardware-specific hooks used by core and firmware code.

State and persistence: `nxp_nci_info` is the per-device runtime anchor, and `nxp_nci_fw_info` holds active firmware-download progress. No durable state is defined here.

Dependencies and integration points: Includes completion, firmware, NFC, and NCI core headers. It is local to the NXP NCI driver folder.

Risks: Max payload, frame mask, and CRC length assumptions must match transport/device firmware mode. Mode transitions depend on all users holding `info_lock` consistently. Test signals include compile coverage across core/firmware/I2C, firmware state progression, and mode-dependent IRQ read dispatch.
