# sources/distributed-fs/ceph-client/drivers/misc/open-dice.c

Purpose: exposes a reserved-memory region containing Open Profile for DICE measured-boot data through `/dev/open-diceN`, allowing userspace to read the region size, mmap the contents read-only/shared-safe, and request a wipe.

Important APIs and types: `struct open_dice_drvdata` stores a mutex, reserved-memory pointer, miscdevice, and generated device name. File operations are `open_dice_read()`, `open_dice_write()`, and `open_dice_mmap_prepare()`. Platform lifecycle is `open_dice_probe()`, `open_dice_remove()`, `open_dice_init()`, and `open_dice_exit()`.

Control flow: probe looks up the device-tree reserved memory, validates nonzero `ULONG_MAX`-bounded page-aligned base/size, allocates driver data, and registers a 0600 misc device. Read returns the region size as an `unsigned long`. Write ignores the user buffer and wipes the reserved memory by `devm_memremap()` with write-combine attributes, `memset()` to zero, and `devm_memunmap()`. Mmap forbids writable shared mappings, clears future write permission, sets write-combine and dump/copy avoidance flags, and maps the reserved physical range.

State and persistence: only the reserved memory content persists outside driver structures. A wipe mutates that memory to zero. Device index is static and monotonically increments during probes.

Dependencies and integration points: depends on device-tree `google,open-dice`, reserved-memory bindings, miscdevice, new VMA descriptor mmap helpers, and userspace consumers of the DICE handoff.

Risks and test signals: the region contains sensitive boot material, so permissions, no-dump/no-copy VMA flags, and wipe behavior are critical. Tests should cover absent reserved memory, unaligned regions, read offsets, mmap permission transitions, concurrent wipe/mmap/read, and optional absence where init treats `-ENODEV` as success.
