<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_sysfs.c

## Purpose
Creates and removes i915 sysfs entries for L3 parity remapping, GT sysfs, GPU error state, and engine sysfs.

## Important APIs, types, and functions
- `kdev_minor_to_i915()` maps a DRM primary device to `drm_i915_private`.
- `i915_setup_sysfs()` creates L3 parity binary attributes when supported, the `gt` kobject, GPU error sysfs, and engine sysfs.
- `i915_teardown_sysfs()` removes those resources.
- Internal `i915_l3_read()`, `i915_l3_write()`, and `l3_access_valid()` implement L3 parity remap access.

## Control flow
Setup conditionally creates `l3_parity` and `l3_parity_slice_1` binary files for platforms with L3 DPF support, then creates a `gt` sysfs directory and delegates to GPU-error and engine sysfs setup. L3 writes validate alignment/range, allocate or reuse per-slice remap storage under the GEM context lock, copy user data, and mark every GEM context's `remap_slice` bit so remapping is applied on context switch.

## State and persistence
Persistent state includes `i915->l3_parity.remap_info[slice]`, per-context `remap_slice` bits, `dev_priv->sysfs_gt`, GPU error sysfs objects, and engine sysfs entries. L3 remap state remains until driver cleanup or replacement.

## Dependencies and integration points
Depends on Linux sysfs/bin_attribute APIs, DRM device/minor plumbing, GT/RPS/RC6/engine sysfs, GPU error sysfs, L3 parity capability macros, and GEM context lists.

## Risks
L3 sysfs writes are privileged but directly affect context remapping and can leave errors propagated until a future GPU reset, noted as a TODO. Teardown removes both L3 files unconditionally, which sysfs tolerates. `gt` kobject creation failure is warning-only, so downstream sysfs code must handle missing directories.

## Test signals
Sysfs presence/absence on HAS_L3_DPF platforms, aligned and unaligned L3 read/write tests, multi-slice systems, context switch applying remap bits, GPU error sysfs operations, engine sysfs visibility, and probe/remove cleanup checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_sysfs.c -->
