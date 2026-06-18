# sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs3-fh.c

## Purpose

`nfs3-fh.c` constructs, validates, logs, and formats Gluster NFSv3 file handles. File handles encode a Gluster identity marker, export identity, object GFID, and mount identity into the fixed-size NFSv3 handle layout.

## Important APIs, types, and functions

- `nfs3_fh_validate()` checks the `:OGL` identifier bytes.
- `nfs3_fh_init()` initializes the identifier and copies an `iatt` GFID into the handle.
- `nfs3_fh_build_indexed_root_fh()` builds a root handle whose export ID is the child xlator index.
- `nfs3_fh_build_uuid_root_fh()` builds a root handle using volume UUID and mount UUID for dynamic volumes.
- `nfs3_fh_is_root_fh()` compares the handle GFID with Gluster's root GFID.
- `nfs3_fh_build_child_fh()`, `nfs3_fh_build_parent_fh()`, and `nfs3_build_fh()` derive handles from parent/child state or an inode.
- `nfs3_fh_to_str()` and `nfs3_log_fh()` support diagnostics.
- `nfs3_fh_compute_size()` returns the static XDR size used by response helpers.

## Control flow

Handle builders initialize an empty struct, install the magic identifier, copy the object GFID, then copy either export index/UUID and mount ID from the parent or caller-provided arguments. Validation is intentionally shallow: it rejects non-Gluster handles by magic bytes, while volume mapping and stale detection happen later in NFSv3 resolve logic.

## State and persistence behavior

File handles are persistent client-visible tokens. The code itself stores no global state, but the bytes it emits can be cached by NFS clients across requests. The export ID scheme changes depending on `nfs.dynamic-volumes`: index-based handles are tied to child order, UUID-based handles are stable across dynamic volume changes.

## Dependencies and integration points

The file depends on `xdr-nfs3.h`, `nfs3-fh.h`, Gluster UUID/iatt utilities, and `nfs_xlator_to_xlid()` from NFS common code. Its output is consumed by NFSv3 replies, mount replies, readdirplus entries, and handle-resolution helpers.

## Risks and edge cases

- `nfs3_fh_hash_entry()` is declared in the header but not implemented here, suggesting stale API or another implementation to verify.
- `nfs3_fh_build_parent_fh()` copies export ID but not mount ID, unlike child handle construction.
- `nfs3_fh_validate()` only checks magic bytes; callers must still validate export and GFID.
- The packed struct must remain exactly `NFS3_FHSIZE`; size changes can break XDR decoding.

## Test signals

Tests should validate fixed handle size, magic validation, root GFID detection, indexed and UUID root handle encoding, child/parent export propagation, string formatting, and compatibility of handles across mount, lookup, and readdirplus flows.
