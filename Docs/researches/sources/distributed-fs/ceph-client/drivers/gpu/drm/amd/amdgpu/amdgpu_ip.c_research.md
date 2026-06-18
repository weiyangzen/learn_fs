## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ip.c

Purpose: implements common AMDGPU IP block registry, discovery helpers, lifecycle wrappers, and logical-to-physical hardware instance mapping. It is the thin coordination layer used by device setup, power management, KMS queries, and block-specific code that needs to find or control an IP by `enum amd_ip_block_type`.

Important APIs/functions: `amdgpu_ip_map_init()` builds `adev->ip_map` for GC, SDMA, and VCN/JPEG aliases using masks discovered elsewhere; `amdgpu_device_ip_block_add()` appends `struct amdgpu_ip_block_version` entries into `adev->ip_blocks`; `amdgpu_ip_block_suspend()` and `amdgpu_ip_block_resume()` delegate to block `suspend`/`resume` callbacks and update `status.hw`; query helpers include `amdgpu_device_ip_get_ip_block()`, `amdgpu_device_ip_block_version_cmp()`, `amdgpu_device_ip_is_hw()`, and `amdgpu_device_ip_is_valid()`. Clock/power gating wrappers iterate valid blocks and call optional per-IP callbacks.

Control flow: device setup calls `amdgpu_device_ip_block_add()` for ASIC-supported blocks. The add path rejects null versions and silently skips harvested VCN/JPEG blocks based on `adev->harvest_ip_mask`, then logs the version tuple and stores the block. Power and clock gating requests walk the active block array, skip invalid or type-mismatched entries, call optional function pointers, and return the last error. Idle waiting resolves one block by type and invokes `wait_for_idle` if present. Logical instance conversion only translates GC, SDMA0, and VCN/JPEG through `adev->ip_map.dev_inst`; other IPs assume logical equals physical.

State and persistence: all state is in-memory on `struct amdgpu_device`: `ip_blocks[]`, `num_ip_blocks`, `ip_map.dev_inst`, and per-block `status`. There is no durable storage. Suspension/resume mutates `status.hw`, while validity is managed by surrounding device code.

Dependencies/integration: depends on `amdgpu.h`, `amdgpu_ip.h`, `amd_shared.h`, block `amd_ip_funcs`, harvesting flags, and IP discovery masks. KMS uses the query helpers for hardware IP info/counts; JPEG idle power management calls `amdgpu_device_ip_set_powergating_state()`.

Risks: `amdgpu_device_ip_block_add()` does not bounds-check `adev->num_ip_blocks` against `AMDGPU_MAX_IP_NUM`, so callers must enforce list capacity. `amdgpu_logical_to_dev_mask()` assumes mapped instances are nonnegative and small enough for `1 << dev_inst`; malformed masks or uninitialized maps could produce invalid shifts. Clock/power gating returns only the last callback error, potentially hiding earlier failures.

Test signals: boot logs should show expected IP block detection strings and absence of harvested VCN/JPEG. Suspend/resume tests should see `status.hw` transitions and no callback errors. KMS `AMDGPU_INFO_HW_IP_*` queries and JPEG power-gating behavior indirectly validate the registry and type lookup paths.
