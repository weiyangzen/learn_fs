# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_8_0_sh_mask.h lines 1-2366

## Scope And Purpose

This chunk is the opening range of the generated AMD MMHUB 1.8.0 register shift/mask header. It contains preprocessor constants only: each hardware register field is exposed as a `<REGISTER>__<FIELD>__SHIFT` and matching `<REGISTER>__<FIELD>_MASK` macro. There are no functions, structs, storage objects, or executable branches in this file section.

The covered register blocks are the complete `aid_mmhub_dagb_dagbdec0` address block and the beginning of `aid_mmhub_dagb_dagbdec1`. DAGB is the MMHUB data/address gateway block used to arbitrate and track read/write client traffic between GPU clients, L1 TLB/ATCVM paths, external address handling, GMI paths, and virtual-channel queues. This range defines bit layouts for:

- `DAGB0_RDCLI0` through `DAGB0_RDCLI15` and `DAGB0_WRCLI0` through `DAGB0_WRCLI15` client controls;
- read and write global controls, GMI controls, DAGB address/data controls, output max-burst/lazy-timer fields, and clock-gating controls;
- per-VC credit controls, TLB credits, read-return credits, write-data/misc/OSD/atomic credits, pending/busy status registers, no-allocation override, and GPU snoop override;
- `DAGB0` misc, fatal-error, FIFO, credit-full, performance-counter, and L1TLB register read/write control fields;
- the first part of `DAGB1`, from `DAGB1_RDCLI0` through the start of `DAGB1_RD_VC4_CNTL`, mirroring the read-side field shapes from `DAGB0`.

The header's purpose is to let AMDGPU MMHUB code build and decode 32-bit register values symbolically instead of open-coding bit positions around SOC15 MMIO accesses.

## Important APIs, Types, And Constants

There are no C APIs or types exported by this chunk. The useful interface is the macro namespace paired with `mmhub_1_8_0_offset.h` register-offset definitions.

- `DAGB0_RDCLI[0-15]` and `DAGB0_WRCLI[0-15]`: repeated per-client arbitration fields. Each client has `VIRT_CHAN`, `CHECK_TLB_CREDIT`, `URG_HIGH`, `URG_LOW`, `MAX_BW_ENABLE`, `MAX_BW`, `MIN_BW_ENABLE`, `MIN_BW`, `OSD_LIMITER_ENABLE`, and `MAX_OSD`. These tune virtual-channel selection, credit checking, urgency thresholds, bandwidth limiting, and outstanding request limits.
- `DAGB0_RD_CNTL` and `DAGB0_WR_CNTL`: top-level read/write scheduling fields for `SCLK_FREQ`, client/VC max-bandwidth windows, IO-level override/compliance, shared VC count, and jump-ahead behavior.
- `DAGB0_RD_GMI_CNTL` and `DAGB0_WR_GMI_CNTL`: GMI-facing credit, level, max-burst, and lazy-timer layouts.
- `DAGB0_RD_ADDR_DAGB`, `DAGB0_WR_ADDR_DAGB`, and `DAGB0_WR_DATA_DAGB`: DAGB enable/jump/whoami controls for read addresses, write addresses, and write data. The read/write address variants include `JUMP_MODE`; the write-data variant does not in this chunk.
- `DAGB0_*_OUTPUT_DAGB_MAX_BURST`, `DAGB0_*_OUTPUT_DAGB_LAZY_TIMER`, `DAGB0_*_ADDR_DAGB_MAX_BURST[0-1]`, `DAGB0_*_ADDR_DAGB_LAZY_TIMER[0-1]`, and `DAGB0_WR_DATA_DAGB_*`: packed nibble fields for VC0-VC7 or CLIENT0-CLIENT15 burst and timer settings.
- `DAGB0_RD_CGTT_CLK_CTRL`, `DAGB0_WR_CGTT_CLK_CTRL`, `DAGB0_L1TLB_*_CGTT_CLK_CTRL`, and `DAGB0_ATCVM_*_CGTT_CLK_CTRL`: clock-gating/low-power timing fields: `ON_DELAY`, `OFF_HYSTERESIS`, `LS_ASSERT_HYSTERESIS`, `LS_OVERRIDE`, and `SOFT_OVERRIDE`.
- `DAGB0_RD_VC[0-7]_CNTL` and `DAGB0_WR_VC[0-7]_CNTL`: VC storage/EA credits plus max/min bandwidth and outstanding request limiting. The write side also has `DAGB0_WR_DATA_CREDIT`, `DAGB0_WR_MISC_CREDIT`, `DAGB0_WR_OSD_CREDIT_CNTL[1-2]`, and `DAGB0_WR_ATOMIC_FIFO_CREDIT_CNTL1`.
- `DAGB0_RD_CNTL_MISC`, `DAGB0_WR_CNTL_MISC`, `DAGB0_RD_TLB_CREDIT`, and `DAGB0_WR_TLB_CREDIT`: pool, IO, TLB, UTCL2 CID, read-return FIFO, and write-data credit fields.
- `DAGB0_*_PENDING`, `DAGB0_FIFO_EMPTY`, `DAGB0_FIFO_FULL`, `DAGB0_WR_CREDITS_FULL`, and `DAGB0_RD_CREDITS_FULL`: full-width or wide status masks for in-flight queues and resource saturation.
- `DAGB0_RDCLI_NOALLOC_OVERRIDE`, `DAGB0_WRCLI_NOALLOC_OVERRIDE`, their `_VALUE` registers, and `DAGB0_WRCLI_GPU_SNOOP_OVERRIDE(_VALUE)`: per-client override masks. In `mmhub_v1_8.c`, the GPU snoop override fields are used for the SDMA client bit.
- `DAGB0_CNTL_MISC` and `DAGB0_CNTL_MISC2`: VC remapping, bandwidth initialization/gap cycles, urgency boost/halt, clock-gating disable bits, busy-disable bits, swap control, HDP CID, and read-return FIFO dlock credit fields.
- `DAGB0_FATAL_ERROR_CNTL`, `DAGB0_FATAL_ERROR_CLEAR`, and `DAGB0_FATAL_ERROR_STATUS[0-3]`: fatal-error filter, clear, valid/CID/address, tag/VFID/space/IO/size/debug/fed, and request attribute fields such as noalloc, unitid, op, security level, TMZ, snoop, inval, nack, RO, memlog, and EOP.
- `DAGB0_PERFCOUNTER_LO`, `DAGB0_PERFCOUNTER_HI`, `DAGB0_PERFCOUNTER[0-2]_CFG`, and `DAGB0_PERFCOUNTER_RSLT_CNTL`: counter result, compare value, event-select range, mode, enable/clear, trigger, and saturate behavior definitions.
- `DAGB0_L1TLB_REG_RW`: indirect L1TLB control read/write trigger bits, VMID exception interrupt control, write-data parity checking, read-return checking disable, and reserved high bits.
- `DAGB1_RDCLI[0-15]`, `DAGB1_RD_CNTL`, `DAGB1_RD_GMI_CNTL`, `DAGB1_RD_ADDR_DAGB`, `DAGB1_RD_OUTPUT_DAGB_*`, `DAGB1_*_RD_CGTT_CLK_CTRL`, `DAGB1_RD_ADDR_DAGB_*`, and `DAGB1_RD_VC[0-4]_CNTL` begin the second DAGB decoder instance with the same read-side layouts as `DAGB0`.

