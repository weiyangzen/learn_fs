# sources/distributed-fs/ceph-client/drivers/block/Makefile

Purpose: maps block driver Kconfig symbols to built-in or modular objects for the kernel build. It is the primary build manifest for `drivers/block`.

Important entries: `ccflags-y += -I$(src)` makes local headers available for trace events. Object mappings include floppy variants (`floppy.o`, `amiflop.o`, `ataflop.o`, `swim3.o`, `swim_mod.o`), memory/virtual drivers (`z2ram.o`, `brd.o`, `loop.o`, `zloop.o`), network/storage drivers (`nbd.o`, `rbd.o`, `drbd/`, `rnbd/`), virtualization drivers (`virtio_blk.o`, Xen front/back), PS3 drivers, null block, Rust null block, ublk, and mtip32xx. `swim_mod-y` combines `swim.o` and `swim_asm.o`.

Control flow: Kbuild evaluates each `obj-$(CONFIG_...)` assignment according to the final kernel configuration. `y` entries link built-in objects; `m` entries produce modules where supported; directory entries recurse into subdirectories.

State and persistence: no runtime state. Build state is produced in object/module artifacts based on `.config`.

Dependencies and integration points: tightly coupled to `drivers/block/Kconfig`; every referenced `CONFIG_*` should be defined there or in a sourced Kconfig. `CONFIG_ATA_OVER_ETH` is intentionally handled by `drivers/block/aoe/Makefile`, so this file does not list AoE directly in the viewed excerpt.

Risks: stale mappings cause selected drivers not to build or unselected code to build. Missing composite object lists break module links. Test signals include `make drivers/block/`, randconfig build coverage, and confirming `CONFIG_AMIGA_FLOPPY=m/y` produces `amiflop.o`.
