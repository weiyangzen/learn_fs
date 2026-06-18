# Research Group subset-b-005220

Work item `subset-b-005220` covers the Linux 3ware SCSI RAID controller drivers and their 9000/SAS protocol headers under `sources/distributed-fs/ceph-client/drivers/scsi/`. The files are related but split by hardware generation: `3w-xxxx.c` handles older Escalade/7000-style controllers with legacy I/O port registers and driver-side SCSI command emulation, `3w-9xxx.c` handles 9000/9550/9650/9690 controllers with Apache-style command packets and firmware `EXECUTE_SCSI`, and `3w-sas.c` handles 9750 SAS/SATA controllers with Liberator doorbell/MFA queues and separate sense-buffer posting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/3w-9xxx.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/3w-9xxx.c

## Purpose

`3w-9xxx.c` is the Linux SCSI low-level driver for 3ware 9000-family storage controllers. It registers a PCI driver named `3w-9xxx`, exposes a SCSI host template, translates kernel SCSI commands into firmware `TW_OP_EXECUTE_SCSI` command packets, handles controller interrupts and asynchronous event notifications, and provides a privileged management character device named `twa`. It supports the 9000, 9550SX, 9650SE, and 9690SA device IDs, including different register offsets and large command queue posting for later adapters.

## Important APIs, Types, and Functions

The module entry points are `twa_init()` and `twa_exit()`, which register and unregister the `pci_driver`. PCI lifecycle is handled by `twa_probe()`, `twa_remove()`, `twa_shutdown()`, and power-management callbacks `twa_suspend()` and `twa_resume()`. The SCSI integration surface is `driver_template`, with `queuecommand = twa_scsi_queue`, `eh_host_reset_handler = twa_scsi_eh_reset`, `bios_param = twa_scsi_biosparam`, `sdev_configure = twa_sdev_configure`, and the `twa_host_groups` sysfs attribute group.

Request execution runs through `twa_scsi_queue_lck()`, `twa_scsiop_execute_scsi()`, `twa_post_command_packet()`, `twa_interrupt()`, and `twa_scsiop_execute_scsi_complete()`. Request IDs are managed with `twa_get_request_id()` and `twa_free_request_id()` against the `free_queue`, `pending_queue`, and `state[]` arrays in `TW_Device_Extension`. Management I/O uses `twa_chrdev_open()` and `twa_chrdev_ioctl()`, with the ioctl ABI defined in `3w-9xxx.h`.

Controller initialization and recovery are concentrated in `twa_reset_sequence()`, `twa_reset_device_extension()`, `twa_initconnection()`, `twa_check_srl()`, `twa_get_param()`, `twa_poll_status()`, `twa_poll_status_gone()`, `twa_empty_response_queue()`, and `twa_empty_response_queue_large()`. AEN handling uses `twa_aen_read_queue()`, `twa_aen_complete()`, `twa_aen_drain_queue()`, `twa_aen_queue_event()`, `twa_aen_sync_time()`, and `twa_aen_severity_lookup()`.

## Control Flow

Probe enables the PCI device, sets bus mastering/MWI, tries a 64-bit coherent DMA mask with 32-bit fallback, allocates a `Scsi_Host`, initializes DMA command and generic buffers, requests PCI regions, maps the controller BAR, disables interrupts, and runs `twa_reset_sequence()` in non-soft-reset mode. The reset sequence waits for controller readiness, drains stale responses, checks firmware/driver SRL compatibility with `InitConnection`, drains AENs, and records compatibility metadata. Probe then configures SCSI host limits, adds the host, prints firmware/BIOS/port data via firmware parameter reads, optionally enables MSI for non-9000 devices, requests the shared IRQ, publishes the adapter in `twa_device_extension_list`, enables interrupts, scans devices, and registers the `twa` char device if it is not already registered.

Normal I/O starts when the SCSI midlayer calls `twa_scsi_queue()`. The driver refuses new work while `TW_IN_RESET` is set, rejects nonzero LUNs if firmware SRL is too old, allocates a request ID, stores the `scsi_cmnd` in `srb[]`, and builds a 16-byte CDB `TW_Command_Apache` packet. Small single-entry transfers below `TW_MIN_SGL_LENGTH` are copied through a per-request coherent generic buffer; larger or multi-entry transfers use `scsi_dma_map()` and firmware SGL entries. `twa_post_command_packet()` either writes the command-packet DMA address to the appropriate command queue register or queues the request in `pending_queue` and unmasks command interrupts when the hardware queue is full.

