# sources/distributed-fs/glusterfs/rpc/xdr/src/glusterfs3.h

## Purpose

`sources/distributed-fs/glusterfs/rpc/xdr/src/glusterfs3.h` provides inline conversion helpers between GlusterFS in-memory structures and generated Gluster protocol/XDR structures. It covers open flag translation, `statvfs`, leases, flock, iatt/stat layouts, upcall payloads, metadata timestamps, and typed dict-to-XDR conversion. The source was read as a complete 963-line file for this report.

## Important APIs, Types, and Functions

Important helpers include `gf_flags_from_flags`, `gf_flags_to_flags`, `gf_statfs_to_statfs`, `gf_statfs_from_statfs`, `gf_proto_lease_to_lease`, `gf_proto_lease_from_lease`, `gf_proto_flock_to_flock`, `gf_proto_flock_from_flock`, `gf_stat_to_iatt`, `gf_stat_from_iatt`, `gfx_stat_to_iattx`, `gfx_stat_from_iattx`, `gfx_mdata_iatt_to_mdata_iatt`, `gfx_mdata_iatt_from_mdata_iatt`, `dict_to_xdr`, and `xdr_to_dict`.

Upcall conversion helpers include recall lease, cache invalidation, inode lock contention, and entry lock contention conversions. Flag macros (`GF_O_*`, `XLATE_BIT`, `UNXLATE_BIT`, access-mode macros) define wire-stable open flags independent of host OS values.

## Control Flow

Most helpers are straight field-copy conversions with early null checks. Dict serialization locks the source dict, allocates an array of `gfx_dict_pair`, iterates `members_list`, maps each known `GF_DATA_TYPE_*` to its XDR union field, computes the XDR variable-size payload using `xdr_sizeof`, then unlocks. Dict deserialization allocates a new dict, iterates received pairs, allocates owned values for strings/UUID/iatt/mdata/opaque pointer-like values, inserts them into the dict, frees rpcgen-allocated key/value buffers, and hands ownership of the completed dict to the caller.

## State and Persistence Behavior

The header owns no global storage. It creates transient heap allocations while converting dictionaries and may transfer ownership to `dict_t` via `dict_set_dynstr`, `dict_set_dynptr`, `dict_set_gfuuid`, `dict_set_iatt`, and `dict_set_mdata`. Upcall conversions may serialize or unserialize embedded xdata dictionaries through Gluster protocol macros. Wire encodings persist only in RPC buffers.

## Dependencies and Integration Points

It depends on `xdr-generic.h`, `xdr-custom.h`, generated `glusterfs4-xdr.h`, `glusterfs/iatt.h`, `protocol-common.h`, and `upcall-utils.h`. It is consumed by RPC clients/servers and translators that need to convert between local VFS-style structures and GlusterFS wire protocol objects.

## Risks and Edge Cases

This file is protocol-boundary code. Field order, missing flag translations, host-specific open flags, lock-owner length limits, empty-string-to-NULL normalization, and dict ownership rules are all high risk. `dict_to_xdr` skips unknown types and warns for pointer/old-string compatibility; callers must tolerate omitted keys. `xdr_to_dict` manually frees rpcgen-allocated buffers, so mismatched XDR allocation behavior or failed insertions can leak or double-free. Inline functions in a widely included header increase rebuild blast radius and can hide ABI drift until integration tests fail.

## Test Signals

Round-trip tests for flags, `iatt`, `statvfs`, flock, lease, upcall payloads, and typed dict entries are useful. Tests should include null dicts, empty dicts, unknown dict types, UUID/iatt/mdata entries, lock owners at boundary lengths, cache invalidation with invalid GFID strings, and compatibility between generated `glusterfs4-xdr` structures and local structs.
