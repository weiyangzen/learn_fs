# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_offset.h lines 4977-7451

## Scope

This chunk covers a generated AMD MMHUB 9.4.1 register-offset header slice. It starts inside the `mmhub_dagb_dagbdec6` address block at `mmDAGB6_RDCLI_TLB_PENDING_BASE_IDX`, then covers all of `mmhub_dagb_dagbdec7`, three MMEA decoder blocks, the second PCTL block, the `:1` L1/UTC virtual-memory blocks, and the opening portion of `mmhub_utcl2_vml2vcdec:1`. It ends at `mmVML2VC1_VM_CONTEXT9_PAGE_TABLE_START_ADDR_LO32_BASE_IDX`, before the remaining context start/end address macros.

The slice contains 2,431 `#define` lines: 1,215 register offset macros and 1,216 `_BASE_IDX` companion macros. Every register in this range uses `_BASE_IDX 1`, reflecting the SOC15 register base instance used by the generated offset table. There are no C functions, structs, enums, storage definitions, includes, or runtime logic here. Although the source tree path is under a local `ceph-client` mirror, this file is AMDGPU hardware register metadata, not distributed filesystem code.

## Purpose

The purpose of this header section is to name MMHUB 9.4.1 register offsets so AMDGPU code can program or read the correct MMIO locations through SOC15 register helpers. The companion `mmhub_9_4_1_sh_mask.h` header defines field shifts and masks; this file supplies the register names, offsets, and base-index selection that those fields attach to.

The covered registers describe:

- DAGB slice 6 tail and DAGB slice 7 traffic arbitration, credits, pending state, status, and performance counters.
- MMEA slices 5, 6, and 7 memory-client grouping, DRAM/GMI/IO/SDP arbitration, address normalization, error, and observability registers.
- PCTL1 deep-sleep, power-gating, RENG RAM, and state-save range controls for UTCL2 plus five slices.
- L1 TLB status and UTCL2/VML2 performance, invalidate, fault, and context-page-table registers for hub instance `:1`.

## Important Macro Families

### DAGB6 Tail And DAGB7

The first lines complete `DAGB6` by providing the `_BASE_IDX` for `mmDAGB6_RDCLI_TLB_PENDING`, then define read-side `OARB` and `OSD` pending offsets, all write clients `WRCLI0..15`, write control and GMI control, address/data DAGB routing controls, output burst and lazy-timer controls, clock-gating controls, write VC controls `WR_VC0_CNTL..WR_VC7_CNTL`, TLB/data/misc credits, GPU snoop override registers, write pending-state registers, FIFO/credit fullness status, performance counters, and reserved offsets through `mmDAGB6_RESERVE13`.

The `mmhub_dagb_dagbdec7` block begins at base address `0x74400` and is complete in this chunk. It defines the same broad DAGB pattern for slice 7: read client offsets, read aggregate control, read-side burst/timer/clock/VC/credit/status/performance registers, write client offsets, write-side control and pending registers, FIFO/fullness observability, and reserve registers. These macros are consumed as register names such as `mmDAGB7_RDCLI0`, `mmDAGB7_RD_CNTL`, `mmDAGB7_WR_CNTL`, and `mmDAGB7_PERFCOUNTER*_CFG`.

### MMEA5, MMEA6, And MMEA7

The `mmhub_ea_mmeadec5`, `mmhub_ea_mmeadec6`, and `mmhub_ea_mmeadec7` blocks start at base addresses `0x74a00`, `0x74f00`, and `0x75400`. Each block has the same generated register layout, with macro prefixes `mmMMEA5_`, `mmMMEA6_`, and `mmMMEA7_`.

Each MMEA block defines client-to-group and group-to-VC mapping registers for DRAM, GMI, IO, and SDP traffic; read and write lazy timers; CAM controls; page-burst controls; priority aging, queueing, fixed-priority, urgency, urgency masking, and quantum registers; address-normalization base/limit/offset entries; GMI peer/link address normalization entries; per-destination credit and write-credit controls; channel control/status; clock-gating controls; debug and reserve registers; and `ERR_STATUS`.

These offsets are the address side of MMHUB external-address arbitration. They let driver code configure how memory clients are grouped, how those groups map onto virtual channels, how arbitration policy differs between DRAM/GMI/IO/SDP paths, and how normalized address windows are represented.

