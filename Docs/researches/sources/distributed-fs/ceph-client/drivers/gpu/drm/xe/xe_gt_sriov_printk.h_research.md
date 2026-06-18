# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_printk.h

Purpose: provides GT-scoped SR-IOV logging macros that include tile and GT context in messages.

Important APIs: `xe_gt_sriov_err`, `notice`, `info`, `dbg`, and `dbg_verbose`. Verbose debug compiles to real debug output only under `CONFIG_DRM_XE_DEBUG_SRIOV`; otherwise it typechecks the GT pointer without emitting code.

Control flow: macros format messages through tile and GT print helpers before forwarding to device-level `xe_sriov_*` log macros.

State and persistence: no state; it standardizes log prefixes for PF/VF SR-IOV code.

Dependencies and integration: includes `xe_gt_printk.h` and `xe_tile_sriov_printk.h`. Used throughout PF/VF control, migration, policy, monitor, and service files.

Risks: macro arguments must be side-effect safe, especially for verbose logs that compile out. Format nesting must stay compatible with tile/device logging macros.

Test signals: build with and without debug SR-IOV, verify log prefixes include PF/VF mode, tile, and GT identity.
