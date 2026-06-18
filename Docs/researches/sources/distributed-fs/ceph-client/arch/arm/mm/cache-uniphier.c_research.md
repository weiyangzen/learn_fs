# sources/distributed-fs/ceph-client/arch/arm/mm/cache-uniphier.c

Purpose: implements the Socionext UniPhier outer/system cache controller, including multi-level cache discovery, queued range/all maintenance operations, active way setup, enable/disable, and global `outer_cache` callback registration.

Important APIs/types/functions: key type is `struct uniphier_cache_data` with control, revision, operation, and way-control MMIO bases plus way/line/range metadata and list node. Important functions include `__uniphier_cache_sync`, `__uniphier_cache_maint_common`, `__uniphier_cache_maint_all`, `__uniphier_cache_maint_range`, `__uniphier_cache_enable`, `__uniphier_cache_set_active_ways`, `uniphier_cache_inv_range`, `uniphier_cache_clean_range`, `uniphier_cache_flush_range`, `uniphier_cache_flush_all`, `uniphier_cache_disable`, `uniphier_cache_enable`, `uniphier_cache_sync`, `__uniphier_cache_init`, and `uniphier_cache_init`.

Control flow: initialization finds an L2 `socionext,uniphier-system-cache` node, recursively follows next-level cache nodes, validates cache properties, maps control/revision/operation registers, derives way masks and range limits, and appends each level to `uniphier_cache_list`. It registers `outer_cache` callbacks, invalidates all levels, enables each level, and programs active ways per possible CPU. Runtime range operations iterate all cache levels and submit queued operations; all operations sync afterward.

State and persistence: `uniphier_cache_list` persists discovered cache levels and MMIO mappings. Hardware control registers retain enabled state and active-way masks. Allocated `uniphier_cache_data` structures remain for the lifetime of the kernel.

Dependencies and integration points: depends on device tree cache properties (`cache-level`, `cache-unified`, `cache-line-size`, `cache-sets`, `cache-size`), MMIO mapping, Linux list infrastructure, `outer_cache`, and UniPhier hardware queue semantics.

Risks: operation registration relies on hardware arbitration and per-CPU status, so local IRQs are disabled for the command sequence but no global lock is used. `range_op_max_size` is reduced by line size; if not initialized correctly, chunking can underflow. L2 initialization failure is fatal, while later levels are optional, so error handling must preserve usable lower levels. SoC revisions have different active-way register offsets.

Test signals: boot UniPhier boards with single and multi-level caches, validate DT property errors, run DMA coherency tests across ranges larger than the queue max, exercise all-cache flush/invalidate paths, and test disable paths during shutdown or power management.
