# sources/distributed-fs/coda/coda-src/venus/vol_repair.cc

## Purpose

`vol_repair.cc` implements Venus repair of inconsistent replicated objects. It supports connected server/server repair through `ViceRepair`, local/global repair cleanup against the CML, disconnected file repair by creating a local repaired object and logging a `CML_Repair_OP`, and ASR permission/running-state controls.

The code bridges user-supplied repair files, cached fake conflict objects, server replica state, and CML mutation pruning. It is both a user-visible repair path and a reintegration conflict recovery component.

## Important APIs, Types, and Functions

`repvol::Repair` is the public dispatcher. It rejects unreachable or resolving volumes, then currently always calls `ConnectedRepair` for non-ASR-issued repair requests.

`GetRepairF` is a helper that recognizes repair file strings of the form `@volume.vnode.unique@realm`, resolves them to cached `fsobj` file data, and returns either a file object or no special handling for ordinary filesystem paths.

`repvol::ConnectedRepair` verifies the target is fake or marked to be repaired, flushes COP2, builds a `ViceStatus` from a repair `fsobj` or path, parses directory fixfiles through `repair_getdfile`, calls `ViceRepair` with multi-RPC, collates results, prunes local CML entries for local directory repairs, sends COP2, purges fake objects, and submits async resolve for repaired directories.

`repvol::DisconnectedRepair` supports disconnected file repair only. It verifies conflict state and parent write access, builds a template version vector from replicas, creates a local repaired `fsobj`, logs a repair CML entry, and calls `LocalRepair` to install file contents in the cache.

`repvol::LocalRepair` fills an `fsobj` from a `ViceStatus`, matriculates it, attaches parent fid state, creates a cache container file, copies repair contents, validates length, and marks the object dirty.

ASR control methods are `reintvol::EnableASR`, `DisableASR`, `AllowASR`, `DisallowASR`, `lock_asr`, `unlock_asr`, and `asr_pgid`.

## Control Flow

Connected repair starts by returning per-replica volume ids in `RWVols`, fetching the target status, and accepting only inconsistent fake objects or local/global to-be-repaired objects. It flushes COP2 because `ViceRepair` does not piggyback COP2. It optionally resolves the repair file to a cache object, generates a store id, acquires an mgroup, and computes a template version vector from the accessible replica objects.

The repair status is built from either cached repair data or `stat(2)` on the repair file. The code opens the repair data, creates a SMARTFTP descriptor, and, for directory repairs, parses the fixfile. When the fixfile includes the local replica, it precomputes fids and link counts for entries that may need corresponding CML pruning.

The server operation is a multi-RPC `ViceRepair`. `Collate_COP1` computes the update set and repair-level return code. The code then maps individual server return codes back to the `RWVols` order. On success or synchronous resolve, it may prune local CML mutations by replaying repair commands into `LogRemove`, `LogRmdir`, `LogChmod`, `LogChown`, `LogUtimes`, or `LogRename` with `cancelFreezes(1)` so frozen CML entries can be thawed and cancelled when safe.

For local/global file repair, successful connected repair discards local mutation state and clears all `to_be_repaired` flags. For all successful connected repairs, the code sends a final COP2, releases resources, purges the fake conflict object if this was not a local fake, and submits a resolve for directories.

Disconnected repair rejects directories, verifies the target is inconsistent, checks parent write access, builds a repair status, kills the fake conflict object if possible, creates a real FSDB object at the repaired fid, logs `LogRepair` with prepend, and copies repair data into the local container. The eventual reintegration of that CML repair entry causes the server-side `ViceRepair` and clears inconsistency remotely.

## State and Persistence Behavior

Connected repair mostly changes server state and cache state. It generates a persistent store id for COP2 finalization, may append or cancel CML entries inside recovery transactions, clears fake object flags before killing conflict placeholders, and can clear CML repair flags.

Disconnected repair persists a local dirty object and a repair CML record. `LocalRepair` mutates durable `fsobj` fields and creates cache container data inside an RVM transaction controlled by the caller.

ASR flags are transient volume flags. `allow_asrinvocation` is user permission, `enable_asrinvocation` is volume-service gating, `asr_running` serializes ASR execution, and `pgid` records the process group allowed to keep operating while ASR is active.

## Dependencies and Integration Points

The file depends on RPC2, Vice interfaces, `inconsist.h`, `copyfile.h`, `prs.h`, `repio.h`, `FSDB`, `fsobj`, `mgrp`, `mariner`, `worker`, `realmdb`, and volume/CML APIs.

It integrates with `vol_cml.cc` by logging repair entries, pruning CML operations, and clearing repair flags; with `vol_reintegrate.cc` through ASR gating and local/global conflict recovery; with `vol_resolve.cc` by submitting resolves after directory repair; and with COP2 and multi-RPC collation in the replicated volume layer.

## Risks and Edge Cases

Connected repair assumes the target object remains meaningful after the initial status get. Fake object purging and local CML pruning must be ordered carefully so users do not see stale conflict state.

Directory fixfile pruning is complex. It depends on parsing the local replica section, looking up names before the server call, preserving link counts, and then converting repair commands into CML operations. Lookup failures or unexpected opcodes can leave server repair successful but local CML cleanup incomplete.

`ConnectedRepair` currently always selected by `Repair` means disconnected repair is unreachable through that dispatcher unless the placeholder predicate is changed.

`LocalRepair` uses assertions around file opens and copy operations. In production builds or unusual environments, bad repair paths or container-file failures can become hard failures rather than graceful error propagation.

ASR flags are simple bit fields without internal locking in this file. Correctness depends on volume entry discipline and the broader Venus single-process LWP model.

## Test Signals

Useful tests include repair of a fake file and fake directory, repair-file-by-fid parsing, ordinary path repair with file, directory, and symlink status, COP2 flush failure, per-replica return-code collation, directory fixfile pruning for remove/rmdir/chmod/chown/utimes/rename, local/global file repair clearing repair flags, disconnected file repair and later reintegration, access denial through parent rights, and ASR allow/enable/running state transitions.

Runtime signals include `MarinerLog("store::Repair")`, `ViceRepair` multi-RPC stats, per-replica `ReturnCodes`, fake-object purge logs, CML pruning logs, and `DisconnectedRepair` length-mismatch or access messages.
