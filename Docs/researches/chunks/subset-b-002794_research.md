# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_2_3_0_sh_mask.h lines 4719-7196

## Scope

This chunk is a middle segment of the generated AMD MMHUB 2.3.0 shift/mask header. It covers line 4719 through line 7196 and defines 1,069 `__SHIFT` macros and 1,054 `_MASK` macros across 334 visible register comments. The range begins at the tail of `MMEA0_LATENCY_SAMPLING`, then covers MMEA0 monitoring and error-control registers, MMHUB power-control (`PCTL`) registers, L1 TLB stream and fault registers, SAW/L2 VM context registers, ATC L2 cache registers, and the beginning of MMVM L2 protection-fault control. It ends inside `MMVM_L2_PROTECTION_FAULT_CNTL`, before that register's remaining `CRASH_ON_RETRY_FAULT` shift and mask definitions.

The content is declarative only. There are no C functions, structs, enums, allocations, branches, loops, locks, or local side effects. The exported surface is a set of preprocessor constants that encode bit positions and masks for memory-mapped MMHUB hardware registers.

## Purpose

`mmhub_2_3_0_sh_mask.h` provides symbolic field definitions for AMDGPU code targeting the MMHUB 2.3.0 register layout. Consumers combine these macros with companion register offsets from `mmhub_2_3_0_offset.h`, defaults from `mmhub_2_3_0_default.h`, and register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, and `WREG32_SOC15` to update VM translation, cache, fault, clock-gating, power-management, performance, and diagnostic registers without embedding raw bit arithmetic in driver logic.

This chunk covers the MMHUB surfaces that support:

- MMEA0 performance counters, EDC counters, DSM/error injection controls, error status, address-decode selection, SDP priority overrides, and clock-control fields.
- PCTL deep-sleep, power-gating ignore, save/restore ranges, reserved fields, status, and performance-counter registers for UTCL2 and two slices.
- L1 TLB status and stream-local translation windows for `TLS0`, including 38 control registers, start/end address pairs, invalidation bits, protection-fault status/address, and IOMMU fault status/address.
- SAW and MMVM L2 controls for context 0, page-table base/start/end registers, context disable masks, pipe-busy readbacks, and L2 cache/fragment/fault behavior.
- ATC L2 controls for cache policy, cache data readback words, transaction limits, group real-time classes, parity status, clock gating, memory light sleep, and SDP port clock-enable handshakes.

## Exported API Surface

There are no callable APIs or local types. The public interface is the macro namespace generated from the MMHUB 2.3.0 register database:

- `MMEA0_*`: monitoring and error-analysis fields, including latency sampling, performance-counter low/high words, two counter configs, result control, SEC/DED/SED EDC counters, DSM single-write controls, error-injection controls, clock-control overrides, EDC mode, error status, address-decode selectors, SDP priority overrides, and always-on misc bits.
- `PCTL_*`: power-control fields, including deep-sleep input/override masks for many MMHUB sub-blocks, power-gating ignore masks, slice-level busy/allow controls, UTCL2 misc controls, slice misc controls, register-engine execute/index/data surfaces, state-controller register-save ranges and exclusion sets, status bits, performance counters, and reserved registers.
- `MMMC_VM_MX_L1_*`: L1 TLB status and performance-counter fields, plus the `TLS0` stream context controls, start/end logical address windows, invalidation streams, pending invalidation state, protection-fault status/address, and IOMMU fault status/address.
- `MMVM_L2_SAW_*`: system aperture/window style L2 controls, context 0 translation controls, page-table base/start/end registers, context-disable bitmaps, and pipe-busy readbacks.
- `MM_ATC_L2_*`: address-translation-cache L2 controls, cache data readback fields, transaction limits, group real-time-class register, parity/error status, clock-gating controls, memory light-sleep timing, and SDP port clock enables/receivers.
- `MMVM_L2_*`: the start of the MMVM L2 control and fault namespace, including L2 cache enable/fragment/cache-mode fields, invalidation controls, status/parity bits, dummy-page fault matching, invalidate-control throttles, and most `MMVM_L2_PROTECTION_FAULT_CNTL` shifts.

The usual generated pattern is `<REGISTER>__<FIELD>__SHIFT` plus `<REGISTER>__<FIELD>_MASK`. Full-width address and data registers often provide a single field with a `0xFFFFFFFFL` mask; packed control/status registers expose one macro pair per subfield.

## Register Areas Covered

The MMEA0 block exposes performance and reliability instrumentation around MMHUB memory paths. The counter registers provide select ranges, modes, enables, clears, trigger controls, and low/high counter readback words. EDC registers count correctable, deferred, and detected errors across DRAM, GMI, IO, RRET/WRET tag memories, page memories, and MAM memories. DSM and DSM2 families define single-write irritation and error-injection controls per memory path, while `MMEA0_ERR_STATUS` reports SDP read/write response status, read-data status, data parity, busy-on-error, FUE, and clear bits. Address-decoder and SDP priority fields influence arbitration/diagnostic selection.

