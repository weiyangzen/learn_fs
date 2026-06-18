# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_8_0_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002774`: lines 1-2366, `Docs/researches/chunks/subset-b-002774_research.md`
- `subset-b-002775`: lines 2367-4719, `Docs/researches/chunks/subset-b-002775_research.md`
- `subset-b-002776`: lines 4720-7085, `Docs/researches/chunks/subset-b-002776_research.md`
- `subset-b-002777`: lines 7086-9431, `Docs/researches/chunks/subset-b-002777_research.md`
- `subset-b-002778`: lines 9432-11750, `Docs/researches/chunks/subset-b-002778_research.md`
- `subset-b-002779`: lines 11751-14067, `Docs/researches/chunks/subset-b-002779_research.md`
- `subset-b-002780`: lines 14068-16391, `Docs/researches/chunks/subset-b-002780_research.md`
- `subset-b-002781`: lines 16392-18711, `Docs/researches/chunks/subset-b-002781_research.md`
- `subset-b-002782`: lines 18712-21060, `Docs/researches/chunks/subset-b-002782_research.md`
- `subset-b-002783`: lines 21061-22628, `Docs/researches/chunks/subset-b-002783_research.md`

## Chunk Research

### subset-b-002774: lines 1-2366

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

### subset-b-002775: lines 2367-4719

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_8_0_sh_mask.h lines 2367-4719

## Scope

This chunk covers 2,353 lines from the generated AMD MMHUB 1.8.0 shift/mask header. It starts inside the `DAGB1_RD_VC4_CNTL` field group at `DAGB1_RD_VC4_CNTL__MAX_BW__SHIFT`, continues through the rest of the DAGB1 read and write data-arbitration group B field definitions, includes DAGB1 status, fatal-error, performance-counter, and L1 TLB register fields, then enters the `aid_mmhub_dagb_dagbdec2` address block for DAGB2 read/write field definitions. The slice ends inside `DAGB2_WR_ADDR_DAGB_LAZY_TIMER0`, after the `CLIENT1_MASK` field; the remaining `CLIENT2..CLIENT7` masks and later DAGB2 write fields are outside this chunk.

The range contains 2,185 `#define` macros and no C functions, structs, enums, storage objects, inline helpers, or executable statements. The macros define bit positions and masks only; the companion `mmhub_1_8_0_offset.h` file supplies register offsets such as `regDAGB1_*` and `regDAGB2_*`.

## Purpose

`mmhub_1_8_0_sh_mask.h` is a generated hardware-register field map for the AMDGPU MMHUB 1.8.0 block. This chunk describes the per-field layout of DAGB1 and part of DAGB2, where DAGB means data arbitration group B in the MMHUB register namespace. These registers shape how MMHUB read and write clients are assigned to virtual channels, how bandwidth and outstanding-data limits are applied, how credits are distributed across TLB, storage, EA, GMI, OSD, and read-return paths, and how status/debug/performance information is exposed.

The header lets driver code use `REG_SET_FIELD`, `REG_GET_FIELD`, and direct mask operations with named fields instead of hard-coded bit arithmetic. For example, a caller can set `DAGB1_CNTL_MISC2__DISABLE_WRREQ_CG_MASK` or use fields from a `DAGB*_WRCLI_GPU_SNOOP_OVERRIDE` register while the offset header identifies the actual MMIO register number.

## Important APIs, Types, And Data

The exported API is the macro namespace. Major groups in this chunk are:

- `DAGB1_RD_VC4_CNTL` tail plus complete `DAGB1_RD_VC5_CNTL`, `DAGB1_RD_VC6_CNTL`, and `DAGB1_RD_VC7_CNTL`: read virtual-channel credit, max/min bandwidth, OSD limiter, and max outstanding-data fields. The chunk boundary omits the first three `DAGB1_RD_VC4_CNTL` shifts, which are immediately above line 2367.
- `DAGB1_RD_CNTL_MISC`, `DAGB1_RD_TLB_CREDIT`, `DAGB1_RD_RDRET_CREDIT_CNTL`, and `DAGB1_RD_RDRET_CREDIT_CNTL2`: read-side shared pool, EA, IO, TLB, read-return FIFO, VC-mode, and equality-fix credit controls.
- `DAGB1_RDCLI_*_PENDING`, `DAGB1_RDCLI_NOALLOC_OVERRIDE`, and `DAGB1_RDCLI_NOALLOC_OVERRIDE_VALUE`: busy/status bitmaps and no-allocation override controls for read clients.
- `DAGB1_WRCLI0` through `DAGB1_WRCLI15`: per-write-client virtual-channel assignment and throttling fields. Each client has `VIRT_CHAN`, `CHECK_TLB_CREDIT`, `URG_HIGH`, `URG_LOW`, `MAX_BW_ENABLE`, `MAX_BW`, `MIN_BW_ENABLE`, `MIN_BW`, `OSD_LIMITER_ENABLE`, and `MAX_OSD` masks.
- `DAGB1_WR_CNTL`, `DAGB1_WR_GMI_CNTL`, `DAGB1_WR_ADDR_DAGB`, and `DAGB1_WR_DATA_DAGB`: global write-side clock/window, IO-level, GMI, address-DAGB, data-DAGB, jump-ahead, self-init, `WHOAMI`, and jump-mode fields.
- `DAGB1_WR_OUTPUT_DAGB_*`, `DAGB1_WR_ADDR_DAGB_*`, and `DAGB1_WR_DATA_DAGB_*`: 4-bit per-VC or per-client max-burst and lazy-timer fields. The `*_0` registers cover clients 0-7 and `*_1` registers cover clients 8-15.
- `DAGB1_WR_VC0_CNTL` through `DAGB1_WR_VC7_CNTL`, `DAGB1_WR_CNTL_MISC`, `DAGB1_WR_TLB_CREDIT`, `DAGB1_WR_DATA_CREDIT`, `DAGB1_WR_MISC_CREDIT`, `DAGB1_WR_OSD_CREDIT_CNTL1/2`, and `DAGB1_WR_ATOMIC_FIFO_CREDIT_CNTL1`: write-side virtual-channel credit, bandwidth, OSD, TLB, GMI, pool, data FIFO, miscellaneous, atomic, and return-credit fields.
- `DAGB1_WRCLI_GPU_SNOOP_OVERRIDE` and `_VALUE`: bitmaps controlling per-write-client GPU snoop override enable/value behavior. In `mmhub_v1_8.c`, SDMA is treated as bit 15 in these registers.
- `DAGB1_WRCLI_*_PENDING` and `DAGB1_WRCLI_DBUS_*_PENDING`: write-client busy/status bitmaps for ask/go/global-send/TLB/OARB/OSD/DBUS stages.
- `DAGB1_DAGB_DLY`, `DAGB1_CNTL_MISC`, and `DAGB1_CNTL_MISC2`: delay, disable, disable-self-init, reset, interrupt, and clock-gating controls. `DAGB1_CNTL_MISC2` includes fine-grained clock-gating disable bits for write request/return, read request/return, TLB write/read, and tap-chain clock gating.
- `DAGB1_FATAL_ERROR_CNTL`, `_CLEAR`, and `_STATUS0..3`: fatal-error enable, clear, and status fields for read requests/responses, write requests/responses, TLB, credits, OSD, DAGB state machines, and DBUS conditions.
- `DAGB1_FIFO_EMPTY`, `DAGB1_FIFO_FULL`, `DAGB1_WR_CREDITS_FULL`, and `DAGB1_RD_CREDITS_FULL`: status bitmaps for request, data, read-return, TLB, OSD, DBUS, and credit FIFOs.
- `DAGB1_PERFCOUNTER_LO/HI`, `DAGB1_PERFCOUNTER0_CFG`, `DAGB1_PERFCOUNTER1_CFG`, `DAGB1_PERFCOUNTER2_CFG`, and `DAGB1_PERFCOUNTER_RSLT_CNTL`: local performance counter result, selector, enable, clear, and latency-measurement fields.
- `DAGB1_L1TLB_REG_RW`: register-read/write pass-through controls for L1 TLB access, with `REGISTER_INDEX`, `REGISTER_WR_DATA`, `REGISTER_RD_DATA`, `REGISTER_RW_SEL`, `REGISTER_ACCESS`, and `REGISTER_STATUS` fields.
- `DAGB2_RDCLI0..15`, `DAGB2_RD_*`, `DAGB2_WRCLI0..15`, and early `DAGB2_WR_*` groups: the same generated field pattern for the next DAGB instance, starting at the `aid_mmhub_dagb_dagbdec2` address block. This chunk reaches through `DAGB2_WR_ADDR_DAGB_LAZY_TIMER0__CLIENT1_MASK`.

The field layouts are highly regular. Per-client write/read client controls use low bits for VC selection and credit checks, mid bits for urgency and bandwidth controls, and high bits for OSD limits. Per-VC credit registers use repeated 4-bit, 5-bit, or 6-bit fields. Busy, override, FIFO, full, and error registers commonly expose 16-bit or 32-bit bitmaps.

## Control Flow

This header has no runtime control flow. It participates in runtime behavior when a C file includes the mask header and writes or reads MMHUB registers with SOC15 helpers:

1. `amdgpu/mmhub_v1_8.c` includes both `mmhub_1_8_0_offset.h` and this shift/mask header.
2. Initialization calls `mmhub_v1_8_init_snoop_override_regs()` during `mmhub_v1_8_gart_enable()`.
3. That function computes the register-distance between `regDAGB1_WRCLI_GPU_SNOOP_OVERRIDE` and `regDAGB0_WRCLI_GPU_SNOOP_OVERRIDE`, then loops over five DAGB instances by applying the same distance from DAGB0.
4. For each MMHUB instance in `adev->aid_mask`, the driver reads `regDAGB0_WRCLI_GPU_SNOOP_OVERRIDE` and `regDAGB0_WRCLI_GPU_SNOOP_OVERRIDE_VALUE`, sets bit 15 for SDMA, and writes the values back. The named field masks in this chunk define the DAGB1 layout corresponding to that repeated hardware pattern.
5. Other fields in this chunk are available to debug, RAS, clock-gating, performance, firmware, or future initialization paths even when current `mmhub_v1_8.c` only directly references the snoop override register offsets from this range.

The chunk also aligns with older and newer MMHUB implementations that manipulate DAGB fields, especially `DAGB1_CNTL_MISC2` clock-gating masks in `mmhub_v1_7.c`, `mmhub_v3_0.c`, `mmhub_v4_1_0.c`, and `mmhub_v4_2_0.c`. That reuse pattern is important because generated register families tend to preserve names while offsets and exact field availability vary by IP version.

## State And Persistence Behavior

The macros are compile-time constants and persist no software state. The hardware registers they describe are stateful MMIO registers whose contents persist until reset, suspend/resume restoration, GPU reset, firmware programming, or another driver write changes them.

Important state classes described by this chunk include:

- Per-client routing state: `RDCLI*` and `WRCLI*` fields assign clients to virtual channels and configure urgency, credit checks, bandwidth limits, and OSD limits.
- Credit and arbitration state: `*_CREDIT`, `*_CNTL`, `*_MAX_BURST*`, and `*_LAZY_TIMER*` fields tune request admission and return-resource allocation. Bad values can persistently starve clients or overcommit FIFOs.
- Snoop override state: `WRCLI_GPU_SNOOP_OVERRIDE` and `_VALUE` hold per-client policy bits. `mmhub_v1_8_init_snoop_override_regs()` sets SDMA snoop override during GART enable for non-SR-IOV-VF devices.
- Clock/power-gating state: `*_CGTT_CLK_CTRL`, `DAGB1_CNTL_MISC`, and `DAGB1_CNTL_MISC2` fields can force or disable clock-gating behavior. These affect power and availability rather than normal kernel memory.
- Diagnostic state: pending, FIFO empty/full, credits-full, fatal-error status, and performance-counter registers expose live hardware state. Clear and control fields such as `DAGB1_FATAL_ERROR_CLEAR` and `DAGB1_PERFCOUNTER_RSLT_CNTL__PERFCOUNTER_CLEAR_MASK` can modify diagnostic state.
- L1 TLB indirect access state: `DAGB1_L1TLB_REG_RW` holds an index, write data, read data, access select, access trigger, and status for low-level TLB register access.

There is no disk state, allocation, reference counting, locking, or software-owned lifetime in the header. Ordering, concurrency, reset sequencing, and SR-IOV policy are imposed by the AMDGPU MMHUB/GMC callers and by firmware.

## Dependencies

This chunk depends on the generated MMHUB 1.8.0 register specification and must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_8_0_offset.h`, which defines the corresponding `regDAGB1_*` and `regDAGB2_*` register offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v1_8.c`, the local MMHUB 1.8 consumer that includes this file and programs DAGB snoop override state.
- SOC15 register helpers and field helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_SOC15_OFFSET`, `WREG32_SOC15_OFFSET`, `SOC15_REG_OFFSET`, `REG_SET_FIELD`, and `REG_GET_FIELD`.
- AMDGPU runtime state used by the consumer path: `struct amdgpu_device`, `adev->aid_mask`, `for_each_inst()`, SR-IOV checks such as `amdgpu_sriov_vf()`, GMC/GART enable sequencing, and PSP-mediated programming for other MMHUB registers.
- Related generated MMHUB versions where similar DAGB field names are consumed by clock-gating code. Cross-version copy/paste is common in AMDGPU register programming, so field-name drift between versions is a practical dependency.

The macros use the conventional generated naming form `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`. Callers rely on exact spelling for `REG_SET_FIELD` expansion and on exact mask/shift values for direct bit operations.

## Integration Points

- `mmhub_v1_8_init_snoop_override_regs()` programs the write-client GPU snoop override/value register family. Although it starts from DAGB0 offsets, it uses the DAGB instance spacing to reach DAGB1 and later DAGBs; the `DAGB1_WRCLI_GPU_SNOOP_OVERRIDE*` field definitions in this chunk document the bit layout for one of those repeated instances.
- `mmhub_v1_8_gart_enable()` invokes snoop override setup after GART aperture, system aperture, TLB, and cache setup, and before system-domain, identity-aperture, VMID, and invalidation programming.
- `amdgpu_sriov_vf(adev)` gates snoop override setup out for SR-IOV VFs. That matters because these registers affect client-level routing and coherency policy and may be PF/host-owned in virtualized environments.
- Clock-gating integration is visible by analogy with other MMHUB versions that use `DAGB1_CNTL_MISC2` masks to enable or disable DAGB request/return and TLB clock gating. The MMHUB 1.8 `set_clockgating` hook is currently a stub, but the generated masks in this chunk are the register interface it would use if implemented.
- Debug and bring-up tools can use the pending, FIFO, fatal-error, perf-counter, and L1TLB pass-through fields to inspect hardware state or clear latched conditions. These are not surfaced as normal userspace APIs in this header, but they are part of the driver-visible register contract.
- DAGB2 groups in this chunk integrate with the same repeated-register model as DAGB1. The offset header places `regDAGB2_*` after DAGB1, and code can compute instance-relative distances when the hardware layout is regular.

## Risks

- Generated-field drift is the central risk. A wrong shift or mask compiles cleanly but causes the driver to modify the wrong bits in MMHUB hardware.
- The chunk boundaries split register groups. `DAGB1_RD_VC4_CNTL` is incomplete at the start, and `DAGB2_WR_ADDR_DAGB_LAZY_TIMER0` is incomplete at the end. Merge/reconciliation should avoid treating either group as fully documented by this chunk alone.
- Per-client and per-VC fields are highly repetitive. A single off-by-one client index, virtual-channel index, or DAGB instance distance can apply bandwidth, snoop, credit, or lazy-timer settings to the wrong client.
- Snoop override bits affect coherency. The current MMHUB 1.8 path explicitly sets SDMA bit 15 so SDMA writes probe/invalidate read-write lines; losing or misplacing that bit can create subtle stale-cache behavior.
- Credit, bandwidth, max outstanding-data, max-burst, and lazy-timer fields affect arbitration fairness and progress. Bad values can starve display/media/SDMA clients, overrun FIFOs, or cause hangs that look like unrelated VM faults.
- Clock-gating override and disable fields can break low-power behavior or, if toggled without sequencing, stall a live hardware block.
- Fatal-error clear/status fields are stateful diagnostics. Clearing too broadly can erase evidence needed by RAS or postmortem handling; enabling too broadly can convert recoverable conditions into fatal flows.
- L1 TLB indirect register access fields are low-level debug/programming controls. Incorrect index, access select, or trigger values can touch internal TLB state outside normal MMHUB setup paths.
- SR-IOV ownership matters. PF, VF, PSP, or firmware may own subsets of DAGB and TLB controls, so direct writes in VF mode can be blocked, ignored, or unsafe.

## Test Signals

- Build coverage: compile AMDGPU with MMHUB 1.8 support. Because this is a generated macro header, missing or renamed fields primarily surface as compile failures in `mmhub_v1_8.c` or related consumers.
- Register-write trace coverage: during `mmhub_v1_8_gart_enable()`, confirm non-SR-IOV paths read and write the DAGB write-client GPU snoop override and value registers for each enabled AID/MMHUB instance, and confirm SR-IOV VF paths skip those writes.
- Functional coherency signal: SDMA write workloads that interact with GPU-cached read/write lines should not exhibit stale data after the SDMA snoop override bit is programmed.
- VM/GART regression signal: MMHUB GART enable/disable, VMID setup, invalidation, and fault-default tests should remain stable after any change to this generated field file, even if the touched fields are not directly in the high-level VM aperture path.
- Debug/RAS signal: fatal-error status/clear, FIFO empty/full, credits-full, pending, and perf-counter reads should decode consistently with hardware documentation and should not show impossible bit combinations after idle or stress runs.
- Power-management signal: if clock-gating support is added for MMHUB 1.8 using `DAGB1_CNTL_MISC2` or `*_CGTT_CLK_CTRL` fields, validate suspend/resume, runtime clock-gating flags, and stress workloads under both enabled and disabled clock-gating states.

### subset-b-002776: lines 4720-7085

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_8_0_sh_mask.h lines 4720-7085

## Scope

This chunk covers the middle of the generated MMHUB 1.8.0 shift/mask header for AMD GPU register programming. The range starts inside the `aid_mmhub_dagb_dagbdec2` address block, completes the later write-side `DAGB2_*` field definitions, covers almost the entire `aid_mmhub_dagb_dagbdec3` block, and begins the `aid_mmhub_dagb_dagbdec4` block through `DAGB4_RDCLI2` field definitions.

The source is a register-description header, not executable C. It defines preprocessor constants of the form `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`. These constants describe bit positions and bit masks for MMHUB DAGB registers; companion register addresses live in `mmhub_1_8_0_offset.h`, and the values are consumed by AMDGPU register access helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15*`, and `WREG32_SOC15*`.

