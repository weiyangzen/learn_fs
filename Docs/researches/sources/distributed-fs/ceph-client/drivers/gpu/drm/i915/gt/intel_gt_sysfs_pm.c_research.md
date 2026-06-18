# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_sysfs_pm.c

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_sysfs_pm.c

### Purpose
`intel_gt_sysfs_pm.c` implements sysfs power-management and frequency attributes for GTs, including RC6 residency, RPS frequencies and thresholds, SLPC controls, throttle reason status, media frequency factor, media RP0/RPn frequencies, and default values.

### Important APIs, Types, And Functions
The public entry point is `intel_gt_sysfs_pm_init()`. Important helpers include generic read/write dispatchers for parent versus per-GT objects, RC6 residency readers, RPS frequency show/store functions, SLPC `ignore_eff_freq` and power-profile handlers, throttle reason bool attributes, media frequency factor show/store, media RP0/RPn pcode readers, RPS threshold show/store functions, and default attribute readers.

### Control Flow
Initialization creates RC6 groups when PM and RC6 are supported, creates Gen6+ RPS frequency files, optional VLV efficient-frequency files, optional RPS thresholds when GuC SLPC is not used, and per-GT-only files for punit frequency, SLPC controls, throttle reasons, media ratio mode, and `.defaults`. Legacy parent attributes aggregate across GTs: frequency reads return the maximum across GTs, RC6 reads return the minimum, and writes apply to every GT. Per-GT attributes operate on the specific `gtN`.

### State, Persistence, And Dependencies
State read/written includes `gt->rc6.enabled`, RC6 residency counters, RPS requested/actual/min/max/boost frequencies, RPS up/down thresholds, `gt->defaults`, GuC SLPC power profile and media ratio mode, performance limit reason registers, pcode fused media frequencies, and runtime PM-protected MMIO state. Dependencies include sysfs, kobjects, i915 sysfs compatibility, RPS/RC6, GuC SLPC, pcode, GT registers, runtime PM, and throttle reason masks.

### Integration Points
Called by `intel_gt_sysfs_register()` for both legacy and per-GT locations. Userspace power management tools and tests consume these ABI files. It bridges old `gt_*` device attributes and new `rps_*` per-GT attributes.

### Risks
ABI compatibility drives non-obvious aggregate semantics. Store operations through legacy parent files update all GTs and can partially fail. Input parsing must reject invalid SLPC profile strings and unsupported media ratio factors. Runtime PM must cover MMIO reads. Conditional creation must match hardware capabilities to avoid dead sysfs files.

### Test Signals
Sysfs ABI tests should cover root and media GT layouts, legacy parent aggregation, min/max frequency writes, boost frequency, RPS thresholds with and without SLPC, RC6 residency, throttle reason files, media frequency factor scaling, media RP0/RPn reads, invalid stores, and `.defaults` contents.
