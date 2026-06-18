# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dkl_phy.c

## Purpose
This file implements serialized access to Dekel PHY registers. Dekel registers require selecting a HIP index/bank before accessing the actual MMIO register, so the code wraps reads, writes, read-modify-writes, and posting reads with a display-global PHY spinlock.

## Important APIs, Types, and Functions
`intel_dkl_phy_init()` initializes `display->dkl.phy_lock`. `dkl_phy_set_hip_idx()` selects the HIP index for a `struct intel_dkl_phy_reg`. `intel_dkl_phy_read()`, `intel_dkl_phy_write()`, `intel_dkl_phy_rmw()`, and `intel_dkl_phy_posting_read()` perform the corresponding `intel_de` MMIO operation after setting the index.

## Control Flow
Each public accessor acquires `display->dkl.phy_lock`, calls `dkl_phy_set_hip_idx()`, accesses `DKL_REG_MMIO(reg)`, and releases the lock. The HIP selector validates that the decoded TC port is in range and warns/returns early when invalid. RMW delegates the masked update to `intel_de_rmw()`.

## State and Persistence Behavior
The persistent local state is the spinlock in `display->dkl`. Hardware state is the selected HIP index and the target PHY registers. The lock ensures that index selection and data access are an indivisible sequence with respect to other Dekel PHY accesses.

## Dependencies and Integration Points
Dependencies include DRM device/print helpers, `intel_de`, display core, `intel_dkl_phy_regs.h`, and Dekel register encoding helpers such as `DKL_REG_TC_PORT`, `HIP_INDEX_REG`, `HIP_INDEX_VAL`, and `DKL_REG_MMIO`. It integrates with Type-C/PHY programming, PLL/link setup, and low-level display bring-up paths.

## Risks
Without the lock, concurrent PHY accesses could select one bank and read or write another caller's target register. Invalid TC port decoding only warns and returns from HIP selection, so the following access still uses the encoded MMIO register under the lock; callers must pass valid `intel_dkl_phy_reg` values. Accessors assume runtime power and MMIO readiness are handled by the caller.

## Test Signals
Signals include link training on Dekel PHY platforms, no HIP-index race symptoms under concurrent hotplug/modeset, correct PHY register readback, lockdep clean spinlock usage, and no invalid TC port warnings.
