# sources/distributed-fs/ceph-client/drivers/block/Kconfig

Purpose: defines the Linux kernel configuration menu for block device drivers under `drivers/block`. It gates the entire block driver submenu behind `BLK_DEV`, sources subordinate Kconfig files, and declares selectable drivers such as floppy, loop, NBD, RAM disk, AoE, Xen, virtio, RBD, ublk, and zoned loop.

Important symbols: `menuconfig BLK_DEV` depends on `BLOCK` and defaults to enabled. Architecture-gated legacy drivers include `BLK_DEV_FD`, `AMIGA_FLOPPY`, `ATARI_FLOPPY`, `MAC_FLOPPY`, `BLK_DEV_SWIM`, `AMIGA_Z2RAM`, `N64CART`, and `GDROM`. Network/storage options include `BLK_DEV_NBD`, `ATA_OVER_ETH`, `BLK_DEV_RBD` with `select CEPH_LIB`, and `BLK_DEV_RNBD` through a sourced file. Virtualization options include UML UBD, Xen front/back, and `VIRTIO_BLK` selecting `SG_POOL`. Modern test/experimental options include `BLK_DEV_UBLK`, `BLKDEV_UBLK_LEGACY_OPCODES`, and `BLK_DEV_ZONED_LOOP`.

Control flow: Kconfig has declarative dependency flow. If `BLK_DEV=n`, all enclosed options are skipped. Sourced Kconfigs are included in menu order. Driver choices then control object inclusion in `drivers/block/Makefile` and subdirectory Makefiles.

State and persistence: configuration state persists in the kernel `.config` and controls compile-time object selection, module availability, selected dependencies, and help text exposed to configurators.

Dependencies and integration points: feeds the block driver Makefile, architecture symbols, networking, Xen, virtio, Ceph, io_uring, and sourced submenus. The `ATA_OVER_ETH` symbol is consumed by `drivers/block/aoe/Makefile`.

Risks: dependency mistakes can expose drivers on unsupported platforms or hide valid combinations. Help text may become stale relative to documentation. Test signals are Kconfig parsing (`make oldconfig`/`allyesconfig`/arch configs), expected object inclusion for selected symbols, and dependency propagation such as `BLK_DEV_RBD` selecting Ceph support.
