# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_7_sh_mask.h lines 4718-7076

## Purpose

This chunk is part of a generated AMD MMHUB 1.7 register shift/mask header. It defines C preprocessor constants for bitfield extraction and composition in MMHUB DAGB register blocks. Each field is exposed through the conventional AMDGPU generated-header pair:

- `<REGISTER>__<FIELD>__SHIFT` for the low bit position.
- `<REGISTER>__<FIELD>_MASK` for the raw 32-bit field mask.

The repository path is under `distributed-fs/ceph-client`, but this source is GPU driver hardware metadata, not Ceph or filesystem logic. The chunk contains no executable functions, structs, callbacks, or software algorithms.

The range starts in the middle of DAGB2 write-path definitions and then enters `addressBlock: mmhub_dagb_dagbdec3`, covering a large part of DAGB3 read and write register layouts. DAGB appears to be an MMHUB data/arbitration gateway block with per-client, per-virtual-channel, credit, pending, clock-gating, performance, and fatal-error reporting fields.

## Important APIs, Types, And Macros

There are no normal C APIs or types in this slice. The macro namespace is the public interface consumed by AMDGPU register access code together with the matching MMHUB 1.7 offset header.

Major field families in this chunk include:

- `DAGB2_WR_*`: the tail of the DAGB2 write path, including output lazy timers, clock-gating controls, address/data DAGB burst and lazy-timer tables, per-VC write controls, credit controls, snoop override, pending-bit status, delay injection, miscellaneous remap/clock/busy controls, fatal-error decode fields, FIFO/credit fullness, performance counters, L1TLB register read/write controls, and reserved registers.
- `DAGB3_RDCLI0..15` and `DAGB3_WRCLI0..15`: repeated client control registers with `VIRT_CHAN`, TLB-credit checking, urgency high/low thresholds, max/min bandwidth controls, OSD limiter enable, and max outstanding request fields.
- `DAGB3_RD_CNTL` and `DAGB3_WR_CNTL`: shared read/write control words for SCLK frequency encoding, client and VC bandwidth windows, IO level override and compliance VC, shared VC count, and jump-fix behavior.
- `DAGB3_RD_GMI_CNTL` and `DAGB3_WR_GMI_CNTL`: GMI path credit, level, max-burst, and lazy-timer fields.
- `DAGB3_RD_ADDR_DAGB`, `DAGB3_WR_ADDR_DAGB`, and `DAGB3_WR_DATA_DAGB`: DAGB enable, jump-ahead enable, self-init disable, `WHOAMI`, and read/write address `JUMP_MODE` controls.
- `*_OUTPUT_DAGB_MAX_BURST` and `*_OUTPUT_DAGB_LAZY_TIMER`: per-VC nibbles for output burst and timer tuning across VC0-VC7.
- `*_ADDR_DAGB_MAX_BURST0/1`, `*_ADDR_DAGB_LAZY_TIMER0/1`, `*_DATA_DAGB_MAX_BURST0/1`, and `*_DATA_DAGB_LAZY_TIMER0/1`: per-client nibble fields for clients 0-15.
- `DAGB3_RD_VC0_CNTL..DAGB3_RD_VC7_CNTL` and `DAGB3_WR_VC0_CNTL..DAGB3_WR_VC7_CNTL`: per-virtual-channel storage and EA credits, bandwidth limiters, minimum bandwidth controls, OSD limiter enable, and max OSD fields.
- `*_CNTL_MISC`, `*_TLB_CREDIT`, `*_DATA_CREDIT`, `*_MISC_CREDIT`, `*_OSD_CREDIT_CNTL*`, `DAGB3_RD_RDRET_CREDIT_CNTL*`, and `DAGB3_WR_ATOMIC_FIFO_CREDIT_CNTL1`: pool, TLB, return, atomic FIFO, OSD, and data-credit allocation fields.
- `*_PENDING`: full-width busy bitmaps for ask/go/global-send/TLB/OARB/OSD/DBUS pending state.
- `DAGB2_PERFCOUNTER*` and `DAGB2_PERFCOUNTER_RSLT_CNTL`: low/high counter value fields, compare value, selector ranges, modes, enable/clear bits, trigger selection, enable-any, clear-all, and stop-on-saturate controls.
- `DAGB2_FATAL_ERROR_STATUS*` and `DAGB3_FATAL_ERROR_STATUS*`: fatal-error valid bit, client ID, address low/high fields, tag, VFID/VF, address space, IO, size, FED, operation, write/read TMZ, snoop, invalidate, NACK, read-only, memlog, and EOP decode fields.

## Control Flow

This header chunk has no runtime control flow. Its only behavior is C preprocessing.

Typical consumer flow is:

1. A MMHUB 1.7 AMDGPU source includes the companion offset header and this mask header.
2. The caller selects a `mmDAGB*` register offset from the offset header and the relevant `DAGB*__FIELD__SHIFT` and `DAGB*__FIELD_MASK` macros from this header.
3. Driver code uses AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32`, `WREG32`, or SOC15-style wrappers to assemble, update, poll, or decode a 32-bit MMIO register.
4. Actual ordering, idle requirements, polling loops, reset handling, and firmware coordination live in the consumer driver code, not in this generated header.

The repeated macro layout implies several hardware programming patterns: per-client setup across 16 clients, per-VC setup across 8 virtual channels, per-direction read/write tuning, and status collection from full-width busy or error registers.

## State And Persistence Behavior

The macros persist no software state. They describe hardware-visible MMHUB DAGB state.

The represented hardware state includes:

- Persistent-until-reprogrammed configuration: virtual-channel selection, TLB credit checking, urgency thresholds, bandwidth windows, max/min bandwidth limits, OSD limits, GMI credit and burst behavior, DAGB enable/jump settings, per-client burst sizes, per-client lazy timers, per-VC credit pools, clock-gating delays, and VC remapping.
- Volatile live status: pending busy bitmaps, FIFO empty/full bits, write/read credit full fields, and fatal-error status words.
- Action or control bits: fatal-error clear, performance-counter enable/clear, performance result clear-all, stop-on-saturate, clock-gating override bits, GPU snoop override/value masks, and L1TLB register read/write control bits.
- Diagnostic and telemetry state: performance counter low/high values, compare value, performance select windows, start/stop triggers, DAGB delay fields, fatal-error address/tag/VF/client/operation decodes, and reserved scratch-like words.

Persistence is hardware-defined. Configuration fields are expected to be reprogrammed during ASIC initialization, reset recovery, power-management transitions, virtualization setup, or golden-setting application. Status and counter fields may be volatile, latched, clear-on-write, or meaningful only after specific blocks are idle or selected.

## Dependencies

This chunk depends on the generated AMD MMHUB 1.7 register set remaining synchronized:

- `mmhub_1_7_sh_mask.h` supplies the field masks and shifts documented here.
- The matching MMHUB 1.7 offset header supplies the actual register addresses for the `DAGB2_*` and `DAGB3_*` registers.
- AMDGPU bitfield helpers depend on exact macro spelling, especially the `__SHIFT` and `_MASK` suffix convention.
- MMHUB initialization, golden settings, memory-management bring-up, clock-gating setup, GPU reset/recovery, virtualization, and hang-dump paths depend on these bit layouts matching the ASIC specification.
- Similar DAGB register families exist across DAGB0, DAGB1, DAGB2, and DAGB3 and across MMHUB generations. The names are deliberately regular, but fields can still differ by generation or block instance.

## Integration Points

Primary integration points are:

- MMHUB register programming: consumers combine these masks with MMHUB offsets to program DAGB read/write client routing, bandwidth, credit, lazy-timer, and burst behavior.
- Power and clock management: `*_CGTT_CLK_CTRL`, `*_L1TLB_*_CGTT_CLK_CTRL`, `*_ATCVM_*_CGTT_CLK_CTRL`, and `DAGB*_CNTL_MISC2` fields expose clock-gating delays, light-sleep overrides, soft-stall overrides, and clock-gating disable bits.
- Memory-translation and TLB paths: TLB credit fields, TLB pending bits, ATCVM clock controls, L1TLB clock controls, and `DAGB2_L1TLB_REG_RW` connect this metadata to MMHUB address translation behavior.
- Performance and diagnostics: DAGB2 performance counter fields support selectable counter windows and triggered measurement. FIFO/credit fullness, pending bitmaps, and fatal-error status fields support hang analysis and low-level debug dumps.
- Error handling and RAS-like reporting: fatal-error control, clear, and status fields allow consumer code to filter errors, clear latches, and decode client, address, tag, VF/VFID, access type, operation, and response flags.
- Virtualization and isolation: fields such as `VFID`, `VF`, GPU snoop override/value, per-client controls, and virtual-channel mappings are relevant to SR-IOV or multi-client isolation paths.

## Risks And Edge Cases

- The chunk boundary is artificial. It begins after the first part of `DAGB2_WR_OUTPUT_DAGB_MAX_BURST` and ends after `DAGB3_FATAL_ERROR_STATUS3`, so adjacent chunks are required for the complete file-level picture.
- Header/offset mismatch is the main correctness risk. These masks can compile with the wrong generation's offset header but program or decode the wrong bits on hardware.
- Repeated client and VC groups are easy to copy incorrectly. Client 0-7 and 8-15 fields use separate registers, and read/write/address/data variants look nearly identical while targeting different hardware paths.
- Full-width pending and snoop masks do not mean arbitrary writes are safe. Some registers are status bitmaps, some are override controls, and consumer code must know the hardware access semantics.
- Credit and bandwidth fields can affect liveness. Incorrect TLB, return, OSD, atomic, GMI, or pool credits can create throttling, starvation, deadlock, or hangs under memory pressure.
- Clock-gating and light-sleep override fields can interact with active traffic, reset, and firmware-owned sequences. Writes may require block idle state or prescribed ordering not visible in this header.
- Fatal-error status fields are decoders, not policy. Error latches may require clear sequencing, and address/tag/VF fields may be invalid unless `VALID` is set.
- Reserved registers and reserve masks should generally be preserved during read-modify-write unless the hardware programming guide requires a full-register write.

## Test Signals

Useful validation signals include:

- Build coverage for AMDGPU sources that include MMHUB 1.7 offset and mask headers.
- Static generated-header checks that every field has matching `__SHIFT` and `_MASK` definitions, masks align with shifts, and repeated DAGB2/DAGB3 register families are complete.
- Cross-checks against the companion MMHUB 1.7 offset header so every `DAGB2_*` and `DAGB3_*` register named here has a matching register address where expected.
- Hardware bring-up on MMHUB 1.7 ASICs, confirming MMHUB initialization, memory translation, rings, VM faults, reset recovery, suspend/resume, and clock-gating transitions are stable.
- Stress tests that exercise high memory traffic, concurrent read/write clients, TLB pressure, atomics, virtualization/VF traffic, and bandwidth-limit settings without hangs or starvation.
- Debug and hang-dump tests that read pending, FIFO, credit, performance counter, and fatal-error status registers and decode fields consistently.
- Error-injection or fault-path tests, where available, that verify fatal-error valid/client/address/tag/VF/operation fields and clear behavior.
