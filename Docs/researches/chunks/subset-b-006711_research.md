# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sapphirerapids/uncore-cache.json lines 5336-7315

## Scope

This chunk covers the tail of the Sapphire Rapids `uncore-cache.json` PMU event table in the vendored Linux `tools/perf` tree. The file is declarative JSON metadata, not executable CephFS code. Perf's `pmu-events` generator consumes the complete JSON array and emits generated C event tables for symbolic uncore event lookup.

The requested range starts inside the `UNC_CHA_TOR_INSERTS.PMM` object: lines 5329-5335 contain that object's opening fields, while line 5336 in this chunk begins at its `PublicDescription`. The chunk then contains the rest of the file through the final `UNC_CHA_XPT_PREF.SENT1` object and the closing JSON array bracket on line 7315.

The full source file has 7,315 lines and parses as 687 top-level event objects. This line range intersects 187 logical event objects, with 186 fully contained in the range. Those objects are all `Unit: "CHA"` package-level uncore cache/home-agent events:

- 10 `UNC_CHA_TOR_INSERTS.*` objects, including the partial `PMM` object at the beginning.
- 163 `UNC_CHA_TOR_OCCUPANCY.*` objects.
- 2 `UNC_CHA_WB_PUSH_MTOI.*` objects.
- 6 `UNC_CHA_WRITE_NO_CREDITS.*` objects.
- 6 `UNC_CHA_XPT_PREF.*` objects.

## Purpose

This metadata exposes Sapphire Rapids CHA uncore cache and home-agent events to Linux perf users through stable symbolic names. The dominant purpose of this chunk is to describe TOR, or table-of-requests, activity:

- `UNC_CHA_TOR_INSERTS.*` counts successful TOR entry insertions that match a subevent qualifier.
- `UNC_CHA_TOR_OCCUPANCY.*` accumulates, for each cycle, the number of valid TOR entries that match a qualifier. These are occupancy-cycle events, not plain transaction counts.
- `UNC_CHA_WB_PUSH_MTOI.*` splits WbPushMtoI handling by whether the line was pushed to LLC or memory.
- `UNC_CHA_WRITE_NO_CREDITS.MC0` through `.MC5` count cases where the CHA cannot send writes into a selected integrated memory controller because write credits are unavailable.
- `UNC_CHA_XPT_PREF.*` counts XPT prefetches sent or dropped because of AD CMS write-port conflicts or missing XPT AD egress credits.

The TOR occupancy section is the largest part of the chunk. It lets perf users separate local IA-core traffic, IO-originated traffic, remote-socket traffic, LLC hit/miss state, memory target class, CXL accelerator-memory traffic, queue class, opcode-match filters, and local-vs-remote target behavior. These events are useful for low-level workload diagnosis on Sapphire Rapids systems, especially when investigating LLC/SF behavior, data-read/RFO pressure, page-walk reads, streaming writes, IO or PCIe-originated coherency traffic, and memory-controller write backpressure.

## Important Data Fields

Each object follows the perf PMU event schema consumed by `tools/perf/pmu-events/jevents.py`:

- `EventName` is the user-facing symbolic name shown by `perf list` and accepted by `perf stat -e`.
- `EventCode` is the hardware selector. This chunk uses `0x35` for TOR inserts, `0x36` for TOR occupancy, `0x56` for WbPushMtoI outcomes, `0x5a` for CHA-to-iMC write-credit-empty events, and `0x6f` for XPT prefetch events.
- `UMask` selects the subevent. Broad placeholder selectors sometimes omit it; concrete filters use masks such as `0xc001ff08` for remote snoops, `0xc817fe01` for IA miss data reads, and high-bit masks such as `0x10c8968201` for CXL accelerator-memory filters.
- `Counter` is `"0,1,2,3"` for insert, writeback-push, write-credit, and XPT-prefetch events. Every TOR occupancy object in this chunk uses `"0"`, preserving the hardware constraint for occupancy accumulation.
- `Unit` is `"CHA"` throughout, binding the events to Sapphire Rapids CHA uncore PMUs.
- `PerPkg` is `"1"` throughout, marking these as package-scoped events rather than per-thread or per-core counters.
- `Experimental` appears on 137 of the 187 logical objects in this chunk. The 50 non-experimental objects are mostly established IA and IO TOR occupancy aliases.
- `BriefDescription` is present on all 187 logical objects. `PublicDescription` is present on 165; 22 CXL accelerator occupancy records rely on terse brief descriptions only.
- `PortMask` and `FCMask` appear on a small set of page-walk, local-CXL, and IO partial-write entries, usually as zero masks. These fields are still part of the event encoding contract and should be preserved.

The chunk has 17 logical objects without `UMask`: the partial `UNC_CHA_TOR_INSERTS.PMM`, `UNC_CHA_TOR_INSERTS.PREMORPH_OPC`, `UNC_CHA_TOR_INSERTS.REMOTE_TGT`, and broad TOR occupancy selectors such as `DDR`, `HIT`, `MISS`, `MATCH_OPC`, `PMM`, `PREMORPH_OPC`, and `REMOTE_TGT`. These omissions should be treated as schema choices unless checked against upstream event documentation.

