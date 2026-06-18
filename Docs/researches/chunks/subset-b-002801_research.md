# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_3_0_0_sh_mask.h lines 7205-7478

## Scope And Purpose

This chunk is the closing register-field section of the AMDGPU MMHUB 3.0.0 shift/mask header. It contains generated-style preprocessor constants for the MMHUB MMUTCL2, shared VM aperture, ATC L2, MML2TLB, and GPUVA VMID translation-assist register blocks. Every exported symbol is a bitfield contract of the form `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`; there are no functions, structs, enums, local variables, or executable branches in this range.

The range begins with the tail of `MMMC_VM_FB_NOALLOC_CNTL`, then covers `MMUTCL2_HARVEST_BYPASS_GROUPS` and `MMUTCL2_GROUP_RET_FAULT_STATUS`. It then moves through address blocks `mmhub_mmutcl2_mmvmsharedvcdec`, `mmhub_mmutcl2_mmatcl2pfcntrdec`, `mmhub_mmutcl2_mmatcl2pfcntldec`, `mmhub_mmutcl2_mmvml2pspdec`, `mmhub_mmutcl2_mml2tlbpspdec`, `mmhub_mmutcl2_mmatcl2pspdec`, `mmhub_mmutcl2_mml2tlbpfdec`, `mmhub_mmutcl2_mml2tlbpldec`, and `mmhub_mmutcl2_mml2tlbprdec`. The file ends at line 7478 with the include guard `#endif`, so this chunk completes the full `mmhub_3_0_0_sh_mask.h` header.

The companion register-address header is `mmhub_3_0_0_offset.h`. This `_sh_mask.h` file does not name addresses by itself; it supplies the field layout used when callers read or write the offsets with AMDGPU MMIO helpers.

## Important APIs, Types, And Constants

There are no callable APIs or C types. The public interface is the set of register-field macros consumed by helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, and related register access wrappers in AMDGPU code.

Important constants in this chunk include:

- `MMMC_VM_FB_NOALLOC_CNTL__ROUTER_GPA_MODE2_NOALLOC_MASK` and `__ROUTER_GPA_MODE3_NOALLOC_MASK`: final no-allocate policy bits for framebuffer access paths using GPA modes. The earlier fields for local/remote FB and ATCL2 no-allocate are immediately above the chunk boundary.
- `MMUTCL2_HARVEST_BYPASS_GROUPS__BYPASS_GROUPS`: a full-width bitmap naming harvested or bypassed MMUTCL2 groups.
- `MMUTCL2_GROUP_RET_FAULT_STATUS__FAULT_GROUPS`: a full-width bitmap reporting groups with return faults.
- `MMMC_VM_FB_LOCATION_BASE` and `MMMC_VM_FB_LOCATION_TOP`: 24-bit framebuffer base/top fields. `mmhub_v3_0_get_fb_location()` reads `regMMMC_VM_FB_LOCATION_BASE`, applies `MMMC_VM_FB_LOCATION_BASE__FB_BASE_MASK`, and shifts the value left by 24 to recover the MC framebuffer base.
- `MMMC_VM_AGP_TOP`, `MMMC_VM_AGP_BOT`, and `MMMC_VM_AGP_BASE`: 24-bit AGP aperture fields. `mmhub_v3_0_init_system_aperture_regs()` writes these registers from `adev->gmc.agp_start` and `adev->gmc.agp_end` shifted by 24.
- `MMMC_VM_SYSTEM_APERTURE_LOW_ADDR` and `MMMC_VM_SYSTEM_APERTURE_HIGH_ADDR`: 30-bit logical address fields. The MMHUB v3.0 initialization path programs them from the min/max of FB and AGP ranges shifted by 18.
- `MMMC_VM_MX_L1_TLB_CNTL`: L1 TLB control fields for `ENABLE_L1_TLB`, `SYSTEM_ACCESS_MODE`, `SYSTEM_APERTURE_UNMAPPED_ACCESS`, `ENABLE_ADVANCED_DRIVER_MODEL`, `ECO_BITS`, and `MTYPE`. `mmhub_v3_0_init_tlb_regs()` sets these through `REG_SET_FIELD`, enabling the L1 TLB, selecting system access mode `3`, enabling the advanced driver model, clearing unmapped system-aperture access, clearing ECO bits, and selecting uncached `MTYPE_UC`.
- `MM_ATC_L2_PERFCOUNTER_LO` and `MM_ATC_L2_PERFCOUNTER_HI`: ATC L2 counter result fields. The high register splits into a 16-bit high counter value and a 16-bit compare value.
- `MM_ATC_L2_PERFCOUNTER0_CFG`, `MM_ATC_L2_PERFCOUNTER1_CFG`, and `MM_ATC_L2_PERFCOUNTER_RSLT_CNTL`: ATC L2 performance-counter event selection, event range end, mode, enable, clear, start/stop trigger, global enable/clear, and stop-on-saturate fields.
- `MMUTCL2_TRANSLATION_BYPASS_BY_VMID`: two 16-bit VMID bitmaps, one for translation bypass and one for GPA mode VMIDs.
- `MMUTC_TRANSLATION_FAULT_CNTL0` and `MMUTC_TRANSLATION_FAULT_CNTL1`: default physical page address low/high fields plus default IO, SPA, and snoop attributes used for translation-fault handling.
- `MMUTCL2_FFBM_ENABLE_CNTL__ENABLE_FFBM`: single-bit control for FFBM enablement.
- `MMUTC_GPUVA_VMID_TRANSLATION_ASSIST_CNTL__ENABLE`: single-bit enable for the GPUVA VMID translation-assist interface.
- `MM_ATC_L2_IOV_MODE_CNTL__PSEUDO_IOV_EN`: single-bit pseudo-IOV mode control.
- `MML2TLB_TLB0_STATUS`: status bits for TLB busy state, parity errors, and aperture faults.
- `MML2TLB_TMZ_CNTL__TMZ_MODULATION`: trusted-memory-zone modulation control.
- `MMUTC_GPUVA_VMID_TRANSLATION_ASSIST_REQUEST_LO/HI`: request address, VMID, VFID, VF flag, GPA mode, read/write/execute permissions, client ID, and request-valid bit for translation assist.
- `MMUTC_GPUVA_VMID_TRANSLATION_ASSIST_RESPONSE_LO/HI`: response address, permissions, fragment size, snoop/SPA/IO attributes, PTE TMZ, no-PTE, memory type, memlog, NACK, LLC no-allocate, and ACK fields.
- `MMUTCL2_L2TLB_CREDIT_SAFETY_FETCH_RDREQ`: 10-bit credit value plus write strobe for L2 TLB fetch read-request credit safety.
- `MML2TLB_PERFCOUNTER0_CFG` through `MML2TLB_PERFCOUNTER3_CFG`, `MML2TLB_PERFCOUNTER_RSLT_CNTL`, `MML2TLB_PERFCOUNTER_LO`, and `MML2TLB_PERFCOUNTER_HI`: MML2TLB performance-counter configuration, result-control, and 48-bit result/compare register layout, mirroring the ATC L2 pattern but exposing four counter config registers.

