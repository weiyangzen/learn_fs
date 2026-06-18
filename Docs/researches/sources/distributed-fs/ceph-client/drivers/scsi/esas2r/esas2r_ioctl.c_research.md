<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/esas2r/esas2r_ioctl.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/esas2r/esas2r_ioctl.c

## Purpose

`esas2r_ioctl.c` implements the ATTO ExpressSAS R6xx user-management interface. It bridges SCSI-device ioctls, `/proc/scsi/esas2r/ATTOnode`, and sysfs binary attributes to several firmware protocols: flash/FM API, FS API, VDA, CSMI, SMP passthrough, HBA ioctls, NVRAM parameter writes, and firmware core-dump retrieval. The file is not on the normal block I/O fast path, but it can issue firmware requests, build scatter/gather lists, allocate coherent DMA buffers, reset adapters, upload/download firmware data, and expose target inventory.

## Important APIs, Types, and Functions

The exported entry points are `esas2r_ioctl_handler()`, `esas2r_ioctl()`, `esas2r_write_params()`, `esas2r_read_fw()`, `esas2r_write_fw()`, `esas2r_read_vda()`, `esas2r_write_vda()`, `esas2r_read_fs()`, and `esas2r_write_fs()`. `handle_hba_ioctl()` is externally used by the sysfs `hw` binary attribute in `esas2r_main.c`.

Important internal helpers include `handle_buffered_ioctl()`, `handle_smp_ioctl()`, `handle_csmi_ioctl()`, `handle_hba_ioctl()`, `do_fm_api()`, `allocate_fw_buffers()`, `free_fw_buffers()`, and completion callbacks such as `complete_buffered_ioctl_req()`, `complete_fm_api_req()`, `complete_nvr_req()`, `vda_complete_req()`, and `fs_api_complete_req()`. `struct esas2r_buffered_ioctl` describes a reusable DMA-buffered command: adapter, source ioctl pointer, buffer length and offset, request-builder callback, and optional completion postprocessor.

The file owns module-global coherent-buffer state for buffered ioctls: `esas2r_buffered_ioctl`, `esas2r_buffered_ioctl_addr`, `esas2r_buffered_ioctl_size`, `esas2r_buffered_ioctl_pcid`, serialized by `buffered_ioctl_semaphore`. It also manipulates per-adapter firmware-transfer buffers under `a->firmware`, VDA buffers under `a->vda_buffer`, and FS API buffers under `a->fs_api_buffer`.

## Control Flow

`esas2r_ioctl_handler()` is the top-level dispatch. It validates that `arg` is present and `cmd` is in the Express ioctl range, copies a fixed `struct atto_express_ioctl` from userspace, checks `EXPRESS_IOCTL_SIGNATURE`, selects an adapter either from `hostdata` or `ioctl->header.channel`, then switches on the command. Simple commands return channel lists, adapter channel info, current/default NVRAM, or kernel pointers in `GET_MOD_INFO`. Request-producing commands call firmware helpers and translate negative kernel errors to ATTO ioctl return codes before copying the fixed ioctl structure back to userspace.

The shared buffered path is `handle_buffered_ioctl()`. It serializes all users with `down_interruptible()`, grows or allocates a global coherent buffer large enough for the command, copies the ioctl payload into that buffer, allocates an internal request, initializes an S/G context whose physical-address callback maps offsets into the coherent buffer, invokes the operation-specific callback, and waits on `a->buffered_ioctl_waiter` if the callback started asynchronous firmware work. On success it optionally runs a done callback and copies the coherent buffer back into the original ioctl object.

CSMI handling mixes local response filling and firmware tunneling. Local `GET_DRVR_INFO`, `GET_CNTLR_CFG`, `GET_CNTLR_STS`, SCSI-address lookup, and device-address lookup are handled from PCI and `targetdb` state. PHY, SMP/SSP/STP passthrough, link-error, connector, SATA signature, and task-management requests are tunneled through VDA ioctl requests with `VDA_IOCTL_CSMI`. The tunnel completion temporarily replaces the request completion callback so target ID and LUN returned by firmware are restored before the original completion path runs.

HBA ioctl handling similarly supports local adapter info, adapter address, firmware coredump trace upload/reset/info, SCSI passthrough, device address, adapter control, and limited device info, while tunneling selected functions when `HBAF_TUNNEL` is set or when the operation is backend-specific. SCSI passthrough builds a SCSI VDA request, copies CDB, LUN, direction, queue-tag flags, sense buffer pointer, and data length from the ioctl, then uses `scsi_passthru_comp_cb()` to map firmware `RS_*` status to ATTO passthrough status and advance enumeration to the next present target.

