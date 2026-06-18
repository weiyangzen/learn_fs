# sources/distributed-fs/ceph-client/fs/romfs/Kconfig

## Purpose
This Kconfig file declares ROMFS filesystem support and selects which backing stores are compiled: block devices, MTD devices, or both. It makes ROMFS available as a tiny read-only filesystem for initramfs/install media and other read-only media.

## Important Symbols
`ROMFS_FS` is the top-level tristate, dependent on `BLOCK || MTD`. The `choice` block selects one of `ROMFS_BACKED_BY_BLOCK`, `ROMFS_BACKED_BY_MTD`, or `ROMFS_BACKED_BY_BOTH`. Derived booleans `ROMFS_ON_BLOCK` and `ROMFS_ON_MTD` are set from that choice. `ROMFS_ON_BLOCK` selects `BUFFER_HEAD`, because block-backed storage uses buffer heads in `storage.c`.

## Control Flow
Kconfig control flow is declarative. Enabling `ROMFS_FS` opens the backing-store choice. Block support requires `BLOCK`; MTD support requires built-in MTD or module-compatible MTD when ROMFS is a module. The selected derived symbols control conditional compilation in `storage.c`, `internal.h`, and `Makefile`.

## State And Persistence
The file controls build-time configuration only. It does not manage runtime state or persistent filesystem data. Its choices determine which code paths exist in the built kernel/module.

## Dependencies And Integration Points
It integrates with the kernel build system, MTD, block layer, and buffer-head infrastructure. `Documentation/filesystems/romfs.rst` is referenced for format/user documentation. `Makefile` consumes `CONFIG_ROMFS_FS`, `CONFIG_ROMFS_ON_MTD`, and `CONFIG_MMU`.

## Risks
Misconfigured dependencies can build ROMFS without any backing store, which `storage.c` explicitly rejects with a preprocessor error. Module/built-in dependency rules for MTD are important because direct MTD access must be linkable. Choosing only block support disables NOMMU direct MTD mapping.

## Test Signals
Build matrix tests should cover `ROMFS_FS=n`, `m`, and `y`; block-only, MTD-only, and both; MMU and NOMMU; and module builds with MTD as built-in or module-compatible. Runtime smoke tests should mount block-backed and MTD-backed ROMFS images matching the selected configuration.
