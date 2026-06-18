# sources/distributed-fs/ceph-client/fs/ntfs3/Kconfig

## Purpose
Defines kernel configuration options for the `ntfs3` read-write filesystem driver and optional feature sets.

## Important APIs, Types, And Functions
`NTFS3_FS` is a tristate driver option for filesystem type/module `ntfs3`; it depends on the legacy `NTFS_FS` being disabled or modular and selects `BUFFER_HEAD`, `NLS`, and `LEGACY_DIRECT_IO`. `NTFS3_64BIT_CLUSTER` enables 64-bit cluster numbers on 64-bit builds. `NTFS3_LZX_XPRESS` enables external Windows compression formats. `NTFS3_FS_POSIX_ACL` selects POSIX ACL support.

## Control Flow
Kconfig controls whether `Makefile` builds `ntfs3.o` and whether compression libraries and ACL code paths are compiled. Help text documents compatibility and recommended defaults.

## State And Persistence
No runtime state is defined here. The selected options affect on-disk compatibility: 64-bit clusters can create volumes Windows cannot mount, while POSIX ACLs are Linux-specific and ignored by Windows.

## Dependencies And Integration Points
Integrated with the kernel build system, `fs/ntfs3/Makefile`, VFS ACL support, NLS, buffer heads, and optional decompression code under `ntfs3/lib`.

## Risks And Edge Cases
Enabling 64-bit clusters changes interoperability expectations. Disabling LZX/XPRESS limits reading externally compressed files. ACL support can expose Linux-only metadata semantics on NTFS.

## Test Signals
Build `NTFS3_FS=y`, `m`, and disabled; verify module name and mount type; test optional compression and ACL matrices; ensure legacy `NTFS_FS` dependency constraints behave as intended.
