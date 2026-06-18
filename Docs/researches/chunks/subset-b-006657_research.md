# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/uncore-cache.json lines 5352-7547

## Scope

This chunk covers the tail of the Emerald Rapids `uncore-cache.json` PMU event table in the vendored Linux `tools/perf` tree. The file is static JSON metadata, not executable code. The perf `pmu-events` generator consumes these objects and emits generated C event tables for symbolic uncore event lookup.

The requested range starts inside the `UNC_CHA_TOR_INSERTS.MMCFG` object: lines 5346-5351 contain that object's opening fields, while line 5352 in this chunk begins at its `PublicDescription`. The rest of the range contains complete event objects and ends with the file's closing JSON array on line 7547. In total this slice includes 207 `EventName` records: 19 `UNC_CHA_TOR_INSERTS.*` records, 174 `UNC_CHA_TOR_OCCUPANCY.*` records, 2 `UNC_CHA_WB_PUSH_MTOI.*` records, 6 `UNC_CHA_WRITE_NO_CREDITS.*` records, and 6 `UNC_CHA_XPT_PREF.*` records.

## Purpose

The purpose of this metadata is to expose Emerald Rapids CHA uncore cache/home-agent events to perf users through stable symbolic names. The dominant families in this chunk describe TOR, or table-of-requests, activity in the CHA:

- `UNC_CHA_TOR_INSERTS.*` counts successful TOR entry insertions matching a subevent selector.
- `UNC_CHA_TOR_OCCUPANCY.*` accumulates, for each cycle, the number of valid TOR entries matching a selector. These are occupancy-cycle events rather than simple transaction counts.
- `UNC_CHA_WB_PUSH_MTOI.*` counts WbPushMtoI outcomes routed to LLC or memory.
- `UNC_CHA_WRITE_NO_CREDITS.MC0` through `.MC5` count times that CHA writes cannot be sent into a selected iMC because write credits are unavailable.
- `UNC_CHA_XPT_PREF.*` tracks XPT prefetches that are sent or dropped because of conflicts or missing egress credits on two apparent paths, `0` and `1`.

These events support low-level memory hierarchy analysis on Emerald Rapids systems, especially separation of local IA core traffic, IO-originated traffic, remote-socket requests, LLC hit/miss cases, memory target classes, CXL accelerator or expander memory targets, queue classes, and credit pressure.

## Important Data Fields

Each JSON object follows the perf PMU event schema used by `tools/perf/pmu-events/jevents.py`:

- `EventName` is the symbolic event users pass to `perf stat -e` or see in `perf list`.
- `EventCode` is the hardware event selector. This chunk uses `0x35` for TOR inserts, `0x36` for TOR occupancy, `0x56` for WbPushMtoI outcomes, `0x5a` for CHA-to-iMC write-credit empty events, and `0x6f` for XPT prefetch events.
- `UMask` refines the subevent. Many broad selector placeholders in this slice omit `UMask`, while concrete source/opcode/target filters provide masks such as `0xc001ff01`, `0xc817fe01`, `0x20e8068240`, or `0x10c8968201`.
- `Counter` lists valid uncore counters. TOR inserts, writeback push, write-credit, and XPT-prefetch events use `"0,1,2,3"`. TOR occupancy events use `"0"`, reflecting the special occupancy accumulation counter constraint.
- `Unit` is `"CHA"` throughout this chunk, binding records to CHA uncore PMUs.
- `PerPkg` is `"1"` throughout this chunk, marking the events as package-scoped.
- `Experimental` appears on most records, especially broad TOR selectors, CXL-specific filters, and newer/less stable memory target variants.
- `BriefDescription` and `PublicDescription` provide user-facing text for `perf list` and generated event metadata.
- `PortMask` and `FCMask` appear on a few page-walk, IO partial-write, and local CXL variants, commonly as zero masks. Their presence is still significant because the generator preserves recognized qualifier fields when constructing event encodings.

The chunk contains several repeated mask patterns. IA-originated occupancy names use a low source selector ending in `...01`; IO-originated names use `...04`; remote request queue entries use `...40`; local/remote target variants commonly switch between values such as `...fe...`, `...7e...`, `...86...`, `...8a...`, and CXL filters with high prefixes such as `0x10...` for accelerator memory and `0x20...` for expander memory.

## APIs, Types, And Generated Representation

There are no functions or C types defined in this JSON file. The important API surface is the generated representation produced from it:

- `tools/perf/pmu-events/jevents.py` parses the JSON event objects and emits generated C tables.
- `struct pmu_event` in `tools/perf/pmu-events/pmu-events.h` carries generated fields such as event name, PMU/unit binding, description, encoding string, package scope, and flags.
- `pmu_events_table__for_each_event()` iterates model-specific events.
- `pmu_events_table__find_event()` resolves a requested symbolic event name against the generated model table.
- Runtime perf commands such as `perf list` and `perf stat -e` consume the generated event metadata and pass the resolved event code, umask, and qualifiers to Linux perf event opening paths.

For these records, `EventCode`, `UMask`, `Counter`, `FCMask`, and `PortMask` are transformed into the event encoding used for `perf_event_attr.config` and related uncore qualifier fields. `Unit: "CHA"` maps the generated event to matching CHA PMU names exposed by the kernel uncore driver.

## Control Flow

The JSON itself has no control flow. Its effective build and runtime flow is:

1. The perf build invokes the PMU events generation path for x86.
2. `jevents.py` reads `tools/perf/pmu-events/arch/x86/emeraldrapids/uncore-cache.json` as part of the Emerald Rapids model directory.
3. Each event object is validated and converted into generated C event-table entries.
4. The generated tables are compiled into perf's PMU event database.
5. At runtime, perf maps the current CPU model to the Emerald Rapids table through the x86 mapfile.
6. `perf list` displays these CHA events, and `perf stat -e <event>` resolves names such as `UNC_CHA_TOR_OCCUPANCY.IA_MISS_DRD_REMOTE_DDR` into a CHA uncore PMU event configuration.
7. The kernel uncore PMU driver programs the package-level CHA counters if the hardware and permissions support them.

The chunk's event families are ordered by selector family: the tail of `UNC_CHA_TOR_INSERTS`, then the large `UNC_CHA_TOR_OCCUPANCY` family, then WbPushMtoI, write-credit, and XPT-prefetch events. Because this range includes the final `]`, JSON syntax here closes the whole file.

## State And Persistence Behavior

The persistent state is the checked-in event metadata and the generated event table produced during perf builds. The JSON does not open files, mutate runtime state, or persist measurement data.

At runtime, these definitions become package-level CHA uncore counter configurations. The measured state lives in hardware counters, not in the JSON. TOR insert events count matching allocations into the CHA TOR, while TOR occupancy events accumulate matching valid entries every cycle, so users must interpret occupancy results as occupancy-cycle totals that generally require normalization by elapsed cycles, sampling interval, or traffic count.

The `PerPkg` flag means these are package-scoped uncore measurements. Results can differ from per-core event expectations because a single package may contain many CHAs and perf may aggregate across CHA PMU instances depending on command syntax and kernel PMU exposure.

## Dependencies And Integration Points

This chunk integrates with the Linux perf PMU event stack:

- `tools/perf/pmu-events/README` documents the event JSON layout, model directories, and generated tables.
- `tools/perf/pmu-events/jevents.py` is the parser/generator for fields used here.
- `tools/perf/pmu-events/pmu-events.h` defines the generated event and metric table interfaces.
- `tools/perf/pmu-events/arch/x86/mapfile.csv` associates Emerald Rapids CPU identifiers with this model directory.
- `tools/perf/builtin-list.c` and perf's event parsing paths expose these generated events to users.
- The x86 uncore PMU kernel driver must expose compatible CHA PMUs and counter slots for the event encodings to be usable.

Although this source path is under `sources/distributed-fs/ceph-client`, the file belongs to a vendored Linux perf tooling subtree. It has no direct CephFS, distributed-file-system protocol, metadata-server, client cache, or network control flow.

## Event Family Notes

The `UNC_CHA_TOR_INSERTS` portion of this slice covers broad target/source filters such as MMIO, NearMem, non-coherent, PMM, PRQ, remote requests, RRQ, snoops from remote sockets, WBQ, and several remote-RRQ miss opcodes targeting local CXL type 3 expander memory. Most use event code `0x35` on counters `0,1,2,3`; explicit masks include `0x4` for PRQ IOSF, `0x20` for non-IOSF PRQ, `0xc001ffc8` for all remote requests, `0xc001ff08` for remote snoops, `0x40` for RRQ, and high CXL/opcode masks such as `0x20e8168240`.