## Purpose

The purpose of this chunk is to give the driver exact symbolic names for programming and decoding MMHUB DAGB arbitration, credit, virtual-channel, clock-gating, fatal-error, FIFO-status, performance-counter, and L1 TLB control registers on the MMHUB 1.8.0 IP block. The DAGB blocks appear as repeated hardware decoder instances. This chunk completes instance 2, defines instance 3 in detail, and starts instance 4.

The mask/shift pairs keep register manipulation centralized and mechanically checkable. Driver code can compose a register value with named fields instead of hard-coding bit positions. Diagnostic code can also decode hardware status registers, especially fatal-error and counter registers, using the same definitions.

## Important APIs, Types, And Macro Families

There are no functions, structs, enums, or callable APIs in this range. The important interface is the macro namespace exported by the header.

`DAGB2_WR_*` macros at the start of the chunk complete the write path for DAGB instance 2. The range includes write address/data DAGB burst and lazy-timer fields, write data DAGB control fields, write virtual-channel controls `DAGB2_WR_VC0_CNTL` through `DAGB2_WR_VC7_CNTL`, write miscellaneous credit controls, pending-bit status registers, GPU snoop override masks, DAGB delay/misc controls, fatal-error controls/status, FIFO/credit-full status, performance counters, and `DAGB2_L1TLB_REG_RW`.

`DAGB3_RDCLI0` through `DAGB3_RDCLI15` define the repeated read-client configuration layout for DAGB instance 3. Each client has fields for virtual channel selection, TLB credit checking, high/low urgency thresholds, maximum and minimum bandwidth controls, OSD limiter enable, and maximum outstanding depth. The same layout later appears for `DAGB3_WRCLI0` through `DAGB3_WRCLI15` on the write side and begins again for `DAGB4_RDCLI0` through the visible portion of `DAGB4_RDCLI2`.

`DAGB3_RD_CNTL`, `DAGB3_WR_CNTL`, `DAGB3_RD_GMI_CNTL`, and `DAGB3_WR_GMI_CNTL` describe global read/write arbitration windows, SCLK frequency encoding, IO-level override, shared virtual-channel selection, fixed jump behavior, EA credits, GMI level, maximum burst size, and lazy timers.

`DAGB3_RD_ADDR_DAGB`, `DAGB3_WR_ADDR_DAGB`, and `DAGB3_WR_DATA_DAGB` describe DAGB enable and policy fields, including `DAGB_ENABLE`, `ENABLE_JUMP_AHEAD`, `DISABLE_SELF_INIT`, `WHOAMI`, and read/write address `JUMP_MODE`. Per-client maximum burst and lazy-timer registers split clients 0-7 and 8-15 into separate 32-bit registers with 4-bit lanes.

`DAGB3_RD_OUTPUT_DAGB_MAX_BURST`, `DAGB3_RD_OUTPUT_DAGB_LAZY_TIMER`, `DAGB3_WR_OUTPUT_DAGB_MAX_BURST`, and `DAGB3_WR_OUTPUT_DAGB_LAZY_TIMER` use 4-bit lanes for virtual channels 0-7. These fields tune output burst lengths and timer behavior per virtual channel.

`DAGB3_RD_CGTT_CLK_CTRL`, `DAGB3_WR_CGTT_CLK_CTRL`, `DAGB3_L1TLB_RD_CGTT_CLK_CTRL`, `DAGB3_L1TLB_WR_CGTT_CLK_CTRL`, `DAGB3_ATCVM_RD_CGTT_CLK_CTRL`, and `DAGB3_ATCVM_WR_CGTT_CLK_CTRL` expose clock-gating/timing controls: on delay, off hysteresis, light-sleep assert hysteresis, light-sleep override, and soft override.

`DAGB3_RD_VC0_CNTL` through `DAGB3_RD_VC7_CNTL` and `DAGB3_WR_VC0_CNTL` through `DAGB3_WR_VC7_CNTL` define virtual-channel credit and bandwidth controls. The shared layout includes storage credit, EA credit, max bandwidth enable/value, min bandwidth enable/value, OSD limiter enable, and max OSD.

`DAGB3_RD_TLB_CREDIT`, `DAGB3_RD_RDRET_CREDIT_CNTL`, `DAGB3_WR_TLB_CREDIT`, `DAGB3_WR_DATA_CREDIT`, `DAGB3_WR_MISC_CREDIT`, `DAGB3_WR_OSD_CREDIT_CNTL1`, `DAGB3_WR_OSD_CREDIT_CNTL2`, and `DAGB3_WR_ATOMIC_FIFO_CREDIT_CNTL1` define TLB, read-return, data, atomic, OSD, and miscellaneous credit fields used to bound request flow through the DAGB pipelines.

`DAGB3_RDCLI_*_PENDING` and `DAGB3_WRCLI_*_PENDING` macros decode per-client pending bitmaps for ask/go/global-send/TLB/OARB/OSD stages and, on the write side, DBUS ask/go stages. These are status fields, not configuration fields.

`DAGB3_WRCLI_GPU_SNOOP_OVERRIDE` and `DAGB3_WRCLI_GPU_SNOOP_OVERRIDE_VALUE` expose 16-bit masks that let software override GPU snoop behavior per write client. `mmhub_v1_8.c` has a concrete integration point for the same register family: `mmhub_v1_8_init_snoop_override_regs()` computes the distance between DAGB instances and sets SDMA client bit 15 in the DAGB write-client snoop override registers across the available DAGB instances.

`DAGB3_CNTL_MISC` and `DAGB3_CNTL_MISC2` cover cross-cutting DAGB controls, including EA virtual-channel remapping, bandwidth initialization/gap cycles, urgency boost/halt controls, clock-gating disable bits, EA busy disables, swap control, RDRET FIFO performance control, HDP client ID, and RDRET FIFO deadlock credits.

`DAGB3_FATAL_ERROR_CNTL`, `DAGB3_FATAL_ERROR_CLEAR`, and `DAGB3_FATAL_ERROR_STATUS0` through `DAGB3_FATAL_ERROR_STATUS3` define fatal-error filtering, clearing, and captured error fields. The status registers expose validity, client ID, low/high address bits, transaction tag, VFID/VF, address space, IO, size, debug mask, FED, allocation state, unit ID, operation, security level, TMZ read/write bits, snoop, invalid, NACK, read-only, memory-log, and end-of-packet state.

`DAGB3_FIFO_EMPTY`, `DAGB3_FIFO_FULL`, `DAGB3_WR_CREDITS_FULL`, and `DAGB3_RD_CREDITS_FULL` are status bitmap definitions for FIFO and credit saturation. `DAGB3_PERFCOUNTER_LO`, `DAGB3_PERFCOUNTER_HI`, `DAGB3_PERFCOUNTER0_CFG`, `DAGB3_PERFCOUNTER1_CFG`, `DAGB3_PERFCOUNTER2_CFG`, and `DAGB3_PERFCOUNTER_RSLT_CNTL` describe a small performance-counter block with select ranges, mode, enable, clear, start/stop triggers, enable-any, clear-all, and stop-on-saturate fields.

`DAGB3_L1TLB_REG_RW` describes indirect L1 TLB control access bits: write/read control strobes, VMID exception interrupt control, write-data parity checking, read-return check disable, and a reserved high-bit mask.

## Control Flow

This header chunk has no local control flow. It does not branch, call functions, allocate memory, or update state by itself. Control flow is introduced only when driver code includes the header and uses these macros in register programming or status decode paths.

The typical downstream flow is:

1. Include `mmhub_1_8_0_offset.h` for register addresses and `mmhub_1_8_0_sh_mask.h` for field positions.
2. Read a 32-bit MMHUB register with `RREG32_SOC15`, `RREG32_SOC15_OFFSET`, or a related access helper.
3. Modify one or more fields with `REG_SET_FIELD` or decode them with `REG_GET_FIELD`, using the masks and shifts in this header.
4. Write the updated value back with `WREG32_SOC15` or `WREG32_SOC15_OFFSET`.

The visible `mmhub_v1_8.c` integration follows that pattern for DAGB snoop override registers. It uses offset-header symbols to address repeated DAGB instances and writes the SDMA client override bit. The masks in this chunk make equivalent field-aware writes possible for DAGB2, DAGB3, and DAGB4 fields even when this particular C file does not reference every field directly.

## State And Persistence Behavior

The macros themselves have no runtime state and no persistence. They are compile-time constants.

The hardware state represented by this chunk is persistent MMIO register state inside the GPU's MMHUB while the device is powered and configured. Writes to the corresponding registers can affect request arbitration, read/write client routing, virtual-channel credit accounting, clock-gating behavior, snoop behavior, fatal-error latching, performance-counter selection, and L1 TLB control. Reads from status registers expose transient pipeline state such as pending bits, FIFO empty/full status, credit-full status, fatal-error captures, and performance-counter values.

Driver-level persistence depends on how the consuming code applies these fields during device initialization, reset, suspend/resume, SR-IOV mode transitions, RAS handling, and debug collection. The header does not save or restore register values; callers must decide when to reprogram them.

## Dependencies And Integration Points

This chunk depends on `mmhub_1_8_0_offset.h` for the matching `regDAGB*` register address definitions. For example, the companion offset file maps `regDAGB3_RDCLI0` at `0x0180`, `regDAGB3_WR_VC0_CNTL` at `0x01d1`, `regDAGB3_L1TLB_REG_RW` at `0x01ff`, and `regDAGB4_RDCLI0` at `0x0200`. The masks here are only meaningful when paired with those addresses.

The primary C integration point for this header is `drivers/gpu/drm/amd/amdgpu/mmhub_v1_8.c`, which includes both the offset and shift/mask headers. That file initializes MMHUB VM page-table registers, aperture registers, TLB controls, and DAGB write-client snoop overrides for all active AID/MMHUB instances. Other AMDGPU infrastructure provides the register access macros, the `REG_SET_FIELD` and `REG_GET_FIELD` helpers, and SOC15 instance addressing.

The definitions are also structurally aligned with neighboring ASIC/IP headers such as `mmhub_1_7_sh_mask.h` and `mmhub_9_4_1_sh_mask.h`. That alignment matters because AMDGPU code often carries similar initialization patterns across IP versions while selecting different offset/mask headers for each hardware generation.

## Risks And Edge Cases

Because this is generated hardware-interface data, the main risk is register-layout drift. A wrong shift or mask can corrupt unrelated bits in the same 32-bit register, which is especially risky for credit, clock-gating, TLB, and fatal-error control registers.

The chunk boundary begins in the middle of a DAGB2 register family and ends in the middle of `DAGB4_RDCLI2`. A final merged per-file analysis must reconcile adjacent chunks before drawing conclusions about complete DAGB2 and DAGB4 coverage.

Many fields are repeated across clients, virtual channels, and DAGB instances. Copy-generation mistakes are easy to miss visually: a single instance number, client number, mask width, or shift nibble could be wrong while the surrounding pattern still looks valid.

Several registers expose status or clear semantics rather than ordinary read/write configuration. For example, fatal-error clear, pending-bit, FIFO-full, and performance-counter clear fields should not be treated as stable configuration fields. Calling code must preserve hardware-defined write-one-to-clear or latch behavior from the register spec.

The `DAGB*_L1TLB_REG_RW` fields include read/write control strobes and a broad reserved mask. Software should avoid writing reserved bits unless the hardware programming guide explicitly requires a value.

Virtualization and partitioning are relevant. Fatal-error status includes VFID/VF fields, while `mmhub_v1_8.c` skips some programming in SR-IOV VF mode. Code using these masks must respect PF/VF ownership of MMHUB registers.

## Test Signals

Build-time coverage should include compiling AMDGPU with `mmhub_v1_8.c` so the generated header, include guard, and macro names remain valid with the offset header and common SOC15 register helpers.

Static validation should compare this header against the authoritative register database or against adjacent generated headers for the same IP family. High-signal checks include verifying that each `*_MASK` width matches its corresponding `*_SHIFT`, that client/VC lane masks advance by the expected 4-bit or 5-bit increments, and that DAGB3 offsets in `mmhub_1_8_0_offset.h` line up with the DAGB3 mask block in this file.

Runtime validation should focus on consumers rather than this header alone. For snoop override programming, read back `DAGB*_WRCLI_GPU_SNOOP_OVERRIDE` and `DAGB*_WRCLI_GPU_SNOOP_OVERRIDE_VALUE` after `mmhub_v1_8_init_snoop_override_regs()` and verify that SDMA client bit 15 is set only when the driver is allowed to program those registers.

Hardware/debug tests can exercise fatal-error capture and decode using `DAGB*_FATAL_ERROR_STATUS*` fields, performance-counter programming through the `DAGB*_PERFCOUNTER*_CFG` and result-control masks, and FIFO/credit/pending status collection under load.

Regression signals should include suspend/resume and GPU reset paths, because MMHUB register programming often needs to be restored after power or reset events. SR-IOV PF and VF tests are also important because some registers are not safe for guest-side programming.

### subset-b-002777: lines 7086-9431

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_8_0_sh_mask.h lines 7086-9431

## Purpose

This chunk is a generated-style register bitfield contract for AMD MMHUB 1.8.0 hardware. It contains preprocessor constants only: each hardware field is exposed as a `*_MASK` and/or `*__SHIFT` macro that downstream AMDGPU code can combine with the matching register offsets from `mmhub_1_8_0_offset.h`.

The selected range covers the tail of the `DAGB4_RDCLI2` field set, the bulk of the `DAGB4` read/write data-address generation block, and the start of the `aid_mmhub_ea_mmeadec0` MMEA decoder register fields through `MMEA0_GMI_WR_PRI_AGE`. These definitions describe how MMHUB clients are assigned to virtual channels, throttled, credited, monitored, mapped into groups, and prioritized for DRAM/GMI traffic. The file does not implement policy itself; it gives the driver the bit positions needed to program or inspect that policy.

## Major Register Families Covered

