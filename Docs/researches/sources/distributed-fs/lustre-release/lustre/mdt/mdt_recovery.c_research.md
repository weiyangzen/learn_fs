# sources/distributed-fs/lustre-release/lustre/mdt/mdt_recovery.c

## Purpose

`mdt_recovery.c` contains MDT replay/reconstruction helpers. It restores transaction numbers, statuses, version data, disposition data, and lock references from target last-reply data so resent or replayed metadata operations can receive a reply consistent with the originally committed operation. It also has specialized reconstruction for create and setattr replies that need current/fake attributes in the response body.

## Important APIs, Types, and Functions

- `mdt_steal_ack_locks()` transfers saved locks from a matching outstanding reply state to the current resent request.
- `mdt_req_from_lrd()` restores request/reply transno, status, pre-versions, and last-reply opaque data from `struct tg_reply_data`.
- `mdt_reconstruct_generic()` is the common reconstructor for operations whose saved last-reply data is enough.
- `mdt_fake_ma()` creates a minimal `MA_INODE` attribute set with `LA_NLINK` and regular-file mode for objects that disappeared after commit.
- `mdt_reconstruct_create()` restores create replies and repacks object attributes, LMV size, and remote-MDT indications.
- `mdt_reconstruct_setattr()` restores setattr replies and repacks current or fake attributes.
- `reconstructors[REINT_MAX]` maps reint opcodes to reconstruction handlers, including `mdt_reconstruct_open()` implemented in `mdt_open.c`.
- `mdt_reconstruct()` is the dispatcher used by MDT reint replay paths.

## Control Flow

Generic reconstruction calls `mdt_req_from_lrd()`, which copies `lrd_transno` and `lrd_result` into the request, writes pre-operation versions into the reply, clears the transno when the original result was an error, writes reply transno/status, steals any ACK locks from an outstanding reply with the same XID/opcode, and returns `lrd_data` for opcode-specific interpretation.

`mdt_steal_ack_locks()` walks `exp_outstanding_replies` under `exp_lock`, finds a reply state with matching XID, logs opcode mismatch if present, removes it from the export list under the service-part reply lock, copies each saved lock into the new request with `ptlrpc_save_lock()`, clears the old reply state's lock count, and schedules the old difficult reply. If the export is already disconnected, it decrefs stolen locks and clears the new reply state's lock count so disconnected clients do not retain transaction locks.

Create reconstruction first restores last-reply data. If the saved status is success, it finds the child by the requested FID. Lookup failure evicts the client because the server cannot reconstruct a committed create reply. It fetches current attributes, prepares LMV reply buffers for directory LMV creates, fakes attributes if the object was destroyed after commit, handles remote-created objects by returning `OBD_MD_MDS` and `-EREMOTE` or `-EIO` for old clients, packs LMV size flags, and packs attrs into `RMF_MDT_BODY`.

Setattr reconstruction similarly restores last-reply data, finds the target object, evicts the client if lookup fails, fetches current attributes, fakes them on `-ENOENT`, packs them into the reply, and drops the object.

## State and Persistence Behavior

The persistent source for reconstruction is target last-reply data (`tg_reply_data`/`lsd_reply_data`) maintained by the target recovery layer and updated by operation handlers such as `mdt_empty_transno()`. This file consumes that data to rebuild volatile reply fields. It also manipulates outstanding reply state and LDLM lock references so transaction locks survive resends correctly.

It does not change filesystem metadata except indirectly by evicting clients when reconstruction invariants fail. Attribute data packed during reconstruction reflects current object state when possible; if the object was already unlinked after the original commit, the fake attribute response deliberately reports `nlink=0` so clients invalidate cached state.

## Dependencies and Integration Points

This file depends on MDT thread info, request capsules, target last-reply data, PTLRPC reply-state lists and difficult replies, LDLM lock save/decref helpers, MDT object lookup/lifetime, complex attribute fetch, body packing, DNE client compatibility checks, and `mdt_reconstruct_open()` from `mdt_open.c`. The dispatcher is tied to reint opcode values (`REINT_SETATTR`, `REINT_CREATE`, `REINT_OPEN`, etc.).

## Risks and Edge Cases

- `mdt_steal_ack_locks()` uses nested spinlocks over export and service reply state; lock ordering must remain consistent with PTLRPC reply handling.
- Opcode mismatch on a matching XID is logged but does not stop lock stealing. That preserves progress but could mask a serious client/server replay confusion.
- Reconstruction evicts the client when an object lookup for a supposedly committed create/setattr cannot be performed, because returning a fabricated success for an unknown FID would corrupt client recovery.
- Fake attributes are intentionally minimal. Clients must honor `nlink=0` and not treat the object as a fully valid regular file.
- The `reconstructors` table assumes every replayable opcode has a non-NULL handler; adding a new `REINT_*` without updating the table will hit `LASSERT()`.

## Test Signals

Tests should cover generic reconstruction of successful and failed operations, transno clearing on saved errors, version restoration, ACK-lock stealing on resent requests, disconnected export lock decref, create reconstruction for existing child, child deleted after commit, remote-created object with old/new DNE clients, create lookup failure eviction, setattr reconstruction with existing/deleted target, open reconstruction delegation, and table coverage for every replayable reint opcode.
