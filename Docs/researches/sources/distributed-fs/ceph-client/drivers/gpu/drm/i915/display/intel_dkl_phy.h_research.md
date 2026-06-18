# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dkl_phy.h

## Purpose
This header declares the Dekel PHY register access API for display code.

## Important APIs, Types, and Functions
It includes `intel_dkl_phy_regs.h` for `struct intel_dkl_phy_reg` and declares `intel_dkl_phy_init()`, `intel_dkl_phy_read()`, `intel_dkl_phy_write()`, `intel_dkl_phy_rmw()`, and `intel_dkl_phy_posting_read()`.

## Control Flow
The header has no logic. The API contract is that callers initialize the PHY lock before performing serialized register accesses through the C implementation.

## State and Persistence Behavior
No state is defined here. Accessors operate on lock and hardware state owned by `struct intel_display` and Dekel PHY registers.

## Dependencies and Integration Points
It forward-declares `struct intel_display` and depends on Dekel register descriptors. It is consumed by PHY, DDI, PLL, and Type-C display code needing banked PHY MMIO access.

## Risks
Callers must not bypass these helpers for banked Dekel registers unless they can prove serialization and HIP index correctness. The API also assumes the caller has satisfied runtime power requirements.

## Test Signals
Build coverage, Dekel PHY link bring-up, register read/write validation, and absence of HIP index races are the main signals.
