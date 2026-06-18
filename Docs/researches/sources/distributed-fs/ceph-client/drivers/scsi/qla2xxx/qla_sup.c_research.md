# sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_sup.c

## Purpose

`qla_sup.c` contains support routines for the QLogic Fibre Channel `qla2xxx` driver, centered on adapter-local nonvolatile storage and board service functions rather than SCSI I/O. It implements low-level NVRAM serial bit-banging for older ISP2xxx adapters, flash and option-ROM access for newer 24xx/25xx/27xx/28xx families, flash layout discovery, firmware/BIOS/EFI/FCODE version extraction, beacon LED control, flash-backed NPIV and FCP priority configuration loading, and VPD field extraction.

The file is part of the Ceph-client source mirror only by repository placement; the code itself is a Linux SCSI FC HBA driver support module. Its persistent state lives on the HBA flash/NVRAM, and its runtime state is mostly cached in `struct qla_hw_data`.

## Important APIs, Types, and Data

- Public NVRAM operations: `qla2x00_read_nvram_data`, `qla2x00_write_nvram_data`, `qla24xx_read_nvram_data`, `qla24xx_write_nvram_data`, `qla25xx_read_nvram_data`, and `qla25xx_write_nvram_data`.
- Public option-ROM operations: `qla2x00_read_optrom_data`, `qla2x00_write_optrom_data`, `qla24xx_read_optrom_data`, `qla24xx_write_optrom_data`, and `qla25xx_read_optrom_data`.
- Public flash metadata operations: `qla2xxx_get_flash_info`, `qla2x00_get_flash_version`, `qla24xx_get_flash_version`, and `qla82xx_get_flash_version`.
- Public service helpers: `qla2xxx_flash_npiv_conf`, `qla2xxx_get_vpd_field`, `qla24xx_read_fcp_prio_cfg`, `qla2x00_beacon_on/off/blink`, `qla24xx_beacon_on/off/blink`, and `qla83xx_beacon_blink`.
- Key firmware-layout types come from `qla_fw.h`: `struct qla_flt_location`, `struct qla_flt_header`, `struct qla_flt_region`, `struct qla_fdt_layout`, `struct qla_npiv_header`, `struct qla_npiv_entry`, and `struct qla_fcp_prio_cfg`.
- Key runtime fields come from `struct qla_hw_data`: `iobase`, `pdev`, `hardware_lock`, `req_q_map`, `isp_ops`, `nvram_base`, flash/NVRAM offset fields, `flt`, `flt_region_*`, `fdt_*`, firmware/boot code revision arrays, `vpd`, `fcp_prio_cfg`, `beacon_blink_led`, `beacon_color_state`, and flash security flags.
- Hardware access is through adapter register layouts such as `struct device_reg_2xxx` and `struct device_reg_24xx`, plus helper macros/functions like `rd_reg_word`, `wrt_reg_word`, `rd_reg_dword`, `wrt_reg_dword`, `RD_REG_WORD_PIO`, and `WRT_REG_WORD_PIO`.

## Control Flow

Initialization flow enters this file from `qla_init.c`. After PCI setup and reset, `qla2xxx_get_flash_info` runs for flash-layout-capable adapters. It optionally marks QLA28xx secure MCU state, finds the Flash Layout Table (FLT) start using `qla2xxx_find_flt_start`, parses FLT regions in `qla2xxx_get_flt_info`, parses Flash Description Table (FDT) erase/write parameters in `qla2xxx_get_fdt_info`, and reads 82xx IDC timeout parameters in `qla2xxx_get_idc_param`. `qla_init.c` then calls `ha->isp_ops->get_flash_version` and later reads FCP priority config on 24xx/25xx families.

