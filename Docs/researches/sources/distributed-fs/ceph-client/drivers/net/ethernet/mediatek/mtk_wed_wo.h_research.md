# sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_wed_wo.h

## Purpose
This header defines the MediaTek WED WO firmware, MCU message, CCIF queue, and per-device transport data structures shared by `mtk_wed_mcu.c` and `mtk_wed_wo.c`.

## Important APIs and Types
- `struct mtk_wed_mcu_hdr` is the MCU wire header with version, command, length, sequence, flags, status, and reserved payload area.
- `struct mtk_wed_fw_region` and `struct mtk_wed_fw_trailer` describe firmware layout metadata parsed from WO firmware binaries.
- `struct mtk_wed_wo_queue_desc`, `struct mtk_wed_wo_queue_entry`, and `struct mtk_wed_wo_queue` describe CCIF DMA rings.
- `struct mtk_wed_wo` ties hardware, TX/RX queues, MCU response synchronization, and MMIO IRQ state together.
- `mtk_wed_mcu_check_msg()` validates MCU packet version and length before dispatch.

## Control Flow
The header declares the init/deinit, MCU send/update, RX event, unsolicited event, and TX SKB functions that form the WO transport lifecycle. It also defines command flags such as response-needed and response message indicators that drive dispatch decisions in the C files.

## State and Persistence
State is primarily per-WO instance: queue descriptors and buffers, MCU wait/response queue/sequence, and regmap IRQ mask/tasklet metadata. Firmware state is represented through reserved-memory region names and firmware binary names.

## Dependencies and Integration Points
It depends on SKB and netdevice kernel types, MediaTek WED hardware forward declarations, firmware files for MT7981/MT7986/MT7988, CCIF register offsets, and MCU boot reset bits.

## Risks and Test Signals
Risks include ABI mismatch with firmware message headers, hard-coded command length/ring size limits, packed descriptor alignment assumptions, and global firmware names drifting from linux-firmware packaging. Test signals are compiler layout checks through normal builds, firmware boot, MCU message validation failures, and runtime RX/TX ring operation.
