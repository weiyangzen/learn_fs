# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_vf_debugfs.c

Purpose: registers VF-specific GT debugfs entries under each GT directory.

Important APIs and functions: `xe_gt_sriov_vf_debugfs_register` creates a `vf` directory and DRM info files for `self_config`, `abi_versions`, and optionally `runtime_regs`. In debug builds it also exposes writable `resfix_stoppers` for migration recovery delay injection.

Control flow: registration asserts VF mode and GT dentry private data, creates `vf`, assigns GT private data, then creates info files backed by VF printer functions.

State and persistence: debugfs entries are volatile. `resfix_stoppers` directly mutates `gt->sriov.vf.migration.debug.resfix_stoppers`, affecting recovery worker wait injection.

Dependencies and integration: depends on DRM debugfs, GT debugfs simple show helper, VF printers, GT types, and SR-IOV mode checks.

Risks: `resfix_stoppers` can intentionally stall migration recovery in debug kernels. Runtime regs are hidden unless debug or debug SR-IOV is enabled.

Test signals: VF debugfs tree enumeration, output of self config/version/runtime files after negotiation, and controlled migration recovery stalls using `resfix_stoppers`.
