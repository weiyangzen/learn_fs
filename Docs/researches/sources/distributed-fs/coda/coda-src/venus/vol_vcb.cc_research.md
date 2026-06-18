# sources/distributed-fs/coda/coda-src/venus/vol_vcb.cc

## Purpose

`vol_vcb.cc` implements volume callback (VCB) management. VCBs let Venus validate or invalidate cached state at volume granularity using server-maintained version stamps. The file handles callback breaks, fetching initial volume version stamps, piggyback validation of multiple volumes, collation of callback status from replicated servers, cached-object validation before acquiring a volume stamp, and the simple policy for deciding when a callback is worth requesting.

## Important APIs, Types, and Functions

Global state includes `vcbbreaks`, a count of broken volume callbacks, and `VCBEnabled`, the default policy toggle.

`vdb::CallBackBreak` maps a kernel/server callback-break `Volid` to a volume and invokes `reintvol::CallBackBreak`.

`reintvol::GetVolAttr` is the main validation/fetch routine. If `VVV` is null, it validates cached FSOs, calls `ViceGetVolVS`, and records returned version stamps and callback status. If `VVV` is present, it batches validation of volumes on the same VSG or host through `ViceValidateVols`.

`reintvol::UpdateVCBInfo` handles the single-server/non-replicated callback result path.

`repvol::CollateVCB` handles replicated callback collation, requiring every participating server to return `CallBackSet` before preserving the callback.

`reintvol::ValidateFSOs` walks cached fsobjs in the volume and refetches status/data for invalid objects before a volume stamp is fetched.

`reintvol::PackVS` serializes version stamps into an RPC counted byte string.

`reintvol::CallBackBreak`, `ClearCallBack`, `SetCallBack`, and `WantCallBack` maintain callback state and policy.

## Control Flow

A callback break enters through `vdb::CallBackBreak`. The volume is looked up, `CallBackBreak` clears `VCBStatus` and persistent `VVV` if a callback was set, and the global break count increments only when a callback was actually broken.

`GetVolAttr` first gets a connection and, for replicated volumes, an mgroup. It records the current `cbbreaks` count so it can avoid installing callback state if a concurrent callback break occurred during the RPC.

When the local volume version vector is null, `GetVolAttr` calls `ValidateFSOs` first. This ensures any cached file state is valid before Venus asks servers for a volume-level version stamp that will summarize that state. It then calls `ViceGetVolVS`, collates the non-mutating result, and updates VCB info if no callback break raced.

When the version vector is non-null, `GetVolAttr` builds a batch of up to `MAX_PIGGY_VALIDATIONS` eligible volumes: reachable, wanting a callback, non-null VVV, and on the same VSG for replicated volumes or same host for non-replicated volumes. It serializes all version stamps, calls `ViceValidateVols`, collates results, and then applies per-volume flags. Valid callback results set callbacks and promote directory access rights for `ANYUSER_UID` and the current uid. Valid no-callback results clear callbacks. Invalid results clear callbacks and reset `VVV`.

`ValidateFSOs` iterates the volume's `fso_list`, skips dying or already-valid objects, holds the next object while calling `FSDB->Get` on the current one, and purges kernel state on `EINCONS`.

## State and Persistence Behavior

`VCBStatus`, `VCBHits`, and some policy counters are transient, while `VVV` is a persistent volume version vector. Updates to `VVV` are wrapped in RVMLIB transactions.

A valid callback means Venus can trust `VVV` until a callback break. A callback break clears both the transient callback status and the persistent version vector so later accesses must validate or refetch.

`GetVolAttr` installs callback state only if `cbbreaks` has not changed since the RPC started. This avoids accepting stale callback promises after a concurrent break.

## Dependencies and Integration Points

This file depends on RPC2, Vice callback/status types, `comm`, `fso`, `mariner`, `mgrp`, `venuscb`, `venusvol`, `vproc`, and `worker`.

It integrates with server RPCs `ViceGetVolVS` and `ViceValidateVols`, cache validation through `FSDB->Get`, kernel purge through `k_Purge`, access-right promotion on directories, COP1/reintegration paths that call `CollateVCB` or `UpdateVCBInfo`, and callback-break downcalls through `vdb::CallBackBreak`.

## Risks and Edge Cases

The batching path serializes version stamps into a raw byte string. It depends on matching server expectations for stamp count and endian conversion. Replicated and non-replicated paths use different stamp counts and host arrays.

`ValidateFSOs` mutates and may remove objects while iterating `fso_list`, so it holds the next object before the fetch. This pattern must be preserved.

Callback collation is intentionally conservative. Any participating replicated server returning no callback clears the volume callback, and any zero stamp resets `VVV`.

`WantCallBack` uses a simple threshold: more than one cached fsobj and no current callback. That policy may be suboptimal for workloads with frequent mutations or partitions, but it is easy to reason about.

## Test Signals

Useful tests include callback break with and without an active callback, initial `ViceGetVolVS` fetch after validating stale FSOs, piggyback validation across same-VSG replicated volumes, same-host non-replicated volumes, callback-break race during RPC, mixed server callback statuses, invalid zero stamps, `ValidateFSOs` handling status-only and data invalidation, and `WantCallBack` threshold behavior.

Runtime signals include `vcbbreaks`, VVV debug prints, `MarinerLog("store::GetVolVS")`, `MarinerLog("store::ValidateVols")`, callback status logs, access-right promotion effects, and kernel purges on `EINCONS`.