`twa_interrupt()` serializes completions under `host_lock`. It validates interrupt status, ignores interrupts during reset, decodes clearable PCI/controller errors, clears host/attention interrupts, drains pending posts on command interrupts, and drains response queue entries on response interrupts. For firmware command errors, `twa_fill_sense()` prints or copies sense data from the command header. Internal AEN and char-device requests are completed without calling `scsi_done()`. SCSI requests run copy-back for small read buffers, set result status, optionally report residual bytes, unmap DMA, call `scsi_done()`, free the request ID, and decrement posted counts.

Management ioctl flow is serialized by a global `twa_chrdev_mutex` plus per-controller `ioctl_lock`. `TW_IOCTL_FIRMWARE_PASS_THROUGH` copies a user command into coherent memory, patches request IDs and SGLs with `twa_load_sgl()`, posts it as an internal command, waits up to `TW_IOCTL_CHRDEV_TIMEOUT`, resets the controller on timeout, and copies the firmware response back. Other ioctls expose compatibility info, walk the AEN event ring, or implement an advisory lock with an expiration time.

## State and Persistence Behavior

All persistent runtime state is in memory. `TW_Device_Extension` stores MMIO base address, coherent command/generic buffers, command states, queue heads/tails, per-request `srb[]` pointers, stats counters, reset flags, the AEN event ring, compatibility info, and char-device wait/lock state. The driver does not persist metadata to disk; firmware state is queried or updated through controller parameter tables and `InitConnection`. Shutdown/suspend notify the controller by sending `InitConnection` with one message credit and feature zero, then clear interrupts.

## Dependencies and Integration Points

The file depends on the kernel PCI, DMA, SCSI midlayer, block timeout, sysfs host attributes, interrupt, waitqueue, mutex, uaccess, and time APIs. Hardware integration is through MMIO register macros from `3w-9xxx.h`; firmware integration is through 3ware command packets, SRL compatibility negotiation, parameter table reads, REQUEST_SENSE AEN polling, and management passthrough. User-space integration is through `/dev/twa` and a `stats` host sysfs attribute. The driver also relies on the global `sys_tz` timezone when converting host time for AEN timestamps and time synchronization.

## Risks and Edge Cases

The char-device minor lookup races with remove; the source explicitly notes this in `twa_chrdev_open()`, and the global device-extension list is compacted by decrementing a count without clearing or reindexing removed slots. The ioctl passthrough path trusts the user-supplied firmware command shape after size checks and must correctly patch SGL positions for both old and Apache command formats, including PAE and 9690SA-specific layout. Request state transitions are split across queueing, ISR, reset, and ioctl timeout paths; missing a posted-count decrement or DMA unmap can corrupt later completions. Small-buffer copy-through depends on `twa_command_mapped()` and must stay in sync with completion copy-back. Firmware error strings are parsed from adjacent strings in `err_specific_desc`, so malformed firmware buffers could affect printed/logged parameter text if not NUL-terminated; the driver clamps one terminator before copying. Suspend/resume has ordering risk around MSI re-enable: resume requests the IRQ before re-enabling MSI if `TW_USING_MSI` was set.

## Test Signals

Useful validation signals include successful PCI probe with firmware/BIOS/port printk lines, SCSI scan discovering the expected units and LUN behavior by firmware SRL, `/sys/class/scsi_host/host*/stats` showing posted/pending/SG/reset/AEN counters, passthrough ioctl completion and timeout reset behavior, AEN generation and retrieval through the event ioctls, reset recovery from SCSI EH timeouts, suspend/resume with and without `use_msi=1`, and stress I/O with small single-SGL buffers, large multi-SG DMA, command-queue-full pending reposts, and controller error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/3w-9xxx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/3w-9xxx.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/3w-9xxx.h

## Purpose

`3w-9xxx.h` is the private protocol and state definition header for the 3ware 9000-family driver. It defines the command packet wire layouts, register bits, PCI IDs, firmware opcodes, AEN/error text tables, ioctl ABI structures, queue-state constants, SGL sizing rules, and `TW_Device_Extension` state used by `3w-9xxx.c`.

## Important APIs, Types, and Definitions

