# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hwio.h

## Purpose
Defines MDP TOP register offsets and DP PHY interface-selection bit masks shared by DPU top-level hardware code.

## Important APIs, types, and functions
- Register offsets include interrupt status/enable/clear registers, split-display controls, danger/safe status, watchdog timer controls/load values, clock controls/status, interface reset/select, MDP output control, vsync select, DCE select, and DP PHY interface selection.
- `MDP_DP_PHY_INTF_SEL_*` masks identify INTF and PHY mapping fields.
- `MDP_PERIPH_TOP0` and `MDP_PERIPH_TOP0_END` mark snapshot split points for newer top-register layout.

## Control flow
The file is declarative. Callers use the offsets with `DPU_REG_READ` and `DPU_REG_WRITE`.

## State and persistence
No state is stored here; the macros address hardware registers whose state is controlled elsewhere.

## Dependencies and integration points
Includes `dpu_hw_util.h` for bit helpers. `dpu_hw_top.c`, `dpu_kms.c` snapshot code, interrupt code, and other top-level register users depend on these offsets.

## Risks
Incorrect offsets affect low-level hardware programming globally. Snapshot split markers must match MDSS generation layout or register dumps become incomplete or invalid. DP PHY field masks must stay aligned with hardware documentation.

## Test signals
Runtime tests include interrupt handling, split-display operation, danger/safe status reads, watchdog/vsync programming, DP PHY routing, and display snapshot register coverage.
