# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_3_0_2_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002808`: lines 1-2377, `Docs/researches/chunks/subset-b-002808_research.md`
- `subset-b-002809`: lines 2378-4756, `Docs/researches/chunks/subset-b-002809_research.md`
- `subset-b-002810`: lines 4757-7198, `Docs/researches/chunks/subset-b-002810_research.md`
- `subset-b-002811`: lines 7199-7228, `Docs/researches/chunks/subset-b-002811_research.md`

## Chunk Research

### subset-b-002808: lines 1-2377

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_3_0_2_sh_mask.h lines 1-2377

## Scope

This chunk covers the opening 2,377 lines of the generated MMHUB 3.0.2 shift/mask header. The range starts with the license, include guard, and `mmhub_dagbdec` address block, then defines the `DAGB0` register field layout from `DAGB0_RDCLI0` through the first three mask definitions of `DAGB0_FATAL_ERROR_STATUS4`. The next lines after this chunk add the remaining `DAGB0_FATAL_ERROR_STATUS4` masks and continue into `DAGB0_SDP_CGTT_CLK_CTRL`, so this chunk intentionally ends in the middle of that final fatal-status register's mask set.

The covered content is entirely preprocessor data. It defines `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` constants for 32-bit MMIO register fields; it contains no functions, structs, enums, storage, or executable control flow.

## Purpose

The purpose of this header section is to encode the bit-level ABI for the MMHUB 3.0.2 DAGB0 datapath. MMHUB is the memory hub side of AMDGPU virtual memory and memory-traffic routing. The `DAGB0` register families in this chunk describe read/write client arbitration, virtual-channel assignment, bandwidth limits, TLB and return credits, clock-gating controls, pending/busy state, SDP routing and error handling, performance counters, and fatal-error capture fields.

The companion `mmhub_3_0_2_offset.h` header supplies the register addresses, for example `regDAGB0_RDCLI0`, `regDAGB0_WR_DATA_CREDIT`, `regDAGB0_SDP_ERR_STATUS`, and `regDAGB0_FATAL_ERROR_STATUS0..4`. This file supplies the field positions and masks consumed by AMDGPU helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, and `SOC15_REG_OFFSET`.

## Important Macro Families

### Read Client Control

`DAGB0_RDCLI0` through `DAGB0_RDCLI23` define the same per-client read-side layout. Each client has fields for:

- `VIRT_CHAN`, selecting the virtual channel.
- `CHECK_TLB_CREDIT`, gating requests on TLB credit availability.
- `URG_HIGH` and `URG_LOW`, encoding urgency thresholds or priorities.
- `MAX_BW_ENABLE` / `MAX_BW` and `MIN_BW_ENABLE` / `MIN_BW`, controlling bandwidth limiting or reservation.
- `OSD_LIMITER_ENABLE` and `MAX_OSD`, limiting outstanding demand.

`DAGB0_RD_CNTL` adds global read arbitration knobs such as client and VC max-bandwidth windows, shared-VC count, and round-robin enable. `DAGB0_RD_IO_CNTL` and `DAGB0_RD_GMI_CNTL` provide two priority override slots plus a common priority for IO and GMI classes. `DAGB0_RD_ADDR_DAGB` enables the read address DAGB path, jump-ahead behavior, self-init suppression, instance identity, and jump mode.

The read path also defines clock-gating controls (`DAGB0_RD_CGTT_CLK_CTRL`, `DAGB0_L1TLB_RD_CGTT_CLK_CTRL`), per-client maximum burst and lazy-timer nibbles grouped as clients 0-7, 8-15, and 16-23, virtual-channel controls `DAGB0_RD_VC0_CNTL` through `DAGB0_RD_VC5_CNTL`, and IO/GMI VC controls. `DAGB0_RD_CNTL_MISC`, `DAGB0_RD_TLB_CREDIT`, `DAGB0_RD_RDRET_CREDIT_CNTL`, and `DAGB0_RD_RDRET_CREDIT_CNTL2` describe storage pool, UTCL2 VCI, read-return compatibility mode, per-TLB credits, per-VC read-return credits, VC mode, equality-fix controls, and pool credit.

The read-side pending and override registers (`DAGB0_RDCLI_ASK_PENDING`, `GO_PENDING`, `GBLSEND_PENDING`, `TLB_PENDING`, `OARB_PENDING`, `ASK2ARB_PENDING`, `ASK2DF_PENDING`, `OSD_PENDING`, `ASK_OSD_PENDING`, `NOALLOC_OVERRIDE`, and `NOALLOC_OVERRIDE_VALUE`) expose full-width bitmaps. These fields are likely used for diagnostics, drain checks, or debug overrides because each register has a single `BUSY`, `ENABLE`, or `VALUE` field covering all 32 bits.

### Write Client Control

`DAGB0_WRCLI0` through `DAGB0_WRCLI23` mirror the read client format: virtual-channel selection, TLB-credit checking, urgency thresholds, max/min bandwidth policy, OSD limiting, and max outstanding demand.

`DAGB0_WR_CNTL` differs slightly from the read global control. It has client and VC max-bandwidth windows plus `VC_ROUNDROBIN_EN`, `UPDATE_FED`, and `UPDATE_NACK`, which are write-path policy/update controls. `DAGB0_WR_IO_CNTL` and `DAGB0_WR_GMI_CNTL` mirror the read-side IO/GMI priority override shape. `DAGB0_WR_ADDR_DAGB` controls the write address DAGB path, while `DAGB0_WR_DATA_DAGB` separately controls the write data path; both expose enable, jump-ahead, self-init, and identity fields, with the address path also carrying `JUMP_MODE`.

Write address and write data paths each have grouped maximum-burst and lazy-timer controls for clients 0-23. The write path also includes `DAGB0_WR_VC0_CNTL` through `DAGB0_WR_VC5_CNTL`, IO/GMI VC controls, `DAGB0_WR_CNTL_MISC`, `DAGB0_WR_TLB_CREDIT`, `DAGB0_WR_DATA_CREDIT`, `DAGB0_WR_MISC_CREDIT`, `DAGB0_WR_DATA_FIFO_CREDIT_CNTL1`, and `DAGB0_WR_ATOMIC_FIFO_CREDIT_CNTL1`. These registers describe storage and HDP client ID selection, per-TLB credits, burst-size data credits, atomic credits, deadlock VC selection, data FIFO credits, atomic FIFO credits, pool credits, VC mode, and fix bits.

Write pending and override registers include the read-side set plus write-specific DBUS pending state and GPU snoop overrides: `DAGB0_WRCLI_DBUS_ASK_PENDING`, `DAGB0_WRCLI_DBUS_GO_PENDING`, `DAGB0_WRCLI_GPU_SNOOP_OVERRIDE`, `DAGB0_WRCLI_GPU_SNOOP_OVERRIDE_VALUE`, `DAGB0_WRCLI_NOALLOC_OVERRIDE`, and `DAGB0_WRCLI_NOALLOC_OVERRIDE_VALUE`.

### DAGB Miscellaneous State and Performance Counters

`DAGB0_DAGB_DLY` exposes delay, client, and position fields. `DAGB0_CNTL_MISC` has a bandwidth initialization cycle field. `DAGB0_CNTL_MISC2` is a compact control and debug register with read/write busy overrides, TLB busy overrides, SDP busy override, swap control, parity check enable, read-data parity-to-NACK behavior, write-data parity-to-RAS behavior, read-return FIFO performance selection, and fine-grain clock-gating disable bits for read/write return tap chains.

`DAGB0_FIFO_EMPTY`, `DAGB0_FIFO_FULL`, `DAGB0_RD_CREDITS_FULL`, and `DAGB0_WR_CREDITS_FULL` expose packed status fields for FIFO and credit fullness. `DAGB0_PERFCOUNTER_LO` and `DAGB0_PERFCOUNTER_HI` hold the low counter bits, high counter bits, and a compare value. `DAGB0_PERFCOUNTER0_CFG`, `DAGB0_PERFCOUNTER1_CFG`, and `DAGB0_PERFCOUNTER2_CFG` define event selection, ending selection, performance mode, enable, and clear bits. `DAGB0_PERFCOUNTER_RSLT_CNTL` selects a counter result and provides start/stop triggers, enable-any, clear-all, and stop-on-saturate controls.

`DAGB0_L1TLB_REG_RW` exposes command bits for L1 TLB register write/read control plus a large reserved field. `DAGB0_RESERVE1` through `DAGB0_RESERVE4` are full-width reserved register fields.

### SDP Routing, Credits, Errors, and Fatal Capture

The SDP section begins with `DAGB0_SDP_RD_BW_CNTL`, which controls SDP read bandwidth maximum, minimum, and max-bandwidth window. `DAGB0_SDP_PRIORITY_OVERRIDE` supplies two override slots, each with priority, client ID, and enable bits for DRAM read/write, GMI read/write, and IO read/write traffic. `DAGB0_SDP_RD_PRIORITY` and `DAGB0_SDP_WR_PRIORITY` define common priorities for DRAM, GMI, and IO. `DAGB0_SDP_RD_CLI2SDP_VC_MAP` and `DAGB0_SDP_WR_CLI2SDP_VC_MAP` map DRAM/GMI/IO client classes onto SDP virtual channels.

