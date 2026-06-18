# sources/distributed-fs/ceph-client/drivers/scsi/3w-xxxx.c

## Purpose

`3w-xxxx.c` is the older Linux SCSI low-level driver for 3ware Storage Controller and 7000-series Escalade adapters. Unlike the 9000/SAS drivers, it does more SCSI emulation inside the driver: it handles common CDBs such as INQUIRY, TEST_UNIT_READY, READ_CAPACITY, MODE_SENSE, READ/WRITE, REQUEST_SENSE, and SYNCHRONIZE_CACHE by building legacy 3ware command packets and parameter table requests. It registers a PCI driver named `3w-xxxx`, exposes a SCSI host, handles legacy I/O-port register interrupts, and provides a privileged management character device named `twe`.

## Important APIs, Types, and Functions

Module and PCI lifecycle functions are `tw_init()`, `tw_exit()`, `tw_probe()`, `tw_remove()`, and `tw_shutdown()`. SCSI integration is through `driver_template`, with `queuecommand = tw_scsi_queue`, `eh_host_reset_handler = tw_scsi_eh_reset`, `bios_param = tw_scsi_biosparam`, `sdev_configure = tw_sdev_configure`, and `tw_host_groups`.

Request and controller primitives include `tw_state_request_start()`, `tw_state_request_finish()`, `tw_post_command_packet()`, `tw_poll_status()`, `tw_poll_status_gone()`, `tw_check_bits()`, `tw_decode_bits()`, `tw_decode_sense()`, `tw_check_errors()`, and `tw_empty_response_que()`. Initialization and reset are implemented by `tw_allocate_memory()`, `tw_initialize_device_extension()`, `tw_initconnection()`, `tw_setfeature()`, `tw_reset_sequence()`, and `tw_reset_device_extension()`.

SCSI opcode handlers include `tw_scsiop_read_write()`, `tw_scsiop_test_unit_ready()`, `tw_scsiop_test_unit_ready_complete()`, `tw_scsiop_inquiry()`, `tw_scsiop_inquiry_complete()`, `tw_scsiop_read_capacity()`, `tw_scsiop_read_capacity_complete()`, `tw_scsiop_mode_sense()`, `tw_scsiop_mode_sense_complete()`, `tw_scsiop_request_sense()`, and `tw_scsiop_synchronize_cache()`. AEN support uses `tw_aen_read_queue()`, `tw_aen_complete()`, and `tw_aen_drain_queue()`. Management ioctl support uses `tw_chrdev_open()`, `tw_chrdev_ioctl()`, and `tw_fops`.

## Control Flow

Probe enables the PCI device, sets bus mastering, requires a 32-bit coherent DMA mask, allocates a SCSI host and `TW_Device_Extension`, allocates coherent command packets and 512-byte alignment buffers, requests I/O regions, stores BAR0 as an I/O-port base, disables interrupts, and runs `tw_reset_sequence()`. Reset soft-resets the controller, drains the AEN queue, checks controller errors, performs `InitConnection`, and attempts to set the clean-shutdown feature table. Probe then configures host limits, adds the SCSI host, requests a shared IRQ, appends the adapter to the global device-extension list, enables interrupts, scans units, and registers `/dev/twe` if needed.

`tw_scsi_queue_lck()` is a CDB dispatcher. It blocks while reset is active, allocates a request ID, stores the SCSI command, and calls an opcode-specific handler. READ/WRITE maps the SCSI scatterlist, constructs legacy `TW_OP_READ` or `TW_OP_WRITE`, computes LBA and sector count from 6- or 10-byte CDBs, handles WRITE_10 DPO/FUA by setting firmware flags, fills SGL entries, updates statistics, and posts the packet. INQUIRY, TEST_UNIT_READY, READ_CAPACITY, and MODE_SENSE issue `TW_OP_GET_PARAM` commands to firmware tables; their completion handlers fabricate SCSI response buffers from returned parameters. REQUEST_SENSE returns a fixed no-sense buffer but completes with DID_ERROR, intentionally nudging error handling/reset. Unknown opcodes return ILLEGAL_REQUEST sense.

`tw_interrupt()` handles host, attention, command, and response interrupts under `host_lock`. Attention interrupts start an internal AEN read. Command interrupts retry pending requests until the hardware queue fills again, then mask command interrupts when there is no pending work. Response interrupts drain the response queue, decode command errors into sense where possible, dispatch completion by original CDB, set SCSI result, unmap DMA, call `scsi_done()`, free request IDs, and decrement posted counts. Internal AEN and char-device completions bypass SCSI completion; ioctl completions wake `ioctl_wqueue`.

The `twe` char device supports `TW_OP_NOP`, `TW_OP_AEN_LISTEN`, and `TW_CMD_PACKET_WITH_DATA`. The data ioctl copies a user command into coherent memory, patches the request ID and first SGL based on the command SGL offset, posts it as an internal request, waits up to 60 seconds, resets on timeout, and copies the response back. `TW_OP_AEN_LISTEN` drains one code from the in-memory AEN ring or returns queue-empty.

## State and Persistence Behavior

`TW_Device_Extension` runtime state includes the I/O-port base, per-request command and alignment buffers, unit-present cache, SCSI command pointers, request free/pending queues, state array, counters, host and PCI pointers, an AEN code ring, reset and ioctl flags, char-device request ID, and ioctl waitqueue/lock. No state is persisted by the driver. Unit presence and capacity are discovered from firmware parameter tables; AENs are kept only in the in-memory ring. Shutdown sends an `InitConnection` with one message credit and clears/enables interrupts just before exit.

## Dependencies and Integration Points

The file depends on the Linux PCI, coherent DMA, SCSI midlayer, interrupt, mutex, waitqueue, uaccess, block timeout, and I/O-port APIs. Its hardware interface uses `inl()`/`outl()` register macros from `3w-xxxx.h`, not MMIO mapping. Firmware integration is through legacy command packets, parameter tables, AEN tables, and clean-shutdown features. User-space integration is `/dev/twe` plus the host `stats` sysfs attribute. Supported PCI IDs are `PCI_DEVICE_ID_3WARE_1000` and `PCI_DEVICE_ID_3WARE_7000`.

## Risks and Edge Cases

The char-device open path explicitly races with remove, and the global minor-to-device list is managed only by a count. The older emulation model has more CDB-specific surface area than the 9xxx/SAS drivers, so READ/WRITE, capacity, mode page, and unit-present behavior can diverge from modern SCSI expectations. Several internal paths assume request ID 0 for reset-time polling and can be disrupted if state is not fully quiesced. DMA unmap calls happen on most completions and reset paths, but not every opcode maps data, making unmap correctness dependent on CDB path behavior. The AEN ring overwrites old entries without a clobber status like 9xxx. I/O-port register access and 32-bit DMA assumptions limit portability. `tw_setfeature()` contains an odd error branch that references `tw_dev->srb[request_id]` during reset-time setup, where no SCSI command should exist, so that path is risky if a bad alignment physical address occurs.

## Test Signals

Strong signals include probe of 1000/7000 adapters, correct `/sys/class/scsi_host/host*/stats`, SCSI scan showing online units but hiding hot spares/offline units, READ/WRITE I/O with scatterlists near `TW_MAX_SGL_LENGTH`, INQUIRY/READ_CAPACITY/MODE_SENSE response contents, `twe` AEN listen and passthrough ioctls, AEN queue drain after reset, command-queue-full pending reposts, SCSI EH reset recovery, clean shutdown notification, and fault injection for PCI parity/abort, controller queue errors, and firmware sense table mappings.
