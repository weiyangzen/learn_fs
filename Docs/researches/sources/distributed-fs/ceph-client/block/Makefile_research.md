# sources/distributed-fs/ceph-client/block/Makefile

## Purpose
This Makefile defines which block-layer objects are built into the kernel or optional modules. It is the build-side counterpart to `block/Kconfig`.

## Important APIs, types, and targets
`obj-y` lists mandatory block core objects including `bdev.o`, `bio.o`, `blk-core.o`, multi-queue files, partition support, request QoS, disk events, and `badblocks.o`. Conditional `obj-$(CONFIG_*)` lines include BSG, block cgroup controllers, IO schedulers, integrity, zoned support, writeback throttling, debugfs, Opal, power management, inline encryption, and deprecated holder support. `bfq-y` composes the BFQ scheduler from `bfq-iosched.o`, `bfq-wf2q.o`, and `bfq-cgroup.o`.

## Control flow
Kbuild evaluates config symbols and appends matching objects. If `CONFIG_IOSCHED_BFQ` is enabled, the composite `bfq.o` is linked from the `bfq-y` list. Objects in `obj-y` are always included when the block directory is built.

## State and persistence behavior
The file has no runtime state. Its persistent effect is the object graph baked into the kernel build output.

## Dependencies and integration points
It depends on Kconfig symbols from `block/Kconfig` and scheduler Kconfig files. It integrates with top-level kernel Kbuild and with C files that expect symbols to be available only when their configuration is enabled.

## Risks
Object omissions cause link failures or missing runtime features. Adding an object to `obj-y` rather than a guarded `obj-$(CONFIG_*)` can force unwanted code into all block builds. Composite object ordering matters for BFQ because `bfq-cgroup.o` supplies hooks referenced by the main scheduler.

## Test signals
Build matrix coverage with BFQ, cgroups, inline encryption, integrity, zoned block devices, and debugfs toggled on and off is the key signal. Link-time undefined symbol checks are especially useful for conditional combinations.
