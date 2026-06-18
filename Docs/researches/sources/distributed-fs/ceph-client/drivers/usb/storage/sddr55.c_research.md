<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/sddr55.c -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/sddr55.c

## Purpose

`sddr55.c` supports SanDisk SDDR-55 SmartMedia readers. It exposes SmartMedia as a SCSI disk by synthesizing common SCSI responses, reading device capacity IDs, maintaining logical-to-physical maps, and translating READ_10/WRITE_10 into reader-specific block commands.

## Important APIs, Types, and Functions

`struct sddr55_card_info` stores card capacity, geometry, read-only state, forced-read-only/fatal-error flags, last-access timestamp, sense data, and LBA/PBA maps. Core helpers include `sddr55_status()`, `sddr55_read_deviceID()`, `sddr55_get_capacity()`, `sddr55_read_map()`, `sddr55_read_data()`, `sddr55_write_data()`, and `sddr55_transport()`.

## Control Flow

The transport lazily allocates card state. REQUEST_SENSE returns cached sense data and clears it. INQUIRY and MODE_SENSE_10 are synthesized. Before most commands, the driver checks media status if no map exists or if the previous access is older than half a second. READ_CAPACITY identifies card size, computes usable capacity as 250 logical blocks per 256 physical blocks, returns the final 512-byte sector, and rebuilds maps. READ_10 translates SCSI page to logical block/page and reads mapped PBAs or zeros for unallocated LBAs. WRITE_10 rejects read-only/fatal states, finds spare PBAs for new LBAs, sends write commands, reads back device-reported new PBA, and updates both maps.

## State and Persistence Behavior

State is volatile in `us->extra`, but writes persist to SmartMedia and alter card-level block mappings. Media removal frees maps and clears fatal/forced-read-only flags. Map inconsistencies set `force_read_only`; severe write-map conflicts set `fatal_error`.

## Dependencies and Integration Points

The file depends on usb-storage bulk helpers, SCSI command constants, `usb_stor_access_xfer_buf()`, `fill_inquiry_response()`, `unusual_sddr55.h`, and the generic usb-storage lifecycle. It uses no external MTD layer; SmartMedia geometry and map policy are implemented locally.

## Risks and Test Signals

Risks include trusting device-returned PBAs, manual zone math, partial map updates on write failure, capacity assumptions for unknown IDs, and forcing read-only after duplicate LBA detection. Tests should cover all listed device IDs, media removal/reinsertion, read-only cards, unallocated reads, write allocation exhaustion, bad-block status, new-PBA out-of-range reports, map inconsistency, and sense codes for no media/incompatible medium/illegal command.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/sddr55.c -->
