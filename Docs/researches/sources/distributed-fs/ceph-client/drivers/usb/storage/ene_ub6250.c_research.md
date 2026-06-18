# sources/distributed-fs/ceph-client/drivers/usb/storage/ene_ub6250.c

## Purpose

`ene_ub6250.c` is a usb-storage subdriver for ENE UB6250 card readers. It supports SD/MMC and MemoryStick media by loading device-side firmware snippets, emulating selected SCSI disk commands, and maintaining MemoryStick logical-to-physical block maps.

## Important APIs, Types, and Functions

`struct ene_ub6250_info` is the main per-device state, containing a bounce buffer, SD/MS/SM status bytes, SD geometry fields, MemoryStick map/control fields, firmware pattern state, last block count, sense status, and resume flags. `ene_load_bincode()` loads one of six firmware files and sends it to the device using a bulk-only command wrapper. `ene_send_scsi_cmd()` sends CBWs, optional data phases, and CSWs. Generic SCSI emulation helpers include `do_scsi_request_sense()` and `do_scsi_inquiry()`. SD paths include `ene_sd_init()`, `ene_get_card_status()`, `sd_scsi_read_capacity()`, `sd_scsi_read()`, and `sd_scsi_write()`. MemoryStick paths include `ene_ms_init()`, `ms_card_init()`, logical map allocation/scanning helpers, `ms_scsi_read_capacity()`, `ms_scsi_read()`, and `ms_scsi_write()`. `ene_transport()` routes commands to SD and/or MS handlers, while `ene_ub6250_probe()`, `ene_ub6250_resume()`, and `ene_ub6250_reset_resume()` handle usb-storage integration and PM.

## Control Flow

Probe allocates usb-storage state, creates `ene_ub6250_info` plus a 512-byte bounce buffer, installs the `ene_ub6250` transport, runs `usb_stor_probe2()`, then probes card status. Transport clears SCSI residue, initializes media if status is not ready, and dispatches the command to SD or MS handlers based on readiness bits. SD initialization loads two firmware patterns, executes device commands, parses status/CSD-like data, and computes capacity. SD read/write loads the SD R/W firmware, builds vendor CBWs with block addresses, and transfers the SCSI scatterlist. MS initialization loads MS firmware, distinguishes MS Pro from classic MS, reads boot/system information for classic MS, builds Phy2Log/Log2Phy maps, scans logical block numbers, and allocates write buffers. MS Pro read/write is direct block I/O; classic MS read/write translates logical blocks to physical blocks, allocates replacement blocks, copies pages, and updates maps. Resume/reset-resume zero media status so the next command reinitializes.

## State and Persistence Behavior

Runtime state includes cached firmware pattern (`BIN_FLAG`), media status, SD capacity fields, total block count, MemoryStick maps, write buffers, and the last sense status. Firmware blobs are loaded from the host filesystem on demand but not persisted by the driver. Persistent media changes happen on SD/MS card data blocks and, for classic MS, physical-block mappings and overwrite/management metadata. The driver drops status on resume to force reinitialization but frees only the main bounce buffer in its extra destructor; MemoryStick map/write allocations are managed by MS init/free helpers during reinitialization.

## Dependencies and Integration Points

The file depends on usb-storage bulk-only wrappers, SCSI command definitions, firmware loader APIs, unusual-device tables, and ENE-specific firmware files under `ene-ub6250/`. It integrates with the SCSI disk layer by faking inquiry, request sense, mode sense, capacity, TEST UNIT READY, and READ_10/WRITE_10, while importing USB_STORAGE namespace symbols.

## Risks and Test Signals

Risks include mandatory external firmware availability, many little-endian/unaligned parses from firmware buffers, sparse error propagation where helper status domains are mixed with USB transport constants, potential memory leaks for MS map/write buffers on disconnect, capacity and bounds checks limited to starting block, ambiguous routing when both SD and MS readiness bits are set, and classic MemoryStick remap/power-loss exposure. Test signals include missing-firmware probe/read failures, SD standard versus high-capacity capacity math, MMC and SD card status parsing, MS Pro direct read/write, classic MS boot-block scan and map rebuild, REQUEST_SENSE after illegal commands, resume forcing reinit, and disconnect after classic MS allocations.
