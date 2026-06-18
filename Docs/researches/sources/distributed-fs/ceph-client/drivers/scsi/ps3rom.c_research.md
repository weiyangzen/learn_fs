# sources/distributed-fs/ceph-client/drivers/scsi/ps3rom.c

## Purpose
`ps3rom.c` is the PlayStation 3 BD/DVD/CD-ROM SCSI driver. It presents a PS3 storage ROM device as an emulated SCSI host, translates SCSI packet and READ/WRITE_10 commands into PS3 LV1 storage hypervisor operations, and completes commands from the PS3 storage interrupt path.

## Important APIs, types, and functions
`struct ps3rom_private` stores the PS3 storage device and the single current SCSI command. `struct lv1_atapi_cmnd_block` is the hypervisor ATAPI command block. SCSI configuration is in `ps3rom_sdev_configure()`, which forces 10-byte MODE SENSE and READ/WRITE behavior. Command builders are `ps3rom_atapi_request()`, `ps3rom_read_request()`, and `ps3rom_write_request()`, with helpers `srb10_lba()` and `srb10_len()`. The SCSI queue entry is `ps3rom_queuecommand()`, completion runs through `ps3rom_interrupt()`, and device lifecycle is `ps3rom_probe()`, `ps3rom_remove()`, `ps3rom_init()`, and `ps3rom_exit()`.

## Control flow
Probe accepts only CD frame-sized block devices, allocates a 64 KiB GFP_DMA bounce buffer, calls `ps3stor_setup()` with `ps3rom_interrupt`, allocates a one-target/one-LUN SCSI host, stores the host in ps3 system-bus driver data, adds the host, and scans. Queueing stores the command as `curr_cmd`, dispatches READ_10 and WRITE_10 through direct `lv1_storage_read()`/`lv1_storage_write()`, and dispatches other commands as ATAPI packets through `lv1_storage_send_device_command()`. Write and ATAPI data-out paths copy from SCSI SG lists to the bounce buffer before issuing LV1 operations.

Interrupt completion calls `lv1_storage_get_async_status()`, checks the tag, fetches `curr_cmd`, copies bounce data back to the SCSI SG list on successful reads/data-in operations, sets residuals, decodes LV1 CHECK CONDITION status into SCSI sense data when possible, clears `curr_cmd`, and calls `scsi_done()`. Immediate command-submission failure builds ILLEGAL REQUEST sense and completes synchronously.

## State and persistence behavior
The driver is volatile and single-command (`can_queue = 1`). Persistent media state is outside the driver. The active async operation is correlated by `dev->tag` and `priv->curr_cmd`. Data staging uses `dev->bounce_buf`, `dev->bounce_lpar`, and `dev->bounce_size`.

## Dependencies and integration points
The file depends on PS3-specific system bus/storage helpers, LV1 hypervisor calls, SCSI midlayer, cdrom constants, highmem/slab allocation, and scatterlist copy helpers. It integrates with the PS3 storage core through `ps3stor_setup()`/`ps3stor_teardown()` and `ps3_system_bus_driver_register()`.

## Risks and test signals
Risks include relying on a single `curr_cmd`, tag mismatch only being logged, fixed 12-byte ATAPI packet copy regardless of CDB length, bounce-buffer size limiting max sectors, and error paths where an interrupt with no valid current command would be unsafe. Tests should cover probe rejection of non-CD frame block sizes, READ_10/WRITE_10 boundary sector counts, ATAPI non-data and data-in/out commands, LV1 policy-denied errors, CHECK CONDITION decoding, REQUEST_SENSE error handling, tag mismatch logging, remove after active command quiescence, and SG residual accounting.
