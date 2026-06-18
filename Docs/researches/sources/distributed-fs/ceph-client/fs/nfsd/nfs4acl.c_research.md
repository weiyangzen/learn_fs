# sources/distributed-fs/ceph-client/fs/nfsd/nfs4acl.c

## Purpose
`nfs4acl.c` translates between Linux POSIX ACLs/mode bits and NFSv4 ACL ACE lists for NFSD. It supports encoding filesystem ACLs as NFSv4 ACLs and converting client-supplied NFSv4 ACL attributes back into POSIX access/default ACLs.

## Important APIs, types, and functions
Public entry points include `nfsd4_get_nfs4_acl()`, `sort_pacl_range()`, `nfsd4_acl_to_attr()`, `nfs4_acl_bytes()`, `nfs4_acl_get_whotype()`, and `nfs4_acl_write_who()`. Major internal helpers include `mask_from_posix()`, `deny_mask_from_posix()`, `low_mode_from_nfs4()`, `summarize_posix_acl()`, `_posix_to_nfsv4_one()`, `sort_pacl()`, state allocation/free helpers, `process_one_v4_ace()`, `nfs4_acl_nfsv4_to_posix()`, and `ace2type()`.

## Control flow
For POSIX-to-NFSv4, the code fetches the access ACL or synthesizes one from mode, optionally fetches a directory default ACL, allocates a worst-case NFSv4 ACL, summarizes effective POSIX permissions under the mask, then emits ALLOW and DENY ACEs for owner, named users, owning group, named groups, and everyone. Default ACLs receive inheritance and inherit-only flags. For NFSv4-to-POSIX, the code initializes effective and default permission state, rejects unsupported ACE types or flags, routes inherited ACEs to default state only for directories, applies ALLOW/DENY masks in order, copies missing owner/group/other entries from effective state into default state when needed, builds POSIX ACLs, sorts named users/groups, and maps `-EINVAL` to `nfserr_attrnotsupp`.

## State and persistence
State is temporary conversion state only. `struct posix_acl_state` accumulates allow/deny masks for owner, group, other, everyone, named users, named groups, and POSIX mask. Resulting `na_pacl` and `na_dpacl` are attached to `struct nfsd_attrs` so the VFS setattr path can persist them. The special who-string table maps `OWNER@`, `GROUP@`, and `EVERYONE@`; all other names are treated as named principals.

## Dependencies and integration points
It depends on POSIX ACL APIs, NFSD ACL structures, VFS attribute setting, NFSv4 XDR streams, kernel uid/gid helpers, and filesystem ACL support. NFSv4 GETATTR/SETATTR ACL paths call these helpers during attribute encode/decode.

## Risks and test signals
Risks are semantic loss in both directions, especially DENY ordering, POSIX mask derivation, default ACL inheritance, directory delete-child handling, unsupported NFSv4 flags, named user/group sorting before `posix_acl_valid()`, and conservative permission reduction in `low_mode_from_nfs4()`. Test signals include round-trip ACL tests with owner/named user/group/everyone entries, DENY-before-ALLOW cases, inherited directory ACLs, files receiving inheritance flags, unsupported ACE types/flags, empty ACLs, ACLs without default owner/group/other entries, maximum ACE counts, special who-string encode/decode, and filesystems without POSIX ACL support.