- `DAGB4_RDCLI2` through `DAGB4_RDCLI15`: per-read-client fields for virtual channel selection, TLB credit checking, high/low urgency thresholds, max/min bandwidth limiting, OSD limiter enablement, and maximum outstanding depth.
- `DAGB4_RD_CNTL`, `DAGB4_RD_GMI_CNTL`, and `DAGB4_RD_ADDR_DAGB`: shared read-side controls for SCLK/window sizing, IO level override/selection, shared virtual-channel count, GMI EA credit/level/burst/lazy timing, address DAGB enablement, jump-ahead mode, self-init control, and `WHOAMI` identity fields.
- `DAGB4_RD_OUTPUT_DAGB_*`, `DAGB4_RD_ADDR_DAGB_*`, and `DAGB4_RD_VC0_CNTL` through `DAGB4_RD_VC7_CNTL`: read-side per-VC burst limits, lazy timers, reset values, increment/idle decays, timeout behavior, VC enablement, weights, channel thresholds, credit counters, and refill credits.
- `DAGB4_RD_CGTT_CLK_CTRL`, `DAGB4_L1TLB_RD_CGTT_CLK_CTRL`, and `DAGB4_ATCVM_RD_CGTT_CLK_CTRL`: clock-gating and soft-override fields for the read DAGB, L1 TLB read path, and ATCVM read path.
- `DAGB4_RD_CNTL_MISC`, `DAGB4_RD_TLB_CREDIT`, `DAGB4_RD_RDRET_CREDIT_CNTL`, and `DAGB4_RD_RDRET_CREDIT_CNTL2`: read-path stall gating, credit-reset behavior, TLB credit values, return credit per virtual channel, and combined VC4-VC7 return credit fields.
- `DAGB4_RDCLI_*_PENDING`: compact status bitmaps showing read client pending state at ASK, GO, global-send, TLB, OARB, and OSD stages.
- `DAGB4_WRCLI0` through `DAGB4_WRCLI15`: write-client mirrors of the per-client channel, TLB-credit, urgency, bandwidth, OSD limiter, and max-outstanding fields.
- `DAGB4_WR_CNTL`, `DAGB4_WR_GMI_CNTL`, `DAGB4_WR_ADDR_DAGB`, `DAGB4_WR_DATA_DAGB`, `DAGB4_WR_ADDR_DAGB_*`, `DAGB4_WR_DATA_DAGB_*`, and `DAGB4_WR_VC0_CNTL` through `DAGB4_WR_VC7_CNTL`: write-side shared control, address/data DAGB enablement, per-VC burst/lazy-timer configuration, and virtual-channel credit/refill/threshold behavior.
- `DAGB4_WR_CGTT_CLK_CTRL`, `DAGB4_L1TLB_WR_CGTT_CLK_CTRL`, and `DAGB4_ATCVM_WR_CGTT_CLK_CTRL`: write-side clock-gating control fields.
- `DAGB4_WR_CNTL_MISC`, `DAGB4_WR_TLB_CREDIT`, `DAGB4_WR_DATA_CREDIT`, `DAGB4_WR_MISC_CREDIT`, `DAGB4_WR_OSD_CREDIT_CNTL*`, and `DAGB4_WR_ATOMIC_FIFO_CREDIT_CNTL1`: write-path stall, reset, TLB/data/misc/OSD/atomic FIFO credit configuration, including several per-VC or per-group credit fields.
- `DAGB4_WRCLI_GPU_SNOOP_OVERRIDE*` and `DAGB4_WRCLI_*_PENDING`: write-client snoop override controls and pending-state bitmaps for ASK, GO, global-send, TLB, OARB, OSD, DBUS ASK, and DBUS GO stages.
- `DAGB4_DAGB_DLY`, `DAGB4_CNTL_MISC`, and `DAGB4_CNTL_MISC2`: delay tuning, request counter enables/limits, page-size match fields, return/output allocation knobs, bypass behavior, credit expansion, VC stall disabling, self-init gating, arbitration override, and assorted debugger/disable flags.
- `DAGB4_FATAL_ERROR_*`: fatal error enable/clear/status fields for read and write timeout conditions, missing TC/GC/SDMA data, DBUS-missing conditions, unexpected read return, ATCVM invalidation-vs-request hazards, invalidation FIFO request handling, and client IDs associated with read, write, DBUS, and FIFO error sources.
- `DAGB4_FIFO_EMPTY`, `DAGB4_FIFO_FULL`, `DAGB4_WR_CREDITS_FULL`, and `DAGB4_RD_CREDITS_FULL`: FIFO and credit saturation status bitmaps.
- `DAGB4_PERFCOUNTER_*`: low/high counter values, compare values, event selectors, performance modes, enable/clear fields, result selection, start/stop triggers, global enable/clear, and saturate-stop behavior.
- `DAGB4_L1TLB_REG_RW`: L1 TLB debug/register access command fields, including valid/write control, 7-bit address, 8-bit write data, and 8-bit read data.
- `MMEA0_DRAM_*` and `MMEA0_GMI_*`: memory decoder arbitration maps. The DRAM and GMI families map client IDs 0-31 to four groups, map groups to virtual channels, configure lazy request accumulation, CAM depth and reorder limits, page burst thresholds, priority aging, priority queueing/fixed/urgency behavior, and priority quantum values. The chunk ends after the `MMEA0_GMI_WR_PRI_AGE` masks.

## Important APIs, Types, and Functions

This header range declares no C functions, structs, enums, variables, or callable APIs. Its public interface is the generated macro namespace:

- `*_MASK` values isolate fields inside 32-bit MMHUB registers.
- `*__SHIFT` values define how callers pack field values into those masks or unpack field values from a register read.
- The corresponding register address symbols live in the companion offset header and are consumed by AMDGPU register helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, and field-update helpers/macros used elsewhere in the driver.

The direct integration point for this generation is `amdgpu/mmhub_v1_8.c`, which includes both `mmhub/mmhub_1_8_0_offset.h` and this mask header. The hand-written MMHUB 1.8 code primarily programs VM, GART, invalidation, fault, clock/power, and RAS behavior; many of the detailed `DAGB4` and `MMEA0` masks in this chunk are hardware-contract data available for bring-up code, diagnostics, register dumps, or future tuning rather than necessarily referenced by name in current C logic.

## Control Flow

There is no runtime control flow in the chunk. Including the header makes constant definitions visible at compile time. Runtime control flow appears only in callers that use these constants while reading, modifying, or writing MMHUB registers.

The typical downstream register-update sequence is:

1. Select the MMHUB 1.8.0 register offset from `mmhub_1_8_0_offset.h`.
2. Read the current 32-bit register value when preserving unrelated fields.
3. Clear the target field with the matching `*_MASK`.
4. Shift the new value by the matching `*__SHIFT`.
5. Mask and OR the shifted value into the register image.
6. Write the final value to the correct MMHUB instance/register.

Status fields use the inverse pattern: read the register, apply the mask, shift the field down, and interpret the result as a bitmap or encoded value. Pending, FIFO, credit-full, fatal-error-status, and performance-counter fields in this chunk are examples of readback-oriented contracts.

## State and Persistence Behavior

The header has no mutable state and persists nothing by itself. The constants describe state stored in MMHUB hardware registers while the GPU is powered and initialized.

Several register families represent long-lived configuration state: client-to-VC routing, bandwidth limit enables and windows, urgency thresholds, maximum outstanding request depths, DAGB enablement, per-VC weights/thresholds/refill credits, lazy timers, request accumulation thresholds, CAM/reorder depths, priority aging coefficients, and priority quantum settings. These values affect memory-fabric scheduling and can persist until device reset, power gating, suspend/resume restore, or explicit reprogramming.

Other families describe transient or event state: pending-stage bitmaps, FIFO empty/full state, credit-full state, fatal-error status, performance-counter low/high values, compare fields, and TLB debug read data. Some fields have clear or reset semantics in hardware, such as fatal error clear bits, performance counter clear bits, and reset/self-init controls. This header does not encode whether a bit is read-only, write-only, write-one-to-clear, self-clearing, sticky, or reserved; callers must follow ASIC documentation and existing driver sequencing.

## Dependencies and Integration Points

- Depends only on C preprocessor inclusion; the include guard and macro spelling are the effective ABI.
- Must stay synchronized with `mmhub_1_8_0_offset.h`, because masks are only meaningful with the matching register offsets and MMHUB generation.
- Integrated by `amdgpu/mmhub_v1_8.c` for MMHUB 1.8 ASIC support, including multi-instance access through SOC15 register helpers and `adev->aid_mask`.
- Ties into AMDGPU GPUVM/GART setup, MMHUB invalidation, RAS/error reporting, register debugging, performance monitoring, and any firmware or bring-up code that inspects MMHUB arbitration state.
- Names reference hardware subblocks rather than Linux objects: `DAGB4` is a data/address generation/arbitration block, `RDCLI`/`WRCLI` are read/write clients, `VC` is virtual channel state, `L1TLB`/`ATCVM` are translation paths, `GMI` is the GPU memory interconnect side, and `MMEA0` is the memory decoder arbitration block for DRAM/GMI routing.

## Risks and Edge Cases

- A wrong mask or shift silently programs the wrong hardware bits. For this chunk, that can alter memory request routing, starvation prevention, outstanding-request limits, clock-gating behavior, credit accounting, or fatal-error handling.
- Repeated register layouts are easy to confuse. `RDCLI` and `WRCLI` fields are mostly parallel, as are DRAM and GMI arbitration maps, but a caller must still use the exact register-specific macro because small field-layout differences can exist across families or ASIC revisions.
- The chunk begins mid-family at `DAGB4_RDCLI2` and ends mid-MMEA priority area after `MMEA0_GMI_WR_PRI_AGE`; neighboring chunks are needed for the complete file-level picture.
- Encoded values are not self-describing. Fields such as urgency levels, aging coefficients, priority quantums, CAM depths, burst limits, and lazy timers need hardware documentation or known-good register tables to determine valid ranges and units.
- Status and control fields share the same macro style. Writing a status or reserved field as though it were a normal configuration field can clear diagnostics, trigger self-clearing behavior, or cause undefined hardware behavior.
- Multi-instance MMHUB support means correct masks are not enough; callers must also target the correct MMHUB/AID instance. A valid bitfield written to the wrong instance can leave another memory hub unconfigured.

## Test Signals

- Build coverage: misspelled or removed macros should fail consumers that include the MMHUB 1.8.0 headers.
- Register readback: after initialization or debug programming, read back `DAGB4_RD_CNTL`, `DAGB4_WR_CNTL`, DAGB per-VC controls, MMEA DRAM/GMI group maps, lazy timers, CAM controls, and priority registers to confirm values land in the expected fields.
- Hardware smoke coverage: GPUVM page-table setup, GART access, SDMA traffic, display/media traffic through MMHUB, peer or GMI traffic, suspend/resume, and GPU reset paths can expose incorrect arbitration, credit, or routing fields indirectly.
- Error diagnostics: `DAGB4_FATAL_ERROR_STATUS*`, pending bitmaps, FIFO full/empty fields, and credit-full registers are strong signals when a field definition or caller usage causes traffic to wedge.
- Performance diagnostics: `DAGB4_PERFCOUNTER_*` and MMEA priority/quantum fields can be used during bring-up to verify that traffic selection and throttling behave as expected.
- RAS/debug integration: MMHUB RAS query/reset paths in `mmhub_v1_8.c` and register dump tooling should continue to compile and report coherent MMHUB state when this generated header is present and synchronized with the hardware offsets.

### subset-b-002778: lines 9432-11750

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_8_0_sh_mask.h lines 9432-11750

## Scope

This chunk covers a large generated field-mask slice from the AMD MMHUB 1.8.0 register mask header. It starts mid-register at the tail of `MMEA0_GMI_WR_PRI_AGE`, covers the rest of the MMEA0 GMI/IO arbitration fields, the MMEA0 SDP, performance, error, DSM, clock-gating, and RAS status fields, then begins the `aid_mmhub_ea_mmeadec1` block for MMEA1 DRAM/GMI/IO arbitration. The final line is only the next register marker, `//MMEA1_IO_WR_CLI2GRP_MAP0`; its field definitions are outside this chunk.

The range contains 2,189 `#define` entries grouped under 128 register names with actual field definitions, plus comment delimiters. It has no C functions, structs, enums, storage objects, or executable statements. Its exported surface is a preprocessor namespace of `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` constants used with the matching `mmhub_1_8_0_offset.h` register-address constants and AMDGPU register helper macros.

## Purpose

`mmhub_1_8_0_sh_mask.h` gives symbolic bit positions and bit masks for MMHUB 1.8.0 hardware registers. This chunk describes fields for two MMHUB EA/MMEA decoder instances:

- `MMEA0` fields for GMI and IO request classification, arbitration, priority aging, urgency, quantization, SDP arbitration, performance counters, error reporting, error injection, clock-gating, and corrected/uncorrected error status.
- The start of `MMEA1` fields for DRAM and GMI request classification, virtual-channel mapping, lazy request accumulation, CAM depth/reorder control, page burst limits, priority policy, urgency masking, and the beginning of IO client-to-group mapping.

The header lets driver code set or inspect individual hardware fields without raw shifts and masks. Typical consumers combine a register value with `REG_SET_FIELD()` or `REG_GET_FIELD()`, then write/read the address from `mmhub_1_8_0_offset.h` with SOC15 MMIO helpers.

## Important APIs, Types, And Data

There are no normal C APIs or types. The important interface is the naming contract of generated macros:

- `*_CLI2GRP_MAP0/1__CIDn_GROUP__SHIFT` and `_MASK` map 32 client IDs to four arbitration groups, packed as 2-bit fields. This appears for MMEA0 IO and MMEA1 DRAM/GMI/IO read/write paths.
- `*_GRP2VC_MAP__GROUPn_VC__SHIFT` and `_MASK` map arbitration groups to virtual channels with 3-bit fields. This appears for MMEA1 DRAM and GMI paths in this chunk.
- `*_LAZY__GROUPn_DELAY`, `REQ_ACCUM_THRESH`, `REQ_ACCUM_TIMEOUT`, and `REQ_ACCUM_IDLEMAX` describe request coalescing/accumulation timing for MMEA1 DRAM/GMI read and write traffic.
- `*_CAM_CNTL__DEPTH_GROUPn`, `REORDER_LIMIT_GROUPn`, `REFILL_CHAIN`, and `PAGEBASED_CHAINING` define CAM sizing and chaining behavior for MMEA1 DRAM/GMI reorder control.
- `*_PAGE_BURST__RD_LIMIT_LO/HI` and `WR_LIMIT_LO/HI` define page burst windows for DRAM/GMI traffic.
- `*_PRI_AGE`, `*_PRI_QUEUING`, `*_PRI_FIXED`, `*_PRI_URGENCY`, `*_PRI_URGENCY_MASKING`, and `*_PRI_QUANT_PRI1/2/3` define the priority scheduler model: age rate/coefficient, queueing coefficient, fixed coefficient, urgency coefficient/mode, client urgency masks, and per-group priority thresholds.
- `MMEA0_SDP_ARB_DRAM`, `MMEA0_SDP_ARB_GMI`, and `MMEA0_SDP_ARB_FINAL` define burst limits, read/write switching policy, VC read-only controls, error-event/halt behavior, and burst stretching for the SDP arbitration stage.
- `MMEA0_SDP_*_PRIORITY`, `MMEA0_SDP_CREDITS`, `MMEA0_SDP_TAG_RESERVE*`, `MMEA0_SDP_VCC_RESERVE*`, `MMEA0_SDP_VCD_RESERVE*`, and `MMEA0_SDP_REQ_CNTL` tune SDP read/write group priority, credit accounting, tag/VC reserve sizes, and request control.
- `MMEA0_MISC` and `MMEA0_MISC2` define broader MMEA0 behavior such as group swaps, null request rate, flow control, request blocking, IO read/write priority enablement, and DRAM/GMI throttle bits.
- `MMEA0_LATENCY_SAMPLING`, `MMEA0_PERFCOUNTER_LO/HI`, `MMEA0_PERFCOUNTER0_CFG`, `MMEA0_PERFCOUNTER1_CFG`, and `MMEA0_PERFCOUNTER_RSLT_CNTL` expose latency/performance sampling, counter selection, reset, start/stop, and counter-bank selection fields.
- `MMEA0_UE_ERR_STATUS_LO/HI` and `MMEA0_CE_ERR_STATUS_LO/HI` define status-valid, address-valid, address, memory-ID, ECC, error-info, count, poison, and reserved fields used by RAS error collection.
- `MMEA0_DSM_CNTL`, `MMEA0_DSM_CNTLA`, and `MMEA0_DSM_CNTLB` define diagnostic single-write/irritator controls for DRAM, GMI, IO, return tag, page, and MAM memories.
- `MMEA0_DSM_CNTL2`, `MMEA0_DSM_CNTL2A`, and `MMEA0_DSM_CNTL2B` define error-injection enable/select-delay fields and a global `INJECT_DELAY`.
- `MMEA0_CGTT_CLK_CTRL` defines clock-gating transition delays and soft override bits for write, read, return, register, and light-sleep behavior.
- `MMEA0_EDC_MODE` and `MMEA0_ERR_STATUS` define EDC/FED/FUE behavior, fatal interrupt controls, status clearing, busy-on-error policy, and SDP response status fields.

