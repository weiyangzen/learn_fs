# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_hti_regs.h

Purpose: defines the HTI `HDPORT_STATE` register and bitfields used to identify firmware-owned display resources.

Important APIs/types/functions: `HDPORT_STATE` is the MMIO address. `HDPORT_ENABLED` gates interpretation. `HDPORT_DDI_USED(phy)` encodes per-PHY reservation bits. `HDPORT_DPLL_USED_MASK` extracts reserved DPLLs.

Control flow: `intel_hti.c` reads `HDPORT_STATE` and tests these bitfields during display initialization and resource queries.

State and persistence behavior: register definitions only; hardware supplies the state.

Dependencies and integration points: depends on i915 register macros from `intel_display_reg_defs.h` and the platform PHY numbering contract.

Risks: PHY-indexed bit arithmetic must remain aligned with hardware documentation. DPLL mask values must match the platform DPLL enum/allocator.

Test signals: register decode tests against known HTI state values and platform bringup with reserved DDI/DPLL resources.
