# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/osssys_4_4_2_offset.h

## Purpose
`osssys_4_4_2_offset.h` is a generated AMDGPU OSSSYS 4.4.2 register-offset header. It maps symbolic OSSSYS register names to word offsets within the `aid_osssys_osssysdec` address block, whose documented base address is `0x4280`. Driver code uses these offsets with SOC15 register-address helpers to access IH VMID lookup tables, interrupt ring registers, status/diagnostic registers, SEM mailbox registers, and virtualization/client-configuration registers for this ASIC/IP version.

## Important APIs, Types, and Functions
The file has no functions or data types. Its exported interface is a set of `#define reg...` offset macros plus matching `reg..._BASE_IDX` macros. Important register groups include:

- `regIH_VMID_0_LUT` through `regIH_VMID_15_LUT` at offsets `0x0000` through `0x000f`, and `regIH_VMID_0_LUT_MM` through `regIH_VMID_15_LUT_MM` at `0x0010` through `0x001f`.
- `regIH_COOKIE_0` through `regIH_COOKIE_7` at `0x0020` through `0x0027`, plus `regIH_REGISTER_LAST_PART0`.
- Primary IH ring registers from `regIH_RB_CNTL` through `regIH_DOORBELL_RETRY_CAM`, secondary ring-1 registers from `regIH_RB_CNTL_RING1` through `regIH_DOORBELL_RPTR_RING1`, and retry/version/control/status/performance registers such as `regIH_RETRY_CAM_ACK`, `regIH_VERSION`, `regIH_CNTL`, `regIH_CNTL2`, `regIH_STATUS`, and `regIH_PERF*`.
- DSM match, interrupt-rate, VF ring status, flood status, storm-client, clock, interrupt flag, last-interrupt, scratch, credit, IOV violation, cookie violation, MMHUB error, memory-power, retry CAM, and `regIH_VMID_LUT_INDEX` registers.
- SEM mailbox registers `regSEM_MAILBOX` and `regSEM_MAILBOX_CLEAR`, with `regSEM_REGISTER_LAST_PART2` as a block boundary marker.
- Virtualization and client-configuration registers: `regIH_ACTIVE_FCN_ID`, `regIH_VIRT_RESET_REQ`, `regIH_CLIENT_CFG`, `regIH_CLIENT_CFG_INDEX`, `regIH_CLIENT_CFG_DATA`, `regIH_CLIENT_CFG_DATA2`, `regIH_CID_REMAP_INDEX`, `regIH_CID_REMAP_DATA`, `regIH_CHICKEN`, `regIH_INT_DROP_*`, `regIH_MMHUB_CNTL`, and `regIH_REGISTER_LAST_PART1`.

All `_BASE_IDX` values in this header are `0`, which tells SOC15-style accessors which register base array entry to use for this block.

## Control Flow and State
There is no runtime control flow. The header guard `_osssys_4_4_2_OFFSET_HEADER` prevents duplicate preprocessing, and the macros are substituted at compile time. The practical use pattern is:

1. A driver includes this offset header and the matching `osssys_4_4_2_sh_mask.h`.
2. The driver computes a physical register index using `SOC15_REG_OFFSET(OSSSYS, instance, regNAME)` or adds an indexed VMID/register offset manually.
3. The driver reads or writes the register through AMDGPU MMIO helpers.

The header does not persist state itself. It identifies persistent hardware register locations that hold VMID/PASID mappings, IH ring state, interrupt diagnostics, SEM mailbox state, memory power controls, active PF/VF identity, client configuration, and interrupt-drop match values.

## Dependencies
This generated header depends on the OSSSYS 4.4.2 register map and the AMDGPU SOC15 register-addressing convention. It must be used with the matching 4.4.2 mask header when fields are manipulated. Direct consumers found in this tree include `drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gc_9_4_3.c`, which includes this file and programs `regIH_VMID_LUT_INDEX`, `regIH_VMID_0_LUT`, and `regIH_VMID_0_LUT_MM` while setting KFD VMID/PASID mappings for GC 9.4.3, and generic GMC code paths that use the same `regIH_VMID_0_LUT` naming pattern for PASID reads and writes on newer IPs.

## Integration Points
The main integration point is the AMDGPU/KFD queue and VM management path. In `kgd_gfx_v9_4_3_set_pasid_vmid_mapping()`, the driver first programs ATHUB VMID/PASID state, waits for the ATHUB update bit, then uses OSSSYS offsets from this header to select the correct AID/XCC entry through `regIH_VMID_LUT_INDEX` and write the PASID mapping into `regIH_VMID_0_LUT + vmid` and `regIH_VMID_0_LUT_MM + vmid`. The same offset map also supports IH ring setup and diagnostics for ASIC code that uses OSSSYS 4.4.2, although this particular offset header is primarily pulled into the KFD GC 9.4.3 implementation in this tree.

## Risks
Offset mistakes are severe because the MMIO access still compiles but targets the wrong hardware register. A bad VMID LUT offset can break PASID attribution, interrupt routing, or KFD process isolation. A wrong `regIH_VMID_LUT_INDEX` offset can cause writes intended for one AID/XCC slice to land in another slice. Incorrect ring, status, flood, or diagnostic offsets can make interrupt setup appear successful while the device remains silent or reports misleading status. Using this header with a non-4.4.2 mask header or an ASIC with a different OSSSYS base address is another risk: field bits may be valid in one version while the register offset belongs to another. Since every `_BASE_IDX` is a constant macro, base-index errors are not detectable by type checking.

## Test Signals
Validation signals include successful builds of the GC 9.4.3 KFD path, successful compute queue creation/destruction, correct VMID/PASID mapping under multi-process KFD workloads, no timeout from ATHUB mapping update followed by OSSSYS LUT writes, correct interrupt attribution across XCC/AID instances, no regressions in GPU reset or SR-IOV PF/VF routing, and register dumps showing `regIH_VMID_LUT_INDEX`, `regIH_VMID_0_LUT + vmid`, and `regIH_VMID_0_LUT_MM + vmid` changing as expected for each VMID. Stress tests should include multiple VMIDs, multiple XCC instances, and workloads that generate graphics, compute, SDMA, and multimedia interrupts.
