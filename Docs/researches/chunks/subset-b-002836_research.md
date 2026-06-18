# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_default.h lines 2931-3933

## Scope And Purpose

This chunk is the final region of the generated AMD MMHUB 9.4.1 default-register header. It starts in the tail of the `mmhub_ea_mmeadec5` address block, covers full default sets for `mmhub_ea_mmeadec6` and `mmhub_ea_mmeadec7`, then covers instance-1 MMHUB power/control, L1 TLB, ATC L2, VM L2, shared VM aperture, hypervisor/SR-IOV, and performance-counter blocks through the header guard close.

The file has no executable C logic. Its purpose is to publish ASIC reset/default values as preprocessor constants named `mm<REGISTER>_DEFAULT`. These constants sit beside the matching `mmhub_9_4_1_offset.h` register offsets and `mmhub_9_4_1_sh_mask.h` field masks. The consuming driver code in `amdgpu/mmhub_v9_4.c` includes all three generated headers and programs or inspects MMHUB registers through SOC15 register helpers.

Within this slice there are 953 `#define` constants: 617 zero defaults and 336 non-zero defaults. The most behaviorally important non-zero groups are the MMEA6/MMEA7 arbitration defaults, PCTL1 power-control defaults, ATC L2 and VM L2 control defaults, VM context defaults for 16 VMIDs, invalidation-engine request defaults for 18 engines, shared aperture defaults, and perf-counter result-control defaults.

## Register Blocks Covered

The first 26 definitions complete `mmMMEA5_*` defaults. They include SDP request/control values, `MISC`, performance counter result control, clock-gating control, and error-status defaults for MMEA5.

`mmhub_ea_mmeadec6` contributes 233 `mmMMEA6_*` defaults. The block defines default DRAM, GMI, and IO client-to-group mappings; group-to-virtual-channel maps; lazy timers; CAM controls; page-burst controls; priority aging, queuing, fixed-priority, urgency, urgency masking, and priority quantum registers; address-normalization windows and hole controls; DRAM/GMI address hash controls; chip-select address decoder defaults for decoders 0-2; SDP arbitration, credits, tag/VC reserves, and request controls; latency/performance counter registers; EDC/DSM registers; clock-gating control; error status; and address-decoder selection.

`mmhub_ea_mmeadec7` mirrors the MMEA6 default pattern for another engine/address decoder instance. It has the same 233-register shape and the same prominent default constants: DRAM client maps use `0x55555555`, IO client maps use `0xe4e4e4e4`, DRAM/GMI lazy timers use `0x78000924`, CAM control uses `0x16db4444`, page-burst uses `0x20002000`, priority quantums use `0x3f3f3f3f`, `0x7f7f7f7f`, and `0xffffffff`, address masks use `0xfffffffe`, address config/select values use `0x00050408`, `0x04076543`, `0x00000008`, `0x87654321`, and `0xa9876543`, and SDP request/credit/arbitration defaults are non-zero.

`mmhub_pctldec1` contributes 87 `mmPCTL1_*` defaults for MMHUB power/deep-sleep control. Most runtime and save-range values default to zero, but `mmPCTL1_CTRL_DEFAULT` is `0x00011040`, UTCL2 and slice misc registers have non-zero defaults, and every UTCL2/slice save-exclusion set defaults to `0xffffffff`.

`mmhub_l1tlb_vml1dec:1`, `mmhub_l1tlb_vml1pldec:1`, and `mmhub_l1tlb_vml1prdec:1` describe instance-1 L1 TLB status, TMZ control, and L1 performance counter registers. Statuses and counter values default to zero; `mmVML1PL1_MC_VM_MX_L1_PERFCOUNTER_RSLT_CNTL_DEFAULT` defaults to `0x04000000`.

`mmhub_utcl2_atcl2dec:1` defines ATC L2 instance-1 control/cache defaults. Key non-zero values include `ATC_L2_CNTL` `0x0001c0c9`, `ATC_L2_CNTL2` `0x00600100`, `ATC_L2_CNTL3` `0x000001f8`, clock/memory low-power controls, and MM group real-time class `0x00000005`.

`mmhub_utcl2_vml2pfdec:1` defines VM L2 protection-fault and control defaults. Important values include `VM_L2_CNTL` `0x00080602`, `VM_L2_CNTL3` `0x80100007`, dummy-page-fault control `0x00000090`, protection-fault controls `0x3ffffffc` and `0x000a0000`, MM protection fault masks at `0xffffffff`, `VM_L2_CNTL4` `0x000000c1`, and L2 clock-gating control `0x00000080`.

