# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_3_0_1_sh_mask.h lines 7298-7483

## Scope And Purpose

This chunk is the final portion of the AMDGPU MMHUB 3.0.1 shift/mask header. It is a generated hardware contract: every exported symbol is a preprocessor constant that describes a bit position or bit mask inside a 32-bit MMHUB register. There are no C functions, structs, enums, local variables, branches, loops, or direct MMIO operations in this range.

The chunk starts mid-register with the final masks for `MM_ATC_L2_PERFCOUNTER_RSLT_CNTL`, then covers several MMUTCL2/L2-TLB address blocks:

- `mmhub_mmutcl2_mmvml2pspdec`: VM/IOMMU translation bypass, IOMMU enable/performance optimization, and default translation-fault target fields.
- `mmhub_mmutcl2_mml2tlbpspdec`: GPU virtual-address VMID translation assist enable.
- `mmhub_mmutcl2_mmatcl2pspdec`: ATC L2 pseudo-IOV mode control.
- `mmhub_mmutcl2_mml2tlbpfdec`: TLB0 status, TMZ control, translation-assist request/response mailboxes, and L2TLB credit safety fetch fields.
- `mmhub_mmutcl2_mml2tlbpldec` and `mmhub_mmutcl2_mml2tlbprdec`: four L2TLB performance counter configuration registers, global result control, and low/high counter result fields.

The final line is the include guard terminator, so this chunk closes the whole `mmhub_3_0_1_sh_mask.h` file.

## Important APIs, Types, And Constants

There are no callable APIs or C types. The public surface is the macro namespace consumed by AMDGPU register helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_SOC15*`, `RREG32_SOC15*`, and `SOC15_REG_OFFSET` after including the matching offset header.

Important constants in this chunk include:

- `MM_ATC_L2_PERFCOUNTER_RSLT_CNTL__ENABLE_ANY_MASK`, `__CLEAR_ALL_MASK`, and `__STOP_ALL_ON_SATURATE_MASK`: the tail of the ATC L2 performance-counter result-control register. The select/start/stop fields are immediately before this chunk.
- `MMUTCL2_TRANSLATION_BYPASS_BY_VMID__TRANS_BYPASS_VMIDS_*` and `__GPA_MODE_VMIDS_*`: two 16-bit VMID bitmaps controlling translation bypass and GPA mode behavior.
- `MMVM_IOMMU_CONTROL_REGISTER__IOMMUEN_*`: the single IOMMU enable field.
- `MMVM_IOMMU_PERFORMANCE_OPTIMIZATION_CONTROL_REGISTER__PERFOPTEN_*`: bit 13 performance optimization enable.
- `MMUTC_TRANSLATION_FAULT_CNTL0__DEFAULT_PHYSICAL_PAGE_ADDRESS_LSB_*` plus `MMUTC_TRANSLATION_FAULT_CNTL1__DEFAULT_PHYSICAL_PAGE_ADDRESS_MSB_*`, `DEFAULT_IO`, `DEFAULT_SPA`, and `DEFAULT_SNOOP`: a split default physical page address and memory attribute fields used when translation faults are redirected.
- `MMUTC_GPUVA_VMID_TRANSLATION_ASSIST_CNTL__ENABLE_*`: enables the GPUVA/VMID translation assist mechanism.
- `MM_ATC_L2_IOV_MODE_CNTL__PSEUDO_IOV_EN_*`: enables pseudo-IOV mode in the ATC L2 path.
- `MML2TLB_TLB0_STATUS__BUSY_*`, `__FOUND_PARITY_ERRORS_*`, and `__FOUND_APERTURE_FAULTS_*`: status bits for TLB0 activity and error discovery.
- `MML2TLB_TMZ_CNTL__TMZ_MODULATION_*`: trusted memory zone modulation control.
- `MMUTC_GPUVA_VMID_TRANSLATION_ASSIST_REQUEST_LO/HI`: request address, VMID, VFID, VF, GPA, read/write/execute permission, client ID, and request-valid fields.
- `MMUTC_GPUVA_VMID_TRANSLATION_ASSIST_RESPONSE_LO/HI`: response address, permissions, fragment size, snoop/SPA/IO attributes, PTE TMZ, no-PTE, memory type, memlog, NACK, LLC no-allocate, and ACK fields.
- `MMUTCL2_L2TLB_CREDIT_SAFETY_FETCH_RDREQ__CREDITS_*` and `__WRITE_*`: credit count plus write strobe/control bit.
- `MML2TLB_PERFCOUNTER0_CFG` through `MML2TLB_PERFCOUNTER3_CFG`: identical performance-counter setup fields for event select, event select end, mode, enable, and clear.
- `MML2TLB_PERFCOUNTER_RSLT_CNTL`: result counter select, start/stop triggers, global enable, clear-all, and stop-on-saturate fields.
- `MML2TLB_PERFCOUNTER_LO` and `MML2TLB_PERFCOUNTER_HI`: 48-bit counter readout split across low 32 bits and high 16 bits, with a high-register compare value in bits 31:16.

## Control Flow And State Behavior

This header contributes no runtime control flow. The C preprocessor substitutes these constants into caller code that reads, writes, or read-modify-writes MMHUB registers.

Runtime state lives in MMHUB hardware. The VMID bypass and GPA mode bitmaps affect whether specific VMIDs participate in normal translation. The IOMMU and performance optimization bits control IOMMU behavior in the MMUTCL2 VM/L2 path. The translation fault control registers hold a default physical target and IO/SPA/snoop attributes for fault handling, making them part of fault containment and recovery behavior.

The translation-assist request/response registers behave like a hardware mailbox. Request fields describe a virtual address, VMID/VFID context, GPA mode, permissions, client ID, and request strobe; response fields return translated address fragments, permissions, memory attributes, no-PTE/NACK state, LLC allocation policy, and ACK state. Correct sequencing is therefore determined by the hardware protocol and the MMIO caller, not by this header.

The TLB status and TMZ fields expose or configure hardware state in the L2 TLB. Performance-counter fields are explicitly stateful: `ENABLE`, `CLEAR`, `ENABLE_ANY`, `CLEAR_ALL`, trigger, compare, and stop-on-saturate bits control accumulation and readout of hardware counters.

Persistence is hardware-local. Values last only as long as the MMHUB instance, reset domain, power-gating state, firmware programming, and driver initialization preserve them. The header does not cache state, serialize access, know register access type, or restore values after suspend/resume.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_3_0_1_offset.h`. For this chunk it maps:

