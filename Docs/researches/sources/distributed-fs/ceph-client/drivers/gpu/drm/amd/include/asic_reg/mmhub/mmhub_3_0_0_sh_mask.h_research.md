# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_3_0_0_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002798`: lines 1-2377, `Docs/researches/chunks/subset-b-002798_research.md`
- `subset-b-002799`: lines 2378-4760, `Docs/researches/chunks/subset-b-002799_research.md`
- `subset-b-002800`: lines 4761-7204, `Docs/researches/chunks/subset-b-002800_research.md`
- `subset-b-002801`: lines 7205-7478, `Docs/researches/chunks/subset-b-002801_research.md`

## Chunk Research

### subset-b-002798: lines 1-2377

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_3_0_0_sh_mask.h lines 1-2377

## Scope

This chunk covers the opening of the generated AMD MMHUB 3.0.0 shift/mask header. The file starts with the AMD MIT-style license, the `_mmhub_3_0_0_SH_MASK_HEADER` include guard, and the beginning of the `mmhub_dagbdec` address block. Lines 1-2377 cover `DAGB0` decoder definitions from the read-client registers through the first fields of `DAGB0_SDP_CGTT_CLK_CTRL`.

The chunk is data-only C preprocessor content. It defines register field offsets and bit masks; it does not define functions, structs, enums, global variables, storage, or executable control flow.

## Purpose

The purpose of this header section is to provide the bit-level ABI for AMDGPU MMHUB 3.0.0 DAGB0 programming. Each field is represented by the standard generated pair:

- `<REGISTER>__<FIELD>__SHIFT`, the bit position used when shifting a value into or out of a register.
- `<REGISTER>__<FIELD>_MASK`, the 32-bit mask used to isolate, clear, or compose that field.