`mmhub_utcl2_vml2vcdec:1` is the largest VM-addressing group in this slice. It defines 16 VM context control defaults, 18 invalidate-engine semaphore/request/ack triples, 18 invalidate address ranges, and page-table base/start/end address pairs for VM contexts 0-15. Context controls default to `0x007ffe80`; invalidate requests default to `0x017c0000`; most semaphores, acknowledgements, ranges, and page-table addresses default to zero.

`mmhub_utcl2_vmsharedpfdec:1`, `mmhub_utcl2_vmsharedvcdec:1`, and `mmhub_utcl2_vmsharedhvdec:1` define shared VM aperture, frame-buffer, PCI, HBM, XGMI, SR-IOV, IOMMU, ATS, MARC, and active-function defaults. Non-zero defaults include PCI arbiter VGA-hole bit `0x00000008`, steering `0x00000001`, memory low-power timing `0x00000208`, local HBM end `0x000fffff`, shared L1 TLB control `0x00002501`, IOMMU MMIO control `0x00000100`, and UTCL2 clock control `0x00000080`.

The chunk ends with instance-1 ATC L2 and VM L2 performance counter blocks: `mmATCL2PFCNTR1_*`, `mmATCL2PFCNTL1_*`, `mmVML2PL1_*`, and `mmVML2PR1_*`. Counter storage/configuration defaults to zero, while result-control defaults use `0x04000000`.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, or inline helpers in this chunk. The public interface is the generated macro namespace:

- `mmMMEA5_*_DEFAULT`, `mmMMEA6_*_DEFAULT`, and `mmMMEA7_*_DEFAULT` publish memory-engine arbitration, address-decoder, EDC, DSM, and performance defaults.
- `mmPCTL1_*_DEFAULT` publishes MMHUB instance-1 power/deep-sleep and state-save defaults.
- `mmVML1_1_*_DEFAULT`, `mmVML1PL1_*_DEFAULT`, and `mmVML1PR1_*_DEFAULT` publish L1 TLB status and performance defaults.
- `mmATCL2_1_*_DEFAULT`, `mmATCL2PFCNTR1_*_DEFAULT`, and `mmATCL2PFCNTL1_*_DEFAULT` publish ATC L2 control/cache/performance defaults.
- `mmVML2PF1_*_DEFAULT`, `mmVML2VC1_*_DEFAULT`, `mmVML2PL1_*_DEFAULT`, and `mmVML2PR1_*_DEFAULT` publish VM L2 protection, context, invalidation, page-table, and performance defaults.
- `mmVMSHAREDPF1_*_DEFAULT`, `mmVMSHAREDVC1_*_DEFAULT`, and `mmVMSHAREDHV1_*_DEFAULT` publish shared physical/function, virtual/context, and hypervisor/SR-IOV defaults.

The macros are intended to align one-to-one with register names in `mmhub_9_4_1_offset.h` and field names in `mmhub_9_4_1_sh_mask.h`. Any rename, insertion, or generated-value drift must preserve that cross-header contract.

## Control Flow

This header has no direct control flow. The implicit initialization flow is:

1. Hardware resets MMHUB registers to ASIC-defined values reflected by this default header.
2. `amdgpu/mmhub_v9_4.c` includes the default, offset, and shift/mask headers for the MMHUB 9.4.1 register model.
3. Runtime setup code reads or writes selected registers through helpers such as `RREG32_SOC15`, `RREG32_SOC15_OFFSET`, `WREG32_SOC15_OFFSET`, `SOC15_REG_ENTRY`, and `SOC15_REG_FIELD`.
4. Driver initialization programs VM apertures, page-table bases, system apertures, TLB controls, protection-fault behavior, clock/power controls, and RAS/EDC monitoring where runtime state must override reset defaults.

The repeated instance-1 naming in this slice matters. The runtime MMHUB v9.4 code handles multiple MMHUB instances with an instance register offset, so defaults for `*1` blocks must stay consistent with corresponding `*0` blocks elsewhere in the same generated header unless the ASIC intentionally differs.

## State And Persistence Behavior

The constants themselves are compile-time state and do not persist anything at runtime. They document persistent hardware reset state and provide a reference for driver code, diagnostics, register dumps, RAS handling, or generated validation that compares programmed values with expected defaults.

Most address and page-table fields default to zero, which means runtime code must install real GPU addresses before normal operation. This includes GART page-table base/start/end fields, protection-fault default addresses, system aperture defaults, framebuffer locations, and AGP aperture registers.

The VM context and invalidation defaults are persistent hardware policy until reprogrammed: all 16 `VML2VC1_VM_CONTEXT*_CNTL` values begin at `0x007ffe80`, and all 18 invalidate engine request registers begin at `0x017c0000`. Incorrect defaults here can affect VMID enablement, fault behavior, invalidate semantics, and TLB coherency before or during driver initialization.

