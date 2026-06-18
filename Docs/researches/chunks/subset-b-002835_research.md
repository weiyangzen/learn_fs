# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_default.h lines 1-2930

## Scope And Purpose

This chunk is the first 2,930 lines of the generated AMDGPU MMHUB 9.4.1 register-default header. It is not executable logic; it is a compile-time catalog of reset/default values for MMHUB registers on the Arcturus-era `mmhub_v9_4` path. The header is included by `drivers/gpu/drm/amd/amdgpu/mmhub_v9_4.c` together with the matching `mmhub_9_4_1_offset.h` and `mmhub_9_4_1_sh_mask.h` files, giving the driver a single ASIC-specific source of default register values while the offset and mask headers provide addresses and bitfields.

The assigned range covers the license/header guard and default macros for these address blocks:

- `mmhub_dagb_dagbdec0` through `mmhub_dagb_dagbdec7`, except the range begins after the file header and includes all DAGB0-7 defaults.
- `mmhub_ea_mmeadec0` through `mmhub_ea_mmeadec4` completely.
- The beginning of `mmhub_ea_mmeadec5`, ending at `mmMMEA5_SDP_TAG_RESERVE1_DEFAULT` on line 2930. The remaining MMEA5 defaults and MMEA6/7 are outside this chunk.
- `mmhub_pctldec0`.
- The first MMHUB instance's L1/L2 VM, ATC, shared VM, hypervisor, and performance-counter blocks: `mmhub_l1tlb_vml1dec`, `mmhub_l1tlb_vml1pldec`, `mmhub_l1tlb_vml1prdec`, `mmhub_utcl2_atcl2dec`, `mmhub_utcl2_vml2pfdec`, `mmhub_utcl2_vml2vcdec`, `mmhub_utcl2_vmsharedpfdec`, `mmhub_utcl2_vmsharedvcdec`, `mmhub_utcl2_vmsharedhvdec`, `mmhub_utcl2_atcl2pfcntrdec`, `mmhub_utcl2_atcl2pfcntldec`, `mmhub_utcl2_vml2pldec`, and `mmhub_utcl2_vml2prdec`.

The later duplicated `:1` address blocks for the second MMHUB instance begin after this chunk.

## Register Families

The DAGB blocks define repeated read/write client defaults for eight Data Address Generation/Bus slices. Each `mmDAGB<N>_*_DEFAULT` group has 16 read clients and 16 write clients using the common `0xfe5fe0f9` default, read/write control defaults (`RD_CNTL`, `WR_CNTL`, GMI controls, address DAGB controls), max-burst and lazy-timer defaults, clock-gating control defaults, VC0-VC7 control defaults, pending-status defaults initialized to zero, FIFO empty/full state, credit-full state, performance counters, and reserved registers set to `0xffffffff`. Write-side blocks add write-data DAGB burst/lazy and data/misc credit defaults. These values describe the reset arbitration and buffering posture that the driver later modifies only for selected features such as snoop override and medium-grain clock gating.

The MMEA blocks define memory access and address-decode defaults for external-address or memory-engine slices. MMEA0-4 are complete in this chunk, while MMEA5 is partial. For each complete MMEA instance, the defaults include DRAM, GMI, and IO client-to-group maps; group-to-VC maps; lazy and CAM controls; page/group burst controls; priority aging, queuing, fixed-priority, urgency, urgency masks, and quantum registers; address normalization base/limit/offset windows; DRAM/GMI hole and non-power-of-two channel controls; bank/misc address decode configuration; DRAM/GMI hash and harvest controls; three address decoder subblocks with chip-select base addresses, masks, address selectors, column selectors, and rank-multiplier selectors; SDP arbitration, priority, credits, and reserve defaults; latency sampling; perf counters; EDC counters/mode/status; DSM controls; clock gating; and address decoder selection.

The PCTL0 block provides power/control and state-save defaults for the first MMHUB partition. It includes deepsleep and page-gating override registers, per-slice DAGB busy and deepsleep-allow bits for slices 0-4, UTCL2 and slice misc controls, RENG execute/index/data registers, and STCTRL register-save ranges and exclusion sets. Most dynamic state defaults to zero; exclusion sets default to `0xffffffff`, meaning the save/restore exclusion mask is initially all ones.