Driver code includes this header together with `mmhub_3_0_0_offset.h`. The offset header supplies addresses such as `regDAGB0_CNTL_MISC2`; this header supplies the field layout for those registers. Consumers normally use AMDGPU helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET` instead of open-coding shifts and masks.

## Register Families

### Read Client Control

The chunk starts with `DAGB0_RDCLI0` through `DAGB0_RDCLI23`. These 24 read clients all share the same field layout: `VIRT_CHAN`, `CHECK_TLB_CREDIT`, high and low urgency thresholds, maximum and minimum bandwidth enable/value fields, `OSD_LIMITER_ENABLE`, and `MAX_OSD`.

This family controls how individual MMHUB read request clients are mapped onto virtual channels and throttled. The repeated 24-client layout is important because client IDs elsewhere in MMHUB code identify GPU blocks such as display, HDP, SDMA, JPEG, VCN, and debug clients. A stale shift or mask here would route traffic to the wrong VC or apply an unintended bandwidth/OSD policy to a hardware client.

The shared read-side control registers that follow include:

- `DAGB0_RD_CNTL`, with bandwidth windows, shared VC count, and round-robin enable.
- `DAGB0_RD_IO_CNTL` and `DAGB0_RD_GMI_CNTL`, with two priority override slots plus common priority.
- `DAGB0_RD_ADDR_DAGB`, enabling DAGB address handling, jump-ahead behavior, self-init control, `WHOAMI`, and jump mode.
- `DAGB0_RD_CGTT_CLK_CTRL` and `DAGB0_L1TLB_RD_CGTT_CLK_CTRL`, which expose on-delay, off-hysteresis, light-sleep assertion hysteresis, light-sleep disable, and busy override fields for clock-gating/test control.

### Read Burst, Lazy Timer, VC, and Credit Control

Read address DAGB burst and lazy-timer settings are split into three registers each for clients 0-7, 8-15, and 16-23. `DAGB0_RD_ADDR_DAGB_MAX_BURST*` and `DAGB0_RD_ADDR_DAGB_LAZY_TIMER*` pack eight 4-bit client fields per register.

Virtual-channel control appears as `DAGB0_RD_VC0_CNTL` through `DAGB0_RD_VC5_CNTL`, plus `DAGB0_RD_IO_VC_CNTL` and `DAGB0_RD_GMI_VC_CNTL`. These set storage credits, max/min bandwidth, OSD limiting, and maximum OSD per VC or special IO/GMI channel. Additional read-side credit registers include:

- `DAGB0_RD_CNTL_MISC`, primarily storage pool credit.
- `DAGB0_RD_TLB_CREDIT`, with six packed TLB credit fields.
- `DAGB0_RD_RDRET_CREDIT_CNTL` and `DAGB0_RD_RDRET_CREDIT_CNTL2`, with VC read-return credits, pool credit, VC mode, and fixed equality controls.

The read pending and override registers (`DAGB0_RDCLI_ASK_PENDING`, `GO_PENDING`, `GBLSEND_PENDING`, `TLB_PENDING`, `OARB_PENDING`, `ASK2ARB_PENDING`, `ASK2DF_PENDING`, `OSD_PENDING`, `ASK_OSD_PENDING`, `NOALLOC_OVERRIDE`, and `NOALLOC_OVERRIDE_VALUE`) are full-width bitmaps. They let diagnostic or low-level code observe per-client busy/pending state and override no-allocate behavior.

### Write Client Control

`DAGB0_WRCLI0` through `DAGB0_WRCLI23` mirror the read-client layout: virtual channel, TLB-credit checking, urgency thresholds, bandwidth enable/value fields, OSD limiter, and maximum OSD. The write-side shared controls include:

- `DAGB0_WR_CNTL`, with client/VC bandwidth windows, round-robin enable, and update behavior for FED/NACK.
- `DAGB0_WR_IO_CNTL` and `DAGB0_WR_GMI_CNTL`, with priority override slots.
- `DAGB0_WR_ADDR_DAGB`, `DAGB0_WR_CGTT_CLK_CTRL`, and `DAGB0_L1TLB_WR_CGTT_CLK_CTRL`.
- `DAGB0_WR_ADDR_DAGB_MAX_BURST*` and `DAGB0_WR_ADDR_DAGB_LAZY_TIMER*` for write-address clients.
- `DAGB0_WR_DATA_DAGB`, `DAGB0_WR_DATA_DAGB_MAX_BURST*`, and `DAGB0_WR_DATA_DAGB_LAZY_TIMER*` for the separate write-data path.

The split between write-address and write-data DAGB programming is a key hardware distinction in this chunk. Address arbitration, data arbitration, burst sizing, and lazy timers can be controlled independently, so consumers must use the address-path masks for address DAGB registers and the data-path masks for data DAGB registers.

### Write VC, Credits, Pending, and Overrides

`DAGB0_WR_VC0_CNTL` through `DAGB0_WR_VC5_CNTL`, `DAGB0_WR_IO_VC_CNTL`, and `DAGB0_WR_GMI_VC_CNTL` mirror the read VC controls. `DAGB0_WR_CNTL_MISC` adds storage pool credit and HDP client ID selection.

Write-side credit fields are more varied than the read-side fields:

- `DAGB0_WR_TLB_CREDIT` packs six TLB credit fields.
- `DAGB0_WR_DATA_CREDIT` separates deadlock VC, large burst, middle burst, and small burst credits.
- `DAGB0_WR_MISC_CREDIT` controls atomic credit and deadlock VC number.
- `DAGB0_WR_DATA_FIFO_CREDIT_CNTL1` and `DAGB0_WR_ATOMIC_FIFO_CREDIT_CNTL1` control VC0-VC3 credits, pool credit, VC mode, and fixed arbitration/equality fields.

The write pending bitmaps cover request, grant, global-send, TLB, OARB, fabric, OSD, and data-bus phases. Write-only override groups include GPU snoop override and no-allocate override masks and values. These are hardware state/diagnostic surfaces rather than normal algorithmic data structures.

### DAGB Miscellaneous, FIFO, Performance, and L1TLB Access

The middle of the chunk defines control and status surfaces around DAGB0 itself:

- `DAGB0_DAGB_DLY` selects a delay, client, and position.
- `DAGB0_CNTL_MISC` exposes bandwidth init cycle.
- `DAGB0_CNTL_MISC2` includes read/write/TLB/SDP busy overrides, swap control, parity checking, read/write return clock-gating related controls, and read-return FIFO performance selection.
- `DAGB0_FIFO_EMPTY`, `DAGB0_FIFO_FULL`, `DAGB0_RD_CREDITS_FULL`, and `DAGB0_WR_CREDITS_FULL` are compact status bitmaps.
- `DAGB0_PERFCOUNTER_LO`, `DAGB0_PERFCOUNTER_HI`, `DAGB0_PERFCOUNTER0_CFG`, `DAGB0_PERFCOUNTER1_CFG`, `DAGB0_PERFCOUNTER2_CFG`, and `DAGB0_PERFCOUNTER_RSLT_CNTL` define local DAGB performance counter data, compare value, event selection, mode, enable, clear, trigger, and stop-on-saturate fields.
- `DAGB0_L1TLB_REG_RW` exposes command bits for L1 TLB register read/write control plus a large reserved field.
- `DAGB0_RESERVE1` through `DAGB0_RESERVE4` are full-width reserved masks.

`amdgpu/mmhub_v3_0.c` directly includes this header and uses `DAGB0_CNTL_MISC2` masks while programming MMHUB clock-gating behavior. That consumer demonstrates the intended use pattern: read a register, clear or set named mask bits, then write the register back through SOC15 MMIO helpers.

### SDP Configuration and Error Handling

The final third of this chunk is the start of the `DAGB0_SDP_*` family. It describes the SDP path connecting DAGB traffic to downstream fabric behavior:

- `DAGB0_SDP_RD_BW_CNTL` controls SDP read bandwidth enable/value, minimum bandwidth, and max bandwidth window.
- `DAGB0_SDP_PRIORITY_OVERRIDE` provides two priority override slots with per-direction enables for DRAM, GMI, and IO read/write.
- `DAGB0_SDP_RD_PRIORITY` and `DAGB0_SDP_WR_PRIORITY` assign per-VC priorities.
- `DAGB0_SDP_RD_CLI2SDP_VC_MAP` and `DAGB0_SDP_WR_CLI2SDP_VC_MAP` map SRT, NRT, deadlock, HRT, IO, and GMI traffic classes to SDP VCs.
- `DAGB0_SDP_ENABLE`, `DAGB0_SDP_CREDITS`, `DAGB0_SDP_TAG_RESERVE*`, `DAGB0_SDP_VCC_RESERVE*`, and `DAGB0_SDP_VCD_RESERVE*` control enablement, tag limits, response credits, tag reservation, and credit reservation distribution.
- `DAGB0_SDP_ERR_STATUS` contains read/write response status, read data status/parity error, clear-error command, busy-on-error behavior, fatal/unrecoverable indication, interrupt policy, and completion fatal handling.
- `DAGB0_SDP_REQ_CNTL` defines pass/chain overrides, inner-domain mode, and request block levels for read, write, and atomic traffic.
- `DAGB0_SDP_MISC` and `DAGB0_SDP_MISC2` contain early write-return enables, original-data and link-manager behavior, FIFO margins, request blocking state, and read-response credit release mode.
- `DAGB0_SDP_ARB_CNTL0` and `DAGB0_SDP_ARB_CNTL1` configure early read/write switching, error event/halt behavior, DED mode, and read/write burst limits.

The chunk also covers fatal error reporting registers: `DAGB0_FATAL_ERROR_CNTL`, `DAGB0_FATAL_ERROR_CLEAR`, and `DAGB0_FATAL_ERROR_STATUS0` through `STATUS4`. These fields capture validity, client ID, address low/high portions, CLI/SDP tags, VF/VFID, address space/IO/size, operation, write/read TMZ, snoop, invalidation, NACK, read-only, memory log, internal/external fatal flags, priority, chain/full/drop, write-address phase, and no-allocate state.

The last lines start `DAGB0_SDP_CGTT_CLK_CTRL` and define only its first five shift fields in this chunk. Its masks continue in the next chunk of the same source file.

## Important APIs, Types, and Functions

There are no callable APIs, types, or functions in this chunk. The important interface is the macro namespace itself. Names are generated in a stable pattern that couples:

- Register name comments such as `//DAGB0_RDCLI0`.
- A set of `__SHIFT` constants.
- A matching set of `_MASK` constants.

The effective API consumers rely on is compile-time availability of these exact macro names. Renaming, deleting, or changing a mask is a source-compatible and hardware-compatible change only if all AMDGPU register programming and all matching offset/default headers are updated together.

