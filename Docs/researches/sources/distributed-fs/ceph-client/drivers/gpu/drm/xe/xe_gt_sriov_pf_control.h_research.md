# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_control.h

Purpose: declares the PF GT SR-IOV control API used by PF provisioning, debugfs, migration, PCI FLR, and GuC event dispatch code.

Important APIs: exposes initialization/restart, pause/resume/stop, save and restore trigger/process/finish/status helpers, FLR prepare/trigger/sync/wait, and conditional `xe_gt_sriov_pf_control_process_guc2pf`. The GuC event function compiles to `-EPROTO` when PCI IOV is disabled.

Control flow: callers initiate operations through synchronous wrappers that generally start an asynchronous state machine then wait for completion, while migration producer/consumer paths use the process/check functions to drive work after ring state changes.

State and persistence: no state is stored in the header; it ties users to `struct xe_gt` and the state definitions in `xe_gt_sriov_pf_control_types.h`.

Dependencies and integration: includes Linux errno/types and forward-declares `struct xe_gt`. It is consumed by PF debugfs for manual stop/pause/resume, PF migration orchestration for save/restore, PCI SR-IOV FLR paths, and GuC event routing.

Risks: the API assumes PF-only callers and valid VFIDs; misuse is mostly caught by implementation asserts. The conditional stub can hide missing PCI IOV support unless callers handle `-EPROTO`.

Test signals: compile with and without `CONFIG_PCI_IOV`, verify all exported functions have matching implementations, and run PF control/migration tests through both debugfs and GuC event paths.
