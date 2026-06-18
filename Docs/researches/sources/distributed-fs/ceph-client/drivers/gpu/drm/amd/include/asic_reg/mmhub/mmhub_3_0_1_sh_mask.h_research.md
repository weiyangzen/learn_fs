# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_3_0_1_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002803`: lines 1-2366, `Docs/researches/chunks/subset-b-002803_research.md`
- `subset-b-002804`: lines 2367-4844, `Docs/researches/chunks/subset-b-002804_research.md`
- `subset-b-002805`: lines 4845-7297, `Docs/researches/chunks/subset-b-002805_research.md`
- `subset-b-002806`: lines 7298-7483, `Docs/researches/chunks/subset-b-002806_research.md`

## Chunk Research

### subset-b-002803: lines 1-2366

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_3_0_1_sh_mask.h lines 1-2366

## Scope And Purpose

This chunk is the opening portion of the generated AMDGPU MMHUB 3.0.1 register shift/mask header. It starts with the AMD MIT-style license and include guard, then defines the first `mmhub_dagbdec` address-block field macros through the first two shift definitions for `DAGB0_SDP_PRIORITY_OVERRIDE`. The source file continues after this range, so this document covers only lines 1-2366.

The file is a hardware register contract, not executable logic. Its public surface is a large set of preprocessor constants named as `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`; callers combine those constants with AMDGPU register helpers to compose or decode 32-bit MMIO register values. In this chunk there are no C functions, structs, enums, storage objects, loops, branches, or direct register accesses.

Within the covered range, the dominant purpose is to describe DAGB0 read and write arbitration for MMHUB 3.0.1: per-client virtual-channel selection, TLB-credit checks, urgency thresholds, bandwidth throttling, outstanding request limits, address/data DAGB burst and lazy timers, clock-gating controls, pending/status bitmaps, FIFO/credit status, and DAGB performance counters.

## Important APIs, Types, And Register Families

There are no callable APIs or local types. The API is the macro namespace consumed by code that includes `mmhub_3_0_1_sh_mask.h`, typically through helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_SOC15*`, and `RREG32_SOC15*`.

Important register families in this chunk include:

- `DAGB0_RDCLI0` through `DAGB0_RDCLI29`: per-read-client control registers. Each has the same field layout: `VIRT_CHAN`, `CHECK_TLB_CREDIT`, `URG_HIGH`, `URG_LOW`, `MAX_BW_ENABLE`, `MAX_BW`, `MIN_BW_ENABLE`, `MIN_BW`, `OSD_LIMITER_ENABLE`, and `MAX_OSD`.
- `DAGB0_WRCLI0` through `DAGB0_WRCLI29`: matching per-write-client controls with the same virtual-channel, TLB-credit, urgency, bandwidth, and outstanding-request limiter fields.
- `DAGB0_RD_CNTL` and `DAGB0_WR_CNTL`: shared read/write arbitration controls for client max-bandwidth window, virtual-channel max-bandwidth window, shared VC count, and round-robin enable.
- `DAGB0_RD_IO_CNTL`, `DAGB0_RD_GMI_CNTL`, `DAGB0_WR_IO_CNTL`, and `DAGB0_WR_GMI_CNTL`: priority override controls with two override slots and a common priority field for IO and GMI traffic.
- `DAGB0_RD_ADDR_DAGB`, `DAGB0_WR_ADDR_DAGB`, and `DAGB0_WR_DATA_DAGB`: DAGB enable, jump-ahead, self-init-disable, `WHOAMI`, and write-address jump-mode fields.
- `DAGB0_*_CGTT_CLK_CTRL` and `DAGB0_L1TLB_*_CGTT_CLK_CTRL`: clock and light-sleep timing fields such as `ON_DELAY`, `OFF_HYSTERESIS`, `LS_ASSERT_HYSTERESIS`, `LS_DISABLE`, and `BUSY_OVERRIDE`.
- `DAGB0_RD_ADDR_DAGB_MAX_BURST[0-3]`, `DAGB0_RD_ADDR_DAGB_LAZY_TIMER[0-3]`, `DAGB0_WR_ADDR_DAGB_MAX_BURST[0-3]`, `DAGB0_WR_ADDR_DAGB_LAZY_TIMER[0-3]`, `DAGB0_WR_DATA_DAGB_MAX_BURST[0-3]`, and `DAGB0_WR_DATA_DAGB_LAZY_TIMER[0-3]`: packed four-bit fields for clients 0-31.
- `DAGB0_RD_VC0_CNTL` through `DAGB0_RD_VC5_CNTL` and `DAGB0_WR_VC0_CNTL` through `DAGB0_WR_VC5_CNTL`: per-virtual-channel storage credit, max/min bandwidth, OSD limiter, and max outstanding fields.
- `DAGB0_RD_IO_VC_CNTL`, `DAGB0_RD_GMI_VC_CNTL`, `DAGB0_WR_IO_VC_CNTL`, and `DAGB0_WR_GMI_VC_CNTL`: IO/GMI virtual-channel bandwidth and OSD controls.
- `DAGB0_RD_CNTL_MISC`, `DAGB0_WR_CNTL_MISC`, `DAGB0_RD_TLB_CREDIT`, `DAGB0_WR_TLB_CREDIT`, `DAGB0_WR_DATA_CREDIT`, `DAGB0_WR_MISC_CREDIT`, `DAGB0_WR_DATA_FIFO_CREDIT_CNTL1`, and `DAGB0_WR_ATOMIC_FIFO_CREDIT_CNTL1`: storage-pool, UTCL2 VCI, TLB, data, DLOCK, OSD, atomic, FIFO, and per-VC credit packing.
- `DAGB0_RDCLI_*_PENDING`, `DAGB0_WRCLI_*_PENDING`, and `DAGB0_WRCLI_DBUS_*_PENDING`: full-width `BUSY` status bitmaps for ask/go/global-send/TLB/output-arbiter/DF/OSD and data-bus pending states.
- `DAGB0_WRCLI_GPU_SNOOP_OVERRIDE` and `DAGB0_WRCLI_GPU_SNOOP_OVERRIDE_VALUE`: full-width per-client enable/value bitmaps for GPU snoop override behavior.
- `DAGB0_DAGB_DLY`, `DAGB0_CNTL_MISC`, and `DAGB0_CNTL_MISC2`: delay selection, bandwidth-init cycle, busy overrides, swap control, parity-check enablement, RDATA/WDATA parity response behavior, RDRET FIFO performance, and tap-chain fine-grain clock-gating disable bits.
- `DAGB0_FIFO_EMPTY`, `DAGB0_FIFO_FULL`, `DAGB0_RD_CREDITS_FULL`, and `DAGB0_WR_CREDITS_FULL`: FIFO and credit fullness/emptiness status fields.
- `DAGB0_PERFCOUNTER_LO`, `DAGB0_PERFCOUNTER_HI`, `DAGB0_PERFCOUNTER0_CFG` through `DAGB0_PERFCOUNTER2_CFG`, and `DAGB0_PERFCOUNTER_RSLT_CNTL`: performance counter low/high words, compare value, event-select range, mode, enable, clear, start/stop triggers, enable-any, clear-all, and stop-on-saturate controls.
- `DAGB0_L1TLB_REG_RW` and `DAGB0_RESERVE1` through `DAGB0_RESERVE4`: L1TLB register read/write control and full-width reserved placeholders.
- `DAGB0_SDP_RD_BW_CNTL` and the start of `DAGB0_SDP_PRIORITY_OVERRIDE`: SDP read bandwidth controls and the first two priority-override shift fields. The masks and remaining fields for `DAGB0_SDP_PRIORITY_OVERRIDE` are outside this chunk.

## Control Flow And State Behavior

This chunk has no runtime control flow. Its constants are substituted by the C preprocessor into other AMDGPU code that reads, modifies, writes, or logs MMHUB registers.

The runtime state represented here lives in MMHUB hardware registers. Read/write client and VC fields configure traffic routing and quality-of-service policy: virtual-channel choice, bandwidth windows, min/max bandwidth enforcement, urgency thresholds, TLB-credit accounting, outstanding request limits, and address/data burst or lazy behavior. Pending, FIFO, credit-full, and performance-counter fields expose hardware status or counter state. Counter control fields such as `ENABLE`, `CLEAR`, `CLEAR_ALL`, triggers, and stop-on-saturate are stateful hardware controls.

Persistence is entirely hardware-local. Values remain until reset, power-gating, firmware programming, or driver reprogramming changes them. This header does not cache register values, serialize access, validate field access direction, or protect callers from writing status-only or reserved fields.

## Dependencies And Integration Points

The immediate companion file is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_3_0_1_offset.h`. It maps the same `mmhub_dagbdec` register names to offsets at base address `0x68000`, with `regDAGB0_RDCLI0` at `0x0000`, `regDAGB0_WRCLI0` at `0x003f`, `regDAGB0_WR_DATA_DAGB` at `0x006b`, `regDAGB0_PERFCOUNTER_LO` at `0x0096`, `regDAGB0_SDP_RD_BW_CNTL` at `0x00a1`, and `regDAGB0_SDP_PRIORITY_OVERRIDE` at `0x00a2`.

