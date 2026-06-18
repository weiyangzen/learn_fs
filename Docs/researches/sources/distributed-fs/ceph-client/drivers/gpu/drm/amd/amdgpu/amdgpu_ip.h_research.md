## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ip.h

Purpose: declares AMDGPU's hardware IP taxonomy, version encoding helpers, logical instance map, and IP block lifecycle/query API. It is the shared contract between ASIC setup code, IP block implementations, and cross-cutting callers such as KMS, power management, and recovery.

Important APIs/types: `enum amd_hw_ip_block_type` names hardware-discovery IPs and aliases `VCN_HWIP`/`JPEG_HWIP` to `UVD_HWIP` for discovery compatibility. `IP_VERSION_FULL()`, `IP_VERSION()`, and extractor macros encode major/minor/revision/variant/subrevision into a packed 32-bit value. `struct amdgpu_ip_map_info` stores logical-to-device instance mappings and function pointers. `struct amdgpu_ip_block_status`, `struct amdgpu_ip_block_version`, and `struct amdgpu_ip_block` describe an IP's runtime state, static version, callback table, and owning device.

Control flow contract: device code fills IP blocks with `amdgpu_device_ip_block_add()`, then calls block lifecycle functions through the function table referenced by `amdgpu_ip_block_version.funcs`. Consumers should use `amdgpu_device_ip_get_ip_block()` and validity/hardware helpers rather than walking `adev->ip_blocks` directly where possible. Clock/power gating and idle wrappers provide type-based broadcast or lookup.

State and persistence: the header defines only in-memory device state. `status.valid`, `status.sw`, `status.hw`, `status.late_initialized`, and `status.hang` are status bits used by initialization, runtime PM, reset, and diagnostics; the header does not prescribe persistence across driver unload.

Dependencies/integration: includes `amd_shared.h` for shared IP block and callback definitions and forward-declares `struct amdgpu_device`. The IP version macros are widely used by version-specific code such as ISP and MES firmware naming.

Risks: the enum includes fixed maximums (`HWIP_MAX_INSTANCE`, `HW_ID_MAX`) that must stay aligned with discovery data. Aliasing JPEG to VCN/UVD is intentional but easy to misread when writing code that needs a separate JPEG IP block versus an IP-discovery hardware ID. Callers of logical mapping functions must handle unmapped entries defensively.

Test signals: compile-time coverage should catch mismatched prototypes. Runtime validation comes from IP discovery, ASIC version selection, KMS hardware info queries, and successful load/unload across ASICs with harvested or multi-instance IPs.