The PCTL block is a large power-management surface. `PCTL_MMHUB_DEEPSLEEP_*`, `PCTL_PG_IGNORE_DEEPSLEEP*`, and `PCTL_SLICE*_CFG_DS_ALLOW*` define per-sub-block masks for deep-sleep eligibility and overrides. Slice and UTCL2 misc registers expose disable, clock-control, and FUE/DFT-style fields. The RENG and STCTRL groups provide register-engine execute/index/data registers plus register-save ranges and exclusion sets for UTCL2 and both slices. PCTL also has status and performance-counter registers that mirror the generated counter pattern used by MMEA0.

The L1 TLB section starts with eight `MMMC_VM_MX_L1_TLBn_STATUS` registers that expose request and page-table-walk counters. It then defines four L1 performance-counter configs plus result and readback registers. The `MMMC_VM_MX_L1_TLS0_*` block is the largest area in the chunk: `TLS0_CNTL` selects enable/system access/debug-mode behavior and `TLS0_CNTL0` through `TLS0_CNTL37` pack per-stream page-table and protection attributes such as enable context, page-table depth, range/PDE/valid/read/write/execute protection defaults, TLB bypass, retry behavior, VMID selection, and address comparators. The matching start/end address pairs describe 38 logical address windows. Invalidate stream and pending registers expose 64-bit bitmaps, and protection/IOMMU fault registers carry status plus low/high fault addresses.

The SAW/L2 VM area describes L2 controls and a dedicated context 0 page table. `MMVM_L2_SAW_CNTL*` exposes cache enables, default-page behavior, PTE/PDE cache sizing, page-table-walk credit limits, walk-order controls, snoop controls, and context-1 identity/fragment behavior. `MMVM_L2_SAW_CONTEXT0_*` defines context enable, page-table depth, range/protection fault defaults, retry behavior, page-table block size, address mode, and base/start/end registers. Context-disable and pipe-busy low/high registers are 32-bit bitmaps.

The ATC L2 section defines cache behavior and power-management details for the memory-management L2. `MM_ATC_L2_CNTL*` fields cover L2 cache enablement, line direction, address translation modes, update/force-miss/cache-size controls, page-fragment sizes, and FIFO active transaction limits. Cache data registers expose tag, valid, VMID, PTE/PDE, and address components for diagnostics. Status registers expose busy and parity information. Clock-gating and light-sleep registers define delay, hysteresis, override, enable, setup, and hold fields; `MM_ATC_L2_SDPPORT_CTRL` names each SDP request/response clock-enable and receiver bit.

The final MMVM L2 section starts the non-SAW L2 control surface consumed by MMHUB setup code. `MMVM_L2_CNTL`, `CNTL2`, and `CNTL3` describe cache enablement, invalidation, default page behavior, VMID/cache modes, bank selection, cache update modes, effective sizes, big-page fragment sizes, associativity, and force-miss bits. `MMVM_L2_STATUS` reports L2 busy, per-domain busy, and cache parity errors. Dummy-page fault and invalidate-control registers support fault matching and invalidation throttling. `MMVM_L2_PROTECTION_FAULT_CNTL` starts the global fault-default policy fields used when enabling or disabling MMHUB fault handling.

## Control Flow And State Behavior

This header has no local control flow. Runtime behavior appears only through driver code that includes the generated macros and performs MMIO reads/writes.

The field names imply several hardware state machines and persistent hardware states:

- VM translation setup persists in MMHUB registers until reset, power loss, or driver reprogramming. Page-table base/start/end fields, context enables, page-table depth, block size, address mode, and fault-default bits determine how MMHUB translates GPU virtual addresses.
- Cache and TLB invalidation is command/state oriented. `MMVM_L2_CNTL2` invalidation bits, L1/TLS invalidation stream bitmaps, pending invalidation readbacks, and `MMVM_INVALIDATE_CNTL` outstanding/alternating controls coordinate TLB/L2 cache flushes.
- Fault handling is sticky and policy driven. Protection and IOMMU fault status/address registers capture fault metadata; clear and allow-update bits control whether later faults overwrite stored status. Fault default-enable bits decide whether invalid accesses fault, route to dummy/default pages, retry, NACK, or crash.
- Power and clock state is shared hardware state. PCTL deep-sleep allow/override masks, power-gating ignore masks, ATC L2 clock-gating overrides, and memory light-sleep setup/hold values affect whether MMHUB sub-blocks may gate clocks or enter low-power states.
- Performance and error counters accumulate hardware events. Counter low/high registers, compare fields, enable/clear bits, EDC counters, MMEA error status, PCTL status, and ATC parity status are readback or clear/control points rather than software-owned data structures.
- DSM/error-injection fields intentionally perturb hardware memory paths for validation. These must be treated as lab/recovery controls, because enabling injection or forced single writes can change observed reliability behavior.

No software persistence is implemented here. Any persistence belongs to hardware register contents and to higher-level AMDGPU state that rewrites these registers during initialization, suspend/resume, reset recovery, GART enable/disable, clock-gating changes, or RAS/error-handling flows.

## Dependencies And Integration Points

