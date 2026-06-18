<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/vgpu.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/vgpu.c

### Purpose
`vgpu.c` manages Intel GVT virtual GPU types and vGPU lifecycle. It initializes guest-visible PVINFO resources, derives supported mediated-device types from host aperture/hidden memory capacity, activates and deactivates vGPUs, creates and destroys vGPU runtime subsystems, and implements device-model or GT reset behavior.

### Important APIs, Types, And Functions
Important functions include `populate_pvinfo_page()`, `intel_gvt_init_vgpu_types()`, `intel_gvt_clean_vgpu_types()`, `intel_gvt_activate_vgpu()`, `intel_gvt_deactivate_vgpu()`, `intel_gvt_release_vgpu()`, `intel_gvt_destroy_vgpu()`, `intel_gvt_create_idle_vgpu()`, `intel_gvt_destroy_idle_vgpu()`, `intel_gvt_create_vgpu()`, `intel_gvt_reset_vgpu_locked()`, and `intel_gvt_reset_vgpu()`. Static vGPU type templates live in `intel_vgpu_configs[]`.

### Control Flow
Type initialization computes available low/high graphics memory after host reservations, allocates type and mdev type arrays, filters templates that fit host resources, names types by graphics generation, and publishes them for mediated-device creation. vGPU creation allocates an ID, initializes locks, IDRs, radix trees, PCI config space, MMIO, resource allocation, PVINFO, GTT, opregion, display, submission, scheduling policy, debugfs, opregion data, EDID, and register whitelists. Failure paths unwind in reverse order. Deactivation clears the active bit, waits for running workloads to drain, and stops scheduling. Reset stops scheduling, waits if the vGPU was current, resets submission, optionally invalidates PPGTT/GGTT/resources/MMIO/display/config space, repopulates PVINFO, and clears failsafe or PV notification state for device-model resets.

### State, Persistence, And Dependencies
Persistent state includes `gvt->types`, `gvt->mdev_types`, `gvt->num_types`, `gvt->vgpu_idr`, each vGPU's status bits, scheduling weight, locks, dmabuf/object/page tracking lists and IDRs, D3 and failsafe flags, `resetting_eng`, allocated graphics resources, MMIO image, GTT state, display/opregion state, submission state, and scheduler policy state. Dependencies include GVT resource allocation, GTT/MMIO/display/opregion/submission/scheduling modules, i915 PVINFO definitions, mediated device type structures, and EDID helpers.

### Integration Points
Mediated-device management calls the type and vGPU create/destroy functions. Guest PCI FLR and guest GT reset paths call reset functions. Submission and scheduler code observe status bits and `resetting_eng`. Debugfs and dmabuf helpers are added and removed here as part of vGPU lifecycle.

### Risks
Lifecycle ordering is critical because many subsystems depend on earlier initialization. Reset paths temporarily drop `vgpu_lock` while waiting for workloads, which requires state to remain valid and protected by scheduling stop semantics. DMLR and D3 transitions intentionally treat PPGTT and PV notification state differently. Type capacity calculations must avoid exposing configurations that exceed low/high GM or fence resources.

### Test Signals
High-value tests include type enumeration on different aperture sizes, create failure injection at each initialization step, activate/deactivate with in-flight workloads, vGPU release versus destroy ordering, DMLR after D3 and non-D3 states, full and per-engine GT reset, EDID/opregion setup on BDW/BXT versus newer ports, and leak checks for IDRs, debugfs, dmabufs, GTT, and submission resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/vgpu.c -->