- `regMMUTCL2_TRANSLATION_BYPASS_BY_VMID` at offset `0x0a94`, `regMMVM_IOMMU_CONTROL_REGISTER` at `0x0a97`, `regMMVM_IOMMU_PERFORMANCE_OPTIMIZATION_CONTROL_REGISTER` at `0x0a98`, and `regMMUTC_TRANSLATION_FAULT_CNTL0/1` at `0x0a99/0x0a9a`.
- `regMMUTC_GPUVA_VMID_TRANSLATION_ASSIST_CNTL` at `0x0aa0`.
- `regMM_ATC_L2_IOV_MODE_CNTL` at `0x0aa4`.
- `regMML2TLB_TLB0_STATUS` at `0x0ab1`, `regMML2TLB_TMZ_CNTL` at `0x0ab2`, translation-assist request/response registers at `0x0ab3` through `0x0ab6`, and `regMMUTCL2_L2TLB_CREDIT_SAFETY_FETCH_RDREQ` at `0x0ab7`.
- `regMML2TLB_PERFCOUNTER0_CFG` through `3_CFG` at `0x0ac0` through `0x0ac3`, result control at `0x0ac4`, and result low/high registers at `0x0ac8/0x0ac9`.

The in-tree MMHUB 3.0.1 implementation is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v3_0_1.c`, which includes both `mmhub_3_0_1_offset.h` and this shift/mask header. That file primarily uses earlier VM context, invalidation, L2 cache, protection-fault, and ATC clock-gating fields, but the include exposes this chunk's register fields to the same IP-specific driver compilation unit. Register access is mediated through SOC15 helpers and the `amdgpu_mmhub_funcs` / `amdgpu_vmhub_funcs` integration used by the broader AMDGPU VM, GART, fault reporting, and clock-gating paths.

Similar macro families appear in adjacent generation headers such as `mmhub_3_0_0_sh_mask.h`, `mmhub_3_0_2_sh_mask.h`, `mmhub_3_3_0_sh_mask.h`, and `mmhub_4_1_0_sh_mask.h`. They are useful for sanity checks, but the exact offset base index and field set remain generation-specific. This chunk uses `reg*` offset names and base index `1` for the matching MMHUB 3.0.1 offset definitions.

## Risks And Edge Cases

- These macros are a hardware ABI. A wrong shift or mask can silently program the wrong VMID bitmap, fault target, memory attribute, permission bit, or performance-counter control while still compiling.
- Line 7298 begins in the middle of `MM_ATC_L2_PERFCOUNTER_RSLT_CNTL`; whole-register reasoning for that ATC L2 result-control register must include the previous chunk.
- VMID and GPA-mode controls are packed bitmaps. Confusing bit number with VMID, or applying the wrong VMID range, can bypass translation for an unintended context.
- Translation fault defaults are split across low and high registers, and address bits represent physical page address fields rather than arbitrary byte addresses. Callers must handle page alignment and high-bit composition correctly.
- Translation-assist request/response fields have handshake semantics (`REQ`, `ACK`, `NACK`) and packed permission/attribute fields. Reading or writing them without respecting hardware ordering could race with the assist engine.
- Full-width masks such as `0xFFFFFFFFL` should be treated as unsigned 32-bit register masks. Signed promotion or incorrect printf formats can produce misleading debug output.
- Status and error bits such as `FOUND_PARITY_ERRORS` and `FOUND_APERTURE_FAULTS` may be sticky or have side effects defined outside this header. The mask header does not encode access permissions or clear semantics.
- Performance-counter clear/enable/trigger fields are stateful. Accidentally setting `CLEAR`, `CLEAR_ALL`, or stop-on-saturate can invalidate measurements or alter diagnostic behavior.
- Cross-generation reuse is risky. Several nearby MMHUB versions have equivalent-looking register names but different offsets, base indices, or available status bits.

## Test And Validation Signals

There are no direct unit tests for this macro-only header chunk. Useful validation signals are compile-time, static, and hardware-observability based:

- Build AMDGPU configurations that compile `mmhub_v3_0_1.c` with `mmhub_3_0_1_offset.h` and `mmhub_3_0_1_sh_mask.h`.
- Run static mask checks: single-bit masks should equal `1U << shift`; multi-bit masks should be contiguous and aligned to their shifts; packed fields should not overlap; full-width fields should use shift zero.
- Compare every register comment group in this chunk against `mmhub_3_0_1_offset.h` to ensure a matching `reg*` offset and `_BASE_IDX` exist.
- On supported hardware, use MMHUB register dumps around GART enable/disable, VMID setup, fault injection, suspend/resume, and SR-IOV mode transitions to confirm only intended MMHUB fields change.
- For translation fault defaults, validate that injected MMHUB faults resolve to the expected default page and that IO/SPA/snoop attributes match the hardware programming guide.
- For translation assist, exercise request/response paths if exposed by firmware or diagnostics and confirm `REQ`, `ACK`, `NACK`, address, permission, and attribute fields transition coherently.
- For performance counters, test enable, clear, trigger selection, stop-on-saturate, low/high readout, and compare fields against expected counter behavior.

## Chunk Notes For Merge Lane

This is the terminal chunk of `mmhub_3_0_1_sh_mask.h`. It should be merged as the tail of the MMHUB 3.0.1 generated register-field contract, specifically the end of ATC L2 performance-counter result control plus MMUTCL2 VM/IOMMU, translation assist, TLB status/TMZ, credit safety, and L2TLB performance-counter definitions. The previous chunk is needed for the beginning of `MM_ATC_L2_PERFCOUNTER_RSLT_CNTL`; no following chunk is needed because this range includes the header guard `#endif`.
