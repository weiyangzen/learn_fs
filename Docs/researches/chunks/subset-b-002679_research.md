# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_2_sh_mask.h lines 29426-31946

## Purpose

This chunk is generated-style register field metadata for the AMD GC 9.4.2 graphics core, focused on GPUVM/UTCL2/VML2 control, virtual-memory context setup, VM invalidate engines, SR-IOV/XGMI aperture controls, and graphics-core CAC power/activity accounting. It provides symbolic bit shifts and masks for 32-bit hardware registers so AMDGPU code can use `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_FIELD`, SOC15 register entries, and generated offset headers instead of open-coded bit positions.

The range begins at the tail of `VM_L2_MM_GROUP_RT_CLASSES`, covers VM L2 reserved-client, parity, clock-gating, ECC, EDC, and performance-counter registers, then moves through `gc_utcl2_vml2vcdec` VM context and invalidation registers. It continues into shared hypervisor/PF/VC VM aperture registers and ends in the `gccacind` indirect CAC register block with weight and accumulator fields through `GC_CAC_ACC_PA0`.

## Important APIs, Types, And Data

There are no C functions, structs, enums, or storage objects declared in this header slice. The exported interface is the generated macro contract:

- `REGISTER__FIELD__SHIFT` is the field low-bit position.
- `REGISTER__FIELD_MASK` is the unshifted field mask.
- Full-register fields such as page-table base low/high words, logical page ranges, CAC override values, and CAC accumulators use `0xFFFFFFFFL` masks.
- Address-block comments such as `gc_utcl2_vml2pldec`, `gc_utcl2_vml2prdec`, `gc_utcl2_vml2vcdec`, `gc_utcl2_vmsharedhvdec`, `gc_utcl2_vmsharedpfdec`, `gc_utcl2_vmsharedvcdec`, and `gccacind` group related hardware decode domains.

Important register groups in this chunk include:

- VM L2 controls: `VM_L2_MM_GROUP_RT_CLASSES`, `VM_L2_BANK_SELECT_RESERVED_CID*`, `VM_L2_CACHE_PARITY_CNTL`, `VM_L2_CGTT_CLK_CTRL`, and `VM_L2_CGTT_BUSY_CTRL` define VM L2 routing class bits, reserved read/write client IDs, parity test controls, and clock-gating timing/override behavior.
- UTC/VML2 ECC and EDC: `VML2_MEM_ECC_INDEX`, `VML2_WALKER_MEM_ECC_INDEX`, `UTCL2_MEM_ECC_INDEX`, matching `*_ECC_CNTL` registers, matching `*_ECC_STATUS` registers, `UTCL2_EDC_MODE`, and `UTCL2_EDC_CONFIG` define indexed ECC counter/error-injection access, SEC/DED counters, UCE/FED status bits, and EDC propagation/bypass modes.
- VM L2 performance counters: `MC_VM_L2_PERFCOUNTER0_CFG` through `MC_VM_L2_PERFCOUNTER7_CFG`, `MC_VM_L2_PERFCOUNTER_RSLT_CNTL`, and `MC_VM_L2_PERFCOUNTER_LO/HI` define event selection, mode, enable, counter selection, clear, and 64-bit result access.
- VM contexts 0-15: each `VM_CONTEXTn_CNTL` has the same field layout for enable, page-table depth/block size, retry behavior, and interrupt/default handling for range, dummy-page, PDE0, valid, read, write, and execute protection faults. `VM_CONTEXTS_DISABLE` exposes per-context disable bits.
- VM invalidation engines 0-17: each engine has semaphore, request, acknowledge, and low/high address-range registers. Requests carry per-VMID invalidate masks, flush type, L2 PTE/PDE0/PDE1/PDE2 invalidation, L1 PTE invalidation, protection-fault status clearing, and optional request logging. ACK registers expose per-VMID completion and semaphore state.
- VM context address registers: `VM_CONTEXTn_PAGE_TABLE_BASE_ADDR_*`, `VM_CONTEXTn_PAGE_TABLE_START_ADDR_*`, and `VM_CONTEXTn_PAGE_TABLE_END_ADDR_*` describe page-directory base and legal logical page range fields for contexts 0-15.
- SR-IOV and XGMI VM sharing: `MC_VM_FB_SIZE_OFFSET_VF0..VF15`, `MC_SHARED_ACTIVE_FCN_ID`, `MC_VM_XGMI_GPUIOV_ENABLE`, `MC_SHARED_VIRT_RESET_REQ`, `VM_PCIE_ATS_CNTL`, and `VM_PCIE_ATS_CNTL_VF_*` define VF framebuffer apertures, active function identity, PF/VF XGMI GPU-IOV enable bits, virtualization reset request bits, and ATS enable/STU fields.
- PF and VC aperture setup: `MC_VM_FB_OFFSET`, system aperture default address LSB/MSB, `MC_VM_STEERING`, cacheable DRAM and local HBM address windows, `MC_VM_APT_CNTL`, `MC_VM_XGMI_LFB_CNTL/SIZE`, framebuffer/AGP/system aperture bounds, and `MC_VM_MX_L1_TLB_CNTL` define memory windows, host mapping, LFB sizing, ATC/L1 TLB behavior, MTYPE, and advanced driver model flags.
- GC CAC indirect registers: `GC_CAC_CNTL`, `GC_CAC_OVR_SEL`, `GC_CAC_OVR_VAL`, many `GC_CAC_WEIGHT_*` registers, and `GC_CAC_ACC_*` registers define activity-counter block/signal selection, thresholds, force disable, override selection/value, per-block signal weights, and 32-bit accumulators for BCI, CB, CP, DB, GDS, IA, LDS, and PA in this slice.

