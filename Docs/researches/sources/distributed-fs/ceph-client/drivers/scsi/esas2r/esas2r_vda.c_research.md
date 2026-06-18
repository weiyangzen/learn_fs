<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/esas2r/esas2r_vda.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/esas2r/esas2r_vda.c

## Purpose

`esas2r_vda.c` builds and completes ESAS2R VDA firmware requests. It validates user-supplied VDA ioctl functions and versions, maps ioctl payloads into firmware request unions, constructs S/G lists for flash, CLI, management, config, and asynchronous-event requests, performs host/firmware endian conversion for management/config/event data, and starts requests through the common request engine.

## Important APIs, Types, and Functions

The main external API is `esas2r_process_vda_ioctl()`, used by ioctl/sysfs VDA read paths to prepare a firmware request. Other exported builder helpers are `esas2r_build_flash_req()`, `esas2r_build_mgt_req()`, `esas2r_build_ae_req()`, `esas2r_build_ioctl_req()`, and `esas2r_build_cfg_req()`. Internal helpers are `esas2r_complete_vda_ioctl()` and `clear_vda_request()`.

`esas2r_vdaioctl_versions[]` is the function-version compatibility table, indexed by VDA function. The request target is `rq->vrq`, a `union atto_vda_req`, with companion response state in `rq->func_rsp` and data buffer state in `rq->data_buf` / `rq->vda_rsp_data`.

## Control Flow

`esas2r_process_vda_ioctl()` starts by setting host-visible success and pending VDA status. It rejects unknown function indexes, too-new versions, and degraded adapters. Non-SCSI functions clear the VDA request while preserving the firmware handle. The request function, interrupt callback, and callback context are installed, then a switch fills the function-specific request.

Flash ioctl accepts file read, write, and info subfunctions, copies the filename, sets length and subfunction, and uses the flash file SGE as the first data SGE for read/write. CLI sets command/response length and data length. Management has the most complex flow: for health and metrics requests it may build a payload SGL separately from the management command SGL; for device-info variants it treats the ioctl data area as the command data; other data-bearing management functions are rejected. Config only supports `VDA_CFG_GET_INIT` through this ioctl path, copies config input data, and endian-converts it before firmware submission. GSV is local: it returns the version table and marks VDA status success without starting firmware work.

When a data length is present, the function initializes an S/G context at the selected first SGE, sets the length, builds the S/G list, and returns an out-of-resources status on failure. For firmware-submitted commands it calls `esas2r_start_request()` and returns true to tell the caller to wait for completion.

`esas2r_complete_vda_ioctl()` copies firmware response fields back into the ioctl. Flash read/info updates file size. Management updates scan generation, device index, optional returned data length, and endian-converts management data back. Config GET_INIT builds user-visible firmware release/version strings and numeric fields. CLI updates command response length.

The builder helpers are used by lower-level driver flows as well as ioctl flows. They clear the request, set the VDA function/subfunction/length, choose legacy SGE versus PRDE layout based on `AF_LEGACY_SGE_MODE`, and copy or endian-convert payloads as needed.

## State and Persistence Behavior

The file does not persist data itself, but VDA requests can query or mutate firmware configuration, RAID groups, flash contents, device health, and asynchronous-event state. Request-local state is stored in `rq->vrq`, `rq->req_stat`, `rq->interrupt_cb`, `rq->interrupt_cx`, `rq->data_buf`, and request list linkage. `clear_vda_request()` preserves the request handle while clearing the rest of the request and data buffer, then initializes the list head to keep non-started requests safe.

## Dependencies and Integration Points

The file depends on VDA ABI types and constants from `atvda.h`, ATTO ioctl definitions, ESAS2R request and SG helpers, adapter degraded/legacy flags, endian conversion helpers in `esas2r_main.c`, and the common firmware start path. It integrates with `esas2r_ioctl.c` for sysfs/ioctl VDA requests and with event/discovery code for management and asynchronous-event requests.

## Risks and Edge Cases

Function-version validation relies on the version table matching firmware ABI expectations. Management requests change `sgc->cur_offset` in non-obvious ways to build payload and command SGLs from different portions of the ioctl buffer; offset mistakes can DMA the wrong user payload. `clear_vda_request()` preserves only the SCSI handle, so callers must reinitialize every required field. GSV completes locally and returns success without starting a request; callers must honor the boolean return. Endian conversion helpers are symmetric in practice but named `nuxi`; applying them twice or missing them on a path will corrupt fields. Builder helpers use `if (vrq->length)` on a little-endian field, which works for nonzero checks but is stylistically fragile.

## Test Signals

Useful tests include invalid function/version/degraded-mode rejection, GSV local completion, flash FINFO/FREAD/FWRITE with file-size response, CLI command length round trip, management health/metrics payload SGLs, device-info management variants, config GET_INIT firmware-release formatting, legacy SGE and PRDE modes, out-of-SGL-resource failure, asynchronous-event request layout, and endian-correct values for capacities, block sizes, target IDs, scan generation, and firmware version fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/esas2r/esas2r_vda.c -->
