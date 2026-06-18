# `sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_fsf.h`

## Purpose

`zfcp_fsf.h` defines the hardware-facing FSF command constants, status values, qualifiers, feature bits, QTCB wire layouts, status-read payload layouts, port/config data layouts, block trace metadata, and CT/ELS request envelope used by the zfcp FSF implementation. It is the protocol contract between zfcp and the FCP adapter firmware.

## Important APIs, Types, And Data

- FSF command constants include FCP command, abort, open/close port/LUN, close physical port, send ELS/generic CT, exchange config/port data, and control file commands.
- QTCB type constants distinguish IO, support, config, and port commands.
- Protocol status constants (`FSF_PROT_*`) and FSF status constants (`FSF_*`) drive recovery and error classification in `zfcp_fsf.c`.
- Status qualifier constants define recommendations and detailed link/security reasons.
- Status-read constants define unsolicited status payload types and subtypes for port closed, incoming ELS, sense data, bit errors, link down/up, notification lost, feature update, and version changes.
- Feature constants expose adapter capabilities such as notification lost, HBAAPI management, chained CT/ELS SBALs, update alerts, SFP data, FC security, DIF/DIX, and NPIV mode.
- `struct fsf_status_read_buffer` is the unsolicited status buffer with queue designator, D_ID, LUN, and a large payload union for raw data, link-down info, bit errors, and version changes.
- `union fsf_prot_status_qual`, `union fsf_status_qual`, `struct fsf_qtcb_prefix`, `struct fsf_qtcb_header`, and `struct fsf_qtcb` define the QTCB exchanged with hardware.
- `struct fsf_qtcb_bottom_io`, `_support`, `_config`, and `_port` define command-specific bottoms for SCSI I/O, support commands, adapter config, and local port data.
- `struct zfcp_blk_drv_data` stores zfcp blktrace metadata: magic, flags, QDIO usage, channel latency, and fabric latency.
- `struct zfcp_fsf_ct_els` is the software envelope for CT/ELS requests: SG request/response, completion handler/data, optional port, status, and destination id.

## Control Flow And Integration

This header is consumed primarily by `zfcp_fsf.c`, which fills QTCBs according to the command constants and interprets status/qualifier values according to these definitions. QDIO carries QTCB pointers and status-read buffers. FC code fills `zfcp_fsf_ct_els` to send CT/ELS requests. Diagnostics cache `fsf_qtcb_bottom_config` and `fsf_qtcb_bottom_port`. SCSI command setup fills `fsf_qtcb_bottom_io`.

## State And Persistence

The types are wire/data layouts, not active state machines. Runtime state appears when these structures are embedded in allocated QTCBs, status-read data pages, diagnostic caches, and block trace records. Most structs are packed to match adapter firmware layout, so their field offsets are persistent protocol contracts.

## Dependencies

The header depends on Linux scatterlist/PFN helpers and libfc/SCSI FC structures. It uses big-endian encoded fields and 24-bit FC IDs manipulated by libfc helpers in implementation files.

## Risks And Edge Cases

- Packed protocol structures must match firmware exactly. Reordering or changing padding breaks hardware communication.
- Several constants share values or semantics across features, for example measurement/request-SFP feature bits; implementation must interpret them in the correct context.
- FSF status additions require updates in `zfcp_fsf.c` handlers, debug formatting, and test expectations.
- `FSF_STATUS_READ_PAYLOAD_SIZE` drives status-read buffer allocation and debug payload assumptions.
- `FSF_FCP_CMND_SIZE` and `FSF_FCP_RSP_SIZE` are checked against FCP structures in implementation; any upstream FCP struct growth can break build-time assertions.
- Security and link-down qualifier values are used for user-visible logs and recovery choices.

## Test Signals

Validation should include:

- Build-time size/layout assertions for FCP command/response structures and QTCB sizes.
- Hardware or simulator exchange-config/port-data parses into expected adapter and port fields.
- FSF status and qualifier values map to correct recovery/logging paths.
- Packed status-read buffers decode ELS, bit-error, link, and version-change payloads correctly.
- Blktrace data magic/flags/latency fields are stable for block-layer consumers.