The first few lines are only masks for `MMEA0_GMI_WR_PRI_AGE` because this chunk begins after that register group's shift definitions. The last line is a marker for `MMEA1_IO_WR_CLI2GRP_MAP0`; its fields are not included here.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by including C files:

1. `amdgpu/mmhub_v1_8.c` includes both `mmhub/mmhub_1_8_0_offset.h` and this `mmhub/mmhub_1_8_0_sh_mask.h` file.
2. Register addresses such as `regMMEA0_CE_ERR_STATUS_LO` come from the offset header; field extraction and updates use this mask header.
3. SOC15 helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, `REG_SET_FIELD`, `REG_GET_FIELD`, `AMDGPU_RAS_REG_ENTRY`, and `SOC15_REG_FIELD` provide the actual control flow that reads, writes, or describes the registers.
4. In `mmhub_v1_8.c`, the RAS tables use MMEA0 and MMEA1 CE/UE status register pairs. The RAS framework later reads those registers, checks validity flags, decodes memory IDs and error metadata, and reports corrected or uncorrected MMHUB errors.
5. Other arbitration, DSM, performance-counter, and clock-gating fields are generated ABI for firmware, diagnostics, or later driver paths even when the local `mmhub_v1_8.c` file does not actively program each field.

## State And Persistence Behavior

The macros themselves are compile-time constants and hold no state. The hardware registers they describe do hold persistent MMHUB state until reset or reprogramming:

- Client-to-group, group-to-VC, lazy accumulation, CAM, page-burst, priority, urgency, and quantization fields shape how MMEA instances schedule DRAM/GMI/IO memory traffic. Bad values can remain active across normal workloads until a GPU reset, suspend/resume restore, or explicit MMHUB reinitialization rewrites them.
- SDP arbitration, reserve, credit, and request-control fields affect downstream request dispatch and fairness for MMEA0 traffic.
- Performance-counter and latency-sampling fields select what hardware events are counted and whether counters run, reset, or dump accumulated values.
- CE/UE status registers persist hardware error observations, including valid flags, addresses, memory IDs, error-info fields, ECC/poison information, and count fields, until the relevant RAS clear/read flow or hardware reset changes them.
- DSM and error-injection fields can intentionally perturb or inject memory errors. These are diagnostic hardware state, not normal software allocations.
- Clock-gating and EDC mode fields influence low-power entry/exit and error propagation behavior for MMEA0.

No disk state, heap allocation, reference counting, locks, or software-owned object lifetime exists in the header. Ordering and synchronization belong to the driver paths that perform MMIO reads and writes.

## Dependencies

This chunk depends on the generated MMHUB 1.8.0 hardware register specification and must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_8_0_offset.h`, which supplies the matching `regMMEA*` register offsets and base indices.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v1_8.c`, the primary local MMHUB 1.8 consumer, including RAS register lists for `MMEA0` and `MMEA1`.
- AMDGPU SOC15 register helpers and field helpers: `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, `REG_SET_FIELD`, `REG_GET_FIELD`, `AMDGPU_RAS_REG_ENTRY`, and `SOC15_REG_FIELD`.
- The AMDGPU RAS framework, which interprets CE/UE status pairs and memory IDs using register metadata and validity flags.
- Hardware/firmware flows that program arbitration, urgency, DSM, error injection, clock-gating, performance counters, and SDP policy for MMHUB EA/MMEA blocks.

Because this is a generated ASIC header, dependency correctness is mostly about version alignment: MMHUB 1.8.0 field masks must be used with MMHUB 1.8.0 offsets and with driver code that targets the same IP version.

## Integration Points

- `mmhub_v1_8.c` includes this header directly, so all `MMEA*__FIELD_MASK` and `MMEA*__FIELD__SHIFT` definitions are available to the MMHUB 1.8 implementation.
- `mmhub_v1_8_ce_reg_list` references `regMMEA0_CE_ERR_STATUS_LO/HI` and `regMMEA1_CE_ERR_STATUS_LO/HI`; the field definitions in this chunk describe how those status words encode valid flags, address bits, memory IDs, ECC, error info, count, and poison state.
- `mmhub_v1_8_ue_reg_list` references `regMMEA0_UE_ERR_STATUS_LO/HI` and `regMMEA1_UE_ERR_STATUS_LO/HI`; this chunk includes the MMEA0 UE masks and starts the MMEA1 register families used by the same RAS block.
- `mmhub_v1_8_ras_memory_list` maps reported memory IDs to names such as `MMEA_WGMI_PAGEMEM`, `MMEA_RGMI_PAGEMEM`, `MMEA_WDRAM_PAGEMEM`, `MMEA_RDRAM_CMDMEM`, `MMEA_MAM_DMEM*`, `MMEA_WRET_TAGMEM`, and `MMEA_RRET_TAGMEM`. Those names align with the DSM/error-injection and CE/UE status fields in this mask slice.
- `mmhub_1_8_0_offset.h` places these register groups in the address space, for example MMEA0 error/DSM/clock fields around `regMMEA0_UE_ERR_STATUS_LO`, `regMMEA0_DSM_CNTL*`, `regMMEA0_CGTT_CLK_CTRL`, `regMMEA0_EDC_MODE`, `regMMEA0_ERR_STATUS`, `regMMEA0_CE_ERR_STATUS_LO/HI`, and MMEA1 DRAM/GMI/IO policy fields beginning at `regMMEA1_DRAM_RD_CLI2GRP_MAP0`.
- Diagnostic or bring-up tooling can use the performance-counter, latency-sampling, DSM, and error-injection fields to select internal MMEA events, inject failures, and verify RAS reporting paths.

## Risks

- Generated-header drift is the primary risk. A wrong shift or mask compiles cleanly but can cause driver code to read or write the wrong bits in a live MMHUB register.
- The chunk starts and ends on partial register boundaries. A reconciled final document must not treat `MMEA0_GMI_WR_PRI_AGE` or `MMEA1_IO_WR_CLI2GRP_MAP0` as fully covered by this chunk alone.
- Cross-generation copying is hazardous. MMEA/MMHUB names recur across MMHUB 1.0, 1.7, 1.8, 9.4, and related ASIC headers, but offsets, masks, and supported fields can differ.
- Arbitration and priority fields can alter memory fairness and latency. Incorrect client grouping, VC mapping, lazy thresholds, CAM depth, urgency masking, or priority coefficients can cause starvation, performance collapse, timeout behavior, or fabric backpressure.
- RAS status masks are safety-critical for observability. Mis-decoding valid flags, memory IDs, CE counts, poison bits, or error-info fields can hide real hardware faults or attribute them to the wrong MMHUB memory.
- DSM and error-injection fields are intentionally disruptive. Enabling them outside controlled diagnostics can create synthetic faults or corrupt normal validation signals.
- Clock-gating and EDC/FED/FUE policy bits interact with power and fault handling. Bad settings can cause stalls, missed fatal interrupts, spurious busy state, or failure to propagate fatal errors.
- Many fields are densely packed. Updating a field without preserving unrelated bits, or using a mask with the wrong register instance, can silently change neighboring fields.

## Test Signals

- Build AMDGPU with MMHUB 1.8 enabled so `mmhub_v1_8.c` compiles against `mmhub_1_8_0_offset.h` and this mask header.
- Generated-header validation should compare every shift/mask pair in this line range against the authoritative MMHUB 1.8.0 register database and verify that each field lies inside the expected 32-bit register.
- Static checks should ensure `REG_SET_FIELD`/`REG_GET_FIELD`, `SOC15_REG_FIELD`, and RAS register entries use field names that exist in this header and register names that exist in the matching offset header.
- Runtime RAS testing should inject or provoke corrected and uncorrected MMHUB errors, then verify CE/UE valid flags, memory IDs, addresses, error-info fields, poison flags, and counts decode correctly for MMEA0 and MMEA1.
- Stress testing should exercise DRAM, GMI, and IO traffic under GPUVM workloads, peer/XGMI traffic, and display/media access while monitoring for VM faults, fabric stalls, request timeouts, and RAS noise.
- Diagnostic validation should program performance counters and latency sampling to known event selections and confirm counter reset/start/stop/dump behavior.
- Power-management smoke should verify clock-gating transitions around MMHUB activity do not introduce stalls or missed error reporting.
- Resume/reset tests should confirm MMHUB arbitration, error status, RAS, and diagnostic state either reinitializes to known-good values or is intentionally preserved according to the platform reset model.

### subset-b-002779: lines 11751-14067

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_8_0_sh_mask.h lines 11751-14067

## Scope

This chunk covers 2,317 lines from the generated AMD MMHUB 1.8.0 shift/mask header. The range starts at `MMEA1_IO_WR_CLI2GRP_MAP0__CID0_GROUP__SHIFT` and ends at `MMEA2_IO_WR_PRI_URGENCY_MASKING__CID23_MASK_MASK`, so both boundaries are inside larger generated register families: the preceding chunk owns the `MMEA1_IO_RD_*` setup and the following chunk owns the remaining `MMEA2_IO_WR_PRI_URGENCY_MASKING` mask bits plus the later `MMEA2_IO_*` quantization and SDP/error-control fields.

The slice contains 2,190 `#define` field macros. There are no functions, structs, enums, variables, inline helpers, allocations, locks, or executable statements. Its API surface is entirely the preprocessor namespace of `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` constants.

## Purpose

`mmhub_1_8_0_sh_mask.h` supplies bit positions and bit masks for fields in the MMHUB 1.8.0 register map. Driver code includes it with `mmhub_1_8_0_offset.h` so register accesses can use symbolic offsets plus symbolic fields through AMDGPU helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and RAS register-table helpers.

This chunk describes the memory-management engine arbiter (`MMEA`) fields for engine instance 1 and the beginning of instance 2:

- `MMEA1` IO read/write client grouping, combine-flush, group burst, priority aging, queuing, fixed-priority, urgency, urgency masking, quantized-priority thresholds, SDP arbitration, SDP priority, credit reserve, miscellaneous control, latency sampling, performance counters, correctable/uncorrectable error status, and DSM error-injection controls.
- `MMEA2` DRAM and GMI client grouping, group-to-virtual-channel mapping, lazy request accumulation, CAM/reorder controls, page-burst limits, priority aging/queuing/fixed/urgency/quantization, and the start of IO grouping and urgency masking.

These macros do not themselves configure the GPU. They are the generated ABI that lets MMHUB v1.8 code and diagnostics build correctly packed 32-bit register values for arbitration, routing, performance, RAS, and error-injection registers.

## Important APIs, Types, And Data

The exported data is organized by hardware register name. Important groups in this chunk include:

- `MMEA1_IO_WR_CLI2GRP_MAP0/1` map IO write client IDs 0-31 into four scheduler groups using two-bit `CID*_GROUP` fields. The corresponding `MMEA1_IO_RD_CLI2GRP_MAP0/1` fields are in the previous chunk.
- `MMEA1_IO_RD_COMBINE_FLUSH` and `MMEA1_IO_WR_COMBINE_FLUSH` expose four group timers plus `COMB_MODE` for combined read/write flush behavior.
- `MMEA1_IO_GROUP_BURST` exposes read/write low/high burst limits for IO traffic.
- `MMEA1_IO_RD_PRI_*` and `MMEA1_IO_WR_PRI_*` define per-group aging rates, age coefficients, queuing coefficients, fixed coefficients, urgency coefficients/modes, 32-client urgency masks, and three sets of four 8-bit quantized-priority thresholds.
- `MMEA1_SDP_ARB_DRAM`, `MMEA1_SDP_ARB_GMI`, and `MMEA1_SDP_ARB_FINAL` define SDP burst-cycle/data limits, early read/write switch behavior, end-of-burst behavior, read/write bank-state decoupling, chain breaking, final DRAM/GMI/IO burst limits, readonly virtual-channel bits 0-7, and error/halt-on-error behavior.
- `MMEA1_SDP_DRAM_PRIORITY`, `MMEA1_SDP_GMI_PRIORITY`, and `MMEA1_SDP_IO_PRIORITY` assign 4-bit read/write priorities for groups 0-3 on DRAM, GMI, and IO paths.
- `MMEA1_SDP_CREDITS`, `MMEA1_SDP_TAG_RESERVE0/1`, `MMEA1_SDP_VCC_RESERVE0/1`, and `MMEA1_SDP_VCD_RESERVE0/1` describe tag, response, and per-VC credit reservation fields.
- `MMEA1_SDP_REQ_CNTL` covers outstanding read/write request thresholds, blocking controls, and deadlock timers.
- `MMEA1_MISC`, `MMEA1_MISC2`, and `MMEA1_MISC_AON` expose global arbiter behavior: DRAM/GMI/IO disable and reset indicators, clock-enable and soft-reset bits, command-buffer disable, client stall behavior, request blocking/throttling, response swap mode, and link-manager always-on controls.
- `MMEA1_LATENCY_SAMPLING`, `MMEA1_PERFCOUNTER_LO/HI`, `MMEA1_PERFCOUNTER0_CFG`, `MMEA1_PERFCOUNTER1_CFG`, and `MMEA1_PERFCOUNTER_RSLT_CNTL` define local sampling, performance counter selection/mode/enable/clear, and result selector/control fields.
- `MMEA1_UE_ERR_STATUS_LO/HI` and `MMEA1_CE_ERR_STATUS_LO/HI` provide RAS status-valid, address-valid, address, memory-id, ECC, error-info, count, and poison fields for uncorrectable and correctable errors.
- `MMEA1_DSM_CNTL`, `MMEA1_DSM_CNTLA/B`, `MMEA1_DSM_CNTL2`, and `MMEA1_DSM_CNTL2A/B` cover DSM and EDC error injection across DRAM read/write command, data, page memories; GMI read/write command, data, page memories; IO read/write command/data memories; return-tag memories; and MAM data memories.
- `MMEA2_DRAM_*` and `MMEA2_GMI_*` repeat the grouping, virtual-channel, lazy accumulation, CAM/reorder, burst, priority, urgency, urgency-mask, and quantized-threshold model for MMHUB engine instance 2 DRAM and GMI traffic.
- `MMEA2_IO_RD_CLI2GRP_MAP0/1`, `MMEA2_IO_WR_CLI2GRP_MAP0/1`, `MMEA2_IO_RD/WR_COMBINE_FLUSH`, `MMEA2_IO_GROUP_BURST`, and `MMEA2_IO_RD/WR_PRI_*` begin the IO-side fields for `MMEA2`. The chunk ends before all write urgency-mask bits are present.

The `addressBlock: aid_mmhub_ea_mmeadec2` marker appears at line 12770 and identifies the transition from `MMEA1` to the `MMEA2` decode block. The `MMEA1` address-block marker itself is earlier in the file, outside this chunk.

## Control Flow

There is no runtime control flow in this header. The flow is indirect:

1. `amdgpu/mmhub_v1_8.c` includes `mmhub/mmhub_1_8_0_offset.h` and this `mmhub/mmhub_1_8_0_sh_mask.h` file.
2. Normal MMHUB bring-up functions program VM/GART/aperture/TLB/cache/invalidation registers using generated offset and field macros from this header family.
3. The RAS path builds CE and UE register lists for `MMEA0` through `MMEA4`, including the `MMEA1_*_ERR_STATUS_*` and `MMEA2_*_ERR_STATUS_*` register offsets from the companion offset header. Generic RAS helpers then use status-valid, address-valid, memory-id, error-info, count, and poison field definitions from this mask header family when decoding and resetting errors.
4. Arbitration, DSM, latency, and performance-counter fields in this slice are available to driver diagnostics, firmware interaction, debug tooling, or future tuning paths that need to read or write MMEA registers without hard-coded bit arithmetic.

No branch, loop, or callback is implemented here; all sequencing and error handling live in the C consumers and in hardware/firmware programming policy.

## State And Persistence Behavior

The macros are compile-time constants and hold no software state. The registers they describe are persistent MMHUB hardware state until reset, suspend/resume reinitialization, GPU reset, firmware reprogramming, or an explicit driver write changes them.

