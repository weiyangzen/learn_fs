# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/uncore-interconnect.json lines 11745-16792

## Chunk Scope

This chunk covers lines 11745-16792 of the Ice Lake Xeon `uncore-interconnect.json` PMU event catalog. It is a data-only slice of a larger JSON array, not executable code. The slice contains 466 event objects: 418 for the `M3UPI` unit and 49 for the `UPI` unit, with one event object beginning before this chunk boundary. Most entries are marked `"Experimental": "1"` and `"PerPkg": "1"`, meaning the generated perf events are model-specific uncore package events rather than per-core counters.

## Purpose

The chunk describes hardware event encodings for Ice Lake server uncore interconnect monitoring. These rows let perf expose named events for UPI/M3UPI traffic, queueing, arbitration, credit pressure, ring activity, writeback routing, and link power states. Users consume the names through `perf list`, `perf stat -e <event>`, JSON output from `perf list --details`, and generated PMU lookup tables.

The data is intended to preserve Intel PMU semantics in a machine-readable form:

- `EventName` gives the stable perf-visible symbolic name, often with a suffix variant such as `.AD_REQ`, `.BL_WB`, `.TGR0`, or `.UP_EVEN`.
- `EventCode` and `UMask` encode the raw PMU selector bits.
- `Counter` constrains which programmable counters can count the event.
- `Unit` maps the event to the uncore PMU block, mainly `M3UPI` in this range and then `UPI` near the end.
- `BriefDescription` and `PublicDescription` provide short and long user-facing text for generated event tables.

## Data Model and Important Fields

Every event object in this chunk follows the perf PMU JSON schema consumed by `tools/perf/pmu-events/jevents.py`. There are no local functions, classes, or runtime state in this file; the important "APIs" are the JSON keys that the generator recognizes.

Key fields visible here:

- `EventName`: required for named hardware events. `jevents.py` lowercases this name when building generated tables, so case and uniqueness still matter for source review.
- `EventCode`: hexadecimal hardware event selector. Several families share one selector and vary by `UMask`.
- `UMask`: hexadecimal sub-selector, commonly one bit per channel/message-class variant. A missing `UMask` is valid for some base events such as clockticks and power-state cycle counters.
- `Counter`: comma-separated allowed counter indexes. Most `M3UPI` entries use `0,1,2,3`, but some packing events use `0,1,2` and earlier chunk context shows other units may use narrower masks.
- `Unit`: uncore PMU namespace. The generator uses this to associate events with PMU names and runtime PMU matching.
- `BriefDescription` and `PublicDescription`: copied into generated descriptions. `PublicDescription` is absent for some terse events, in which case perf tests and generated output rely on the brief text.
- `Experimental` and `PerPkg`: metadata flags affecting presentation and interpretation; `PerPkg` tells users these events are package scoped.

## Event Families in This Chunk

The first part continues `UNC_M3UPI_RxC_OCCUPANCY_VN1`, covering VN1 ingress occupancy variants by AD/BL message class. The chunk then describes receive credit and packing behavior:

- `UNC_M3UPI_RxC_PACKING_MISS_VN0` and `UNC_M3UPI_RxC_PACKING_MISS_VN1` count cases where ingress had packets available but failed to pack them into a flit slot.
- `UNC_M3UPI_RxC_VNA_CRD` and `UNC_M3UPI_RxC_VNA_CRD_MISC` expose remote VNA credit levels, corrected credits, and allocation restrictions across VN0/VN1 and AD/BL.
- `UNC_M3UPI_RxR_OCCUPANCY`, `UNC_M3UPI_RxR_INSERTS`, `UNC_M3UPI_RxR_BYPASS`, `UNC_M3UPI_RxR_CRD_STARVED`, and `UNC_M3UPI_RxR_BUSY_STARVED` describe transgress ingress queues, allocations, bypasses, and starvation on AD, AK, AKC, BL, IFV, and IV classes.

The middle of the slice is dominated by M3UPI transmit/ring pressure:

