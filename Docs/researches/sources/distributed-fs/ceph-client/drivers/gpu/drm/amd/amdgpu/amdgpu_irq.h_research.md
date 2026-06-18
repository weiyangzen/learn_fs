## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_irq.h

Purpose: defines the AMDGPU interrupt ABI inside the driver: IV decode result shape, IRQ source callback contract, per-client source registry, IRQ domain state, and exported control functions.

Important APIs/types: `AMDGPU_MAX_IRQ_SRC_ID`, `AMDGPU_IRQ_CLIENTID_MAX`, and `AMDGPU_IRQ_SRC_DATA_MAX_SIZE_DW` bound source tables and IV payload. `struct amdgpu_iv_entry` carries decoded IH data such as client/source IDs, ring, VMID/PASID, timestamp, node ID, source data, and raw IV pointer. `struct amdgpu_irq_src` combines `num_types`, `enabled_types`, and `amdgpu_irq_src_funcs`. `struct amdgpu_irq` stores installed IRQ state, source clients, IH rings, work items, IRQ domain, virqs, and reset fields. `node_id_to_phys_map` maps AID/XCD node IDs to physical indices.

Control flow contract: IP blocks allocate and populate `amdgpu_irq_src` objects, call `amdgpu_irq_add_id()`, then use `amdgpu_irq_get()`/`amdgpu_irq_put()` as consumers appear or disappear. Each source must provide `set()` to program hardware interrupt enable state and `process()` to handle decoded IVs. External drivers can request IRQ-domain mappings via `amdgpu_irq_create_mapping()`.

State and persistence: state is per-device and in-memory. `enabled_types` atomic counters are allocated during registration and freed in software teardown. IH rings and virq mappings are owned by `struct amdgpu_irq`.

Dependencies/integration: includes Linux IRQ domain headers, SOC IH client ID headers, and `amdgpu_ih.h`. It is used by display, KMS, RAS blocks, media engines, IH implementation, and KFD.

Risks: the maximum client macro is tied to SOC15 client ID maximum even though the file also carries legacy constants; new hardware client IDs must keep those bounds correct. Source processors must tolerate IV fields that differ across ASIC generations. Missing or wrong `set` callbacks make get/put fail with `-EINVAL`.

Test signals: compilation across DC/non-DC and ASIC variants verifies the shared declarations. Runtime tests should cover IRQ source registration, enable refcounting, IV dispatch, domain mapping for delegated clients, and reset resume replay.
