<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mnt_idmapping.h -->
# sources/distributed-fs/ceph-client/include/linux/mnt_idmapping.h

## Purpose
`mnt_idmapping.h` defines VFS mount-idmapping helpers for converting between kernel IDs, filesystem IDs, and VFS-visible IDs. It supports idmapped mounts and preserves type separation between `kuid_t`/`kgid_t` and `vfsuid_t`/`vfsgid_t`.

## Important APIs, Types, and Functions
The header declares `struct mnt_idmap`, `nop_mnt_idmap`, `invalid_mnt_idmap`, and `init_user_ns`. It introduces `vfsuid_t` and `vfsgid_t`, validated with `static_assert()` to have the same layout as `kuid_t` and `kgid_t`. Helpers include `is_valid_mnt_idmap()`, `__vfsuid_val()`, `__vfsgid_val()`, `vfsuid_valid()`, `vfsgid_valid()`, equality helpers, `VFSUIDT_INIT`, `VFSGIDT_INIT`, `INVALID_VFSUID`, `INVALID_VFSGID`, `AS_KUIDT`, `AS_KGIDT`, `vfsgid_in_group_p()`, `mnt_idmap_get()`, `mnt_idmap_put()`, `make_vfsuid()`, `make_vfsgid()`, `from_vfsuid()`, `from_vfsgid()`, `vfsuid_has_fsmapping()`, `vfsgid_has_fsmapping()`, `vfsuid_has_mapping()`, `vfsgid_has_mapping()`, `vfsuid_into_kuid()`, `vfsgid_into_kgid()`, `mapped_fsuid()`, and `mapped_fsgid()`.

## Control Flow and State
Creation paths map a kernel UID/GID through a mount idmap and filesystem user namespace into a VFS ID. Commit paths convert VFS IDs back to kernel IDs after checking filesystem mappings. `mapped_fsuid()` and `mapped_fsgid()` use the current task credentials to initialize ownership for newly created filesystem objects.

## State and Persistence Behavior
The file only declares helpers and external idmap objects. Reference management is via `mnt_idmap_get()` and `mnt_idmap_put()`. Persistent filesystem ownership is affected indirectly when callers use mapped IDs for inode or quota creation.

## Dependencies and Integration Points
It depends on `linux/uidgid.h`, current credential helpers, user namespaces, and mount state from `struct vfsmount`. It is used by VFS inode creation, permission checks, quota code, and filesystems that support idmapped mounts.

## Risks
Mixing raw `uid_t`/`gid_t` with VFS IDs bypasses namespace checks. Treating `nop_mnt_idmap` as a normal idmap can skip fast-path semantics. Invalid IDs intentionally compare false, so callers must check validity before committing ownership. `CONFIG_MULTIUSER=n` forces value accessors to zero, which changes tests and assumptions.

## Test Signals
Exercise idmapped mount creation, inode ownership under user namespaces, invalid mapping failures, group membership checks, `nop_mnt_idmap` behavior, and builds with and without `CONFIG_MULTIUSER`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mnt_idmapping.h -->
