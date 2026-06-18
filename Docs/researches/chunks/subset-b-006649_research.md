# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/cascadelakex/uncore-interconnect.json lines 6281-11953

## Scope

This chunk covers a large middle section of the Cascade Lake Xeon `uncore-interconnect.json` PMU event table. The selected lines describe Intel uncore interconnect events for the `M3UPI` unit: M3 mesh-to-UPI traffic, UPI peer credits, ring usage, ring starvation, receive-control arbitration, transmit-control queues, transmit/receive ring queues, and credit accounting.

The data is declarative JSON metadata consumed by Linux perf's PMU events tooling. It does not define executable functions, classes, or runtime control flow. Each object maps a human-readable perf event name to the low-level event encoding fields that perf later exposes through generated event tables.

The range begins at a complete object for `UNC_M3UPI_M2_BL_CREDITS_EMPTY.IIO5_NCB`. It ends on line 11953 in the middle of the next `UNC_M3UPI_VN0_CREDITS_USED.NCS` object, after `PerPkg` and before that object's remaining fields. The full source file remains valid JSON, but this chunk alone has a trailing partial event that the final merge lane must reconcile with the following chunk.

## Purpose

The purpose of this chunk is to define perf-visible hardware monitoring events for the Cascade Lake Xeon M3UPI uncore block. These events let perf users measure interconnect pressure and backpressure around UPI links and mesh/ring stops, including:

- Credit exhaustion when M3UPI cannot send to M2, UPI peers, or internal TxR paths.
- Ring occupancy, cycles non-empty, cycles full, bypass, NACK, inserts, and starvation on horizontal and vertical AD/AK/BL/IV rings.
- Receive-control arbitration behavior, including lost arbitration, no-credit conditions, packing misses, slot usage, generated flits, held messages, and collisions by virtual network and message class.
- Transmit-control flow-queue occupancy, inserts, cycles non-empty, bypass, and arbitration/speculative-arbitration outcomes.
- Per-package UPI prefetch spawning and VN0 credit-use accounting.

These records are important because uncore interconnect bottlenecks often appear as credit starvation, arbitration loss, or ring occupancy rather than as CPU-core PMU events. The table gives perf enough metadata to program the corresponding uncore PMU counters and present stable symbolic event names.

## Important Schema Fields and Event Families

The event objects in this range use the standard perf JSON PMU schema:

- `EventName`: symbolic name exposed to perf, such as `UNC_M3UPI_RxC_ARB_LOST_VN0.AD_REQ`.
- `EventCode`: hardware event selector, expressed as a hex string.
- `UMask`: unit mask selecting a subcondition or message class; most entries have one, but some base events do not.
- `BriefDescription`: short user-facing summary.
- `PublicDescription`: longer explanation where available. In this chunk, 483 of the 520 `EventName` records have one.
- `Counter`: allowed programmable counters, consistently `0,1,2` for complete events in this chunk.
- `Unit`: `M3UPI` for complete records in this range.
- `PerPkg`: `1`, marking package-scoped uncore events rather than per-core events.
- `Experimental`: present on almost all complete entries, indicating many of these events are not part of perf's most stable event surface.

The chunk contains 520 `EventName` lines. Because of the trailing partial object, only 519 `Unit` lines fall inside the requested range. The complete events are all `M3UPI`.

Major families covered here include:

- `UNC_M3UPI_M2_BL_CREDITS_EMPTY`: the tail of the M2 BL credit-empty group, covering `IIO5_NCB`, aggregate `NCS`, and selected `NCS_SEL`.
- `UNC_M3UPI_MULTI_SLOT_RCVD`: multi-slot flit receive accounting for AD, AK, and BL slots.
- `UNC_M3UPI_RING_BOUNCES_*`, `RING_SINK_STARVED_*`, and `RING_SRC_THRTL`: vertical/horizontal ring bounce and starvation conditions by AD/AK/BL/IV message ring.
- `UNC_M3UPI_RxC_*`: the largest group in this chunk, covering receive-control arbitration, no-credit states, no-AD-request states, occupancy, inserts, collisions, packing misses, VNA credit accounting, generated/sent/not-sent flits, SMI3 prefetch handling, and bypass/held conditions.
- `UNC_M3UPI_RxR_*`: receive-ring queue occupancy, inserts, bypass, busy-starved, credit-starved, and related queue pressure.
- `UNC_M3UPI_STALL_NO_TxR_*`: stalls caused by missing TxR horizontal or vertical credits, split by AD/BL, agent 0/1, and virtual network or message class.
- `UNC_M3UPI_TxC_*`: transmit-control AD/BL flow-queue metrics and arbitration/speculative-arbitration failure or success conditions.
- `UNC_M3UPI_TxR_*`: transmit-ring horizontal and vertical queue metrics, including occupancy, inserts, cycles non-empty/full, bypass, NACK, starved, and ADS-used variants.
- `UNC_M3UPI_UPI_PEER_*_CREDITS_EMPTY`: UPI peer AD/BL credit-empty states split across VNA, VN0, VN1, and AD/BL message classes.
- `UNC_M3UPI_VERT_RING_*_IN_USE`: vertical AD/AK/BL/IV ring-in-use cycle counts split by up/down and even/odd rings where applicable.
- `UNC_M3UPI_UPI_PREFETCH_SPAWN` and `UNC_M3UPI_VN0_CREDITS_USED`: prefetch generation and the start of VN0 credit-use accounting.

The common message-class suffixes are `AD_REQ`, `AD_SNP`, `AD_RSP`, `BL_RSP`, `BL_WB`, `BL_NCB`, and `BL_NCS`. The common virtual-network suffixes are `VN0`, `VN1`, and `VNA`. Ring direction and topology suffixes include `HORZ`, `VERT`, `UP`, `DN`, `EVEN`, and `ODD`; agent-specific variants use `AG0` and `AG1`.

## Control Flow

There is no local control flow in this JSON file. The effective flow is created by perf's PMU-event build and lookup pipeline:

1. The perf build scripts read architecture-specific JSON files under `tools/perf/pmu-events/arch/x86/`.
2. The JSON records are converted into generated C tables used by perf's event lookup code.
3. At runtime, a user names an event, or perf lists available events for a matching CPU model.
4. Perf resolves `EventName` to the table entry for the detected Cascade Lake Xeon model.
5. Perf programs the uncore PMU using `EventCode`, `UMask`, and counter/unit constraints.
6. The kernel/perf uncore PMU driver reads the package-level M3UPI counter values and reports them to the user.

Within this chunk, many records share an `EventCode` and differ only by `UMask`. For example, ring-in-use events use the same event selector for a ring type and use masks to select up/down/even/odd direction, while RxC arbitration families use a shared selector and masks for AD/BL message classes. This grouping means the logical control path is table-driven: perf does not branch on these names directly; it selects the encoded event programmed into the PMU.

## State and Persistence Behavior

The persistent state is the checked-in JSON metadata. The file does not mutate state, allocate memory, perform I/O, or persist runtime data. Its contents are transformed at build time into perf event tables, and those generated tables become the runtime source of truth for symbolic event lookup.

The event data is package-scoped through `PerPkg: "1"`. Counters are constrained to `0,1,2`, so users and tools must treat these as limited uncore resources. Combining many M3UPI events in one perf command can fail or multiplex if the uncore PMU cannot schedule all requested events on the allowed counters.

Most records are marked `Experimental: "1"`. That flag is part of the metadata state exposed to tooling and documentation, and it signals that names or descriptions may be less stable than architecturally documented core events. Downstream consumers should avoid assuming these event names are portable across CPU generations, even though the JSON lives under the `cascadelakex` model directory.

The trailing object at the chunk boundary is a persistence hazard for chunk-level review only. Lines 11948-11953 start `UNC_M3UPI_VN0_CREDITS_USED.NCS` but omit the rest of that JSON object in this slice. The final per-file report should treat the event as complete only after merging with the following chunk.

## Dependencies and Integration Points

