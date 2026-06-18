# File Research: sources/block-storage/linux-dm/drivers/md/Makefile

## Purpose
Maps MD, bcache, and device-mapper Kconfig symbols to kernel objects and composite module object lists.

## Main Contents
- Defines composite objects for `dm-mod`, multipath path selectors, snapshots, mirrors, thin, cache, clone, verity, zoned, MD core, RAID456, linear, multipath, and faulty personalities.
- Builds MD personalities before `md-mod.o`, preserving auto-detection personality registration order.
- Descends into `bcache/` for `CONFIG_BCACHE` and `persistent-data/` for `CONFIG_DM_PERSISTENT_DATA`.
- Adds optional objects to `dm-mod` for init-time table creation, uevents, zoned support, IMA, and audit.
- Adds optional verity FEC and root-hash signature objects.

## Control Flow
The Makefile uses `obj-$(CONFIG_...)` and `*-y` lists. Composite lists gather implementation files into one module or built-in object, while conditional `ifeq` blocks append secondary support files only for built-in boolean features.

## Integration Points
Tightly coupled to `drivers/md/Kconfig`: every configured target has a matching object rule. It also couples DM targets to helper subdirectories and optional kernel facilities such as IMA, audit, zoned block devices, and verity FEC/signature support.

## Notable Behaviors
- Link order comment documents that RAID personalities must precede MD core for boot auto-initialization.
- `dm-round-robin.o` is always built with `DM_MULTIPATH`; other path selectors are independently optional.
- `dm-builtin.o` is controlled by `BLK_DEV_DM_BUILTIN`, not only by `BLK_DEV_DM`.

## Risks And Review Focus
- Missing or mismatched object entries silently break feature builds.
- Composite object names must stay aligned with module names advertised in Kconfig help.
- Conditional append rules for `dm-mod-objs` and `dm-verity-objs` are easy to desynchronize from their Kconfig booleans.