## APIs, Types, And Generated Representation

This JSON file defines no local functions, classes, or C types. Its API surface is the generated perf representation:

- `tools/perf/pmu-events/jevents.py` parses each JSON object and emits generated C tables.
- `struct pmu_event` in `tools/perf/pmu-events/pmu-events.h` carries generated event names, PMU/unit binding, event encodings, descriptions, package scope, and flags.
- Perf table APIs such as `pmu_events_table__for_each_event()` and `pmu_events_table__find_event()` expose generated entries to runtime lookup paths.
- `perf list`, JSON list output, and `perf stat -e <event>` consume the generated metadata.
- The x86 uncore PMU kernel driver must expose compatible Sapphire Rapids CHA PMUs and counter slots for the generated encodings to schedule.

For records in this chunk, `EventCode`, `UMask`, `Counter`, `PortMask`, and `FCMask` become the hardware event encoding or scheduling constraints. `EventName`, `BriefDescription`, `PublicDescription`, `Unit`, `PerPkg`, and `Experimental` become lookup and display metadata.

## Control Flow

The JSON itself has no executable control flow. Its effective build and runtime flow is table-driven:

1. The perf build invokes the x86 PMU event generation path.
2. `jevents.py` reads `tools/perf/pmu-events/arch/x86/sapphirerapids/uncore-cache.json` as part of the Sapphire Rapids model directory.
3. The generator validates each event object and converts it into generated C event-table entries.
4. The generated tables are compiled into perf's PMU event database.
5. At runtime, perf maps the current CPU model to the Sapphire Rapids event table through the x86 mapfile.
6. User commands such as `perf list --details` or `perf stat -e UNC_CHA_TOR_OCCUPANCY.IA_MISS_DRD` resolve symbolic event names to CHA uncore PMU configurations.
7. The kernel uncore PMU driver programs package-level CHA counters if the hardware, counter constraints, and permissions allow it.

Within this chunk, event ordering is by family: the tail of `UNC_CHA_TOR_INSERTS`, then the large `UNC_CHA_TOR_OCCUPANCY` family, followed by compact WbPushMtoI, write-credit, and XPT-prefetch families. Because this range includes the closing `]`, syntax changes here can close or break the complete file.

## State And Persistence Behavior

The persistent state is the checked-in PMU event metadata and any generated perf event tables produced during a build. The JSON does not persist measurements, allocate runtime state, or interact with CephFS state.

Runtime state exists in hardware counters after perf programs the CHA uncore PMUs. `PerPkg: "1"` means results are package-level measurements; a package can expose many CHA instances, and perf may aggregate or select instances depending on command syntax and kernel PMU exposure.

The meaning of the counts differs by family. TOR insert events are event counts for matching entries inserted into the TOR. TOR occupancy events accumulate matching valid entries per cycle, so their raw values usually need normalization by elapsed cycles, active CHA count, or related traffic counts before being compared as rates or queue depths. Write-credit and XPT-prefetch events are count-style backpressure or prefetch-path signals.

The event names and encodings are compatibility state for user scripts. Renaming aliases, changing `UMask` values, removing experimental flags, or relaxing `Counter: "0"` on occupancy events can alter user-visible behavior even when the JSON still parses.

## Dependencies And Integration Points

This chunk integrates with the Linux perf PMU event stack:

- `tools/perf/pmu-events/README` documents the event JSON database, model directories, mapfile matching, and generated tables.
- `tools/perf/pmu-events/Build` wires JSON inputs, `jevents.py`, generated event tables, and PMU event tests into perf builds.
- `tools/perf/pmu-events/jevents.py` consumes fields used in this chunk.
- `tools/perf/pmu-events/pmu-events.h` defines the generated event and metric table interfaces.
- `tools/perf/pmu-events/arch/x86/mapfile.csv` maps Sapphire Rapids CPU identifiers to this model directory.
- `tools/perf/builtin-list.c` and perf's event parser expose generated events to users.
- The x86 uncore PMU kernel driver provides the actual CHA PMU devices, counter slots, and package-scoped event programming.

Although this path is under `sources/distributed-fs/ceph-client`, the file belongs to a vendored Linux perf tooling subtree. It has no direct Ceph client, metadata-server, journal, object-store, or distributed-filesystem control flow. Its connection to the broader source tree is through tooling and performance-observability metadata.

## Event Family Notes

The `UNC_CHA_TOR_INSERTS` portion of this chunk covers PMM access, pre-morphed opcode matching, PRQ IOSF and non-IOSF, remote target placeholders, all remote requests, remote snoops, RRQ, a duplicate remote-snoop alias `SNPS_FROM_REM`, and WBQ. Most use event code `0x35` with counters `0,1,2,3`; explicit masks include `0x4` for PRQ IOSF, `0x20` for PRQ non-IOSF, `0xc001ffc8` for all remote requests, `0xc001ff08` for remote snoops, `0x40` for RRQ, and `0x80` for WBQ.

