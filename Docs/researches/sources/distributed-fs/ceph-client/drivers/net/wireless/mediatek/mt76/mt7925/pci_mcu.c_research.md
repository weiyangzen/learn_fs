# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/pci_mcu.c

## Purpose
This file provides the MT7925 PCIe MCU transport glue. It installs MCU send/parse operations, routes firmware scatter download commands to the FWDL queue, and performs initial PM ownership plus firmware boot.

## Important APIs, Types, And Functions
`mt7925_mcu_send_message()` fills the MT7925 MCU header and submits the SKB to either `MT_MCUQ_WM` or `MT_MCUQ_FWDL`. `mt7925e_mcu_init()` installs a static `mt76_mcu_ops` table using `mt7925_mcu_parse_response()` and starts firmware.

## Control Flow
MCU send calls `mt7925_mcu_fill_message()`, sets the MCU timeout to three seconds, selects FWDL for `MCU_CMD(FW_SCATTER)`, and queues the raw SKB to the selected mt76 MCU queue. MCU init assigns the ops table, gives firmware then driver PM ownership through PCIe helpers, disables PCIe L0s in `MT_PCIE_MAC_PM`, runs firmware, and cleans the FWDL queue after boot.

## State And Persistence
The file mutates `dev->mt76.mcu_ops`, `mdev->mcu.timeout`, PCIe PM register L0s state, and FWDL queue contents. Firmware boot state is established by `mt7925_run_firmware()` and later consumed by register/device init.

## Dependencies And Integration Points
It depends on the shared MT7925 MCU header/response helpers, mt76 MCU queueing, PCIe PM ownership helpers, and `mt7925_run_firmware()`. PCI probe exposes this through `hif_ops.mcu_init`.

## Risks
Routing the wrong command to the wrong queue can hang firmware download. Header fill errors must not leak the SKB into a queue. Ownership sequencing and L0s disable timing are hardware-sensitive, and FWDL cleanup must run after firmware load to avoid stale descriptors.

## Test Signals
Successful patch/RAM download, MCU command response parsing, timeout behavior, FWDL queue cleanup, and reset-time MCU reinitialization validate this transport layer.
