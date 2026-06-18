# sources/distributed-fs/ceph-client/net/sctp/stream.c

## Purpose
Implements SCTP stream allocation, stream extension lifecycle, stream reset/reconfiguration request send paths, and inbound RE-CONFIG parameter processing. It owns the association stream counters, per-stream sequence reset state, and the mechanics that move queued chunks when stream counts shrink or grow.

## Important APIs, Types, And Functions
Exports `sctp_stream_init`, `sctp_stream_init_ext`, `sctp_stream_free`, `sctp_stream_clear`, `sctp_stream_update`, `sctp_send_reset_streams`, `sctp_send_reset_assoc`, `sctp_send_add_streams`, and the `sctp_process_strreset_*` handlers. Key state lives in `struct sctp_stream`, `struct sctp_association`, `struct sctp_stream_out_ext`, and RE-CONFIG parameter structs such as `sctp_strreset_outreq`, `sctp_strreset_inreq`, `sctp_strreset_tsnreq`, and `sctp_strreset_addstrm`.

## Control Flow
Initialization preallocates genradix-backed incoming/outgoing stream arrays, sets outgoing stream state to open, and selects the interleave operations table. Shrink/update paths first unschedule all scheduler queues, fail queued chunks for removed outgoing stream ids, migrate extensions, and reschedule survivors. Local reset/add requests validate peer capabilities, outstanding reset state, stream bounds, and chunk-size limits before creating RE-CONFIG chunks and closing affected outgoing streams until responses arrive. Inbound reset handlers enforce request sequence windows, replay cached results for duplicate requests, update stream mids/ssns or TSN maps, create ULP notifications, and return response chunks. Response handling looks up the original request in `asoc->strreset_chunk`, applies success/failure side effects, reopens streams, emits notifications, and drops the reconf timer/reference when all outstanding parameters complete.

## State And Persistence
All state is in-memory per association: stream counts, genradix arrays, per-stream `mid`/`mid_uo`, incoming `mid`, stream open/closed state, `strreset_inseq`, `strreset_outseq`, `strreset_outstanding`, cached `strreset_result[]`, and held `strreset_chunk`. No durable persistence exists. Correctness depends on holding chunk/transport references while timers are active.

## Dependencies And Integration Points
Integrates with SCTP schedulers (`stream_sched.h`), output queue chunk lists, RE-CONFIG chunk builders, state-machine primitive `sctp_primitive_RECONF`, TSN map helpers, ULP event factories, reconf timers on transports, and PR-SCTP accounting.

## Risks
High-risk areas are off-by-one stream bounds, failing to restore stream state after send failure, mismatched `strreset_outstanding` accounting for combined requests, timer/reference leaks around `strreset_chunk`, and shrinking outgoing streams while chunks or scheduler extension state still exist.

## Test Signals
Exercise full and per-stream outgoing/incoming reset, duplicate/out-of-window RE-CONFIG requests, reset while outqueue is non-empty, association TSN reset, add-stream success/failure rollback, scheduler switching around stream count changes, and notification flags for denied/failed/performed responses.