The AEN and error translation surfaces are `twa_message_type`, `twa_aen_table`, `twa_aen_severity_table`, and `twa_error_table`. Register definitions include control bits such as `TW_CONTROL_CLEAR_ATTENTION_INTERRUPT`, `TW_CONTROL_DISABLE_INTERRUPTS`, and `TW_CONTROL_ISSUE_SOFT_RESET`, plus status bits such as `TW_STATUS_RESPONSE_INTERRUPT`, `TW_STATUS_COMMAND_QUEUE_FULL`, `TW_STATUS_MICROCONTROLLER_READY`, and masks for expected/unexpected interrupt state.

Firmware opcodes and protocol constants include `TW_OP_INIT_CONNECTION`, `TW_OP_GET_PARAM`, `TW_OP_SET_PARAM`, `TW_OP_EXECUTE_SCSI`, `TW_OP_DOWNLOAD_FIRMWARE`, and `TW_OP_RESET`. Compatibility constants such as `TW_9000_ARCH_ID`, `TW_CURRENT_DRIVER_SRL`, `TW_BASE_FW_SRL`, and `TW_FW_SRL_LUNS_SUPPORTED` drive reset-time SRL negotiation. The header also defines request states `TW_S_INITIAL`, `TW_S_STARTED`, `TW_S_POSTED`, `TW_S_PENDING`, `TW_S_COMPLETED`, and `TW_S_FINISHED`.

Command wire types are `TW_SG_Entry`, `TW_Command` for older command packets, `TW_Command_Apache` for 9000+ execute-SCSI packets, `TW_Command_Apache_Header` for sense/error metadata, `TW_Command_Full` as a header-plus-union wrapper, and `TW_Initconnect` for controller connection negotiation. Management ABI types are `TW_Event`, `TW_Ioctl_Driver_Command`, `TW_Ioctl_Buf_Apache`, `TW_Lock`, `TW_Param_Apache`, `TW_Response_Queue`, and `TW_Compatibility_Info`. `TW_Device_Extension` is the main in-memory adapter object.

## Control Flow Supported by the Header

The macros encode all controller register access patterns used by the C file: `TW_CONTROL_REG_ADDR()`, `TW_STATUS_REG_ADDR()`, command/response queue address macros for normal and large queues, `TW_CLEAR_*`, `TW_DISABLE_INTERRUPTS()`, `TW_ENABLE_AND_CLEAR_INTERRUPTS()`, `TW_MASK_COMMAND_INTERRUPT()`, `TW_UNMASK_COMMAND_INTERRUPT()`, and `TW_SOFT_RESET()`. Packet-field macros pack and unpack firmware bitfields without C bitfields: `TW_OPRES_IN()`, `TW_OPSGL_IN()`, `TW_OP_OUT()`, `TW_SGL_OUT()`, `TW_SEV_OUT()`, `TW_RESID_OUT()`, `TW_REQ_LUN_IN()`, and `TW_LUN_OUT()`.

DMA width controls are centralized through `twa_addr_t` and `TW_CPU_TO_SGL()`, switching between little-endian 64-bit and 32-bit SGL addresses based on `CONFIG_ARCH_DMA_ADDR_T_64BIT`. `TW_COMMAND_SIZE`, `TW_APACHE_MAX_SGL_LENGTH`, `TW_ESCALADE_MAX_SGL_LENGTH`, and `TW_PADDING_LENGTH` adapt packet layout to DMA address size.

## State and Persistence Behavior

`TW_Device_Extension` contains only runtime state. It stores the MMIO base, coherent buffers and DMA addresses for command packets and per-request generic data, request-to-SCSI-command mappings, free and pending queues, request states, posted and pending counters, SGL/sector/reset/AEN counters, host and PCI pointers, bit flags for reset/MSI/attention-loop state, a circular `TW_Event` queue with wrap/clobber indicators, char-device lock and waitqueue state, and cached compatibility information. None of these structures are persistent across unload or reboot; persistent controller facts are retrieved from firmware parameter tables.

## Dependencies and Integration Points

The header assumes kernel types such as `__le16`, `__le32`, `__le64`, `dma_addr_t`, `struct pci_dev`, `struct scsi_cmnd`, `struct Scsi_Host`, `wait_queue_head_t`, `struct mutex`, and `ktime_t`. It is tightly coupled to Linux SCSI, PCI, DMA, MMIO, and uaccess code in `3w-9xxx.c`. The ioctl structures form a user-visible ABI for 3ware management tools, so field order, packing, flexible array placement, and command padding are compatibility-sensitive.

## Risks and Edge Cases