The `UNC_CHA_TOR_OCCUPANCY` section mirrors the insert family with event code `0x36` and counter `0`, but with much more detailed qualifiers. It includes broad selectors (`ALL`, `DDR`, `EVICT`, `HIT`, `MISS`), IA-originated traffic, IO-originated traffic, queue selectors (`IPQ`, `IRQ_IA`, `IRQ_NON_IA`, `PRQ`, `RRQ`, `WBQ`), locality groupings (`LOC_ALL`, `LOC_IA`, `LOC_IO`, `REM_ALL`, `REM_SNPS`), and opcode/target filters.

The IA occupancy records distinguish code reads, data reads, page-table reads, RFOs, ItoM, WbMtoI, WCIL/WCILF, UCRDF/WIL, LLC prefetch code/data/RFO, hit versus miss, local versus remote, DDR versus PMM, and CXL accelerator target classes. Several CXL records have no `PublicDescription`, so consumers should not infer more than the event name, mask, and Intel hardware documentation support.

The IO occupancy records distinguish IO CLFLUSH, hit/miss, ItoM, ItoMCacheNear partial writes, PCI RdCur, RFO, WbMtoI, and local/remote variants. These entries help separate device-originated cacheable/coherent traffic from IA-core-originated traffic.

The final compact families are straightforward but operationally important. `UNC_CHA_WB_PUSH_MTOI.LLC` and `.MEM` split whether WbPushMtoI was pushed to LLC or memory. `UNC_CHA_WRITE_NO_CREDITS.MC0` through `.MC5` split write-credit starvation by memory controller using masks `0x1` through `0x20`. `UNC_CHA_XPT_PREF` uses event code `0x6f`: `SENT0`/`SENT1` use masks `0x1`/`0x10`, no-credit drops use `0x4`/`0x40`, and conflict drops use `0x8`/`0x80`.

## Risks And Edge Cases

The first logical object is incomplete in this line slice. The merge lane needs the previous chunk for the opening fields of `UNC_CHA_TOR_INSERTS.PMM`, and validation should parse the complete file rather than this line range as standalone JSON.

The largest risk is silent metadata drift. Many TOR occupancy entries differ only by long suffixes and extended masks, so a one-digit mask error can still parse cleanly while programming a different hardware condition. CXL accelerator variants are especially sensitive because the high mask bits encode target class and locality.

The counter constraint on occupancy events matters. Treating `UNC_CHA_TOR_OCCUPANCY.*` as normal `0,1,2,3` events would create invalid or misleading scheduling behavior; grouping several occupancy events may also overconstrain counter 0 and lead to multiplexing or scheduling failures.

Optional fields are uneven. Some broad selector objects omit `UMask`, 22 CXL occupancy records omit `PublicDescription`, and only a handful carry `PortMask` or `FCMask`. Schema checks should distinguish intended omissions from accidental data loss by comparing against authoritative perf or Intel PMU data.

The duplicate remote-snoop aliases `REM_SNPS` and `SNPS_FROM_REM` use the same mask in both insert and occupancy families. Removing one as "duplicate" could break existing perf scripts that depend on the alias.

The final object has no trailing comma and is followed by the closing JSON array bracket. Any syntax edit around `UNC_CHA_XPT_PREF.SENT1` can break generation for the entire Sapphire Rapids uncore-cache event table.

## Test Signals

Useful validation signals for this chunk include:

- `python3 -m json.tool sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sapphirerapids/uncore-cache.json` succeeds on the complete file.
- Full-file parsing reports 687 top-level event objects.
- A line-aware object scan finds 187 logical objects intersecting lines 5336-7315, all with `Unit: "CHA"` and `PerPkg: "1"`.
- Representative selectors are present with expected event codes: `UNC_CHA_TOR_INSERTS.*` at `0x35`, `UNC_CHA_TOR_OCCUPANCY.*` at `0x36`, `UNC_CHA_WB_PUSH_MTOI.*` at `0x56`, `UNC_CHA_WRITE_NO_CREDITS.*` at `0x5a`, and `UNC_CHA_XPT_PREF.*` at `0x6f`.
- Perf PMU event generation for the x86 Sapphire Rapids directory completes without schema or parse errors.
- Perf PMU event lookup tests can find representative names such as `UNC_CHA_TOR_INSERTS.RRQ`, `UNC_CHA_TOR_OCCUPANCY.IA_MISS_DRD_REMOTE_DDR`, `UNC_CHA_TOR_OCCUPANCY.IO_MISS_PCIRDCUR_REMOTE`, `UNC_CHA_WB_PUSH_MTOI.MEM`, `UNC_CHA_WRITE_NO_CREDITS.MC5`, and `UNC_CHA_XPT_PREF.DROP1_NOCRD`.
- On Sapphire Rapids hardware with CHA uncore PMUs available, `perf stat -a -e` can schedule a small representative set, and counts move plausibly under memory, IO, or prefetch-heavy workloads.

## Cross-Chunk Notes

This is chunk 2 of 2 for `sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sapphirerapids/uncore-cache.json`. The previous chunk is required for the full `UNC_CHA_TOR_INSERTS.PMM` object and for the earlier event families in the same JSON array. The final per-file research document should be produced later by the merge/reconciliation lane after both Sapphire Rapids `uncore-cache.json` chunks are available.
