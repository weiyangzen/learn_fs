# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/uncore-cache.json lines 12884-12923

## Scope

This chunk covers the final 40 lines of the Skylake Xeon `uncore-cache.json` PMU event table in the vendored Linux `tools/perf` tree. The file is static JSON metadata, not executable program logic. Perf's PMU event generator reads these records and emits compiled event tables so users can request Intel uncore events by symbolic names.

The requested range starts in the middle of a JSON object. Lines 12880-12883, just before this chunk, contain the opening fields for `UNC_H_XSNP_RESP.EXT_RSPI_FWDM`: `BriefDescription`, `Counter`, `Deprecated`, and `EventCode`. Lines 12884-12889 finish that object. The chunk then contains two complete deprecated external-response objects and the final complete deprecated hit object before closing the JSON array at line 12923.

## Purpose

The events in this slice preserve legacy `UNC_H_XSNP_RESP.*` names for core cross-snoop response counters and redirect users to the newer `UNC_CHA_XSNP_RESP.*` naming scheme. They are compatibility aliases for Skylake Xeon CHA uncore PMU events. The aliases remain programmable because they retain the same hardware selector fields as the replacement `UNC_CHA_XSNP_RESP.*` definitions, while the `Deprecated` marker and descriptions tell users to migrate.

The visible events are:

- `UNC_H_XSNP_RESP.EXT_RSPI_FWDM`, partially visible in this chunk, deprecated in favor of `UNC_CHA_XSNP_RESP.EXT_RSPI_FWDM`, with `EventCode: "0x32"` and `UMask: "0x30"`.
- `UNC_H_XSNP_RESP.EXT_RSPS_FWDFE`, deprecated in favor of `UNC_CHA_XSNP_RESP.EXT_RSPS_FWDFE`, with `EventCode: "0x32"` and `UMask: "0x22"`.
- `UNC_H_XSNP_RESP.EXT_RSPS_FWDM`, deprecated in favor of `UNC_CHA_XSNP_RESP.EXT_RSPS_FWDM`, with `EventCode: "0x32"` and `UMask: "0x28"`.
- `UNC_H_XSNP_RESP.EXT_RSP_HITFSE`, deprecated in favor of `UNC_CHA_XSNP_RESP.EXT_RSP_HITFSE`, with `EventCode: "0x32"` and `UMask: "0x21"`.

Earlier full replacement records in the same file describe these as external-request cross-snoop response filters. They count core cross snoops where a cache lookup determines snooping is necessary, then filter by response state transition: response I to forwarded M, response S to forwarded F/E, response S to forwarded M, or any response to hit F/S/E.

## Important Data Fields

Each object uses the perf PMU event JSON schema used under `tools/perf/pmu-events`:

- `EventName` is the symbolic event exposed through perf's generated event tables. In this chunk the names use the legacy `UNC_H_XSNP_RESP` prefix.
- `BriefDescription` is user-facing text shown by perf and, for these aliases, carries the deprecation redirect to the corresponding `UNC_CHA_XSNP_RESP` event.
- `Counter` is `"0,1,2,3"` for the complete visible objects and for the partially visible first object from the preceding lines. These events can be scheduled on any listed CHA uncore counter.
- `Deprecated` is `"1"` for every visible alias, causing the generated `struct pmu_event` to carry deprecation metadata.
- `EventCode` is `"0x32"` for this cross-snoop response event family.
- `UMask` selects the external request and response subtype. The visible masks are `0x30`, `0x22`, `0x28`, and `0x21`.
- `Experimental` is `"1"` for every visible alias, warning that the metadata is marked experimental in this vendored perf table.
- `PerPkg` is `"1"`, so measurements are package-scoped uncore events rather than thread-local counters.
- `Unit` is `"CHA"`, binding the aliases to Intel Cache/Home Agent uncore PMUs.

There is no `PublicDescription` in these deprecated alias records. The non-deprecated `UNC_CHA_XSNP_RESP.*` records earlier in the file carry longer descriptions for the same event code and masks.

## APIs, Types, And Generated Representation

This JSON file does not define local functions, classes, or C types. Its effective API is the generated perf PMU event table:

- `tools/perf/pmu-events/jevents.py` reads JSON event files under `tools/perf/pmu-events/arch/<arch>/<model>/`.
- The generated C uses `struct pmu_event` from `tools/perf/pmu-events/pmu-events.h`, including fields such as `name`, `event`, `desc`, `pmu`, `unit`, `perpkg`, and `deprecated`.
- `pmu_events_table__for_each_event()` iterates generated events for listing and alias setup.
- `pmu_events_table__find_event()` resolves a symbolic event name, such as `UNC_H_XSNP_RESP.EXT_RSPS_FWDM`, against the generated table.
- Runtime perf code then maps the generated alias to the hardware event selector string built from `EventCode`, `UMask`, and related fields.

For this chunk, `Deprecated`, `EventCode`, `UMask`, `Unit`, and `PerPkg` are the important generated semantics. The event aliases should still resolve, but consumers should prefer the replacement `UNC_CHA_XSNP_RESP.*` names.

## Control Flow

The JSON has no direct control flow. Its build-time and runtime flow is:

