# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_log_ring.h

Purpose: this header defines the in-memory RAS log-ring data model and public operations.

Important types and macros: `MAX_RECORD_PER_BATCH` caps per-batch entries at 32. `RAS_LOG_SEQNO_TO_BATCH_IDX()` extracts the batch from a sequence number. `enum ras_log_event` distinguishes UE, DE, CE, poison creation/consumption, RMA, and sentinel values. `struct ras_aca_reg` wraps ACA register dumps. `struct ras_log_info` records sequence, timestamp, event, and register payload. `struct ras_log_batch_tag` carries batch ID, timestamp, and sub-sequence while producers add related events. `struct ras_log_ring` stores mempool, radix root, spinlock, counters, and deletion cursor.

Control flow and state: the header declares init/fini, batch-tag create/destroy, log append, batch record retrieval, and overview APIs. No persistent storage is involved; the ring is volatile kernel memory.

Dependencies and integration: it includes `ras_aca.h` for register counts and indices. CPER serialization depends on this header's event and register layout. Risks include callers retaining pointers after ring cleanup/deletion, event enum drift against CPER mapping, and unclear ownership of batch tags. Test signals should verify all events map to expected CPER behavior, batch tag lifetime is respected, and overview counts remain sensible after cleanup and wrap-like deletion.