Firmware read/write uses a stateful cache. `esas2r_write_fw()` validates a flash image header at offset 0, caches command headers for upload/status queries, allocates coherent image storage for downloads, accumulates chunks, and calls `do_fm_api()` when the final byte arrives. `esas2r_read_fw()` either returns cached status, starts an upload into coherent storage, or executes an upload-size query against a temporary coherent header buffer. VDA and FS APIs follow a sysfs-like write-then-read model: writes cache the request in coherent memory; a read at offset 0 allocates a request, builds SG lists, starts firmware processing, waits for completion when needed, and then copies data back to the caller.

## State and Persistence Behavior

No on-disk state is written directly, but firmware/NVRAM state can be changed. `EXPRESS_IOCTL_WRITE_PARAMS` and `write_live_nvram` paths call `esas2r_nvram_write()` via `esas2r_write_params()`. Firmware flash paths can upload/download flash images or query flash state through FM/FS/VDA APIs. Adapter reset can be triggered by `ATTO_FUNC_ADAP_CTRL` with `ATTO_AC_AF_HARD_RST`.

Runtime state is kept in coherent buffers and per-adapter wait flags. The buffered ioctl buffer is global, reused across adapters, and protected by one semaphore. FM API, FS API, VDA, and NVRAM paths use per-adapter completion flags plus wait queues. Firmware upload/download state is kept in `a->firmware.state`, `header`, `data`, `orig_len`, and DMA addresses. The VDA and FS buffers are kept until driver unload or until reallocated larger.

## Dependencies and Integration Points

The file depends on Linux userspace copy helpers, coherent DMA APIs, PCI config/PCIe capability reads, wait queues, mutexes, semaphores, SCSI ioctl plumbing, and many ESAS2R helpers from `esas2r.h`: request allocation/free, VDA/FS/FM/NVRAM builders, SG-list construction, adapter reset, target database lookup, target enumeration, model-name helpers, and endian conversion helpers. It integrates with `esas2r_main.c` through SCSI host template `.ioctl`, `/proc` ioctl forwarding, and sysfs binary attribute read/write functions.

The firmware integration points are `esas2r_start_request()`, `esas2r_process_vda_ioctl()`, `esas2r_process_fs_ioctl()`, `esas2r_fm_api()`, `esas2r_nvram_write()`, and `esas2r_build_ioctl_req()`. User-space integration is with ATTO Express ioctl structures from `atioctl.h` and VDA structures from `atvda.h`.

## Risks and Edge Cases

The top-level ioctl copies only `sizeof(struct atto_express_ioctl)` from userspace and later uses embedded variable lengths for firmware/VDA/HBA payloads; compatibility depends on those payloads fitting the fixed union layout passed by this driver. Length arithmetic for buffered ioctls, firmware images, VDA, and FS API requests must stay bounded or coherent-buffer copies can overrun or silently truncate. Several waits use `wait_event_interruptible()` inside `while` loops without checking signal interruption, so interrupted management tools may still leave firmware work in flight.

Global buffered ioctl storage is keyed only by one semaphore and one `pcid`; reuse across adapters is serialized but still couples DMA memory lifetime to the adapter that last allocated it. Degraded-mode checks are present in selected tunnel/VDA paths but not uniformly before local operations. Adapter reset from an ioctl can race with other sysfs/proc management activity. CSMI and HBA address paths read `targetdb` entries, sometimes under `mem_lock` and sometimes without it, so target discovery/removal races are worth stress testing.

## Test Signals

Useful signals are successful Express signature validation and channel selection, GET_CHANNELS output for multiple adapters, READ/WRITE/DEFAULT_PARAMS behavior, FM firmware upload/download/status flows, FS BEGIN/read/write requests, VDA GSV/config/management/CLI/flash operations, CSMI local status/config/address commands, tunneled CSMI PHY/SMP/STP/task-management commands, HBA GET_ADAP_INFO including PCIe link fields and interrupt mode, HBA SCSI passthrough with data-in, data-out, no-data, sense data, and residuals, firmware coredump trace upload/reset/info, sysfs `fw`, `fs`, `vda`, `hw`, `live_nvram`, and `default_nvram` attributes, and failure injection for allocation failure, invalid versions/functions, degraded mode, bad target IDs, unsupported LUN encodings, and copy_to_user faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/esas2r/esas2r_ioctl.c -->
