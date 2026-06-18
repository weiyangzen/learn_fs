# sources/distributed-fs/lustre-release/lustre/mdt/mdt_io.c

## Purpose
This file implements MDT-side data operations for Data-on-MDT (DoM): high-priority BRW/punch request lock checks, prepare/commit of read/write buffers, fallocate, punch/truncate, fiemap, data-version lookup, DoM lock glimpse/LVB handling, read-on-open optimization, and discard of cached client data when objects are destroyed.

## Important APIs, Types, And Functions
Public entry points include `mdt_hp_brw()`, `mdt_hp_punch()`, `mdt_obd_preprw()`, `mdt_obd_commitrw()`, `mdt_fallocate_hdl()`, `mdt_fiemap_get()`, `mdt_punch_hdl()`, `mdt_dom_object_size()`, `mdt_glimpse_enqueue()`, `mdt_brw_enqueue()`, `mdt_dom_client_has_lock()`, `mdt_data_version_get()`, `mdt_dom_read_on_open()`, `mdt_dom_discard_data()`, and `mdt_dom_obj_lvb_update()`. Internal helpers cover lock prolongation, BRW read/write prep, commit transactions, fallocate-zero fallback, FIEMAP sparse-region checks, glimpse AST work, and LVB reply packing.

## Control Flow
High-priority setup attaches `ptlrpc_hpreq_ops` when the request is covered by a client DoM lock and does not require server locking or replay processing. `mdt_obd_preprw()` validates one-object BRW requests, finds the MDT object, stores it in thread info, then maps remote buffers to local niobufs under `mot_dom_sem` for read or write. `mdt_obd_commitrw()` completes read cleanup or write commit; writes map nodemap IDs for reply, process grants/quota, update timestamps only for current FMD XIDs, run a DT transaction, retry for ENOSPC/restart cases, update counters, and refresh DoM LVBs. Fallocate and punch handlers optionally take server data locks, validate object type and resource ids, update attributes in transactions, and update LVB replies. Glimpse paths fill DoM size/block/time in either old MDT-body fields or the newer DLM LVB. Read-on-open grows the open reply with inline data only when a DoM+layout lock was returned and the configured optimization is enabled.

## State And Persistence
Persistent data changes are made through DT transactions against `mdt_bottom` objects. Runtime coordination uses `mdt_object::mot_dom_sem`, LDLM resources/LVBs, grant accounting, FMD XID tracking, lprocfs counters, and object flags such as `mot_discard_done`. Read-on-open copies data into the RPC reply without changing persistence. Discard uses a local PW DOM lock with `LDLM_FL_AST_DISCARD_DATA` to force clients to drop cached pages.

## Dependencies And Integration Points
This file sits between target RPC handling, LDLM, DT object IO, grants/quota, nodemap, request capsules, lprocfs counters, and MDT object lookup. It relies on prototypes and structures from `mdt_internal.h`, lower DT methods such as `dt_bufs_get()`, `dt_write_commit()`, `dt_falloc()`, `dt_fiemap_get()`, and target helpers such as `tgt_mdt_data_lock()` and `tgt_grant_*()`.

## Risks
DoM IO is lock-sensitive. Missing `mot_dom_sem` release, stale object handling, or incorrect high-priority lock matching can cause deadlocks, stale writes, or client eviction noise. Write grant handling must commit/deallocate grants on all error paths. Root-squash/nodemap remapping affects quota bypass flags and returned IDs. Fallocate zero fallback writes chunks using BRW-style commit and must avoid double-freeing buffers. Read-on-open must respect encryption-unit sizing and reply capacity; partial reads are intentionally ignored. Async discard stores object pointers in lock AST data and depends on callback cleanup for references.

## Test Signals
Relevant tests include DoM read/write under lock cancellation, BRW replay exclusion from high-priority handling, grants and overquota flags, root-squash writes, stale/missing object reads and writes during eviction/unlink, fallocate punch/zero/keep-size modes, FIEMAP with sparse DoM regions and server locks, old/new DoM LVB clients, read-on-open for encrypted and unencrypted files, and async discard behavior for old and new clients.
