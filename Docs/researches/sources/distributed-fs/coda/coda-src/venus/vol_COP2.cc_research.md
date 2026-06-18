# Research: sources/distributed-fs/coda/coda-src/venus/vol_COP2.cc

## Purpose

`vol_COP2.cc` implements the Venus COP2 facility for replicated volumes. After a mutating COP1 operation produces a `ViceStoreId` and `ViceVersionVector` update set, this code distributes that update set to the AVSG. It supports immediate synchronous COP2 RPCs, deferred asynchronous RPCs from the volume daemon, and piggybacked COP2 data on later worker RPCs. Update propagation is intentionally idempotent, and multiple pending update sets can be batched into one `RPC2_CountedBS` buffer.

## Important APIs, Types, and Functions

- `COP2EntrySize` is the serialized size of one `ViceStoreId` plus one `ViceVersionVector`.
- `repvol::COP2(mgrpent *, RPC2_CountedBS *)` sends an already packed buffer to all VSG members through `MRPC_MakeMulti(ViceCOP2_OP)` and clears matching queued entries on success.
- `repvol::COP2(mgrpent *, ViceStoreId *, ViceVersionVector *, int donotpiggy)` either queues the entry for piggybacking or packs and sends a one-entry buffer immediately.
- `repvol::FlushCOP2(time_t window)` is the volume-daemon/direct-flush path. It sends oldest entries when they are old enough, filling buffers with younger entries as capacity allows.
- `repvol::FlushCOP2(mgrpent *, RPC2_CountedBS *)` is the piggyback preparation path. It directly sends all but the final buffer-full and copies the remaining entries into the caller's piggyback buffer.
- `repvol::GetCOP2()` serializes pending entries in FIFO order without removing them.
- `repvol::FindCOP2()` locates a queued entry by store id.
- `repvol::AddCOP2()` appends a new queue entry.
- `repvol::ClearCOP2(RPC2_CountedBS *)` parses a sent buffer, removes matching queued entries, deletes them, and resets the buffer length.
- `repvol::ClearCOP2()` drains the whole queue.
- `cop2ent` stores one pending `sid`, `updateset`, and enqueue time and has a small free-list-backed allocator.

## Control Flow

When a mutating replicated operation finishes COP1, callers invoke the single-entry `COP2` overload. If piggybacking is enabled and the caller did not force direct sending, `AddCOP2()` appends a `cop2ent` and returns success. Otherwise the method serializes the store id with `htonsid`, serializes the update vector with `htonvv`, and delegates to the buffer-sending `COP2` overload.

The buffer-sending `COP2` overload assumes a replicated volume and an existing `mgrpent`. It performs `MRPC_MakeMulti` with `ViceCOP2_OP`, collates via `Collate_COP2`, records multi-RPC stats, and calls `ClearCOP2(PiggyBS)` only when the multi-RPC succeeded. This means failed sends leave queue entries intact for future retry.

Daemon flushing starts at the head of `cop2_list`, which is maintained FIFO. If the list is empty or the oldest entry is younger than `window`, the flush returns. Otherwise it obtains an mgroup as `V_UID`, calls `GetCOP2()` to fill a local buffer up to `COP2SIZE`, sends it with `COP2`, releases the mgroup, and repeats from the list head until no eligible entries remain or a send/acquire error occurs. The code explicitly tolerates concurrent flushing: entries may disappear while `GetMgrp()` yields, so a zero-length buffer after mgroup acquisition is logged and stops the loop.

Piggyback flushing is used when a caller already has an mgroup for a normal VSG RPC. While the queued data exceeds one COP2 buffer, it sends full buffers directly. If the remaining queue fits in one buffer, it serializes those entries into the caller's `PiggyBS` so the caller can attach them to the normal RPC. The entries are not removed until the caller later calls `ClearCOP2()` after the piggybacked RPC succeeds.

## State and Persistence Behavior

`cop2_list` itself is a transient `dlist` owned by `repvol` and initialized in `repvol::ResetTransient()`. `cop2ent` objects are heap allocated, not RVM recovered. Pending COP2 updates therefore represent runtime delivery work rather than durable state in this file; durable mutation/reintegration state lives in the CML and is what can regenerate or require update propagation after recovery. Each entry records enqueue time through `Vtime()` for daemon window decisions.

`GetCOP2()` is non-destructive and network-byte-order serializing. `ClearCOP2()` is destructive only for entries whose store ids appear in the supplied buffer. This split is what makes direct-send retry and piggyback retry safe: the queue is cleared only after a successful RPC path calls back into clear logic. `ClearCOP2(void)` is used when a replicated volume is being destroyed and any remaining transient queue entries must be dropped.

The allocator keeps up to `MaxFreeCOP2ents` deleted entries on a process-local free list. Allocation zeroes memory only when obtaining fresh storage from `new char[len]`; reused entries are overwritten by the constructor fields that matter.

## Dependencies and Integration Points

The implementation depends on RPC2, Vice `ViceCOP2`, `mgrpent` multi-RPC connection state, `repvol::Collate_COP2()` from `venusvol.cc`, mariner/RPC statistics logging, `PIGGYCOP2`/COP mode globals from communication configuration, byte-order helpers from `nettohost.h`, and the `cop2ent`/`repvol` declarations in `venusvol.h`. Callers include connected CFS mutation paths, volume-status mutation, CML reintegration commit paths, repair code that forces non-piggybacked COP2, replicated fid allocation that best-effort flushes first, resolution/repair paths that require a clean COP2 queue, and `vol_daemon.cc` periodic flushing.

## Risks and Edge Cases

- The COP2 queue is transient. If callers assume queue persistence across process restart, update propagation can be lost unless higher-level CML/reintegration recovery recreates the need.
- `FlushCOP2(time_t window)` compares the oldest entry age and stops if it is younger than the window, so younger entries behind it are never sent alone. This preserves FIFO behavior but delays newer updates.
- `GetCOP2()` serializes from the list head each time without marking entries in flight. Concurrent flushers can send overlapping buffers, which is acceptable only because COP2 propagation is idempotent.
- `ClearCOP2()` silently ignores store ids that are no longer present. That matches concurrent/idempotent semantics but can hide unexpected duplicate or stale buffer contents.
- Buffer-size correctness depends on every packed buffer length being a multiple of `COP2EntrySize`; malformed buffers trigger `CHOKE`.
- The free-list allocator is not visibly locked in this file. It assumes Venus's scheduling/concurrency model is sufficient or that calls are serialized at a higher level.
- The debug print for `cop2ent` does not print the version vector contents even though logging in `GetCOP2()` does, limiting postmortem visibility from object dumps.

## Test Signals

Useful tests should exercise immediate COP2, piggyback queueing, daemon flushing with zero and nonzero windows, piggyback flushing when the queue is larger than `COP2SIZE`, successful clear after direct and piggybacked sends, failed sends leaving entries queued, malformed buffer length handling, duplicate/concurrent clear behavior, `FindCOP2` matching on both store-id fields, FIFO serialization order, free-list reuse bounds, and integration with callers that invoke `ClearCOP2(&PiggyBS)` after successful normal VSG RPCs. Runtime signals include `MULTI_RECORD_STATS(ViceCOP2_OP)`, mariner `store::COP2` logs, `LOG` lines for flush/no-entry cases, and fatal `CHOKE` paths for internal contract violations.
