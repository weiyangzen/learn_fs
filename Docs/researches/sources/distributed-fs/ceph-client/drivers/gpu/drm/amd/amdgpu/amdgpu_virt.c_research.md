# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_virt.c

## Purpose

`amdgpu_virt.c` implements common AMDGPU virtualization support for passthrough and SR-IOV VF operation. It detects virtualization mode, installs ASIC-specific virt ops, negotiates full GPU access and reset handshakes, manages PF2VF/VF2PF shared-memory data exchange, handles dynamic critical regions, reserves RAS bad pages, provides indirect register access through RLCG/VFI, exposes SR-IOV video codec limits, and proxies RAS telemetry/CPER/remote commands to the host.

## Important APIs And Functions

Basic operation wrappers include `amdgpu_virt_request_full_gpu()`, `amdgpu_virt_release_full_gpu()`, `amdgpu_virt_reset_gpu()`, `amdgpu_virt_request_init_data()`, `amdgpu_virt_ready_to_reset()`, and `amdgpu_virt_wait_reset()`. These call installed `virt->ops` callbacks and update runtime/no-hw-access caps. `amdgpu_virt_init_setting()` applies VF display/power defaults, while `amdgpu_virt_init()` detects VF/passthrough state and selects VI/SOC15/NV virt ops.

Data exchange is handled by `amdgpu_virt_init_data_exchange()`, `amdgpu_virt_exchange_data()`, `amdgpu_virt_read_pf2vf_data()`, `amdgpu_virt_write_vf2pf_data()`, and delayed work `amdgpu_virt_update_vf2pf_work_item()`. PF2VF checks version and checksum, imports feature flags, register access flags, multimedia bandwidth limits, UUID, and RAS caps. VF2PF writes driver version, memory usage, firmware versions, dummy page, optional MES info, and checksum. Retry failures can schedule reset when RAS interrupts or retry limits indicate stale data.

Dynamic critical region support is in `amdgpu_virt_init_critical_region()` and `amdgpu_virt_get_dynamic_data_info()`. It reads a host-provided init-data header from VRAM, validates VRAM bounds, signature, checksum, and per-table sizes, records table offsets/sizes, reserves the critical VRAM region, and lets callers copy dynamic table contents.

RAS support includes bad-page data setup/reservation, `amdgpu_virt_get_ras_capability()`, telemetry count requests, CPER dump requests, post-reset telemetry refresh, critical-region hit checks, bad-page requests, and remote RAS command forwarding. It ratelimits host messages and caches telemetry so reads can continue during reset.

Register access support includes `amdgpu_virt_get_rlcg_reg_access_flag()`, `amdgpu_virt_rlcg_reg_rw()`, `amdgpu_virt_rlcg_vfi_reg_rw()`, `amdgpu_sriov_wreg()`, and `amdgpu_sriov_rreg()`. These route protected GC/MMHUB register reads/writes through legacy scratch registers or newer VFI registers when SR-IOV access restrictions require it, protected by `rlcg_reg_lock`.

## Control Flow, State, And Integration

Initialization detects VF state from ASIC-specific IOV function registers. If SR-IOV is present, ASIC-specific ops are installed and optional GPU init data is requested. Early data exchange may read PF2VF data from BIOS or dynamic critical region; later, reserved VRAM mappings are used for ongoing PF2VF/VF2PF updates. Reset paths stop data exchange and set MP1 FLR state before reset, then adjust GC/MES readiness afterward.

Persistent runtime state lives in `adev->virt`: caps, ops, mm table, error buffer, shared reserve pointers, feature/reg-access flags, dynamic critical region metadata, delayed VF2PF work, multimedia limits, RLCG lock, RAS caps/cache/rate limits, bad page handler data, and migration flags. GPU-visible state includes reserved VRAM PF2VF/VF2PF/telemetry areas and optional MM table BO.

Dependencies include `amdgpu_ras`, reset domains, DPM, VI/SOC15/NV virt ops, firmware info from many IP blocks, TTM VRAM manager, PSP/RLCG register control, Xen/hypervisor detection, CPER ring helpers, and SR-IOV message definitions.

## Risks And Test Signals

Risks are high because this file gates hardware access in virtualized environments. Key risks include checksum or size validation mistakes for host-provided shared memory, delayed work running across teardown/reset, missed cancellation of data exchange, incorrect cap transitions between full-access/runtime modes, RLCG timeouts or stale GRBM shadow registers, bad-page reservation leaks, trusting telemetry sizes/checksums, null virt ops, firmware skip list drift, and ABI drift with `amd_sriovmsg.h`.

Test signals include SR-IOV detection across supported ASICs, passthrough detection, full GPU request/release/reset callback failures, PF2VF v1/v2 checksum and size validation, VF2PF field/checksum generation, delayed update retry/reset behavior, dynamic critical region signature/checksum/bounds failures, bad page import/reservation, RLCG/VFI read/write paths and timeout errors, firmware skip decisions per MP0 version, video codec limit updates, RAS caps and telemetry block mapping, CPER dump ring writes, critical-region hit queries, and reset pre/post behavior.
