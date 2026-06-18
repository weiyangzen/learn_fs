# sources/distributed-fs/openafs/src/afs/UKERNEL/osi_groups.c

## Purpose

`osi_groups.c` implements UKERNEL group-list manipulation for PAG assignment. It adapts OpenAFS PAG encoding into the user-space credential group array.

## Important APIs, Types, and Functions

- `afs_xsetgroups` is unsupported and asserts.
- `afs_getgroups` copies `cred->cr_groups` into a caller-provided `gid_t` array and returns `cr_ngroups`.
- `afs_setgroups` validates `NGROUPS_MAX`, optionally copies the credential with `crcopy`, sets `cr_ngroups`, and writes the new group list.
- `usr_setpag` generates or accepts a PAG value, allocates a small temporary group array, inserts two PAG groups if none are present, encodes the PAG with `afs_get_groups_from_pag`, and updates the credential.

## Control Flow

`usr_setpag` is the public path, used through the `setpag` macro in `sysincludes.h`. It generates a PAG if `pagvalue == -1`, copies current groups, makes room for the two PAG gids when needed, and calls `afs_setgroups`. Cleanup always frees the temporary small-space allocation.

## State and Persistence Behavior

The file mutates only in-memory `usr_ucred` group membership. If `change_parent` is false, a copied credential is installed through the caller's `cred` pointer; otherwise the original credential is changed in place. The PAG persists for that credential until it is replaced or freed.

## Dependencies and Integration Points

It depends on OpenAFS PAG helpers `afs_genpag`, `afs_get_pag_from_groups`, `afs_get_groups_from_pag`, and `crcopy`, plus UKERNEL small-space allocation. It integrates with token identity and request creation through credentials.

## Risks and Edge Cases

`gidset` is allocated with fixed `AFS_SMALLOCSIZ`; group insertion checks byte size before shifting, but `afs_getgroups` must not overflow that buffer if a credential already has many groups. `afs_xsetgroups` intentionally aborts if reached. `pagvalue == -1` is compared against an unsigned `afs_uint32`, relying on wrap semantics.

## Test Signals

Test PAG creation with and without an existing PAG, maximum group counts, `change_parent` true and false, allocation failure, invalid oversized group lists, and round-trip decoding through `afs_get_pag_from_groups`.