The syntactic dependency is only the C preprocessor. Semantically, the chunk pairs with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_2_3_0_offset.h` for matching `mm...`/`reg...` offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_2_3_0_default.h` for reset/default values such as L2 control defaults used by setup code.
- AMD register helper macros, especially `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`.

Direct include sites in this tree are `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v2_3.c` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c`. `mmhub_v2_3.c` is the main runtime consumer for this ASIC generation: it initializes GART apertures, system aperture registers, L1 TLB controls, MMVM L2 cache controls, VMID context configuration, invalidation ranges, protection-fault behavior, client-ID fault reporting, and MMHUB clock-gating/light-sleep state. The DCN31 resource path includes the same header for display resource table construction on hardware using this MMHUB register set.

Related code in other MMHUB generations uses matching macro names for similar behavior. For example, nearby `mmhub_v2_0.c`, `mmhub_v3_0*.c`, `mmhub_v3_3.c`, `mmhub_v4_2_0.c`, `mmhub_v1_7.c`, and `mmhub_v9_4.c` show how `MM_ATC_L2_*`, `MMVM_L2_PROTECTION_FAULT_CNTL*`, `MMVM_L2_SAW_*`, and `MMEA0_EDC_*` fields are used for cache setup, fault policy, SAW context programming, clock gating, and RAS counter decoding. These cross-generation users are useful comparison points but must not be assumed bit-compatible without the matching generated header.

## Risks

- Generated-header drift is the main risk. A wrong shift or mask can silently update an adjacent hardware field during `REG_SET_FIELD` read-modify-write operations, affecting VM translation, fault policy, power state, or diagnostic controls.
- The chunk mixes control, status, clear, and readback fields in the same macro form. Consumers need the register specification or established driver sequence to know whether a field is writable, read-only, sticky, write-one-to-clear, clear-on-read, or reserved.
- VM context, page-table, and fault-policy fields are safety-critical for GPU memory isolation. Incorrect values can cause invalid DMA, hidden faults routed to dummy/default pages, fault storms, no-retry crashes, or loss of useful fault evidence.
- Cache/TLB invalidation fields are ordering-sensitive. Missing L1/L2 invalidation bits, wrong pending-stream interpretation, or incorrect outstanding limits can leave stale translations active after VM updates.
- PCTL and ATC clock-gating/light-sleep fields affect live hardware availability. Over-aggressive deep-sleep enables or stale override bits can cause hangs, timeouts, or unreliable fault/performance readback.
- MMEA DSM/error-injection controls can deliberately create SEC/DED/FUE-like behavior. Accidentally enabling injection or single-write irritators in production code would look like hardware reliability failures.
- The range starts and ends at chunk boundaries inside register groups. Earlier chunks contain the first `MMEA0_LATENCY_SAMPLING` shifts, and later chunks contain the rest of `MMVM_L2_PROTECTION_FAULT_CNTL`; merge-time validation should avoid treating those boundary groups as locally incomplete defects.

## Test Signals

Useful validation is mostly build-time, generation-time, and hardware-integration oriented:

- Compile or preprocess AMDGPU and DCN31 code that includes `mmhub_2_3_0_offset.h`, `mmhub_2_3_0_sh_mask.h`, and `mmhub_2_3_0_default.h`.
- Static generation checks that every complete register in the full `mmhub_2_3_0_sh_mask.h` file has matching `__SHIFT` and `_MASK` definitions, with explicit chunk-boundary exceptions for `MMEA0_LATENCY_SAMPLING` and `MMVM_L2_PROTECTION_FAULT_CNTL`.
- Cross-check register and field names against `mmhub_2_3_0_offset.h` and the source register database used to generate the header.
- Runtime MMHUB bring-up tests on MMHUB 2.3.0-class ASICs: GART enable/disable, VMID programming, page-table base/start/end programming, L1/L2 TLB/cache invalidation, VM fault reporting, dummy/default page handling, and no-retry/retry fault behavior.
- Suspend/resume and GPU reset tests that verify MMHUB register state is restored correctly, including PCTL save ranges, deep-sleep overrides, ATC L2 clock gating, memory light sleep, and cache/TLB control registers.
- RAS and diagnostics validation that reads MMEA0 EDC counters, `MMEA0_ERR_STATUS`, ATC L2 parity status, L1/TLS protection fault status, and IOMMU fault addresses, including clear/update behavior.
- Performance-counter validation that MMEA0, PCTL, and L1 TLB counters can be configured, cleared, started/stopped, and read without corrupting unrelated fields.

## Chunk Notes For Merge

This document is intentionally source-tree aligned and covers only lines 4719-7196 of `mmhub_2_3_0_sh_mask.h`. Earlier chunks should cover the beginning of MMEA0 and the missing `MMEA0_LATENCY_SAMPLING` shifts. Later chunks should continue `MMVM_L2_PROTECTION_FAULT_CNTL` and the rest of the MMVM L2 protection-fault namespace. The final per-file report should treat the whole file as a generated ASIC register bitfield map for AMDGPU MMHUB programming, not as handwritten runtime logic.