## Control Flow

This chunk has no runtime control flow. Hardware sequencing is implied by register semantics in consumers:

1. The driver computes field values using `REG_SET_FIELD` or direct mask operations.
2. The driver writes the composed value through SOC15 MMIO helpers to the address from `mmhub_3_0_0_offset.h`.
3. Hardware applies arbitration, credit, clock-gating, pending-state, performance-counter, SDP, or fatal-error behavior.
4. For status and pending registers, driver/debug code reads the register and uses `REG_GET_FIELD` or mask tests to decode the state.

Several fields are command or strobe style controls rather than durable state, especially clear/error, enable/clear performance counter, request block, and override bits. Test or reset code must respect hardware ordering when toggling them.

## State and Persistence

The header itself has no mutable state and persists nothing. The state described by these macros lives in MMHUB hardware registers. Some fields represent configuration that persists until reset or another register write, such as bandwidth windows, VC mappings, credit allocation, clock-gating controls, and SDP request policy. Other fields represent live status or captured error state, such as pending bitmaps, FIFO full/empty indicators, performance counter values, SDP error status, and fatal error status registers.

Because these are memory-mapped hardware registers, persistence is hardware lifecycle dependent. GPU reset, power gating, firmware initialization, or PF/VF separation in SR-IOV can restore or block access to subsets of this state.

## Dependencies and Integration Points

Primary dependencies are:

- `mmhub_3_0_0_offset.h`, which supplies the register addresses matching these field layouts.
- AMDGPU SOC15 register helpers and bitfield helpers, especially `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`.
- `drivers/gpu/drm/amd/amdgpu/mmhub_v3_0.c`, which includes this header and uses MMHUB 3.0.0 masks while configuring VM, TLB/cache, fault handling, clock gating, and register addresses.
- Hardware documentation or generator inputs that define MMHUB 3.0.0 DAGB0 field positions.

This header is also structurally paired with nearby generated headers for other MMHUB IP versions. Similar register families appear in `mmhub_2_0_0_sh_mask.h`, `mmhub_3_0_1_sh_mask.h`, and later MMHUB headers, but field presence can vary by generation. Version-specific C code must include the matching version header.

## Risks

The main risk is silent hardware misprogramming. These constants are trusted by low-level driver code; an incorrect bit position can change unrelated fields, route traffic through the wrong virtual channel, overconstrain credits, leave clock gating disabled, fail to clear errors, or decode fatal errors incorrectly.

Large repeated client blocks are susceptible to generator or copy/paste drift. The `RDCLI*` and `WRCLI*` families are intentionally repetitive, but even one inconsistent mask would affect only one hardware client and could appear as a workload-specific GPU hang, bandwidth regression, or VM fault.

Read/write address/data path separation is another hazard. Write address DAGB and write data DAGB registers look similar but are distinct. Using the wrong macro family could configure burst or lazy timer behavior for the wrong pipeline stage.

Status and command fields share registers in some families. Code that clears or enables bits without preserving unrelated fields can accidentally drop fatal status, alter interrupt policy, or change request blocking. Consumers should prefer read-modify-write helpers with the correct masks.

The file ends mid-register for `DAGB0_SDP_CGTT_CLK_CTRL` in this chunk. Any per-file analysis or generated documentation must reconcile this with the following chunk before treating that register as fully documented.

## Test Signals

Useful signals for validating code that depends on this chunk include:

- Successful compile of `amdgpu/mmhub_v3_0.c` with `mmhub_3_0_0_offset.h` and this header included together.
- GPU boot without MMHUB register-access faults on ASICs using MMHUB 3.0.0.
- Correct GART/VM initialization, TLB invalidation, and MMHUB protection fault reporting in `dmesg`.
- Clock-gating tests that toggle `DAGB0_CNTL_MISC2` fields and observe expected power/performance behavior without hangs.
- Stress workloads that exercise display, HDP, SDMA, JPEG/VCN, and IO/GMI clients without read/write pending bitmaps sticking.
- Performance counter configuration that increments, clears, triggers, and saturates according to `DAGB0_PERFCOUNTER*` settings.
- Error-injection or fault tests that populate `DAGB0_SDP_ERR_STATUS` and `DAGB0_FATAL_ERROR_STATUS*` fields with decodable client, address, VF, tag, operation, and fatality information.

### subset-b-002799: lines 2378-4760

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_3_0_0_sh_mask.h lines 2378-4760

## Scope And Purpose

This chunk is the second slice of the AMDGPU MMHUB 3.0.0 register shift/mask header. It is a generated-style hardware definition file: every exposed bitfield is represented by preprocessor constants named `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`. There are no C functions, structs, enums, variables, branches, loops, or executable initialization in this range.

The covered range starts at the tail of the `DAGB0_SDP_CGTT_CLK_CTRL` masks, then defines the full `DAGB0_SDP_LATENCY_SAMPLING` register. It then covers the `DAGB1` read-side DAGB client, arbitration, virtual-channel, pending/status, performance-counter, and SDP interface fields. The middle of the chunk switches to the `mmhub_pctldec` power/control block, including deep-sleep controls, power-gating/deep-sleep allow masks for UTCL2 and slices, RENG/stctrl save ranges, PCTL status, PCTL performance counters, and reserved registers. The final part covers L1 TLB status and performance-counter masks, `MM_ATC_L2` translation/cache controls, fixed-frame-buffer mapping (`MMUTCL2_FFBM`) controls, and the beginning of `MMVM_L2` cache/invalidation controls.

The chunk ends at line 4760 after the first four `MMVM_L2_CNTL3` shift macros. The rest of `MMVM_L2_CNTL3` masks and later MMVM L2 registers are intentionally outside this chunk and must be reconciled with the next chunk.

## Important APIs, Types, And Constants

