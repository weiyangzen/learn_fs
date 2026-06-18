# sources/distributed-fs/ceph-client/drivers/block/zram/Kconfig

Purpose: Kconfig menu for the zram compressed RAM block device and its selectable compression backends/features.

Important symbols: `ZRAM` enables the driver and selects `ZSMALLOC`. Backend booleans select LZ4, LZ4HC, ZSTD, DEFLATE, 842, and LZO/LZO-RLE libraries. `ZRAM_BACKEND_FORCE_LZO` guarantees LZO support when no other backend is selected. The default compressor choice emits `ZRAM_DEF_COMP`. Optional features include `ZRAM_WRITEBACK`, `ZRAM_TRACK_ENTRY_ACTIME`, `ZRAM_MEMORY_TRACKING`, and `ZRAM_MULTI_COMP`.

Control flow and state: this file has no runtime control flow; it controls compilation, default strings, and dependency closure. The default compressor choice is constrained by enabled backend symbols. Memory tracking selects access-time tracking.

Dependencies and integration: integrates zram with block, sysfs, MMU, zsmalloc, compression libraries, debugfs, writeback support, and admin documentation.

Risks: invalid combinations are mostly prevented by dependencies, but default compressor availability depends on matching backend selection. The force-LZO fallback changes configuration even when a user did not explicitly choose LZO.

Test signals: config matrix builds for each backend, no-backend fallback to LZO, default compressor string correctness, writeback/access-time/debugfs combinations, and multi-compressor builds.
