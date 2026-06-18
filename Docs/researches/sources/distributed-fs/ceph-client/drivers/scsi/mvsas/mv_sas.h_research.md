# sources/distributed-fs/ceph-client/drivers/scsi/mvsas/mv_sas.h

## Purpose

`mv_sas.h` is the shared interface and state definition header for the Marvell mvsas driver. It defines the chip dispatch ABI, controller/PHY/port/device/slot data structures, DMA layout helpers, flash-backed HBA info page format, and function prototypes used by the main libsas implementation and chip-specific 64xx/94xx backends.

## Important APIs, Types, and Definitions

- `DRV_NAME`, `DRV_VERSION`, `MVS_ID_NOT_MAPPED`, `WIDE_PORT_MAX_PHY`, `MVS_MAX_SG`, `MVS_CHIP_SLOT_SZ`, `MVS_RX_FISL_SZ`, and FIS address macros describe global driver constants and per-chip sizing.
- `struct mvs_dispatch` is the central hardware abstraction table. It contains chip init/remap, ISR, interrupt mask, PHY register, port config, command issue, RX update, register-set allocation, PRD generation, PHY discovery, SPI/flash, DMA workaround, interrupt tuning, NCQ error, and GPIO hooks.
- `struct mvs_chip_info` provides per-family dimensions and selects the dispatch table.
- `struct mvs_cmd_hdr` matches the hardware command header written for each slot.
- `struct mvs_port`, `struct mvs_phy`, `struct mvs_device`, `struct mvs_slot_info`, and `struct mvs_info` hold all live driver state.
- `struct hba_info_page`, `struct phy_tuning`, and `struct ffe_control` describe the 256-byte flash/NVRAM HBA information page and PHY tuning data.
- Prototypes export the main functions from `mv_sas.c` to probe/interrupt/chip files: queueing, scan, PHY control, device notifications, resets, RX handling, task release, and GPIO.

## Control Flow and Contracts

The header’s most important control-flow contract is `struct mvs_dispatch`: generic code calls `MVS_CHIP_DISP->...` instead of touching chip-specific registers directly. Backends must provide coherent implementations for ring advancement, interrupt status/ack, PRD sizing, register-set allocation, port type detection, and PHY reset. The main file assumes these hooks are callable under `mvi->lock` and often from interrupt context.

The DMA layout macros define how generic code interprets memory allocated elsewhere: RX FIS areas are indexed by register set or unassociated PHY ID, slot buffers are split into command table/open-address-frame/PRD/status areas, and command headers contain physical addresses for those regions. Any backend change in PRD size/count must remain compatible with the slot buffer sizing constants from `mv_defs.h`.

## State and Persistence Behavior

`struct mvs_info` is the in-memory controller instance. It stores PCI/device handles, MMIO regions, libsas host pointers, TX/RX rings and DMA addresses, RX FIS DMA memory, slot headers, chip identity, reserved-tag bitmap, per-PHY and per-port arrays, device table, flash fields, bulk DMA buffers, and a flexible array of slot info. None of this is persistent except `hba_info_param`, `flashid`, `flashsize`, and `flashsectSize`, which mirror data read from controller flash/NVRAM by other driver code.

`struct hba_info_page` documents persistent firmware/flash contents, including signature, per-port SAS addresses, FFE controls, PHY rates, and tuning parameters. Fields filled with `0xff` are considered invalid. The main `mv_sas.c` code uses the runtime state derived from these values but does not itself write the page.

## Dependencies and Integration Points

The header includes Linux kernel core headers, DMA/PCI/interrupt APIs, libsas, SCSI command/tag helpers, SAS ATA integration, and Marvell hardware definitions from `mv_defs.h`. It exposes external dispatch tables `mvs_64xx_dispatch` and `mvs_94xx_dispatch`, target-mode globals, and the optional `interrupt_coalescing` tunable.

Every source file in the mvsas driver depends on this header for common type identity. The header also defines the low-level driver data pointers that libsas stores in `sas_ha_struct`, `asd_sas_phy`, `asd_sas_port`, `domain_device`, and `sas_task`.

## Risks and Edge Cases

- The dispatch table is large and mostly unchecked at call sites. Missing or incompatible backend hooks can crash generic paths.
- Several structures map hardware DMA or firmware ABI layouts; packing/alignment and endian conversions are critical.
- Macros such as `MVS_PHY_ID` depend on a local variable named `sas_phy`, which makes call-site context significant and easy to misuse.
- `struct mvs_info` uses a flexible array for slots; allocation must account for chip slot count and alignment.
- The HBA info page uses bitfields and mixed-width fields for persistent hardware data; portability and endian assumptions should be treated carefully.

## Test Signals

Header-level validation comes from successful builds across all mvsas chip backends, sparse/endian checks on MMIO and DMA structures, boot/probe on 64xx and 94xx adapters, stress of maximum slot/SG counts, and exercising optional hooks such as GPIO, SPI, interrupt coalescing, STP reset, and DMA workarounds.
