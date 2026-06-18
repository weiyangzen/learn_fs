# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/mem-types.h

Purpose: `mem-types.h` enumerates common allocation type IDs used by the GlusterFS memory accounting system.

Important APIs and types: `enum gf_common_mem_types_` includes type IDs for core objects such as event pools, fd/inode tables, translators, volume options, timers, iobufs, rpc structures, graph objects, trie nodes, runner argv/log buffers, statedump buffers, store handles, syncop tasks/envs, throttle buckets, volfiles, and generic integer/pointer/data pairs. `gf_common_mt_end` terminates the enum.

Control flow and state: no logic. The enum values are persisted only indirectly in allocation accounting records and debug diagnostics.

Dependencies and integration: `mem-pool.h` stringizes these constants in `GF_MALLOC`/`GF_CALLOC` calls, and many source files choose a type ID to make statedumps and leak diagnosis meaningful.

Risks: changing enum order can confuse any tooling that assumes numeric stability in dumps. New subsystems need distinct entries to avoid misleading accounting. Overusing generic entries reduces diagnostic value.

Test signals: build coverage should catch missing enum names. Runtime memory-accounting/statedump tests should assert allocations are attributed to expected type strings for translators, graph objects, sync tasks, and parser allocations.
