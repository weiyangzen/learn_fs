# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_sh_mask.h lines 35539-37903

## Scope And Purpose

This chunk is a generated AMD MMHUB 9.4.1 shift/mask register header slice for the MMEA6 memory-engine/address-decoder block. It contains preprocessor constants that describe bit positions and bit masks for fields in MMEA6 DRAM, GMI, IO, address-normalization, address-decoder, and SDP arbitration registers.

The source file has no executable code. Its purpose is to provide the field layout contract used by AMDGPU register helpers when they construct, extract, or update MMHUB register values. This header is paired with `mmhub_9_4_1_offset.h`, which defines register offsets, and `mmhub_9_4_1_default.h`, which defines reset/default values for the same register names.

The requested range contains 2,167 `#define` entries: 1,082 `__SHIFT` constants and 1,085 `_MASK` constants. The count is not exactly paired because the range begins inside the tail of `MMEA6_DRAM_WR_CAM_CNTL` and ends inside the beginning of `MMEA6_SDP_VCC_RESERVE0`. This partial-boundary behavior matters for reconciliation with adjacent chunks.

## Register Families Covered

The first lines complete the `MMEA6_DRAM_WR_CAM_CNTL` field layout started before this chunk. The covered fields include reorder-limit shifts, refill-chain shift, CAM depth masks for groups 0-3, reorder-limit masks for groups 0-3, and the refill-chain mask. The matching `MMEA6_DRAM_RD_CAM_CNTL` layout is immediately before this slice.

The DRAM arbitration section defines `MMEA6_DRAM_PAGE_BURST`, read/write priority aging, queuing, fixed priority, urgency, and three priority quantum registers for read and write traffic. These fields encode per-group coefficients, thresholds, burst limits, and urgency modes for four traffic groups.

The GMI arbitration section defines read/write client-to-group maps, group-to-virtual-channel maps, lazy request accumulation, CAM controls, page-burst controls, age/queue/fixed/urgency priority controls, urgency masking, and priority quantum registers. GMI maps split client IDs 0-31 across two map registers per read/write direction, with 2-bit group fields for each client. Urgency masking uses 32 single-bit client masks per read/write direction.

The address-normalization section defines `MMEA6_ADDRNORM_BASE_ADDR0..5`, `LIMIT_ADDR0..5`, and `OFFSET_ADDR1/3/5`, plus DRAM/GMI hole controls, non-power-of-two channel configuration, and global controls. Base registers expose base, interleave, crop, hole-mode, channel, fine-grain channel, and hash fields; limit/offset registers expose narrower address boundary fields.

The address-decoder section defines bank configuration, miscellaneous address decoder controls, DRAM and GMI address-hash controls, DRAM and GMI harvest-enable controls, and three repeated chip-select decoder instances: `ADDRDEC0`, `ADDRDEC1`, and `ADDRDEC2`. Each decoder has base addresses for CS0-CS3 and secondary CS0-CS3, address masks, address configuration, address selection, column-selection low/high registers, and rank-mapping selection registers.

The IO arbitration section defines read/write client-to-group maps, read/write combine flush controls, group-burst controls, age/queue/fixed/urgency priority controls, urgency masking, and priority quantum registers. Like GMI, the client maps cover client IDs 0-31 with 2-bit group selectors, while urgency masking has one mask bit per client.

The SDP section begins the System Data Path arbitration and credit layout. This chunk fully covers DRAM and GMI arbitration controls, final arbitration controls, DRAM/GMI/IO priority controls, tag/response credit limits, tag reservation for VC0-VC7, and the opening shifts for `MMEA6_SDP_VCC_RESERVE0`. The `MMEA6_SDP_VCC_RESERVE0` masks and subsequent SDP reserve/request/misc fields continue after the requested range.

## Important APIs, Types, Functions, And Macros

There are no C APIs, structs, enums, functions, or inline helpers in this chunk. The entire public interface is generated macro data.

The macro naming contract is:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit index for a register field.
- `<REGISTER>__<FIELD>_MASK` gives the already-shifted bit mask for the same field.
- Multi-field registers use repeated names such as `GROUP0`, `GROUP1`, `CID0`, `CID31`, `VC0`, `CS0`, and `BANK5` to expose indexed hardware fields without C arrays.
- Macros are integer constants with an `L` suffix on masks, for example `0x000000FFL`, and plain hexadecimal values for shifts.

Important macro families in the chunk include:

- `MMEA6_DRAM_*`: DRAM-side arbitration and priority fields for read/write traffic.
- `MMEA6_GMI_*`: GMI-side client mapping, arbitration, urgency, and priority fields.
- `MMEA6_ADDRNORM*`: address-normalization window, hole, NP2-channel, and global-control fields.
- `MMEA6_ADDRDEC*`: bank, hash, harvest, chip-select, address-selection, column-selection, and rank-map fields.
- `MMEA6_IO_*`: IO-side client mapping, combine-flush, arbitration, urgency, and priority fields.
- `MMEA6_SDP_*`: SDP arbitration, priority, tag, response credit, and virtual-channel reservation fields.

Common field layouts repeat across DRAM, GMI, and IO. Priority age registers have four 3-bit aging-rate fields and four 3-bit age-coefficient fields. Queuing/fixed registers have four 3-bit group coefficients. Urgency registers have four 3-bit urgency coefficients and four one-bit urgency-mode fields. Quantum registers have four 8-bit thresholds. Page/group-burst registers pack four 8-bit read/write or group limits.

## Control Flow

This header has no runtime control flow. The implicit use flow is compile-time and register-access driven:

1. Driver code includes the generated MMHUB 9.4.1 register headers.
2. Code selects a register through offset macros from `mmhub_9_4_1_offset.h`.
3. Code constructs or decodes bitfields using the `__SHIFT` and `_MASK` constants in this file, often through AMDGPU/SOC15 helpers.
4. Hardware observes the resulting MMIO register values when the driver programs MMHUB arbitration, address decoding, VM aperture, RAS, or diagnostic state.

The chunk itself does not decide when registers are written. That behavior lives in AMDGPU MMHUB/GMC/VM initialization, power-management, virtualization, RAS, and debug paths. This file supplies the bit layout those paths must obey.

## State And Persistence Behavior

The macros are compile-time constants and do not persist runtime state. They describe persistent hardware register layout, meaning they define how software interprets and writes MMHUB state that does persist in the device until reset or reprogramming.

Arbitration-related fields persist as hardware policy after programming. DRAM, GMI, and IO group mappings, virtual-channel maps, priority coefficients, urgency modes, urgency masks, burst limits, CAM depths, reorder limits, and quantum thresholds directly influence request ordering, fairness, latency, and bandwidth distribution.

Address-normalization and address-decoder fields persist as address-routing state. Base/limit/offset windows, hole controls, channel and interleave fields, bank configuration, address hashing, harvest enable, chip-select base/mask/configuration, column-selection, and rank-map selection fields determine how MMEA6 routes physical memory requests to DRAM/GMI resources.

SDP fields persist as request/response credit and final arbitration policy. Tag limits, read/write response credits, VC tag reservations, VC credit reservations, readonly VC flags, error-event and halt-request policy, and burst-stretch controls can affect forward progress and error response behavior.

Because this slice starts and ends on partial register definitions, consumers of generated documentation should combine it with adjacent chunks before treating the full source file as completely described.

## Dependencies And Integration Points

This header depends only on the C preprocessor, but it is tightly coupled to the generated AMDGPU MMHUB register model:

- `mmhub_9_4_1_offset.h` must define matching `mmMMEA6_*` register offsets.
- `mmhub_9_4_1_default.h` must define matching `mmMMEA6_*_DEFAULT` reset values where applicable.
- AMDGPU SOC15 register helpers use field masks and shifts to isolate and modify register fields without hard-coded bit arithmetic.
- MMHUB v9.4 runtime code uses the generated register model for GPU memory controller setup, VM hub programming, TLB invalidation, protection-fault handling, RAS/EDC handling, clock/power management, and register diagnostics.
- Hardware and firmware interfaces rely on the generated register layout matching the ASIC specification exactly.

Integration is mostly name-based. If a register or field is renamed in one generated header but not the others, C compilation may fail for direct references. More dangerous drift can still compile if stale masks remain unused until a specific runtime path or debug path touches that field.

## Risks And Edge Cases

The main correctness risk is bitfield drift. A wrong shift or mask can write the wrong hardware bits while leaving nearby fields unchanged, which can produce silent misconfiguration rather than an obvious crash.

The repeated register families create generation and review risk. DRAM, GMI, and IO priority fields use similar layouts with small differences; GMI and IO client maps each enumerate 32 client IDs; DRAM/GMI hash controls and chip-select decoders repeat across multiple banks and decoder instances. A single missing or shifted field can affect only one client, VC, bank, chip-select pair, or decoder instance.

Partial chunk boundaries are a documentation risk. This range begins after the `MMEA6_DRAM_WR_CAM_CNTL` heading and ends before the rest of `MMEA6_SDP_VCC_RESERVE0`. Merge/reconciliation must avoid treating these partial blocks as complete register descriptions.

Address-decoder fields are high blast-radius. Mistakes in base, mask, chip-select, column-selection, rank-map, hash, harvest, or channel fields can route memory to the wrong slice, bank, channel, or aperture. Such bugs may appear as data corruption, GPU hangs, RAS events, or performance anomalies.

Arbitration and credit fields are performance and forward-progress sensitive. Bad CAM depths, reorder limits, urgency masks, VC maps, tag limits, or response credits can cause starvation, excessive latency, underutilization, or deadlock-like behavior under load.

The macros carry no type safety. Any code can combine a shift from one register with a mask from another if names are misused. Review and generated-header consistency checks are the primary protection.

## Test Signals

Build tests should compile AMDGPU code that includes `mmhub_9_4_1_sh_mask.h`, especially paths that reference MMEA6 register fields through SOC15 field helpers.

Generated-header validation should verify that every full register represented in this slice has a matching offset macro and, where present, a matching default macro. It should also verify that each field has a coherent shift/mask pair, except for the known partial boundary cases at `MMEA6_DRAM_WR_CAM_CNTL` and `MMEA6_SDP_VCC_RESERVE0`.

Static consistency checks can validate mask geometry: each `_MASK` should align with its corresponding `__SHIFT`, repeated fields should not overlap, and same-layout register families should have equivalent field widths unless the ASIC specification says otherwise.

Runtime smoke tests on MMHUB 9.4.1 hardware should cover GART and VM setup, MMHUB initialization, TLB invalidation, protection-fault reporting, suspend/resume, power/clock gating, and memory traffic through DRAM, GMI, and IO paths.

Stress and performance tests are important for this slice because much of it describes arbitration, priority, urgency, and credit policy. Useful signals include memory bandwidth fairness, latency under mixed read/write traffic, GMI/IO traffic behavior, and absence of hangs under high outstanding-request pressure.

RAS and diagnostic tests should read address-decoder and MMEA status paths after initialization and under injected or simulated faults. Register-dump comparisons against generated offsets/defaults/masks can catch field drift before it becomes a runtime-only failure.
