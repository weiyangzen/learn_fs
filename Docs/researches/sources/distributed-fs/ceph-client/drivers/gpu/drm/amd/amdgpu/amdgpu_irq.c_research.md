## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_irq.c

Purpose: implements the generic AMDGPU interrupt subsystem: PCI IRQ/MSI setup, interrupt handler entry, IH ring dispatch, source registration, enable refcounting, reset-time state replay, and IRQ-domain forwarding for child components.

Important APIs/functions: `amdgpu_irq_init()` allocates one PCI IRQ vector, registers `amdgpu_irq_handler()`, initializes work handlers for IH1/IH2/soft IH, and marks IRQ state installed. `amdgpu_irq_add_id()` installs a `struct amdgpu_irq_src` under client/source IDs and allocates per-type atomic enable counters. `amdgpu_irq_get()`/`amdgpu_irq_put()` refcount interrupt enables and call `amdgpu_irq_update()` on 0-to-1 or 1-to-0 transitions. `amdgpu_irq_dispatch()` decodes IV entries, routes to registered source processors, IRQ domains, or AMDKFD fallback. `amdgpu_irq_gpu_reset_resume_helper()` restores MSI-X for VF/passthrough and reapplies every source state.

Control flow: hardware IRQs enter `amdgpu_irq_handler()`, which processes the primary IH ring and marks runtime PM activity when handled, then invokes fatal RAS interrupt handling. Secondary IH rings are processed from workqueue callbacks. Dispatch decodes the IV, validates client/source IDs, forwards legacy/ISP virqs through `generic_handle_domain_irq()` when mapped, otherwise calls `src->funcs->process()`. If no driver source claims the IV, AMDKFD receives it.

State and persistence: persistent runtime state lives in `adev->irq`: installed IRQ number, MSI status, client source arrays, atomic enable counters, IH rings, work items, IRQ domain, virq mappings, and reset-related fields. No disk persistence exists. The enable counters are the source of truth for whether `src->funcs->set()` should enable or disable hardware.

Dependencies/integration: depends on PCI IRQ APIs, Linux IRQ domains, DRM vblank, PM runtime, IH decode/process helpers, RAS fatal handling, AMDKFD interrupt delivery, and optional DC IRQ code. KMS vblank enable/disable uses `amdgpu_irq_get/put()` on `adev->crtc_irq`; NBIO/JPEG RAS late init enables IRQ sources through this subsystem.

Risks: incorrect source registration or `num_types` sizing can produce invalid refcount access. `amdgpu_irq_put()` guards RMA state specially and warns on underflow, but callers still need balanced get/put. Dispatch deliberately forwards unhandled IVs to KFD, so source processors should return nonzero only when fully handled. IRQ domain mask/unmask callbacks are stubs, making mapped child IRQ behavior dependent on simple handling.

Test signals: probe should allocate/free vectors cleanly with MSI enabled or disabled by module parameter. Interrupt tests should verify vblank, hotplug, RAS, IH1/IH2/soft delegation, reset resume state replay, and KFD interrupt delivery. Fault injection should exercise invalid client/source IDs without crashes.
