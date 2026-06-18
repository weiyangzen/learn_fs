<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mes_userqueue.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mes_userqueue.h

Purpose: declares the MES-backed userqueue function table.

Important APIs: includes `amdgpu_userq.h` and exports `extern const struct amdgpu_userq_funcs userq_mes_funcs`.

Control flow and state: no logic or state. The exported table is implemented in `mes_userqueue.c` and selected by userqueue manager setup when MES is the backend.

Dependencies and integration points: requires common userqueue type definitions. The function table provides MQD create/destroy, map/unmap, detect/reset, preempt, and restore hooks to generic userqueue code.

Risks and test signals: risks are declaration/implementation drift or backend selection without MES support. Compile/link and successful user queue lifecycle through `userq_mes_funcs` validate the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mes_userqueue.h -->
