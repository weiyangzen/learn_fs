# sources/distributed-fs/ceph-client/drivers/usb/storage/alauda.c

## Purpose

`alauda.c` implements a USB storage subdriver for RATOC/Olympus/Fujifilm Alauda-based xD and SmartMedia card readers. It converts a small SCSI disk command set into Alauda vendor control and bulk commands, including NAND flash LBA-to-PBA mapping and ECC handling.

## Important APIs, Types, and Functions

`struct alauda_media_info` tracks per-slot capacity, geometry, zone size, page/block shifts, and lazy `lba_to_pba`/`pba_to_lba` maps. `struct alauda_info` stores two port states, a write endpoint, sense data, and media initialization state. Media and mapping helpers include `alauda_get_media_status()`, `alauda_ack_media()`, `alauda_get_media_signature()`, `alauda_init_media()`, `alauda_check_media()`, `alauda_read_map()`, `alauda_ensure_map_for_zone()`, and `alauda_free_maps()`. Data path helpers include `alauda_read_block_raw()`, `alauda_read_block()`, `alauda_write_lba()`, `alauda_read_data()`, and `alauda_write_data()`. `nand_init_ecc()`, `nand_compute_ecc()`, and related helpers manage redundancy-area ECC. `alauda_transport()` dispatches SCSI commands, and `alauda_probe()` installs the transport into usb-storage.

## Control Flow

Probe uses `usb_stor_probe1()`, assigns `Alauda Control/Bulk` transport, sets `max_lun` to 1 for xD/SmartMedia ports, and completes with `usb_stor_probe2()`. On TEST UNIT READY, READ CAPACITY, READ_10, or WRITE_10, `alauda_check_media()` polls/acknowledges media status, initializes media geometry from a signature, allocates zone-map pointer arrays, and resets media after changes. Zone maps are generated lazily by reading redundancy data for every physical block in a zone. Reads translate logical pages to mapped PBAs and return zeroes for never-written blocks. Writes read or synthesize a full physical block, update page data and ECC, write a fresh unused PBA, update maps, and erase the old PBA.

## State and Persistence Behavior

Host state includes cached media geometry, per-zone mapping tables, sense key/ASC/ASCQ, and `media_initialized`. These caches are freed on media removal/change and device disconnect. Persistent storage state is the NAND card itself: block erase/write operations, logical-address metadata in redundancy bytes, bad/unusable block markings, and generated ECC persist on media. The driver does not persist maps to disk and rebuilds them from flash metadata.

## Dependencies and Integration Points

The driver depends on usb-storage core probe, transport, scatterlist-buffer helpers, unusual-device tables, SCSI command constants, and Alauda vendor control/bulk opcodes. It integrates with the SCSI disk layer by faking INQUIRY, REQUEST_SENSE, READ_CAPACITY, and allowing medium removal while exposing block I/O through READ_10/WRITE_10.

## Risks and Test Signals

Risks include reverse-engineered protocol assumptions, unchecked failure from `alauda_ensure_map_for_zone()` because it returns void, global ECC lookup tables initialized per device, media-change state shared across both ports, write amplification and power-loss exposure during remap/erase, and fragile redundancy parsing for unknown card IDs. Test signals include xD and SmartMedia LUN behavior, media insertion/removal/unit-attention sense, card signature detection across supported IDs, lazy map creation, reads from unwritten blocks returning zeroes, ECC regeneration on partial-block writes, bad duplicate LBA handling, and disconnect cleanup after maps are allocated.