Key hardware state represented by this chunk includes:

- Client-to-group and group-to-VC mappings, which determine how MMHUB clients are classified for DRAM, GMI, and IO arbitration.
- Scheduler behavior such as lazy accumulation delays/timeouts, CAM depths, reorder limits, burst caps, priority aging, urgency modes, and quantized-priority thresholds.
- Credit pools and per-VC reserves, which control how many tags or response credits can be consumed by traffic classes.
- Request blocking, throttling, clock-gating overrides, soft reset, and busy/reset status bits.
- Latency sampling and performance counter selector/enabler/result registers.
- RAS CE/UE status latches and DSM error-injection controls for command, data, tag, page, and MAM memories.

Because these are hardware registers rather than kernel-owned memory, persistence is tied to device power and reset domains. The header does not define locking, ordering, barriers, atomicity, or lifetime rules; callers must obey MMIO ordering and ASIC-specific programming sequences.

## Dependencies

This chunk depends on the generated MMHUB 1.8.0 register specification. It must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_8_0_offset.h`, which provides the matching `regMMEA1_*` and `regMMEA2_*` register offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v1_8.c`, the primary local MMHUB v1.8 C consumer.
- AMDGPU register helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `AMDGPU_RAS_REG_ENTRY`, `amdgpu_ras_inst_query_ras_error_count`, and `amdgpu_ras_inst_reset_ras_error_count`.
- MMHUB RAS memory identifiers, including names such as `AMDGPU_MMHUB_WGMI_PAGEMEM`, `AMDGPU_MMHUB_RDRAM_CMDMEM`, `AMDGPU_MMHUB_MAM_DMEM*`, `AMDGPU_MMHUB_WRET_TAGMEM`, and IO/GMI/DRAM command/data/page memory IDs.
- The generated SOC15 include structure and ASIC selection in `gmc_v9_0.c`, which wires MMHUB v1.8 functions and RAS support for matching hardware.

The naming pattern also depends on adjacent chunks. The source range begins after the `MMEA1_IO_RD_CLI2GRP_MAP1` mask family and ends before the final `MMEA2_IO_WR_PRI_URGENCY_MASKING` masks, so full per-file analysis must reconcile this document with chunks `subset-b-002778` and `subset-b-002780`.

## Integration Points

- MMHUB v1.8 initialization in `mmhub_v1_8_gart_enable()` configures core address-translation state, then enables the system domain, disables identity aperture, sets VMID configuration, and programs invalidation. This chunk is less about VM address fields and more about the MMEA arbitration/error-control field namespace that the same generated header family exposes.
- RAS integration in `mmhub_v1_8_ce_reg_list` and `mmhub_v1_8_ue_reg_list` includes `MMEA1` and `MMEA2` CE/UE error status registers. Generic RAS code uses those register pairs plus field definitions to query and reset per-instance error counts across `adev->aid_mask`.
- The `mmhub_v1_8_ras_memory_list` maps MMEA memory IDs to readable labels such as WGMI/RGMI/DRAM/IO command/data/page memories, MAM memories, and return-tag memories. Those labels line up directly with the CE/UE/DSM memory families exposed in this chunk.
- Performance diagnostics can use the `MMEA1_LATENCY_SAMPLING` and `MMEA1_PERFCOUNTER*` fields to select events, enable/clear counters, and read low/high result halves.
- Firmware, bring-up scripts, or future kernel tuning code can use the DRAM/GMI/IO client grouping, priority, urgency, burst, CAM, lazy, and SDP fields to adjust memory traffic arbitration without introducing raw bit constants.
- Error-injection and validation paths can use `MMEA1_DSM_CNTL*` together with `MMEA1_EDC_MODE` and `MMEA1_ERR_STATUS` to force, count, propagate, clear, or gate injected and real error conditions.

## Risks

- Generated-field drift is the central risk. A wrong shift or mask still compiles but causes `REG_SET_FIELD`/`REG_GET_FIELD` to write or decode the wrong bits in MMHUB registers.
- This chunk has split-family boundaries. Treating it as self-contained would miss `MMEA1_IO_RD_*` fields before line 11751 and the final `MMEA2_IO_WR_PRI_URGENCY_MASKING` bits after line 14067.
- Many fields are repeated across `MMEA0`-`MMEA4`, DRAM/GMI/IO paths, read/write directions, and groups 0-3. Copying a macro with the wrong engine instance, path, or direction can silently tune a different scheduler.
- Client grouping and group-to-VC mappings affect traffic routing and fairness. Bad values can starve clients, send traffic to an unintended virtual channel, or trigger backpressure.
- Lazy accumulation, CAM depth, reorder limits, burst caps, priority aging, urgency modes, quantization thresholds, and credit reservations are performance-sensitive. Incorrect tuning can cause latency spikes, throughput loss, head-of-line blocking, or hangs under high memory pressure.
- `MMEA1_MISC`, `MMEA1_MISC2`, request blocking, reset, clock-gating, and stall/override fields can disable paths or hold requests. Misuse can make the hub appear wedged even if VM programming is correct.
- RAS status fields must be decoded with the exact valid/address/memory-id/count/poison masks. Incorrect masks can undercount real errors, misattribute a memory block, or clear evidence before diagnostics collect it.
- DSM error-injection bits are hazardous in production. Accidentally enabling injection or bypass/gating modes can manufacture CE/UE events, poison traffic, or obscure genuine hardware faults.
- Cross-generation similarity is high. MMHUB 1.7, 1.8, and later generated headers use many similar names with different offsets or field layouts; mixing offset and mask headers from different generations is valid C but invalid hardware programming.

## Test Signals

- Build an AMDGPU configuration that includes `mmhub_v1_8.c` and the generated MMHUB 1.8.0 headers; this catches missing macro names but not semantic drift.
- Generated-header validation should compare every `MMEA1_*` and `MMEA2_*` field in this range against the authoritative MMHUB 1.8.0 register database, including field widths and split boundary completeness.
- Static checks should ensure every `regMMEA1_*`/`regMMEA2_*` error-status register used by `mmhub_v1_8.c` has matching `_STATUS_VALID_FLAG`, `_ADDRESS_VALID_FLAG`, `_ADDRESS`, `_MEMORY_ID`, `_ERR_INFO`, `_CE_CNT`, `_POISON`, or related masks in the mask header family.
- Runtime MMHUB v1.8 smoke should boot matching hardware, enable GART, run VMID/GPUVM workloads, suspend/resume, and reset without MMHUB faults or hung requests.
- RAS validation should inject or simulate CE/UE events for MMEA1 and MMEA2 memories, verify `amdgpu_ras_inst_query_ras_error_count()` reports the expected counts and memory IDs, and confirm reset clears the status latches.
- Performance-counter validation should program `MMEA1_PERFCOUNTER0_CFG`/`MMEA1_PERFCOUNTER1_CFG`, sample `MMEA1_PERFCOUNTER_LO/HI`, and verify clear/enable/result-control behavior against expected traffic.
- Arbitration tuning tests should stress DRAM, GMI, and IO traffic classes under concurrent GPUVM workloads and watch for fairness regressions, timeouts, RAS events, or request-blocked status after changing grouping, priority, urgency, burst, CAM, or credit fields.

### subset-b-002780: lines 14068-16391

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_8_0_sh_mask.h lines 14068-16391

## Scope

This chunk is a generated shift/mask section from the AMDGPU MMHUB 1.8.0 register header. It contains only C preprocessor constants and register-block comments; there are no functions, structs, enums, variables, allocations, locks, or executable branches in the requested range.

The range starts in the tail of `MMEA2_IO_WR_PRI_URGENCY_MASKING`, covers the rest of the MMEA2 memory-engine-address-decoder field map through `MMEA2_CE_ERR_STATUS_HI`, then starts `addressBlock: aid_mmhub_ea_mmeadec3` and covers most of the matching MMEA3 field map. It ends inside `MMEA3_LATENCY_SAMPLING`, after the `SAMPLER0_WRITE` shift definition and before the remaining latency-sampling fields and masks in the next chunk.

Major covered families are:

- MMEA2 IO priority quantization, SDP arbitration/priority/credits/tag and VC reserve controls, request control, miscellaneous arbitration behavior, latency sampling, performance counters, uncorrectable and correctable error status, DSM/error-injection controls, clock control, EDC mode, error status, request throttling, and always-on link-manager fields.
- MMEA3 DRAM/GMI/IO client-to-group maps, group-to-VC maps, lazy accumulation, CAM and page/group burst controls, priority aging/queuing/fixed/urgency/urgency masking/quantization controls, SDP arbitration/priority/credits/tag and VC reserve controls, request control, miscellaneous arbitration behavior, and the beginning of latency sampling.

## Purpose

The purpose of this header slice is to publish the bit-level ABI for MMHUB 1.8.0 MMEA2 and MMEA3 registers. Each field is represented with the generated AMD register-header convention:

- `<REGISTER>__<FIELD>__SHIFT`: the field's bit offset.
- `<REGISTER>__<FIELD>_MASK`: the 32-bit mask used to isolate or compose that field.

The sibling `mmhub_1_8_0_offset.h` header supplies the register offsets such as `regMMEA2_CE_ERR_STATUS_LO`, `regMMEA3_UE_ERR_STATUS_HI`, and the MMEA arbitration/control register names. This chunk supplies the field positions and masks that AMDGPU code can use with helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_FIELD`, `RREG32_SOC15`, and `WREG32_SOC15`.

Although the source tree path is under a local `ceph-client` mirror, the content is AMD GPU MMIO metadata, not Ceph or distributed filesystem logic.

## Important APIs, Types, And Macros

There are no normal C APIs or types in this range. The public interface is the macro namespace for MMEA2/MMEA3 register fields.

Important macro groups include:

- `MMEA2_IO_RD_PRI_QUANT_PRI*` and `MMEA2_IO_WR_PRI_QUANT_PRI*`: four 8-bit group threshold fields per priority-quantization register.
- `MMEA2_SDP_ARB_DRAM`, `MMEA2_SDP_ARB_GMI`, and `MMEA2_SDP_ARB_FINAL`: burst limits, early read/write switch controls, error-event and halt-request controls, read-only VC flags, and burst stretching.
- `MMEA2_SDP_{DRAM,GMI,IO}_PRIORITY`: packed 4-bit read/write priorities for groups 0 through 3.
- `MMEA2_SDP_CREDITS`, `MMEA2_SDP_TAG_RESERVE*`, `MMEA2_SDP_VCC_RESERVE*`, and `MMEA2_SDP_VCD_RESERVE*`: tag limits, response credits, tag reserves, and VC credit reserves for VCC/VCD pools, including `DISTRIBUTE_POOL`.
- `MMEA2_SDP_REQ_CNTL` and `MMEA3_SDP_REQ_CNTL`: request pass/write/atomic override bits, DRAM/GMI chain override bits, inner-domain mode, and block-level controls for read/write/atomic traffic.
- `MMEA2_MISC`, `MMEA2_MISC2`, `MMEA2_MISC_AON`, and `MMEA3_MISC`: relative arbitration priority flags, early write-return enable flags per VC, link-manager thresholds/delays, chain-switch/favour flags, CSGROUP swapping, IO read/write priority enable, request blocking, and DRAM/GMI throttles.
- `MMEA2_PERFCOUNTER_LO`, `MMEA2_PERFCOUNTER_HI`, `MMEA2_PERFCOUNTER0_CFG`, `MMEA2_PERFCOUNTER1_CFG`, and `MMEA2_PERFCOUNTER_RSLT_CNTL`: counter result fields, compare value, performance event range selection, mode, enable/clear, trigger controls, global clear, and stop-on-saturate behavior.
- `MMEA2_UE_ERR_STATUS_*` and `MMEA2_CE_ERR_STATUS_*`: valid flags, address fields, memory IDs, ECC/parity/poison flags, error-info fields, and UE/CE/FED counters. These are directly referenced by the MMHUB 1.8 RAS register tables.
- `MMEA2_DSM_CNTL*` and `MMEA2_DSM_CNTL2*`: data-share-memory single-write controls and error-injection enables/delay selectors for DRAM, GMI, IO, read-return/write-return tags, page memories, and MAM D0-D3 memories.
- `MMEA2_CGTT_CLK_CTRL` and `MMEA2_EDC_MODE`: on/off clock-gating timing, soft overrides, light-sleep override, EDC count/gate/dedicated-mode/propagate/bypass controls.
- `MMEA2_ERR_STATUS`: SDP response status/data status, parity error, clear/busy flags, fatal interrupt control, level-interrupt mode, and FUE client status.
- MMEA3 `*_CLI2GRP_MAP0/1`: 32 client-ID group mappings split into low and high halves for DRAM, GMI, and IO read/write paths.
- MMEA3 `*_GRP2VC_MAP`, `*_LAZY`, `*_CAM_CNTL`, page/group burst, and priority families: group-to-VC mapping, accumulation thresholds/timeouts/idle limits, CAM depth/reorder limits, chaining controls, read/write burst windows, aging/queuing/fixed/urgency coefficients, per-client urgency masking, and quantization thresholds.

## Control Flow

This chunk has no runtime control flow. Its effect is compile-time name binding for driver code that reads or writes MMHUB registers.

Runtime sequencing is owned by consumers:

1. AMDGPU MMHUB 1.8 code includes `mmhub_1_8_0_offset.h` and `mmhub_1_8_0_sh_mask.h`.
2. Code selects a register offset with `reg...` or `mm...` symbols from the offset header.
3. Register helpers compose field values using the `__SHIFT` and `_MASK` macros from this file.
4. MMIO helpers read, update, or write the register on the relevant MMHUB instance.

The chunk does not describe when a register may be written, whether a field is read-only, self-clearing, sticky, or write-one-to-clear, or what polling is required. Those rules come from the hardware specification and the higher-level MMHUB/RAS/performance/clock-gating code.

## State And Persistence Behavior

The header itself stores no software state and persists nothing. It describes MMIO-backed hardware state in the MMHUB memory-engine address-decode path.

The represented hardware state includes:

- Traffic classification state: mapping up to 32 client IDs into four arbitration groups for MMEA3 DRAM, GMI, and IO read/write paths.
- Arbitration and QoS state: group-to-VC mapping, priority coefficients, urgency modes, per-client urgency masking, priority quantization thresholds, burst limits, read-only VC flags, chain-breaking and page-based chaining controls, CAM depth/reorder limits, and read/write switch preferences.
- Credit and reserve state: SDP tag limits, read/write response credits, tag reservations for VC0-VC7, and VCC/VCD credit reserves with optional distributed pools.
- Request-control state: pass/write/atomic overrides, DRAM/GMI chain overrides, request block levels, and inner-domain mode.
- Error and RAS state: CE/UE status valid bits, failing address and memory ID fields, ECC/parity/poison flags, error-info payloads, CE/UE/FED counters, SDP response error state, FUE flags, fatal-interrupt control, and clear/busy bits.
- Diagnostic state: MMEA2 performance counter selection/results, result triggers, latency-sampling enables, DSM irritator/single-write controls, and DSM error-injection delay/enables.
- Power/clock and link-manager state: CGTT delay/override fields, EDC mode flags, early write-return flags, relative priority flags, link-manager dynamic mode/thresholds/reconnect delay/idle behavior, and always-on part-ack hysteresis/deassert mode.

Persistence is hardware-defined. Configuration fields generally persist until reprogrammed, reset, power-gated, or restored after suspend/resume. Status, error, interrupt, counter, clear, and injection fields may be sticky, read-only, write-one-to-clear, self-clearing, or sequencing-sensitive. The masks alone do not encode those semantics.

## Dependencies And Integration Points

This chunk depends on the generated MMHUB 1.8.0 register-header set:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_8_0_offset.h` supplies the matching register addresses and base indices.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_8_0_default.h`, where present for this ASIC generation, supplies reset/default values.
- AMDGPU SOC15 register helpers consume the offset and mask headers together.

The direct include site observed in this tree is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v1_8.c`, which includes this header together with `mmhub_1_8_0_offset.h`.

The clearest direct consumer for this specific chunk is MMHUB RAS setup in `mmhub_v1_8.c`. The CE and UE register lists reference `regMMEA2_CE_ERR_STATUS_LO/HI`, `regMMEA3_CE_ERR_STATUS_LO/HI`, `regMMEA2_UE_ERR_STATUS_LO/HI`, and `regMMEA3_UE_ERR_STATUS_LO/HI`. The RAS framework can then pair those offsets with generated status fields such as valid flags, address, memory ID, ECC/parity, error-info, and counters.