The VM and ATC blocks define reset defaults for MMHUB address translation. The L1 TLB status and performance blocks default status and counters to zero. The ATC L2 block defaults control (`ATC_L2_CNTL`, `ATC_L2_CNTL2`, `ATC_L2_CNTL3`, `ATC_L2_MISC_CG`, memory power, clock control, DSM controls, and group runtime classes). The VML2 page-fault block defaults L2 cache control, protection fault policy and status/address registers, identity aperture registers, bank select reserved CIDs, parity control, and clock gating. The VML2 virtual-context block defaults 16 VM context control registers to `0x007ffe80`, exposes context disable and 18 invalidation engine semaphore/request/ack/range registers, and initializes page-table base/start/end registers for VM contexts 0-15 to zero. Shared VM blocks default system/AGP/framebuffer aperture, default-page, steering, local HBM, XGMI, SR-IOV/GPUIOV, IOMMU, ATS, MARC, and active-function registers. Perf counter control/result blocks default counters to zero and result control to `0x04000000`.

## APIs, Types, And Symbols

This header exposes only preprocessor constants. There are no C functions, structs, enums, or runtime control-flow constructs in the chunk. The public surface is the set of `#define mm<REGISTER>_DEFAULT <hex>` macros, guarded by `_mmhub_9_4_1_DEFAULT_HEADER`.

The most driver-visible symbols in this range are the defaults for registers that `mmhub_v9_4.c` reads, modifies, or writes:

- `mmVML2PF0_VM_L2_CNTL_DEFAULT`, `mmVML2PF0_VM_L2_CNTL2_DEFAULT`, `mmVML2PF0_VM_L2_CNTL3_DEFAULT`, and `mmVML2PF0_VM_L2_CNTL4_DEFAULT` seed L2 cache configuration before `REG_SET_FIELD()` applies runtime ASIC policy.
- `mmVML2PF0_VM_L2_PROTECTION_FAULT_CNTL_DEFAULT` and `mmVML2PF0_VM_L2_PROTECTION_FAULT_CNTL2_DEFAULT` are the reset baseline for default-page and no-retry/retry fault handling.
- `mmVML2VC0_VM_CONTEXT<N>_CNTL_DEFAULT`, page-table base/start/end defaults, and invalidation-engine defaults provide the reset values for VM context setup and TLB invalidation plumbing.
- `mmVMSHAREDVC0_MC_VM_MX_L1_TLB_CNTL_DEFAULT`, framebuffer/AGP/system aperture defaults, and `mmVMSHAREDPF0_MC_VM_SYSTEM_APERTURE_DEFAULT_ADDR_*_DEFAULT` are related to system aperture programming.
- `mmATCL2_0_ATC_L2_MISC_CG_DEFAULT` and DAGB `CNTL_MISC2` defaults interact with clock-gating update paths.
- DAGB and MMEA defaults are also coupled to offset arithmetic in the driver, for example the distance between DAGB instances and the split of DAGB slices across MMHUB instances.

## Control Flow And Runtime Use

The file itself has no control flow. Its values become part of runtime control flow when included by `mmhub_v9_4.c`. The main runtime sequence is `mmhub_v9_4_gart_enable()`, which loops over two MMHUB instances and programs GART apertures, system apertures, L1 TLB, L2 cache, DAGB snoop override, system VM domain, identity aperture, VMID context configuration, and invalidation ranges.

Several of those routines read hardware registers rather than writing defaults verbatim, then use reset defaults as known baselines when the current hardware value is not the desired seed. `mmhub_v9_4_init_cache_regs()` explicitly starts from `mmVML2PF0_VM_L2_CNTL3_DEFAULT` and `mmVML2PF0_VM_L2_CNTL4_DEFAULT` before selecting bank and fragment-size fields based on `adev->gmc.translate_further`. VM context setup uses the VML2VC register family defined here and address distances derived from the offset header. Fault control paths update `mmVML2PF0_VM_L2_PROTECTION_FAULT_CNTL` fields to either redirect faults to the default page or crash on retry/no-retry faults.

The DAGB defaults feed lower-level assumptions in two driver paths. `mmhub_v9_4_init_snoop_override_regs()` iterates DAGB slices, with a comment stating DAGB0-4 belong to hub0 and DAGB5-7 to hub1, and sets SDMA snoop override bits. `mmhub_v9_4_update_medium_grain_clock_gating()` uses DAGB register spacing and toggles clock-gating disable masks for per-slice DAGB control registers. The default values in this chunk establish the reset state against which those feature toggles operate.

## State And Persistence Behavior

The header is static build-time data and persists only as compiled constants in the kernel object. It does not allocate memory, hold locks, perform I/O, or persist state on disk.

