# Research: sources/distributed-fs/eos/mgm/ofs/cmds/DropReplica.inc

## Purpose

`DropReplica.inc` coordinates replica removal from an FST and from the EOS namespace. It is a small helper used when a specific file id and filesystem id must be dropped, such as fsck-driven cleanup.

## Important APIs, Types, and Functions

- `XrdMgmOfs::DropReplica(fid, fsid) const` is the only function.
- It treats `fsid == 0` as a no-op success.
- It calls `gOFS->DeleteExternal(fsid, fid, true)` to request physical deletion.
- It calls `gOFS->_dropstripe("", fid, err, Root(), fsid, true)` to remove the replica from namespace metadata.

## Control Flow

The function logs the target file/fsid, sends the FST unlink/drop request, records a false return if that send fails, then uses root virtual identity to drop the stripe from the namespace by file id. Namespace drop errors are logged but do not currently flip the returned boolean; the return value primarily reflects FST message success.

## State and Persistence Behavior

The helper can trigger both external FST deletion and namespace metadata mutation through `_dropstripe`. It does not itself lock or persist state; it delegates both state-changing operations.

## Dependencies and Integration Points

Dependencies include `DeleteExternal`, `_dropstripe`, `VirtualIdentity::Root`, and XRootD error objects. It integrates fsck/repair-like flows with data-server cleanup and namespace replica accounting.

## Risks and Edge Cases

- Return value does not reflect namespace drop failure, only FST deletion failure.
- If FST deletion succeeds and namespace drop fails, data and namespace can remain inconsistent.
- If FST deletion fails and namespace drop succeeds, metadata may forget a replica that still exists physically.
- Empty path plus root identity assumes `_dropstripe` can authorize by fid only.

## Test Signals

Tests should cover fsid zero no-op, FST deletion failure, namespace drop failure, combined success, root identity use, and consistency checks after partial failure.
