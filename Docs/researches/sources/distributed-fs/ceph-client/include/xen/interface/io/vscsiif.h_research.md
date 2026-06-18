# sources/distributed-fs/ceph-client/include/xen/interface/io/vscsiif.h

## Purpose
`vscsiif.h` defines the Xen paravirtual SCSI frontend/backend wire ABI: Xenstore negotiation nodes, SCSI request and response ring payloads, scatter/gather grant descriptors, action codes, and result decoding macros.

## Important APIs, Types, and Functions
The header exports `struct scsiif_request_segment`, `struct vscsiif_request`, `struct vscsiif_response`, constants such as `VSCSIIF_ACT_SCSI_CDB`, `VSCSIIF_ACT_SCSI_ABORT`, `VSCSIIF_ACT_SCSI_RESET`, `VSCSIIF_SG_TABLESIZE`, `VSCSIIF_SG_GRANT`, `VSCSIIF_MAX_COMMAND_SIZE`, and `VSCSIIF_SENSE_BUFFERSIZE`, plus `XEN_VSCSIIF_RSLT_*` macros for SCSI and host status extraction. `DEFINE_RING_TYPES(vscsiif, ...)` creates the shared ring type.

## Control Flow
The frontend publishes `event-channel`, `ring-ref`, and optional protocol data in Xenstore, then sends CDB, abort, or reset requests through the ring. The backend maps grant references, performs the SCSI operation, and posts a response with echoed `rqid`, sense data, result, and residual length. Large I/O can use direct `seg[]` entries or indirect grant pages when `feature-sg-grant` is negotiated.

## State and Persistence Behavior
Persistent coordination state is in Xenstore nodes for vhost/device lifecycle and per-device states. Runtime state is the shared ring page, event channel, grant references, and request IDs; no file-backed persistence is owned by this header.

## Dependencies and Integration Points
It depends on Xen ring and grant-table definitions. It integrates guest SCSI frontend drivers, backend storage drivers, Xenstore tooling/libxl, event channels, grant-table mapping, and Linux SCSI mid-layer result conventions.

## Risks and Test Signals
Risks include ABI size drift, incorrect `nr_segments`/`VSCSIIF_SG_GRANT` interpretation, untrusted grant offsets and lengths, stale Xenstore reconfiguration states, and mismatched SCSI result encoding. Test signals include frontend/backend ring ABI compile checks, direct and indirect SG I/O, hot-add/hot-remove Xenstore state transitions, abort/reset handling, and sense/residual propagation.