### PCTL1

The `mmhub_pctldec1` block starts at base address `0x76300`. It defines `mmPCTL1_CTRL`, MMHUB deep-sleep interface and override registers, power-gating/deep-sleep ignore controls, per-slice DAGB busy and deep-sleep-allow registers for slices 0 through 4, UTCL2 and slice misc registers, RENG execute/index/data registers, and state-controller save ranges and exclusion sets.

The repeated `STCTRL_REGISTER_SAVE_RANGE0..4` and `STCTRL_REGISTER_SAVE_EXCL_SET0..1` families appear for UTCL2 and for each slice `SLICE0..SLICE4`. These offsets are used by power-management or reset flows that need hardware-assisted register save/restore boundaries and exclusions.

### L1 TLB And UTCL2/VML2 Instance 1

The `mmhub_l1tlb_vml1dec:1` block at base address `0x76500` defines `mmVML1_1_MC_VM_MX_L1_TLB0_STATUS` through `TLB7_STATUS`. The following `mmhub_l1tlb_vml1pldec:1` and `mmhub_l1tlb_vml1prdec:1` blocks define performance counter low/high/config offsets for the L1 TLB pipe-left and pipe-right blocks.

The `mmhub_utcl2_atcl2dec:1` block at base address `0x76600` covers ATCL2 memory power and performance counter offsets. The `mmhub_utcl2_vml2pfdec:1` block at `0x76700` covers VML2 prefetch controls, fault-clear/status/address registers, default-page and snapshot controls, VMID lookup range registers, and performance counters.

The `mmhub_utcl2_vml2vcdec:1` block starts at base address `0x76800` and is only partially covered here. This chunk includes VM L2 control and protection fault controls, bank select and cache controls, performance counters, invalidate request and acknowledgment registers for engines 0 through 17, invalidate address range low/high registers for engines 0 through 17, context page-table base address low/high registers for contexts 0 through 15, and context page-table start address low/high registers through context 9 low. The remaining context start and end address registers continue in the next chunk.

## Control Flow

This header has no executable control flow. Its effect is compile-time symbol substitution: AMDGPU code references a macro such as `mmVML2VC1_VM_INVALIDATE_ENG0_REQ` or `mmMMEA7_ERR_STATUS`, the preprocessor substitutes the register offset, and SOC15 register accessors combine that offset with the relevant base instance selected by `_BASE_IDX`.

The runtime sequencing belongs to consumers in MMHUB, GMC, VM, reset, clock-gating, power-management, and diagnostics code. Those consumers decide when to program DAGB QoS/credit state, when to configure MMEA arbitration and address normalization, when PCTL1 register-save or deep-sleep controls may be changed, and when VML2 invalidate/fault/context registers are written or polled.

## State And Persistence Behavior

The file itself stores no software state and persists nothing. It describes MMIO-backed hardware state. Register contents generally persist in hardware until reset, power-gating, suspend/resume restore, driver reprogramming, or hardware self-update, depending on the individual register semantics defined by the ASIC.

Important hardware state represented by this slice includes DAGB per-client arbitration and pending masks, write snoop overrides, credit accounting, FIFO/fullness status, and performance counters; MMEA memory-client grouping, priority and urgency policy, address normalization windows, destination credits, channel/debug state, and error status; PCTL1 deep-sleep and state-save configuration; L1 TLB status; VML2 prefetch/fault/snapshot/performance state; VML2 invalidate request/ack state; and VML2 per-context page-table base/start address state.

Several register names imply side effects or sequencing sensitivity even though this header cannot encode those rules: fault clear, invalidate request/acknowledge, performance counter clear or result controls, deep-sleep overrides, RENG execute controls, and state-save range programming. Consuming code must preserve the hardware-defined read/modify/write, polling, and ordering requirements.

## Dependencies And Integration Points