There are no callable APIs or C types. The public interface is the macro namespace consumed by AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15*`, and `WREG32_SOC15*` after this header is included with its companion offset header.

Important macro families in this chunk:

- `DAGB0_SDP_LATENCY_SAMPLING`: sampler enable and selector fields for DRAM, GMI, IO, read, write, atomic-return, atomic-no-return, and virtual-channel latency sampling. This completes the small DAGB0 tail inherited from the previous chunk boundary.
- `DAGB1_RDCLI0` through `DAGB1_RDCLI23`: per-read-client policy registers. Each client uses the same layout: `VIRT_CHAN`, `CHECK_TLB_CREDIT`, urgency high/low thresholds, max/min bandwidth enable and value fields, OSD limiter enable, and max outstanding request limit.
- `DAGB1_RD_CNTL`, `DAGB1_RD_IO_CNTL`, and `DAGB1_RD_GMI_CNTL`: shared read-path arbitration and fabric controls, including client/VC max-bandwidth windows, shared VC count, round-robin enable, IO level-compliance/override controls, GMI credits, GMI level, max burst, and lazy timer.
- `DAGB1_RD_ADDR_DAGB`, `DAGB1_RD_ADDR_DAGB_MAX_BURST0-2`, and `DAGB1_RD_ADDR_DAGB_LAZY_TIMER0-2`: read-address DAGB enablement, jump-ahead, self-init-disable, `WHOAMI`, and packed per-client burst/lazy-timer fields.
- `DAGB1_RD_VC0_CNTL` through `DAGB1_RD_VC5_CNTL`, plus `DAGB1_RD_IO_VC_CNTL` and `DAGB1_RD_GMI_VC_CNTL`: read virtual-channel credit and QoS controls, including storage credits, EA credits, max/min bandwidth controls, OSD limiter fields, and max outstanding counts. MMHUB 3.0.0 exposes six numbered read VCs here rather than a full `VC0-VC7` sequence in this chunk.
- `DAGB1_RD_CNTL_MISC`, `DAGB1_RD_TLB_CREDIT`, `DAGB1_RD_RDRET_CREDIT_CNTL`, and `DAGB1_RD_RDRET_CREDIT_CNTL2`: storage-pool credits, UTCL2 VCI, legacy read-return cache-coherency mode, packed TLB0-TLB5 credits, and read-return per-VC credits.
- `DAGB1_RDCLI_*_PENDING`, `DAGB1_FIFO_EMPTY`, `DAGB1_FIFO_FULL`, and `DAGB1_RD_CREDITS_FULL`: full-width or packed status bitmaps for internal read-client pipeline stages, FIFO state, and credit-full conditions.
- `DAGB1_RDCLI_NOALLOC_OVERRIDE` and `DAGB1_RDCLI_NOALLOC_OVERRIDE_VALUE`: 16-bit enable/value maps for no-allocate override policy.
- `DAGB1_CNTL_MISC`, `DAGB1_CNTL_MISC2`, and clock-gating controls such as `DAGB1_RD_CGTT_CLK_CTRL`, `DAGB1_L1TLB_RD_CGTT_CLK_CTRL`, and `DAGB1_SDP_CGTT_CLK_CTRL`: delay, bandwidth-gap/init cycles, parity, urgent halt/boost, clock-gating disable, and busy-override fields.
- `DAGB1_PERFCOUNTER_LO/HI`, `DAGB1_PERFCOUNTER0_CFG` through `2_CFG`, and `DAGB1_PERFCOUNTER_RSLT_CNTL`: DAGB1 performance-counter result, compare, event select, mode, enable, clear, trigger, global clear/enable, and stop-on-saturate fields.
- `DAGB1_SDP_*`: SDP read bandwidth, priority override, read priority, client-to-SDP VC map, enable, credits, tag reserve, VCC reserve, error status, request control, misc, arbitration, clock-gating, and latency-sampling fields. `DAGB1_SDP_ERR_STATUS` is especially stateful because it includes status nibbles, data-parity flag, clear bit, fatal-interrupt controls, level interrupt, and busy-on-error controls.
- `PCTL_CTRL`: MMHUB power-control fields for power-gating enable, deep-sleep mode, stctrl idle thresholds, protection-fault ignore, UTCL2 legacy mode, SDP disconnect mode, ZSC timer, Z9 power down/up, SNR disable, and write-ack guard.
- `PCTL_MMHUB_DEEPSLEEP_IB`, `PCTL_MMHUB_DEEPSLEEP_OVERRIDE`, `PCTL_MMHUB_DEEPSLEEP_OVERRIDE_IB`, `PCTL_PG_IGNORE_DEEPSLEEP`, and `PCTL_PG_IGNORE_DEEPSLEEP_IB`: bitmaps for deep-sleep input bits, override bits, and power-gating ignore-deep-sleep bits across `DS0-DS16`, `DS_ATHUB`, and `ALLIPS` variants. Some include `SETCLEAR` high-bit semantics.
- `PCTL_SLICE0_*` and `PCTL_SLICE1_*`: per-slice DAGB write/read busy selectors, deep-sleep allow/allow-IB masks, misc controls, RENG execution controls, RENG RAM index/data, and STCTRL register-save ranges/exclusion sets.
- `PCTL_UTCL2_*`: UTCL2 misc, RENG execution, RENG RAM index/data, and STCTRL register-save range/exclusion fields.
- `PCTL_STATUS`: status bits for MMHUB config done, interlock enable, fence request/ack, MMHUB idle, power-gating FSM command status, MMHUB power, and stale RENG RAM indicators for global, UTCL2, slice0, and slice1 RAMs.
- `PCTL_PERFCOUNTER_LO/HI`, `PCTL_PERFCOUNTER0_CFG`, `PCTL_PERFCOUNTER1_CFG`, and `PCTL_PERFCOUNTER_RSLT_CNTL`: PCTL counter results, compare value, event selection, enable/clear controls, start/stop triggers, and stop-on-saturate control.
- `PCTL_RESERVED_0` through `PCTL_RESERVED_3`: reserved register fields. They preserve generated register-map shape and should not be treated as safe write targets without hardware guidance.
- `MMMC_VM_MX_L1_TLB0_STATUS` through `TLB5_STATUS`: per-L1-TLB busy, parity-error-found, and aperture-fault-found status fields.
- `MMMC_VM_MX_L1_PERFCOUNTER0_CFG` through `3_CFG`, `MMMC_VM_MX_L1_PERFCOUNTER_RSLT_CNTL`, and `MMMC_VM_MX_L1_PERFCOUNTER_LO/HI`: L1 TLB performance-counter controls and readback fields.
- `MM_ATC_L2_CNTL`, `CNTL2`, `CACHE_DATA0-2`, `CNTL3-5`, `MM_GROUP_RT_CLASSES`, `STATUS`, `STATUS2`, `MISC_CG`, `MEM_POWER_LS`, `CGTT_CLK_CTRL`, and `SDPPORT_CTRL`: ATC L2 translation request counts, cache invalidation mode, default-page behavior, GPA request fragmentation, bank/cache update controls, cache-data readback fields, fragment sizes, ATS request credit, transaction limits, real-time class bitmap, busy/outstanding-request status, parity error info, clock/memory power controls, and SDP port clock-enable handshakes.
- `MMUTCL2_FFBM_CONFIG`, `ACCESS_CNTL`, `ADDRESS`, `DATA`, `INVALIDATE_REQUEST`, and `INVALIDATE_RESPONSE`: fixed-frame-buffer mapping TLB page size, request/grant handshake, VFID/address selection, valid/read/write/fragment/FB_SPA data fields, and invalidate request/ack fields.
- `MMVM_L2_CNTL`, `MMVM_L2_CNTL2`, and the beginning of `MMVM_L2_CNTL3`: MMVM L2 cache enable, fragment processing, endian swap modes, PDE0 tag generation, LRU update behavior, default page-out behavior, split/queue/cache-address modes, PDE fault classification, identity mode, L1/L2 invalidation request bits, per-domain invalidate disable, big-K optimization disable, VMID/cache invalidation modes, PDE cache size, and the first `MMVM_L2_CNTL3` update/bank fields.

## Control Flow And State Behavior

This header has no direct runtime control flow. It provides constants that compile into call sites performing MMIO register reads, writes, or read-modify-write sequences. The effective control flow is in AMDGPU MMHUB implementation files, especially code that uses `REG_SET_FIELD` and `WREG32_SOC15` against offsets from `mmhub_3_0_0_offset.h`.

Runtime state lives in GPU MMHUB hardware registers, not in this file. The DAGB1 read-path fields configure routing and QoS for read clients: virtual-channel selection, urgency thresholds, max/min bandwidth windows, outstanding request limits, TLB-credit checking, read-return credits, and SDP request/priority/VC mapping. Pending, FIFO, credit-full, and error-status fields expose live hardware pipeline state. Performance-counter fields are stateful controls for hardware accumulation, clearing, event selection, and result latching.

The PCTL fields drive power-management state for MMHUB blocks. `PCTL_CTRL` and deep-sleep/ignore/allow bitmaps affect whether MMHUB, UTCL2, and slice blocks can enter or ignore deep-sleep/power-gated states. RENG RAM and STCTRL save-range fields are part of register-engine/save-restore behavior around low-power transitions. `PCTL_STATUS` exposes the observable handshake state: config completion, interlock, fences, idle state, power state, command status, and stale RAM indicators.

The L1 TLB and ATC/MMVM L2 fields describe the virtual-memory translation path. L1 status registers report busy and fault/error findings. L1/PCTL/DAGB counters expose hardware event counts. ATC L2 and MMVM L2 controls configure translation request credits, cache update behavior, cache invalidation, fragment sizes, default-page behavior, status polling, and fixed-frame-buffer mapping. `MMUTCL2_FFBM_ACCESS_CNTL` and invalidate request/response pairs represent hardware handshakes: software requests access or invalidation and must observe grant/ack bits according to the hardware programming sequence.

Persistence is hardware-local and reset/power-state dependent. This header does not save register state, restore it after suspend, serialize MMIO access, poll status, or distinguish read-only, write-one-to-clear, sticky, or reserved fields. Those semantics must come from the ASIC programming guide and the driver code using these constants.

## Dependencies And Integration Points

The direct companion file is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_3_0_0_offset.h`, which supplies the `reg*` offsets and base indices for the register names used here. Examples from that offset file include `regDAGB1_RDCLI0` at `0x00b8`, `regPCTL_CTRL` at `0x0380`, `regMM_ATC_L2_CNTL` at `0x06c0`, `regMMUTCL2_FFBM_CONFIG` at `0x06d4`, and `regMMVM_L2_CNTL` at `0x0700`.

