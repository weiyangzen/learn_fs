
# sources/distributed-fs/ceph-client/drivers/md/dm-pcache/Makefile

## Purpose
Defines how the persistent-cache device-mapper target is built. It aggregates the pcache target, cache device, segment, backing device, cache metadata, garbage collection, writeback, cache segment, key, and request handling objects into one `dm-pcache.o` module or built-in object.

## Important APIs, Types, And Functions
`dm-pcache-y` lists component objects: `dm_pcache.o`, `cache_dev.o`, `segment.o`, `backing_dev.o`, `cache.o`, `cache_gc.o`, `cache_writeback.o`, `cache_segment.o`, `cache_key.o`, and `cache_req.o`. `obj-$(CONFIG_DM_PCACHE) += dm-pcache.o` binds the aggregate to the Kconfig option.

## Control Flow
This is build-system control flow only. If `CONFIG_DM_PCACHE` is enabled, Kbuild compiles the listed objects and links them as the pcache module or built-in component.

## State And Persistence
No runtime state. The object list determines which source files contribute runtime state and on-media metadata handlers to the final target.

## Dependencies And Integration Points
Integrates with Kbuild and the `DM_PCACHE` Kconfig symbol. The aggregate depends on source-level initialization ordering inside `dm_pcache.o` and module init/exit functions.

## Risks
Forgetting an object causes unresolved symbols or missing behavior, especially because the visible files call helpers in `segment`, `cache_writeback`, `cache_segment`, and `dm_pcache`. Adding new source files requires updating this list.

## Test Signals
Build `CONFIG_DM_PCACHE=m` and `=y`, inspect linked symbols for all pcache subsystems, and run modpost to catch missing or stale object entries.