Legacy ISP2xxx NVRAM access follows a serial command sequence. `qla2x00_lock_nvram_access` waits for `NVR_BUSY` and takes the host semaphore on supported adapters. `qla2x00_nv_write` toggles select/clock/data bits. `qla2x00_nvram_request` shifts out read commands and shifts in 16 data bits. Writes use `qla2x00_write_nvram_word`, with write-enable and write-disable command sequences, readiness polling, and optional timeout handling through `qla2x00_write_nvram_word_tmo`. Protection handling is split into `qla2x00_clear_nvram_protection` and `qla2x00_set_nvram_protection`.

Newer NVRAM reads are flash-backed. `qla24xx_read_nvram_data` maps logical NVRAM offsets through `nvram_data_addr`; `qla25xx_read_nvram_data` reads from `ha->flt_region_vpd_nvram`. The 25xx write path performs read-modify-write of a 64 KiB VPD/NVRAM region through `read_optrom` and `write_optrom`, while 24xx writes directly enable flash writes, clear NVRAM protection, program dwords, restore protection, and disable flash writes.

Flash reads/writes split by adapter generation. ISP2xxx code directly uses byte-addressed flash registers, handles bank selection, detects manufacturer/device IDs, erases sectors or full flash depending on part geometry, programs bytes, and suspends/resumes the HBA around option-ROM operations. 24xx+ code uses `flash_addr`/`flash_data` dword transactions, FDT-derived sector size and erase command values, and optional DMA burst load/dump mailbox paths. QLA28xx secure flash adds region validation, SFUB extraction/checksum verification, secure mailbox update, semaphore locking, and a reset-to-ROM path when secure firmware support is unavailable.

Beacon flow is timer/DPC driven. Sysfs or other control paths call `ha->isp_ops->beacon_on`, which sets firmware GPIO control options and marks `ha->beacon_blink_led`. The DPC loop checks `BEACON_BLINK_NEEDED` and invokes `ha->isp_ops->beacon_blink`. The blink functions toggle GPIO or adapter-family-specific LED registers and update `beacon_color_state`. `beacon_off` clears the blink flag, forces LEDs off, and restores firmware LED control where applicable.

Version extraction scans option-ROM PCI expansion images. The 2xxx path reads bytewise and parses BIOS/EFI headers, with special text scanning for FCODE revision. The 24xx/82xx paths use `read_optrom`/flash dword reads from FLT boot regions, parse `PCIR` image headers, then read firmware image headers from active primary/secondary firmware regions. QLA81xx additionally reads golden firmware version data.

## State and Persistence Behavior

The persistent objects touched by this file are HBA NVRAM words, flash-backed NVRAM/VPD regions, boot/firmware/option-ROM images, flash layout tables, flash description tables, NPIV configuration blocks, FCP priority configuration blocks, and secure flash update metadata. Writes can permanently alter adapter firmware or configuration and are therefore bracketed by request blocking, flash-protection changes, mailbox-update flags, hardware semaphores, and, for older adapters, RISC pause/reset handling.

Runtime state cached in `qla_hw_data` includes discovered flash region offsets (`flt_region_*`), FDT erase/protection data (`fdt_*`), active version arrays (`bios_revision`, `efi_revision`, `fcode_revision`, `fw_revision`, `gold_fw_version`), flags such as `secure_adapter`, `secure_fw`, `secure_mcu`, `fac_supported`, `fcp_prio_enabled`, and beacon state. `qla24xx_read_fcp_prio_cfg` allocates and owns `ha->fcp_prio_cfg` until invalidated or freed elsewhere.

The file uses multiple concurrency controls. Register-level 2xxx NVRAM writes are protected with `ha->hardware_lock` plus adapter NVRAM semaphores. Option-ROM sysfs/BSG callers serialize staging via `ha->optrom_mutex` outside this file, while this file sets `MBX_UPDATE_FLASH_ACTIVE` and blocks SCSI requests around flash accesses. QLA28xx secure updates use a flash-access semaphore via FAC or remote register locking.

## Dependencies and Integration Points

