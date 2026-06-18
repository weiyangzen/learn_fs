# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vcn.c

## Purpose

`amdgpu_vcn.c` implements common support for modern VCN video decode/encode blocks: firmware lookup, BO/shared-memory setup, suspend/resume preservation, power profile and power gating coordination, decode/encode/unified ring tests, firmware log debugfs, scheduler-mask debugfs, RAS poison dispatch, SR-IOV-aware RAS handling, sysfs reset mask, per-instance engine reset, and IP state dumps.

## Important APIs And Functions

`amdgpu_vcn_early_init()` binds each VCN instance to firmware, supporting shared or per-instance firmware. `amdgpu_vcn_sw_init()` initializes per-instance mutexes, counters, idle work, DPG indirect SRAM mode, a Steam Deck BIOS quirk, unified queue selection for VCN4+, firmware version logging, VCPU BO sizing, firmware shared memory layout selection for VCN3/4/5, optional firmware log space, and optional DPG SRAM BO. `amdgpu_vcn_sw_fini()` releases DPG SRAM, saved BOs, VCPU BO, rings, firmware, register dump buffers, and mutexes.

Suspend/resume helpers save VCPU BOs unless RAS/DPC recovery requires a clean reload. `amdgpu_vcn_get_profile/put_profile()` toggle the video DPM power profile while any VCN instance is ungated. `amdgpu_vcn_ring_begin_use/end_use()` maintain submission counters, cancel/schedule idle work, transition power state, and pause/unpause DPG for pre-unified queue engines.

Ring tests include direct decode register writes, software decode ring END packets, decode message IBs, software decode buffer IBs, encode initialize/close-session messages, and unified queue tests that combine encode/decode paths depending on IP version. `amdgpu_vcn_unified_ring_ib_header()` and checksum helpers build the single-queue packet wrapper.

RAS/debug interfaces include `amdgpu_vcn_process_poison_irq()`, `amdgpu_vcn_ras_sw_init()`, `amdgpu_vcn_ras_late_init()`, `amdgpu_vcn_psp_update_sram()`, firmware log init/read debugfs, VCN scheduler mask debugfs, reset mask sysfs, and register dump init/dump/print. `amdgpu_vcn_ring_reset()` resets whole VCN instances for non-unified queues by stopping schedulers, invoking the IP reset callback, retesting rings, forcing fence completion, and restarting schedulers.

## Dependencies And Integration

The file depends on firmware loading, AMDGPU BO/IB/job/ring APIs, DRM scheduler, DPM power profiles, IP version helpers, PSP firmware loading, debugfs, sysfs, RAS core, reset domains, and SR-IOV virtualization callbacks. It is designed to be called by IP-version-specific VCN block code that fills register addresses, ring callbacks, reset callbacks, DPG callbacks, and RAS IRQ sources.

## State, Risks, And Tests

State is per VCN instance in `adev->vcn.inst[]`: firmware, VCPU BO, shared memory offsets, rings, IRQs, DPG SRAM, pause state, counters, mutexes, current power state, delayed idle work, firmware version, queue mode, and reset callback. Device-level state tracks instance masks, RAS, register dump buffers, supported reset mask, caps, and workload profile active state.

Risks include firmware shared layout mismatches across VCN generations, incorrect per-instance firmware release when firmware is shared, DPG pause races with encode submissions, idle power gating while counters or fences are active, debugfs log pointer validation errors, sysfs/debugfs updates racing ring scheduling, reset not restarting schedulers on failure paths, and SR-IOV poison handling when virtualization ops are absent.

Test signals include per-IP firmware naming, per-instance firmware mode, BO/shared memory sizing for VCN3/4/5, firmware log enable/read wraparound, begin/end power profile nesting, DPG pause behavior, encode/decode/unified ring tests, SR-IOV ring-test skips, RAS poison dispatch in PF and VF modes, sysfs reset mask creation/removal, scheduler mask debugfs set/get, per-instance reset failure paths, and register dump output for powered/unpowered instances.
