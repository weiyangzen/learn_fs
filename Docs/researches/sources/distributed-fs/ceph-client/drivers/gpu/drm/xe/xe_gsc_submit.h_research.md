# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gsc_submit.h

## Purpose
Declares reusable GSC packet/header helpers for kernel clients.

## Important APIs
- Header construction and poisoning: `xe_gsc_emit_header`, `xe_gsc_poison_header`.
- Reply processing: `xe_gsc_check_and_update_pending`, `xe_gsc_read_out_header`.
- Packet submission: `xe_gsc_pkt_submit_kernel`.
- Session identity: `xe_gsc_create_host_session_id`.

## Integration and Risks
The API assumes caller-provided GGTT-visible buffers and an initialized `struct xe_gsc` with a valid GSCCS queue. Callers must size payloads consistently with HECI/GSC ABI expectations and validate output before parsing.