The `UNC_CHA_TOR_OCCUPANCY` portion mirrors many of the insert selectors using event code `0x36` and counter `0`. It includes broad selectors (`ALL`, `DDR`, `EVICT`, `HIT`, `MISS`), local IA traffic (`IA_*`), IO traffic (`IO_*`), queue selectors (`IPQ`, `IRQ_IA`, `IRQ_NON_IA`, `PRQ`, `RRQ`, `WBQ`), local/remote grouping (`LOC_ALL`, `LOC_IA`, `LOC_IO`, `REM_ALL`, `REM_SNPS`), and opcode/target filters.

The IA occupancy records are the most detailed. They distinguish code reads, data reads, RFOs, prefetches, page-walk reads, ItoM, WbMtoI, WCIL/WCILF, UCRDF/WIL, hit versus miss, local versus remote home or target, DDR versus PMM, and CXL accelerator or expander targets. Several CXL records only have terse `BriefDescription` text, so their exact semantics depend heavily on the event name and mask.

The IO occupancy records similarly distinguish IO CLFLUSH, hit/miss, ItoM, ItoMCacheNear partial writes, PCI RdCur/FsRdCur, RFO, WbMtoI, and local/remote target variants. These are important for PCIe/CXL device traffic analysis because they separate IO-originated cacheable flows from IA-core-originated flows.

The final families are compact: `UNC_CHA_WB_PUSH_MTOI.LLC` and `.MEM` split WbPushMtoI outcomes; `UNC_CHA_WRITE_NO_CREDITS.MC0` through `.MC5` split write-credit starvation by memory controller; and `UNC_CHA_XPT_PREF.SENT0`, `.SENT1`, `.DROP0_NOCRD`, `.DROP1_NOCRD`, `.DROP0_CONFLICT`, and `.DROP1_CONFLICT` describe XPT prefetch success or drop causes.

## Risks And Edge Cases

The first event in the requested line range is incomplete when viewed as a standalone slice. The preceding lines contain the opening fields for `UNC_CHA_TOR_INSERTS.MMCFG`, so merge/reconciliation must combine adjacent chunks before validating per-object completeness.

Many selector objects intentionally omit `UMask`. That can be valid for placeholder or base events, but it makes accidental omission difficult to distinguish from an intentional broad filter. Any future edits should verify against Intel Emerald Rapids uncore event documentation or a known-good perf event table.

The occupancy family is counter-constrained to `Counter: "0"`. Treating these as normal counter `0,1,2,3` events would let perf schedule invalid or misleading measurements. Conversely, changing insert/counting events to counter `0` only would unnecessarily reduce schedulability.

Several descriptions contain rough wording, repeated fragments, or terse placeholders such as event names used as `BriefDescription`. These are user-facing through `perf list`, but they should not be "cleaned up" without preserving the underlying event name, mask, and hardware meaning.

CXL accelerator and expander events encode complex high-bit masks. A single digit error in masks such as `0x10c8968201` versus `0x20c8968201` can silently move an event between accelerator and expander target classes while still parsing as valid JSON.

The final object has no trailing comma and is followed by the closing `]`. Any syntax edit at this tail can break generation for the entire Emerald Rapids cache event table.

## Test Signals

Useful validation signals for this chunk include:

- Running JSON validation on the complete `emeraldrapids/uncore-cache.json`, not just this line slice.
- Running the perf PMU event generation path and confirming `pmu-events.c` is emitted without parse or schema errors.
- Building perf with generated PMU events enabled.
- Running perf's PMU event tests, especially generated-table lookup tests under `tools/perf/tests/pmu-events.c`.
- Using `perf list --details` or JSON list output on an Emerald Rapids-capable build to spot-check representative events from each family: `UNC_CHA_TOR_INSERTS.RRQ`, `UNC_CHA_TOR_OCCUPANCY.IA_MISS_DRD_REMOTE_DDR`, `UNC_CHA_TOR_OCCUPANCY.IO_MISS_PCIRDCUR_REMOTE`, `UNC_CHA_WB_PUSH_MTOI.MEM`, `UNC_CHA_WRITE_NO_CREDITS.MC5`, and `UNC_CHA_XPT_PREF.DROP1_NOCRD`.
- On Emerald Rapids hardware with CHA uncore PMUs available, running `perf stat -a -e` for a few of these events and checking that counter scheduling succeeds and produces plausible package-level counts.

## Cross-Chunk Notes

This document intentionally covers only lines 5352-7547. The preceding chunk is needed for the full `UNC_CHA_TOR_INSERTS.MMCFG` object, and earlier chunks contain the rest of the Emerald Rapids uncore-cache event families. The merge lane should combine all chunks before producing the final per-file research report.