## Control Flow And State Behavior

This chunk has no local control flow. At compile time, it supplies constants consumed by C helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and `WREG32_SOC15_OFFSET`.

Runtime state lives in MMHUB hardware registers. Writes to the client, VC, credit, burst, lazy-timer, and clock-control fields alter live arbitration, bandwidth, queueing, and power behavior in the GPU memory hub. Reads from pending, FIFO, credit-full, fatal-error, and performance-counter fields report transient hardware state. The macros do not cache values, serialize access, poll for idle, or preserve state across reset; that responsibility belongs to the MMHUB driver code and firmware/PSP paths that own the register programming sequence.

The concrete v1.8 integration path in `mmhub_v1_8.c` programs MMHUB registers for each active AID instance. `mmhub_v1_8_init_snoop_override_regs()` computes the register distance between `regDAGB1_WRCLI_GPU_SNOOP_OVERRIDE` and `regDAGB0_WRCLI_GPU_SNOOP_OVERRIDE`, iterates five DAGB instances, and sets bit 15 in both the override-enable and override-value registers so SDMA writes probe-invalidate read/write cache lines. Other v1.8 MMHUB routines in the same file use this generated header for VM/L1TLB/L2 fields outside this particular line range.

Persistence is hardware-defined. Register contents may persist until GPU reset, MMHUB reinitialization, power-gating, suspend/resume restore, SR-IOV virtualization policy, or firmware intervention. Fatal-error status and performance-counter values are especially stateful: clear/enable bits can change the diagnostic state, while status fields are snapshots of hardware events.

## Dependencies And Integration Points

This file depends on being included with the matching `mmhub_1_8_0_offset.h` address/offset header. The mask header alone cannot address MMIO; offset macros such as `regDAGB0_RDCLI0`, `regDAGB0_WRCLI_GPU_SNOOP_OVERRIDE`, and `regDAGB1_WRCLI_GPU_SNOOP_OVERRIDE` provide the register numbers.

Important integration points in this source tree:

- `drivers/gpu/drm/amd/amdgpu/mmhub_v1_8.c` includes both `mmhub_1_8_0_offset.h` and `mmhub_1_8_0_sh_mask.h` and implements MMHUB v1.8 GART, VM page-table, aperture, L1TLB, cache, invalidation, and snoop-override setup.
- `drivers/gpu/drm/amd/amdgpu/gmc_v9_0.c` selects `mmhub_v1_8_funcs` and `mmhub_v1_8_ras` for the ASICs that use this MMHUB generation, so these macros feed the GC/GMC initialization path through the MMHUB function table.
- SOC15 register helpers (`RREG32_SOC15`, `WREG32_SOC15`, `RREG32_SOC15_OFFSET`, `WREG32_SOC15_OFFSET`) are the expected access layer. They combine the MMHUB block, instance/AID index, register offset, and optional per-DAGB offset.
- `REG_SET_FIELD`/`REG_GET_FIELD` style helpers depend on the exact generated macro naming convention: `<REG>__<FIELD>_MASK` and `<REG>__<FIELD>__SHIFT`.
- The `DAGB1` definitions are layout mirrors of `DAGB0` definitions but live at a separate address block; code using computed distances between DAGB instances depends on the companion offset header preserving instance spacing.
- Golden-register tables and later MMHUB implementations reuse the same conceptual DAGB fields. Those are useful comparison points, but masks are ASIC-version-specific and should not be freely mixed between MMHUB versions.

## Risks And Edge Cases

- Hardware contract drift is the core risk. A wrong mask or shift can program the wrong VC, urgency threshold, credit limit, clock-gating control, snoop override, fatal-error clear bit, or performance counter selector.
- This is a generated, repetitive header. Small differences between read/write, address/data, DAGB0/DAGB1, and VC/client variants matter. Mechanical edits can easily copy a `DAGB0` mask into a `DAGB1` consumer or treat write-data DAGB fields as if they had the same `JUMP_MODE` field as address DAGB fields.
- Many status fields are full-width or high-bit masks such as `0xFFFFFFFFL`, `0x80000000L`, `0xFC000000L`, and `0xFE000000L`. Consumers should treat register values as unsigned 32-bit quantities and avoid signed shifts or host-width assumptions.
- Pending, FIFO, fatal-error, and performance-counter registers are live hardware state. Read-modify-write operations against status or clear registers can lose events if callers do not understand write-one-to-clear, latch, or counter-clear semantics from the hardware spec.
- Clock-gating override fields (`LS_OVERRIDE`, `SOFT_OVERRIDE`, and `DISABLE_*_CG`) can affect power and idle behavior. Incorrect programming can cause idle/power regressions or hide busy state from higher-level power-management logic.
- GPU snoop override programming uses bit 15 for SDMA in current v1.8 code rather than a named field-specific helper. If client numbering changes, the hard-coded SDMA bit and the `ENABLE`/`VALUE` masks must be revalidated against this header and the ASIC spec.
- The chunk ends in the middle of the `DAGB1_RD_VC4_CNTL` register block. Whole-file research must merge subsequent chunks before making complete claims about DAGB1 or later MMHUB register families.
- SR-IOV and PSP-mediated paths can restrict direct register writes. `mmhub_v1_8_init_snoop_override_regs()` skips SR-IOV VFs, and L1TLB setup may use PSP register programming; direct use of these masks must respect those ownership boundaries.

## Test And Validation Signals

There are no direct unit tests for this macro chunk. Useful validation signals are integration and static checks:

- Build coverage for AMDGPU with `mmhub_v1_8.c` and `gmc_v9_0.c` enabled verifies that generated macro names still match consumers and SOC15 register helper expectations.
- Static mask/shift validation can check that every `_MASK` aligns with its `__SHIFT`, full-width fields have shift zero, repeated client/VC groups are internally consistent, and packed nibble/byte fields cover the expected bit ranges without overlap.
- MMHUB v1.8 hardware smoke tests should cover GART enable/disable, VM context setup, TLB invalidation, suspend/resume, and SDMA write coherency. The snoop override path should preserve cache coherence for SDMA writes that probe-invalidate read/write lines.
- RAS/error-path testing can inject or observe MMHUB faults and verify that `DAGB0_FATAL_ERROR_STATUS[0-3]` decoding reports valid client, address, VFID, request type, and attribute bits.
- Performance-counter validation can configure `DAGB0_PERFCOUNTER[0-2]_CFG`, select result registers via `DAGB0_PERFCOUNTER_RSLT_CNTL`, and confirm clear/enable/trigger behavior against expected traffic.
- Power-management and clock-gating validation should compare idle residency and MMHUB busy behavior before and after changes to `DAGB0_CNTL_MISC2` and `*_CGTT_CLK_CTRL` fields.
- Register dumps on supported ASICs can compare `DAGB0` and `DAGB1` repeated field layouts against `mmhub_1_8_0_offset.h` spacing and against AMD's generated register specification.

## Chunk Notes For Merge Lane

This is the first chunk of a much larger generated MMHUB 1.8.0 mask header. It fully covers `DAGB0` and only starts `DAGB1`; later chunks are required for the rest of DAGB1 and the remaining MMHUB address blocks. The final per-file document should preserve the distinction between compile-time macro vocabulary, companion offset definitions, and the runtime register programming implemented in `mmhub_v1_8.c`.
