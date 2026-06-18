# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_7_sh_mask.h lines 7077-9435

## Purpose

This chunk is generated AMD MMHUB 1.7 register bitfield metadata. It defines `__SHIFT` and `_MASK` preprocessor macros for the tail of `DAGB3`, all of `mmhub_dagb_dagbdec4` (`DAGB4`), and the beginning of `mmhub_dagb_dagbdec5` (`DAGB5`). The macros describe how AMDGPU code packs and decodes fields in Data Address Generation Block registers for MMHUB traffic routing, bandwidth throttling, virtual-channel arbitration, TLB/credit accounting, clock gating, pending-status observation, fatal-error reporting, and performance counters.

Although this path sits under a Ceph-client source tree mirror, the file is Linux AMD GPU driver hardware metadata. It contains no Ceph filesystem logic, no executable code, and no runtime storage by itself.

The covered range includes:

- `DAGB3_FATAL_ERROR_STATUS3`, FIFO/credit-full indicators, perf counter controls/results, L1 TLB register read/write controls, and reserve registers. The previous chunk contains the earlier `DAGB3` field definitions, so this range begins mid-register-family.
- The complete `DAGB4` address block: read clients `RDCLI0..15`, read control/credit/VC registers, write clients `WRCLI0..15`, write control/credit/data/atomic/OSD registers, snoop override fields, pending-status registers, delay/control/miscellaneous registers, fatal-error status/clear/control registers, FIFO/credit fullness indicators, perf counters, L1TLB control, and reserved registers.
- The start of `DAGB5`: read clients `RDCLI0..15`, read bandwidth/GMI/DAGB controls, output max-burst/lazy-timer fields, read-side CGTT clock controls, L1TLB/ATCVM read clock controls, and the first `RD_ADDR_DAGB_MAX_BURST0` client fields. The next chunk is required for the rest of `DAGB5`.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, callbacks, locks, allocations, or direct MMIO operations in this chunk. Its interface is the generated macro namespace consumed by AMDGPU register helpers:

- `DAGB<n>_<REGISTER>__<FIELD>__SHIFT` gives the bit position for a field.
- `DAGB<n>_<REGISTER>__<FIELD>_MASK` gives the 32-bit mask for the same field.
- These macros pair with `regDAGB*` offsets from `mmhub_1_7_offset.h` and are normally used through `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_FIELD`, direct mask operations, and SOC15 read/write helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_SOC15_OFFSET`, and `WREG32_SOC15_OFFSET`.

High-signal register families in this range are:

- `RDCLI0..15` and `WRCLI0..15`: per-client read/write routing and QoS fields. Each client exposes `VIRT_CHAN`, `CHECK_TLB_CREDIT`, `URG_HIGH`, `URG_LOW`, `MAX_BW_ENABLE`, `MAX_BW`, `MIN_BW_ENABLE`, `MIN_BW`, `OSD_LIMITER_ENABLE`, and `MAX_OSD`.
- Read and write global controls: `RD_CNTL`/`WR_CNTL` contain `SCLK_FREQ`, bandwidth windows, IO-level override/comply fields, shared VC count, and jump behavior. `RD_GMI_CNTL`/`WR_GMI_CNTL` carry EA credit, level, burst, and lazy-timer fields.
- DAGB routing controls: `RD_ADDR_DAGB`, `WR_ADDR_DAGB`, and `WR_DATA_DAGB` describe enable, jump-ahead, self-init disable, `WHOAMI`, and jump-mode style controls.
- Per-output and per-client burst/timer arrays: `*_OUTPUT_DAGB_MAX_BURST`, `*_OUTPUT_DAGB_LAZY_TIMER`, `*_ADDR_DAGB_MAX_BURST0/1`, `*_ADDR_DAGB_LAZY_TIMER0/1`, and write-data equivalents encode compact 4-bit fields for VCs or client slots.
- Virtual-channel controls: `RD_VC0..7_CNTL` and `WR_VC0..7_CNTL` define per-VC EA/storage credits, bandwidth limits, OSD limiter enable, and max OSD.
- Credit controls and status: `RD_TLB_CREDIT`, `WR_TLB_CREDIT`, `RD_RDRET_CREDIT_CNTL`, `RD_RDRET_CREDIT_CNTL2`, `WR_DATA_CREDIT`, `WR_MISC_CREDIT`, `WR_OSD_CREDIT_CNTL1/2`, `WR_ATOMIC_FIFO_CREDIT_CNTL1`, `WR_CREDITS_FULL`, and `RD_CREDITS_FULL`.
- Pending and fullness indicators: `RDCLI_*_PENDING`, `WRCLI_*_PENDING`, DBUS pending status, `FIFO_EMPTY`, and `FIFO_FULL` expose busy/full bitmaps used for diagnostics and drain checks.
- Clock and light-sleep controls: `RD_CGTT_CLK_CTRL`, `WR_CGTT_CLK_CTRL`, `L1TLB_*_CGTT_CLK_CTRL`, and `ATCVM_*_CGTT_CLK_CTRL` define on-delay, off-hysteresis, soft-stall override, and light-sleep override bits for write/read/return/register paths.
- Error and debug/observability: `FATAL_ERROR_CNTL`, `FATAL_ERROR_CLEAR`, `FATAL_ERROR_STATUS0..3`, `DAGB_DLY`, `CNTL_MISC`, `CNTL_MISC2`, `PERFCOUNTER_LO`, `PERFCOUNTER_HI`, `PERFCOUNTER0..2_CFG`, and `PERFCOUNTER_RSLT_CNTL`.
- Snoop override fields: `WRCLI_GPU_SNOOP_OVERRIDE` and `WRCLI_GPU_SNOOP_OVERRIDE_VALUE` expose enable bitmaps for write clients. `mmhub_v1_7.c` programs these by offset stride to enable SDMA snoop behavior across DAGB instances.

## Control Flow

This header chunk has no runtime control flow. Its behavior is entirely through C preprocessing and later MMIO operations in consumer code.

Typical consumer flow is:

1. MMHUB 1.7 driver code includes `mmhub_1_7_offset.h` and `mmhub_1_7_sh_mask.h`.
2. Code selects a register offset such as `regDAGB0_WRCLI_GPU_SNOOP_OVERRIDE`, `regDAGB4_WR_CNTL`, or another `regDAGB*` macro from the offset header.
3. Code uses a mask/shift macro from this header through `REG_SET_FIELD`, `REG_GET_FIELD`, or direct mask arithmetic to build or decode the 32-bit register value.
4. SOC15 helpers perform the actual MMIO read/write against the selected MMHUB instance.

The visible MMHUB 1.7 consumer in this tree is `amdgpu/mmhub_v1_7.c`. Most of that file programs VM hub, TLB, cache, GART aperture, invalidation, and RAS fields from other sections of this header, while DAGB integration appears in two important places:

- `mmhub_v1_7_init_snoop_override_regs()` computes the per-DAGB register stride from `regDAGB1_WRCLI_GPU_SNOOP_OVERRIDE - regDAGB0_WRCLI_GPU_SNOOP_OVERRIDE`, iterates five DAGB instances, and sets bit 15 in both `WRCLI_GPU_SNOOP_OVERRIDE` and `WRCLI_GPU_SNOOP_OVERRIDE_VALUE` so SDMA writes probe/invalidate cached RW lines.
- `mmhub_v1_7_update_medium_grain_clock_gating()` and `mmhub_v1_7_get_clockgating()` use `DAGB0_CNTL_MISC2` and `DAGB1_CNTL_MISC2` masks from earlier chunks to control/read DAGB clock-gating state. The `DAGB4_CNTL_MISC2` masks in this chunk follow the same generated field pattern for later instances even though this specific driver code only names DAGB0/1 directly.

The header does not encode safe access ordering, reset sequencing, drain loops, read side effects, sticky status clearing rules, or privilege/SR-IOV ownership. Those rules live in the MMHUB driver, SOC15 accessors, firmware expectations, and hardware specification.

## State And Persistence Behavior

This file stores no software state. The macros describe fields in MMHUB hardware registers whose persistence is hardware-defined.

The represented hardware state includes:

- Persistent configuration until reset or reprogramming: client-to-virtual-channel mapping, urgency thresholds, bandwidth windows, max/min bandwidth enforcement, OSD limits, EA/storage credits, GMI burst/lazy timing, DAGB enable/jump routing, client and VC burst settings, snoop override enable/value bits, and clock-gating/light-sleep override controls.
- Live status and diagnostic state: pending client bitmaps, FIFO empty/full bitmaps, read/write credit-full indicators, TLB/data/misc credit state, and performance counter low/high result registers.
- Error state: fatal-error status registers carry address high bits, request ID, source ID, client ID, VMID/VFID, tag, opcode, VF/space/IO/size/FED indicators, snoop/invalid/NACK/RO/MEMLOG/EOP style qualifiers, plus explicit clear/control fields.
- Reserved fields/registers: `RESERVE*` and explicit `RESERVE` masks are generated placeholders. They should not be treated as available driver-owned state.

Some fields are configuration knobs that persist across normal operation; others are counters, latches, status bitmaps, or write-trigger/clear bits. This header does not distinguish read-only, write-one-to-clear, sticky, or firmware-owned fields beyond macro names.

## Dependencies

This chunk depends on the AMDGPU SOC15 register stack and sibling generated MMHUB metadata:

- `mmhub_1_7_offset.h` supplies matching `regDAGB*` register offsets and base indices.
- Earlier and later chunks of `mmhub_1_7_sh_mask.h` complete the `DAGB3` and `DAGB5` field definitions and provide the rest of MMHUB 1.7 VM, ATC, MMEA, and DAGB masks.
- `amdgpu/mmhub_v1_7.c`, `soc15.h`, and `soc15_common.h` provide the runtime MMIO helpers and field manipulation macros that make these constants operational.
- Cross-generation MMHUB drivers such as `mmhub_v1_8.c` and `mmhub_v9_4.c` use closely related DAGB patterns, but offsets, instance counts, and field availability can differ.

The generated field names must stay synchronized with the offset header and with any code that computes register stride across DAGB instances. Because `DAGB4` is one of several repeated blocks, small differences in naming, spacing, or masks can break looped access patterns that start from `DAGB0` and stride across instances.

## Integration Points

Primary integration points are:

- MMHUB initialization and GART setup: `mmhub_v1_7.c` includes this header for MMHUB register field packing during VM, TLB, cache, aperture, invalidation, and fault-control setup.
- SDMA coherency/snoop setup: `mmhub_v1_7_init_snoop_override_regs()` writes the DAGB write-client snoop override registers across five DAGB instances. The `DAGB4_WRCLI_GPU_SNOOP_OVERRIDE*` masks in this chunk describe the final instance reached by that loop.
- Power management and clock gating: DAGB `CNTL_MISC2` and `*_CGTT_CLK_CTRL` fields integrate with medium-grain clock gating and light-sleep behavior. Incorrect masks can leave request, return, TLB, or register subpaths ungated or over-gated.
- Performance/debug tooling: `PERFCOUNTER*`, `FIFO_*`, pending, credit, and fatal-error fields are observability hooks for debugging MMHUB stalls, under-crediting, bandwidth throttling, and fatal transaction errors.
- RAS and fault handling: fatal-error status fields overlap conceptually with the broader AMD RAS path and error interrupt reporting. This chunk provides decode fields, while higher-level RAS event handling lives outside the header.
- Hardware generation tables: the file is part of the MMHUB 1.7 generated register contract and is consumed alongside other generated ASIC register headers under `include/asic_reg`.

## Risks And Edge Cases

- Chunk boundaries are artificial. This range starts mid-`DAGB3` and ends mid-`DAGB5`; reviewing it alone is insufficient for a complete per-instance DAGB model.
- `DAGB4` contains many repeated per-client and per-VC fields. Copy/paste or generator errors can compile cleanly while shifting one client or VC into the wrong nibble.
- Snoop override handling is instance-stride-sensitive. `mmhub_v1_7.c` computes a distance from `DAGB0` to `DAGB1` and applies it across five instances; offset/header mismatches can silently program the wrong DAGB instance or wrong register.
- Many fields influence memory-system QoS and coherency. Bad `VIRT_CHAN`, credit, bandwidth, OSD, burst, or lazy-timer masks can produce stalls, unfair arbitration, performance cliffs, or ordering/coherency bugs.
- Clock-gating and light-sleep override fields affect live MMHUB datapaths. Overly broad masks can stall read/write/return/register paths; under-broad masks can prevent intended power savings.
- Fatal-error clear/control fields should not be treated as ordinary status. Writes can clear latched error evidence or change fatal-error filtering.
- Reserved masks are full-width or high-bit placeholders in several registers. Driver code should avoid relying on reserved fields unless directed by an authoritative hardware programming guide.
- Cross-generation similarity is risky. MMHUB 1.7, 1.8, and 9.4 DAGB names are similar, but masks and instance behavior should not be assumed interchangeable.

## Test Signals

Useful validation signals include:

- Build coverage for `amdgpu/mmhub_v1_7.c` and any code including `mmhub_1_7_sh_mask.h`, ensuring all `DAGB*` field names referenced by consumers remain available.
- Generated-header consistency checks that every `DAGB4` and covered `DAGB5` field has both `__SHIFT` and `_MASK` forms and matches the register names in `mmhub_1_7_offset.h`.
- Static checks for repeated field layout consistency across `DAGB0..DAGB5`, especially `RDCLI/WRCLI`, `RD_VC/WR_VC`, `*_MAX_BURST`, `*_LAZY_TIMER`, pending, credit, and `CNTL_MISC2` families.
- Hardware boot smoke tests on MMHUB 1.7 ASICs covering GART enable, VM context setup, SDMA writes, cache coherency, suspend/resume, and SR-IOV VF paths.
- Coherency tests that exercise SDMA write snoop override behavior, looking for stale cache lines, missed probe invalidations, or data corruption.
- Stress tests for GPUVM memory traffic under mixed SDMA/display/media clients to expose DAGB credit, OSD, virtual-channel, and bandwidth-window mistakes.
- Power-management tests for medium-grain clock gating and light sleep, watching for MMHUB hangs, unexpected register-access timeouts, or missing power-state transitions.
- Diagnostic/RAS tests that read fatal-error, FIFO, pending, credit, and perf-counter registers and verify fields decode consistently with hardware events.
- Regression indicators include VM fault storms, SDMA coherency failures, MMHUB register access timeouts, GART enable failures, display/media traffic stalls, unexpected fatal-error interrupts, or power-gating instability after changing generated masks.