The main in-tree consumer for this exact generation is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v3_0.c`, which includes `mmhub/mmhub_3_0_0_offset.h` and `mmhub/mmhub_3_0_0_sh_mask.h`. Its VM initialization path programs `MMVM_L2_CNTL`, `MMVM_L2_CNTL2`, and `MMVM_L2_CNTL3` using these masks, then writes the corresponding MMHUB registers. Later suspend/disable paths clear `MMVM_L2_CNTL` and `MMVM_L2_CNTL3`. The same conceptual MMVM L2 fields are used by adjacent generation implementations such as `mmhub_v3_0_2.c`, `mmhub_v3_3.c`, and `mmhub_v4_1_0.c`, but those must include their own generation-specific register headers.

DAGB1, PCTL, SDP, L1 TLB, ATC L2, and FFBM macros may be used by firmware bring-up code, debug/register-dump paths, power-management flows, performance-counter tooling, or future driver changes even when this tree's active MMHUB v3.0 code only uses a subset. The generated macro namespace must therefore stay aligned with the hardware offset file, the ASIC IP discovery data, and any scripts or tools that decode register dumps.

## Risks And Edge Cases

- The file is a hardware ABI. A wrong mask or shift can silently program the wrong bitfield while compiling cleanly, causing VM translation failures, stale TLB/cache contents, incorrect power transitions, or distorted performance counters.
- The repeated `DAGB1_RDCLI0-23` layout is easy to misread. A single copied field with the wrong client number could affect only one read client and be hard to diagnose without per-client traffic tests.
- Packed fields are common: client, VC, deep-sleep, TLB, counter, and cache-fragment fields often occupy adjacent 1-, 2-, 3-, 4-, 5-, 6-, 7-, 8-, or 10-bit ranges. Off-by-one shifts can produce plausible register values that target a neighboring client or selector.
- Full-width masks such as `0xFFFFFFFFL` should be handled as unsigned 32-bit register values. Signed promotion or debug formatting can make register dumps misleading.
- Status and control fields are mixed in the same header without access-mode metadata. Fields named `CLEAR`, `ACK`, `REQUEST`, `GRANT`, `BUSY`, `STATUS`, `FOUND_*`, and `*_ERROR_*` may be read-only, sticky, write-one-to-clear, pulse, or handshake fields depending on hardware semantics.
- PCTL power/deep-sleep fields are high risk because incorrect writes can prevent MMHUB from idling, power down an active block, lose register-engine state, or mask a protection fault during power transitions.
- Translation-cache and invalidation fields are high risk because stale VM/ATC/MMVM state can produce DMA to stale physical pages or persistent page faults. `INVALIDATE_ALL_L1_TLBS`, `INVALIDATE_L2_CACHE`, FFBM invalidation request bits, and status/ack bits must be sequenced by real driver logic, not blindly toggled from masks.
- Reserved PCTL fields preserve generated map shape, not software permission to write those bits.
- The chunk boundary splits `MMVM_L2_CNTL3`; whole-file research must use the next chunk before making complete statements about that register's masks.

## Test And Validation Signals

There are no direct unit tests for this macro-only header. Useful validation signals are compile-time, static, and hardware-facing:

- Build AMDGPU code paths that include `mmhub_3_0_0_sh_mask.h`, especially `drivers/gpu/drm/amd/amdgpu/mmhub_v3_0.c`, and treat warnings or undefined macro errors as integration failures.
- Run static mask/shift consistency checks: each mask should be contiguous after right-shifting by its shift value; single-bit masks should match `1U << shift`; repeated packed fields should not overlap; full-width fields should have shift zero.
- Cross-check every register-comment group in this chunk against `mmhub_3_0_0_offset.h` for a matching `reg*` offset and base index.
- Compare the repeated `DAGB1_RDCLI*`, deep-sleep bitmap, slice0/slice1, L1 TLB status, and performance-counter layouts against adjacent MMHUB generation headers only as a sanity check. Exact values remain generation-specific.
- On supported hardware, verify MMHUB v3.0 VM bring-up by observing `mmhub_v3_0.c` writes to `MMVM_L2_CNTL`, `MMVM_L2_CNTL2`, and `MMVM_L2_CNTL3`, then checking that VM/GART initialization, page-table updates, and TLB/cache invalidation paths do not report MMHUB protection faults.
- For PCTL changes, exercise suspend/resume, runtime power management, deep-sleep entry/exit, and register dumps around `PCTL_STATUS` to confirm fence, idle, power, and stale-RAM bits transition as expected.
- For DAGB1/SDP/performance-counter changes, run memory/display workloads with register dumps or perf-counter reads to confirm traffic counters, error status, and latency-sampling fields behave monotonically or clear as expected.

## Chunk Notes For Merge Lane

This chunk covers the DAGB1 read-side and SDP section, the full PCTL block present in this range, L1 TLB status/performance counters, ATC L2 and FFBM controls, and the start of MMVM L2 controls for `mmhub_3_0_0_sh_mask.h`. It is not a whole-file report. The final per-file document should merge this with chunk 1 for the beginning of DAGB0, chunk 3 for the rest of `MMVM_L2_CNTL3` and later MMVM/MMEA sections, and chunk 4 for the file tail and include-guard closure.

### subset-b-002800: lines 4761-7204

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_3_0_0_sh_mask.h lines 4761-7204

## Scope And Purpose

This chunk is a generated-style AMDGPU MMHUB 3.0.0 register field header. It contains C preprocessor constants only: every hardware field is represented as `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` macros. There are no C functions, structs, enums, storage objects, or executable branches in this range.

The range starts inside the `MMVM_L2_CNTL3` register definition and then covers most of the MMHUB MMUTCL2/MMVML2 virtual-memory control surface: L2 status and fault handling, identity aperture fields, L2 cache/cache-parity controls, VM context controls for contexts 0-15, invalidation engines 0-17, page-table base/start/end address registers for contexts 0-15, PTE cache fragment-size controls, MMHUB and UTCL2 performance counters, per-VF framebuffer size/offset registers, and the beginning of PF/shared aperture controls. The chunk ends at line 7204 in the middle of `MMMC_VM_FB_NOALLOC_CNTL`; the remaining masks for that register are outside this work item.

The companion offset header is `mmhub_3_0_0_offset.h`. That file maps register names such as `regMMVM_CONTEXT0_CNTL`, `regMMVM_INVALIDATE_ENG0_REQ`, and `regMMMC_VM_FB_SIZE_OFFSET_VF0` to MMIO offsets; this `_sh_mask.h` chunk defines the bit layout used to compose or decode the 32-bit values at those offsets.

## Important APIs, Types, And Constants

There are no callable APIs or declared C types. The public interface is the macro namespace consumed by AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_SOC15*`, `RREG32_SOC15*`, and `SOC15_REG_OFFSET`.

