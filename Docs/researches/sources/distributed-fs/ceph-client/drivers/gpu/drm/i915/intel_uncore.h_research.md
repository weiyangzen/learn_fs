# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_uncore.h

Purpose: Defines the uncore data model and inline MMIO API used by i915 code to access registers safely across power-gated GT/media/GSC domains.

Important APIs/types: `struct intel_uncore`, `struct intel_uncore_funcs`, `struct intel_uncore_fw_get`, `struct intel_forcewake_range`, `struct intel_uncore_mmio_debug`, forcewake domain enums and bitmasks, raw accessors `__raw_uncore_read/write*`, traced accessors `intel_uncore_read/write*`, untraced accessors, `_fw` raw critical-section accessors, forcewake APIs, register wait helpers, `intel_uncore_rmw()`, `intel_uncore_rmw_fw()`, `intel_uncore_read64_2x32()`, and `raw_reg_read/write()`.

Control flow: Inline read/write functions dispatch through `uncore->funcs`, which the C file initializes based on platform and forcewake requirements. Raw helpers apply `gsi_offset` for GSI registers below `0x40000`. `intel_uncore_read64_2x32()` locks uncore, forcewakes both halves, and retries upper/lower reads to reduce rollover races.

State/persistence: The header lays out persistent uncore state: MMIO base, GT/runtime PM pointers, forcewake tables, shadow tables, timers, active counts, user forcewake count, FIFO count, and debug flags. The `UNCORE_NEEDS_FLR_ON_FINI` flag persists teardown policy until `intel_uncore_fini_mmio()`.

Dependencies/integration: Includes Linux locking/timer/io helpers and i915 register definitions. Used almost everywhere hardware registers are touched. The locked `_fw` accessors are intended for IRQ/critical sections where callers explicitly manage serialization and forcewake.

Risks: Raw and `_fw` helpers bypass normal tracing, forcewake acquisition, and some safety checks; callers must hold the right locks and domains. 64-bit writes are explicitly unsupported due to 32-bit split-write hazards. `raw_reg_read/write()` does not apply `gsi_offset`, so GSI users must compensate manually.

Test signals: Compile-time coverage through inline use, runtime warnings from implementation assertions, and selftest validation for forcewake/shadow behavior.
