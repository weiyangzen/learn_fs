# sources/distributed-fs/ceph-client/fs/romfs/Makefile

## Purpose
The ROMFS Makefile connects Kconfig selections to the kernel build. It builds the `romfs` object when `CONFIG_ROMFS_FS` is enabled and conditionally includes NOMMU MTD mmap support.

## Important Build Rules
`obj-$(CONFIG_ROMFS_FS) += romfs.o` builds ROMFS as built-in or module according to the top-level tristate. `romfs-y := storage.o super.o` always includes storage access and superblock/inode logic. When `CONFIG_MMU` is not `y`, `romfs-$(CONFIG_ROMFS_ON_MTD) += mmap-nommu.o` adds direct MTD mmap support for NOMMU systems.

## Control Flow
Build control is declarative. The composite `romfs.o` is formed from required objects and optional `mmap-nommu.o`. The conditional deliberately excludes NOMMU mmap code on MMU builds and excludes it when MTD backing is not enabled.

## State And Persistence
No runtime state is present. The file determines which object files are linked into the kernel or module.

## Dependencies And Integration Points
It consumes `CONFIG_ROMFS_FS`, `CONFIG_MMU`, and `CONFIG_ROMFS_ON_MTD` from Kconfig. It assumes `super.o` provides filesystem registration and `storage.o` provides backing-store reads, while `mmap-nommu.o` provides `romfs_ro_fops` only for the `!MMU && ROMFS_ON_MTD` case referenced by `internal.h`.

## Risks
The conditional must stay aligned with `internal.h`; otherwise `romfs_ro_fops` could be declared but not linked, or NOMMU MTD direct mapping support could be silently omitted. Build coverage across MMU/NOMMU and backing-store combinations is the main guard.

## Test Signals
Compile tests should verify block-only, MTD-only, both, MMU, and NOMMU combinations. A NOMMU plus MTD build should include `mmap-nommu.o`; ordinary MMU builds should not.
