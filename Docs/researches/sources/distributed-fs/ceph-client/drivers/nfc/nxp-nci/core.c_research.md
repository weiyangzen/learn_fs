# sources/distributed-fs/ceph-client/drivers/nfc/nxp-nci/core.c

Purpose: Implements the generic NXP NCI core driver that registers an NCI device over a transport-provided PHY interface.

Important APIs and functions: Exports `nxp_nci_probe()` and `nxp_nci_remove()`. NCI ops are `nxp_nci_open()`, `nxp_nci_close()`, `nxp_nci_send()`, and firmware download through `nxp_nci_fw_download()`. Proprietary NCI notification handlers log RF PLL unlock and TXLDO errors via `nxp_nci_core_ops`.

Control flow: Probe allocates `nxp_nci_info`, stores PHY id/ops/max payload, initializes firmware work/completion and mutex, forces cold mode through `set_mode()`, allocates/registers an NCI device, and returns it to the PHY driver. Open transitions cold to NCI mode under `info_lock`; close returns to cold. Send validates mode and `write` callback, delegates SKB ownership to the PHY write path, and consumes or frees SKBs appropriately. Remove completes any active firmware worker, cancels work, returns hardware to cold, unregisters, and frees the NCI device.

State and persistence: `nxp_nci_info` stores current mode, max payload, PHY ops, mutex, NCI device pointer, and firmware worker state. No durable persistence exists.

Dependencies and integration points: Integrates with NCI core allocation/registration, Linux NFC firmware download API, transport `nxp_nci_phy_ops`, and firmware code in `firmware.c`.

Risks: `nxp_nci_open()` sets mode to NCI even if `set_mode()` fails after being called, preserving the returned error but leaving state optimistic. Send mode checks prevent firmware and cold writes through normal NCI path. Test signals include mode transitions, send without write op, send while cold/FW, proprietary RF notifications, firmware download dispatch, remove during FW mode, and probe unwind after NCI register failure.