The hardware registers described by the macros are volatile MMIO state. Many reset defaults are intentionally overwritten during GPU initialization, resume, VM setup, SR-IOV handling, fault policy changes, clock-gating changes, and TLB invalidation. Page-table base/start/end registers, context controls, invalidation engines, aperture registers, and fault-address/status registers reflect live GPU VM state after initialization, not the zero defaults in this header. Performance counters and status registers default to zero but become hardware-updated observation points once enabled.

Power-management and state-save registers in PCTL0 are persistence-adjacent for suspend/resume and deep-sleep flows. Their defaults describe what the hardware exposes at reset, while driver-managed save/restore policies can change which register ranges are captured or excluded.

## Dependencies And Integration Points

This header depends on generated register naming consistency across the MMHUB 9.4.1 header set. The macro names must line up with:

- `mmhub_9_4_1_offset.h` for register addresses and instance spacing.
- `mmhub_9_4_1_sh_mask.h` for fields consumed by `REG_SET_FIELD()` and mask constants.
- `mmhub_v9_4.c` for runtime MMHUB initialization, GART enable/disable, VM context programming, cache and fault setup, snoop overrides, and clock-gating control.
- SOC15 register access helpers such as `RREG32_SOC15_OFFSET()`, `WREG32_SOC15_OFFSET()`, and `SOC15_REG_OFFSET()`.
- Core AMDGPU state in `struct amdgpu_device`, including `adev->gmc`, `adev->vmhub`, `adev->vm_manager`, `adev->cg_flags`, and SR-IOV mode.

The default macros are ASIC-specific ABI between generated register databases and handwritten driver code. Changing a default constant can alter boot-time MMIO programming even if no C logic changes. Renaming a macro or moving it between generated variants can break compilation where `mmhub_v9_4.c` references the symbol directly.

## Risks And Edge Cases

- The chunk is generated-looking, repetitive hardware data. Manual edits are high risk because a one-digit hex change can silently alter arbitration, credit, cache, fault, or clock-gating behavior.
- The assigned range ends mid-`mmhub_ea_mmeadec5`. A chunk-level report must not imply that all MMEA5 defaults were reviewed here; the rest of MMEA5 and MMEA6/7 are covered by later chunks.
- The header contains per-instance repetition rather than arrays. Driver loops infer instance distances from offset symbols, so missing or inconsistent instance-specific defaults can be hard to spot by type checking alone.
- Some registers are status/counter/live hardware registers even though a default macro exists. Tests that compare runtime values to `*_DEFAULT` after initialization would be wrong for VM context, invalidation, fault, aperture, counter, FIFO, and status registers.
- SR-IOV and GPU virtualization paths use shared/hypervisor VM registers from this range. Defaulting these incorrectly can affect guest aperture setup, ATS/IOMMU behavior, GPUIOV/XGMI handling, or fault isolation.
- Clock-gating defaults interact with runtime power-management decisions. Inconsistent `CGTT_CLK_CTRL`, ATC L2 misc clock-gating, or DAGB `CNTL_MISC2` defaults can produce hangs that appear as timing or power-state bugs rather than obvious register mismatches.
- Fault-control defaults are security and reliability sensitive. Protection fault masks, default fault addresses, and no-retry/retry behavior determine whether bad GPU VM accesses are contained, redirected, retried, or surfaced as fatal faults.

## Test Signals

Useful validation for this chunk is mostly integration and hardware-oriented:

- Build coverage for `drivers/gpu/drm/amd/amdgpu/mmhub_v9_4.c` with this header included, confirming every referenced `mm..._DEFAULT` macro still resolves.
- Generated-header consistency checks comparing default, offset, and shift/mask headers for the same MMHUB 9.4.1 register database, including duplicate instance blocks and expected address-block ordering.
- Boot or resume testing on MMHUB 9.4 hardware that exercises `mmhub_v9_4_gart_enable()`, VMID setup, invalidation engines, page-table base programming, and GART access.
- VM fault tests that toggle `set_fault_enable_default`, validate dummy/default-page redirection, and inspect `VM_L2_PROTECTION_FAULT_STATUS` and fault address registers.
- TLB/cache tests that verify `VM_L2_CNTL3` and `VM_L2_CNTL4` programming for both `translate_further` and non-`translate_further` configurations.
- SR-IOV/virtualization tests that cover shared/hypervisor VM aperture, ATS/IOMMU, and GPUIOV defaults.
- Clock-gating and power-management tests that enable/disable medium-grain clock gating and deep-sleep paths while running SDMA and MMHUB traffic, watching for hangs, FIFO/credit anomalies, and counter behavior.
