# sources/distributed-fs/ceph-client/drivers/memstick/core/mspro_block.c Research

## Purpose
`mspro_block.c` implements block-device support for Sony MemoryStick PRO storage cards. Unlike the legacy driver, it relies on the card’s PRO logical addressing and attribute table rather than building a private FTL.

## Important APIs, Types, And Functions
The main runtime object is `struct mspro_block_data`, which stores the memstick device, blk-mq disk/queue, current request, protocol handler callback, scatterlist progress, sysfs attributes, geometry, interface mode, and active/eject flags. Driver entry points are `mspro_block_probe`, `mspro_block_remove`, optional PM callbacks, and `mspro_block_driver`. Block integration uses `mspro_queue_rq`, `mspro_block_issue_req`, `mspro_block_complete_req`, `mspro_block_stop`, `mspro_block_start`, `mspro_block_init_disk`, and `ms_block_bdops`. Protocol flow uses `h_mspro_block_req_init`, `h_mspro_block_transfer_data`, `h_mspro_block_wait_for_ced`, `h_mspro_block_get_ro`, and `h_mspro_block_setup_cmd`. Attribute parsing and sysfs exposure use `mspro_block_read_attributes` plus `mspro_block_attr_show_*`.

## Control Flow
Probe initializes card register windows, waits for CED, negotiates serial/4-bit/8-bit interface, reads write-protect state, reads the attribute directory, creates a sysfs `media_attributes` group, and registers `mspblkN`. Queue submission accepts one request at a time, maps request segments, programs a PRO parameter register with data count/address, sends read/write commands, pages data through `READ_LONG_DATA` or `WRITE_LONG_DATA`, and completes or chunks the blk request when the memstick callback chain reports CED or error.

## State And Persistence
Persistent media state is represented by the PRO attribute table, system info, device info, MBR/PBR/specfile records, and card data. Runtime state includes parsed copies of sysfs attributes, current segment/page counters, negotiated `system` bus mode, `read_only`, `active`, and `eject`. There is no driver-maintained on-card mapping; capacity comes from `user_block_count`, `block_size`, and `unit_size`.

## Dependencies And Integration Points
The driver integrates with the memstick core, blk-mq, sysfs, register-block helpers in `<linux/memstick.h>`, IDR disk numbering, gendisk, SCSI-like geometry reporting, and host capabilities such as `MEMSTICK_CAP_PAR4`, `MEMSTICK_CAP_PAR8`, and `MEMSTICK_CAP_AUTO_GET_INT`.

## Risks
Only one request is tracked, so blk-mq parallelism is intentionally constrained. `h_mspro_block_transfer_data` assumes per-segment page-size multiples and maps a single page-sized transfer view from each SG segment. Attribute parsing trusts card-provided offsets and sizes after bounded count validation; malformed attributes can exercise allocation and range logic. Resume under `CONFIG_MEMSTICK_UNSAFE_RESUME` validates only sysinfo identity, not all media state.

## Test Signals
Test with PRO cards in serial, 4-bit, and 8-bit-capable hosts; read/write workloads across SG boundaries; sysfs attribute reads for sysinfo/model/MBR/devinfo; write-protect changes; request errors and STOP command paths; removal during active I/O; suspend/resume with identical and swapped media; and dynamic major allocation through the `major` parameter.