The main macro families in this chunk are:

- `MMVM_L2_CNTL3` tail fields: cache bank selection, update mode, wildcard reference value, big-page and 4K effective-size/associativity controls, and force-miss bits for 4K PTE, big-page PTE, and PDE caches. The register begins before this chunk.
- `MMVM_L2_STATUS`: L2 busy state, per-context/domain busy bitmap, and parity-error indicators for 4K PTE, big-page PTE, and PDE cache levels.
- Dummy-page and protection-fault registers: `MMVM_DUMMY_PAGE_FAULT_CNTL`, dummy-page fault address low/high, `MMVM_L2_PROTECTION_FAULT_CNTL`, `CNTL2`, `MM_CNTL3`, `MM_CNTL4`, `STATUS`, fault logical address low/high, and default physical page address low/high.
- Identity aperture registers: `MMVM_L2_CONTEXT1_IDENTITY_APERTURE_LOW_ADDR_*`, `HIGH_ADDR_*`, and `MMVM_L2_CONTEXT_IDENTITY_PHYSICAL_OFFSET_*`, which describe logical identity aperture bounds and physical offsets.
- L2 cache and routing controls: `MMVM_L2_CNTL4`, `MMVM_L2_MM_GROUP_RT_CLASSES`, `MMVM_L2_BANK_SELECT_RESERVED_CID`, `MMVM_L2_BANK_SELECT_RESERVED_CID2`, `MMVM_L2_CACHE_PARITY_CNTL`, `MMVM_L2_CGTT_CLK_CTRL`, `MMVM_L2_CNTL5`, `MMVM_L2_GCR_CNTL`, `MMVM_L2_CGTT_BUSY_CTRL`, `MMVM_L2_PTE_CACHE_DUMP_CNTL`, `MMVM_L2_PTE_CACHE_DUMP_READ`, and `MMVM_L2_BANK_SELECT_MASKS`.
- Credit-safety registers: `MMUTCL2_CREDIT_SAFETY_GROUP_RET_CDC`, `MMUTCL2_CREDIT_SAFETY_GROUP_CLIENTS_INVREQ_CDC`, `MMUTCL2_CREDIT_SAFETY_GROUP_CLIENTS_INVREQ_NOCDC`, `MMVML2_CREDIT_SAFETY_IH_FAULT_INTERRUPT`, and `MMVML2_WALKER_CREDIT_SAFETY_FETCH_RDREQ`. Each exposes a credit count plus an update bit.
- Address block `mmhub_mmutcl2_mmvml2vcdec`: `MMVM_CONTEXT0_CNTL` through `MMVM_CONTEXT15_CNTL`, all sharing the same field layout for `ENABLE_CONTEXT`, `PAGE_TABLE_DEPTH`, `PAGE_TABLE_BLOCK_SIZE`, retry behavior, and default/interrupt enables for range, dummy-page, PDE0, valid, read, write, and execute protection faults.
- `MMVM_CONTEXTS_DISABLE`: a packed disable bitmap for contexts 0-15.
- Invalidation engines 0-17: `MMVM_INVALIDATE_ENGn_SEM`, `REQ`, `ACK`, `ADDR_RANGE_LO32`, and `ADDR_RANGE_HI32`. Request fields include per-VMID invalidation bitmap, flush type, L2 PTE/PDE invalidation, L1 PTE invalidation, protection-fault address clearing, request logging, and 4K-only invalidation. Acknowledgements expose per-VMID ack plus semaphore state.
- Per-context page-table address registers: for contexts 0-15, `PAGE_TABLE_BASE_ADDR_LO32/HI32` expose full 64-bit page-directory-entry fields, while `PAGE_TABLE_START_ADDR_LO32/HI32` and `PAGE_TABLE_END_ADDR_LO32/HI32` expose logical page-number bounds with 32 low bits and 4 high bits.
- PTE fragment-size controls: `MMVM_L2_PER_PFVF_PTE_CACHE_FRAGMENT_SIZES` plus context-specific `MMVM_L2_CONTEXT0_PER_PFVF_PTE_CACHE_FRAGMENT_SIZES` through `CONTEXT15`, containing PF/VF and context fragment sizes for PTE cache behavior.
- Address block `mmhub_mmutcl2_mmvml2pldec`: `MMMC_VM_L2_PERFCOUNTER0_CFG` through `7_CFG`, `MMMC_VM_L2_PERFCOUNTER_RSLT_CNTL`, `MMUTCL2_PERFCOUNTER0_CFG` through `3_CFG`, and `MMUTCL2_PERFCOUNTER_RSLT_CNTL`. These cover performance event selection ranges, modes, enable/clear bits, start/stop triggers, global enable/clear, and stop-on-saturate.
- Address block `mmhub_mmutcl2_mmvml2prdec`: `MMMC_VM_L2_PERFCOUNTER_LO/HI` and `MMUTCL2_PERFCOUNTER_LO/HI`, with low 32-bit counter values and high 16-bit counter/compare-value packing.
- Address block `mmhub_mmutcl2_mmvmsharedhvdec`: `MMMC_VM_FB_SIZE_OFFSET_VF0` through `VF15`, each packing a 16-bit VF framebuffer size and 16-bit VF framebuffer offset.
- Address block `mmhub_mmutcl2_mmvmsharedpfdec`: `MMMC_VM_FB_OFFSET`, system aperture default physical page-number low/high, default steering, memory power light-sleep setup/hold, cacheable DRAM range, local sysmem range, APT controls, local FB range, local FB address lock, `MMUTCL2_CGTT_CLK_CTRL`, `MMUTCL2_CGTT_BUSY_CTRL`, and the first part of `MMMC_VM_FB_NOALLOC_CNTL`.

