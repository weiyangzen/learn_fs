# sources/distributed-fs/ceph-client/drivers/media/i2c/ccs/ccs-limits.h

## Purpose
`ccs-limits.h` is the generated public index for CCS capability limits. It defines `struct ccs_limit`, declares `ccs_limits[]`, and assigns stable `CCS_L_*` numeric IDs and offset macros used by `CCS_LIM()` and `CCS_LIM_AT()`.

## Important APIs, Types, and Functions
`struct ccs_limit` stores register, size, flags, and name metadata. `CCS_L_FL_SAME_REG` marks table entries that share a logical limit range. `CCS_L_*` constants cover frame/data descriptors, gain/exposure/timing/PLL constraints, crop/output limits, binning/scaling/HDR/PHY/compression/test-pattern/correction/flash/PDAF/bracketing capabilities, and `CCS_L_LAST`.

## Control Flow
No functions are implemented here. `ccs_module_init()` in `ccs-core.c` consumes the IDs and generated table to build offsets; runtime limit access goes through `ccs_get_limit()` and `ccs_replace_limit()`.

## State and Persistence Behavior
The header has no state. It defines symbolic access to per-device cached limit state. Offset macros such as `CCS_L_FRAME_FORMAT_DESCRIPTOR_OFFSET(n)` and `CCS_L_BINNING_SUB_TYPE_OFFSET(n)` define byte offsets into multi-entry cached limit regions.

## Dependencies and Integration Points
It depends on kernel bits/types and is generated together with `ccs-limits.c` and `ccs-regs.h`. It is included by `ccs.h`, `ccs-core.c`, `ccs-quirk.c`, and register-access code.

## Risks and Edge Cases
Generated numeric IDs are ABI-like inside this driver; reordering without regenerating the table breaks cached-limit access. Offset macros must match the register width and size in `ccs_limits[]`. `CCS_L_LAST` must equal the number of logical limits, not raw table rows.

## Test Signals
Build-time table/header consistency is checked by module init. Probe should be tested with sensors exercising descriptor arrays, same-register split arrays, and optional capability groups so all offset macros are used against real cached data.