The principal source integration point in this tree is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v3_0_1.c`, which includes both `mmhub_3_0_1_offset.h` and `mmhub_3_0_1_sh_mask.h`. That implementation primarily uses later MMVM fields from the same header for VM/GART setup, invalidation, and protection-fault decoding, but the include provides the complete MMHUB 3.0.1 register-field namespace for any DAGB, VM, fault, and debug code compiled in that translation unit.

The file follows the AMDGPU generated-register convention shared with nearby MMHUB headers such as `mmhub_2_0_0_sh_mask.h`, `mmhub_3_0_2_sh_mask.h`, and `mmhub_9_4_1_sh_mask.h`. Cross-generation similarity is useful for review, but the `reg*` offsets, base indices, client counts, and exact masks are ASIC-specific; code should include the header matching the IP block being programmed.

Although this repository path is under a Ceph client source import, this file belongs to the Linux AMDGPU DRM hardware interface and has no Ceph filesystem behavior.

## Risks And Edge Cases

- These constants are a hardware ABI. A wrong shift or mask can silently program the wrong field, change request routing, alter bandwidth policy, lose TLB-credit accounting, or misread status while still compiling cleanly.
- The read-client and write-client blocks are highly repetitive. Copy/paste or generator drift can affect a single client while leaving neighboring macros correct, so spot checks should cover client 0, middle clients, and client 29.
- Many registers pack repeated fields tightly into one word. Client burst/lazy timers use 4-bit lanes, TLB credits use 5-bit lanes, bandwidth and OSD fields use larger packed ranges, and status registers may be full-width bitmaps. Read-modify-write callers must preserve unrelated bits.
- Full-width masks such as `0xFFFFFFFFL` should be treated as 32-bit register values. Signed promotion or wrong printf formats can make diagnostics misleading.
- Status and control fields share the same macro naming style. Pending, FIFO, credit, and counter result fields may be read-only or side-effectful depending on the hardware guide; the header does not encode access permissions.
- Clock, parity, busy override, snoop override, counter clear, and `L1TLB_REG_RW` fields are not passive metadata. Accidental writes can change power behavior, suppress or force busy state, clear diagnostics, or alter debug access.
- The chunk boundary splits `DAGB0_SDP_PRIORITY_OVERRIDE` after only `OVERRIDE0_PRIORITY__SHIFT` and `OVERRIDE0_CLIENT_ID__SHIFT`. Whole-file research must merge this with the following chunk before describing that register completely.

## Test And Validation Signals

There are no direct unit tests for this macro-only chunk. Useful validation is compile-time, static, and hardware-observation based:

- Build AMDGPU code paths that include `mmhub_3_0_1_sh_mask.h`, especially `mmhub_v3_0_1.c`, to catch missing or renamed macros.
- Run static mask/shift consistency checks: masks should be contiguous, single-bit masks should match their shift, packed fields should not overlap, and full-width masks should start at shift zero.
- Compare this chunk against `mmhub_3_0_1_offset.h` so every covered register-comment group has a corresponding `reg*` offset and base index.
- Compare generated values against the authoritative AMD register database for MMHUB 3.0.1, especially repeated `RDCLI`/`WRCLI` layouts, 30-client limits, VC count, FIFO/credit status widths, and performance-counter controls.
- On MMHUB 3.0.1 hardware or simulator, inspect MMHUB register dumps around VM/GART initialization, power transitions, and display or media client activity to confirm DAGB fields remain at expected firmware/driver-programmed values.
- For debug/performance paths, validate that counter enable/clear/select fields and high/low counter reads behave as expected and that clear bits do not persist unexpectedly.

## Chunk Notes For Merge Lane

This is the first chunk of `mmhub_3_0_1_sh_mask.h`. It covers the license, include guard, and the opening `mmhub_dagbdec` DAGB0 arbitration/QoS/status/performance-counter section through the start of `DAGB0_SDP_PRIORITY_OVERRIDE`. The final per-file report should reconcile this with the next chunk before making complete statements about SDP priority, later DAGB0 registers, MMVM, MMEA, ATC, or L2TLB fields.

### subset-b-002804: lines 2367-4844

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_3_0_1_sh_mask.h lines 2367-4844

## Scope And Purpose

This chunk is a generated AMDGPU MMHUB 3.0.1 register field-mask header segment. It contains preprocessor constants only: each hardware register field is represented as a `<REGISTER>__<FIELD>__SHIFT` macro and a matching `<REGISTER>__<FIELD>_MASK` macro. There are no C functions, structs, enums, variables, storage allocations, locks, loops, branches, or direct MMIO operations in this range.

The covered range defines 2,122 macros across 335 register-comment groups and 7 address blocks. It starts in the middle of `DAGB0_SDP_PRIORITY_OVERRIDE`, then completes the late `mmhub_dagbdec` SDP control/status section. It then covers `mmhub_pctldec` power-control/deepsleep fields, L1 TLB status/performance and TLS window fields, SAW context fields, ATC L2 cache/control/status/clock-gating fields, and the beginning of MMVM L2 control/protection-fault fields. The chunk ends in the middle of `MMVM_L2_PROTECTION_FAULT_CNTL2`; the remaining masks for that register and later MMVM fields are outside this work item.

The companion offset header is `mmhub_3_0_1_offset.h`. That file gives register offsets and base indices; this header gives the bit positions used by AMDGPU register helpers to build and decode 32-bit MMHUB register values.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this header chunk. The public interface is the generated macro namespace consumed by helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and their offset variants in MMHUB driver code.

Important macro families in this slice are:

- `DAGB0_SDP_PRIORITY_OVERRIDE`, `DAGB0_SDP_RD_PRIORITY`, and `DAGB0_SDP_WR_PRIORITY`: priority override fields for two selected clients plus packed per-VC read/write priorities for SDP traffic.
- `DAGB0_SDP_RD_CLI2SDP_VC_MAP` and `DAGB0_SDP_WR_CLI2SDP_VC_MAP`: maps SRT, NRT, DLOCK, HRT, IO, and GMI request classes into SDP virtual channels.
- `DAGB0_SDP_ENABLE`, `DAGB0_SDP_CREDITS`, `DAGB0_SDP_TAG_RESERVE0/1`, `DAGB0_SDP_VCC_RESERVE0/1`, and `DAGB0_SDP_VCD_RESERVE0/1`: SDP enablement, tag limits, response credits, and reserved credits across VC0-VC7, including the `DISTRIBUTE_POOL` controls.
- `DAGB0_SDP_ERR_STATUS`: read/write response status, read-response data status/parity error, clear-status, busy-on-error, fatal-error interrupt, level interrupt, and ignore-fatal-data/error controls.
- `DAGB0_SDP_REQ_CNTL`, `DAGB0_SDP_MISC_AON`, `DAGB0_SDP_MISC`, `DAGB0_SDP_MISC2`, `DAGB0_SDP_ARB_CNTL0/1`, `DAGB0_SDP_CGTT_CLK_CTRL`, and `DAGB0_SDP_LATENCY_SAMPLING`: request pass/post-write and chain overrides, block levels, early write-return enables, client-group VC mapping, arbitration override/retry policy, clock-gating/light-sleep timing, and latency sampling filters.
- `PCTL_CTRL`: global MMHUB power-control bits for power-gating enablement, MMHUB deepsleep mode, RSMU/DAGB idle thresholds, protection-fault ignore policy, EA partial/full ack overrides, and RSMU read-timer controls.
- `PCTL_MMHUB_DEEPSLEEP_IB`, `PCTL_MMHUB_DEEPSLEEP_OVERRIDE`, `PCTL_MMHUB_DEEPSLEEP_OVERRIDE_IB`, `PCTL_PG_IGNORE_DEEPSLEEP`, and `PCTL_PG_IGNORE_DEEPSLEEP_IB`: deepsleep input, override, and ignore bitmaps for DS0-DS16 plus ATHUB/CANE/IB-oriented control bits.
- `PCTL_SLICE0_*` and `PCTL_SLICE1_*`: per-slice DAGB read/write busy configuration, deepsleep allow bitmaps, register-engine pointers, critical-register lock bits, tile idle thresholds, memory light-sleep enablement, deep-sleep disconnect behavior, execute-on-update, and read-timer enablement.
- `PCTL_RENG_*` and `PCTL_*_STCTRL_REGISTER_SAVE_*`: register-engine execution, RAM index/data windows, and state-controller save range/exclusion sets for UTCL2 and both slices.
- `PCTL_STATUS`, `PCTL_PERFCOUNTER_LO/HI`, `PCTL_PERFCOUNTER0_CFG`, `PCTL_PERFCOUNTER1_CFG`, and `PCTL_PERFCOUNTER_RSLT_CNTL`: power-control status and performance-counter result/configuration fields.
- `MMMC_VM_MX_L1_TLB0_STATUS` through `TLB7_STATUS`: busy and parity-error status for eight L1 TLB instances.
- `MMMC_VM_MX_L1_PERFCOUNTER0_CFG` through `3_CFG`, `MMMC_VM_MX_L1_PERFCOUNTER_RSLT_CNTL`, and result low/high registers: L1 performance counter event selection, enable/clear controls, compare value, trigger selection, global enable/clear, and stop-on-saturate fields.
- `MMMC_VM_MX_L1_TLS0_CNTL` and `MMMC_VM_MX_L1_TLS0_CNTL0` through `CNTL37`: TLS range enablement, default/request behaviour, snoop, atomic, client ID, VMID, volatile, LRU, priority, and virtual-address high-bit matching for 38 TLS windows.
- `MMMC_VM_MX_L1_TLS0_START_ADDR{0..37}_{LO32,HI32}` and `END_ADDR{0..37}_{LO32,HI32}`: low/high split address bounds for those TLS windows.
- `MMMC_VM_MX_L1_TLS0_INVALIDATE_STREAM_*`, `INVALIDATE_REQUEST_PENDING_*`, `PROTECTION_FAULT_STATUS`, protection-fault address registers, and IOMMU fault status/GVADDR registers: TLS invalidation, pending-request, fault decode, and fault-address fields.
- `MMVM_L2_SAW_CNTL`, `CNTL2`, `CNTL3`, `CNTL4`, `CONTEXT0_CNTL`, `CONTEXT0_CNTL2`, page-table base/start/end registers, `CONTEXTS_DISABLE`, and `PIPES_BUSY_*`: SAW L2 page-walk, retry, context, and pipe-busy controls.
- `MM_ATC_L2_CNTL`, `CNTL2`, `CACHE_DATA0..2`, `CNTL3`, `CNTL4`, `CNTL5`, `MM_GROUP_RT_CLASSES`, `STATUS`, `STATUS2`, `MISC_CG`, `MEM_POWER_LS`, `CGTT_CLK_CTRL`, and `SDPPORT_CTRL`: ATC L2 translation-cache policy, cache-data inspection, invalidation/update mode, ATS credits, clock-gating, memory light-sleep, busy/error status, and SDP port clock-enable controls.
- `MMVM_L2_CNTL`, `MMVM_L2_CNTL2`, `MMVM_L2_CNTL3`, `MMVM_L2_STATUS`, `MMVM_DUMMY_PAGE_FAULT_*`, `MMVM_INVALIDATE_CNTL`, `MMVM_L2_PROTECTION_FAULT_CNTL`, and the beginning of `MMVM_L2_PROTECTION_FAULT_CNTL2`: main MMVM L2 cache enablement, invalidation, bank/fragment/effective-size policy, busy/parity status, dummy-page fault controls, and protection-fault default/interrupt/crash policy.

## Control Flow And State Behavior

This header has no runtime control flow. The C preprocessor substitutes the constants into driver code that performs MMIO reads, writes, read-modify-write updates, status decoding, or debug printing.

Runtime state lives in MMHUB hardware registers. DAGB0 SDP fields affect request prioritization, VC mapping, credits, arbitration, error status, and clock/latency policy for the SDP-facing path. PCTL fields control and observe power-gating, deepsleep, register save/restore, and slice-level state-control behavior. L1 TLB/TLS fields represent TLB busy/parity status, performance-counter state, translation-local-storage windows, invalidation request state, and fault latches. ATC L2 fields control translation-cache policy and clock/light-sleep behavior. MMVM L2 fields configure the central VM translation cache, invalidate L1/L2 translation state, expose busy/parity status, and define how dummy-page and protection faults are treated.

Some fields are plainly stateful request or latch controls: `CLEAR_ERROR_STATUS`, performance-counter `CLEAR` and `CLEAR_ALL`, invalidation request/pending bits, cache invalidation bits, `CLEAR_PROTECTION_FAULT_STATUS_ADDR`, `ALLOW_SUBSEQUENT_PROTECTION_FAULT_STATUS_ADDR_UPDATES`, and crash-on-fault controls. The header names their bit positions but does not encode access type, reset values, ordering requirements, or polling rules.

Persistence is hardware-local. Register values survive only according to MMHUB reset, power-gating, firmware, and driver initialization/save-restore behavior. The header does not store state itself. Driver code such as `mmhub_v3_0_1.c` owns the software policy: it programs the L2 cache, TLB, protection fault defaults, VM contexts, invalidation engine metadata, and clock-gating/light-sleep bits using these masks.

## Dependencies And Integration Points

The immediate dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_3_0_1_offset.h`. In that file, the late DAGB0 SDP registers in this chunk run from `regDAGB0_SDP_RD_BW_CNTL` at offset `0x00a1` through `regDAGB0_SDP_LATENCY_SAMPLING` at `0x00b8` in base block `0x68000`. The PCTL block starts at base address `0x68e00` with `regPCTL_CTRL` at `0x0380`. L1 TLB status begins at base `0x69600` with `regMMMC_VM_MX_L1_TLB0_STATUS` at `0x0588`. The MMVM L2 block begins at `regMMVM_L2_CNTL` offset `0x0680`, with `regMMVM_L2_PROTECTION_FAULT_CNTL2` at `0x0689`.

