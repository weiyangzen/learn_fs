# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_hti.c

Purpose: captures Hardware Test Interface display resource reservations so i915 does not use display PHYs or DPLLs already claimed by HTI firmware/hardware state.

Important APIs/types/functions: `intel_hti_init()` reads `HDPORT_STATE` when the platform advertises HTI. `intel_hti_uses_phy()` reports whether HTI enabled a given PHY. `intel_hti_dpll_mask()` returns the DPLL mask encoded in the HTI state.

Control flow: display initialization calls `intel_hti_init()` before output creation. Later output and DPLL setup can query the cached state to skip reserved resources.

State and persistence behavior: a single MMIO snapshot is stored in `display->hti.state`. This runtime cache persists until driver teardown or reinitialization and is not refreshed dynamically.

Dependencies and integration points: depends on `DISPLAY_INFO(display)->has_hti`, `intel_de_read()`, `HDPORT_STATE` bits from `intel_hti_regs.h`, PHY enum values, and DPLL allocation logic elsewhere in i915.

Risks: the DPLL mask comment notes that bit values must match platform DPLL numbering. A stale or incorrectly decoded HTI state can hide usable resources or allow conflicts with HTI-owned ports. `intel_hti_uses_phy()` warns on `PHY_NONE`, so callers need valid PHY mapping.

Test signals: platform boots with and without HTI support, logs/resource availability when HTI reserves a DDI, DPLL mask correctness for each platform, and warnings for invalid PHY callers.
