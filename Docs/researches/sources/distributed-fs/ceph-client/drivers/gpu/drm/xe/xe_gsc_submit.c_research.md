# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gsc_submit.c

## Purpose
Provides generic GSC HECI packet helpers: creating host session IDs, emitting and validating MTL GSC headers, tracking pending replies, and submitting kernel packets to GSC through the GSCCS command streamer.

## Important APIs and Functions
- `xe_gsc_create_host_session_id` returns a random 64-bit host session handle with the top client-ID bits clear.
- `xe_gsc_emit_header` writes `struct intel_gsc_mtl_header`, encoding validity marker, HECI client, optional client-tagged host session handle, version, and total message size.
- `xe_gsc_poison_header` fills a header with `POISON_FREE` to catch stale replies.
- `xe_gsc_check_and_update_pending` copies `gsc_message_handle` from an output header into the input header when GSC marks a reply pending.
- `xe_gsc_read_out_header` validates marker, status, total size, and minimum payload length.
- `xe_gsc_pkt_submit_kernel` emits `GSC_HECI_CMD_PKT` into a batch buffer and waits for the submitted job fence.

## Control Flow
Callers allocate GGTT-visible input/output memory, emit a GSC header plus payload, call `xe_gsc_pkt_submit_kernel`, then validate the output header and parse payload. Pending-message users can reuse the same input header after `xe_gsc_check_and_update_pending` updates the retry handle.

## State and Persistence
The file does not own persistent state. It uses `gsc->q` for submission and relies on caller-owned buffers/maps. Host session IDs are randomized per caller and encoded with the HECI client ID in the top byte only when nonzero.

## Dependencies and Integration Points
Used by GSC firmware version query, GSC proxy, HuC auth via GSC, and any other kernel GSC clients. Depends on Xe batch-buffer/job submission, DRM fences, GSC command ABI, and map helpers.

## Risks and Edge Cases
- `xe_gsc_read_out_header` computes `payload_size = size - GSC_HDR_SIZE` before testing `size < GSC_HDR_SIZE`; unsigned underflow is later rejected by the size check but should remain considered when modifying validation.
- Packet submission requires input and output sizes at least the GSC header size and waits for only `HZ`.
- Header helpers assert host session client bits are initially clear, so callers must not pre-encode client IDs.

## Test Signals
- Unit-style tests can validate header fields, pending handle propagation, and invalid output header rejection.
- Integration tests include HuC auth and proxy transactions that exercise real GSCCS packet submission.
