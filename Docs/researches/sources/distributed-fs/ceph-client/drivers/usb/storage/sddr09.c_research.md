<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/sddr09.c -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/sddr09.c

## Purpose

`sddr09.c` supports SanDisk SDDR-09 SmartMedia readers and the SmartMedia LUN of some DPCM combo readers. It translates normal SCSI block commands into the reader's vendor SCSI commands, builds NAND logical-to-physical maps, and computes SmartMedia ECC/control bytes during writes.

## Important APIs, Types, and Functions

`struct nand_flash_dev` describes supported NAND IDs and geometry. `struct sddr09_card_info` stores capacity, page/block geometry, LBA/PBA maps, LBA count, and write-protect flags. Vendor-command helpers include `sddr09_send_command()`, `sddr09_read20/21/22()`, `sddr09_writeX()`, `sddr09_read_status()`, and `sddr09_read_deviceID()`. Mapping and media helpers include `sddr09_get_cardinfo()`, `sddr09_read_map()`, `sddr09_get_wp()`, `sddr09_read_data()`, `sddr09_write_data()`, and `sddr09_write_lba()`.

## Control Flow

Initialization resets configuration, allocates card state, and initializes ECC lookup tables. READ_CAPACITY reads write-protect status and card ID, selects NAND geometry, reads the control area of every physical block, builds LBA/PBA maps, and returns logical capacity. READ_10 maps logical pages through `lba_to_pba` and reads zeros for never-written LBAs. WRITE_10 allocates or reuses a PBA, reads the whole physical block including control data, patches user pages and ECC bytes, and writes the whole block back. The DPCM transport routes LUN 0 to CompactFlash through CB transport and LUN 1 to SDDR09 after temporarily rewriting the SCSI LUN.

## State and Persistence Behavior

Per-device state is held in `us->extra`. The LBA/PBA maps are volatile reconstructions from card control bytes and are rebuilt after capacity discovery. Writes persist to SmartMedia and update in-memory maps. Static fake-sense variables in `sddr09_transport()` and static `lastpba` in `sddr09_find_unused_pba()` are process-global, which can cross-contaminate multiple devices.

## Dependencies and Integration Points

The file depends on usb-storage control/bulk helpers, SCSI opcode handling, scatterlist buffer utilities, `unusual_sddr09.h`, NAND geometry constants embedded locally, and CB reset/transport for combo devices.

## Risks and Test Signals

Risks include hand-built NAND ECC, whole-block rewrite exposure on power loss, static global fake sense and allocation cursor, limited/old NAND ID table, map corruption handling, and writing PBA 1 being silently ignored. Tests should cover each supported card size, no-media and write-protect states, duplicated/bad map entries, unwritten LBA reads, partial-block writes with ECC repair, DPCM LUN routing, and REQUEST_SENSE after faked failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/sddr09.c -->
