# sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs3-fh.h

## Purpose

`nfs3-fh.h` defines the wire-compatible Gluster NFSv3 file-handle structure and builder/validator API. It fixes the handle layout used by mount, lookup, readdirplus, and all NFSv3 operations that identify files by opaque NFS handles.

## Important APIs, types, and functions

`struct nfs3_fh` is a packed 64-byte handle containing four identifier bytes, `exportid`, object `gfid`, `mountid`, and padding. Macros define the magic bytes, static size, static initializer, and index extraction from `exportid[15]`. Prototypes cover compute size, hash entry, validation, indexed/UUID root builders, root detection, child/parent handle derivation, logging, formatting, and inode-based handle construction.

## Control flow

The header has no runtime control flow. It encodes the expected handle lifecycle: create a root handle for an export, derive child handles from attributes returned by lookup/create/readdirplus, validate handles on incoming requests, then map export ID plus GFID back to a subvolume and inode.

## State and persistence behavior

The struct layout is a persistent client-facing ABI. NFS clients treat it as opaque but may cache it for long periods, so identifier, export ID, GFID, and mount ID semantics must remain stable. Dynamic-volume mode relies on UUID export IDs; non-DVM mode relies on subvolume index in the final export ID byte.

## Dependencies and integration points

The header includes NFSv3 XDR definitions, Gluster `iatt`, UUID compatibility, and xlator list types. It is included by `nfs3.h`, mount code, helper code, and file-handle implementation.

## Risks and edge cases

- Any change to `struct nfs3_fh` must preserve `NFS3_FHSIZE`.
- The index macro reads only `exportid[15]`, limiting non-DVM indexed exports to one byte of identity.
- Declared functions must stay synchronized with implementations; currently `nfs3_fh_hash_entry()` needs link verification.

## Test signals

Static assertions or tests should confirm size and field offsets. Runtime tests should cover stale/invalid handles, root handles under both export schemes, and readdirplus handle decode by a client.
