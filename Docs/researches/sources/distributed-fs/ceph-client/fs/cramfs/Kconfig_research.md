# sources/distributed-fs/ceph-client/fs/cramfs/Kconfig

Purpose: declares build options for the compressed ROM filesystem.

Important entries: `CONFIG_CRAMFS` is a tristate that selects `ZLIB_INFLATE`. `CONFIG_CRAMFS_BLOCKDEV` enables mounting images from block devices and defaults to yes when block support is available. `CONFIG_CRAMFS_MTD` enables direct mapping from physical memory through MTD and depends on compatible Cramfs/MTD build modes.

Control flow: no runtime logic. These options compile in the block-device read path, MTD direct-map path, or both.

State and persistence: no runtime state; Kconfig controls feature availability.

Dependencies/integration: links to `fs/cramfs/Makefile`; selects zlib inflate for `uncompress.c`; depends on `BLOCK` and `MTD` for the respective backends.

Risks: disabling both blockdev and MTD support leaves the filesystem type with no viable get-tree backend. The help text documents format limitations: read-only, small filesystem/file size limits, limited uid/gid/timestamps/hard links.

Test signals: build each combination of `CRAMFS`, `CRAMFS_BLOCKDEV`, and `CRAMFS_MTD`; mount block images; mount `mtd:<name>` direct images; and ensure zlib dependencies resolve for module and built-in builds.