- `qla_os.c` assigns these functions into per-family `struct isp_operations`, selecting different NVRAM, option-ROM, version, and beacon handlers by adapter generation.
- `qla_init.c` relies on `qla2xxx_get_flash_info`, `get_flash_version`, and `qla24xx_read_fcp_prio_cfg` during adapter bring-up before NVRAM config and firmware setup.
- `qla_attr.c` uses `ha->isp_ops->read_optrom`, `write_optrom`, `get_flash_version`, `beacon_on/off`, and `qla2xxx_get_vpd_field` for sysfs-visible adapter management.
- `qla_bsg.c` exposes option-ROM read/update through BSG and delegates the actual hardware access to these `isp_ops` methods.
- `qla_gs.c` uses `qla2xxx_get_vpd_field` to populate FDMI/RDP management data such as serial number, model name, and engineering-change fields.
- `qla_mbx.c`, `qla_nx.c`, and `qla_nx2.c` provide mailbox/FAC helpers used here, including RAM load/dump, secure flash update, LED config, register access, reset waits, and 82xx/8044-specific option-ROM paths.
- Linux kernel dependencies include PCI config access, DMA coherent allocation, vmalloc/kvmalloc-style buffers, FC vport creation, SCSI request blocking, spinlocks, delays, endian helpers, and scheduler rescheduling during long polling loops.

## Risks and Edge Cases

- Flash and NVRAM writes are high-risk operations. Wrong offsets, bad FLT/FDT interpretation, or interrupted erase/program cycles can corrupt adapter firmware, VPD, or boot code.
- Several paths depend on adapter family macros. A misclassified adapter can select the wrong access width, banking scheme, flash sector geometry, or secure-update path.
- Long polling loops use fixed retry counts with microsecond delays. Hardware that never completes can stall the caller for substantial time, while premature timeout leaves partially completed operations.
- Some functions reuse request-ring memory as temporary FLT/FDT/ROM parsing buffers. Callers must only invoke these paths when that ring buffer is safe for scratch use.
- `qla24xx_write_flash_data` falls back from DMA burst writes to slow writes for some adapters, but QLA27xx/28xx abort on burst failure. This is intentional but makes failure handling generation-specific.
- QLA28xx secure flash depends on parsing firmware-array sizes to locate the SFUB. Malformed update buffers can fail validation, and any size interpretation bug would affect where secure metadata is copied and checksummed.
- `qla25xx_write_nvram_data` read-modify-writes an entire 64 KiB region and indexes with `naddr << 2`; callers must pass dword-oriented offsets consistent with the rest of the driver.
- VPD parsing is deliberately simple and assumes valid PCI VPD resource structure after `qla2xxx_is_vpd_valid`. Malformed VPD returns no field rather than repairing or deeply validating all tags.
- Beacon functions change firmware options and GPIO ownership. Failure to restore options can leave firmware LED control disabled or LEDs in a misleading state.

## Test Signals

Useful positive signals are successful adapter initialization logs after `qla2xxx_get_flash_info`, populated `flt_region_*` and `fdt_*` values in debug output, valid BIOS/EFI/FCODE/FW version sysfs values, successful optrom BSG/sysfs readback, stable NPIV auto-vport creation from flash config, enabled FCP priority config after a valid config checksum, and visible beacon on/off/blink behavior.

Negative signals include `Unable to validate FLASH data`, FLT/FDT checksum warnings, `No matching ROM signature`, `PCI data struct not found`, flash read/write dword timeouts, NVRAM readiness timeouts, failed sector erase/program logs, failed burst-read/write fallback logs, secure SFUB checksum failures, secure mailbox update failures, HBA reset/online wait failures after reset-to-ROM, and missing or invalid VPD/FCP priority fields.

Targeted validation should cover read-only flash info discovery on each supported family, legacy bytewise option-ROM reads on ISP2xxx, 24xx+ dword and burst reads, controlled write paths with known-good images in a hardware lab, QLA27xx/28xx primary/secondary active image selection, QLA28xx secure and non-secure update paths, sysfs and BSG optrom interfaces, beacon sysfs toggling, and malformed FLT/FDT/VPD/FCP-priority fixtures where hardware simulation or fault injection is available.