The direct local consumer is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v3_0_1.c`, which includes both `mmhub_3_0_1_offset.h` and this `mmhub_3_0_1_sh_mask.h`. Direct integrations visible there include:

- `mmhub_v3_0_1_init_system_aperture_regs()`: writes protection-fault default address registers and sets `MMVM_L2_PROTECTION_FAULT_CNTL2__ACTIVE_PAGE_MIGRATION_PTE_READ_RETRY`.
- `mmhub_v3_0_1_init_tlb_regs()`: programs L1 TLB control fields from an earlier chunk of this same header.
- `mmhub_v3_0_1_init_cache_regs()`: uses `MMVM_L2_CNTL`, `MMVM_L2_CNTL2`, and `MMVM_L2_CNTL3` fields from this chunk to enable L2 cache, set default-page-out behavior, trigger L1/L2 invalidation, and tune bank/large-fragment policy.
- `mmhub_v3_0_1_gart_disable()`: clears L1 TLB enablement and disables `MMVM_L2_CNTL__ENABLE_L2_CACHE`, then clears `regMMVM_L2_CNTL3`.
- `mmhub_v3_0_1_set_fault_enable_default()`: uses `MMVM_L2_PROTECTION_FAULT_CNTL` masks in this chunk to switch range/PDE/NACK/dummy/valid/read/write/execute faults between default-page handling and crash-on-fault behavior.
- `mmhub_v3_0_1_update_medium_grain_clock_gating()`, `mmhub_v3_0_1_update_medium_grain_light_sleep()`, and `mmhub_v3_0_1_get_clockgating()`: read or modify `MM_ATC_L2_MISC_CG__ENABLE_MASK` and `MM_ATC_L2_MISC_CG__MEM_LS_ENABLE_MASK` from this chunk.

The same macro families are mirrored in neighboring generation files such as `mmhub_3_0_0_sh_mask.h`, `mmhub_3_0_2_sh_mask.h`, and later MMHUB versions. Those are useful for sanity checking generated patterns, but call sites must include the header matching the selected ASIC/IP version because field positions and client maps are generation-specific.

## Risks And Edge Cases

- These macros are a hardware ABI. A wrong shift or mask compiles cleanly but can program the wrong bit in MMHUB hardware, producing stale translations, bad arbitration, incorrect fault routing, hangs, or hard-to-debug power-state failures.
- The chunk starts inside `DAGB0_SDP_PRIORITY_OVERRIDE`; the omitted beginning contains the first fields for override slot 0. Whole-register documentation must merge this with the previous chunk.
- The chunk ends inside `MMVM_L2_PROTECTION_FAULT_CNTL2`; the masks after `CLIENT_ID_PRT_FAULT_INTERRUPT_MASK` and later fault/status/address fields are in the next chunk.
- Many repeated packed fields cover VCs, DS bits, slices, TLB instances, TLS windows, and address-window indices. Off-by-one shifts or incorrect register-family selection can affect only one client, VMID, window, or slice, making failures sparse and platform-dependent.
- Status, clear, invalidate, and performance-counter controls are mixed with ordinary configuration fields. Treating all masks as persistent settings can clear fault evidence, request unintended invalidations, reset counters, or leave fault status updates blocked.
- Protection-fault policy is security and stability sensitive. Misprogramming `*_ENABLE_DEFAULT`, `CLIENT_ID_NO_RETRY_FAULT_INTERRUPT`, `CRASH_ON_NO_RETRY_FAULT`, or `CRASH_ON_RETRY_FAULT` can either hide real faults behind dummy/default pages or escalate recoverable faults into GPU resets.
- L2 cache and invalidation fields are central to VM correctness. Incorrect `ENABLE_L2_CACHE`, `INVALIDATE_ALL_L1_TLBS`, `INVALIDATE_L2_CACHE`, VMID mode, bank selection, fragment size, or force-miss masks can leave stale translations after page-table updates.
- PCTL and ATC clock/light-sleep fields can fail only under suspend/resume, runtime power management, SR-IOV policy, low-power entry/exit, or specific display/media traffic mixes.
- Full-width masks such as address low words and register-engine data fields should be treated as unsigned 32-bit values. Signed promotion or wrong debug formatting can make register dumps misleading.
- Reserved and save-range/exclusion fields preserve generated register-map shape; their presence is not a guarantee that normal driver code may write arbitrary values safely.

## Test And Validation Signals

There are no direct unit tests for this macro-only header chunk. Useful validation signals are compile, static, and hardware integration checks:

- Build AMDGPU configurations that include `mmhub_v3_0_1.c`, `mmhub_3_0_1_offset.h`, and `mmhub_3_0_1_sh_mask.h`.
- Run static mask/shift checks: single-bit masks should equal `1U << shift`; multi-bit masks should be contiguous after shifting; repeated VC/DS/TLS/address fields should not overlap; full-width fields should have shift zero.
- Cross-check every register-comment group in this chunk against `mmhub_3_0_1_offset.h` so offsets, base indices, and generated register names stay aligned.
- Boot supported MMHUB 3.0.1 hardware and exercise GART enable/disable, VMID setup, page-table updates, and VM invalidations. Register dumps should show expected changes to `MMVM_L2_CNTL*`, protection-fault controls, and ATC clock-gating fields.
- Trigger or inspect VM protection faults to validate `MMVM_L2_PROTECTION_FAULT_CNTL`, `CNTL2`, and status decode paths used by `mmhub_v3_0_1_print_l2_protection_fault_status()`.
- Toggle medium-grain clock gating/light sleep and verify `MM_ATC_L2_MISC_CG__ENABLE_MASK` and `MEM_LS_ENABLE_MASK` round-trip through `set_clockgating()` and `get_clockgating()`.
- Use register dumps around suspend/resume or power-gating transitions to validate PCTL save ranges, deepsleep allow/override/ignore masks, and slice misc fields.
- For performance-counter fields, validate that enabling, clearing, trigger selection, high/low reads, and stop-on-saturate behavior match the hardware guide.

## Chunk Notes For Merge Lane

This is a middle chunk of `mmhub_3_0_1_sh_mask.h`. It should be merged with the previous chunk for the complete `DAGB0_SDP_PRIORITY_OVERRIDE` register and with the next chunk for the complete `MMVM_L2_PROTECTION_FAULT_CNTL2` and subsequent MMVM L2 protection-fault/status/address definitions. Whole-file research should treat this slice as the bridge from late DAGB0 SDP/QoS controls through power management, L1 TLB/TLS, ATC L2, and the start of MMVM L2 fault policy.

### subset-b-002805: lines 4845-7297

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_3_0_1_sh_mask.h lines 4845-7297

## Chunk Scope

This chunk is a large middle slice of the generated AMD MMHUB 3.0.1 shift/mask header. It covers source lines 4845-7297 and contains only C preprocessor constants for hardware register bitfields, using the generated naming pattern `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`.

The range starts inside `MMVM_L2_PROTECTION_FAULT_CNTL2`, so the first few visible macros are the trailing masks for that register and the matching shifts are in the previous chunk. It then spans MMVM L2 fault/status controls, MMVM virtual-context programming, TLB invalidation engines, page-table aperture registers, performance counters, shared MMVM/MMUTCL2 aperture controls, and the beginning of ATC L2 performance-counter controls. The range ends inside `MM_ATC_L2_PERFCOUNTER_RSLT_CNTL`, so that register is also completed by the next chunk.

This header chunk is not executable C and defines no logic by itself. Its purpose is to provide compile-time bit positions and masks used by AMDGPU MMHUB/GMC code when programming or decoding MMHUB 3.0.1 MMIO registers.

## Purpose And Hardware Area

The visible definitions describe the MMHUB MMUTCL2/MMVM register map for virtual memory translation, fault reporting, cache/TLB invalidation, memory aperture routing, and debug telemetry.

The main hardware areas are:

- MMVM L2 protection-fault reporting and default-address controls, including fault status decoding, logical fault address capture, physical default page address, and context identity apertures.
- MMVM L2 cache, credit, parity, clock-gating, and bank-selection controls, including PTE cache dump access and credit-safety update registers.
- MMVM context programming for contexts 0-15: enable bits, page-table depth/block size, per-fault interrupt/default behavior, page-table base addresses, start/end logical address ranges, and per-context PTE cache fragment/bank fields.
- MMVM invalidate engines 0-17: semaphore, request, acknowledgement, and address-range registers used to invalidate L1/L2 translation caches per VMID or address range.
- MMVM/MMUTCL2 performance counters for L2 and UTCL2 events, including counter select, mode, enable, clear, start/stop trigger, result selection, and low/high counter result fields.
- Shared MMVM/MMUTCL2 registers for PCIe ATS, northbridge/MMIO aperture windows, top-of-DRAM, framebuffer offset, cacheable/local system memory ranges, local framebuffer ranges, virtualization reset/active-function state, clock gating, harvest bypass, and group return fault status.
- Shared virtual-client aperture registers for framebuffer, AGP, system aperture bounds, and L1 TLB control.
- ATC L2 performance-counter read/config/result-control fields at the end of the slice.

Within the driver, the macros are paired with generated register-address headers and consumed by ASIC-specific AMDGPU code through register write/read helpers. They allow callers to compose register values without open-coded bit positions.

## Important Definitions

This chunk defines no functions, structs, unions, enums, inline helpers, storage objects, or exported symbols. The important interface is the macro set.

Each normal field has:

- `...__SHIFT`: the low bit of the field in a 32-bit register value.
- `..._MASK`: the bit mask used to isolate or clear the field.

Important macro families in this slice include:

- Fault controls and capture: trailing `MMVM_L2_PROTECTION_FAULT_CNTL2` masks, `MMVM_L2_PROTECTION_FAULT_MM_CNTL3`, `MMVM_L2_PROTECTION_FAULT_MM_CNTL4`, `MMVM_L2_PROTECTION_FAULT_STATUS`, `MMVM_L2_PROTECTION_FAULT_ADDR_LO32/HI32`, and `MMVM_L2_PROTECTION_FAULT_DEFAULT_ADDR_LO32/HI32`.
- Identity/aperture controls: `MMVM_L2_CONTEXT1_IDENTITY_APERTURE_LOW_ADDR_*`, `MMVM_L2_CONTEXT1_IDENTITY_APERTURE_HIGH_ADDR_*`, and `MMVM_L2_CONTEXT_IDENTITY_PHYSICAL_OFFSET_*`.
- L2 cache behavior controls: `MMVM_L2_CNTL4`, `MMVM_L2_CNTL5`, `MMVM_L2_MM_GROUP_RT_CLASSES`, `MMVM_L2_BANK_SELECT_RESERVED_CID`, `MMVM_L2_BANK_SELECT_RESERVED_CID2`, `MMVM_L2_BANK_SELECT_MASKS`, and per-context `MMVM_L2_CONTEXT*_PER_PFVF_PTE_CACHE_FRAGMENT_SIZES`.
- L2 reliability/debug controls: `MMVM_L2_CACHE_PARITY_CNTL`, `MMVM_L2_PTE_CACHE_DUMP_CNTL`, `MMVM_L2_PTE_CACHE_DUMP_READ`, and `MMVM_L2_GCR_CNTL`.
- Clock/busy controls: `MMVM_L2_CGTT_CLK_CTRL`, `MMVM_L2_CGTT_BUSY_CTRL`, `MMUTCL2_CGTT_CLK_CTRL`, and `MMUTCL2_CGTT_BUSY_CTRL`.
- Credit-safety controls: `MMUTCL2_CREDIT_SAFETY_GROUP_RET_CDC`, `MMUTCL2_CREDIT_SAFETY_GROUP_CLIENTS_INVREQ_CDC`, `MMUTCL2_CREDIT_SAFETY_GROUP_CLIENTS_INVREQ_NOCDC`, `MMVML2_CREDIT_SAFETY_IH_FAULT_INTERRUPT`, and `MMVML2_WALKER_CREDIT_SAFETY_FETCH_RDREQ`.
- Context controls: `MMVM_CONTEXT0_CNTL` through `MMVM_CONTEXT15_CNTL` and `MMVM_CONTEXTS_DISABLE`.
- Invalidation engines: `MMVM_INVALIDATE_ENG0_SEM` through `MMVM_INVALIDATE_ENG17_SEM`, `MMVM_INVALIDATE_ENG0_REQ` through `MMVM_INVALIDATE_ENG17_REQ`, `MMVM_INVALIDATE_ENG0_ACK` through `MMVM_INVALIDATE_ENG17_ACK`, and `MMVM_INVALIDATE_ENG0_ADDR_RANGE_LO32/HI32` through `MMVM_INVALIDATE_ENG17_ADDR_RANGE_LO32/HI32`.
- Page-table address programming: `MMVM_CONTEXT0_PAGE_TABLE_BASE_ADDR_LO32/HI32` through `MMVM_CONTEXT15_PAGE_TABLE_BASE_ADDR_LO32/HI32`, plus per-context `PAGE_TABLE_START_ADDR_LO32/HI32` and `PAGE_TABLE_END_ADDR_LO32/HI32`.
- L2/UTCL2 performance counters: `MMMC_VM_L2_PERFCOUNTER0_CFG` through `MMMC_VM_L2_PERFCOUNTER7_CFG`, `MMMC_VM_L2_PERFCOUNTER_RSLT_CNTL`, `MMMC_VM_L2_PERFCOUNTER_LO/HI`, `MMUTCL2_PERFCOUNTER0_CFG` through `MMUTCL2_PERFCOUNTER3_CFG`, `MMUTCL2_PERFCOUNTER_RSLT_CNTL`, and `MMUTCL2_PERFCOUNTER_LO/HI`.
- Shared MMVM/MMUTCL2 aperture and virtualization registers: `MMVM_PCIE_ATS_CNTL`, `MMMC_VM_NB_MMIOBASE`, `MMMC_VM_NB_MMIOLIMIT`, `MMMC_VM_NB_PCI_CTRL`, `MMMC_VM_NB_PCI_ARB`, `MMMC_VM_NB_TOP_OF_DRAM_SLOT1`, `MMMC_VM_NB_LOWER_TOP_OF_DRAM2`, `MMMC_VM_NB_UPPER_TOP_OF_DRAM2`, `MMMC_VM_FB_OFFSET`, `MMMC_VM_SYSTEM_APERTURE_DEFAULT_ADDR_LSB/MSB`, `MMMC_VM_STEERING`, `MMMC_SHARED_VIRT_RESET_REQ`, `MMMC_SHARED_ACTIVE_FCN_ID`, `MMUTCL2_HARVEST_BYPASS_GROUPS`, and `MMUTCL2_GROUP_RET_FAULT_STATUS`.
- Shared VC aperture registers: `MMMC_VM_FB_LOCATION_BASE`, `MMMC_VM_FB_LOCATION_TOP`, `MMMC_VM_AGP_TOP/BOT/BASE`, `MMMC_VM_SYSTEM_APERTURE_LOW_ADDR`, `MMMC_VM_SYSTEM_APERTURE_HIGH_ADDR`, and `MMMC_VM_MX_L1_TLB_CNTL`.
- ATC L2 telemetry: `MM_ATC_L2_PERFCOUNTER_LO`, `MM_ATC_L2_PERFCOUNTER_HI`, `MM_ATC_L2_PERFCOUNTER0_CFG`, `MM_ATC_L2_PERFCOUNTER1_CFG`, and the visible start of `MM_ATC_L2_PERFCOUNTER_RSLT_CNTL`.

## Control Flow

There is no runtime control flow in this chunk. The C preprocessor expands these macros wherever MMHUB programming code includes the header.

The effective control flow exists in consumers that:

- Compose a register value by shifting a chosen field value by `__SHIFT` and then applying `_MASK`.
- Decode a register read by masking and right-shifting a field.
- Perform read-modify-write updates where `_MASK` clears a field and a shifted value inserts the new hardware setting.
- Program context control, page-table base, and page-table range registers before enabling VM contexts.
- Submit TLB invalidation by programming an engine's address-range registers, request bits, and VMID mask, then polling or checking the matching acknowledgement/semaphore fields.
- Decode `MMVM_L2_PROTECTION_FAULT_STATUS` after a page-walk or permission fault to determine client ID, VMID, VF/VFID, read/write/atomic direction, mapping error, permission faults, walker error, PRT, and whether additional faults are queued.
- Enable, clear, select, start, stop, and read MMVM L2, UTCL2, or ATC L2 performance counters.

Because the file is generated register metadata, the correctness of control flow depends on downstream code following the hardware sequencing rules for the matching MMHUB 3.0.1 register-address definitions.

## State And Persistence Behavior

The header itself has no mutable state, allocates no memory, performs no I/O, and persists no data. All state described here is hardware state in MMHUB/MMUTCL2 registers.

Important state classes described by the macros are:

- Fault state: `MMVM_L2_PROTECTION_FAULT_STATUS` and fault address/default-address registers reflect current or latched protection-fault information until hardware or driver fault-handling paths clear or overwrite it.
- Context state: `MMVM_CONTEXT*_CNTL`, page-table base, start, and end registers define the active GPU virtual address spaces for VM contexts 0-15. These settings persist in hardware until reset, reprogramming, suspend/resume restore, or context teardown.
- Invalidation state: invalidate-engine semaphore/request/ack/address-range registers hold transient synchronization and invalidation commands. Drivers generally expect request bits and acknowledgements to converge before assuming stale translations have been flushed.
- Cache and bank-selection state: L2 fragment size, bank masks, reserved client IDs, GCR, and PTE cache dump controls affect cache behavior, debug visibility, and cache partitioning while the MMHUB block is active.
- Aperture state: shared framebuffer, AGP, system aperture, local system memory, cacheable DRAM, local framebuffer, MMIO, top-of-DRAM, and default-address registers control address routing and fallback behavior.
- Virtualization state: `MMMC_SHARED_VIRT_RESET_REQ` and `MMMC_SHARED_ACTIVE_FCN_ID` expose PF/VF reset and active-function selection bits for SR-IOV or virtualized access paths.
- Clock/power state: `*_CGTT_CLK_CTRL`, `*_CGTT_BUSY_CTRL`, and `MMMC_MEM_POWER_LS` describe clock-gating, busy override, and memory light-sleep timing fields.
- Telemetry state: performance counter config/result registers and low/high counter result fields represent transient debug counters whose values are explicitly selected, cleared, enabled, stopped, or allowed to saturate by consumer code.

Macro definitions are compile-time constants. Register state lifetime and persistence are controlled by MMIO writes, firmware interaction, GPU reset, runtime power management, suspend/resume, and virtualization reset flows outside this header.

## Dependencies And Integration Points

This chunk has only the whole-file include guard and the C preprocessor as direct dependencies. There are no `#include` directives in the visible range.