This chunk depends on AMD's generated MMHUB 9.4.1 register database. It must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_sh_mask.h`, which supplies the field-level shifts and masks for these register names.
- Other generated MMHUB 9.4.1 headers, including default-value headers when present.
- SOC15 base-address tables and AMDGPU register accessor macros such as `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, `REG_SET_FIELD`, and `REG_GET_FIELD`.

Expected consumers are AMDGPU MMHUB/GMC code paths for ASICs using MMHUB 9.4.1. Integration points include GPU VM hub setup, VM context page-table programming, VM invalidate issuance and acknowledgment polling, memory-client QoS setup, DRAM/GMI/IO/SDP arbitration setup, GMI peer addressing, clock-gating and deep-sleep policy, reset and suspend/resume register save/restore, fault reporting, error decoding, and performance/debug counter collection.

The `:1` suffix in the address-block comments and macro names such as `mmVML1_1_*` and `mmVML2VC1_*` is significant. It distinguishes the second MMHUB/UTCL2/VML2 instance from instance 0. Code that mixes instance-0 offsets with these instance-1 macros can target the wrong hub.

## Risks And Edge Cases

- Offset drift is high impact. A wrong value can direct MMIO reads or writes to an unrelated MMHUB register while still compiling cleanly.
- `_BASE_IDX` consistency matters. Every macro in this chunk uses base index `1`; using access helpers with a different base instance can corrupt another hub or silently read stale state.
- The chunk boundaries are artificial. This slice starts after the `mmDAGB6_RDCLI_TLB_PENDING` offset itself and ends before all `VML2VC1` context start/end address registers are present, so final file-level analysis must merge neighboring chunks before making complete claims.
- Repeated generated families are copy-sensitive. `DAGB6`/`DAGB7`, `MMEA5`/`MMEA6`/`MMEA7`, and context or invalidate-engine arrays have many near-identical names where a one-digit index error changes the hardware client, memory slice, VM context, or invalidate engine.
- VM invalidate registers are sequencing-sensitive. Request, acknowledge, and address-range registers must be programmed and polled in the order required by hardware; this header provides only addresses.
- VM context page-table base and start address registers are split low/high. Consumers must pair the correct low/high halves and preserve address alignment and logical page-number width.
- PCTL1 deep-sleep and register-save controls affect power and reset behavior. Bad ranges or exclusions can leave hardware state unrestored or block low-power entry.
- MMEA arbitration and address-normalization registers affect real memory routing and QoS. Bad group maps, VC maps, priority policies, credit limits, or address windows can cause starvation, incorrect peer/GMI routing, or memory faults.
- Status, fault, and error registers may be sticky, clear-on-write, or read-side-effecting depending on the hardware definition. Generic read/modify/write patterns are risky unless matched to the field semantics in the shift/mask and programming guides.

## Test Signals

Useful validation is mostly generated-header consistency plus hardware behavior:

- Build AMDGPU with MMHUB 9.4.1 support enabled; renamed, missing, or malformed macros should surface as compile failures in MMHUB/GMC/VM users.
- Mechanically compare this offset header with AMD's authoritative register database and verify that each register macro has the expected `_BASE_IDX` and matching field definitions in `mmhub_9_4_1_sh_mask.h`.
- Cross-check repeated register families for contiguous offsets and expected cardinality: DAGB7 clients and VC controls, MMEA5/6/7 matching layouts, PCTL1 UTCL2 plus slices 0-4 state-save ranges, VML2 invalidate engines 0-17, and VM contexts 0-15.
- Exercise GPU VM workloads that create, update, and invalidate page tables; verify invalidate acknowledgments complete and VM faults decode through the expected `VML2PF1`/`VML2VC1` registers.
- Run memory traffic across DRAM, GMI, IO, and SDP paths under graphics, compute, SDMA, and peer traffic; watch for hangs, throttling, starvation, or unexpected fault/error status.
- Test suspend/resume, GPU reset, and clock/deep-sleep transitions that depend on PCTL1 state-save and deep-sleep controls.
- Validate performance/debug paths by programming DAGB, L1TLB, ATCL2, VML2PF, and VML2VC counters and confirming low/high counter reads and result-control behavior.
- Where supported, inject or observe VM and MMHUB faults and confirm address/context/engine attribution is plausible for the instance-1 registers covered here.

## Cross-Chunk Notes

The previous chunk is needed for the beginning of `mmhub_dagb_dagbdec6`, including the offset half of `mmDAGB6_RDCLI_TLB_PENDING`. The next chunk is needed for the rest of `VML2VC1_VM_CONTEXT*_PAGE_TABLE_START_ADDR_*`, the corresponding end address registers, and any later MMHUB 9.4.1 offset blocks. The final per-file document should reconcile those boundaries before summarizing the complete `mmhub_9_4_1_offset.h` register map.
