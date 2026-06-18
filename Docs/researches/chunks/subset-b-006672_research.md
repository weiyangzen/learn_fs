# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/uncore-interconnect.json lines 3920-4392

## Scope

This chunk covers the final 473 lines of the Haswell Xeon `uncore-interconnect.json` PMU event table. The range starts inside the last `UNC_S_RxR_CRD_STARVED` SBOX event object, beginning at its `BriefDescription` field on line 3920, and continues through the end of the JSON array on line 4392.

The selected records describe Intel uncore interconnect events for two units:

- `SBOX`: 32 complete event records in this range, plus the start-line portion of a complete event whose opening brace is on line 3919. These cover S-box receive-ring credit starvation, ingress queue inserts and occupancy, transmit-ring ADS use, egress queue inserts and occupancy, and transmit-ring starvation.
- `UBOX`: 16 complete event records at the end of the file. These cover uncore box clockticks, event messages, thread/core filter matching, PHOLD cycles, RACU register requests, and uncore-to-core monitor/error/trap notifications.

The data is declarative JSON metadata consumed by Linux perf's PMU events tooling. It does not define executable functions, classes, or runtime control flow. Each object maps a perf-visible event name to low-level uncore PMU programming fields such as event selector, unit mask, allowed counters, unit name, and package scope.

The full source file has 4,392 lines and parses as valid JSON. This chunk is not intended to parse independently because it starts after an object opener and includes the closing `]` for the full file.

## Purpose

The purpose of this chunk is to expose the tail of Haswell Xeon uncore interconnect events to perf users. These events help diagnose package-level traffic pressure and control-message behavior outside the CPU core PMUs.

The SBOX records focus on traffic entering and leaving an S-box ring stop:

- `UNC_S_RxR_CRD_STARVED.IV` counts receive-ring injection starvation for the IV class when ingress cannot forward to egress because credits are unavailable.
- `UNC_S_RxR_INSERTS.*` counts allocations into SBOX ingress queues for AD bounce, AD credit, AK, BL bounce, BL credit, and IV traffic classes.
- `UNC_S_RxR_OCCUPANCY.*` tracks occupancy of the same ingress buffers.
- `UNC_S_TxR_ADS_USED.AD`, `.AK`, and `.BL` report transmit-ring ADS use by ring type.
- `UNC_S_TxR_INSERTS.*` counts allocations into SBOX egress queues for traffic destined to the ring.
- `UNC_S_TxR_OCCUPANCY.*` tracks egress buffer occupancy.
- `UNC_S_TxR_STARVED.AD`, `.AK`, `.BL`, and `.IV` count egress injection starvation onto the corresponding ring.

The UBOX records expose package-level control and notification activity:

- `UNC_U_CLOCKTICKS` provides a unit clock baseline.
- `UNC_U_EVENT_MSG.DOORBELL_RCVD` counts Virtual Logical Wire doorbell messages received from uncore.
- `UNC_U_FILTER_MATCH.*` counts per-thread filter matches, with enable/disable variants and U2C-specific variants.
- `UNC_U_PHOLD_CYCLES.ASSERT_TO_ACK` counts PHOLD cycles from assertion to acknowledgement.
- `UNC_U_RACU_REQUESTS` counts outstanding register requests in the message-channel tracker.
- `UNC_U_U2C_EVENTS.*` counts uncore-to-core events for monitor thread notifications, livelock, LTError, correctable and uncorrectable machine checks, traps, and other notification classes.

Together these records give perf enough metadata to program Haswell Xeon uncore PMUs for ring-queue pressure and package-control event analysis.

## Important Schema Fields and Event Families

The records use the standard perf PMU events JSON schema:

- `EventName`: symbolic event name exposed to perf, such as `UNC_S_TxR_OCCUPANCY.AD_CRD` or `UNC_U_U2C_EVENTS.UMC`.
- `EventCode`: hardware event selector as a hex string. Most records have one; `UNC_U_CLOCKTICKS` omits it.
- `UMask`: unit mask selecting a traffic class, direction, filter mode, or notification subtype. Base events such as `UNC_U_RACU_REQUESTS` may omit it.
- `BriefDescription`: short user-facing label.
- `PublicDescription`: longer explanation where available. This chunk has 48 `EventName` records and 44 `PublicDescription` fields.
- `Counter`: allowed programmable counters. SBOX events use `0,1,2,3`; UBOX events use `0,1`.
- `Unit`: uncore PMU unit name, either `SBOX` or `UBOX`.
- `PerPkg`: consistently `1`, marking the events as package-scoped.

Major event-code groupings in this range are:

- `0x14`: SBOX RxR credit-starved event for `IV`.
- `0x13`: SBOX RxR ingress insert events split by AD/AK/BL/IV and bounce/credit classes.
- `0x11`: SBOX RxR ingress occupancy events for the same classes.
- `0x4`: SBOX TxR ADS-used events for AD, AK, and BL.
- `0x2`: SBOX TxR egress insert events.
- `0x1`: SBOX TxR egress occupancy events.
- `0x3`: SBOX TxR starved events for AD, AK, BL, and IV rings.
- `0x41`, `0x42`, `0x43`, `0x45`, and `0x46`: UBOX filter, event-message, uncore-to-core, PHOLD-cycle, and RACU-request events.

The common SBOX suffixes are `AD_BNC`, `AD_CRD`, `AK`, `BL_BNC`, `BL_CRD`, and `IV`. The common UBOX suffix families are filter mode suffixes (`ENABLE`, `DISABLE`, `U2C_ENABLE`, `U2C_DISABLE`) and U2C event subtype suffixes (`CMC`, `LIVELOCK`, `LTERROR`, `MONITOR_T0`, `MONITOR_T1`, `OTHER`, `TRAP`, `UMC`).

## Control Flow

There is no local control flow in this JSON file. The effective control path is created by perf's table-driven PMU event pipeline:

1. Perf build tooling reads architecture-specific JSON files under `tools/perf/pmu-events/arch/x86/`.
2. The Haswell Xeon event records are converted into generated C tables.
3. At runtime, perf selects the matching CPU model and exposes the generated event names through `perf list` and event lookup.
4. When a user selects an event, perf resolves the symbolic `EventName` to `EventCode`, `UMask`, `Counter`, `Unit`, and package-scope metadata.
5. The relevant uncore PMU driver programs package-level SBOX or UBOX counters and reports counts back through perf.

Within this chunk, related events share selectors and differ mostly by `UMask`. For example, SBOX egress occupancy events all use event code `0x1` while masks select AD bounce, AD credit, AK, BL bounce, BL credit, or IV. UBOX uncore-to-core events all use event code `0x43` while masks select monitor, error, trap, machine-check, or other event classes. The runtime behavior is therefore data-driven rather than implemented by branches in this file.

## State and Persistence Behavior

The persistent state is the checked-in JSON metadata. The file does not allocate memory, mutate runtime state, perform I/O, or persist measurements. During the perf build, these records become generated event tables; at runtime, hardware counters hold the measured state.

All records in this chunk are package-scoped with `PerPkg: "1"`. This matters for interpretation because counts aggregate package-level uncore behavior rather than per-thread or per-core activity. SBOX counters are limited to `0,1,2,3`; UBOX counters are limited to `0,1`. Tools must account for scheduling limits, multiplexing, and unavailable units on systems that do not expose the expected Haswell Xeon uncore PMUs.

The start boundary is a chunking artifact. The event object for `UNC_S_RxR_CRD_STARVED.IV` begins at line 3919, while this requested range begins at line 3920. The final per-file merge should treat it as one complete event in the full source file, not as a malformed standalone fragment.

## Dependencies and Integration Points

This file integrates with Linux perf's PMU events infrastructure rather than with CephFS client runtime code. Although it is stored under `sources/distributed-fs/ceph-client`, the path mirrors Linux `tools/perf` content.

Key dependencies and integration points are:

- Perf's PMU event JSON parser and generated-table builder, which require valid full-file JSON and known schema fields.
- The x86 CPU model mapping for `haswellx`, which controls when these events are available.
- Kernel/perf uncore PMU support for the `SBOX` and `UBOX` units, including package-level counter discovery and programming.
- Perf user interfaces such as `perf list`, `perf stat -e`, and generated event documentation.
- Intel Haswell Xeon uncore event definitions, which are the external source of truth for event selectors, masks, descriptions, and counter constraints.
- Adjacent lines in the same file, especially lines 3919 and earlier SBOX event families, because this chunk starts inside an event object and represents only the final part of the source file.

## Risks and Edge Cases

The main risk is silent metadata drift. A wrong `EventCode` or `UMask` can program a different hardware condition while still producing plausible perf output. This is especially easy in repeated SBOX families where many records differ only by suffix and mask.

Description quality is uneven. Several SBOX descriptions are repeated boilerplate, and the receive-ring credit-starvation text includes awkward wording: "the Ingress but unable to forward to Egress due to lack of credit." UBOX descriptions also repeat "Monitor Sent to T0" in `BriefDescription` for event subtypes that are not strictly monitor T0 events, such as `UMC`, `TRAP`, `OTHER`, and `CMC`. Consumers should prefer `EventName` and hardware documentation over brief text when precision matters.

Some records omit fields that many neighboring records include. `UNC_U_CLOCKTICKS` has no `EventCode` or `UMask`, and `UNC_U_RACU_REQUESTS` has no `UMask`. That is normal for some perf PMU event definitions, but schema validators or custom tooling must not assume every event has all optional fields.

Counter constraints differ by unit. SBOX events can use four counters, while UBOX events can use two. A single perf command requesting too many events from the same unit may fail to schedule or may require multiplexing.

Raw counts are not directly comparable across all families. Occupancy and PHOLD cycle events are cycle-like, inserts and requests are occurrence-like, and starvation events count specific backpressure conditions. Useful analysis usually needs normalization by clockticks, elapsed time, traffic volume, package count, or uncore unit instance count.

The line-range boundary is another edge case for research tooling. Lines 3920-4392 are not a standalone JSON document, so validation must parse the full file.

## Test Signals

High-signal validation for this chunk includes:

- The full `sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/uncore-interconnect.json` file parses as valid JSON.
- Perf PMU event table generation succeeds for the `haswellx` architecture directory.
- Generated event tables include representative SBOX records from this chunk with expected event codes and masks, such as `UNC_S_RxR_INSERTS.AD_CRD` (`0x13`/`0x1`), `UNC_S_TxR_OCCUPANCY.IV` (`0x1`/`0x20`), and `UNC_S_TxR_STARVED.BL` (`0x3`/`0x4`).
- Generated event tables include representative UBOX records such as `UNC_U_CLOCKTICKS`, `UNC_U_FILTER_MATCH.U2C_ENABLE`, `UNC_U_PHOLD_CYCLES.ASSERT_TO_ACK`, `UNC_U_RACU_REQUESTS`, and `UNC_U_U2C_EVENTS.UMC`.
- `perf list` on a matching Haswell Xeon system exposes SBOX and UBOX events from this range.
- `perf stat -e` can schedule representative events within the unit-specific counter limits.
- Hardware sanity checks show expected nonzero values under relevant activity: SBOX inserts/occupancy under ring traffic, starvation under induced ring pressure or credit pressure, UBOX filter and U2C events under matching control-message or notification activity, and UBOX clockticks as a baseline.

For repository-only validation, the most practical checks are full-file JSON parsing, perf PMU-events generator tests, and diff review against the corresponding upstream Linux perf Haswell Xeon event data.

## Cross-Chunk Notes

This is a chunk-level research artifact only. The final per-file report should merge it with earlier chunks before making whole-file conclusions.

The previous chunk is needed to include the opening brace and preceding sibling records for the `UNC_S_RxR_CRD_STARVED` family. This chunk completes the file and has no following chunk dependency for this source path.