The header contains static lookup tables in a header rather than `extern` declarations; that is acceptable because it is included by one C file, but including it elsewhere would create duplicated table definitions. Several wire structures are `__packed` or manually padded; changes can silently break firmware ABI, especially around 32-bit versus 64-bit DMA address sizes. The AEN event timestamp is 32-bit seconds and the C file notes a year-2106 overflow. `TW_PRINTK` is a multi-statement macro without `do { } while (0)`, so use in unusual conditional contexts would be fragile. Ioctl constants and error codes are part of the management ABI and should not be renumbered.

## Test Signals

Header-level validation comes from successful compilation on 32-bit and 64-bit DMA configurations, correct `sizeof()` and alignment of command packet structures, working firmware passthrough for old and Apache packets, correct LUN/request ID packing, successful AEN text decoding, and probe-time SRL compatibility output matching firmware values. Regression tests should include sparse/endian checks because the 9000 header deliberately uses little-endian fields in firmware-facing structures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/3w-9xxx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/3w-sas.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/3w-sas.c

## Purpose

`3w-sas.c` is the SCSI low-level driver for LSI 3ware 9750 SAS/SATA RAID controllers. It shares the broad 3ware SCSI-host model with `3w-9xxx.c`, but uses the 9750 "Liberator" register interface: inbound host queues, outbound response queues, doorbell interrupts, and pre-posted sense buffers. It registers a PCI driver named `3w-sas`, exposes a `twl` management character device for firmware passthrough, and adds sysfs binary files for AEN and compatibility data.

## Important APIs, Types, and Functions

Module and PCI entry points are `twl_init()`, `twl_exit()`, `twl_probe()`, `twl_remove()`, `twl_shutdown()`, `twl_suspend()`, and `twl_resume()`. SCSI integration is through `driver_template`, with `queuecommand = twl_scsi_queue`, `eh_host_reset_handler = twl_scsi_eh_reset`, `bios_param = twl_scsi_biosparam`, `sdev_configure = twl_sdev_configure`, and `twl_host_groups`.

I/O path functions are `twl_scsi_queue_lck()`, `twl_scsiop_execute_scsi()`, `twl_post_command_packet()`, and `twl_interrupt()`. Request allocation uses `twl_get_request_id()` and `twl_free_request_id()`. AEN and controller management flows use `twl_handle_attention_interrupt()`, `twl_aen_read_queue()`, `twl_aen_complete()`, `twl_aen_drain_queue()`, `twl_aen_queue_event()`, `twl_aen_sync_time()`, `twl_get_param()`, `twl_initconnection()`, and `twl_reset_sequence()`.

User-visible management surfaces are `twl_chrdev_open()`, `twl_chrdev_ioctl()`, the `twl_fops` char-device operations, `twl_sysfs_aen_read()`, `twl_sysfs_compat_info()`, and `twl_show_stats()`. Error handling uses `twl_fill_sense()` with the separately posted sense buffers defined in `3w-sas.h`.

## Control Flow

Probe enables the PCI device, sets bus mastering/MWI, requires a 64-bit coherent DMA mask, allocates a SCSI host and private device extension, allocates coherent command packets, generic buffers, and sense buffers, requests PCI regions, maps BAR 1, masks interrupts, and calls `twl_reset_sequence()`. Reset optionally soft-resets the controller, waits for scratchpad readiness transitions, performs extended `InitConnection`, posts every sense buffer address to the firmware, checks controller status, drains AENs, and records compatibility metadata. Probe then configures host limits, adds the SCSI host, prints model/firmware/BIOS/PHY data from parameter tables, optionally enables MSI, requests the shared IRQ, registers the adapter in `twl_device_extension_list`, unmasks interrupts, scans the host, creates `3ware_aen_read` and `3ware_compat_info` binary sysfs files, and registers `/dev/twl` if needed.

Normal SCSI I/O allocates a request ID, saves `SCpnt`, builds an Apache execute-SCSI packet, maps all scatterlist entries with `scsi_dma_map()`, writes SGL entries through `TW_CPU_TO_SGL()`, updates sector/SGL stats, and posts the command DMA address by writing high then low queue registers with `TWL_PULL_MODE`. The Liberator path does not maintain a pending queue for command-queue-full retry in the way the older drivers do; it assumes the host queue post succeeds once the packet is written.

