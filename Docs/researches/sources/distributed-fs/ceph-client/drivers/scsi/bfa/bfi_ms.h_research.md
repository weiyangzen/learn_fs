# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfi_ms.h

## Purpose
`bfi_ms.h` defines message-service firmware ABI structures for IOCFC configuration, FC port, FCXP pass-through, unsolicited frame buffers, login services, remote ports, initiator target nexus, SCSI IO, task management, and MSI-X vector mapping.

## Important APIs, Types, and Functions
The file is packed and includes `bfi.h`, `bfa_fc.h`, and service definitions. `struct bfi_iocfc_cfg_s` describes queue counts, endian signature, request/response circular queues, shadow index addresses, stats/config response DMA addresses, sense buffer segments, and interrupt attributes. `struct bfi_iocfc_cfgrsp_s` returns firmware config, interrupt attributes, boot WWNs, preboot config, and queue register offsets. FC port messages cover enable/disable/service params/events/trunk SCNs. `struct bfi_fcxp_send_req_s` and `_rsp_s` define ELS/CT pass-through request/response payloads. LPS messages define login/logout and CVL events. RPORT and ITN sections define create/delete/speed/QoS/LIP and initiator-nexus lifecycles. `struct bfi_ioim_req_s`, `enum bfi_ioim_status`, `struct bfi_ioim_rsp_s`, and task management structs define SCSI IO and reset/abort firmware contracts. MSI-X enums map CB and CT ASIC vectors.

## Control Flow
The driver configures IOCFC queues, then BFA modules use these message structures for FC link, login, rport, ITN, IO, and task-management flows. IO requests carry an FCP command plus inline SGEs and optional DIF metadata. Firmware returns `bfi_ioim_rsp_s`, which BFA/BFAD maps to SCSI completion status. Task-management requests carry LUN and timeout and complete with `bfi_tskim_status`.

## State and Persistence
Most definitions represent runtime firmware state: queue DMA locations, boot WWN snapshots, FC link events, FCXP tags, login tags, rport firmware handles, ITN handles, IO tags, status/reuse semantics, and MSI-X vector layout. IOCFC config also includes boot/preboot configuration read from firmware response state.

## Dependencies and Integration Points
`bfad_im.c` consumes `bfi_ioim_status` and `bfi_tskim_status` to complete SCSI commands and task-management waits. `bfad_bsg.c` uses FCXP behavior for ELS/CT pass-through. Core BFA modules use IOCFC, FC port, RPORT, ITN, IOIM, TSKIM, and MSI-X layouts when programming firmware queues.

## Risks
Like `bfi.h`, this is a packed firmware ABI where field sizes, endian annotations, bitfields, tags, and opcodes are fixed. IO status comments describe reuse restrictions; mishandling `reuse_io_tag` or abort statuses can corrupt IO tag lifecycle. `bfi_ioim_req_s` supports max 64-byte CDBs while BFAD host setup uses 16-byte SCSI CDBs, so any feature expansion must coordinate both layers.

## Test Signals
Test IOCFC queue setup, interrupt attribute programming, link event decode, FCXP pass-through success/failure, login/logout, rport create/delete, ITN lifecycle, IO completion status mapping, abort/task-management paths, and MSI-X vector selection for CB versus CT ASICs.