## Control Flow And State Behavior

This header has no runtime control flow. It is a compile-time interface for composing and decoding 32-bit hardware register values. Runtime behavior occurs only in code that includes this header and then performs MMIO reads or writes against the MMHUB 3.0.0 register offsets.

The shared VM aperture fields in this chunk participate in MMHUB address translation state. The driver programs AGP base/bottom/top and system aperture low/high registers during MMHUB setup, and it reads framebuffer location registers to derive memory-controller addresses. `MMMC_VM_MX_L1_TLB_CNTL` is read-modify-written during TLB initialization and disable paths; those operations persist in the GPU register file until reset, power transition, firmware reprogramming, or a later driver write.

The translation-bypass, fault-default, FFBM, GPUVA translation-assist, pseudo-IOV, TMZ, and credit-safety fields configure MMUTCL2 and MML2TLB hardware behavior. They can affect whether VMIDs bypass translation, what physical attributes are returned for translation faults, whether translation-assist handshakes are accepted, whether secure/TMZ behavior is modulated, and whether request credits are overridden or repaired.

The status and performance-counter registers represent hardware-owned state. `MML2TLB_TLB0_STATUS` exposes busy/error/fault bits. ATC L2 and MML2TLB performance counters accumulate event counts according to selected `PERF_SEL`, `PERF_SEL_END`, and `PERF_MODE` values; `ENABLE`, `CLEAR`, `CLEAR_ALL`, start/stop triggers, and stop-on-saturate fields change counter state. The header does not encode which fields are read-only, sticky, write-one-to-clear, or side-effectful.

## Dependencies And Integration Points

The immediate companion file is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_3_0_0_offset.h`. Its matching offset neighborhood maps this chunk's registers to MMHUB offsets and base indices: `regMMMC_VM_FB_LOCATION_BASE` at `0x08ec`, `regMMMC_VM_MX_L1_TLB_CNTL` at `0x08f3`, ATC L2 performance-counter registers at `0x0900` through `0x090a`, `regMMUTCL2_TRANSLATION_BYPASS_BY_VMID` at `0x0a94`, translation fault controls at `0x0a99` and `0x0a9a`, translation assist registers at `0x0aa0` and `0x0ab3` through `0x0ab6`, `regMMUTCL2_L2TLB_CREDIT_SAFETY_FETCH_RDREQ` at `0x0ab7`, and MML2TLB performance-counter registers at `0x0ac0` through `0x0ac9`.

The primary in-tree consumer is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v3_0.c`, which includes both `mmhub_3_0_0_offset.h` and this shift/mask header. Direct uses from this chunk include `MMMC_VM_FB_LOCATION_BASE__FB_BASE_MASK` in `mmhub_v3_0_get_fb_location()` and the `MMMC_VM_MX_L1_TLB_CNTL` field macros in `mmhub_v3_0_init_tlb_regs()` and `mmhub_v3_0_gart_disable()`. The same file also writes the AGP and system aperture registers named in this chunk, using raw shifted values rather than `REG_SET_FIELD`.