## Control Flow And State Behavior

The header has no runtime control flow. The C preprocessor substitutes constants into driver code that performs MMIO reads, writes, and read-modify-write operations against MMHUB registers.

Runtime state lives in the GPU. The context-control fields program how VMIDs translate memory: whether a context is enabled, page-table depth and block size, and whether different fault classes interrupt, retry, or fall back to default behavior. The page-table base/start/end registers define the active translation roots and logical aperture ranges for each context. The invalidation engine registers implement a hardware protocol: software writes semaphore/request/address-range registers, hardware updates acknowledgement bits, and callers poll or otherwise synchronize with the ack state.

Fault state is also hardware-resident. `MMVM_L2_PROTECTION_FAULT_STATUS` encodes whether more faults are queued, walker error class, permission bits, mapping error, client ID, read/write direction, atomic access, VMID, VF/VFID, and PRT status. Fault address and default-address registers expose the logical faulting page and fallback physical page location. Control bits such as `CLEAR_PROTECTION_FAULT_STATUS_ADDR`, retry fault interrupt enablement, and crash-on-fault settings influence how the hardware records and escalates faults.

Cache, clock-gating, credit, and performance-counter registers are stateful knobs around the translation cache. Cache fields configure fragment sizes, associativity, partitioning, force-miss behavior, parity checking, PTE dump selection/readback, and group real-time classes. Performance-counter config registers select events and modes, then enable or clear accumulation; result-control registers select counters, start/stop triggers, global clear, and stop-on-saturate behavior.

Persistence is hardware-local. Values generally persist only until reset, power-gating, firmware reinitialization, or driver reprogramming. This header does not store state, serialize access, distinguish read-only from write-only fields, or restore values across suspend/resume.

## Dependencies And Integration Points