Other integration is implied by the generated register contract rather than visible direct references in this source slice:

- MMHUB QoS/arbitration tuning code can use MMEA2/MMEA3 DRAM/GMI/IO priority, burst, urgency, client mapping, and credit fields.
- Performance/debug paths can use MMEA2 performance counter and latency-sampling macros to select events, clear counters, set triggers, and read results.
- RAS and validation paths can use DSM and EDC/error-status fields for error injection, error propagation, and status decoding.
- Clock-gating and power-management paths can use CGTT/link-manager fields when coordinating MMHUB power and traffic-idle behavior.

Cross-generation similarity is high but not safe to assume. The repeated MMEA2/MMEA3 families resemble other MMHUB versions, but masks, field presence, and register offsets must remain matched to the 1.8.0 offset/mask/default set.

## Risks And Edge Cases

- Bitfield drift is high impact. A wrong shift or mask can silently program a different hardware field, causing traffic starvation, incorrect VC assignment, MMHUB hangs, bad RAS decoding, or broken performance counters.
- The repeated DRAM/GMI/IO and read/write families are copy-sensitive. Many field layouts are identical, but a typo across `MMEA3_DRAM_*`, `MMEA3_GMI_*`, and `MMEA3_IO_*` may affect only one traffic class or direction.
- Client-ID maps cover 32 clients in two registers. Off-by-one or low/high-half mistakes can route a single client to the wrong arbitration group and only appear under specific engines or workloads.
- QoS and arbitration fields interact. Priority coefficients, urgency masking, quantization thresholds, burst limits, CAM depth/reorder limits, VC mapping, and credit reserves should be validated as a set; changing one field can starve or over-prioritize another traffic class.
- Error status fields are RAS-visible. Misdecoding valid flags, memory IDs, address bits, CE/UE counts, FED counts, or poison/parity/ECC flags can produce wrong user-visible error reports or hide actionable failures.
- DSM and EDC controls are diagnostic and fault-injection sensitive. Enabling injection, bypassing EDC, or changing delay/single-write behavior in production paths can create artificial errors or mask real ones.
- Some fields are command-like or status-like despite being represented as plain masks, such as clear-error bits, counter clear bits, request-blocked status, injection enables, and busy-on-error controls. Consumers must follow hardware sequencing.
- The chunk starts and ends mid-family: `MMEA2_IO_WR_PRI_URGENCY_MASKING` begins before this range, and `MMEA3_LATENCY_SAMPLING` continues after it. The merge lane should join adjacent chunk research before making complete file-level claims about those two registers.

## Test Signals

Useful validation is mostly build coverage, generated-header consistency, and hardware/RAS behavior:

- Build AMDGPU with MMHUB 1.8 support enabled. Missing or renamed macros should fail in `mmhub_v1_8.c` and related SOC15 register code.
- Mechanically compare this generated header against AMD's authoritative MMHUB 1.8.0 register database and the matching `mmhub_1_8_0_offset.h`; each register field here must correspond to the correct offset name and bit layout.
- RAS tests should inject or observe MMHUB CE/UE events and verify that MMEA2/MMEA3 status valid flags, address fields, memory IDs, ECC/parity/poison flags, error-info fields, and CE/UE/FED counters decode correctly.
- MMHUB stress tests should exercise DRAM, GMI, and IO read/write traffic under mixed GPU engines to catch client-group, priority, urgency, credit, and VC-reserve programming errors.
- Performance-counter validation should select MMEA2 events, clear counters, use start/stop triggers, read LO/HI results, and verify stop-on-saturate or compare behavior where supported.
- Clock-gating and suspend/resume tests should cover CGTT, link-manager, EDC, and arbitration state restoration around reset, power gating, and resume.
- Error-path diagnostics should watch kernel logs and RAS telemetry for stuck busy/error bits, incorrect fatal interrupt behavior, unexpected request blocking, malformed memory IDs, or repeated CE/UE counter values.

## Cross-Chunk Notes

Adjacent chunks are required for complete coverage of the surrounding generated file. The previous chunk owns the beginning of `MMEA2_IO_WR_PRI_URGENCY_MASKING`, and the next chunk owns the rest of `MMEA3_LATENCY_SAMPLING` plus later MMHUB 1.8.0 register fields. The final per-file research document should reconcile those boundaries before describing complete MMEA2/MMEA3 latency and urgency-masking behavior.

### subset-b-002781: lines 16392-18711

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_8_0_sh_mask.h lines 16392-18711

## Scope

This chunk covers the tail of the `MMEA3` MMHUB EA decoder register field definitions and most of the next decoder instance, `aid_mmhub_ea_mmeadec4`, exposed as `MMEA4_*` shift and mask macros. The range starts inside `MMEA3_LATENCY_SAMPLING`, continues through the `MMEA3` performance-counter, uncorrectable/correctable error, DSM/error-injection, clock-gating, EDC, error-status, and miscellaneous control fields, and then defines the corresponding `MMEA4` client grouping, arbitration, priority, credit, performance, reliability, DSM, clock, EDC, and error-status fields through `MMEA4_MISC2`.

The file is a generated AMDGPU register-mask header. It contains no functions, structs, storage, or executable control flow. Its API surface is the set of C preprocessor constants that other AMDGPU MMHUB code uses when composing or decoding 32-bit memory-mapped register values.

## Purpose

The purpose of this chunk is to provide bit-accurate symbolic names for fields in MMHUB EA MMEA decoder instances 3 and 4 on `mmhub_1_8_0` ASICs. These fields let driver code express hardware programming in terms of client IDs, request groups, virtual channels, priority/urgency policy, SDP arbitration, credits, latency sampling, performance counters, ECC/parity status, error injection, and clock/error control instead of hard-coded numeric shifts and masks.

The `MMEA4` definitions mirror the pattern used for earlier MMEA decoder instances. They describe how DRAM, GMI, and IO read/write traffic is grouped, mapped to virtual channels, delayed, prioritized, throttled, blocked, counted, and diagnosed. The final per-file research pass should reconcile this chunk with the preceding and following chunks because `mmhub_1_8_0_sh_mask.h` is a single generated register map split only for research-size reasons.

## Important APIs And Register Families

The public API in this chunk is the macro naming convention:

- `REGISTER__FIELD__SHIFT` gives the least-significant bit of a field.
- `REGISTER__FIELD_MASK` gives the field mask already positioned in the register word.
- Consumers normally combine these with AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, or local read/modify/write helpers from the surrounding driver tree.

Important register families in this range include:

- `MMEA3_LATENCY_SAMPLING`, `MMEA4_LATENCY_SAMPLING`: two latency samplers with enable/select bits for DRAM, GMI, IO, read, write, atomic-return, atomic-no-return, and virtual-channel filters.
- `MMEA3_PERFCOUNTER_*`, `MMEA4_PERFCOUNTER_*`: low/high counter words, compare value, per-counter configuration (`PERF_SEL`, `PERF_SEL_END`, `PERF_MODE`, `ENABLE`, `CLEAR`), and result control (`PERF_COUNTER_SELECT`, start/stop triggers, enable-any, clear-all, stop-on-saturate).
- `MMEA3_UE_ERR_STATUS_*`, `MMEA4_UE_ERR_STATUS_*`: uncorrectable-error status, address validity, encoded address, memory ID, ECC/parity indicators, error-info validity, error-info payload, UE and FED counters, and reserved high bits.
- `MMEA3_CE_ERR_STATUS_*`: correctable-error status at the end of the `MMEA3` block, with valid/address/memory fields and high-word ECC, error-info, CE count, poison, and reserved bits.
- `MMEA3_DSM_*`, `MMEA4_DSM_*`: data SRAM/memory diagnostic and fault-injection controls for DRAM read/write command/page/data memories, GMI read/write command/page/data memories, IO read/write command/data memories, read/write return tag memories, and MAM D0-D3 memories.
- `MMEA4_DRAM_*`, `MMEA4_GMI_*`, `MMEA4_IO_*`: client-ID to group maps, group-to-virtual-channel maps, lazy request accumulation, CAM control, page/group burst limits, age/fixed/queue/urgency priorities, urgency masking per client ID, and quantum thresholds for the DRAM, GMI, and IO traffic classes.
- `MMEA4_SDP_*`: shared data path arbitration for DRAM/GMI/final arbitration, per-class priorities, tag and response credits, per-VC tag/VCC/VCD reservations, request pass/password overrides, request chain overrides, inner-domain mode, and read/write/atomic block levels.
- `MMEA4_MISC` and `MMEA4_MISC2`: relative priority mode, early write-return per VC, link-manager dynamic/reconnect/halt/idle settings, chain-switch preferences, client-group swapping, IO read/write priority enable, request blocking status, and DRAM/GMI read/write throttles.
- `MMEA4_CGTT_CLK_CTRL`, `MMEA4_EDC_MODE`, `MMEA4_ERR_STATUS`: clock-gating delays/overrides, EDC/FED/FUE handling, bypass/propagation policy, SDP response status, data parity error, error clearing, busy-on-error behavior, fatal interrupt controls, level interrupt mode, and client FUE flag.

## Control Flow

There is no direct control flow in this chunk. It is a declarative bitfield table.

Runtime control flow appears in the driver code that includes this header. Typical use is:

1. Read a 32-bit MMHUB register from the appropriate MMIO address header.
2. Use a `*_MASK` and `*_SHIFT` pair, or a higher-level field helper, to extract or update one field.
3. Write the composed value back during ASIC initialization, clock/power configuration, memory-hub tuning, RAS setup, performance collection, or debug/error-injection flows.

The macros are also used in branch decisions when driver code decodes status registers. For example, status-valid and address-valid fields gate whether an error record is meaningful, while fatal-interrupt and busy-on-error fields affect how initialization or recovery paths configure hardware behavior.

## State And Persistence Behavior

The header itself has no persistent state and performs no I/O. State changes occur only when another compilation unit uses these constants to program memory-mapped MMHUB registers.

The hardware state represented by these fields is persistent at the device-register level until reset or reprogramming. Important state classes include:

- Arbitration and quality-of-service state: client-to-group maps, group-to-VC maps, lazy accumulation, priority, urgency, burst, quantum, throttle, request-block, and chain-switch settings.
- Credit and reservation state: SDP tag limits, read/write response credits, per-VC tag reservations, and VCC/VCD credit reservations.
- Diagnostic state: latency-sampling filter selection, performance-counter configuration and current counter words.
- Reliability state: uncorrectable and correctable error status, ECC/parity flags, error counters, poison/FED/FUE status, fatal-interrupt policy, and clear-error bits.
- Test and fault-injection state: DSM irritator data, single-write enables, per-memory error-injection enables, injection-delay selection, and global injection delay.
- Power/clock state: clock-gating delay, hysteresis, soft stall/override bits, and EDC bypass/propagation controls.

Because these are hardware register definitions, incorrect use can persist until GPU reset and can affect memory request ordering, fairness, error reporting, or debug behavior across later driver operations.

## Dependencies And Integration Points

This header depends on the corresponding MMHUB address header for register offsets. The `_sh_mask.h` file supplies field-level layout, while code elsewhere needs the register address definitions to perform MMIO reads and writes. It also depends on the AMDGPU convention for generated ASIC headers: field names are stable tokens consumed by register helper macros and by ASIC-specific initialization tables.

Integration points include:

- AMDGPU MMHUB initialization and IP block code that configures client groups, virtual channels, priority policy, clock gating, and SDP credits for `mmhub_1_8_0`.
- RAS and error-handling paths that read `UE_ERR_STATUS`, `CE_ERR_STATUS`, `EDC_MODE`, and `ERR_STATUS` fields to classify ECC, parity, poison, FED/FUE, fatal, and response-status conditions.
- Performance and debug tooling paths that configure `PERFCOUNTER*`, `LATENCY_SAMPLING`, and result-control fields.
- Hardware validation and bring-up paths that use DSM/error-injection fields for targeted memory/register-file fault injection.
- Generated-register consistency with sibling decoder instances (`MMEA0` through `MMEA4` and later chunks), because much of the programming model is replicated per EA decoder.

Although this repository path sits under a Ceph client source import, the file is part of the Linux AMDGPU DRM hardware register interface, not Ceph filesystem logic.

## Risks And Edge Cases

The main risk is bitfield drift from the hardware specification. A wrong shift or mask can silently program the wrong field in a 32-bit MMIO register, affecting unrelated hardware behavior in the same word.

Several registers pack many independent fields tightly. The client-to-group maps place sixteen 2-bit client group fields in a single word, urgency masking places one bit per client ID across all 32 bits, and SDP priority/reservation registers pack multiple per-group or per-VC values. Callers must preserve unrelated bits during read/modify/write operations.

Fields with side effects need special care. `CLEAR`, `CLEAR_ALL`, `CLEAR_ERROR_STATUS`, DSM single-write enables, error-injection enables, request blocking, clock overrides, EDC bypass, and fatal-interrupt controls are not passive metadata. Accidentally setting them while updating adjacent fields could clear diagnostic state, inject errors, suppress protection, stall requests, or change interrupt delivery.

Status fields and control fields share naming conventions but have different access semantics. For example, `REQUESTS_BLOCKED`, `BUSY_ON_ERROR`, `FUE_FLAG`, `STATUS_VALID_FLAG`, and address-valid bits should generally be interpreted as hardware-reported state, while group maps, priority values, credits, and throttle bits are programmed policy. Code review should verify access direction against the register spec, not just the macro name.

The chunk boundary starts inside the `MMEA3` section and ends before the `MMEA4_CE_ERR_STATUS_*` definitions are complete in the next chunk. Any merged per-file report should avoid treating this document as a complete account of either decoder instance.

## Test Signals

High-signal validation is mostly compile-time and hardware/driver-behavior oriented:

- Build AMDGPU code paths that include `mmhub_1_8_0_sh_mask.h` so generated macro names and suffixes remain available to all consumers.
- Compare this header against the authoritative AMD register database for `mmhub_1_8_0`, especially packed client maps, urgency masks, SDP credit/reservation fields, DSM/error-injection fields, and `ERR_STATUS` side-effect bits.
- Exercise register helper unit tests or static checks, where available, to ensure representative `REG_SET_FIELD`/`REG_GET_FIELD` calls produce the expected masks and shifts for multi-bit fields such as client group, virtual channel, priority, credit, and injection delay.
- On hardware or simulator, read back programmed DRAM/GMI/IO group and priority settings after MMHUB initialization and confirm only intended fields changed.
- Use RAS/error-injection validation to confirm `UE_ERR_STATUS`, `CE_ERR_STATUS`, `EDC_MODE`, `ERR_STATUS`, and DSM injection controls report and clear expected ECC/parity/FED/FUE events.
- Use performance-counter and latency-sampling smoke tests to confirm counter enable/clear/select bits, start/stop triggers, and sampler filters select the intended traffic class and virtual channels.

### subset-b-002782: lines 18712-21060

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_8_0_sh_mask.h lines 18712-21060

## Scope

This chunk is a generated AMD MMHUB 1.8.0 register field header segment. It starts in the tail of the `MMEA4` address-decode block with `MMEA4_MISC2`, corrected-error status, and always-on link-manager fields. It then covers the `aid_mmhub_pctldec0` power-control block, L1 TLB status and performance-counter fields, ATC L2 fields, VM L2 control/fault/ECC fields, all `VM_CONTEXT0_CNTL` through `VM_CONTEXT15_CNTL` field masks, `VM_CONTEXTS_DISABLE`, and the beginning of the VM invalidation-engine request table through `VM_INVALIDATE_ENG4_REQ`.