Neighbor generation headers such as `mmhub_3_0_1_sh_mask.h`, `mmhub_3_0_2_sh_mask.h`, `mmhub_3_3_0_sh_mask.h`, and later `mmhub_4_*` variants contain similar macro families. They are useful for comparing repeated hardware layouts, but their offsets and base indices differ. Code for MMHUB 3.0.0 must include the matching 3.0.0 offset and shift/mask headers to avoid programming the wrong register instance or field layout.

This header also depends implicitly on AMDGPU register helper conventions. `REG_SET_FIELD(value, REG, FIELD, new_value)` expects `REG__FIELD_MASK` and `REG__FIELD__SHIFT` to exist and to describe a contiguous field. `REG_GET_FIELD` expects the same layout for extraction. Raw masks like `MMMC_VM_FB_LOCATION_BASE__FB_BASE_MASK` are also used directly when code needs only masking without a shift helper.

## Risks And Edge Cases

- These macros are a hardware ABI. A wrong mask or shift can silently program MMHUB address translation, aperture, TLB, security, or counter behavior incorrectly while still compiling.
- Several fields encode address fragments rather than byte addresses. FB and AGP fields are 24-bit values that callers shift by 24, while system aperture fields use a different logical-page shift. Mixing these units would produce plausible but wrong apertures.
- `MMMC_VM_MX_L1_TLB_CNTL` is manipulated by read-modify-write. Any stale mask or overlap in `ENABLE_L1_TLB`, `SYSTEM_ACCESS_MODE`, `ENABLE_ADVANCED_DRIVER_MODEL`, `SYSTEM_APERTURE_UNMAPPED_ACCESS`, `ECO_BITS`, or `MTYPE` could preserve or clear unrelated hardware state.
- `MMUTCL2_TRANSLATION_BYPASS_BY_VMID` packs two independent 16-bit VMID bitmaps into one register. Treating it as a single VMID value or using an unshifted high-half value would affect the wrong VMID group.
- Translation-assist request and response high registers are densely packed. Address-high bits, VMID/VFID, permission bits, client ID, request/ACK, and NACK fields occupy neighboring ranges; off-by-one shifts can create valid-looking handshakes with invalid attributes.
- Full-width masks such as `0xFFFFFFFFL` should be treated as unsigned 32-bit quantities. Signed promotion or incorrect printk formats can confuse diagnostics and register-dump comparisons.
- Status and counter fields may be volatile, sticky, or side-effectful. The generated header gives bit positions only; it does not document access type, reset value, ordering requirements, or whether a field is safe to write.
- Cross-generation names are intentionally similar. Reusing a macro from MMHUB 3.0.1, 3.0.2, 3.3.0, or 4.x against 3.0.0 offsets could compile but target a different base index or field contract.

## Test And Validation Signals

There are no direct unit tests for this macro-only header range. Useful validation signals are compile-time, static, and hardware-facing:

- Build AMDGPU configurations that compile `amdgpu/mmhub_v3_0.c` and include `mmhub_3_0_0_offset.h` plus `mmhub_3_0_0_sh_mask.h`.
- Run static mask/shift checks for this chunk: single-bit masks must equal `1 << shift`; multi-bit masks must be contiguous at the documented shift; repeated performance-counter config registers should have identical field layouts; full-width masks should have shift zero.
- Compare this chunk against the matching offset header to ensure every register-comment group has a `reg*` offset and `_BASE_IDX` in the corresponding address block.
- Exercise MMHUB v3.0 GART/VM initialization and teardown paths. Relevant signals include correct programming of AGP/system aperture registers, `MMMC_VM_MX_L1_TLB_CNTL` values after init and disable, and correct framebuffer-base derivation from `MMMC_VM_FB_LOCATION_BASE`.
- On supported hardware, inspect MMHUB register dumps across driver load, suspend/resume, SR-IOV modes, and GART disable/re-enable to confirm only expected fields in this chunk change.
- For performance-counter fields, hardware tests should validate clear, enable, trigger, stop-on-saturate, low/high reads, and compare behavior for both ATC L2 and MML2TLB counter blocks.
- For translation-assist and fault-default fields, useful stress signals are VM fault injection, invalid-address access, VF/VMID scenarios, and checks that reported client IDs, permissions, ACK/NACK status, and default physical attributes match the hardware programming guide.

## Chunk Notes For Merge Lane

This is the final chunk of `mmhub_3_0_0_sh_mask.h`. It completes the MMUTCL2 shared VM aperture, ATC L2 performance, PSP-facing translation controls, GPUVA translation-assist, MML2TLB status/control, credit safety, and MML2TLB performance-counter sections. Whole-file reconciliation should merge this with earlier chunks that cover the license/include guard opening and the preceding MMHUB/MMUTCL2 register blocks.
