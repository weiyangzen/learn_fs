<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_mocs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_mocs.c

Purpose: defines and programs Memory Object Control State tables for i915 GTs, selecting platform-specific cacheability/L3/L4 settings and installing them into global, per-engine, and L3CC registers.

Important APIs and functions: public functions are `intel_mocs_init()`, `intel_mocs_init_engine()`, and `intel_set_mocs_index()`. Internal types `drm_i915_mocs_entry` and `drm_i915_mocs_table` carry table entries, sizes, and well-known UC/WB/unused indices. Platform tables include SKL/Broxton, ICL/TGL/Gen12, DG1/DG2, and MTL variants. Helpers include `get_mocs_settings()`, `get_entry_control()`, `__init_mocs_table()`, `mocs_offset()`, `init_mocs_table()`, `get_entry_l3cc()`, `l3cc_combine()`, and `init_l3cc_table()`.

Control flow: table selection zeroes a table descriptor, chooses entries and indices based on graphics IP/platform, validates size and Gen9 skip-caching workaround restrictions, and returns flags indicating global MOCS, engine MOCS, and render L3CC programming. GT init programs global MOCS registers when supported and always programs L3CC when flagged. Engine init, called under forcewake, skips global-MOCS platforms, otherwise writes each engine's MOCS table and programs render L3CC for render engines. `intel_set_mocs_index()` caches UC and optional WB indices into `gt->mocs` for command emitters such as migration and LRC workarounds.

State and persistence: software persists selected indices in `gt->mocs`. Hardware persists MOCS and LNCFCMOCS register tables until reset or power loss, so init paths must run at GT/engine initialization and after reset as appropriate. Undefined entries are filled from `unused_entries_index` to discourage accidental reserved-index use.

Dependencies and integration points: depends on platform/IP feature macros, intel uncore forcewake MMIO, MCR multicast writes for XeHP+ L3CC, engine IDs/classes, GT MOCS storage, and command emitters that encode MOCS indices into BLTs. User-space ABI relies on stable MOCS indices for older platforms and bspec-published tables for ICL+.

Risks: MOCS indices are ABI-sensitive; changing existing entries can break userspace/GmmLib assumptions. Reserved hardware entries must be programmed but not used on ICL+. DGFX/global-MOCS handling differs from integrated platforms. `mocs_offset()` only lists known engine IDs and asserts on unsupported IDs. Wrong UC/WB indices can cause coherency or Flat CCS copy bugs.

Test signals: `selftest_mocs.c`, register readback after GT/engine init and reset, platform table selection tests across Gen9-Gen12/DG1/DG2/MTL, BLT migration coherency tests, userspace MOCS ABI tests, and forcewake/MCR validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_mocs.c -->