Interrupt handling reads `TWL_HISTAT`. Attention interrupts call `twl_handle_attention_interrupt()`, which reads the outbound doorbell, detects controller errors, starts AEN REQUEST_SENSE polling if not already in the attention loop, and clears the doorbell. Response interrupts read an outbound MFA from high/low queue registers. If `TW_NOTMFA_OUT()` indicates the value is a sense-buffer address rather than a normal response, the ISR finds the matching sense buffer, extracts the request ID from its header, copies or prints sense data, and reposts that sense buffer to firmware. Normal responses get the request ID from `TW_RESID_OUT()`. Internal AEN/ioctl completions wake or continue their state machines; SCSI completions set result, report residual bytes for single-SG commands, unmap DMA, complete the command, free the request, and decrement posted counts.

The char-device ioctl path supports `TW_IOCTL_FIRMWARE_PASS_THROUGH` only. It is serialized by `twl_chrdev_mutex` and `ioctl_lock`, copies the user ioctl into coherent memory, patches request ID and SGL fields for old or new command packets with `twl_load_sgl()`, posts the command, waits for `chrdev_request_id` to become free, resets on timeout, copies the response back, and frees the coherent ioctl buffer.

## State and Persistence Behavior

Runtime state is stored in `TW_Device_Extension`: MMIO base, command/generic/sense coherent buffers and DMA addresses, SCSI command pointers, request free queue and states, counters, AEN event queue, compatibility info, char-device wait state, MSI/reset/attention flags, and an `online` flag used by shutdown/remove guards. Sysfs binary files expose in-memory AEN and compatibility buffers directly through `memory_read_from_buffer()` under `host_lock`; they do not persist events beyond the in-memory ring. The controller is notified on suspend/shutdown through `InitConnection` with one credit and no features.

## Dependencies and Integration Points

The driver depends on Linux PCI, coherent DMA, SCSI midlayer, interrupts, sysfs binary attributes, block queue timeout APIs, waitqueues, mutexes, and uaccess. Firmware integration is through Liberator registers, inbound/outbound queue MFAs, sense-buffer posting, parameter tables, and 3ware ioctl-compatible command packets. User-space integration includes `/dev/twl`, `3ware_aen_read`, `3ware_compat_info`, and host stats `3ware_stats`. The management interface is described as used by smartmontools.

## Risks and Edge Cases

`twl_probe()` requires a 64-bit DMA mask and does not fall back to 32-bit DMA, so older or constrained platforms fail probe. `twl_scsiop_execute_scsi()` treats `scsi_dma_map()` returning zero as failure, which may matter for valid zero-data commands if they ever reach this path. Residual calculation compares firmware SGL length in command storage without endian conversion and can be suspicious on big-endian platforms. The char-device minor lookup has the same global-array/remove shape as the 9xxx driver, but without an explicit race comment. Sense-buffer matching is a linear scan over `TW_Q_LENGTH` entries per sense response; correctness depends on the firmware returning exact DMA addresses and on reposting every buffer after use. The `online` guard avoids double shutdown but must be set and cleared consistently across partial probe and remove paths.

## Test Signals

Validation should cover 9750 PCI probe, 64-bit DMA setup, sense-buffer posting without `TWL_STATUS_OVERRUN_SUBMIT`, sysfs binary reads gated by `CAP_SYS_ADMIN`, firmware passthrough via `/dev/twl`, AEN generation and time-sync handling, reset after SCSI EH timeout and ioctl timeout, suspend/resume with MSI enabled and disabled, and I/O stress with multi-SG reads/writes while injecting firmware sense responses and doorbell attention interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/3w-sas.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/3w-sas.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/3w-sas.h

## Purpose

`3w-sas.h` defines the private hardware protocol, firmware command formats, ioctl ABI, and per-controller state for the LSI 3ware 9750 SAS/SATA RAID driver. It is the Liberator/SAS counterpart to `3w-9xxx.h`, with different register offsets, response encoding, SGL layout, and sense-buffer state.

## Important APIs, Types, and Definitions

Register definitions cover the Liberator status, inbound doorbell, host interrupt status/mask, outbound doorbell/clear, scratchpad, inbound queue, and outbound queue registers: `TWL_STATUS`, `TWL_HIBDB`, `TWL_HISTAT`, `TWL_HIMASK`, `TWL_HOBDB`, `TWL_HOBDBC`, `TWL_SCRPD3`, `TWL_HIBQPL/H`, and `TWL_HOBQPL/H`. Interrupt and status bits include `TWL_HISTATUS_VALID_INTERRUPT`, `TWL_HISTATUS_ATTENTION_INTERRUPT`, `TWL_HISTATUS_RESPONSE_INTERRUPT`, `TWL_STATUS_OVERRUN_SUBMIT`, `TWL_CONTROLLER_READY`, `TWL_DOORBELL_CONTROLLER_ERROR`, and `TWL_DOORBELL_ATTENTION_INTERRUPT`.

