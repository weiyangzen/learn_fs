# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_3_0_2_offset.h

## Purpose

`mmhub_3_0_2_offset.h` is a generated AMDGPU ASIC register-offset contract for the MMHUB 3.0.2 hardware block. It maps named MMHUB registers to SOC15 register indices and matching base-index macros so the driver can program memory-hub virtual memory, GART aperture, TLB/cache, invalidation, protection-fault, frame-buffer aperture, power-control, and diagnostic registers without embedding numeric offsets in C code.

The file is data-only preprocessor surface. It contains AMD's permissive license text, an include guard, hardware address-block comments, and `#define` pairs. There are no C functions, structs, enums, local variables, branches, or runtime algorithms in this header. Its behavior comes from consumers expanding macros such as `regMMVM_L2_CNTL` and `regMMVM_L2_CNTL_BASE_IDX` through AMDGPU SOC15 MMIO accessors.

## Exported API Surface

The exported API is the macro namespace guarded by `_mmhub_3_0_2_OFFSET_HEADER`. The header defines 1,347 macros total: one include-guard macro plus 673 register offset macros and 673 matching `*_BASE_IDX` macros. Every base-index macro in this file is `0`, which means MMHUB 3.0.2 consumers address these registers through SOC15 MMHUB base segment 0.

Important register families include:

- `regDAGB0_*` and `regDAGB1_*`: data/address gateway block registers for read and write clients, virtual channels, credits, pending status, FIFO state, clock-gating controls, SDP arbitration/credits, fatal-error status, and performance counters.
- `regPCTL_*`: MMHUB power/deepsleep, state-control, register-save, RENG RAM, status, and performance-counter registers.
- `regMMMC_VM_MX_L1_*`: L1 TLB status, performance-counter configuration, performance-counter result, and `regMMMC_VM_MX_L1_TLB_CNTL`.
- `regMMVM_L2_*`, `regMMUTCL2_*`, and `regMMVML2_*`: VM L2 control/status, dummy page fault, invalidation control, protection-fault control/status/default address, identity aperture, cache parity, GCR, clock/busy control, PTE-cache dump, credit-safety, and translation-assist registers.
- `regMMVM_CONTEXT0_*` through `regMMVM_CONTEXT15_*`: VM context control and 64-bit page-table base/start/end ranges for 16 VM contexts.
- `regMMVM_INVALIDATE_ENG0_*` through `regMMVM_INVALIDATE_ENG17_*`: invalidate-engine semaphore, request, acknowledgement, and address-range registers for 18 invalidation engines.
- `regMMMC_VM_L2_PERFCOUNTER*` and `regMMUTCL2_PERFCOUNTER*`: VM L2 and MMUTCL2 performance-counter configuration and result registers.
- `regMMMC_VM_FB_SIZE_OFFSET_VF0` through `regMMMC_VM_FB_SIZE_OFFSET_VF15`: per-VF frame-buffer size/offset registers used by virtualization-facing flows.
- `regMMMC_VM_*`: shared VM aperture and memory-routing registers for FB offset, system aperture default, steering, cacheable/local memory ranges, AGP range, FB location, and address translation control.
- `regMMUTCL2_TRANSLATION_BYPASS_BY_VMID`, `regMMUTC_GPUVA_VMID_TRANSLATION_ASSIST_CNTL`, and `regMMUTC_TRANSLATION_FAULT_CNTL*`: PSP/translation-assist and translation-fault controls.

## Address Blocks

The source preserves the generated hardware address-block layout:

| Address block | Base address | Line range | Role |
| --- | ---: | ---: | --- |
| `mmhub_dagbdec` | `0x68000` | 28-578 | DAGB0/DAGB1 read/write clients, credits, pending/FIFO state, SDP controls, fatal-error status, and DAGB performance counters |
| `mmhub_pctldec` | `0x68e00` | 580-698 | MMHUB deepsleep/power control, register-save ranges, RENG RAM access, status, and PCTL performance counters |
| `mmhub_l1tlb_mmvml1pfdec` | `0x69600` | 700-714 | L1 TLB status registers |
| `mmhub_l1tlb_mmvml1pldec` | `0x69670` | 716-728 | L1 TLB performance-counter configuration |
| `mmhub_l1tlb_mmvml1prdec` | `0x69690` | 730-736 | L1 TLB performance-counter result registers |
| `mmhub_mmutcl2_mmvml2pfdec` | `0x69a00` | 738-828 | VM L2 controls, fault registers, invalidation control, identity aperture, cache/GCR controls, dump, translation assist, and credit-safety registers |
| `mmhub_mmutcl2_mmvml2vcdec` | `0x69b00` | 830-1272 | VM context controls, invalidate-engine sem/request/ack/address ranges, page-table base/start/end pairs, and per-context PTE-cache fragment sizes |
| `mmhub_mmutcl2_mmvml2pldec` | `0x69e90` | 1274-1304 | VM L2 and MMUTCL2 performance-counter configuration |
| `mmhub_mmutcl2_mmvml2prdec` | `0x69ee0` | 1306-1316 | VM L2 and MMUTCL2 performance-counter results |
| `mmhub_mmutcl2_mmvmsharedhvdec` | `0x69f30` | 1318-1352 | Per-VF FB size/offset registers |
| `mmhub_mmutcl2_mmvmsharedpfdec` | `0x6a140` | 1354-1392 | PF/shared FB offset, system aperture default, steering, memory power, cacheable/local memory ranges, APT, clock/busy, noalloc, harvest, and fault-status registers |
| `mmhub_mmutcl2_mmvmsharedvcdec` | `0x6a1b0` | 1394-1412 | FB location, AGP aperture, system aperture, and L1 TLB control |
| `mmhub_mmutcl2_mmvml2pspdec` | `0x6a850` | 1414-1423 | Translation bypass, GPUVA/VMID translation assist, and translation-fault controls |