Practical integration dependencies are implicit:

- The matching `mmhub_3_0_1` register-offset/address header that names the physical MMIO registers corresponding to these fields.
- AMDGPU MMIO helpers and register-field helper macros used by GMC/MMHUB code to write, read, poll, and update register values.
- ASIC-specific VM/MMHUB initialization code that programs contexts, apertures, fault defaults, L2 controls, clock gating, and performance counters in a safe order.
- VM update and eviction paths that program page-table bases/ranges and issue invalidate-engine requests after page-table changes.
- Interrupt/fault-handling code that reads MMVM L2 fault status and fault-address fields and may use invalidation or default-page behavior in response.
- Power-management and reset code that must preserve or restore VM context, aperture, clock-gating, and shared state across suspend/resume, runtime power transitions, and GPU resets.
- Virtualization/SR-IOV integration that depends on PF/VF active-function, reset, per-PFVF cache fragment sizing, and VFID-related fault fields.
- Debug/performance tooling that selects and reads MMVM L2, UTCL2, and ATC L2 performance counter events.

The `// addressBlock:` comments are useful generated grouping markers. In this chunk they separate `mmhub_mmutcl2_mmvml2vcdec`, `mmhub_mmutcl2_mmvml2pldec`, `mmhub_mmutcl2_mmvml2prdec`, `mmhub_mmutcl2_mmvmsharedhvdec`, `mmhub_mmutcl2_mmvmsharedpfdec`, `mmhub_mmutcl2_mmvmsharedvcdec`, `mmhub_mmutcl2_mmatcl2pfcntrdec`, and `mmhub_mmutcl2_mmatcl2pfcntldec`.

