# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_4_1_0_offset.h

## Purpose

`mmhub_4_1_0_offset.h` is a generated AMDGPU register offset header for the MMHUB 4.1.0 hardware block. It contains symbolic register names and base-index selectors used by the SOC15 register access macros to read and write memory-management hub registers on matching AMD GPUs.

The file is data-only: it defines no C types, functions, or executable control flow. Its main contract is the numeric register layout. Consumers include it to translate meaningful register names such as `regMMVM_L2_CNTL`, `regMMVM_INVALIDATE_ENG0_REQ`, or `regMMMC_VM_FB_LOCATION_BASE` into MMIO offsets under the `MMHUB` hardware IP.

## Structure and Register Coverage

The header has a conventional include guard, AMD MIT-style license text, and 1,279 macro definitions. There are 640 register offset macros and 639 matching `_BASE_IDX` macros; most registers in this file use base index `0`.

The declared address blocks are:

| Address block | Base address | Main register families |
| --- | ---: | --- |
| `mmhub_dagb_dagbdec` | `0x68000` | `DAGB0_*` and `DAGB1_*` read/write clients, credit, pending, SDP, error, performance, and clock-gating controls |
| `mmhub_pctldec` | `0x69000` | `PCTL_*` power/control, deep-sleep allow, register-save, RENG, status, and performance registers |
| `mmhub_mmutcl2_mmvmsharedpfdec` | `0x69300` | shared PF VM aperture, NB/MMIO, FB offset, cacheable/local address, reset, active function, and UTCL2 status controls |
| `mmhub_mmutcl2_mmvml2pfdec` | `0x69390` | L2 control, status, dummy-page fault, invalidation control, protection fault control/status/address, identity aperture, cache parity, GCR, credit safety |
| `mmhub_mmutcl2_mmvml2prdec` | `0x694d0` | MM VM and UTCL2 performance counter low/high result registers |
| `mmhub_mmutcl2_mmvml2pldec` | `0x69510` | performance counter configuration registers for VM L2 and UTCL2 |
| `mmhub_mmutcl2_mmvmsharedvcdec` | `0x69550` | framebuffer location, AGP aperture, system aperture, and L1 TLB control registers |
| `mmhub_mmutcl2_mmvml2vcdec` | `0x69590` | VM context controls, invalidate engines, page-table base/start/end ranges, and per-PF/VF PTE cache fragment sizes |
| `mmhub_mmutcl2_mmvml2pspdec` | `0x69b10` | PSP/IOMMU-facing translation bypass, host translation, IOMMU control, fault control, and VSCH power status |

Notable offset sequences are intentionally regular and are used by driver-side arithmetic:

- `regMMVM_CONTEXT0_CNTL` through `regMMVM_CONTEXT15_CNTL` are contiguous from `0x0564` to `0x0573`.
- `regMMVM_INVALIDATE_ENG0_*` through `ENG17_*` encode 18 invalidation engines with predictable distances for semaphore, request, acknowledge, and address-range registers.
- `regMMVM_CONTEXT0_PAGE_TABLE_BASE_ADDR_LO32` starts at `0x05cf`, with paired low/high page-table base, start, and end registers for contexts 0-15.
- `regDAGB0_*` and `regDAGB1_*` expose two DAGB slices; the clock-gating consumer uses `regDAGB0_CNTL_MISC2` at `0x00a1` and `regDAGB1_CNTL_MISC2` at `0x023e`.

## Important APIs, Types, and Functions

This header itself exports preprocessor constants, not functions or types. The important "API" surface is:

- `reg<name>` macros: register offsets consumed by `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, and their `_OFFSET` variants.
- `reg<name>_BASE_IDX` macros: base-array selectors used by the generated register-access infrastructure. For this header they are effectively all `0`, so the driver addresses a single MMHUB register segment.
- Naming compatibility with `mmhub_4_1_0_sh_mask.h`: field names in the mask header are used with the offset names here through `REG_SET_FIELD` and `REG_GET_FIELD`.

The primary consumer is `amdgpu/mmhub_v4_1_0.c`, which includes this file and `mmhub_4_1_0_sh_mask.h` together. Important consumer functions include:

- `mmhub_v4_1_0_init()` stores absolute SOC15 offsets into `adev->vmhub[AMDGPU_MMHUB0(0)]`, including page-table base, invalidation engine, context-control, fault-status, fault-control, bank-select, and contexts-disable registers. It also derives `ctx_distance`, `ctx_addr_distance`, `eng_distance`, and `eng_addr_distance` by subtracting adjacent offset macros from this header.
- `mmhub_v4_1_0_gart_enable()` programs GART, system aperture, TLB, L2 cache, VM contexts, identity aperture, and invalidation ranges using MMHUB register names from this header.
- `mmhub_v4_1_0_gart_disable()` disables all VM contexts, L1 TLB, advanced driver model, L2 cache, and L2 control state through these offsets.
- `mmhub_v4_1_0_set_fault_enable_default()` reads and writes `regMMVM_L2_PROTECTION_FAULT_CNTL` to select whether protection faults redirect to default pages or crash/report.
- `mmhub_v4_1_0_get_fb_location()` and `mmhub_v4_1_0_get_mc_fb_offset()` read `regMMMC_VM_FB_LOCATION_BASE` and `regMMMC_VM_FB_OFFSET` and shift/mask those hardware values into memory-controller address units.
- `mmhub_v4_1_0_update_medium_grain_clock_gating()` toggles DAGB slice clock-gating bits by reading and writing `regDAGB0_CNTL_MISC2` and `regDAGB1_CNTL_MISC2`.

`amdgpu/imu_v12_0.c` also includes this header. Its `imu_v12_init_gfxhub_settings()` mirrors selected GFXHUB register programming from current MMHUB values by reading MMHUB aperture and TLB registers such as `regMMMC_VM_FB_LOCATION_BASE`, `regMMMC_VM_FB_LOCATION_TOP`, `regMMMC_VM_FB_OFFSET`, `regMMMC_VM_AGP_*`, `regMMMC_VM_MX_L1_TLB_CNTL`, `regMMMC_VM_SYSTEM_APERTURE_*`, `regMMMC_VM_LOCAL_*`, and `regMMMC_VM_SYSTEM_APERTURE_DEFAULT_ADDR_*`.

## Control Flow

There is no runtime control flow in this header. The indirect control flow is determined by its consumers:

1. `mmhub_v4_1_0_init()` runs during MMHUB setup and converts named offsets into cached absolute addresses in `struct amdgpu_vmhub`.
2. `mmhub_v4_1_0_gart_enable()` writes page-table, aperture, TLB, cache, context, and invalidation registers in a fixed initialization sequence.
3. VM invalidations later use `hub->vm_inv_eng0_sem`, `hub->vm_inv_eng0_req`, `hub->vm_inv_eng0_ack`, and the calculated engine spacing derived from this header.
4. Fault printing and fault policy paths use the L2 protection fault status/control offsets and the companion mask header to decode or update fields.
5. IMU programming may copy already-initialized MMHUB memory aperture state into GFXHUB-related IMU RLC RAM entries.

Because the driver derives register spacing from macro subtraction, control-flow correctness depends on the header preserving the hardware ordering of contexts and invalidation engines.

## State and Persistence Behavior

The header has no mutable state and persists no data. It describes hardware state locations.

The registers it names control persistent device state for the current driver/hardware session:

- VM context state: context enable bits, page-table base addresses, page-table start/end ranges, and context-disable state.
- Aperture state: framebuffer, AGP, system aperture, local FB, local sysmem, default-page, and cacheable DRAM ranges.
- Translation and cache state: L1 TLB, L2 cache, bank selection, GCR, identity aperture, invalidation controls, and PTE fragment-size controls.
- Fault state: L2 protection fault controls, status, fault addresses, dummy-page fault state, and translation fault controls.
- Power/performance state: DAGB and PCTL clock/deep-sleep controls and performance counters.
- Virtualization/IOMMU state: active function, shared virtualization reset, PF/VF fragment sizing, host translation, and IOMMU controls.

Those hardware values are reprogrammed during driver initialization, reset, resume, GART enable/disable, and clock-gating transitions. They are not persisted by the header itself.

## Dependencies

Direct compile-time dependencies are minimal: the header only needs the C preprocessor and its include guard. Practical dependencies come from generated AMDGPU register conventions:

- SOC15 register access macros and per-IP base tables in the AMDGPU driver.
- `mmhub_4_1_0_sh_mask.h` for field masks and shifts used with the offsets.
- `soc15_common.h` and generated hardware-IP metadata for converting `(MMHUB, instance, reg)` into an MMIO address.
- Kernel AMDGPU structures such as `struct amdgpu_device`, `struct amdgpu_vmhub`, and GMC/VM manager fields in consuming code.

The header must remain synchronized with the exact MMHUB 4.1.0 hardware register specification and with the companion mask/default headers for the same IP revision.

## Integration Points

Key integration points are:

- AMDGPU MMHUB function table: `mmhub_v4_1_0_funcs` exposes init, GART enable/disable, fault policy, FB location, MC FB offset, clock-gating, and page-table-base programming hooks. These hooks rely on this header for all MMHUB register addresses.
- VM manager and GART setup: context and page-table macros program VMID 0 for the system domain and VMIDs 1-15 for application contexts.
- VM invalidation infrastructure: invalidation engine offsets and spacing are cached into `adev->vmhub` and used by common VM flush paths.
- Fault reporting: L2 protection fault status and control offsets integrate with `amdgpu_mmhub_client_name()` and the interrupt/fault handling path.
- SR-IOV policy: several consumers skip PF-owned aperture/cache/fault registers when `amdgpu_sriov_vf(adev)` is true, so offset availability must match PF/VF accessibility assumptions.
- IMU/GFX initialization: `imu_v12_0.c` reads MMHUB aperture values to seed GFXHUB-related IMU RLC RAM programming.
- Power management: DAGB and PCTL registers provide the hooks for medium-grain clock gating, light sleep, register save ranges, and performance diagnostics.

## Risks and Maintenance Notes

- Offset drift is high impact. A wrong numeric macro can program the wrong MMIO register, leading to VM faults, hangs, memory corruption, reset failures, or silent performance/power regressions.
- Arithmetic dependencies make ordering part of the ABI. `mmhub_v4_1_0_init()` computes context and engine distances from adjacent macros; inserting, renaming, or reordering generated constants incorrectly can break all VMID or invalidation-engine programming.
- The mask header must match the offset header. `REG_SET_FIELD` and `REG_GET_FIELD` assume the register name and field masks describe the same hardware revision.
- SR-IOV access restrictions are enforced in consumer code, not here. Adding new consumers for PF-owned registers must preserve `amdgpu_sriov_vf()` behavior to avoid illegal VF MMIO accesses.
- Address-unit shifts are consumer-specific. For example, framebuffer and aperture values are shifted by 12, 18, 24, or 44 bits depending on the register. The header does not encode those units; using a macro in the wrong address domain can produce invalid apertures.
- Generated reserved registers (`*_RESERVE*`, `*_RESERVED_*`) should not be treated as available feature controls without hardware documentation.
- The file is under a Ceph-client source mirror path, but its content is AMDGPU DRM driver code. Tests and validation should target the kernel/driver build and hardware behavior, not Ceph filesystem behavior.

## Test Signals

Useful validation signals after changing this header or its generator include:

- Compile coverage for AMDGPU configurations that include `mmhub_v4_1_0.c` and `imu_v12_0.c`; missing or renamed macros should fail at build time.
- Boot/probe logs on MMHUB 4.1.0 hardware with no MMHUB/GMC initialization errors, no IMU RLC RAM programming failures, and no unexpected VM fault storms.
- GART and VM tests that allocate GPU memory, bind page tables, submit commands using VMIDs beyond 0, and verify successful MMHUB invalidation acknowledgements.
- Fault-injection or negative VM tests that exercise `MMVM_L2_PROTECTION_FAULT_STATUS_LO32` decoding and default-page/crash policy toggling.
- Suspend/resume and GPU reset tests, because the named context, aperture, cache, and PCTL/DAGB state must be restored consistently.
- SR-IOV PF/VF smoke tests to confirm VF paths skip inaccessible MMHUB registers while PF-hosted programming still leaves guests functional.
- Clock-gating telemetry or debugfs checks confirming `regDAGB0_CNTL_MISC2` and `regDAGB1_CNTL_MISC2` changes do not regress power or hang behavior.
