# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_vf.h

Purpose: declares the VF-side GT SR-IOV API for bootstrap/config/runtime, migration recovery, register emulation, and debug printing.

Important APIs: reset/bootstrap/version query, config query, PF connect, runtime query, migrated event handler, init early/init, recovery pending, GMDID/GUC IDs/LMEM/scheduler group accessors, read32/write32, config/runtime/version printers, wait valid GGTT, and fixup completion count.

Control flow: the expected VF lifecycle is early migration init, GuC bootstrap, config query, PF connect, runtime query, regular register access, and migration recovery handling after migrated events.

State and persistence: no state in the header; state is defined in `xe_gt_sriov_vf_types.h`.

Dependencies and integration: forward-declares GT, register, printer, and firmware version types. Used by VF debugfs, MMIO helpers, CCS/migration, GuC init, and query paths.

Risks: `xe_gt_sriov_vf_lmem` is declared but not implemented in the researched `.c` file, which should be checked against the broader tree. Callers must only use VF APIs on VF devices after required negotiation.

Test signals: link check for all declarations, VF-only assertions, and lifecycle ordering tests.