The immediate register-offset dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_3_0_0_offset.h`. In that file, representative offsets are `regMMVM_L2_STATUS` at `0x0703`, `regMMVM_CONTEXT0_CNTL` at `0x0740`, `regMMVM_INVALIDATE_ENG0_REQ` at `0x0763`, `regMMMC_VM_L2_PERFCOUNTER0_CFG` at `0x0824`, `regMMMC_VM_FB_SIZE_OFFSET_VF0` at `0x084c`, and `regMMMC_VM_FB_OFFSET` at `0x08d7`.

The direct in-tree consumer for this exact header is `drivers/gpu/drm/amd/amdgpu/mmhub_v3_0.c`, which includes `mmhub/mmhub_3_0_0_offset.h`, `mmhub/mmhub_3_0_0_sh_mask.h`, and default-value headers. Important uses include:

- `mmhub_v3_0_get_invalidate_req()`: builds an invalidation request with `MMVM_INVALIDATE_ENG0_REQ` fields for per-VMID invalidation, flush type, L2 PTE/PDE invalidation, L1 PTE invalidation, and protection-fault-address clearing.
- `mmhub_v3_0_print_l2_protection_fault_status()`: decodes `MMVM_L2_PROTECTION_FAULT_STATUS` with `REG_GET_FIELD` to report client ID, read/write direction, walker errors, permission faults, VMID, VF/VFID, and PRT state.
- MMHUB cache/TLB initialization paths: program `MMVM_L2_CNTL3`, `MMVM_L2_CNTL4`, and `MMVM_L2_CNTL5` fields, including cache fragment-size and physical-request controls.
- `mmhub_v3_0_enable_system_domain()` and `mmhub_v3_0_setup_vmid_config()`: use `MMVM_CONTEXT0_CNTL` and `MMVM_CONTEXT1_CNTL` field macros to enable contexts, set page-table depth/block size, and configure protection-fault behavior for contexts 1-15 through offset strides.
- `mmhub_v3_0_disable_identity_aperture()`: writes the identity aperture and physical offset registers covered here, skipping VF-SRIOV where the PF is responsible.
- `mmhub_v3_0_program_invalidation()`: initializes all 18 invalidation engine address-range registers to the full supported range using the engine address stride.
- MMHUB register base setup: stores SOC15 offsets for context base address, invalidation semaphore/request/ack, context-control, L2 protection fault status/control, and bank-select reserved CID2; it derives `ctx_distance`, `ctx_addr_distance`, `eng_distance`, and `eng_addr_distance` from adjacent register offsets.

Similar macro families appear in `mmhub_3_0_1_sh_mask.h`, `mmhub_4_1_0_sh_mask.h`, and `mmhub_4_2_0_sh_mask.h`, but exact field widths and high-address masks differ by IP version. Call sites must include the matching generation header rather than assuming a common MMHUB layout.

## Risks And Edge Cases

- This file is a hardware ABI. A wrong mask or shift can still compile while programming the wrong bit in VM translation, fault, invalidation, or cache-control hardware.
- The chunk starts inside `MMVM_L2_CNTL3`; whole-file research should combine it with the prior chunk before describing the full register.
- The chunk ends inside `MMMC_VM_FB_NOALLOC_CNTL`; line 7204 includes `ROUTER_ATCL2_NOALLOC_MASK`, while `ROUTER_GPA_MODE2_NOALLOC_MASK` and `ROUTER_GPA_MODE3_NOALLOC_MASK` continue after the boundary.
- Repeated register groups are easy to misuse. Context 0 is the system/domain context, while contexts 1-15 are often programmed by stride from `MMVM_CONTEXT1_*`; invalidation engines 0-17 similarly rely on offset arithmetic. A correct-looking macro from the wrong context or engine can target the wrong register.
- Invalidation request, ack, and semaphore bits form a synchronization protocol with hardware. If callers set a flush type or per-VMID bitmap incorrectly, stale translations can remain visible or software can wait on the wrong acknowledgement bit.
- Fault-control bits can change system behavior sharply. Defaulting, interrupting, retrying, or crashing on retry/no-retry faults affects both diagnostics and user-visible GPU recovery behavior.
- Full-width masks such as `0xFFFFFFFFL` should be treated as unsigned 32-bit fields. Signed promotion can confuse diagnostics or static comparisons.
- Status, fault, counter, and cache-dump registers can be read-only, sticky, write-one-to-clear, or have other side effects depending on the hardware guide. The macro header does not encode access type.
- Per-VF framebuffer size/offset registers are virtualization-sensitive. Misprogramming VF size or offset can expose an incorrect framebuffer aperture or break SR-IOV isolation assumptions.
- Power and clock-gating controls such as `CGTT_CLK_CTRL`, light-sleep setup/hold, and busy overrides are low-level hardware knobs; invalid values can cause hangs, excessive power, or missed idle/busy transitions.

## Test And Validation Signals

There are no direct unit tests for this macro-only header chunk. Useful validation is compile-time, static, and hardware-oriented:

- Build AMDGPU configurations that include `mmhub_v3_0.c` and `mmhub_3_0_0_sh_mask.h`.
- Run static mask/shift checks: single-bit masks should match their shift, multi-bit masks should be contiguous, packed repeated fields should not overlap, and full-width masks should have shift zero.
- Cross-check every register-comment group in this chunk against `mmhub_3_0_0_offset.h` to verify that each register has a matching `reg*` offset and base index.
- Exercise MMHUB GART/VM bring-up on MMHUB 3.0 hardware and confirm that context enablement, page-table start/end bounds, identity aperture disablement, and invalidation address ranges match the values programmed by `mmhub_v3_0.c`.
- Trigger or inspect MMHUB VM fault reporting and verify that `MMVM_L2_PROTECTION_FAULT_STATUS` decodes client ID, RW, VMID, VF/VFID, permission, mapping, and PRT fields consistently with register dumps.
- Exercise GPUVM invalidation paths and verify request/ack progression for all active VMIDs; stale translation symptoms after mapping changes are a strong signal of bad invalidation masks.
- If performance counters are used by diagnostics, verify enable, clear, event select, result select, high/low readback, compare value, and stop-on-saturate behavior against hardware documentation.
- For SR-IOV, validate that PF-owned identity aperture and VF framebuffer size/offset programming are not touched by VF-only code paths and that VF register dumps reflect the expected aperture partitioning.

## Chunk Notes For Merge Lane

This chunk covers the central MMVM/MMUTCL2 field definitions for `mmhub_3_0_0_sh_mask.h`, especially VM contexts, invalidation engines, L2 fault/cache controls, performance counters, and PF/VF aperture fields. Merge with adjacent chunks before making whole-file claims about `MMVM_L2_CNTL3` or `MMMC_VM_FB_NOALLOC_CNTL`, because both register groups are split by this chunk's boundaries.

### subset-b-002801: lines 7205-7478

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
