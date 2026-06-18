# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_sseu.c

## Purpose
`intel_sseu.c` discovers and reports slice/subslice/EU or Xe_HP DSS topology for i915 GTs, translates hardware fuse registers into `sseu_dev_info`, builds RPCS powergating requests, and copies topology masks to userspace.

## Important APIs, Types, And Functions
Public functions include `intel_sseu_set_info()`, `intel_sseu_subslice_total()`, `intel_sseu_get_hsw_subslices()`, `intel_sseu_copy_eumask_to_user()`, `intel_sseu_copy_ssmask_to_user()`, `intel_sseu_info_init()`, `intel_sseu_make_rpcs()`, `intel_sseu_dump()`, `intel_sseu_print_topology()`, `intel_sseu_print_ss_info()`, and `intel_slicemask_from_xehp_dssmask()`. Internal generation paths parse HSW, CHV, BDW, Gen9, Gen11, Gen12, and Xe_HP fuse layouts.

## Control Flow
`intel_sseu_info_init()` dispatches by graphics version/platform. Each generation helper reads fuse/disable registers, sets topology dimensions, fills slice/subslice/DSS masks and EU masks, computes totals, and records powergating capabilities. Copy helpers linearize masks into query-ioctl byte layouts. `intel_sseu_make_rpcs()` converts requested per-context SSEU powergating into RPCS bits, with special Gen11 subslice rules and perf exclusive-stream override.

## State, Persistence, And Dependencies
Topology persists in `gt->info.sseu` for the GT lifetime. It depends on uncore register reads, platform macros, bitmap helpers, i915 perf state, query UAPI copy routines, DRM printers, and GT register definitions.

## Integration Points
GT init calls topology discovery. Query ioctl code uses copy helpers. Context setup and render powergating use RPCS values. Debugfs and error-state dumping use print/dump helpers. Perf can pin a stable SSEU request.

## Risks
Fuse interpretation is highly generation-specific. Xe_HP collapses hardware concepts into a fake slice 0 for UAPI compatibility. RPCS field limits, Gen11 two-slice translation, and EU pair expansion can be off-by-one or platform-invalid. Userspace-visible mask layout must remain stable.

## Test Signals
Topology query tests, per-platform fuse fixtures, debugfs topology output, perf exclusive stream tests, RPCS programming validation, and regression checks on Gen9/Gen11/Xe_HP systems are high-value signals.