The numeric macro values are SOC15 register indices used by AMDGPU register helpers. They are not byte offsets for direct CPU dereference.

## Control Flow

This header has no runtime control flow. The effective flow is preprocessor and MMIO-helper driven:

1. `drivers/gpu/drm/amd/amdgpu/mmhub_v3_0_2.c` includes this header with `mmhub_3_0_2_sh_mask.h`.
2. The C file passes offset macros such as `regMMVM_CONTEXT0_PAGE_TABLE_BASE_ADDR_LO32`, `regMMVM_INVALIDATE_ENG0_REQ`, `regMMVM_L2_CNTL`, and `regMMMC_VM_FB_LOCATION_BASE` to `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, and their `_OFFSET` variants.
3. Field macros from the matching sh/mask header are used by `REG_SET_FIELD` and `REG_GET_FIELD` to build or decode register values.
4. Runtime sequencing is implemented by `mmhub_v3_0_2.c`, not this header. That sequencing initializes GART page-table registers, system aperture/default/fault registers, L1 TLB and L2 cache controls, VM context controls, invalidation engines, fault policy, and FB-location access.

The consumer also derives stride constants by subtracting adjacent offset macros, for example context-control distance, page-table-address distance, invalidate-engine request distance, and invalidate-engine address-range distance. This makes contiguous layout correctness part of the header's ABI.

## State and Persistence Behavior

The file itself stores no software state and creates no persistent data. It names hardware state that persists in MMHUB registers until reset, power transition, or explicit reprogramming:

- VM context page-table base/start/end registers hold GART and per-VM address translation configuration.
- VM context control registers hold enablement, page-table depth, block size, and fault policy bits.
- L1 TLB and L2 cache registers hold translation-cache enablement, invalidation behavior, bank selection, fragment sizes, and identity-aperture behavior.
- Invalidate-engine semaphore, request, acknowledgement, and address-range registers represent transient synchronization state for TLB/cache invalidation.
- Protection-fault status/address/default-address registers expose fault state and define the dummy/default page used by fault handling.
- FB, AGP, system aperture, local FB, local system-memory, cacheable DRAM, and FB offset/location registers define memory routing and aperture state.
- PCTL, clock/busy, deepsleep, and memory-power registers influence power-management behavior.
- Performance-counter registers provide diagnostic configuration and sampled counts.
- Per-VF FB size/offset registers are virtualization-sensitive state used to partition or remap frame-buffer resources.

Because all state is hardware state, a wrong offset can silently read or write the wrong register and cause VM faults, bad aperture routing, display/GPU hangs, invalid SR-IOV isolation, or resume failures.

## Dependencies

Direct dependencies are intentionally minimal:

- The include guard `_mmhub_3_0_2_OFFSET_HEADER` prevents duplicate macro definition.
- Consumers depend on `mmhub/mmhub_3_0_2_sh_mask.h` for matching field shifts and masks.
- `amdgpu/mmhub_v3_0_2.c` depends on these macros through AMDGPU SOC15 helper APIs from the surrounding driver, including `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_SOC15_OFFSET`, and `WREG32_SOC15_OFFSET`.
- Field construction and decoding depend on shared helper macros such as `REG_SET_FIELD` and `REG_GET_FIELD`.
- Runtime data used with these offsets comes from AMDGPU structures such as `struct amdgpu_device`, `struct amdgpu_vmhub`, GMC/GART fields, VM manager settings, SR-IOV mode checks, and MMHUB client-info tables.

The header itself has no Linux type, compiler-extension, allocator, locking, or runtime library dependency.

## Integration Points

The observed direct include site is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v3_0_2.c`. That file wires this generated register map into the AMDGPU MMHUB function table through `mmhub_v3_0_2_funcs`.

Key integration paths:

