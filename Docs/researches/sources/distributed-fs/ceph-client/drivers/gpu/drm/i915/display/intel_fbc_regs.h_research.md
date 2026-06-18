# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fbc_regs.h

Purpose: defines MMIO register offsets and bitfields for legacy FBC, DPFC, FBC render-state nuke, dirty-rect, underrun debug, stride override, and Xe3p system-cache usage.

Important APIs/types/functions: contains register macros such as `FBC_CONTROL`, `FBC_STATUS`, `FBC_CFB_BASE`, `FBC_LL_BASE`, `FBC_TAG()`, `DPFC_CONTROL`, `ILK_DPFC_CONTROL()`, `ILK_DPFC_CB_BASE()`, `GLK_FBC_STRIDE()`, `XE3_FBC_DIRTY_RECT()`, `XE3_FBC_DIRTY_CTL()`, `FBC_DEBUG_STATUS()`, `SNB_DPFC_CTL_SA`, `MSG_FBC_REND_STATE()`, and `XE3P_LPD_FBC_SYS_CACHE_USAGE_CFG`, plus field helpers for enable bits, compression status, plane/fence selection, compression ratio limits, dirty line ranges, and cache ranges.

Control flow: no runtime flow exists in the header. `intel_fbc.c` uses these constants to program CFB bases, activate/deactivate compression, nuke compression state, select planes/fences, enable dirty-rect tracking, apply workarounds, inspect underrun status, and configure system cache.

State and persistence: the header itself has no state; it describes persistent hardware MMIO state that survives until explicitly reprogrammed or reset.

Dependencies and integration: depends on `intel_display_reg_defs.h` for `_MMIO`, `_MMIO_PIPE`, and `REG_*` helpers. The macros are tightly coupled to the per-generation function tables in `intel_fbc.c`.

Risks: bitfield mistakes can corrupt display registers, select the wrong plane/fence, allocate CFB outside accessible stolen ranges, or leave FBC active during unsafe updates. Some field names overlap across generations, so callers must use the right macro for the active platform.

Test signals: compile all platform variants, inspect register writes with debug logs or MMIO tracing during FBC enable/disable, and run underrun/dirty-rect/system-cache paths on hardware that advertises those feature bits.
