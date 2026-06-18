# sources/distributed-fs/ceph-client/drivers/scsi/fnic/fcpio.h

## Purpose

`fcpio.h` is the host-to-firmware and firmware-to-host command ABI for FNIC FCP I/O. It defines request/response types, status codes, command tags, initiator SCSI commands, task management commands, target-mode command structures, reset/FLOGI/echo/lunmap requests, fixed-size host and firmware request unions, CQ color-bit handling, and SCSI vNIC LUN map formats.

## Important APIs, Types, and Functions

- `enum fcpio_type`: command and completion type namespace, including initiator commands (`FCPIO_ICMND_16`, `FCPIO_ICMND_32`, completions, and ITMF), target-mode requests, ACK/reset/FLOGI/echo/lunmap, and FIP FLOGI registration.
- `enum fcpio_status`: firmware header and completion status values such as invalid header/parameter, out of resources, abort, timeout, SGL invalid, data count mismatch, firmware error, task-management failure, no path, path failed, and LUN map change pending.
- `struct fcpio_tag` plus `fcpio_tag_id_*()` and `fcpio_tag_exid_*()`: encodes either a host request ID or FC OX/RX exchange IDs.
- `struct fcpio_header` plus `fcpio_header_enc()` and `fcpio_header_dec()`: common type/status/tag header for all requests and responses.
- `struct fcpio_icmnd_16` and `struct fcpio_icmnd_32`: host initiator SCSI commands with LUN map ID, SGL address/count, sense buffer address/length, CDB, flags, FC destination, and timeouts.
- `struct fcpio_itmf` and `enum fcpio_itmf_tm_req_type`: host task management and abort requests.
- Target-mode structures: `fcpio_tdata`, `fcpio_txrdy`, `fcpio_trsp`, `fcpio_ttmf_ack`, `fcpio_tabort`, target command notifications, target TMF, and target abort completions.
- Miscellaneous structures: `fcpio_reset`, `fcpio_flogi_reg`, `fcpio_flogi_fip_reg`, `fcpio_echo`, `fcpio_lunmap_req`, and their completions/notifications.
- `struct fcpio_host_req`: 128-byte host request envelope.
- `struct fcpio_fw_req`: 64-byte firmware request/completion envelope.
- `fcpio_color_enc()` and `fcpio_color_dec()`: manipulate and read the firmware request color bit, with `rmb()` after color read to order descriptor contents.
- `struct fcpio_lunmap_entry` and `struct fcpio_lunmap_tbl`: 256-entry LUN map table for SCSI vNICs.

## Control Flow

Runtime code fills `struct fcpio_host_req` with a common header and one union member, posts it through a vNIC work queue, and later receives a `struct fcpio_fw_req` from firmware. `fcpio_header_dec()` and tag decoding identify the request or exchange being completed. Initiator I/O completions use `fcpio_icmnd_cmpl` status, residual, and sense length; task management completions use ITMF response status; ACK messages carry firmware's last received work entry; reset/FLOGI/echo/lunmap completions advance control paths. Firmware-owned descriptors use the color bit in the last byte as the ownership/validity marker, and `fcpio_color_dec()` enforces a read barrier before callers inspect the rest of the descriptor.

## State and Persistence Behavior

The header itself has no mutable global state, but it defines all firmware-visible state exchanged across the host/adapter boundary. Tags persist for the lifetime of outstanding requests, SGL and sense addresses point into DMA-mapped host memory, LUN maps persist until firmware reports a change, and FLOGI registration state tells firmware the FC identity/MAC selection in use. The fixed 128-byte and 64-byte envelope sizes are an ABI persistence boundary across driver and firmware versions.

## Dependencies and Integration Points

The file depends on Ethernet address definitions from `<linux/if_ether.h>`. It is used heavily by `fnic_scsi.c` for SCSI command submission/completion, abort and reset handling, firmware reset completion, FLOGI registration completion, ACK processing, and status-to-SCSI-result mapping. It also interacts with `fnic_fdls.h` and `fip.c` through FLOGI/FIP registration payloads and with vNIC work-queue/copy-work-queue code that transports these envelopes.

## Risks and Edge Cases

- Structure layout, envelope size, and field offsets must match firmware exactly.
- Many fields are plain integer types rather than annotated `__le` or `__be`; callers must know which fields are firmware-endian, FC big-endian, or host-endian.
- Tag reuse before a delayed completion arrives can complete the wrong SCSI command; the FNIC tag and OXID lifetimes must stay aligned with this ABI.
- Incorrect SGL count/address/sense length can trigger firmware SGL errors or corrupt host memory.
- `fcpio_color_dec()` relies on hardware writing the color bit last. Removing or moving the barrier can expose stale descriptor contents.
- Status values such as `FCPIO_LUNMAP_CHNG_PEND`, `FCPIO_PATH_FAILED`, and task-management failures need careful mapping to SCSI retry, failfast, or transport events.

## Test Signals

Useful tests include normal read/write completions for 16-byte and 32-byte CDB paths, residual under/over handling, sense data transfer, abort-task and LUN-reset completions, reset completion, FLOGI and FIP FLOGI registration completion, ACK index tracking, LUN-map change notification, firmware timeout/abort/SGL-invalid/data-count-mismatch statuses, color-bit wrap, and DMA/SGL stress under queue depth.