- `UNC_M3UPI_STALL0_NO_TxR_HORZ_CRD_*` and `UNC_M3UPI_STALL1_NO_TxR_HORZ_CRD_*` count stalls from missing horizontal transgress credits for AD/BL, agent 0/1, and transgress indexes.
- `UNC_M3UPI_TxC_AD_*`, `UNC_M3UPI_TxC_AK_*`, `UNC_M3UPI_TxC_BL_*`, and `UNC_M3UPI_TxC_BL_WB_FLQ_OCCUPANCY` cover flit queue bypass, not-empty cycles, inserts, occupancy, and arbitration failures on AD/AK/BL egress paths.
- `UNC_M3UPI_TxR_HORZ_*` covers horizontal transgress ADS usage, bypass, full/not-empty cycles, inserts, NACKs, occupancy, and starvation.
- `UNC_M3UPI_TxR_VERT_*` mirrors much of the same behavior for vertical rings, split into numbered ring groups and variants such as AD, AK, AKC, BL, IV, IFV, and TGC.
- `UNC_M3UPI_VERT_RING_*_IN_USE` gives direct in-use counters for AD, AKC, AK, BL, IV, and TGC vertical ring directions/parities.

The later M3UPI entries track peer credits and writeback routing:

- `UNC_M3UPI_UPI_PEER_AD_CREDITS_EMPTY` and `UNC_M3UPI_UPI_PEER_BL_CREDITS_EMPTY` identify when peer credits are empty for request/response/snoop/non-coherent/writeback classes.
- `UNC_M3UPI_VN0_CREDITS_USED`, `UNC_M3UPI_VN1_CREDITS_USED`, `UNC_M3UPI_VN0_NO_CREDITS`, and `UNC_M3UPI_VN1_NO_CREDITS` expose VN-level credit usage and no-credit conditions by traffic type.
- `UNC_M3UPI_WB_PENDING` and `UNC_M3UPI_WB_OCC_COMPARE` describe writeback pending state and local-destination versus route-through occupancy comparisons for VN0/VN1.
- `UNC_M3UPI_XPT_PFTCH` and `UNC_M3UPI_UPI_PREFETCH_SPAWN` expose prefetch-related arbitration, arrival, bypass, flitting, and loss conditions.

The final section starts the `UPI` unit:

- `UNC_UPI_CLOCKTICKS` gives the UPI clock baseline.
- `UNC_UPI_DIRECT_ATTEMPTS` counts direct packet attempts for D2C and D2K.
- `UNC_UPI_FLOWQ_NO_VNA_CRD`, `UNC_UPI_M3_BYP_BLOCKED`, `UNC_UPI_M3_RXQ_BLOCKED`, and `UNC_UPI_M3_CRD_RETURN_BLOCKED` expose flow queue, bypass, receive queue, and credit-return blocking causes.
- `UNC_UPI_L1_POWER_CYCLES`, `UNC_UPI_PHY_INIT_CYCLES`, `UNC_UPI_POWER_L1_REQ`, `UNC_UPI_POWER_L1_NACK`, `UNC_UPI_RxL0_POWER_CYCLES`, and `UNC_UPI_RxL0P_POWER_CYCLES` describe link-layer/PHY power-state residency and transitions.
- `UNC_UPI_REQ_SLOT2_FROM_M3` counts request slot-2 classes arriving from M3.
- `UNC_UPI_RxL_BASIC_HDR_MATCH` starts a header match family for received UPI packets, with class and opcode-match variants for NCB, NCS, request, response, snoop, and writeback traffic. The family continues after this chunk.

## Control Flow and Integration

There is no direct control flow in this JSON file. The effective flow is build-time:

1. `tools/perf/pmu-events/Build` includes the architecture JSON tree in the generated PMU event build.
2. `tools/perf/pmu-events/jevents.py` reads event JSON objects, normalizes descriptions and event names, and emits generated C tables in `pmu-events.c`.
3. The generated tables are included by perf PMU lookup code through `pmu-events/pmu-events.h`.
4. Runtime consumers such as `perf list`, `perf stat`, `util/pmu.c`, `builtin-list.c`, and Python bindings surface the generated names, encodings, and descriptions.
5. Tests under `tools/perf/tests/pmu-events.c` compare generated table entries against expected JSON-derived fields.

Because this is a chunk of one large array, the chunk boundaries do not align with semantic families. The opening event is a continuation of an object/family started before line 11745, and the final `UNC_UPI_RxL_BASIC_HDR_MATCH` family continues after line 16792.