Firmware constants define `TW_OP_INIT_CONNECTION`, `TW_OP_GET_PARAM`, `TW_OP_SET_PARAM`, `TW_OP_EXECUTE_SCSI`, AEN codes, request states, 9750 compatibility values (`TW_9750_ARCH_ID`, `TW_CURRENT_DRIVER_SRL`), queue sizes, ioctl limits, parameter table IDs, and the 9750 PCI ID. Field macros include `TW_OPRES_IN()`, `TW_OPSGL_IN()`, `TW_OP_OUT()`, `TW_SGL_OUT()`, `TW_SEV_OUT()`, `TW_RESID_OUT()`, `TW_NOTMFA_OUT()`, `TW_REQ_LUN_IN()`, and `TW_LUN_OUT()`.

Wire structs are packed around `#pragma pack(1)`: `TW_SG_Entry_ISO`, `TW_Command`, `TW_Command_Apache`, `TW_Command_Apache_Header`, `TW_Command_Full`, `TW_Initconnect`, `TW_Event`, `TW_Ioctl_Driver_Command`, `TW_Ioctl_Buf_Apache`, `TW_Param_Apache`, and `TW_Compatibility_Info`. `TW_Device_Extension` stores the driver runtime state, including separate `sense_buffer_virt/phys` arrays that are unique to the SAS driver among the files in this work item.

## Control Flow Supported by the Header

The register macros implement the queue and doorbell protocol used by `3w-sas.c`: `TWL_MASK_INTERRUPTS()`, `TWL_UNMASK_INTERRUPTS()`, `TWL_CLEAR_DB_INTERRUPT()`, `TWL_SOFT_RESET()`, and address macros for high/low inbound/outbound queue writes and reads. The command-size and SGL-length macros adapt old and new command packets to 32-bit versus 64-bit `dma_addr_t` sizes: `TW_COMMAND_SIZE`, `TW_LIBERATOR_MAX_SGL_LENGTH`, `TW_LIBERATOR_MAX_SGL_LENGTH_OLD`, and padding lengths.

Response decoding differs from 9xxx: the outbound value may be an MFA or a normal response. `TW_NOTMFA_OUT()` identifies normal request-ID responses, while non-MFA responses are matched against pre-posted sense-buffer DMA addresses. LUN and request IDs are packed into 16-bit fields and converted by the C file with `cpu_to_le16()` around `TW_REQ_LUN_IN()`.

## State and Persistence Behavior

The header defines no durable storage. `TW_Device_Extension` persists only while the driver owns the PCI function. It contains command/generic/sense DMA buffers, request state, stats, AEN ring state, char-device state, compatibility info, and an `online` boolean. The AEN ring and compatibility data can be exposed through sysfs, but they are snapshots of volatile memory and are rebuilt after probe/reset from firmware events and `InitConnection` data.

## Dependencies and Integration Points

The header depends on kernel DMA, PCI, SCSI, waitqueue, mutex, and MMIO types supplied by the C file includes. Its ioctl packet layout is user-visible through the `twl` character device and must remain compatible with management tools such as smartmontools. The firmware-facing structs are sensitive to packing and architecture-dependent DMA address size.

## Risks and Edge Cases

`TW_SG_Entry_ISO` uses `dma_addr_t` for both address and length, making the SGL entry size architecture-dependent; the padding macros compensate, but any change in type assumptions can break command layout. `TW_CPU_TO_SGL()` selects `cpu_to_le64()` or `cpu_to_le32()` with a runtime `sizeof(dma_addr_t)` expression, so static analysis and endian testing are important. Several register macros take an argument `x` but reference `tw_dev` inside the macro body, which works only when the local variable is named `tw_dev`; this is fragile macro hygiene. Like the 9xxx header, `TW_PRINTK` is a raw multi-statement macro.

## Test Signals

Expected test signals include successful compilation on supported architectures, correct command and header sizes for 9750 firmware, successful reset-time sense-buffer registration, accurate request ID extraction from response and sense-buffer paths, working sysfs reads of `TW_Event` and `TW_Compatibility_Info`, and valid firmware passthrough for both old and Apache command variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/3w-sas.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/3w-xxxx.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/3w-xxxx.c -->
