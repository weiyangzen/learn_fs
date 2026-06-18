# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_mcr.c

## Purpose
Implements GT multicast/replicated register steering. It identifies non-terminated hardware instances for MCR register ranges and serializes unicast/multicast MMIO access through software and hardware steering locks.

## Important APIs and Functions
- Initialization: `xe_gt_mcr_init_early`, `xe_gt_mcr_init`, and `xe_gt_mcr_set_implicit_defaults`.
- Steering helpers: `xe_gt_mcr_get_nonterminated_steering`, `xe_gt_mcr_get_dss_steering`, and `xe_gt_mcr_steering_info_to_dss_id`.
- Accessors: `xe_gt_mcr_unicast_read_any`, `xe_gt_mcr_unicast_read`, `xe_gt_mcr_unicast_write`, and `xe_gt_mcr_multicast_write`.
- Diagnostics: `xe_gt_mcr_steering_dump`.
- Platform data: many `xe_mmio_range` tables map register ranges to L3BANK, NODE, MSLICE, LNCF, DSS/XeCore, OADDRM/GPMXMT, SQIDI/PSMI, GAM1, INSTANCE0, or implicit steering.

## Control Flow
- Early init selects platform/media/main GT steering tables, initializes `mcr_lock`, and marks INSTANCE0 initialized for early VRAM/CCS probing.
- Normal init computes group/instance targets for each steering type using fuse registers, topology masks, GuC hwconfig, and platform generation rules.
- `xe_gt_mcr_get_nonterminated_steering` finds the table containing a register and returns target group/instance; implicit ranges require no per-access steering.
- Accessors take `mcr_lock`; on MTL+ they also acquire `STEER_SEMAPHORE`, program `MTL_MCR_SELECTOR` or `MCR_SELECTOR`, perform read/write, restore multicast mode for unicast writes, release the hardware semaphore, and unlock.

## State and Persistence
`gt->steering[]` stores range tables, initialized flags, and target group/instance values. `gt->steering_dss_per_grp` records DSS layout. `gt->mcr_lock` serializes all steering changes. Hardware selector/semaphore state is transient but must be restored to multicast-friendly defaults.

## Dependencies and Integration Points
Used by GT init, register save/restore, PAT, MOCS, workarounds, VRAM/flat CCS probing, GuC ADS, OA/EU stall code, and debugfs steering dumps. Depends on platform version, fuse topology, GuC hwconfig, MMIO, and SR-IOV gating.

## Risks and Edge Cases
- MCR registers are unavailable on SR-IOV VFs; accessors assert not VF.
- Missing table entries fall back to steering 0/0 with a warning, which may read terminated instances on new platforms until tables are updated.
- Hardware semaphore acquisition timeout only warns; subsequent access may still race external firmware steering.
- DSS-per-group fallback values are used when GuC hwconfig lacks layout attributes, which is risky on newer platforms.

## Test Signals
- Debugfs `steering` should show expected ranges and targets per platform.
- Register save/restore readback checks exercise MCR reads/writes.
- Platform bring-up should validate MCR table coverage warnings and nonzero reads for known fused configurations.
