# sources/distributed-fs/ceph-client/include/linux/poison.h

Purpose: centralizes debug poison pointer and byte constants used by lists, timers, memory allocators, slab, journals, DMA pools, networking, BPF, VFS, stack depot, io_uring, and security code.

Important APIs and types: defines `POISON_POINTER_DELTA`, pointer sentinels such as `LIST_POISON1/2`, `TIMER_ENTRY_STATIC`, `TAIL_MAPPING`, `MUTEX_POISON_WW_CTX`, `SKB_LIST_POISON_NEXT`, `NET_PTR_POISON`, `BPF_PTR_POISON`, `VFS_PTR_POISON`, `STACK_DEPOT_POISON`, and `IO_URING_PTR_POISON`, plus byte patterns such as `PAGE_POISON`, `SLUB_RED_*`, `POISON_INUSE`, `POISON_FREE`, `POISON_END`, and subsystem-specific free markers.

Control flow: subsystems assign these constants to freed, inactive, or invalidated pointers/memory so accidental reuse faults early or is recognizable in memory dumps. Architectures may offset poison pointers with `CONFIG_ILLEGAL_POINTER_VALUE`.

State and persistence: no state is held; constants influence debug/runtime memory contents.

Dependencies and integration points: used by list manipulation, timer setup, page/slab allocators, journal code, DMA pool, networking, mutex debugging, key destruction, BPF, VFS, stack depot, and io_uring.

Risks and test signals: risks include choosing poison values that become valid mapped addresses, collisions with subsystem bit packing such as page-pool signatures, and tests relying on exact poison values across architectures. Test list/slab/page poisoning, KASAN/KFENCE-style diagnostics, freed object detection, and architecture illegal-pointer offsets.
