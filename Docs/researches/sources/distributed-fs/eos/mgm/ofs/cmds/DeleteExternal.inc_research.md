# Research: sources/distributed-fs/eos/mgm/ofs/cmds/DeleteExternal.inc

## Purpose

`DeleteExternal.inc` sends an authenticated drop request from the MGM to an FST so the data server deletes a physical replica or stripe. It builds a short-lived capability containing delete access, manager id, fsid, and fid, then sends an HTTP-style query to the FST.

## Important APIs, Types, and Functions

- `XrdMgmOfs::DeleteExternal(fsid, fid, is_fsck)` is the only function.
- It looks up the filesystem in `FsView::gFsView.mIdView` under `ViewMutex`.
- It constructs capability parameters `mgm.access=delete`, `mgm.manager`, `mgm.fsid`, and `mgm.fids`.
- `SymKey::CreateCapability()` encrypts/signs capability data using the current key and `mCapabilityValidity`.
- `SendQuery(fst_host, fst_port, qreq, qresp)` sends `/?fst.pcmd=drop` plus optional `fst.drop.type=fsck`.

## Control Flow

The function reads the filesystem object, extracts queue, host, and port, and returns false if the fsid is unknown. It builds an `XrdOucEnv`, creates an output capability environment, appends it to the drop query, sends the query to the FST, logs send failure, deletes the allocated capability env, and returns success/failure.

## State and Persistence Behavior

This file does not update namespace metadata. It causes external state mutation on an FST when the query is accepted. It reads filesystem registry state and current symmetric key material.

## Dependencies and Integration Points

Dependencies include `FsView`, filesystem locator/core params, `FileId::Fid2Hex`, `SymKey` capability creation, key store, `SendQuery`, and MGM manager identity. It is used by `DropReplica()` and likely other replica-removal paths.

## Risks and Edge Cases

- Capability generation failure prevents physical deletion.
- Unknown fsid returns false without namespace cleanup.
- `SendQuery` return convention is inverted in this code path: nonzero indicates failure.
- FST-side acceptance is not strongly confirmed beyond query send result.
- Capability validity and key rotation affect whether FSTs accept the deletion.

## Test Signals

Tests should cover valid and missing fsid, generated query parameters, fsck drop type, capability creation failure, send failure, port extraction, key-store behavior, and integration with `DropReplica()` when FST deletion fails but namespace drop proceeds.