- `mmhub_v3_0_2_init()` converts selected offsets into absolute MMHUB register addresses stored in `adev->vmhub[AMDGPU_MMHUB0(0)]`, including context-0 page-table base, invalidation engine 0 sem/request/ack, context control, L2 protection fault status/control, and reserved CID register addresses.
- `mmhub_v3_0_2_setup_vm_pt_regs()` writes page-table base low/high registers using `regMMVM_CONTEXT0_PAGE_TABLE_BASE_ADDR_*` plus `hub->ctx_addr_distance * vmid`.
- `mmhub_v3_0_2_gart_enable()` sequences GART aperture, system aperture, TLB, L2 cache, system-domain, identity-aperture, VMID, and invalidation setup using offsets from this header.
- `mmhub_v3_0_2_gart_disable()` clears VM context controls and disables L1 TLB and L2 cache registers.
- `mmhub_v3_0_2_set_fault_enable_default()` writes L2 protection-fault policy registers, skipping inaccessible registers for SR-IOV VFs.
- `mmhub_v3_0_2_get_fb_location()` and `mmhub_v3_0_2_get_mc_fb_offset()` read FB location/offset registers from this map.
- Fault logging uses `regMMVM_L2_PROTECTION_FAULT_STATUS` for the register address and matching sh/mask macros to decode CID, RW, and fault-class bits.

The file also integrates indirectly with VM invalidation, page-fault handling, GART setup, memory aperture setup, and SR-IOV policy via the generic AMDGPU VMHUB/MMHUB abstraction.

## Risks and Edge Cases

- Register-offset drift between MMHUB generations is high risk. Neighboring headers such as `mmhub_3_0_0_offset.h`, `mmhub_3_0_1_offset.h`, `mmhub_3_3_0_offset.h`, and `mmhub_4_1_0_offset.h` have different offsets and sometimes different base indices; mixing generations can program wrong hardware.
- Base-index assumptions are fragile. This file's `*_BASE_IDX` values are all `0`, while nearby generations may use other base indices. Consumers should continue using the generated base-index macros rather than baking in `0`.
- Stride derivation depends on contiguous register layout. `mmhub_v3_0_2_init()` subtracts adjacent macro values to derive VM context and invalidation-engine distances; any generated gap or reordering would break offset-based loops.
- 64-bit register pairs require correct low/high pairing and hardware-required write ordering. The header only names halves; it cannot enforce correct sequencing for page-table bases, address ranges, fault addresses, apertures, or default addresses.
- VMID and invalidation-engine cardinality are implicit. The header exposes 16 contexts and 18 invalidate engines, and the consumer loops over those counts. A future map with a different count would need coordinated code changes.
- SR-IOV accessibility matters. The consumer skips some registers for virtual functions because the PF programs them; wrong offsets or missing skips can cause access faults or isolation issues.
- Fault-policy and default-page registers are safety-sensitive. Incorrect offsets may suppress faults, redirect them incorrectly, or trigger crash-on-fault paths unexpectedly.
- Power/deepsleep/register-save registers are present even though the current v3.0.2 clock-gating hooks are TODO. Future use should validate access sequencing against power-management state.
- Reserved or diagnostic registers should not be treated as scratch registers; the generated names do not imply safe arbitrary writes.

## Test Signals

Useful validation signals for this header are build-time, bring-up, and hardware behavior checks:

- Build AMDGPU code paths that include `mmhub_v3_0_2.c`; missing or renamed offset/base-index macros should fail at compile time.
- Compare generated offsets and base indices against the authoritative AMD register database for MMHUB 3.0.2 when regenerating or rebasing.
- Boot hardware or simulation that selects `mmhub_v3_0_2_funcs` and verify GART enable completes without VM setup faults.
- Exercise page-table programming for VMID 0 and nonzero VMIDs; confirm low/high page-table base/start/end writes land at the expected context strides.
- Exercise TLB/cache invalidation and watch for request/ack progress without timeout on all configured invalidate engines.
- Trigger controlled VM faults where possible and verify L2 protection-fault status decoding reports the expected client ID, read/write direction, and fault class.
- Validate FB location and MC FB offset reads against expected memory-controller aperture values.
- Run SR-IOV VF smoke tests to confirm skipped PF-owned registers do not cause VF access errors and per-VF aperture behavior remains isolated.
- Run suspend/resume or runtime power-management smoke tests before using PCTL/deepsleep/register-save offsets in new code.

## Research Notes

The source header was read completely across all 1,425 lines. It is a generated-style MMHUB 3.0.2 register map, not executable logic. Substantive behavior was therefore researched through its macro families, address-block organization, and the observed consumer `amdgpu/mmhub_v3_0_2.c`, which uses these offsets to initialize and operate AMDGPU MMHUB VM, GART, cache/TLB, invalidation, fault, and aperture paths.