## Control Flow

This file has no runtime control flow. Its behavior is compile-time substitution: including C files combine the masks and shifts with generated offsets from `gc_9_4_2_offset.h` and with AMDGPU register helpers.

Typical consumer flow is:

1. Include `gc/gc_9_4_2_offset.h` and `gc/gc_9_4_2_sh_mask.h` for the target ASIC.
2. Read or construct a register value with SOC15 helpers.
3. Use `REG_SET_FIELD`, `REG_GET_FIELD`, or `SOC15_REG_FIELD` with these macro names to encode or decode hardware fields.
4. Write the register value, poll an ACK/status register, or report decoded state.

Concrete local examples include `amdgpu/gfx_v9_4_2.c`, which includes this exact header and uses the UTC ECC masks through `SOC15_REG_FIELD(VML2_MEM_ECC_CNTL, SEC_COUNT)`, `SOC15_REG_FIELD(VML2_MEM_ECC_CNTL, DED_COUNT)`, corresponding walker/UTCL2 fields, and `REG_SET_FIELD(..., WRITE_COUNTERS, 1)` while querying or clearing RAS counters. The common GC/GMC pattern is also visible in files such as `gmc_v9_0.c`, where a VM invalidate request is constructed with `VM_INVALIDATE_ENG0_REQ` fields for per-VMID invalidation, flush type, L2/L1 invalidation, and protection-fault clearing.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. The state they describe lives in GPU registers and changes through MMIO or indirect register access.

Important state categories are:

- Long-lived VM configuration: VM context controls, page-table base/start/end address registers, context disable bits, aperture bounds, framebuffer/AGP locations, local HBM and cacheable DRAM windows, TLB controls, ATS enables, and XGMI/GPU-IOV enables remain in hardware until reprogrammed, reset, or lost across power transitions.
- Transient invalidation synchronization: `VM_INVALIDATE_ENG*_SEM`, `*_REQ`, `*_ACK`, and address-range fields are part of request/acknowledge cache-invalidation protocol. Consumers must issue the request with the correct VMID bits and poll or consume matching ACK/semaphore state.
- RAS/error state: ECC index/control registers select indexed memory blocks and expose SEC/DED counters. `*_ECC_STATUS` UCE/FED bits are status/clear fields used by GC 9.4.2 RAS paths; local code writes `0x3` to clear `UTCL2_MEM_ECC_STATUS`, `VML2_MEM_ECC_STATUS`, and `VML2_WALKER_MEM_ECC_STATUS` after logging or reset.
- Test and injection state: `ENABLE_ERROR_INJECT`, `ENABLE_SINGLE_WRITE`, `INJECT_DELAY`, `DSM_IRRITATOR_DATA`, `TEST_FUE`, forced VM L2 parity mismatch fields, EDC bypass/propagation fields, and clock-gating overrides can intentionally alter hardware behavior. These are not ordinary production toggles.
- Counter state: VM L2 performance counters and GC CAC accumulator registers collect hardware activity until cleared, reselected, reset, or overwritten. CAC weights and threshold/select fields influence how activity is counted or used by power-management logic.

There is no disk state, kernel allocation, reference counting, or lock ownership in this header. Persistence concerns are exclusively hardware persistence and whether driver init, suspend/resume, reset, SR-IOV mode changes, and RAS recovery paths restore the intended register state.

## Dependencies

This chunk depends on the rest of the generated GC 9.4.2 register family:

- `gc_9_4_2_offset.h` provides the matching register offsets and indirect register IDs.
- Neighboring `gc_9_4_2_sh_mask.h` chunks define adjacent fields used by the same generated header.
- AMDGPU helper macros and types such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_FIELD`, `SOC15_REG_ENTRY`, `SOC15_REG_ENTRY_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, and indirect-register helpers interpret these masks.
- GC 9.4.2 code in `amdgpu/gfx_v9_4_2.c` depends on the VML2/UTCL2 ECC fields matching the hardware RAS counter layout.
- GPUVM/GMC/GFXHUB code depends on the VM context and invalidation field names matching the register layout, even when similar field groups are defined under generation-specific prefixes in other ASIC families.
- Power-management and power-tune paths use CAC indirect registers in other generations through `CGS_IND_REG_GC_CAC`; the `gccacind` block here provides the GC 9.4.2 layout for equivalent weight, select, override, and accumulator registers.

The data is a hardware contract. It should stay synchronized with AMD's generated register sources, the matching offset header, and the firmware/SMU expectations for GC 9.4.2/Aldebaran-class devices.

## Integration Points

Primary integration points are:

