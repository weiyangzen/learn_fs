# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_virt.h

## Purpose

`amdgpu_virt.h` defines the AMDGPU virtualization data model, feature flags, host/guest shared-memory structures, operation callbacks, SR-IOV helper macros, RLCG register access constants, RAS telemetry state, dynamic critical region metadata, and public virtualization APIs. It is the common header used by bare-metal, passthrough, and SR-IOV VF-aware AMDGPU code.

## Important Types, Macros, And APIs

Capability flags identify SR-IOV-ready VBIOS, IOV enabled, VF mode, passthrough, runtime mode, and VF MMIO protection. RLCG constants define indirect GC/MMHUB read/write operations, scratch-register error bits, VFI commands/status, and function identifier register offsets. `enum amdgpu_sriov_vf_mode` distinguishes bare metal, one-VF, and multi-VF modes.

`struct amdgpu_virt_ops` is the host-interface callback table for full GPU access, init data, reset, mailbox transmission, RAS poison handling, RAS telemetry/CPER/bad-page/critical-region requests, and remote RAS commands. `struct amdgpu_virt_fw_reserve` stores PF2VF, VF2PF, telemetry, and checksum-key pointers. Legacy and current PF2VF/VF2PF message structs describe shared data exchanged with GIM/PF.

`struct amdgpu_virt` is the main device virtualization state: caps, CSA object, interrupt sources, FLR/bad-page work, MM table, ops, VF error ring, shared reserve pointers, generated capability attributes, feature/reg-access flags, dynamic critical region table, delayed VF2PF work and retry interval, multimedia bandwidth limits, autoload ucode id, RLCG lock, debug access mutex, RAS caps/telemetry/cache, bad-page handler data, and XGMI migration flag.

Macros such as `amdgpu_sriov_vf`, `amdgpu_sriov_runtime`, `amdgpu_sriov_fullaccess`, `amdgpu_sriov_reg_indirect_*`, `amdgpu_sriov_ras_*`, and `amdgpu_virt_xgmi_migrate_enabled` centralize mode/feature checks. `DECLARE_ATTR_CAP_CLASS(amdgpu_virt, AMDGPU_VIRT_CAPS_LIST)` uses `amdgpu_utils.h` to declare virtualization capability attributes.

The public APIs cover mode setup, full GPU access, reset handshake, MM table allocation, RAS interrupt/error data, data exchange, dynamic critical region access, debugfs access gating, VF mode query, codec updates, SR-IOV register read/write, firmware skip decisions, pre/post reset, XNACK support, RLCG access, RAS telemetry/CPER/bad-page/critical checks, and remote RAS commands.

## Control Flow And Integration

Most AMDGPU subsystems call the small mode macros to branch around VF restrictions. IP block code uses `amdgpu_sriov_wreg/rreg` when register access may need RLCG. Reset code calls pre/post hooks. Firmware loading asks `amdgpu_virt_fw_load_skip_check()`. Video code imports codec bandwidth limits. RAS code delegates host telemetry through virtualization APIs. VF error reporting uses `vf_errors`.

Dependencies include `amdgv_sriovmsg.h`, `amdgpu_utils.h` through included AMDGPU headers, RAS block enums, video codec types, DRM/BO/ring structures, workqueues, mutexes, and SR-IOV mailbox request enums.

## State, Risks, And Tests

State is broad and cross-subsystem. Risks include ABI drift in PF2VF/VF2PF and RAS telemetry structs, macro checks that miss runtime/full-access distinctions, stale shared-memory pointers after reset, delayed work races, feature flag misinterpretation, non-atomic cap updates, and incorrect RLCG selection causing blocked MMIO or host errors.

Test signals include compile coverage for all helper macros, mode detection results, virt ops null handling, PF2VF/VF2PF struct size/alignment compatibility, data exchange pointer setup for legacy and dynamic regions, debugfs access gating, SR-IOV register access flag selection, RAS capability bit mapping, codec limit propagation, and reset/data-exchange lifecycle ordering.