The file contains preprocessor constants only. Every logical register field is represented as a `REGISTER__FIELD__SHIFT` macro plus a matching `REGISTER__FIELD_MASK` macro. There are no C functions, structs, variables, storage allocations, loops, branches, locks, or direct MMIO operations in this chunk. Runtime behavior comes from AMDGPU code that includes this header with the matching `mmhub_1_8_0_offset.h` register offsets and then uses `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and related SOC15 helpers.

Major covered blocks are:

- `MMEA4_MISC2`, `MMEA4_CE_ERR_STATUS_LO`, `MMEA4_MISC_AON`, and `MMEA4_CE_ERR_STATUS_HI`.
- `PCTL0_CTRL`, global MMHUB deep-sleep/override/ignore registers, per-slice `PCTL0_SLICE{0..4}_CFG_*`, `PCTL0_UTCL2_MISC`, and `PCTL0_SLICE{0..4}_MISC`.
- `MC_VM_MX_L1_TLB0_STATUS` through `MC_VM_MX_L1_TLB7_STATUS`.
- L1 TLB performance-counter config, result-control, low-result, and high-result fields.
- `ATC_L2_CNTL`, cache data, status, clock/power, DSM error-injection/counting, and MM group real-time-class fields.
- `VM_L2_CNTL` through `VM_L2_CNTL5`, VM dummy-page fault fields, VM L2 protection-fault control/status/address fields, identity-aperture fields, MM group real-time-class selection, reserved-CID bank-select fields, parity control, clock/busy control, and ECC index/control/status fields.
- `VM_CONTEXT0_CNTL` through `VM_CONTEXT15_CNTL`, `VM_CONTEXTS_DISABLE`, `VM_INVALIDATE_ENG0_SEM` through `VM_INVALIDATE_ENG17_SEM`, and `VM_INVALIDATE_ENG0_REQ` through the start of `VM_INVALIDATE_ENG4_REQ`.

## Purpose

This header segment defines the bit layout for MMHUB register programming on ASICs using the MMHUB 1.8.0 register map. The companion offset header says where a register is located; this shift/mask header says how to pack and unpack individual fields in that register.

The practical purpose is to make VM, memory-routing, RAS, TLB, ATC, and power-management programming readable and generation-specific. For example, `mmhub_v1_8.c` uses these field names to configure the L1 TLB, L2 cache, VMID contexts, VM fault-default behavior, active page migration retry behavior, identity aperture disablement, and invalidation-engine metadata. The macros also support RAS status decoding for `MMEA4` corrected errors, ATC/VM L2 ECC status, and low-level performance counter setup.

Because the header is generated, the important contract is exactness: the field name, bit shift, and mask must match the hardware register database for MMHUB 1.8.0. A wrong mask can compile successfully while changing the wrong bit in a live MMIO register.

## Important Macro Families

### MMEA4 RAS, Throttling, and Always-On Fields

The chunk begins with `MMEA4_MISC2` fields for DRAM/GMI arbitration swap controls, DRAM/GMI burst limits, IO read/write priority enablement, return-swap mode, request blocking, request-blocked status, and DRAM/GMI read/write throttle bits. These fields describe MMEA address-decode behavior and throttling state for the fourth memory-mapped engine/address decode instance.

The `MMEA4_CE_ERR_STATUS_LO` and `MMEA4_CE_ERR_STATUS_HI` macros define corrected-error status latches. The low word records validity flags, an address field, and memory ID. The high word records ECC, error-info validity, error info, CE count, poison, and reserved bits. `mmhub_v1_8.c` includes `regMMEA4_CE_ERR_STATUS_LO` and `regMMEA4_CE_ERR_STATUS_HI` in `mmhub_v1_8_ce_reg_list`, so these masks are part of MMHUB RAS query/reset behavior even though the RAS code does not live in this header.

`MMEA4_MISC_AON` exposes link-manager partial-ack hysteresis and deassert-mode fields. Those are always-on control-plane bits and should be treated as hardware policy/state, not software-owned persistent data.

### PCTL0 Deep-Sleep, Power-Gating, and Slice Controls

`PCTL0_CTRL` contains global MMHUB power-control fields: power-gating enable, allowed deep-sleep mode, RSMU and DAGB idle thresholds, an option to ignore protection faults for state-control purposes, EA0 through EA5 partial/full acknowledgement override bits, and RSMU read-timer controls.

The deep-sleep bitmaps are repeated across several registers:

- `PCTL0_MMHUB_DEEPSLEEP_IB` exposes DS0 through DS16 plus a `SETCLEAR` bit.
- `PCTL0_MMHUB_DEEPSLEEP_OVERRIDE` and `_OVERRIDE_IB` expose DS0 through DS16 plus ATHUB/CANE or IB-specific override coverage.
- `PCTL0_PG_IGNORE_DEEPSLEEP` and `_IB` define which deep-sleep indications power-gating logic should ignore, including ATHUB and all-IPS variants.
- `PCTL0_SLICE{0..4}_CFG_DS_ALLOW` and `_IB` repeat DS0 through DS16 allow masks per slice.

The per-slice `PCTL0_SLICE{0..4}_CFG_DAGB_BUSY` fields are full-width `DB_LNCFG` masks. `PCTL0_UTCL2_MISC` and `PCTL0_SLICE{0..4}_MISC` define register-engine start pointers, critical-register locks, tile idle thresholds, memory light-sleep enablement, forced PGFSM completion, deep-sleep/disconnect behavior, register-engine execute-on-update, and read timer enablement. These fields connect MMHUB to clock, power, and reset sequencing paths.

### L1 TLB Status and Performance Counters

`MC_VM_MX_L1_TLB0_STATUS` through `MC_VM_MX_L1_TLB7_STATUS` are compact status registers with `BUSY` and `FOUND_PARITY_ERRORS` bits for eight L1 TLB instances. They are useful for debug, hang analysis, and parity/error validation after L1 TLB programming.

The L1 performance counter register families provide:

- Four counter configs, `MC_VM_MX_L1_PERFCOUNTER0_CFG` through `3_CFG`, each with `PERF_SEL`, `PERF_SEL_END`, `PERF_MODE`, `ENABLE`, and `CLEAR`.
- `MC_VM_MX_L1_PERFCOUNTER_RSLT_CNTL` for selecting result counters, start/stop triggers, global enable, clear-all, and stop-on-saturate.
- `MC_VM_MX_L1_PERFCOUNTER_LO` and `_HI`, where the high word also carries a compare value.

The enable/clear/trigger fields are stateful hardware controls. Software must avoid assuming reads are passive if a selected counter mode has side effects elsewhere in the performance-monitoring pipeline.

### ATC L2 Translation, Cache, DSM, and Clock Fields

The ATC L2 block defines address-translation cache policy and observability fields:

- `ATC_L2_CNTL` covers translation read/write request counts, host translation request counts, address-mod dependence, cache invalidation mode, default-page-out-to-system-memory behavior, fragment/aperture interaction mode, and client GPA request fragment size.
- `ATC_L2_CNTL2` covers bank select/count, cache update mode, LRU update on write, tag-index swapping, VMID mode, and wildcard reference value.
- `ATC_L2_CACHE_DATA0..3` expose a cache-data inspection window containing validity, cached attributes, virtual page address high/low pieces, and physical page address pieces.
- `ATC_L2_CNTL3` covers fragment sizes, delayed invalidation requests, ATS request credits, clock-request hysteresis, and repeater fine-grain clock-gating override.
- `ATC_L2_STATUS` and `ATC_L2_STATUS2` expose busy/outstanding-request and uncorrectable-error status.
- `ATC_L2_MISC_CG`, `ATC_L2_MEM_POWER_LS`, and `ATC_L2_CGTT_CLK_CTRL` define clock-gating and memory light-sleep controls.
- `ATC_L2_CACHE_{4K,32K,2M}_DSM_INDEX` and `_DSM_CNTL` define ECC/DSM index selection, error injection, single-write, delay, counter write, SEC/DED count, and FUE test controls.
- `ATC_L2_CNTL4` and `ATC_L2_MM_GROUP_RT_CLASSES` define invalidate-map miss-disable and MM group real-time-class classification.

These masks interact with GPU address translation and ATS behavior. In the local `mmhub_v1_8.c`, ATC is enabled through `MC_VM_MX_L1_TLB_CNTL__ATC_EN` outside this exact chunk, while this chunk supplies lower-level ATC L2 policy/status fields needed by debug, RAS, and platform-specific tuning.

### VM L2 Cache, Fault, Identity Aperture, and ECC Fields

The `VM_L2_*` families are the main VM translation cache controls in this chunk. `VM_L2_CNTL` defines L2 cache enablement, L2 fragment processing, PTE/PDE endian swap modes, PDE cache tag generation, LRU update behavior, default-page-out behavior, PDE cache split mode, effective queue size, PDE fault classification, context-1 identity access mode, identity-mode fragment size, and tag-index swapping. `mmhub_v1_8_init_cache_regs()` uses these fields to enable L2 cache, fragment processing, PDE tag generation policy, fault classification, and identity access mode.

`VM_L2_CNTL2` defines global invalidation controls, big-page optimization/VMID mode, invalidate-cache mode, PDE cache effective size, queue stall behavior, and retry-latency behavior. `mmhub_v1_8_init_cache_regs()` sets the `INVALIDATE_ALL_L1_TLBS` and `INVALIDATE_L2_CACHE` bits during cache bring-up.

`VM_L2_CNTL3`, `VM_L2_CNTL4`, and `VM_L2_CNTL5` define bank selection, update modes, wildcard values, 4K/bigK fragment and effective sizes, force-miss controls, partition count, physical walker request controls, MM IFIFO transaction limits, clock-gating overrides, VFIFO head-of-queue behavior, and walker fetch PDE mtype/noalloc controls. `mmhub_v1_8.c` programs `VM_L2_CNTL3` from `regVM_L2_CNTL3_DEFAULT` and adjusts bank/fragment fields based on `adev->gmc.translate_further`; it programs `VM_L2_CNTL4` from `regVM_L2_CNTL4_DEFAULT` and toggles physical request fields for XGMI CPU-connected or APP APU configurations.

The VM fault registers are split across dummy-page and protection-fault controls:

- `VM_DUMMY_PAGE_FAULT_CNTL` and address registers define dummy-page fault enablement, logical-address comparison behavior, and low/high dummy-page address fields.
- `VM_L2_PROTECTION_FAULT_CNTL` defines fault status clearing, subsequent status-address update permission, default handling for range/PDE/translate-further/NACK/dummy/valid/read/write/execute faults, no-retry client interrupt bitmaps, and crash-on-fault bits.
- `VM_L2_PROTECTION_FAULT_CNTL2` defines PRT fault interrupt client maps, active page migration PTE behavior, read-retry behavior, and retry fault interrupt enablement.
- `VM_L2_PROTECTION_FAULT_STATUS` exposes more-faults, walker error, permission faults, mapping error, client ID, read/write, atomic, VMID, VF/VFID, uncorrectable error, and fatal error detected bits.
- Protection fault address/default-address registers split logical or physical page addresses into low 32-bit and high 4-bit pieces.

`mmhub_v1_8_init_system_aperture_regs()` writes the protection-fault default address and sets `ACTIVE_PAGE_MIGRATION_PTE_READ_RETRY`. `mmhub_v1_8_set_fault_enable_default()` updates most default-fault policy bits and sets crash-on-no-retry/retry bits when default handling is disabled. Fault handling correctness therefore depends directly on these masks.

Identity-aperture fields define context-1 low/high logical page boundaries and physical offset. `mmhub_v1_8_disable_identity_aperture()` uses the corresponding offset registers and these field definitions describe the low/high split.

The VM L2 reliability and debug fields include `VM_L2_BANK_SELECT_RESERVED_CID`, `VM_L2_BANK_SELECT_RESERVED_CID2`, `VM_L2_CACHE_PARITY_CNTL`, `VM_L2_CGTT_CLK_CTRL`, `VM_L2_CGTT_BUSY_CTRL`, ECC index registers for VML2, walker memory, and UTCL2, ECC control registers with injection/test/count fields, ECC status registers, `UTCL2_EDC_MODE`, and `UTCL2_EDC_CONFIG`. These support RAS, error injection, and low-level diagnostics.

### VM Context Controls and Context Disable Bitmap

`VM_CONTEXT0_CNTL` through `VM_CONTEXT15_CNTL` are repeated VMID context-control bit definitions. Each context has fields for:

- `ENABLE_CONTEXT`.
- Page-table depth and block size.
- Interrupt and default handling for range, dummy-page, PDE0, valid, read, write, execute, and secure protection faults.
- `RETRY_PERMISSION_OR_INVALID_PAGE_FAULT`.

`mmhub_v1_8_enable_system_domain()` programs `VM_CONTEXT0_CNTL` with context enable, VMID0 page-table depth/block size, and retry fault behavior. `mmhub_v1_8_setup_vmid_config()` programs contexts 1 through 15 using `VM_CONTEXT1_CNTL` as the base and `hub->ctx_distance` spacing, enabling contexts and setting the default fault policy bits plus retry permission for per-process XNACK support.

`VM_CONTEXTS_DISABLE` is a 16-bit disable bitmap, one bit per context. It provides a compact hardware control for disabling VM contexts, distinct from writing each `VM_CONTEXTn_CNTL`.

The repeated field names are intentionally context-specific (`VM_CONTEXT7_CNTL__...`, etc.) even when the bit layout is identical. That lets generated code and register-field macros remain type/name safe for each concrete register.

### VM Invalidation Semaphores and Requests

The chunk defines single-bit semaphore fields for `VM_INVALIDATE_ENG0_SEM` through `VM_INVALIDATE_ENG17_SEM`. These registers arbitrate or signal use of the eighteen MMHUB invalidation engines.

It then defines request fields for `VM_INVALIDATE_ENG0_REQ` through the beginning of `VM_INVALIDATE_ENG4_REQ`:

- `PER_VMID_INVALIDATE_REQ` is a 16-bit VMID request bitmap.
- `FLUSH_TYPE` selects the invalidation/flush type.
- Individual invalidate bits cover L2 PTEs, L2 PDE0/PDE1/PDE2, and L1 PTEs.
- `CLEAR_PROTECTION_FAULT_STATUS_ADDR` requests fault-address status clearing.
- `LOG_REQUEST` requests request logging.

`mmhub_v1_8_init()` stores `regVM_INVALIDATE_ENG0_REQ` and computes `hub->eng_distance` from adjacent engine request offsets. Other TLB flush paths use these addresses indirectly through `amdgpu_vmhub`. The field masks in this chunk define the request value semantics that those paths must write.

## Control Flow and State Behavior

There is no executable control flow in this header. It affects runtime only when included into C code that expands the macros.

The state represented by the macros is hardware state:

- Configuration state, such as VM L2 cache enablement, fragment sizes, physical walker request policy, context enablement, retry-fault policy, ATC L2 request/cache policy, PCTL deep-sleep permission, and clock-gating settings.
- Status state, such as L1 TLB busy/parity status, ATC L2 busy/UCE status, VM L2 fault status, ECC status, and MMEA4 corrected-error latches.
- Counter and performance-monitoring state, such as L1 performance counters and DSM/ECC SEC/DED count fields.
- Request/acknowledgement state, such as VM invalidation semaphore and request registers.
- Error-injection/test state, such as ATC DSM controls and VML2/walker/UTCL2 ECC controls.

Some fields are write-one-to-clear, request, latch, or counter-control fields in hardware terms, but the header itself does not encode those semantics beyond names and masks. Ordering, timeouts, polling, reset values, and privilege constraints are implemented in driver code and hardware documentation.

AMDGPU also has mode2 save/restore storage for several VM/MMHUB registers in `struct amdgpu_gmc`, including `VM_L2_CNTL`, `VM_L2_CNTL2`, dummy-page fault registers, protection-fault registers, MM group RT class fields, bank select fields, parity control, all 16 VM context controls and page-table address arrays, and `MC_VM_MX_L1_TLB_CNTL`. This chunk contributes masks for many of those saved/restored registers, but the persistence itself is in the driver data structure, not in this generated header.

## Dependencies and Integration Points

This chunk depends on the AMD generated-register convention:

- `mmhub_1_8_0_offset.h` provides the matching `reg...` offset macros for the same MMHUB 1.8.0 register names.
- `soc15_common.h` and `soc15.h` provide SOC15 register-access helpers.
- `REG_SET_FIELD` and `REG_GET_FIELD` use the `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` macros to modify packed register values.
- `amdgpu/mmhub_v1_8.c` is the primary local consumer for MMHUB 1.8 programming.

Observed integration points in `mmhub_v1_8.c` include:

- `mmhub_v1_8_init_system_aperture_regs()`, which programs `VM_L2_PROTECTION_FAULT_DEFAULT_ADDR_*` and updates `VM_L2_PROTECTION_FAULT_CNTL2__ACTIVE_PAGE_MIGRATION_PTE_READ_RETRY`.
- `mmhub_v1_8_init_cache_regs()`, which uses `VM_L2_CNTL`, `VM_L2_CNTL2`, `VM_L2_CNTL3`, and `VM_L2_CNTL4` fields to enable and tune the MMHUB L2 translation cache.
- `mmhub_v1_8_enable_system_domain()`, which uses `VM_CONTEXT0_CNTL` fields for VMID0 context enablement and page-table shape.
- `mmhub_v1_8_setup_vmid_config()`, which uses `VM_CONTEXT1_CNTL` fields and context spacing to initialize VMIDs 1 through 15.
- `mmhub_v1_8_disable_identity_aperture()`, which writes the identity aperture low/high and physical offset registers whose low/high page-number fields are defined here.
- `mmhub_v1_8_program_invalidation()` and `mmhub_v1_8_init()`, which rely on the invalidation-engine register family; this chunk provides semaphore and request field semantics for engines 0 through 4.
- `mmhub_v1_8_set_fault_enable_default()`, which uses `VM_L2_PROTECTION_FAULT_CNTL` masks to switch between default-page fault handling and crash-on-fault behavior.
- `mmhub_v1_8_ce_reg_list`, which references `MMEA4_CE_ERR_STATUS_LO/HI` offsets and depends on the matching status-valid, info-valid, address, memory-ID, CE-count, and poison field definitions for correct RAS interpretation.

## Risks

- Mask or shift drift is silent at compile time. A wrong bit definition can produce valid C that corrupts VM, ATC, power, or RAS behavior at runtime.
- The chunk mixes control, status, request, and error-injection fields. Treating request or clear bits as normal persistent configuration can lose fault information, trigger unexpected invalidations, or disturb performance counters.
- VM L2 fields are central to address translation. Incorrect `ENABLE_L2_CACHE`, invalidation, page-fragment, walker, or fault-classification masks can cause stale translations, VM faults, hangs, or data corruption.
- VM context fields are repeated across 16 contexts. A copy-generation error in one context's masks may only affect specific VMIDs and can be hard to reproduce.
- Invalidation request fields must align with the firmware/driver flush protocol. Bad `PER_VMID_INVALIDATE_REQ`, `FLUSH_TYPE`, or L1/L2 invalidate masks can leave stale TLB entries after page-table updates.
- Protection-fault controls are security and stability sensitive. Incorrect default handling or crash-on-fault bits can either hide real faults by routing them to a dummy page or escalate recoverable faults into GPU resets.
- The address registers in this family split page addresses into low 32-bit and high 4-bit fields. Callers shift GPU addresses before writing, so mask mistakes here combine badly with address-shift mistakes in code.
- PCTL0 deep-sleep and clock/power fields can produce platform-specific failures. A wrong slice allow/ignore bit may only appear under suspend/resume, low-power states, clock gating, or multi-die activity.
- ATC L2 DSM/ECC controls include error injection and counter-write fields. Accidentally enabling injection or writing counters in production paths could pollute RAS telemetry or generate synthetic faults.
- The chunk stops mid-family at `VM_INVALIDATE_ENG4_REQ`; later invalidation-engine request, ack, and address-range fields are in subsequent lines/chunks and must be reconciled in the final per-file report.

## Test and Validation Signals

Useful validation is mostly build, boot, and hardware-integration testing:

- Build AMDGPU with MMHUB 1.8 support enabled to catch missing or renamed masks used by `mmhub_v1_8.c`.
- Boot on MMHUB 1.8 hardware and verify GART/VM bring-up, including VMID0 context programming and VMIDs 1 through 15 context setup.
- Run GPU memory-management workloads that update page tables and force TLB invalidations; hangs or stale mappings point at `VM_INVALIDATE_ENG*` request semantics or VM L2 invalidation fields.
- Exercise XNACK/retry-fault and active-page-migration paths, checking `VM_CONTEXTn_CNTL__RETRY_PERMISSION_OR_INVALID_PAGE_FAULT` and `VM_L2_PROTECTION_FAULT_CNTL2` behavior.
- Trigger invalid memory accesses under debug kernels and confirm VM fault status decodes CID, VMID, RW/atomic, permission/mapping, VF/VFID, UCE, and FED fields as expected.
- Validate the default-page fault path by toggling `mmhub_v1_8_set_fault_enable_default()` behavior and confirming default-page routing versus crash-on-fault behavior.
- Run suspend/resume, reset, and clock/power-management stress tests to catch PCTL0 deep-sleep, slice, clock-gating, or UTCL2 miscellaneous field regressions.
- Query and reset MMHUB RAS state, verifying `MMEA4_CE_ERR_STATUS_LO/HI` decoded addresses, memory IDs, CE counts, poison, and validity flags.
- Use RAS injection or lab-only diagnostics for ATC DSM and VML2/walker/UTCL2 ECC fields, ensuring injection enable/count/test bits are only touched by intended diagnostic paths.
- Use performance-counter diagnostics to confirm L1 counter select, mode, enable, clear, trigger, result low/high, compare, and saturation behavior.
- Compare regenerated `mmhub_1_8_0_sh_mask.h` against the authoritative register database, with special attention to repeated VM context fields, PCTL slice fields, and invalidation-engine request fields.

## Cross-Chunk Notes

This chunk begins after most of `MMEA4_MISC2` has already been defined, so the complete `MMEA4_MISC2` field story is split with the previous chunk. It also ends while the invalidation-engine request family is still in progress; engines 5 through 17, invalidate acknowledgements, and address-range fields continue later in the source file. The merge/reconciliation lane should connect these neighboring chunks before producing the final per-file report.

### subset-b-002783: lines 21061-22628

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_8_0_sh_mask.h lines 21061-22628

## Purpose

This chunk is the tail of the generated MMHUB 1.8.0 register shift/mask header used by the AMDGPU driver. It does not implement executable control flow; it defines C preprocessor constants that describe bit positions and bit masks for MMHUB register fields. The paired offset header supplies register addresses, while this header supplies the field encodings consumed through `REG_SET_FIELD`, `REG_GET_FIELD`, raw mask operations, and SOC15 register read/write helpers.

The covered range spans several hardware programming areas:

- VM invalidate engine request, acknowledgement, and address-range fields for engines 4-17, plus the full ACK and address-range macro sets for engines 0-17.
- Per-VMID page-table base, start, and end address fields for contexts 0-15.
- Shared VM aperture, framebuffer, AGP, DRAM, HBM, XGMI, SR-IOV, IOMMU, MARC, and ATS control fields.
- ATC L2, VM L2, UTC translation-assist, and L2 TLB performance counter fields.
- MM_CANE clock-gating override and correctable/uncorrectable error status fields used by RAS paths.

## Important APIs, Types, and Macros

This file exports macros rather than APIs or types. The important macro families are:

- `VM_INVALIDATE_ENGn_REQ__*`: request fields for invalidation engines. `PER_VMID_INVALIDATE_REQ` occupies bits 0-15, `FLUSH_TYPE` occupies bits 16-17, and one-bit controls select L2 PTE, L2 PDE0/PDE1/PDE2, L1 PTE invalidation, protection-fault status clearing, and request logging.
- `VM_INVALIDATE_ENGn_ACK__*`: acknowledgement fields for invalidation engines. The low 16 bits mirror per-VMID acknowledgement state, and bit 16 is `SEMAPHORE`.
- `VM_INVALIDATE_ENGn_ADDR_RANGE_LO32/HI32__*`: per-engine invalidate address-range fields. The low word carries an `S_BIT` plus low logical page address bits; the high word carries the high 5 logical page address bits.
- `VM_CONTEXTn_PAGE_TABLE_BASE_ADDR_*`, `VM_CONTEXTn_PAGE_TABLE_START_ADDR_*`, and `VM_CONTEXTn_PAGE_TABLE_END_ADDR_*`: per-context page-table root and virtual address bound encodings. Base registers use full 32-bit low/high page-directory-entry pieces; start/end high registers expose only a 4-bit high logical page-number field.
- `MC_VM_*`: shared memory-controller VM aperture and translation controls, including framebuffer location, AGP bounds, system aperture bounds, default physical page address, L1 TLB control, top-of-DRAM fields, cacheable DRAM and local HBM ranges, direct-system aperture behavior, XGMI local framebuffer sizing, SR-IOV VF framebuffer size/offset, active function ID, and GPU IOV enable bits.
- `VM_IOMMU_*`, `MC_VM_MARC_*`, and `VM_PCIE_ATS_CNTL*`: IOMMU enable/performance, MARC base/relocation/length windows, and PCIe ATS enable/STU fields for PF and VFs.
- `ATC_L2_PERFCOUNTER*`, `MC_VM_L2_PERFCOUNTER*`, and `L2TLB_PERFCOUNTER*`: performance counter result, selection, mode, enable, clear, trigger, and saturation-control fields.
- `UTC_GPUVA_VMID_TRANSLATION_ASSIST_*`: request/response fields for software or debug-assisted GPU virtual address translation, including VMID, GPU VA, permissions, client ID, request/ack/nack, fragment size, snoop, SPA/IO, TMZ, memory type, and no-PTE status.
- `MM_CANE_*`: clock-gating soft overrides plus error status fields for SDPM/SDPS response/data/parity status and CE/UE ECC/parity address, memory ID, info, count, poison, and fatal-event fields.

The direct integration point in the AMDGPU code for this ASIC generation is `amdgpu/mmhub_v1_8.c`, which includes both `mmhub_1_8_0_offset.h` and this shift/mask header.

## Control Flow

There is no runtime control flow inside the header. Runtime behavior appears in code that consumes these constants:

- `mmhub_v1_8_setup_vm_pt_regs()` writes `regVM_CONTEXT0_PAGE_TABLE_BASE_ADDR_LO32/HI32` plus context-offset distances to program per-VMID page-table roots.
- `mmhub_v1_8_init_gart_aperture_regs()` programs context 0 start/end bounds with `regVM_CONTEXT0_PAGE_TABLE_START_ADDR_*` and `regVM_CONTEXT0_PAGE_TABLE_END_ADDR_*`.
- `mmhub_v1_8_init_system_aperture_regs()` writes AGP, framebuffer, system aperture, default-page, and fault default-address registers whose fields are defined in this header chunk.
- `mmhub_v1_8_init_tlb_regs()` reads and rewrites `regMC_VM_MX_L1_TLB_CNTL` using the `MC_VM_MX_L1_TLB_CNTL__*` field macros for L1 TLB enable, system access mode, advanced driver model, aperture behavior, memory type, and ATC enable.
- `mmhub_v1_8_setup_vmid_config()` iterates VM contexts 1-15 and writes per-context page-table start/end bounds using the register spacing derived from context address register offsets.
- `mmhub_v1_8_program_invalidation()` iterates 18 invalidation engines and initializes each engine address range to the full range using `regVM_INVALIDATE_ENG0_ADDR_RANGE_LO32/HI32` plus `hub->eng_addr_distance`.
- `mmhub_v1_8_init()` caches `vm_inv_eng0_req`, `vm_inv_eng0_ack`, `ctx_addr_distance`, `eng_distance`, and `eng_addr_distance`, making the repeated register layout in this chunk part of the generic VM hub invalidation path.
- The RAS tables in `mmhub_v1_8.c` add `regMM_CANE_CE_ERR_STATUS_LO/HI` and `regMM_CANE_UE_ERR_STATUS_LO/HI`, which correspond to the MM_CANE CE/UE masks defined at the end of this chunk.

## State and Persistence Behavior

The macros describe hardware register state. Persistence is therefore MMIO/hardware-local, not file-backed:

- Page-table base/start/end registers persist in MMHUB until rewritten by driver initialization, VM context setup, reset, suspend/resume restore, or GPU reset recovery.
- Invalidation request and acknowledgement registers are transient synchronization state between CPU/driver writes and MMHUB completion. The field layout must match hardware because the VM manager polls ACK bits and relies on engine spacing to select the correct invalidation engine.
- Aperture and address-window registers define persistent translation windows while the device is running: framebuffer location, AGP range, system aperture, cacheable DRAM, local HBM, XGMI LFB, MARC regions, and VF framebuffer partitioning.
- TLB/cache control bits persist until changed and directly affect translation behavior, caching, ATS/ATC participation, and fault handling.
- Performance counters persist as hardware counters until cleared through their `CLEAR` or `CLEAR_ALL` fields; result registers split low 32 bits from high 16 counter bits and high 16 compare-value bits.
- MM_CANE CE/UE status registers hold error records, address-valid flags, memory IDs, error info, and counters until cleared or consumed by RAS handling. `MM_CANE_ERR_STATUS__CLEAR_ERROR_STATUS` is the explicit clear bit for the aggregate error-status register.

## Dependencies and Integration Points

This chunk depends on the SOC15 AMDGPU register infrastructure:

- `mmhub_1_8_0_offset.h` provides `reg...` register names; this header provides the matching `__SHIFT` and `__MASK` constants.
- `soc15.h`/`soc15_common.h` provide `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, and `SOC15_REG_OFFSET`.
- Generic register helpers such as `REG_SET_FIELD` depend on the naming convention `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT`.
- VM hub integration uses `struct amdgpu_vmhub` fields such as `ctx0_ptb_addr_lo32`, `vm_inv_eng0_req`, `vm_inv_eng0_ack`, `ctx_addr_distance`, `eng_distance`, and `eng_addr_distance`.
- GART and VM programming depends on `adev->gmc`, `adev->vm_manager`, `adev->aid_mask`, SR-IOV state, XGMI migration state, PSP indirect register programming, and `for_each_inst()` over AID/MMHUB instances.
- RAS integration depends on `AMDGPU_RAS_REG_ENTRY`, `struct amdgpu_ras_err_status_reg_entry`, and the MMHUB RAS query paths that read MM_CANE CE/UE status pairs.

