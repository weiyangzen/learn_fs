# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/coredump.c

Purpose: Firmware crash dump assembly for MT7915/MT7916/MT798x devices, with optional firmware memory dumping exposed through Linux devcoredump.

Important APIs: `mt7915_coredump_get_mem_layout`, `mt7915_coredump_new`, `mt7915_coredump_submit`, `mt7915_coredump_register`, and `mt7915_coredump_unregister`. Internal helpers compute memory size and collect firmware state, trace, stack, task, and context information.

Control flow: registration allocates `dev->coredump.crash_data` and optionally a memory buffer based on chip-specific region layout when `coredump_memdump=1`. On crash, `mt7915_coredump_new` records GUID/timestamp under `dump_mutex`; `mt7915_coredump_build` allocates a packed dump, copies metadata, reads firmware exception registers, traces, task queues, context, call stack, and optional pre-collected memory, then `dev_coredumpv` submits it.

State and persistence: crash data persists in `dev->coredump.crash_data` across crashes until unregister. The module parameter `coredump_memdump` controls large memory capture. Dump payload contains kernel/fw version, chip id, exception state, traces, and optional memory region data.

Dependencies and integration: called by init/register/unregister and `mt7915_mac_dump_work`; uses devcoredump, `vzalloc`, UTS name, GUID/time helpers, register access, and `mt7915_memcpy_fromio`.

Risks: memory layout lengths are hardware-specific and large; buffer length accounting must stay aligned with headers. `mt7915_coredump_unregister` assumes `crash_data` exists. Trace loops copy large fixed arrays and rely on firmware register formats varying by chip.

Test signals: firmware assert via debugfs, coredump with and without memdump, chip variants 7915/7916/7981/7986, devcoredump userspace retrieval, unregister after failed partial registration, and lockdep around `dump_mutex`.