This file integrates with Linux perf's PMU events infrastructure rather than with CephFS client runtime code. Although it sits in the repository under `sources/distributed-fs/ceph-client`, the path mirrors or vendors Linux `tools/perf` content.

Key integration points are:

- The perf PMU events JSON parser/generator, which expects valid event objects with fields such as `EventName`, `EventCode`, `UMask`, `BriefDescription`, `PublicDescription`, `Counter`, `Unit`, and `PerPkg`.
- The x86 CPU model mapping for `cascadelakex`, which determines when these event names are offered for the running machine.
- The uncore PMU driver support for the `M3UPI` unit and its three programmable counters.
- Perf user interfaces such as `perf list`, `perf stat -e`, and metric/reporting paths that display descriptions and program event selectors.
- Adjacent chunks of this same JSON file, because event families are split by line range. This chunk begins after earlier `M3UPI_M2_BL_CREDITS_EMPTY` entries and ends before the rest of `VN0_CREDITS_USED`.

The file depends on Intel's Cascade Lake Xeon uncore event definitions being represented accurately. The correctness of the table is not locally derivable from code in this file; it depends on hardware documentation, upstream Linux perf event data, and validation on supported systems.

## Risks and Edge Cases

The main risk is metadata drift. A wrong `EventCode` or `UMask` silently programs a different hardware condition while preserving a plausible event name and description. These events are low-level enough that such mistakes may only show up as misleading performance analysis rather than immediate test failures.

Description/name mismatches are another risk. This chunk contains repeated families where only a suffix and mask change, so copy/paste mistakes are easy. A notable example pattern is in UPI peer credit-empty events: some brief descriptions mention one message class while the `EventName` suffix names another. Those should be checked against the authoritative uncore event list before using the brief text as documentation.

The `Experimental` flag means consumers should be careful with long-lived automation that depends on exact names. Event availability and semantics can vary across stepping, socket topology, BIOS configuration, and kernel uncore PMU support.

Counter scheduling is constrained. Every complete record in this chunk targets `Counter: "0,1,2"`, but the M3UPI unit may expose multiple instances or links depending on hardware topology. Tooling must handle unavailable units, multiplexing, and package aggregation correctly.

Some events count cycles while others count inserts, flits, credits, arbitration outcomes, or occupancy-like conditions. Comparing raw values across families can be misleading unless normalized by elapsed cycles, unit instance count, or traffic volume.

The chunk boundary itself is an edge case. A line-range consumer that tries to parse only lines 6281-11953 as standalone JSON will fail because the selected range is not a complete JSON array and ends mid-object. Research and reconciliation must use the full source file for syntax validation.

## Test Signals

High-signal validation for this chunk includes:

- The full `uncore-interconnect.json` file parses as valid JSON after any edits.
- Perf's PMU event table generation succeeds for the `cascadelakex` architecture directory.
- Generated tables include the `M3UPI` events from this range with the expected `EventCode`, `UMask`, `Counter`, `PerPkg`, and description fields.
- `perf list` on a matching Cascade Lake Xeon system shows representative events from each family, including RxC arbitration, TxC flow-queue, TxR/RxR queue, ring-in-use, UPI peer credit-empty, and VN0 credit-used families.
- `perf stat -e` can schedule representative M3UPI events on allowed counters without parser errors.
- Hardware sanity checks show nonzero values under relevant traffic: UPI peer credit events under inter-socket pressure, ring occupancy under mesh/ring traffic, and TxR/RxR inserts or cycles-non-empty when the link is active.

For repository-only validation, the best checks are JSON parsing of the full file, perf PMU-events generator tests, and diff review against upstream Linux perf event data for Cascade Lake Xeon.

## Cross-Chunk Notes

This is a chunk-level research artifact only. The final per-file report should merge it with neighboring chunks before drawing whole-file conclusions.

The previous chunk contains earlier `M3UPI_M2_BL_CREDITS_EMPTY` records that precede `IIO5_NCB`. The next chunk is required to complete `UNC_M3UPI_VN0_CREDITS_USED.NCS` and continue the VN0 credit-use family.
