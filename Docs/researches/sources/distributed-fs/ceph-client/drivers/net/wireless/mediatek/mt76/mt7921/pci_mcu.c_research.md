# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/pci_mcu.c

## Purpose
This file provides PCIe-specific MCU ownership and message transport for MT7921. It installs MCU ops, moves the device from firmware ownership to driver ownership, disables PCI L0s, runs firmware, and routes firmware-download commands to the firmware-download queue.

## Important APIs, Types, And Functions
`mt7921e_driver_own()` writes `MT_TOP_LPCR_HOST_DRV_OWN` and polls for firmware ownership to clear. `mt7921_mcu_send_message()` fills a connac2 MCU TX descriptor, sets timeout to three seconds, selects `MT_MCUQ_FWDL` for `MCU_CMD(FW_SCATTER)` and `MT_MCUQ_WM` otherwise, then sends the raw SKB to the selected MCU queue. `mt7921e_mcu_init()` installs `mt76_mcu_ops` and runs ownership plus firmware load.

## Control Flow
During PCI probe or reset, common mt792x MCU init calls `mt7921e_mcu_init()`. The function installs `.mcu_skb_send_msg` and `.mcu_parse_response`, takes driver ownership, disables PCI L0s in `MT_PCIE_MAC_PM`, runs firmware through common `mt7921_run_firmware()`, and cleans the firmware-download queue.

## State And Persistence
State changes include host/firmware ownership, MCU operation table pointer, MCU timeout, PCI power-management register L0s disable bit, firmware running state set by common code, and firmware-download queue contents.

## Dependencies And Integration Points
It depends on PCI register remap helpers, mt76 MCU ops, connac2 message filling, raw TX queue submission, and `mt7921_mcu_parse_response()`/`mt7921_run_firmware()` from common MCU code.

## Risks
Ownership polling failure prevents all later firmware communication. Queue selection must send scatter download commands to the FWDL queue, or firmware download stalls. The hardcoded timeout affects all PCI MCU commands. Disabling L0s is hardware-specific and should stay aligned with PCI power behavior.

## Test Signals
Probe and reset should show successful driver ownership, firmware scatter download on FWDL, normal MCU commands on WM, no timeout during firmware start, and a cleaned FWDL queue after init. Inject ownership timeout to verify `-EIO` and cleanup paths.