## Risks

- Boundary incompleteness: this chunk starts after the first `MMVM_L2_PROTECTION_FAULT_CNTL2` shift/mask definitions and ends before the complete `MM_ATC_L2_PERFCOUNTER_RSLT_CNTL` definition. The final per-file merge should reconcile those registers with adjacent chunks.
- Generated-header drift: any mismatch between these bit masks/shifts, the matching offset header, and the authoritative MMHUB 3.0.1 register specification can compile cleanly but program the wrong hardware bits.
- Semantic ambiguity: masks and shifts do not encode whether fields are read-only, write-one-to-clear, sticky, reset-only, privileged, debug-only, or safe only while a block is idle. Consumers must use hardware documentation and established AMDGPU sequencing.
- VM context hazards: wrong `MMVM_CONTEXT*_CNTL`, page-table base, start, or end programming can cause GPU virtual-address translation failures, data corruption, page faults, or unintended access to default pages.
- Invalidation hazards: missing or incorrect `MMVM_INVALIDATE_ENG*_REQ` bits, address ranges, VMID masks, or acknowledgement polling can leave stale L1/L2 translations resident after page-table updates.
- Fault-handling hazards: mis-decoding `MMVM_L2_PROTECTION_FAULT_STATUS` can attribute faults to the wrong VMID, VFID, client, access type, or fault class, making recovery or diagnostics misleading.
- Aperture hazards: framebuffer, AGP, system aperture, top-of-DRAM, default-address, and local-memory range fields define address routing. Incorrect values can break MMIO/VRAM/system-memory accesses.
- Clock/power hazards: CGTT and light-sleep timing fields can interact with power-gated or clock-gated MMHUB blocks. Incorrect programming can cause hangs, lost register state, or false busy/idle detection.
- Debug/performance side effects: performance-counter clear/enable/result-control fields can disturb in-flight measurements, and PTE cache dump or parity-force fields may be unsafe outside controlled debug or validation flows.
- Virtualization hazards: PF/VF reset and active-function fields are sensitive in SR-IOV environments. Incorrect use can affect the wrong function or expose misleading per-VF state.