- GFX RAS handling in `gfx_v9_4_2.c`: `gfx_v9_4_2_utc_blocks` uses `VML2_MEM_ECC_*`, `VML2_WALKER_MEM_ECC_*`, and `UTCL2_MEM_ECC_*` index/control fields to walk indexed UTC/VML2 memory blocks, read SEC/DED counts, log sub-block names, and clear counters with the `WRITE_COUNTERS` bit. RAS status query/reset paths read and clear the three `*_ECC_STATUS` registers.
- VM fault and invalidation machinery: VM invalidate fields match the common AMDGPU pattern for building per-VMID invalidation requests, selecting flush behavior, invalidating L2 PTE/PDE levels and L1 PTEs, and tracking per-engine ACK state.
- GPUVM context programming: VM context control fields and page-table base/start/end fields are used by hub initialization code to configure VMID contexts, retry/default fault handling, page-table geometry, and aperture ranges.
- SR-IOV and virtualization: VF framebuffer size/offset registers, active function ID, VF/PF reset request bits, ATS enable bits, and XGMI GPU-IOV enable bits integrate with PF/VF setup and virtualized memory isolation.
- XGMI and large-framebuffer setup: `MC_VM_XGMI_LFB_CNTL` and `MC_VM_XGMI_LFB_SIZE` provide PF LFB region and size fields analogous to MMHUB code that derives XGMI physical address ranges from LFB region/size registers.
- Memory aperture and host mapping setup: PF/VC shared aperture registers feed framebuffer, AGP, system aperture, cacheable DRAM, local HBM, host-mapping, TLB, MTYPE, ATC, and advanced-driver-model configuration.
- Performance and power instrumentation: VM L2 perfcounter fields and GC CAC weight/accumulator fields are the low-level register definitions used by profiling, diagnostics, firmware-mediated power logic, or power-management tables.

## Risks

- A wrong shift or mask silently targets the wrong hardware bits. For VM context and invalidation registers, that can produce stale translations, missed TLB flushes, incorrect protection-fault behavior, or broken page-table geometry.
- VM invalidate engines are replicated 18 times with identical field layouts. Copying a field from the wrong engine or computing engine spacing incorrectly can make one VMID appear flushed while another engine owns the outstanding request.
- Context address registers split logical/page-directory addresses across low/high words with narrow high masks on start/end ranges. Consumers must preserve address unit and width semantics; treating these as raw byte addresses or full 64-bit masks would misprogram apertures.
- ECC and EDC fields include both production RAS counters/status and destructive test/injection controls. Accidentally setting `ENABLE_ERROR_INJECT`, parity force bits, EDC bypass, or `TEST_FUE` can create false RAS events or real correctness loss.
- Counter clear behavior is register-specific. GC 9.4.2 RAS code clears UTC counters by writing a value containing `WRITE_COUNTERS` and clears status registers with `0x3`; new consumers should not assume all status or count fields are clear-on-read.
- SR-IOV, ATS, and XGMI GPU-IOV controls affect isolation and address translation for PF/VF functions. Misprogramming VF enable bits, active function IDs, reset requests, or ATS state can leak access, strand a VF, or break peer/CPU-connected memory access.
- CAC registers are indirect and power-sensitive. Incorrect weights, thresholds, or override values can skew activity accounting and power-management behavior even if graphics workloads otherwise run.
- Cross-generation names are similar but not interchangeable. GC 9.4.2, MMHUB, GCVM, and later GC variants use related `VM_CONTEXT*` and `VM_INVALIDATE_ENG*` names with prefix/layout differences; including the wrong ASIC header can compile but program invalid fields.
- The file is generated metadata. Manual edits are high risk and should normally be made by regenerating the ASIC register headers from the authoritative hardware source.

## Test Signals

Useful validation signals include:

- Build coverage for GC 9.4.2/Aldebaran code paths that include `gc_9_4_2_sh_mask.h`, especially `gfx_v9_4_2.c` and `amdgpu_amdkfd_aldebaran.c`.
- Static consistency checks that every register named in this chunk has a matching offset or indirect index in `gc_9_4_2_offset.h`.
- RAS tests on GC 9.4.2 hardware that query and reset GFX RAS counts, confirm SEC/DED increments are decoded from the expected `VML2_*` and `UTCL2_*` fields, and confirm `*_ECC_STATUS` bits are logged and cleared.
- GPUVM stress tests that allocate/free BOs across VMIDs, force page-table updates, issue invalidations, and verify no stale mappings, VM fault storms, or invalidate timeout messages occur.
- SR-IOV validation with PF and multiple VFs that checks VF framebuffer apertures, ATS enable behavior, virtual reset requests, and XGMI GPU-IOV enable state across VF reset and host suspend/resume.
- XGMI and large-framebuffer tests that verify peer-memory visibility and LFB region/size calculations after boot and reset.
- Power/performance instrumentation tests that read VM L2 perf counters and GC CAC accumulators, then verify counter selection, clear, and accumulation behavior remain stable under graphics and compute workloads.
- Runtime smoke tests across reset, suspend/resume, and RAS recovery paths, because these registers are mostly persistent hardware configuration rather than ordinary local variables.