`DAGB0_SDP_ENABLE` is a single enable bit. `DAGB0_SDP_CREDITS` defines read-response, write-response, and command credits. `DAGB0_SDP_TAG_RESERVE0/1`, `DAGB0_SDP_VCC_RESERVE0/1`, and `DAGB0_SDP_VCD_RESERVE0/1` reserve tags or credits per virtual channel and optionally distribute pool resources.

`DAGB0_SDP_ERR_STATUS` captures read/write response status, read data status, read data parity error, error-clear control, busy-on-error policy, FUE flag, ignored read-response fatal error disable, fatal interrupt enable, ignore-client-fatal interrupt policy, level interrupt mode, and busy-on-completion-fatal behavior. `DAGB0_SDP_REQ_CNTL` controls request pass-PW overrides, request-chain overrides for DRAM/GMI, inner-domain mode, and block levels for read/write/atomic requests.

`DAGB0_SDP_MISC_AON`, `DAGB0_SDP_MISC`, and `DAGB0_SDP_MISC2` include link-manager hysteresis/deassert behavior, early write-return enables for VC0-VC7, early SDP original data behavior, dynamic link-manager mode, halt/reconnect/idle thresholds, data FIFO margins, read-return swap mode, request blocking, request-blocked status, and read-response credit-release mode. `DAGB0_SDP_ARB_CNTL0` and `DAGB0_SDP_ARB_CNTL1` tune early read/write switching, error event or halt request behavior, DED mode, and read/write burst limits by cycle and data count.

The fatal-error registers at the end of the chunk provide a captured transaction record. `DAGB0_FATAL_ERROR_CNTL` selects a filter number and `DAGB0_FATAL_ERROR_CLEAR` clears captured fatal state. `DAGB0_FATAL_ERROR_STATUS0` records validity, client ID, and low address bits. `STATUS1` records high address bits. `STATUS2` records client tag, SDP tag, VFID, VF, address space, IO, and size. `STATUS3` records unit ID, operation, security level, write/read TMZ, snoop, invalidation, NACK, read-only, memory-log, internal fatal, and external fatal. The chunk includes `STATUS4` shifts for priority, chain, full, drop, write-address phase, and no-allocate, plus masks for priority, chain, and full; the remaining masks are in the next chunk.

## Control Flow and State Behavior

This chunk has no software control flow. Its effect is compile-time substitution of constants into AMDGPU register access code.

The state represented here is hardware state in MMHUB DAGB0. Some fields are persistent configuration until reset or reprogramming, such as virtual-channel assignment, bandwidth windows, max/min bandwidth, priorities, clock-gating hysteresis, TLB/data/FIFO credits, SDP VC maps, request policy, and performance counter selection. Other fields are status or sticky error state, such as pending bitmaps, FIFO empty/full, credit full, SDP error status, performance counter results, and fatal-error status. A few fields behave as command or control bits, such as performance counter clear bits, SDP error clear, fatal error clear, request blocking, no-allocate and snoop overrides, and busy overrides.

The header does not encode ordering rules. Callers must follow the owning MMHUB and SOC15 initialization paths when sequencing reads, writes, drains, clears, and polls.

## Dependencies and Integration Points

Direct dependencies are the generated MMHUB 3.0.2 register headers and AMDGPU register helpers:

- `mmhub_3_0_2_offset.h` supplies register offsets and base indices for every `DAGB0_*` register in this chunk.
- `mmhub_3_0_2_default.h` supplies reset/default values for related MMHUB registers where generated defaults exist.
- `amdgpu/mmhub_v3_0_2.c` includes this header and the matching offset header, then uses `REG_SET_FIELD` / `REG_GET_FIELD` heavily for MMHUB VM, L1 TLB, L2 cache, invalidation, and fault registers elsewhere in this same generated mask file.
- SOC15 accessors (`RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, `SOC15_REG_OFFSET`) are the runtime bridge from these constants to real MMIO accesses.

Within the inspected `mmhub_v3_0_2.c` implementation, the later MMVM fields from this same header are used for page table base programming, GART aperture setup, system aperture setup, TLB and L2 cache enablement, VMID context setup, invalidation request generation, and L2 protection fault decoding. The `DAGB0` fields in this chunk are more likely consumed by initialization, diagnostics, RAS/error handling, perf/debug, or future generation-specific tuning paths that need to inspect or program DAGB datapath arbitration and SDP state.

The client-ID table in `mmhub_v3_0_2.c` maps MMHUB client IDs to names such as VMC, DCEDMC, MP0/MP1, HDP, LSDMA, JPEG, VCN, VSCH, and debug clients. That table is relevant when decoding `CID` fields from MMHUB fault or fatal status registers defined in this header.

## Risks

- Bit drift is high impact. Incorrect masks or shifts can write the wrong hardware field, causing memory-routing faults, arbitration starvation, hangs, bad performance data, or lost fatal-error context.
- The read and write client families are highly repetitive but not semantically interchangeable. Mechanical edits can easily change one client or path while leaving the matching read/write or address/data counterpart inconsistent.
- Bandwidth, urgency, OSD, VC, and credit fields directly affect memory traffic scheduling. Bad values can create unfairness, underutilization, deadlocks, or timeout-sensitive stalls.
- Pending, busy override, no-allocate override, snoop override, SDP request blocking, and clear bits should not be treated as ordinary persistent configuration. Misuse can mask real drains/errors or force traffic behavior outside normal policy.
- SDP error and fatal-error fields are diagnostic and recovery-sensitive. Clearing too early can lose root-cause data; failing to clear sticky state can cause repeated interrupts or misleading later reports.
- Clock-gating and low-power controls interact with block idleness. Incorrect `LS_DISABLE`, hysteresis, or busy override programming can waste power or gate clocks while state is still active.
- The chunk boundary cuts `DAGB0_FATAL_ERROR_STATUS4` before all masks are present, so any merged report must join this chunk with the next one before documenting that register as complete.

## Test and Validation Signals

Useful validation is mostly integration and hardware bring-up coverage:

- Build coverage for AMDGPU sources that include `mmhub/mmhub_3_0_2_sh_mask.h`; this catches renamed, missing, or malformed macros.
- MMHUB GART and VM smoke tests should cover the same header's MMVM fields through `mmhub_v3_0_2_gart_enable`, VMID setup, TLB/cache programming, and invalidation paths.
- VM fault injection should verify that MMHUB client IDs and protection/fatal status fields decode consistently with the client table and hardware documentation.
- Suspend/resume, GPU reset, and clock-gating tests should watch for hangs or lost state around DAGB busy, FIFO, credit, and CGTT controls.
- Performance/debug tests should program `DAGB0_PERFCOUNTER*_CFG`, `DAGB0_PERFCOUNTER_RSLT_CNTL`, and counter result registers, then verify event selection, clear, enable, saturation, and result selection behavior.
- RAS/error tests should exercise SDP error handling and fatal-error capture/clear sequencing, preserving `DAGB0_FATAL_ERROR_STATUS0..4` data long enough for diagnostics.
- Stress tests with display, HDP, SDMA, JPEG/VCN, and VM traffic should catch regressions in read/write client VC mapping, priority, bandwidth, OSD, TLB credit, data credit, and SDP credit configuration.

## Unresolved Cross-Chunk References

This range covers only `mmhub_3_0_2_sh_mask.h` lines 1-2377. It does not include the rest of `DAGB0_FATAL_ERROR_STATUS4`, the following `DAGB0_SDP_CGTT_CLK_CTRL` and `DAGB0_SDP_LATENCY_SAMPLING` definitions, the later `DAGB1` block, PCTL, MMVM L1/L2, VM context, invalidation, framebuffer aperture, and shared MMHUB register families. Those belong to later chunks for the same source file and should be reconciled by the merge lane.

### subset-b-002809: lines 2378-4756

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_3_0_2_sh_mask.h lines 2378-4756

## Chunk Scope

This chunk is a generated AMD MMHUB 3.0.2 shift/mask header segment. It covers source lines 2378-4756 and contains only C preprocessor constants for hardware register bitfields. Each complete field follows the AMDGPU generated-header convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position.
- `<REGISTER>__<FIELD>_MASK` gives the raw 32-bit mask.

There are no C functions, structs, enums, variables, branches, loops, locks, allocations, or direct MMIO operations in this range. Runtime behavior comes from AMDGPU code that includes this header with `mmhub/mmhub_3_0_2_offset.h`, especially `amdgpu/mmhub_v3_0_2.c`.

The range begins in the tail of `DAGB0_FATAL_ERROR_STATUS4`, includes complete `DAGB0_SDP_CGTT_CLK_CTRL` and `DAGB0_SDP_LATENCY_SAMPLING`, covers a large `DAGB1` read/SDP/control block, then covers `mmhub_pctldec`, L1 TLB status and performance-counter blocks, and the beginning of the MMVM L2/fault/identity-aperture block. It ends inside `MMVM_L2_CNTL4`, so adjacent chunks are required before making whole-file claims.

The chunk contains 2,172 `#define` entries: 1,086 `__SHIFT` constants and 1,086 `_MASK` constants.

## Purpose

The purpose of this header range is to encode MMHUB 3.0.2 register field layout for AMDGPU memory-hub programming. The companion offset header tells the driver where a register is; this shift/mask header tells it how to pack, update, and decode individual fields in that register.

The visible hardware areas are:

- DAGB read-side client arbitration, virtual-channel, credit, pending, performance, fatal-error, and SDP fields.
- MMHUB power-control and deep-sleep metadata through `PCTL_*`.
- MM L1 TLB status and performance counter fields.
- MMVM L2 cache, invalidation, dummy-page fault, protection-fault, and identity-aperture fields.

In the local driver, `gmc_v11_0.c` selects `mmhub_v3_0_2_funcs` when the MMHUB IP version is `3.0.2`. `mmhub_v3_0_2.c` directly includes this header and uses the generated macros through helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`.

## Important Macro Families

The chunk exports no callable APIs or data types. Its API surface is the macro namespace itself.

Important DAGB and SDP families include:

- `DAGB0_FATAL_ERROR_STATUS4`: the visible tail decodes dropped, write-address-phase, and no-allocation fatal-error attributes. The beginning of this status word is in the previous chunk.
- `DAGB0_SDP_CGTT_CLK_CTRL` and `DAGB1_SDP_CGTT_CLK_CTRL`: clock-gating and light-sleep timing controls with on delay, off hysteresis, light-sleep assertion hysteresis, light-sleep disable, and busy override.
- `DAGB0_SDP_LATENCY_SAMPLING` and `DAGB1_SDP_LATENCY_SAMPLING`: sampler routing for DRAM/GMI/IO, read/write, atomic return/no-return, and virtual-channel selection.
- `DAGB1_RDCLI0` through `DAGB1_RDCLI23`: repeated read-client control registers with virtual-channel selection, TLB-credit checking, urgency thresholds, max/min bandwidth limits, OSD limiter enablement, and max outstanding request fields.
- `DAGB1_RD_CNTL`, `DAGB1_RD_IO_CNTL`, `DAGB1_RD_GMI_CNTL`, and `DAGB1_RD_ADDR_DAGB`: shared read-path control, IO/GMI credit and burst policy, DAGB enable/jump-ahead/self-init/identity fields, and address-path jump mode.
- `DAGB1_RD_ADDR_DAGB_MAX_BURST0..2` and `DAGB1_RD_ADDR_DAGB_LAZY_TIMER0..2`: packed per-client burst and lazy-timer nibbles for read address traffic.
- `DAGB1_RD_VC0_CNTL` through `DAGB1_RD_VC5_CNTL`, plus `DAGB1_RD_IO_VC_CNTL` and `DAGB1_RD_GMI_VC_CNTL`: per-VC storage, EA credits, bandwidth limiters, OSD limits, and IO/GMI virtual-channel credit thresholds.
- `DAGB1_RD_TLB_CREDIT`, `DAGB1_RD_RDRET_CREDIT_CNTL`, and `DAGB1_RD_RDRET_CREDIT_CNTL2`: TLB and read-return credit pool sizing.
- `DAGB1_RDCLI_*_PENDING`, `DAGB1_FIFO_EMPTY`, `DAGB1_FIFO_FULL`, and `DAGB1_RD_CREDITS_FULL`: full-width or compact status bitmaps for read-client pipeline state.
- `DAGB1_CNTL_MISC`, `DAGB1_CNTL_MISC2`, `DAGB1_RD_CNTL_MISC`, `DAGB1_DAGB_DLY`, `DAGB1_L1TLB_REG_RW`, and `DAGB1_RESERVE1..4`: miscellaneous remap, clock-gating, soft-stall, delay, L1TLB register-access, and reserved full-width fields.
- `DAGB1_PERFCOUNTER_LO/HI`, `DAGB1_PERFCOUNTER0_CFG` through `2_CFG`, and `DAGB1_PERFCOUNTER_RSLT_CNTL`: counter value, compare, selector range, mode, enable/clear, trigger, clear-all, and stop-on-saturate fields.
- `DAGB1_SDP_*`: SDP read bandwidth, priority override, read priority, client-to-SDP VC mapping, enable, credits, tag/VCC reserves, error status, request controls, always-on misc fields, general misc fields, arbitration controls, clock gating, and latency sampling.

Important PCTL families include:

- `PCTL_CTRL`: power-gating enablement, allowed deep-sleep mode, RSMU and DAGB idle thresholds, ignore-protection-fault policy for state control, EA0/EA1 acknowledgement override controls, and RSMU read-timer fields.
- `PCTL_MMHUB_DEEPSLEEP_IB`, `PCTL_MMHUB_DEEPSLEEP_OVERRIDE`, `PCTL_MMHUB_DEEPSLEEP_OVERRIDE_IB`, `PCTL_PG_IGNORE_DEEPSLEEP`, and `PCTL_PG_IGNORE_DEEPSLEEP_IB`: deep-sleep state, override, and ignore bitmaps for DS0 through DS16 plus ATHUB/CANE and IPS-related indicators where present.
- `PCTL_SLICE0_*` and `PCTL_SLICE1_*`: per-slice DAGB write/read busy masks, deep-sleep allow/IB allow masks, miscellaneous register-engine/tile-idle/light-sleep/critical-lock fields, register-engine execute controls, RAM index/data windows, and register save/exclusion ranges.
- `PCTL_UTCL2_MISC`, `PCTL_RENG_CTRL`, `PCTL_UTCL2_RENG_*`, and `PCTL_UTCL2_STCTRL_*`: UTCL2 power-control register-engine start pointers, locking, idle thresholds, light-sleep, execution triggers, RAM access, and save/restore range metadata.
- `PCTL_STATUS` and `PCTL_PERFCOUNTER*`: status bits for state-control idle, deep-sleep disconnect, PGFSM busy/state, critical register activity, and PCTL performance-counter selection/result control.
- `PCTL_RESERVED_0..3`: reserved full-width or structured fields that should be treated as generated hardware-reserved metadata rather than general scratch space unless a hardware guide says otherwise.

Important L1 TLB and MMVM L2 families include:

- `MMMC_VM_MX_L1_TLB0_STATUS` through `TLB5_STATUS`: busy and parity-error status for six visible MM L1 TLB instances.
- `MMMC_VM_MX_L1_PERFCOUNTER0_CFG` through `3_CFG`, `MMMC_VM_MX_L1_PERFCOUNTER_RSLT_CNTL`, and `MMMC_VM_MX_L1_PERFCOUNTER_LO/HI`: L1 performance counter select, mode, enable, clear, result select, trigger, global enable/clear, stop-on-saturate, low result, high result, and compare fields.
- `MMVM_L2_CNTL`, `MMVM_L2_CNTL2`, and `MMVM_L2_CNTL3`: MMVM L2 cache enablement, fragment processing, PTE/PDE endian and tag policy, default-page-out behavior, queue sizing, identity-mode behavior, invalidation controls, bank select, cache update modes, fragment sizes, force-miss controls, and effective cache sizes.
- `MMVM_L2_STATUS`: L2 busy, per-context-domain busy, and PTE/PDE cache parity-error status.
- `MMVM_DUMMY_PAGE_FAULT_CNTL` and dummy-page fault address registers: dummy-page fault enablement, logical-address comparison, and split low/high address fields.
- `MMVM_INVALIDATE_CNTL`: invalidate register alternation and maximum outstanding invalidate-register controls.
- `MMVM_L2_PROTECTION_FAULT_CNTL`, `CNTL2`, `MM_CNTL3`, and `MM_CNTL4`: status-address clearing, subsequent update permission, default routing for range/PDE/translate/NACK/dummy/valid/read/write/execute faults, no-retry and PRT interrupt client bitmaps, active page migration PTE behavior, retry fault interrupt enablement, and VML1 read/write client interrupt masks.
- `MMVM_L2_PROTECTION_FAULT_STATUS`: more-faults, walker error, permission faults, mapping error, client ID, RW, atomic, VMID, VF/VFID, and PRT decode fields.
- `MMVM_L2_PROTECTION_FAULT_ADDR_*` and `DEFAULT_ADDR_*`: logical fault page address and default physical fault page address split into low 32-bit and high 4-bit fields.
- `MMVM_L2_CONTEXT1_IDENTITY_APERTURE_*` and `MMVM_L2_CONTEXT_IDENTITY_PHYSICAL_OFFSET_*`: context-1 identity aperture low/high logical page numbers and physical offset.
- `MMVM_L2_CNTL4`: the chunk contains only the first three shift definitions; masks and remaining fields are in the next chunk.

## Control Flow

There is no executable control flow in the header. The only "flow" is C preprocessing: consumers include the header and expand macro constants into register read, write, and read-modify-write code.

Typical runtime flow in the local MMHUB 3.0.2 driver is:

1. `gmc_v11_0.c` selects `mmhub_v3_0_2_funcs` for MMHUB IP version 3.0.2.
2. `mmhub_v3_0_2_init()` records MMHUB register offsets and VM hub distances, including MMVM context, invalidation, and protection-fault registers.
3. `mmhub_v3_0_2_gart_enable()` programs page-table aperture registers, system aperture/default-page registers, L1 TLB control, MMVM L2 cache controls, VMID context controls, identity aperture disablement, and invalidation address ranges.
4. `REG_SET_FIELD` uses the shift/mask pairs from this header to insert field values into 32-bit register values before `WREG32_SOC15`.
5. `REG_GET_FIELD` uses the same pairs to decode status values, notably `MMVM_L2_PROTECTION_FAULT_STATUS` fields in `mmhub_v3_0_2_print_l2_protection_fault_status()`.

The DAGB and PCTL fields in this chunk are mostly metadata for tuning, diagnostics, clock/power control, or future/neighboring driver code. Sequencing rules, polling loops, reset behavior, write-one-to-clear semantics, and SR-IOV access policy live in the C driver and hardware documentation, not in this generated header.

## State And Persistence Behavior

The macros persist no software state. They describe hardware-visible MMHUB state:

- Persistent-until-reprogrammed configuration: DAGB read-client VC selection, urgency, bandwidth, OSD limits, GMI/IO credits, per-client burst/lazy timers, per-VC credits, SDP routing, PCTL deep-sleep permissions, MMVM L2 cache policy, default-page behavior, and identity aperture ranges.
- Volatile status: DAGB pending/FIFO/fullness fields, SDP error status, PCTL status, L1 TLB busy/parity status, MMVM L2 busy/context busy/parity status, and protection-fault status.
- Action/control bits: performance-counter enable/clear, result clear-all, stop-on-saturate, invalidate-all-L1 and invalidate-L2 bits, protection-fault status-address clear, and clock/light-sleep overrides.
- Fault and diagnostic state: dummy-page fault address, protection-fault logical/default addresses, CID/RW/VMID/VF fault decode, VML1 read/write fault interrupt bitmaps, performance counter low/high values, and latency sampler configuration.

In `mmhub_v3_0_2.c`, some fields from this chunk are programmed during GART enable, reset/disable, fault-default policy changes, or fault-status printing. SR-IOV virtual functions skip several protected MMVM L2 and aperture programming paths, so the same masks may be host/PF-owned in virtualized configurations.

## Dependencies And Integration Points

Direct dependencies are minimal: this generated header relies only on the C preprocessor and the whole-file include guard. Practical dependencies are the AMDGPU generated-register and SOC15 access conventions:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_3_0_2_offset.h` supplies matching `reg...` offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v3_0_2.c` directly includes this header and uses many `MMVM_*` fields from this range.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v11_0.c` selects the MMHUB 3.0.2 function table based on IP version.
- `REG_SET_FIELD` and `REG_GET_FIELD` depend on the exact `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` spelling.
- `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET` combine companion offsets with this field metadata to read, write, or cache MMIO register addresses.
- `amdgpu_vmhub` uses MMVM context, invalidation-engine, and protection-fault offsets initialized by `mmhub_v3_0_2_init()`. This chunk provides field layout for several of the corresponding status/control registers.

Observed local integration points from `mmhub_v3_0_2.c` include:

- `mmhub_v3_0_2_init_system_aperture_regs()`: writes `MMVM_L2_PROTECTION_FAULT_DEFAULT_ADDR_LO32/HI32` and updates `MMVM_L2_PROTECTION_FAULT_CNTL2__ACTIVE_PAGE_MIGRATION_PTE_READ_RETRY`.
- `mmhub_v3_0_2_init_cache_regs()`: programs `MMVM_L2_CNTL`, `MMVM_L2_CNTL2`, `MMVM_L2_CNTL3`, and the beginning of `MMVM_L2_CNTL4` behavior visible at the end of this chunk.
- `mmhub_v3_0_2_disable_identity_aperture()`: writes the identity aperture low/high and physical-offset registers whose field splits are defined here.
- `mmhub_v3_0_2_set_fault_enable_default()`: updates default handling and crash-on-fault bits in `MMVM_L2_PROTECTION_FAULT_CNTL`.
- `mmhub_v3_0_2_print_l2_protection_fault_status()`: decodes `CID`, `RW`, `MORE_FAULTS`, `WALKER_ERROR`, `PERMISSION_FAULTS`, and `MAPPING_ERROR` from `MMVM_L2_PROTECTION_FAULT_STATUS`.
- `mmhub_v3_0_2_gart_disable()`: disables MMVM L2 cache with `MMVM_L2_CNTL__ENABLE_L2_CACHE` and clears `MMVM_L2_CNTL3`.

## Risks And Edge Cases

- Boundary incompleteness: line 2378 starts after most of `DAGB0_FATAL_ERROR_STATUS4`, and line 4756 stops before the masks and remaining fields of `MMVM_L2_CNTL4`. The final per-file report must merge adjacent chunks.
- Generated-header drift can compile cleanly but corrupt runtime behavior. A wrong mask in VM L2, protection-fault, identity-aperture, or DAGB credit fields can program the wrong bit while all C types remain valid.
- Header/offset mismatches are high risk. Pairing `mmhub_3_0_2_sh_mask.h` with another MMHUB generation's offset header can address the wrong register or decode a different layout.
- Repeated client and VC fields are easy to mis-audit. `DAGB1_RDCLI0..23`, per-client burst/lazy timer registers, and per-VC controls look regular but still need exact generated values.
- Fault-control fields are stability and security sensitive. Misprogramming default fault handling, no-retry/retry crash policy, PRT interrupts, or active page migration retry behavior can hide faults, create fault storms, or force GPU resets.
- Invalidation/cache fields can leave stale translations. `MMVM_L2_CNTL2`, L2 force-miss/update fields, and identity-aperture programming must agree with page-table and TLB invalidation flows.
- Address split fields require correct caller-side address shifts. Low 32-bit plus high 4-bit page-number fields are vulnerable to off-by-12 or off-by-44 mistakes in consuming code.
- Power-control fields lack access semantics in the header. PCTL deep-sleep, register-save, slice, RENG, and critical-lock fields may require block-idle sequencing or firmware coordination not visible here.
- Status, clear, and counter fields should not be treated as normal configuration. Full-width pending/status masks, performance-counter clear bits, and protection-fault clear bits may be sticky, write-one-to-clear, transient, or destructive depending on hardware semantics.
- SR-IOV behavior is asymmetric. The local driver skips several MMVM L2 and aperture writes for virtual functions, so tests must distinguish PF-owned and VF-accessible registers.

## Test Signals

Useful validation signals for this chunk are build-time, static-generation, and hardware-integration oriented:

- Build AMDGPU with MMHUB 3.0.2 support enabled so `mmhub_v3_0_2.c` includes `mmhub_3_0_2_offset.h` and `mmhub_3_0_2_sh_mask.h`. Missing or renamed macros should fail around `REG_SET_FIELD` and `REG_GET_FIELD` users.
- Static checks should verify every complete field in lines 2378-4756 has a matching `__SHIFT` and `_MASK`, masks align with shifts, and repeated `DAGB1_RDCLI*`, `PCTL_SLICE*`, and `MMMC_VM_MX_L1_PERFCOUNTER*` families remain structurally consistent.
- Regeneration diffs should compare this header range against the authoritative MMHUB 3.0.2 register database, with special attention to VM L2 cache/fault fields, identity aperture splits, PCTL deep-sleep maps, and repeated DAGB client registers.
- Boot and GART bring-up on MMHUB 3.0.2 hardware should validate system aperture programming, default-page fault address setup, L1 TLB enablement, L2 cache enablement, context setup, and identity aperture disablement.
- VM memory workloads should stress page-table updates, TLB invalidations, retry/no-retry fault behavior, XNACK-related policy, and high memory pressure to expose stale translation or fault-routing errors.
- Fault-path tests should trigger invalid GPU accesses and confirm `MMVM_L2_PROTECTION_FAULT_STATUS` decodes CID, RW, permission, mapping, walker, VMID, VF/VFID, and PRT fields consistently.
- Suspend/resume, reset, and clock/power stress should exercise PCTL deep-sleep, DAGB clock-gating, light-sleep, and state-save metadata where those fields are programmed by platform code or firmware.
- Debug/perf tests can exercise DAGB1, PCTL, and L1 TLB performance-counter select/enable/clear/result paths and verify counter values and stop-on-saturate behavior.
- High-traffic media/display/SDMA workloads are useful for DAGB/SDP arbitration and credit field regressions because the MMHUB client table for this generation includes clients such as DCEDMC, HDP, LSDMA, JPEG, VCN, VCNU, and VSCH.

## Cross-Chunk Notes

The previous chunk should complete the beginning of `DAGB0_FATAL_ERROR_STATUS4`, including the `PRI`, `CHAIN`, and related shift/mask context that precedes the visible `DROP`, `WADDR_PHASE`, and `NOALLOC` masks. The next chunk should complete `MMVM_L2_CNTL4` and continue later MMVM L2, MM group, bank-select, parity/ECC, context, and invalidation-engine definitions. Whole-file research for `mmhub_3_0_2_sh_mask.h` should treat this as one generated register-map slice, not as independent executable logic.

### subset-b-002810: lines 4757-7198

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_3_0_2_sh_mask.h lines 4757-7198

## Scope

This chunk is a generated AMDGPU MMHUB 3.0.2 shift/mask header slice. It contains C preprocessor constants only: no functions, structs, enums, variables, allocations, locks, or executable branches. The range starts inside `MMVM_L2_CNTL4` after the first three field shifts were defined in the previous chunk, and it ends inside `MMMC_VM_MX_L1_TLB_CNTL` after `ENABLE_L1_TLB_MASK`; the remaining masks for that TLB register continue in the next chunk.

Within those boundaries the slice defines 2,124 `#define` entries across the MMHUB L2/UTCL2/MMVM shared register surface. Major covered blocks are:

- L2 cache and QoS controls: `MMVM_L2_CNTL4`, group real-time class bits, bank-select reserved client IDs, cache parity controls, clock-gating timing, `MMVM_L2_CNTL5`, GCR controls, busy controls, and PTE cache dump controls.
- GPUVA/VMID translation-assist request and response registers.
- Credit-safety registers for UTCL2/L2 return, invalidation, interrupt, and walker paths.
- `addressBlock: mmhub_mmutcl2_mmvml2vcdec`: VM context controls for contexts 0-15, context-disable bits, invalidation semaphore/request/ack/address-range registers for engines 0-17, page-table base/start/end address registers for contexts 0-15, and per-PF/VF PTE cache fragment-size controls.
- `addressBlock: mmhub_mmutcl2_mmvml2pldec` and `mmhub_mmutcl2_mmvml2prdec`: MM VM L2 and UTCL2 performance-counter configuration and result registers.
- `addressBlock: mmhub_mmutcl2_mmvmsharedhvdec`: per-VF framebuffer size/offset registers for VF0-VF15.
- `addressBlock: mmhub_mmutcl2_mmvmsharedpfdec`: physical-function/shared aperture, local memory, APT, clock/busy, no-allocate, harvest-bypass, and group-fault status controls.
- Beginning of `addressBlock: mmhub_mmutcl2_mmvmsharedvcdec`: framebuffer location, AGP aperture, system aperture, and the first field of L1 TLB control.

Although this repository path is under `sources/distributed-fs/ceph-client`, this file is AMD GPU MMIO metadata, not distributed-filesystem logic.

## Purpose

The purpose of the slice is to publish the bit-level ABI for MMHUB 3.0.2 registers. Each register field uses the generated AMD convention:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset for the field.
- `<REGISTER>__<FIELD>_MASK`: 32-bit field mask used to isolate or compose values.

The matching `mmhub_3_0_2_offset.h` file supplies register addresses such as `regMMVM_CONTEXT0_CNTL`, `regMMVM_INVALIDATE_ENG0_REQ`, `regMMMC_VM_FB_LOCATION_BASE`, and `regMMMC_VM_MX_L1_TLB_CNTL`. This header supplies the masks consumed by helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_OFFSET`, `RREG32_SOC15`, `RREG32_SOC15_OFFSET`, `WREG32_SOC15`, and `WREG32_SOC15_OFFSET`.

The most important operational purpose is MMHUB virtual-memory programming for AMDGPU: enabling contexts, setting page-table geometry, defining GART/system/AGP/framebuffer apertures, issuing VMID-scoped invalidations, tuning L2/UTCL2 behavior, and exposing diagnostic/performance/status fields.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this range. The public interface is the macro namespace consumed by AMDGPU MMHUB code.

Important macro groups include:

- `MMVM_L2_CNTL4` and `MMVM_L2_CNTL5`: L2 cache partitioning, VMC tap physical-request controls, non-RT/soft-RT IFIFO transaction limits, clock-gating overrides, visible-bank FIFO behavior, small-fragment size, walker priority client ID, walker PDE no-allocate/MTYPE enables, and fine-grain clock-gating disable bits.
- `MMVM_L2_MM_GROUP_RT_CLASSES`: 32 one-bit group real-time-class flags.
- `MMVM_L2_BANK_SELECT_RESERVED_CID` and `MMVM_L2_BANK_SELECT_RESERVED_CID2`: reserved read/write client IDs, enable bits, invalidation mode, private invalidation, and fragment-size selectors.
- `MMVM_L2_CACHE_PARITY_CNTL`: parity-check enables and forced parity-mismatch injection for 4K PTE, big-K PTE, and PDE caches, plus forced bank/cache/associativity selection.
- `MMVM_L2_CGTT_CLK_CTRL`, `MMVM_L2_CGTT_BUSY_CTRL`, `MMUTCL2_CGTT_CLK_CTRL`, and `MMUTCL2_CGTT_BUSY_CTRL`: clock-gating on-delay, off-hysteresis, light-sleep hysteresis, LS disable, busy override, read delay, and always-busy fields.
- `MMVM_L2_PTE_CACHE_DUMP_CNTL` and `MMVM_L2_PTE_CACHE_DUMP_READ`: PTE cache dump enable/ready selectors and dump data.
- `MMUTC_GPUVA_VMID_TRANSLATION_ASSIST_REQUEST_*` and `MMUTC_GPUVA_VMID_TRANSLATION_ASSIST_RESPONSE_*`: address, VMID, VF/VFID, GPA mode, requested permissions, client ID, request/ack bits, response permissions, fragment size, snoop/SPA/IO/TMZ/no-PTE/MTYPE/MEMLOG/NACK/LLC-noalloc metadata.
- `MMVM_CONTEXT0_CNTL` through `MMVM_CONTEXT15_CNTL`: context enable, page-table depth and block size, retry behavior, and interrupt/default handling for range, dummy-page, PDE0, valid, read, write, execute, and secure protection faults.
- `MMVM_CONTEXTS_DISABLE`: packed disable bits for contexts 0-15 and related context disable controls.
- `MMVM_INVALIDATE_ENG0_*` through `MMVM_INVALIDATE_ENG17_*`: semaphore fields, per-VMID invalidate request mask, flush type, L2 PTE/PDE and L1 PTE invalidate bits, protection-fault address clear, logging, 4K-only mode, ack bits, and invalidate address ranges.
- `MMVM_CONTEXT*_PAGE_TABLE_BASE_ADDR_*`, `MMVM_CONTEXT*_PAGE_TABLE_START_ADDR_*`, and `MMVM_CONTEXT*_PAGE_TABLE_END_ADDR_*`: low/high pieces for each context's page-table base and aperture bounds.
- `MMVM_L2_PER_PFVF_PTE_CACHE_FRAGMENT_SIZES` and `MMVM_L2_CONTEXT*_PER_PFVF_PTE_CACHE_FRAGMENT_SIZES`: per-PF/VF and per-context PTE cache fragment-size selectors for PF, VF0, and VF1.
- `MMMC_VM_L2_PERFCOUNTER*_CFG`, `MMUTCL2_PERFCOUNTER*_CFG`, `MMMC_VM_L2_PERFCOUNTER_RSLT_CNTL`, `MMUTCL2_PERFCOUNTER_RSLT_CNTL`, and result LO/HI registers: performance event selection, selection-end range, mode, enable, clear, result-counter selection, start/stop trigger, global clear, stop-on-saturate, low counter bits, high counter bits, and compare value.
- `MMMC_VM_FB_SIZE_OFFSET_VF0` through `MMMC_VM_FB_SIZE_OFFSET_VF15`: packed virtual-function framebuffer size and offset fields.
- `MMMC_VM_FB_OFFSET`, `MMMC_VM_FB_LOCATION_BASE`, and `MMMC_VM_FB_LOCATION_TOP`: framebuffer offset/base/top fields used to derive memory-controller visible VRAM placement.
- `MMMC_VM_SYSTEM_APERTURE_DEFAULT_ADDR_*`, `MMMC_VM_SYSTEM_APERTURE_LOW_ADDR`, and `MMMC_VM_SYSTEM_APERTURE_HIGH_ADDR`: default physical page address and system aperture logical address bounds.
- `MMMC_VM_AGP_BASE`, `MMMC_VM_AGP_BOT`, and `MMMC_VM_AGP_TOP`: AGP aperture address fields.
- `MMMC_VM_APT_CNTL`, cacheable-DRAM/local-system/local-FB address range fields, `MMMC_VM_LOCAL_FB_ADDRESS_LOCK_CNTL`, and `MMMC_VM_FB_NOALLOC_CNTL`: aperture translation policy, locality checks, fragment-size cap, local sysmem aperture control, lock bit, and no-allocate behavior.
- `MMUTCL2_HARVEST_BYPASS_GROUPS` and `MMUTCL2_GROUP_RET_FAULT_STATUS`: harvested/bypassed group mask and return-fault group status.
- Partial `MMMC_VM_MX_L1_TLB_CNTL`: shifts for L1 TLB enable, system access mode, unmapped system aperture access, advanced driver model, ECO bits, MTYPE, and only the first mask in this chunk.

## Control Flow

This header chunk has no runtime control flow. Runtime sequencing is supplied by consumers in `amdgpu/mmhub_v3_0_2.c`:

1. `mmhub_v3_0_2_init()` records register offsets for page-table base registers, invalidation semaphore/request/ack registers, context control, L2 fault status/control, context stride, invalidation-engine stride, and the reserved CID2 register.
2. `mmhub_v3_0_2_gart_enable()` programs the GART page-table base, context 0 aperture start/end, AGP/system/default apertures, L1 TLB controls, L2 cache controls, context 0 enablement, context 1-15 VMID controls, and invalidation address ranges.
3. `mmhub_v3_0_2_get_invalidate_req()` composes an invalidate request with `MMVM_INVALIDATE_ENG0_REQ` fields: per-VMID bit, flush type, L2 PTE/PDE invalidation, L1 PTE invalidation, and protection-fault-address clear.
4. `mmhub_v3_0_2_setup_vmid_config()` iterates VM contexts 1-15 using `hub->ctx_distance`, programs `MMVM_CONTEXT1_CNTL` fields for enablement, page-table depth/block size, default fault behavior, and retry/no-retry behavior, then writes page-table start/end bounds using the address-register stride.
5. `mmhub_v3_0_2_program_invalidation()` iterates 18 invalidation engines using `hub->eng_addr_distance` and initializes each engine's address range to a broad range.
6. `mmhub_v3_0_2_gart_disable()` clears all 16 context-control registers, disables L1 TLB and advanced-driver-model bits in `MMMC_VM_MX_L1_TLB_CNTL`, disables L2 cache, and clears `MMVM_L2_CNTL3`.

Other fields in the chunk are diagnostic, RAS/validation, performance, SR-IOV, and power-management surfaces. The masks alone do not encode whether a field is read-only, write-one-to-clear, sticky, self-clearing, or sequencing-sensitive.

## State And Persistence Behavior

The header itself stores no software state and persists nothing. It describes MMIO-backed hardware state in the MMHUB memory-management path.

The represented hardware state includes:

- VM context state: context enable bits, page-table depth/block size, per-fault interrupt/default behavior, retry policy, and 64-bit page-table base/start/end address fields.
- Invalidation state: semaphore, request, ack, VMID mask, flush type, L2/L1 invalidation selectors, optional logging, 4K-only mode, and invalidate address ranges for 18 engines.
- Aperture and memory-placement state: GART/system/AGP/framebuffer bounds, default physical page, local FB/sysmem/cacheable-DRAM ranges, local FB lock, and memory steering.
- L2/UTCL2 cache and TLB state: L2 transaction limits, walker behavior, bank selection/reserved client IDs, PTE fragment sizes, parity checking/injection, PTE cache dump controls, L1 TLB enable and policy fields.
- SR-IOV partition state: per-VF framebuffer size and offset for VF0-VF15, plus per-PF/VF PTE cache fragment-size selectors and VF-aware translation-assist metadata.
- Translation-assist state: request and response payloads for GPUVA/VMID translation assistance, including VMID/VFID, permissions, client ID, memory type, snoop/SPA/IO, PTE TMZ, no-PTE, NACK, LLC no-allocate, request, and ack status.
- Diagnostic and performance state: L2 and UTCL2 performance counter configuration, result selection, triggers, clear bits, stop-on-saturate behavior, counter values, compare values, group return fault status, and harvest-bypass groups.
- Power/clock state: CGTT clock-control and busy-control fields for L2 and UTCL2, plus memory light-sleep setup/hold fields.

Persistence is hardware-defined. Configuration registers generally persist until reset, power-gating loss, suspend/resume restore, or explicit reprogramming. Status, clear, ack, request, counter, fault, and parity-injection fields may have side effects or transient behavior and need hardware-specific sequencing from the surrounding driver.

## Dependencies And Integration Points

This chunk depends on the generated MMHUB 3.0.2 register-header set:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_3_0_2_offset.h` supplies the matching register addresses and base indices.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v3_0_2.c` directly includes this shift/mask header and the offset header.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v3_0_2.h`, `amdgpu.h`, `soc15_common.h`, and common VM/MMHUB helpers provide the driver-side structures and MMIO helper APIs that consume these macros.

Direct integration observed in this tree:

- `mmhub_v3_0_2_get_invalidate_req()` uses `MMVM_INVALIDATE_ENG0_REQ` fields from this chunk to create the invalidate command consumed by common VM hub invalidation paths.
- `mmhub_v3_0_2_setup_vm_pt_regs()`, `mmhub_v3_0_2_init_gart_aperture_regs()`, and `mmhub_v3_0_2_setup_vmid_config()` use the context page-table base/start/end offsets whose fields are described here; the values are written in page-number units using low/high register pairs.
- `mmhub_v3_0_2_init_system_aperture_regs()` writes AGP and system aperture registers covered here and skips host-owned aperture bounds for SR-IOV virtual functions.
- `mmhub_v3_0_2_init_tlb_regs()` uses `MMMC_VM_MX_L1_TLB_CNTL` fields covered by the end of this chunk and masks continued in the next chunk to enable L1 TLB, advanced driver model, system access mode, and uncached MTYPE.
- `mmhub_v3_0_2_init_cache_regs()` writes `MMVM_L2_CNTL4` and `MMVM_L2_CNTL5` fields in this chunk and skips inaccessible cache registers for SR-IOV virtual functions.
- `mmhub_v3_0_2_enable_system_domain()` and `mmhub_v3_0_2_setup_vmid_config()` use context-control fields from this chunk for system VMID and user VMID setup.
- `mmhub_v3_0_2_program_invalidation()` uses invalidate-engine address-range registers from this chunk to initialize all 18 engines.
- `mmhub_v3_0_2_init()` derives `ctx_distance`, `ctx_addr_distance`, `eng_distance`, and `eng_addr_distance` from adjacent register offsets whose field layouts are represented here, and builds `hub->vm_cntx_cntl_vm_fault` from `MMVM_CONTEXT1_CNTL` interrupt masks.
- `mmhub_v3_0_2_get_fb_location()` masks `regMMMC_VM_FB_LOCATION_BASE` with `MMMC_VM_FB_LOCATION_BASE__FB_BASE_MASK`, and `mmhub_v3_0_2_get_mc_fb_offset()` reads `regMMMC_VM_FB_OFFSET`; both field definitions are in this chunk.

Indirect integration is expected in performance/debug tooling, SR-IOV management, firmware/hypervisor setup, and hardware validation code that uses the performance-counter, translation-assist, per-VF framebuffer, parity, PTE dump, and harvest/fault-status fields.

## Risks And Edge Cases

- Bitfield drift is high impact. A wrong shift or mask can silently program a different MMHUB field and cause VM faults, invalidation failure, stale translations, broken apertures, or GPU hangs.
- The chunk starts and ends mid-register. `MMVM_L2_CNTL4` is incomplete at the start, and `MMMC_VM_MX_L1_TLB_CNTL` is incomplete at the end. The merge lane must combine adjacent chunks before making complete file-level statements about those registers.
- Context registers are repeated 16 times with nearly identical layouts. Driver code often programs context 1 using `hub->ctx_distance` to reach contexts 1-15; offset or stride mismatches can leave some VMIDs disabled or with wrong fault/retry policy.
- Invalidation registers are repeated 18 times. Per-engine request/ack/range fields must stay aligned with `hub->eng_distance` and `hub->eng_addr_distance`; a bad stride can poll or program the wrong invalidation engine.
- Invalidation request fields are command-like, not passive data. Incorrect `PER_VMID_INVALIDATE_REQ`, `FLUSH_TYPE`, L1/L2/PDE selectors, or address range can leave stale TLB/cache entries after VM page-table updates.
- Page-table base/start/end values are split across low/high 32-bit registers and written in shifted page-number units. Incorrect shifts or high/low ordering can point MMHUB at the wrong page tables or expose the wrong virtual address range.
- Fault-policy fields affect user-visible recovery behavior. Misprogramming interrupt/default/retry bits can hide faults by redirecting to default pages, cause fault storms, or crash on faults that should be recoverable.
- SR-IOV fields and access restrictions are sensitive. `mmhub_v3_0_2.c` deliberately skips some PF-owned registers for virtual functions; writing per-VF framebuffer, aperture, cache, or translation-assist controls from the wrong privilege context can be blocked or corrupt partitioning assumptions.
- Diagnostic fields such as parity injection, PTE cache dump, performance-counter clear, and translation-assist request/ack can have side effects. They should not be changed by ordinary VM setup paths without validation intent.
- Clock-gating/busy fields can interact with active traffic. Bad CGTT/LS/busy programming can produce hangs or performance regressions that only appear under idle transitions or suspend/resume.
- Cross-generation similarity is not enough. Many names resemble other MMHUB versions, but masks, field presence, and address offsets must be kept matched to the 3.0.2 offset/mask pair.

## Test Signals

Useful validation signals for this chunk are build coverage, generated-header consistency, and MMHUB VM behavior:

- Build AMDGPU with MMHUB 3.0.2 support enabled. Missing or mismatched macros should surface in `mmhub_v3_0_2.c` through `REG_SET_FIELD`, mask constants, and offset/mask include use.
- Compare this generated header slice against AMD's authoritative MMHUB 3.0.2 register database and the matching `mmhub_3_0_2_offset.h`; every field name must align with the correct register offset and bit layout.
- Boot hardware using `mmhub_v3_0_2_funcs.gart_enable` and confirm GART setup succeeds without MMHUB VM faults during memory allocations, command submission, DMA, display/media traffic, and suspend/resume.
- Exercise VMID page-table updates and invalidations. Signals include correct invalidation ack behavior, no stale mappings after unmap/remap, and no timeouts in common VM hub invalidation paths.
- Stress all programmed VM contexts, especially contexts 1-15, to catch wrong context-control stride, page-table bounds, retry behavior, or fault-default settings.
- Validate fault handling by toggling default fault behavior through `set_fault_enable_default`, provoking controlled VM faults, and checking that interrupt/default/retry behavior and logged client information match expectations.
- Test SR-IOV PF and VF paths separately. VFs should avoid PF-owned aperture/cache writes, while PF/hypervisor setup should correctly expose per-VF framebuffer size/offset and aperture state.
- Validate framebuffer and aperture helpers: `get_fb_location()` should decode `MMMC_VM_FB_LOCATION_BASE__FB_BASE_MASK` correctly, and MC framebuffer offset reads should match platform memory maps.
- Run performance-counter/debug validation for L2 and UTCL2 counters: select events, clear, enable, set triggers, read LO/HI results, and verify stop-on-saturate or compare behavior where supported.
- Hardware validation can test parity/PTE-dump/translation-assist fields, but those should remain isolated from normal driver paths because they can inject errors, stall on ready/ack bits, or alter diagnostic state.

## Cross-Chunk Notes

The previous chunk owns the first `MMVM_L2_CNTL4` field shifts (`L2_CACHE_4K_PARTITION_COUNT`, `VMC_TAP_PDE_REQUEST_PHYSICAL`, and `VMC_TAP_PTE_REQUEST_PHYSICAL`). This chunk owns the rest of `MMVM_L2_CNTL4` masks and later fields. The next chunk owns the remaining `MMMC_VM_MX_L1_TLB_CNTL` masks plus following MMHUB 3.0.2 registers. The final per-file research document should reconcile those boundaries before describing complete L2 control or L1 TLB control behavior.

### subset-b-002811: lines 7199-7228

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_3_0_2_sh_mask.h lines 7199-7228

## Scope

This chunk is the final range of the generated AMDGPU MMHUB 3.0.2 shift/mask header. It contains only C preprocessor constants for register-field bit positions and masks, plus the closing `#endif` for `_mmhub_3_0_2_SH_MASK_HEADER`. There are no functions, structs, storage declarations, or executable branches in this range.

The visible lines finish the `MMMC_VM_MX_L1_TLB_CNTL` field masks, then define the `mmhub_mmutcl2_mmvml2pspdec` address block:

- `MMUTCL2_TRANSLATION_BYPASS_BY_VMID`
- `MMUTC_GPUVA_VMID_TRANSLATION_ASSIST_CNTL`
- `MMUTC_TRANSLATION_FAULT_CNTL0`
- `MMUTC_TRANSLATION_FAULT_CNTL1`

These masks are paired with register addresses in `mmhub_3_0_2_offset.h` and are consumed through AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`.

## Purpose

The purpose of this chunk is to provide the bit-level software contract for MMHUB 3.0.2 memory-management control registers at the end of the generated header. MMHUB is the memory hub used by non-graphics GPU clients; this register block controls address translation policy, L1 TLB behavior, VMID-specific bypass behavior, GPUVA translation-assist enablement, and default physical-page routing for translation faults.

The macros are ABI-like generated data. Driver code depends on the exact `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` names and values when composing or decoding 32-bit MMIO register values. A wrong mask can silently program the wrong hardware field.

## Important Macro Families

### `MMMC_VM_MX_L1_TLB_CNTL`

The chunk starts with the mask definitions for the shared MMVM L1 TLB control register:

- `SYSTEM_ACCESS_MODE_MASK` is `0x00000018L`, corresponding to bits 3:4.
- `SYSTEM_APERTURE_UNMAPPED_ACCESS_MASK` is `0x00000020L`, bit 5.
- `ENABLE_ADVANCED_DRIVER_MODEL_MASK` is `0x00000040L`, bit 6.
- `ECO_BITS_MASK` is `0x00000780L`, bits 7:10.
- `MTYPE_MASK` is `0x00003800L`, bits 11:13.

The immediately preceding lines in the same register definition provide the matching shifts and `ENABLE_L1_TLB_MASK`. In `amdgpu/mmhub_v3_0_2.c`, `mmhub_v3_0_2_init_tlb_regs()` reads `regMMMC_VM_MX_L1_TLB_CNTL`, sets `ENABLE_L1_TLB`, `SYSTEM_ACCESS_MODE`, `ENABLE_ADVANCED_DRIVER_MODEL`, clears `SYSTEM_APERTURE_UNMAPPED_ACCESS`, clears `ECO_BITS`, sets `MTYPE` to `MTYPE_UC`, and writes the register back. `mmhub_v3_0_2_gart_disable()` later clears `ENABLE_L1_TLB` and `ENABLE_ADVANCED_DRIVER_MODEL`.

### `MMUTCL2_TRANSLATION_BYPASS_BY_VMID`

This register is in the `mmhub_mmutcl2_mmvml2pspdec` address block. Its two 16-bit fields split the register by VMID:

- `TRANS_BYPASS_VMIDS` uses bits 0:15 (`SHIFT 0x0`, `MASK 0x0000FFFFL`).
- `GPA_MODE_VMIDS` uses bits 16:31 (`SHIFT 0x10`, `MASK 0xFFFF0000L`).

The companion offset header maps `regMMUTCL2_TRANSLATION_BYPASS_BY_VMID` to offset `0x0a14` with base index 0 for MMHUB 3.0.2. This register is not directly programmed by `mmhub_v3_0_2.c` in the searched tree, but the generated field names expose PSP/MMUTCL2 policy control for firmware or future driver paths that need to select VMIDs whose translations bypass normal handling or run in GPA mode.

### `MMUTC_GPUVA_VMID_TRANSLATION_ASSIST_CNTL`

This control register has a single enable field:

- `ENABLE` uses bit 0 (`SHIFT 0x0`, `MASK 0x00000001L`).

The matching offset is `regMMUTC_GPUVA_VMID_TRANSLATION_ASSIST_CNTL` at `0x0a17`. In nearby MMHUB generations, this control belongs to a wider translation-assist register group with request/response registers. In MMHUB 3.0.2, this chunk only exposes the enable bit. The searched in-tree v3.0.2 runtime code does not toggle it directly.

### `MMUTC_TRANSLATION_FAULT_CNTL0` and `MMUTC_TRANSLATION_FAULT_CNTL1`

These registers define the default physical page attributes used by the MMUTC translation-fault path:

- `MMUTC_TRANSLATION_FAULT_CNTL0__DEFAULT_PHYSICAL_PAGE_ADDRESS_LSB` covers all 32 bits of CNTL0.
- `MMUTC_TRANSLATION_FAULT_CNTL1__DEFAULT_PHYSICAL_PAGE_ADDRESS_MSB` covers bits 0:3 of CNTL1.
- `MMUTC_TRANSLATION_FAULT_CNTL1__DEFAULT_IO` is bit 4.
- `MMUTC_TRANSLATION_FAULT_CNTL1__DEFAULT_SPA` is bit 5.
- `MMUTC_TRANSLATION_FAULT_CNTL1__DEFAULT_SNOOP` is bit 6.

The companion offsets are `regMMUTC_TRANSLATION_FAULT_CNTL0` at `0x0a1a` and `regMMUTC_TRANSLATION_FAULT_CNTL1` at `0x0a1b`. These are distinct from the `MMVM_L2_PROTECTION_FAULT_DEFAULT_ADDR_*` and `MMMC_VM_SYSTEM_APERTURE_DEFAULT_ADDR_*` registers that `mmhub_v3_0_2.c` actively programs during GART enable; they describe a PSP/MMUTC-side translation-fault default page route.

## Control Flow and Runtime Use

There is no control flow in this header chunk. Runtime behavior comes from code that includes this generated header.

The main MMHUB 3.0.2 runtime consumer is `amdgpu/mmhub_v3_0_2.c`, which includes both `mmhub_3_0_2_offset.h` and `mmhub_3_0_2_sh_mask.h`. Relevant flows are:

1. `mmhub_v3_0_2_gart_enable()` initializes GART and VM translation by calling GART aperture setup, system aperture setup, TLB setup, L2 cache setup, system-domain enablement, identity-aperture disablement, VMID configuration, and invalidation range programming.
2. `mmhub_v3_0_2_init_tlb_regs()` is the direct runtime consumer of the `MMMC_VM_MX_L1_TLB_CNTL` fields covered by this chunk. It performs a read-modify-write sequence using `REG_SET_FIELD` so reserved fields remain preserved while required translation-cache policy bits are changed.
3. `mmhub_v3_0_2_gart_disable()` uses the same L1 TLB control register to disable the L1 TLB and advanced driver model after disabling VM contexts.
4. `mmhub_v3_0_2_init_system_aperture_regs()` programs related aperture and protection-fault default registers, but it uses earlier register definitions rather than the `MMUTC_TRANSLATION_FAULT_CNTL0/1` fields in this tail chunk.
5. No direct in-tree writes were found for the 3.0.2 `MMUTCL2_TRANSLATION_BYPASS_BY_VMID`, `MMUTC_GPUVA_VMID_TRANSLATION_ASSIST_CNTL`, or `MMUTC_TRANSLATION_FAULT_CNTL0/1` fields. Their presence still matters because the generated header exports the hardware contract for firmware-facing or debug paths.

## State and Persistence Behavior

This file stores no software state. The state represented by these constants lives in hardware MMIO registers and persists until GPU reset, power-domain loss, suspend/resume reinitialization, PF/firmware reprogramming, or explicit driver writes.

Important hardware state represented by this chunk:

- `MMMC_VM_MX_L1_TLB_CNTL` controls whether MMHUB's L1 TLB and advanced driver model are active. The driver intentionally changes this during GART enable and disable.
- `SYSTEM_ACCESS_MODE`, `SYSTEM_APERTURE_UNMAPPED_ACCESS`, and `MTYPE` alter how untranslated or system-aperture memory traffic is handled.
- `MMUTCL2_TRANSLATION_BYPASS_BY_VMID` is VMID-indexed state. If programmed, it changes translation behavior for selected VMIDs and should be treated as security-sensitive under virtualization.
- `MMUTC_GPUVA_VMID_TRANSLATION_ASSIST_CNTL.ENABLE` gates translation-assist behavior. Incorrect persistence across reset or VF/PF transitions could leave assist handling unexpectedly active or inactive.
- `MMUTC_TRANSLATION_FAULT_CNTL0/1` represent a split physical page address plus IO/SPA/snoop attributes for default translation-fault handling.

The split default physical-page address fields require consistent page-number packing: CNTL0 carries the low 32 bits of the default physical page address field and CNTL1 carries four high bits plus attributes. A stale or badly shifted value can redirect faulting traffic to the wrong physical page.

## Dependencies and Integration Points

Generated-register dependencies:

- `mmhub_3_0_2_offset.h` provides the register offsets: `regMMMC_VM_MX_L1_TLB_CNTL` at `0x0873`, `regMMUTCL2_TRANSLATION_BYPASS_BY_VMID` at `0x0a14`, `regMMUTC_GPUVA_VMID_TRANSLATION_ASSIST_CNTL` at `0x0a17`, `regMMUTC_TRANSLATION_FAULT_CNTL0` at `0x0a1a`, and `regMMUTC_TRANSLATION_FAULT_CNTL1` at `0x0a1b`.
- Earlier chunks of `mmhub_3_0_2_sh_mask.h` define the matching shifts for `MMMC_VM_MX_L1_TLB_CNTL`, system aperture registers, VM context registers, L2 cache registers, protection-fault controls, and invalidation registers used by the same MMHUB setup flow.
- The SOC15 register helpers in AMDGPU compose these masks with offsets and per-instance base indices.

Driver integration:

- `amdgpu/mmhub_v3_0_2.c` is the primary consumer for this ASIC's MMHUB register definitions. It wires MMHUB functions into `mmhub_v3_0_2_funcs` and initializes `adev->vmhub[AMDGPU_MMHUB0(0)]` with register offsets and fault handling callbacks.
- `amdgpu_vmhub` integration uses this header indirectly through `hub->ctx_distance`, `hub->ctx_addr_distance`, invalidation offsets, and fault status/control offsets. The chunk's L1 TLB control participates in that broader GART/VM enablement sequence.
- SR-IOV integration is important because nearby setup code skips PF-only shared aperture/cache programming when `amdgpu_sriov_vf(adev)` is true. Any future use of the PSP/MMUTCL2 bypass or fault-default registers must observe the same PF/VF ownership constraints.
- Adjacent MMHUB generations expose similar names with different offsets and sometimes additional translation-assist fields. This chunk must remain paired with MMHUB 3.0.2 offsets, not 3.0.0, 3.0.1, 3.3.0, 4.1.0, or 4.2.0 definitions.

## Risks and Edge Cases

- Mixing this 3.0.2 mask header with another generation's offset header can silently target the wrong register or bit. The same field names recur across MMHUB generations, but offsets and register availability differ.
- `MMMC_VM_MX_L1_TLB_CNTL` is programmed by read-modify-write. A bad mask can damage unrelated reserved or policy bits, affecting translation correctness or performance.
- Enabling the L1 TLB or advanced driver model before apertures and page tables are initialized can expose stale translations; disabling them while VM contexts are active can cause translation failures or severe performance loss.
- `SYSTEM_APERTURE_UNMAPPED_ACCESS` and `SYSTEM_ACCESS_MODE` affect how unmapped system aperture accesses behave. Wrong values can turn expected faults into default-page accesses or vice versa.
- `MMUTCL2_TRANSLATION_BYPASS_BY_VMID` can alter translation behavior for up to 16 VMIDs in each field. Incorrect VMID bit selection is a virtualization and isolation risk.
- The translation-fault default page is split across CNTL0/CNTL1. Incorrect shifting, failure to update both halves, or stale IO/SPA/snoop attributes can redirect faulting requests incorrectly.
- The tail chunk ends the include guard. Any generator or merge error that drops the final `#endif` breaks downstream compilation for all consumers of the generated header.

## Test and Verification Signals

Useful validation signals for this chunk are build coverage, register readback, and GART/VM behavioral tests:

- Compile coverage for MMHUB 3.0.2 paths should include `mmhub_3_0_2_sh_mask.h` and verify all `REG_SET_FIELD` references in `mmhub_v3_0_2.c` resolve.
- Register readback after `mmhub_v3_0_2_gart_enable()` should show `MMMC_VM_MX_L1_TLB_CNTL.ENABLE_L1_TLB=1`, `SYSTEM_ACCESS_MODE=3`, `ENABLE_ADVANCED_DRIVER_MODEL=1`, `SYSTEM_APERTURE_UNMAPPED_ACCESS=0`, `ECO_BITS=0`, and `MTYPE=MTYPE_UC`.
- Register readback after `mmhub_v3_0_2_gart_disable()` should show `MMMC_VM_MX_L1_TLB_CNTL.ENABLE_L1_TLB=0` and `ENABLE_ADVANCED_DRIVER_MODEL=0`.
- GART smoke tests should exercise MMHUB clients such as HDP, JPEG, VCN, LSDMA, and display-related clients listed in `mmhub_client_ids_v3_0_2` and confirm translations work after enablement.
- VM fault tests should verify that L2 protection fault logging still reports sensible `CID`, `RW`, `MORE_FAULTS`, `WALKER_ERROR`, `PERMISSION_FAULTS`, and `MAPPING_ERROR` fields through the v3.0.2 fault callback.
- SR-IOV tests should verify VF paths do not program PF-owned shared MMHUB registers and that PF/firmware ownership is respected for translation bypass and translation-fault default policy.
- Suspend/resume and GPU reset tests should confirm that TLB policy and related aperture/fault registers are restored after hardware state loss.

## Cross-Chunk Notes

This chunk is only the tail of `mmhub_3_0_2_sh_mask.h`. The final per-file report should merge it with earlier chunks that define the rest of `MMMC_VM_MX_L1_TLB_CNTL`, the system aperture/default address registers, VM context registers, invalidation registers, L2 cache/protection-fault fields, and fault status fields used by `mmhub_v3_0_2.c`.