## Test Signals

Useful validation signals for this chunk are mostly compile-time, static, and hardware-integration oriented:

- Build AMDGPU code that includes `mmhub_3_0_1_sh_mask.h` with the matching MMHUB 3.0.1 offset header; renamed or missing macros should fail at compile time.
- Static checks can verify that every visible `__SHIFT` has a matching `_MASK`, masks are aligned with their shift positions, and repeated families such as contexts 0-15 and invalidate engines 0-17 remain structurally identical where expected.
- Regeneration diffs should be reviewed against the authoritative MMHUB 3.0.1 register source, especially for VM context, invalidation, fault-status, aperture, and performance-counter fields.
- Hardware smoke tests should cover GPU initialization, VM context setup, page-table base/range programming, basic VRAM/system-memory access, and recovery after GPU reset.
- VM tests should change mappings, issue invalidations, and confirm no stale translations remain for selected VMIDs and address ranges.
- Fault tests should trigger controlled invalid/permission/range faults and verify decoded `MMVM_L2_PROTECTION_FAULT_STATUS` fields, captured fault addresses, interrupt/default-page behavior, and fault-clear sequencing.
- Suspend/resume and runtime power-management tests should verify that MMHUB context, aperture, clock-gating, and memory light-sleep settings are restored or reprogrammed correctly.
- SR-IOV or virtual-function tests should inspect PF/VF reset, active-function, VFID fault attribution, and per-PFVF cache fragment/bank fields where the platform supports them.
- Debug/performance tests can exercise MMVM L2, UTCL2, and ATC L2 counter select/enable/clear/read flows and confirm counter low/high values advance for expected workloads.

## Cross-Chunk Notes

- The previous chunk should contain the start of `MMVM_L2_PROTECTION_FAULT_CNTL2`, including shifts and masks before `OTHER_CLIENT_ID_PRT_FAULT_INTERRUPT_MASK`.
- The next chunk should complete `MM_ATC_L2_PERFCOUNTER_RSLT_CNTL`, including the masks after `STOP_TRIGGER_MASK` if present, and continue with subsequent ATC L2 definitions.
- The final per-file research document should treat this chunk as generated register metadata and should avoid inferring full VM/MMHUB behavior without the matching offset headers and consuming AMDGPU MMHUB/GMC code.

### subset-b-002806: lines 7298-7483

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
