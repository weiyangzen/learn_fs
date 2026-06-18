# sources/distributed-fs/lustre-release/lustre/mdc/mdc_dev.c

## Purpose

`mdc_dev.c` implements the CL/OSC-facing device, object, lock, IO, request-attribute, and device-type operations that let Metadata Client objects also serve Data-on-MDT file data. It reuses OSC infrastructure for pages, cache writeback, direct IO, fiemap, and common object handling, but maps locks and RPC metadata to MDT/FID semantics through LDLM IBITS locks carrying `MDS_INODELOCK_DOM`.

## Important APIs, Types, And Functions

The exported symbols used by other MDC files are `mdc_ldlm_blocking_ast()`, `mdc_ldlm_glimpse_ast()`, `mdc_fill_lvb()`, and the global `struct lu_device_type mdc_device_type`. The file defines CL operation tables: `mdc_lock_ops`, `mdc_lock_lockless_ops`, `mdc_io_ops`, `mdc_ops` (`cl_object_operations`), `mdc_object_ops` (`osc_object_operations`), `mdc_lu_obj_ops`, `mdc_lu_ops`, and `mdc_device_type_ops`.

Lock helpers include `mdc_lock_build_policy()` for DOM IBITS policy, `mdc_lock_build_einfo()` for LDLM enqueue callbacks, `mdc_dom_lock_match()` for local matching plus AST-data attachment and LVB caching, `mdc_dlmlock_at_pgoff()` for finding a whole-object DOM lock, `mdc_enqueue_send()` for synchronous/asynchronous LDLM enqueue, `mdc_enqueue_fini()` and `mdc_enqueue_interpret()` for reply completion, and `mdc_lock_upcall()`/`mdc_lock_granted()` for converting an LDLM result into an OSC lock state.

IO helpers include `mdc_io_setattr_start()` for truncate/fallocate against Data-on-MDT objects, `mdc_io_fsync_start()` for whole-object writeback and sync, `mdc_io_data_version_start()`/`end()` for asynchronous `MDS_GETATTR` data-version retrieval, and `mdc_io_read_ahead_prep()` for readahead under DOM locks. Object lifecycle helpers include `mdc_object_alloc()`, `mdc_object_init()`, `mdc_object_prune()`, `mdc_object_flush()`, and `mdc_object_fiemap()`.

## Control Flow

When a CL lock is initialized, `mdc_lock_init()` allocates an `osc_lock`, maps enqueue flags to LDLM flags, marks glimpse locks, builds LDLM enqueue info, attaches the MDC lock slice, optionally converts to lockless mode, and records reader/writer use based on IO type. `mdc_lock_enqueue()` rejects unsupported lockahead, handles test/glimpse shortcuts, waits for conflicting locks when needed, grants lockless locks locally, then builds a FID resource name and calls `mdc_enqueue_send()`.

`mdc_enqueue_send()` first tries local LDLM matching with `LDLM_FL_LVB_READY`, treating PR requests as PR|PW for sharing. If a valid lock is found and its AST data can be associated with the object, it invokes the upcall immediately. Otherwise it allocates an enqueue request, optionally cancels local DOM locks for write mode, handles old-server glimpse compatibility, requests an LVB, and calls `ldlm_cli_enqueue()`. Synchronous enqueues finish immediately through `mdc_enqueue_fini()`, while async enqueues store `osc_enqueue_args` and complete in `mdc_enqueue_interpret()`.

Blocking AST flow is handled by `mdc_ldlm_blocking_ast()`. A blocking callback sends async cancellation. A canceling callback creates an independent CL environment, calls `mdc_dlm_canceling()`, flushes or discards pages for the whole object, clears `l_ast_data`, and resets KMS to zero. LVB flow maps MDT `mdt_body` DOM size fields into `ost_lvb` with `mdc_fill_lvb()` for older servers, and `mdc_lock_lvb_update()` updates CL attributes and KMS once a lock is granted.

Device allocation creates an `osc_device`, binds the corresponding OBD found by name, and calls `mdc_setup()`. Device fini tears down procfs/PTLRPC/OSC precleanup, changelog cdevs, and llog context; final free asserts no modifying RPCs are in flight, finalizes CL, runs common OSC cleanup, and frees the `osc_device`.

## State And Persistence Behavior

Persistent metadata and Data-on-MDT data are remote; local state consists of LDLM locks, cached pages, OSC object attributes, LVB/KMS, and OBD/CL device structures. DOM locks are whole-object from the page-cache perspective. Losing a lock flushes dirty data for write mode, discards or selectively keeps clean pages depending on overlapping locks, clears AST data, and resets KMS so future reads refetch authoritative state. For truncate/fallocate, `mdc_io_setattr_start()` updates cached attributes when not lockless and sends an OSC-style punch/fallocate RPC using MDT object FID and a lock handle or server-lock flag.

## Dependencies And Integration Points

This file heavily depends on OSC CL infrastructure (`osc_lock`, `osc_object`, `osc_io`, page-gang lookup, cache writeback, punch/fallocate/fsync helpers), LDLM namespace and lock matching, PTLRPC request capsules, MDT/MDS opcodes, and CL environment APIs. It is the device-type implementation registered by `mdc_request.c` through `class_register_type(..., LUSTRE_MDC_NAME, &mdc_device_type)`. It also calls `mdc_setup()`, `mdc_changelog_cdev_finish()`, and `mdc_llog_finish()` for OBD-level lifecycle integration.

## Risks

The highest-risk areas are lock/cache coherence and lifecycle races. DOM locks use `l_ast_data` without owning object references in the DLM lock, so `mdc_object_prune()` must clear AST data before object destruction. Canceling locks may run during nested IO and therefore must use a fresh environment. Matched-lock paths must avoid associating one LDLM lock with the wrong OSC object; failed association drops the match. Data-version and setattr paths are asynchronous and rely on completion state in `osc_io`. Server-version compatibility for DOM LVBs and glimpse intents is another important compatibility risk.

## Test Signals

Coverage should include DOM read/write/truncate/fallocate/fsync/data-version/fiemap paths, lockless and locked IO, local lock match versus remote enqueue, glimpse on old and new servers, cancellation with dirty pages, object prune during active locks, KMS updates from LVB, and reconnect/teardown. Fault-injection hooks referenced in the file (`OBD_FAIL_MDC_GLIMPSE_DDOS`, `OBD_FAIL_LDLM_ENQUEUE_HANG`, `OBD_FAIL_OSC_CP_ENQ_RACE`, `OBD_FAIL_OSC_CP_CANCEL_RACE`) are direct test signals for race and error handling.