## State and Persistence

The persistent state is the checked-in JSON event catalog. At build time, the catalog is transformed into generated C data. At runtime, perf does not mutate this file; it reads generated event tables and programs hardware PMU selectors based on `EventCode`, `UMask`, PMU unit, counter constraints, and other generated metadata.

Statefulness relevant to users is hardware-side:

- Occupancy events accumulate queue occupancy over cycles and require pairing with not-empty or allocation events to derive average occupancy or latency.
- Credit events represent instantaneous or per-cycle credit pressure conditions.
- Power events count cycles in, entering, or failing to enter UPI link power states.
- Per-package uncore events should be interpreted across sockets/packages and UPI links, not as thread-local measurements.

## Dependencies

This data depends on:

- The perf PMU JSON schema implemented by `pmu-events/jevents.py`.
- Ice Lake Xeon uncore PMU hardware definitions for `M3UPI` and `UPI`.
- The x86 model mapping that selects the `icelakex` event directory for the running CPU.
- Runtime sysfs PMU exposure for matching uncore PMU instances and supported counters.
- Description handling in `builtin-list.c`, `util/python.c`, and test code that expects `BriefDescription`/`PublicDescription` fields to be well-formed strings.

## Risks and Review Notes

- A malformed JSON object anywhere in the large source file can break PMU event generation for the whole model. This chunk begins and ends mid-array, so validation must be done on the complete file.
- Event-name uniqueness is critical. Families here reuse `EventCode` heavily and rely on distinct `UMask` and suffix names to remain distinguishable.
- Several entries have terse `BriefDescription` values that are just the event name, and some lack `PublicDescription`. That is valid but reduces `perf list` usability and can hide semantic mistakes.
- Many descriptions describe derived analysis relationships, such as occupancy plus not-empty or allocations. If companion events live in other chunks, merged documentation should preserve those cross-chunk links.
- The chunk shows one lowercase selector spelling, `0xe4`, while most event codes use uppercase hex digits. Numeric parsing should tolerate this, but reviewers should avoid accidental string-based normalization regressions.
- Some families have suffixes ending in `_1` or numbered ring groups, likely to avoid name collisions or represent hardware ring instances. These should not be "cleaned up" without checking Intel source data and generated table uniqueness.
- `Counter` constraints vary by family. Broadening them in JSON would make perf advertise invalid measurements; narrowing them would make valid events unavailable.
- Most rows are experimental, so user-facing output should make that status visible and tests should not assume stable behavior across CPU steppings without hardware confirmation.

## Test Signals

Useful validation signals for this chunk are:

- Parse the full `uncore-interconnect.json` with a strict JSON parser to catch commas, unterminated strings, and mid-array damage.
- Run the perf PMU event generation path for x86/icelakex and confirm `pmu-events.c` builds.
- Run `tools/perf/tests/pmu-events.c`-backed tests, which verify generated event fields against JSON-derived expectations.
- Use `perf list --details` on an Ice Lake Xeon system and spot-check representative names from this chunk, such as `UNC_M3UPI_RxC_VNA_CRD.LT10`, `UNC_M3UPI_TxR_HORZ_OCCUPANCY.AD_ALL`, `UNC_UPI_POWER_L1_REQ`, and `UNC_UPI_RxL_BASIC_HDR_MATCH.REQ_OPC`.
- For runtime confidence, compare raw event encodings emitted by perf for a few names against the JSON `EventCode` and `UMask` values.
- For semantic confidence, use paired measurements described in `PublicDescription`, such as occupancy with not-empty/allocation events, to check that derived averages are plausible under known UPI traffic.

## Unresolved Cross-Chunk References

The chunk references companion events outside this exact range:

- The first visible event belongs to the `UNC_M3UPI_RxC_OCCUPANCY_VN1` family that started before line 11745.
- Occupancy descriptions mention not-empty and allocation events that may appear in earlier chunks.
- The `UNC_UPI_RxL_BASIC_HDR_MATCH` family continues after line 16792 with additional receive-header variants.
- The final merged file report should reconcile these partial-family boundaries and summarize the whole `uncore-interconnect.json` source, not just this slice.
