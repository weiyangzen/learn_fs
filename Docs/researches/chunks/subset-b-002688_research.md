# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_3_sh_mask.h lines 7181-9540

## Scope

This chunk covers generated shift and mask definitions from the GC 9.4.3 AMD GPU register mask header. It starts inside the `GCEA_IO_WR_PRI_AGE` family, continues through GCEA arbitration, SDP, MAM, DSM, probe, performance counter, and error-status fields, then covers RMI control/status fields, ATC L2 fields, VM L2 fault/cache fields, and ends in the UTCL2/VML2 correctable-error status families at `UTCL2_CE_ERR_STATUS_HI`.

The chunk contains preprocessor constants only. In this range there are 2,182 `#define` entries across 164 register groups: 1,090 `__SHIFT` constants and 1,092 `_MASK` constants. It does not define C functions, structs, variables, storage, or executable control flow.

## Purpose

The purpose of this header section is to provide the bit-level ABI between AMDGPU driver code and GC 9.4.3 hardware registers. Each field is represented by the generated convention:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset for encoding or decoding the field.
- `<REGISTER>__<FIELD>_MASK`, the 32-bit mask that isolates the field in a register value.

Driver code combines these constants with register helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15`, and `SOC15_REG_OFFSET`. The sibling `gc_9_4_3_offset.h` header supplies the register addresses; this file supplies the field layout for those addresses.

## Important Macro Families

### GCEA priority, arbitration, SDP, and performance fields

The first part of the chunk is dominated by Graphics Core EA (`GCEA_*`) fields:

- IO read/write priority aging, queuing, fixed-priority, urgency, urgency masking, and quantized-priority threshold fields. These encode group coefficients, group thresholds, and per-client-ID masks for up to 32 CIDs.
- `GCEA_SDP_ARB_DRAM`, `GCEA_SDP_ARB_FINAL`, `GCEA_SDP_DRAM_PRIORITY`, `GCEA_SDP_IO_PRIORITY`, `GCEA_SDP_CREDITS`, tag reserve, VCC reserve, VCD reserve, request-control, enable, and backdoor credit fields. These describe arbitration and credit allocation between DRAM, GMI, IO, return, command, and data paths.
- `GCEA_MISC` and `GCEA_MISC2`, with debug, arbitration, clock, interrupt, switch, bypass, and error-reporting knobs.
- `GCEA_LATENCY_SAMPLING`, `GCEA_PERFCOUNTER_LO/HI`, `GCEA_PERFCOUNTER0_CFG`, `GCEA_PERFCOUNTER1_CFG`, and `GCEA_PERFCOUNTER_RSLT_CNTL`, which expose local sampling and performance-counter selection, mode, enable, clear, trigger, and result-control fields.
- `GCEA_MAM_CTRL` and `GCEA_MAM_CTRL2`, covering ADRAM/ARAM modes, flush controls, ALOG activity/filtering, SDP priority, client ID, address high bits, and MAM disable behavior.

These fields are used to tune or observe GPU memory fabric behavior. Many are low-level hardware scheduler controls rather than normal user-facing policy.

### GCEA DSM and ECC/error-status support

The DSM families `GCEA_DSM_CNTL`, `GCEA_DSM_CNTLA`, `GCEA_DSM_CNTLB`, `GCEA_DSM_CNTL2`, `GCEA_DSM_CNTL2A`, and `GCEA_DSM_CNTL2B` define diagnostic single-write, irritator-data, error-injection, inject-delay, and inject-delay-select fields for DRAM, GMI, IO, return-tag, page memory, and MAM data/address memories.

The GCEA error-status groups include:

- `GCEA_UE_ERR_STATUS_LO/HI`, with valid flags, address, memory ID, ECC/parity indicators, error info, uncorrectable error count, FED count, and reserved bits.
- `GCEA_CE_ERR_STATUS_LO/HI`, with similar low/high address, memory ID, ECC/other indicators, correctable error count, poison, and reserved bits.
- `GCEA_ERR_STATUS`, `GCEA_PROBE_CNTL`, and `GCEA_PROBE_MAP`, which expose additional probe and error-status surfaces.

These macros are integration points for RAS, diagnostics, and validation code. Writes to DSM control fields can deliberately inject or alter error behavior and therefore must be guarded by the owning debug/RAS path.

### RMI control, status, xbar, TCIW, and scoreboard fields

The chunk next covers the RMI address block. Important groups include:

- `RMI_GENERAL_CNTL`, `RMI_GENERAL_CNTL1`, and `RMI_GENERAL_STATUS`, describing global control and status for RMI busy/error conditions, skid FIFO over/underflow, xbar, UTCL1, scoreboard, TCIW formatter, write/read request FIFO, UTC probe, XNACK, and FIFO occupancy flags.
- `RMI_SUBBLOCK_STATUS0..3`, exposing probe FIFO, TCIW inflight, skid FIFO free-space, PRT FIFO occupancy, and aggregate free-space fields.
- `RMI_XBAR_CONFIG`, `RMI_XBAR_ARBITER_CONFIG`, and `RMI_XBAR_ARBITER_CONFIG_1`, which configure crossbar muxing, xbar input enables, arbiter mode, stalls, break-on-idle/weighted-round-robin behavior, stall timer start values, and round-robin weights for RB0/RB1 read/write traffic.
- `RMI_PROBE_POP_LOGIC_CNTL`, `RMI_UTC_XNACK_N_MISC_CNTL`, and `RMI_DEMUX_CNTL`, covering probe FIFO depth, XNACK timers, UTCL1 permission mode, CP VMID reset disable, demux arbitration, and demux stall timers.
- `RMI_UTCL1_CNTL1`, `RMI_UTCL1_CNTL2`, `RMI_UTC_UNIT_CONFIG`, `RMI_UTCL1_STATUS`, and `RMI_XNACK_DEBUG`, describing UTCL1 response modes, GPUVM defaults, invalidation toggles, forced miss/order/snoop/ack behavior, EDC disable, shootdown options, perf-event filters, TMZ request enablement, status, and XNACK debug fields.
- `RMI_TCIW_FORMATTER0_CNTL` and `RMI_TCIW_FORMATTER1_CNTL`, with write-combine disable/timeout, max inflight request, skid FIFO delta update, safe mode, reorder disable, last-of-burst behavior, and all-fault return-data controls.
- `RMI_SCOREBOARD_CNTL` and `RMI_SCOREBOARD_STATUS0..2`, which expose completion flush controls, VMID invalidation override/force behavior, session IDs, invalidation progress/done state, running/snapshot counters, underflow/overflow indicators, and timestamp/completion flush state.
- `RMI_CLOCK_CNTRL` and `RMI_SPARE*`, which provide dynamic clock busy/wakeup masks and spare override/debug fields.

These fields sit near memory translation, request routing, and VMID invalidation handling. Misprogramming them can affect ordering, invalidation completion, fault return behavior, and fabric-level deadlock risk.

### ATC L2 cache, DSM, power, clock, and error fields

The `ATC_L2_*` register families define address-translation cache L2 behavior:

- `ATC_L2_CNTL`, `ATC_L2_CNTL2`, `ATC_L2_CNTL3`, and `ATC_L2_CNTL4`, covering cache enable/fragment-processing style controls, status, invalidation, update behavior, request shaping, associativity/effective size, force-miss bits, and additional control fields.
- `ATC_L2_CACHE_DATA0..3`, `ATC_L2_CACHE_4K_DSM_INDEX`, `ATC_L2_CACHE_32K_DSM_INDEX`, `ATC_L2_CACHE_2M_DSM_INDEX`, and matching `*_DSM_CNTL` registers, which define diagnostic scan/access fields for cache data and DSM controls.
- `ATC_L2_STATUS` and `ATC_L2_STATUS2`, for busy and status reporting.
- `ATC_L2_MISC_CG`, `ATC_L2_MEM_POWER_LS`, and `ATC_L2_CGTT_CLK_CTRL`, which expose clock-gating and memory power/light-sleep controls.
- `ATC_L2_MM_GROUP_RT_CLASSES`, which maps memory-management groups to real-time classes.
- `ATC_L2_UE_ERR_STATUS_LO/HI` and `ATC_L2_CE_ERR_STATUS_LO/HI`, which mirror the UE/CE error-reporting layout used by other memory blocks: valid/address flags, address, memory ID, ECC/parity/other indicators, error info, counters, poison, FED, and reserved fields.

### VM L2 cache, protection fault, identity aperture, and bank-selection fields

The `VM_L2_*` portion is one of the key driver-facing parts of this chunk:

- `VM_L2_CNTL`, `VM_L2_CNTL2`, `VM_L2_CNTL3`, `VM_L2_CNTL4`, and `VM_L2_CNTL5` define VM L2 cache enablement, fragment processing, endian swap modes, LRU update behavior, default-page behavior, split modes, queue sizes, PDE fault classification, context-1 identity access mode, identity fragment size, PTE address mode, L1/L2 invalidation controls, cache update mode, bank selection, effective sizes, force-miss bits, MM IFIFO limits, BPM/clock-gating overrides, and walker fetch MTYPE/noalloc enablement.
- `VM_L2_STATUS` exposes L2 busy state, per-context-domain busy bits, and PTE/PDE parity-error indicators.
- `VM_DUMMY_PAGE_FAULT_CNTL` and `VM_DUMMY_PAGE_FAULT_ADDR_LO32/HI32` define dummy page fault enablement and comparison address fields.
- `VM_L2_PROTECTION_FAULT_CNTL`, `VM_L2_PROTECTION_FAULT_CNTL2`, `VM_L2_PROTECTION_FAULT_MM_CNTL3`, and `VM_L2_PROTECTION_FAULT_MM_CNTL4` configure which fault classes produce status updates or interrupts, including range, PDE0/1/2, translate-further, NACK, dummy-page, valid, read, write, execute, no-retry client ID, retry fault, active page migration PTE, and VML1 read/write client masks.
- `VM_L2_PROTECTION_FAULT_STATUS` decodes fault state: more faults, walker error, permission fault class, mapping error, client ID, read/write, atomic, VMID, VF, VFID, UCE, and FED.
- `VM_L2_PROTECTION_FAULT_ADDR_*` and `VM_L2_PROTECTION_FAULT_DEFAULT_ADDR_*` expose faulting logical page address and default physical page address halves.
- `VM_L2_CONTEXT1_IDENTITY_APERTURE_*` and `VM_L2_CONTEXT_IDENTITY_PHYSICAL_OFFSET_*` define the identity aperture and physical offset used for context-1 identity mappings.
- `VM_L2_MM_GROUP_RT_CLASSES`, `VM_L2_BANK_SELECT_RESERVED_CID`, and `VM_L2_BANK_SELECT_RESERVED_CID2` provide group real-time class bits and reserved read/write client-ID bank-selection controls.
- `VM_L2_CACHE_PARITY_CNTL`, `VM_L2_CGTT_CLK_CTRL`, and `VM_L2_CGTT_BUSY_CTRL` define parity handling and clock-gating busy/wakeup behavior.

This family is central to page-table cache behavior, TLB/cache invalidation, VM fault reporting, and SR-IOV-aware fault attribution.

### VML2, VML2 walker, and UTCL2 ECC/EDC fields

The tail of the chunk defines ECC and EDC control/status for VM L2, the VM L2 walker, and UTCL2:

- `VML2_MEM_ECC_INDEX`, `VML2_WALKER_MEM_ECC_INDEX`, and `UTCL2_MEM_ECC_INDEX` select the memory instance or index for ECC controls.
- `VML2_MEM_ECC_CNTL`, `VML2_WALKER_MEM_ECC_CNTL`, and `UTCL2_MEM_ECC_CNTL` define inject delay, DSM irritator data, single-write enable, error-injection enable, delay selection, SEC/DED counters, write-counters strobe, and test-FUE flags.
- `VML2_MEM_ECC_STATUS`, `VML2_WALKER_MEM_ECC_STATUS`, and `UTCL2_MEM_ECC_STATUS` expose UCE and FED status bits.
- `UTCL2_EDC_MODE` and `UTCL2_EDC_CONFIG` define force-SEC-on-DED, FED counting, FUE gating, DED mode, FED propagation, bypass, write disable, and EDC disable behavior.
- `VML2_UE_ERR_STATUS_*`, `VML2_WALKER_UE_ERR_STATUS_*`, `UTCL2_UE_ERR_STATUS_*`, `VML2_CE_ERR_STATUS_*`, `VML2_WALKER_CE_ERR_STATUS_*`, and `UTCL2_CE_ERR_STATUS_*` expose uncorrectable and correctable error detail fields. The low registers carry valid/address flags, address, and memory ID. The high registers carry ECC/parity/other indicators, valid error-info, error-info payload, UE/CE count, FED count or poison, and reserved bits.

These fields are RAS-oriented and are tightly coupled to the hardware error collection and injection flows.

## Control Flow and State Behavior

This header has no executable control flow. Its influence is compile-time: C code includes the header and uses the constants to compose, read, and decode 32-bit MMIO register values.

The state represented by this chunk is hardware state, not software persistence inside the header. Important state surfaces include priority/arbitration policy, SDP credits, performance counter configuration/results, MAM/ALOG configuration, DSM error-injection controls, GCEA/ATC/VML2/UTCL2 error status, RMI FIFOs and xbar/scoreboard status, UTCL1 invalidation and XNACK controls, ATC L2 cache and DSM state, VM L2 cache/invalidation/fault status, identity aperture registers, and ECC/EDC control/status.

Some fields are durable configuration bits, some are latched or sticky status bits, and some are command/strobe-like fields. Examples include cache invalidation bits in `VM_L2_CNTL2`, protection-fault clear/update controls in `VM_L2_PROTECTION_FAULT_CNTL`, DSM error-injection enable and write-counter bits, RMI invalidation toggles, scoreboard flush controls, and clock-gating/busy mask fields. Correct use depends on the owning driver sequence and hardware spec; the generated macros do not encode polling, ordering, locking, or timeout policy.

## Dependencies and Integration Points

This chunk depends on the AMD generated register-header convention:

- `gc_9_4_3_offset.h` provides register address names for the field names defined here.
- Other generated GC 9.4.3 headers, especially defaults and registers under `include/asic_reg/gc/`, provide reset values and related register metadata.
- AMDGPU register helpers consume the `__SHIFT` and `_MASK` definitions through `REG_SET_FIELD`, `REG_GET_FIELD`, direct mask/shift expressions, and SOC15 read/write helpers.

Concrete include points in this tree include `amdgpu/gfxhub_v1_2.c`, `amdgpu/gfx_v9_4_3.c`, `amdgpu/amdgpu_amdkfd_gc_9_4_3.c`, and `amdkfd/kfd_device_queue_manager_v9.c`, all of which include GC 9.4.3 offset/mask headers for this ASIC generation.

Observed cross-file integration for the VM fault fields includes `amdgpu/gmc_v9_0.c`, which decodes `VM_L2_PROTECTION_FAULT_STATUS` with `REG_GET_FIELD` for fields such as `CID`, `RW`, `FED`, `MORE_FAULTS`, `WALKER_ERROR`, `PERMISSION_FAULTS`, and `MAPPING_ERROR`. GC 9.4.3-specific gfxhub and KFD paths use the same field/header pattern when configuring VM, queue, and fault behavior for this generation.

## Risks

- Bitfield drift is high impact. A wrong shift or mask can write unrelated hardware fields, causing bad VM fault attribution, cache invalidation failures, hangs, incorrect RAS reporting, or silent performance/debug misconfiguration.
- The file is generated and repetitive. Similar-looking priority, DSM, ECC, and status families have small layout differences, so hand edits or mechanical regeneration mistakes are hard to review by eye.
- GCEA and SDP arbitration/credit fields affect memory fabric scheduling. Incorrect values can starve traffic classes or distort performance measurements.
- DSM and ECC injection controls can intentionally create hardware error conditions. They must stay confined to RAS/debug validation flows.
- RMI and UTCL1 controls are close to VM invalidation, XNACK, request routing, and scoreboard completion. Incorrect sequencing can produce stale translations, false completion, FIFO pressure, or deadlock-prone routing behavior.
- VM L2 fault control and status fields are driver-visible diagnostics. If these masks are wrong, logs may report the wrong client, VMID, VF/VFID, access type, or fault class, making recovery and isolation unreliable.
- Cache, parity, clock-gating, and power fields must match hardware topology and firmware policy. Treating debug or clock-gating masks as ordinary runtime knobs can destabilize bring-up, suspend/resume, reset, or SR-IOV operation.
- The chunk starts after the first `GCEA_IO_RD_PRI_AGE` definitions and continues from the preceding chunk's register family. A merged per-file report should connect this document with neighboring chunks for the complete GCEA priority family.

## Test and Validation Signals

Useful validation is mostly integration-oriented:

- Build AMDGPU and KFD code paths that include `gc/gc_9_4_3_sh_mask.h`; this catches missing, renamed, or syntactically malformed macros.
- Exercise GC 9.4.3 VM fault handling and confirm `VM_L2_PROTECTION_FAULT_STATUS` logs decode CID, RW, VMID, VF/VFID, FED/UCE, permission, mapping, walker, and more-fault fields correctly.
- Run GPU reset, suspend/resume, and VM cache invalidation tests to cover `VM_L2_CNTL*`, `VM_L2_STATUS`, RMI scoreboard, and UTCL1 invalidation-related fields.
- Run KFD queue and GPUVM workloads on GC 9.4.3 hardware to stress RMI request routing, VMID invalidation, XNACK, and protection-fault paths.
- Run RAS validation for GCEA, ATC L2, VML2, VML2 walker, and UTCL2 UE/CE/ECC/EDC fields, including controlled error injection where supported.
- Run performance/debug tests that configure GCEA performance counters and latency sampling, verifying counter selection, enable/clear, result-control, and trigger fields.
- For SR-IOV or partitioned deployments, validate that VM fault attribution and RMI/VM L2 behavior remain correct for VF/VFID and reserved-client-ID bank-selection fields.