1. The perf build runs the PMU event generation path before building the perf binary.
2. `jevents.py` traverses the Skylake Xeon JSON files, including `arch/x86/skylakex/uncore-cache.json`.
3. The generator parses the event objects, including these final deprecated aliases, and emits generated PMU event table data.
4. `pmu-events.c` is compiled into the perf build.
5. At runtime, perf matches the running x86 CPU against `arch/x86/mapfile.csv`; Skylake Xeon CPUIDs matching `GenuineIntel-6-55-[01234]` map to the `skylakex` directory in this tree.
6. `perf list` can display the legacy alias names, with deprecation metadata available from the generated table.
7. `perf stat -e <event>` resolves the alias and programs the package-level CHA uncore PMU counter using event code `0x32` plus the selected mask.

Within the full file, these records are part of a final compatibility block of `UNC_H_*` aliases. This chunk specifically closes the external-request subfamily and then closes the top-level JSON array.

## State And Persistence Behavior

Persistent state is limited to checked-in JSON metadata and any generated `pmu-events.c` output created during the perf build. The source file itself does not create files, maintain mutable process state, or store measurements.

Runtime state lives in hardware uncore counters on supported Skylake Xeon systems. Because `PerPkg` is set, counts are package-level CHA measurements. Because these are cross-snoop response filters, the measured state reflects cache/home-agent snoop response activity for external requests, split by the selected response category.

The deprecation state is also persistent metadata. `Deprecated: "1"` lets downstream perf UI and table consumers distinguish these legacy aliases from the preferred `UNC_CHA_XSNP_RESP.*` records. Removing these aliases would be a user-visible compatibility change for scripts that still use `UNC_H_XSNP_RESP.*` event names.

## Dependencies And Integration Points

This chunk integrates with the Linux perf PMU event stack:

- `tools/perf/pmu-events/README` documents the JSON input format, model directories, `mapfile.csv`, and generation of `pmu-events.c`.
- `tools/perf/pmu-events/jevents.py` consumes the JSON and emits generated C event tables.
- `tools/perf/pmu-events/pmu-events.h` defines `struct pmu_event` and table lookup APIs used by the generated data.
- `tools/perf/pmu-events/arch/x86/mapfile.csv` maps Skylake Xeon CPU IDs to the `skylakex` model directory.
- The x86 uncore PMU driver must expose CHA PMUs and counters compatible with event code `0x32` for the aliases to count on hardware.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file belongs to a vendored Linux perf tooling subtree. It has no direct integration with CephFS client control flow, distributed filesystem metadata state, network protocols, or storage persistence.

## Risks And Edge Cases

The first record is partial in this chunk. A line-range-only reader sees `EventName`, `Experimental`, `PerPkg`, `UMask`, and `Unit` for `UNC_H_XSNP_RESP.EXT_RSPI_FWDM`, but its deprecation description, counter list, deprecated flag, and event code are on immediately preceding lines. The later merge lane must use adjacent chunk context before validating complete object coverage.

The chunk is the end of the JSON array. Any edit here must preserve valid comma placement: the final object has no trailing comma and is followed by `]`. A syntax error at this tail would prevent `jevents.py` from parsing the whole `uncore-cache.json` file.

The compatibility aliases intentionally duplicate the replacement events' selector values. A mismatched `UMask` between `UNC_H_XSNP_RESP.EXT_RSPS_FWDM` and `UNC_CHA_XSNP_RESP.EXT_RSPS_FWDM`, for example, would silently make the deprecated alias count a different snoop-response class than its replacement. The visible masks match the earlier replacement records in this file.

All visible aliases are marked both deprecated and experimental. Users may still rely on them for old scripts, but new documentation and examples should prefer `UNC_CHA_XSNP_RESP.*`.

The brief deprecation strings are the only explanatory text in these alias records. If perf UI suppresses deprecated events by default or does not show `BriefDescription`, users may not see the migration target unless they ask for detailed listings.

## Test Signals

Useful validation signals for this chunk include:

- Run JSON validation on the complete `skylakex/uncore-cache.json`, not just this partial line range.
- Run the perf PMU event generation path and confirm `jevents.py` accepts the file and emits generated event-table entries.
- Build perf and confirm `struct pmu_event` records for the four visible `UNC_H_XSNP_RESP.EXT_*` aliases carry `deprecated = true`, `perpkg = true`, and `unit = "CHA"`.
- Use generated-table lookup tests or a local perf build to confirm both old and new names resolve, for example `UNC_H_XSNP_RESP.EXT_RSPS_FWDFE` and `UNC_CHA_XSNP_RESP.EXT_RSPS_FWDFE`.
- Compare generated selector strings for each alias against its replacement event to ensure `event=0x32` and the same `umask` are preserved.
- On Skylake Xeon hardware with CHA uncore PMUs exposed, run package-wide `perf stat` for a representative deprecated alias and its `UNC_CHA_*` replacement under the same workload and confirm scheduling succeeds and counts are consistent.

## Cross-Chunk Notes

This document intentionally covers only lines 12884-12923. Earlier chunks contain the complete beginning of `UNC_H_XSNP_RESP.EXT_RSPI_FWDM`, the rest of the deprecated `UNC_H_XSNP_RESP.*` compatibility block, and the primary `UNC_CHA_XSNP_RESP.*` replacement records with full public descriptions. The final per-file research document should merge those views before making whole-file claims about all `UNC_H` aliases or all cross-snoop response event variants.
