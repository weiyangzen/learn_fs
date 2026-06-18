# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_service.h

Purpose: declares PF GT SR-IOV relay service APIs for initialization, runtime refresh/printing, and VF request processing.

Important APIs: `xe_gt_sriov_pf_service_init`, `xe_gt_sriov_pf_service_update`, `xe_gt_sriov_pf_service_print_runtime`, and conditional `xe_gt_sriov_pf_service_process_request` with a `-EPROTO` stub when PCI IOV is disabled.

Control flow: PF GT init calls init, lifecycle/update paths call update after registers are valid, GuC relay dispatch calls process_request, and debugfs calls print.

State and persistence: state is defined in `xe_gt_sriov_pf_service_types.h`.

Dependencies and integration: forward-declares `struct xe_gt` and `struct drm_printer`; includes Linux errno/types.

Risks: request processing must be gated to PF devices and PCI IOV builds; callers need to size response buffers according to GuC relay ABI.

Test signals: no-IOV build stubs, relay request dispatch with invalid action/length, and runtime debugfs output after update.
