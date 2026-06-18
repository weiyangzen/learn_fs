# File Research: sources/cow-pools/openzfs/module/zfs/zfs_byteswap.c

## Summary
Provides byteswap routines for ZFS ACL and znode on-disk structures.

## Main Responsibilities
- Byteswaps old fixed `ace_t` ACL entries.
- Byteswaps modern variable-size ZFS ACE layouts.
- Byteswaps embedded ACLs inside old znode physical structures.
- Exports byteswap symbols in kernel builds.

## Key APIs
- `zfs_oldacl_byteswap()`
- `zfs_acl_byteswap()`
- `zfs_znode_byteswap()`
- Internal helpers: `zfs_oldace_byteswap()`, `zfs_ace_byteswap()`

## Important Behavior
`zfs_ace_byteswap()` supports both legacy ACE layout and ZFS ACL layout. It walks a byte buffer, swapping headers first, then chooses entry size based on flags and ACE type, with explicit overrun checks because embedded ACL buffers may be padded.

`zfs_znode_byteswap()` swaps all fixed 64-bit timestamp/stat fields and then swaps embedded ACE data based on ACL version.

## Risks
Variable-size ACE parsing is defensive but still depends on flags and type fields becoming meaningful immediately after byte swap. The old ACL path swaps the entire block because it lacks an exact ACE count.
