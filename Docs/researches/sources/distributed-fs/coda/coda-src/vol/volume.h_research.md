# sources/distributed-fs/coda/coda-src/vol/volume.h

Purpose: primary public contract for Coda volumes, volume disk data, memory-resident volume state, lifecycle APIs, and lock/disk-usage helpers.

Important types/definitions: `ProgramType` identifies file server, volume utility, salvager, or fs utility. `VolumeHeader` is the recoverable header. `VolumeDiskData` is the persistent administrative record with flags, ids, version vector, quotas, usage counters, dates, resolution log pointer, and messages. `vnodeIndex` is the VM allocation bitmap. `VolLock` is the volume-level mutation lock. `Volume` is the VM object tying hash links, cached header, partition, RVM index, vnode bitmaps, online/offline flags, refcount, special status, locks, and reintegrator state. `volHeader` is the LRU-cached copy of disk data.

Control flow/state: macros expose fields of cached `VolumeDiskData`, so most code mutates `V_inUse`, `V_destroyMe`, `V_diskused`, etc. through macro lvalues. Attach modes (`V_READONLY`, `V_CLONE`, `V_UPDATE`, `V_DUMP`, `V_SECRETLY`) define how utilities coordinate with the file server.

Dependencies/integration: includes recovery volume logs, vice types, partition lists, and `voldefs.h`; exposes initialization, lookup, attach, update, purge, shutdown, stats, disk usage, and volume-object lock APIs. Risks include macro-heavy mutable state, persistent layout ABI, raw pointers in persistent/VM structures, and transaction annotations that callers must honor. Test signals: ABI/layout compatibility, attach mode matrix, field macro mutation, disk usage enforcement, and lock helper behavior.
