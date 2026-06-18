# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sierraforest/uncore-io.json

## Purpose
Defines the Sierra Forest uncore I/O PMU event catalog for Linux perf. The file is a 168-entry JSON array of `UNC_IIO_*` events consumed by the perf PMU events table generator and runtime event resolver so users can select named Integrated I/O events instead of programming raw event selectors manually.

## Important APIs, Types, And Event Groups
The data contract is the perf PMU event JSON object schema. Every entry carries `EventName`, `EventCode`, `BriefDescription`, `Counter`, `PerPkg`, `PortMask`, and `Unit`; most entries also carry `UMask`, `FCMask`, and optional `Experimental` or `Deprecated` flags. `Unit` is consistently `IIO`, which routes aliases to the uncore IIO PMU rather than core PMU counters. `PerPkg: "1"` identifies package-scoped counting. `Counter` lists allowed programmable counter slots, generally `0,1,2,3`.

The event surface covers IIO clockticks, completion-buffer inserts and occupancy, data and transaction requests by CPU and of CPU, IOMMU activity for multiple IOMMU blocks, outstanding request counters, target-split request counts, and posted-write-table occupancy. The file uses repeated event-name suffixes such as `.PART0` through `.PART7`, `.ALL_PARTS`, `.READ`, `.WRITE`, `.ALLOC`, `.DEALLOC`, `.ATS_*`, and target classes to expose hardware filters as separate perf aliases.

## Control Flow
There is no executable control flow in the file. At build time, perf tooling parses the JSON array, validates known fields, and emits event table data. At runtime, perf resolves an alias such as `UNC_IIO_COMP_BUF_INSERTS.CMPD.PART3` into the encoded selector fields: event code, umask/filter fields, port mask, counter mask, and the `IIO` PMU unit. The user's measurement flow is therefore declarative: select alias, perf maps it to the matching uncore PMU, and the kernel driver programs hardware counters with the encoded fields.

## State And Persistence
The file persists static hardware event metadata in the repository. It does not read or write runtime state. When compiled into perf, the aliases become part of perf's generated PMU event tables; live counter values are held only by kernel perf events and hardware PMU registers during a measurement session. The `Deprecated` marker on the misspelled `UNC_IIO_NUM_OUSTANDING_REQ_FROM_CPU` entry preserves compatibility while steering users toward the correctly spelled alias.

## Dependencies And Integration Points
The file depends on perf's JSON PMU schema and on Sierra Forest uncore IIO PMU support in the Linux kernel. It integrates with sibling Sierra Forest event files through the architecture/mapfile selection mechanism, where CPU identification chooses this directory's catalogs. The `PortMask` and `FCMask` fields are especially important integration points because they exercise uncore-specific encodings not present in simple core event files.

## Risks
Encoding drift is the main risk: a wrong `EventCode`, `UMask`, `PortMask`, or `FCMask` silently produces misleading performance data. Repeated partition aliases increase copy/paste risk, especially where `.ALL_PARTS` uses a broad mask and individual parts use single-bit masks. `Experimental` events may reflect less stable hardware documentation. Alias spelling compatibility is another risk because changing or removing the deprecated misspelled event could break existing perf scripts.

## Test Signals
Useful tests include `jq empty` JSON validation, perf PMU event table generation, and `perf list` checks on a Sierra Forest-capable build to confirm aliases appear under the IIO unit. Runtime smoke tests should try representative clocktick, completion-buffer, data-request, IOMMU, outstanding-request, and occupancy aliases and verify that perf can open the event on supported hardware without raw encoding errors.