## Risks and Edge Cases

- The register layout is generated and highly repetitive. A single incorrect shift or mask in a repeated VM context or invalidation-engine family would not be caught by C type checking and could silently program the wrong hardware field.
- The requested range starts in the middle of `VM_INVALIDATE_ENG4_REQ`; lines before the chunk define the matching ENG4 shift fields and earlier engines. Research consumers should merge this chunk with adjacent chunks before treating the per-engine family as complete.
- The driver derives spacing from adjacent offsets (`regVM_INVALIDATE_ENG1_REQ - regVM_INVALIDATE_ENG0_REQ`, `regVM_CONTEXT1_PAGE_TABLE_BASE_ADDR_LO32 - regVM_CONTEXT0_PAGE_TABLE_BASE_ADDR_LO32`). If masks or offsets diverge from the hardware generation, invalidation and VMID programming can target wrong registers across all instances.
- Address fields encode page numbers, not byte addresses. Callers shift GPU/physical addresses before writing; using byte addresses directly would overrun masked fields or translate the wrong aperture.
- High address fields are narrow in several groups: start/end high logical page numbers use 4 bits, invalidate range high uses 5 bits, and system aperture default MSB uses 4 bits. Future address-width changes require ASIC-specific headers and cannot be assumed compatible.
- SR-IOV and PF/VF fields are security-sensitive. `MC_VM_FB_SIZE_OFFSET_VFn`, `MC_SHARED_ACTIVE_FCN_ID`, ATS VF enables, `MC_SHARED_VIRT_RESET_REQ`, and `MC_VM_XGMI_GPUIOV_ENABLE` affect virtual function isolation and reset behavior.
- ATS/ATC/IOMMU/MARC controls interact with CPU-visible translation and migration features. Enabling `ATC_ENABLE`, `IOMMUEN`, `MARC_EN`, or relocation windows with bad ranges can create stale translations or incorrect access permissions.
- RAS masks for MM_CANE encode both status and clear/interrupt bits in the same register group. Clearing or enabling fatal interrupts with the wrong mask can lose diagnostic state or generate unexpected interrupts.

## Test Signals

Useful validation signals are mostly integration and hardware-facing:

- Build-test the AMDGPU driver after header changes; compile failures around `REG_SET_FIELD` or missing masks catch naming and generation regressions.
- Exercise GART enable/disable on MMHUB 1.8 hardware and confirm `mmhub_v1_8_get_fb_location()`, GART aperture setup, VMID page-table setup, and L1 TLB programming complete without VM faults.
- Run VM invalidation stress paths, including many VMIDs and multiple MMHUB/AID instances, and check that invalidation request/ACK polling completes without hangs.
- Validate SR-IOV PF and VF boot paths when touching VF framebuffer, ATS, active-function, or GPUIOV fields.
- Check RAS injection or error-query paths for MM_CANE CE/UE records; expected signals are correct CE/UE counts, memory IDs, address-valid flags, and no spurious fatal interrupt behavior.
- Use performance counter smoke tests or debugfs/perf tooling, where available, to verify ATC L2, VM L2, and L2 TLB counter clear/enable/result paths.
- Suspend/resume and GPU reset are important because the register state described here must be reinitialized consistently after hardware context loss.
