# Research: sources/distributed-fs/ceph-client/drivers/scsi/mpt3sas/mpt3sas_ctl.h

## Purpose

`mpt3sas_ctl.h` defines the user-visible and in-kernel management ABI for the mpt3sas control module. It provides misc-device names/minors, ioctl numbers, ioctl payload layouts, diagnostic-buffer flags, event-log payload formats, MCTP passthrough command structure, and exported function prototypes. This header is the contract consumed by `mpt3sas_ctl.c` and by user-space management tools that issue `/dev/mpt3ctl` or `/dev/mpt2ctl` ioctls.

## Important APIs, Types, And Constants

- Device identity: `MPT2SAS_DEV_NAME`, `MPT3SAS_DEV_NAME`, `MPT2SAS_MINOR`, and `MPT3SAS_MINOR` identify the gen2/gen3 misc devices.
- Ioctl opcodes: `MPT3IOCINFO`, `MPT3COMMAND`, compat `MPT3COMMAND32`, event ioctls, `MPT3HARDRESET`, `MPT3BTDHMAPPING`, diagnostic register/release/unregister/query/read/additional-query, and `MPT3ENABLEDIAGSBRRELOAD`.
- Common header: `struct mpt3_ioctl_header` carries `ioc_number`, `port_number`, and `max_data_size` and prefixes every ioctl payload.
- Controller info: `struct mpt3_ioctl_iocinfo` returns adapter type, PCI ids, firmware/BIOS/driver versions, SCSI id, capability bits, and packed PCI topology in `struct mpt3_ioctl_pci_info`.
- Event ABI: `MPT3SAS_CTL_EVENT_LOG_SIZE`, `MPT3_EVENT_DATA_SIZE`, `struct MPT3_IOCTL_EVENTS`, query/enable/report payloads define a fixed-size circular event snapshot interface.
- Firmware passthrough: `struct mpt3_ioctl_command` contains user pointers for reply, data in/out, sense data, sizes, timeout, SGE offset, and a flexible message-frame tail. `struct mpt3_ioctl_command32` maps the same ABI for 32-bit compat pointers.
- BTDH mapping: `struct mpt3_ioctl_btdh_mapping` supports bus/id-to-handle and handle-to-bus/id lookup using sentinel values.
- Diagnostic buffers: `MPT3_APP_FLAGS_*`, `MPT3_FLAGS_REREGISTER`, `MPT3_PRODUCT_SPECIFIC_DWORDS`, and `struct mpt3_diag_*` payloads define register, unregister, query, release, read, additional release-query, and SBR reload commands.
- MCTP in-kernel API: `struct mpt3_passthru_command`, `mpt3sas_get_device_count()`, and `mpt3sas_send_mctp_passthru_req()` expose a kernel-callable passthrough interface.

## Control Flow And Usage

All ioctl payloads begin with `struct mpt3_ioctl_header`; `mpt3sas_ctl.c` reads this header before dispatch so it can resolve the IOC and validate command size. For generic passthrough, user space fills `struct mpt3_ioctl_command`, points its buffer fields at user memory, sets transfer sizes and `data_sge_offset`, and appends the MPI request frame in `mf[1]`. The driver copies the request prefix up to the SGE offset, supplies DMA-backed SGLs/PRPs, waits for firmware completion, then copies data/reply/sense back through the provided pointers.

Diagnostic commands use unique ids to claim or find buffers. Register supplies buffer type, flags, product-specific dwords, requested size, and unique id. Query can use either buffer type or unique id. Release gives firmware ownership back to the driver/application boundary, read copies data starting at an aligned offset and can request repost via `MPT3_FLAGS_REREGISTER`, and unregister frees or returns the buffer depending on whether it was driver allocated.

The MCTP kernel API bypasses user pointers: `struct mpt3_passthru_command` holds kernel buffer pointers plus an `Mpi26MctpPassthroughRequest_t *`, and the implementation selects the HBA by `dev_index` among MCTP-capable adapters.

## State And Persistence Behavior

The header itself stores no state, but its layouts define the durable ABI between user-space tools and the kernel driver. Field sizes, ioctl numbers, and pointer layout are ABI-sensitive. `MPT2DIAGBUFFUNIQUEID`, `MPT3DIAGBUFFUNIQUEID`, and `MPT3_DIAG_UID_NOT_FOUND` are semantic values persisted in in-memory adapter diagnostic state and used across register/query/release/unregister operations. Event-log sizes and diagnostic product-specific array lengths constrain the driver's per-adapter allocations and copy sizes.

## Dependencies And Integration Points

The header includes `mpt3sas_base.h` for MPI types such as `Mpi26MctpPassthroughRequest_t` and `struct htb_rel_query`. Under `__KERNEL__` it includes `<linux/miscdevice.h>`. User-space compatibility depends on stable Linux ioctl encoding and exact structure packing for native and compat command layouts. The command structures integrate with `copy_from_user()`, `copy_to_user()`, DMA setup, sysfs diagnostic triggers, and MCTP-capable firmware paths in `mpt3sas_ctl.c`.

## Risks And Edge Cases

- ABI drift is the main risk. Reordering fields, changing widths, or changing ioctl numbers would break existing management utilities.
- `struct mpt3_ioctl_command` contains raw user pointers and a one-byte flexible tail pattern. The implementation must validate sizes and copy bounds carefully.
- Compat support only covers pointer conversion for the generic command; other payloads rely on identical native/compat layout.
- Event enable uses `event_types[4]`, while query uses `MPI2_EVENT_NOTIFY_EVENTMASK_WORDS`; these must remain consistent with the firmware event mask width expected by the implementation.
- Diagnostic unique ids are user/app selected except for default driver ids, so duplicate or zero ids must be rejected in implementation.
- `struct mpt3_passthru_command` is kernel-only but still has caller-provided pointers and sizes; misuse by another module can trigger invalid memory access or firmware failures.

## Test Signals

Compile-time signals include successful builds with and without `CONFIG_COMPAT`, correct ioctl size checks in the implementation, and no sparse/checkpatch warnings for user pointers. ABI tests should verify native and 32-bit compat `MPT3COMMAND`, all diagnostic payload sizes, event log sizing, and BTDH sentinel behavior. Integration tests should confirm `MPT3IOCINFO.driver_capability` reports MCTP passthrough consistently with the exported MCTP capability and that user tools built against this header interoperate with the control device.