MMEA6/MMEA7 EDC counters, DSM controls, and performance counters default to zero, while error-status registers default to `0x00000300`. RAS code in `mmhub_v9_4.c` references MMEA6/MMEA7 EDC counters and error-status registers through the matching offset/mask headers, so these defaults are part of the expected clean baseline for error accounting.

Power-management defaults also have persistence implications. PCTL1 save-exclusion masks at `0xffffffff`, UTCL2/slice misc defaults, ATC L2 memory low-power defaults, and clock-gating defaults define the initial state that suspend/resume, deep-sleep, and clock-gating code must either honor or explicitly override.

## Dependencies And Integration Points

This header depends only on the C preprocessor, but it is tightly integrated with the generated MMHUB register family:

- `mmhub_9_4_1_offset.h` maps the same register names to MMIO offsets and base indices.
- `mmhub_9_4_1_sh_mask.h` maps the same register names to field shifts and masks.
- `amdgpu/mmhub_v9_4.c` includes this default header with the offset and mask headers, then uses SOC15 helpers for MMHUB initialization, VM setup, protection-fault programming, TLB handling, and RAS/EDC register tables.
- AMDGPU GMC/VM code supplies runtime addresses and VMID state that replace the zero page-table, aperture, AGP, framebuffer, scratch-page, and fault-address defaults.
- SR-IOV and GPU virtualization paths depend on `VMSHAREDHV1_*`, per-VF framebuffer size/offset defaults, active-function state, IOMMU/ATS defaults, XGMI GPUIOV enable defaults, and shared virtual reset registers.
- RAS integration uses MMEA6/MMEA7 EDC counters and error-status registers to expose correctable/uncorrectable error state.

These constants are generated hardware-interface data. They should not be edited by hand unless the corresponding ASIC register specification and generated offset/mask headers are updated consistently.

## Risks And Edge Cases

The largest correctness risk is silent drift between default, offset, and shift/mask headers. Because all names are preprocessor macros, a stale default can compile cleanly while documenting or driving the wrong reset expectation.

Repeated register families increase copy/paste and generation risk. MMEA6 and MMEA7 are nearly identical; VM context 0-15 and invalidation engine 0-17 entries are repetitive. A single missing context, swapped engine index, or inconsistent value can break only one VMID or invalidate engine and be difficult to isolate.

Address and aperture defaults are mostly zero. Code that assumes reset values are already valid would route memory transactions to address zero or leave VM ranges unprogrammed. Runtime initialization must remain the source of truth for page-table bases, aperture limits, framebuffer locations, and fault target addresses.

Non-zero arbitration and priority defaults directly shape MMHUB traffic behavior. Changes to DRAM/GMI/IO group mappings, urgency masks, quantum values, or SDP credits may affect fairness, latency, bandwidth, or deadlock avoidance. Such changes require hardware validation, not just compilation.

VM/TLB defaults are sensitive. Context control `0x007ffe80`, L2 control/protection defaults, invalidate request `0x017c0000`, ATC L2 controls, and shared TLB control influence address translation, ATS/IOMMU interaction, invalidation completion, and page-fault handling.

RAS and diagnostic code can treat zero/non-zero counter and status defaults as baseline assumptions. If EDC counter reset values or error-status defaults change unexpectedly, error reporting may show false positives, miss initial faults, or clear hardware state incorrectly.

Instance numbering is another hazard. This chunk is dominated by `*1` blocks, while runtime code often computes instance offsets from base instance-0 register names. Any mismatch between generated instance-1 offsets/defaults and runtime instance-offset arithmetic can produce wrong-register access.

## Test Signals

Build-level signals are basic but important: the AMDGPU tree must compile with this header included by `amdgpu/mmhub_v9_4.c`, and all referenced default macros must remain syntactically valid integer constants.

Generated-header consistency checks should verify that every `mm..._DEFAULT` macro in this chunk has a corresponding offset macro and a corresponding set of shift/mask definitions where applicable. This is especially important for MMEA6/MMEA7 EDC registers, VM context arrays, invalidate engine arrays, and shared VM aperture blocks.

Runtime smoke tests should exercise MMHUB initialization on MMHUB v9.4.1 ASICs: GART setup, VMID page-table programming, system aperture programming, TLB invalidation, protection-fault handling, suspend/resume, clock/power gating, and SR-IOV paths where available.

RAS test signals should read MMEA6/MMEA7 EDC counters and error-status registers before and after injected or simulated events, confirming reset baselines and counter field interpretation.

Register-dump or golden-register tests can compare post-reset hardware values against this header before driver reprogramming. Differences should be triaged as ASIC stepping changes, generated-header drift, firmware side effects, or driver initialization ordering.

Performance and stress signals should cover memory traffic through DRAM, GMI, and IO paths because the non-zero MMEA arbitration, priority, and SDP defaults can change latency and fairness without producing immediate functional failures.
