## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sandybridge/uncore-cache.json

### Purpose
`uncore-cache.json` defines 25 Sandy Bridge uncore CBOX cache events. It covers LLC/CBOX lookup outcomes by request type and MESI state plus cross-snoop response categories for eviction, external snoop, and cross-core snoop traffic.

### Important APIs, Types, And Data Fields
The file uses the uncore event schema:

- `EventName` includes `UNC_CBO_CACHE_LOOKUP.*` and `UNC_CBO_XSNP_RESPONSE.*`.
- `Unit: "CBOX"` identifies the uncore PMU block.
- `EventCode` and `UMask` encode CBOX selectors.
- `Counter` generally allows `0,1`.
- `PerPkg: "1"` marks package-level uncore scope.
- `BriefDescription` provides user-facing help.

There are no functions or classes.

### Control Flow And Data Flow
Perf's uncore event handling maps these symbolic names to CBOX PMU events. Runtime counting occurs per package/CBOX rather than per core thread. Users can select lookup events such as read/write/any lookups in `I`, `M`, `E/S`, or `MESI` states, or snoop response events such as `HITM_XCORE` and `MISS_EXTERNAL`.

### State And Persistence
The file persists static uncore event metadata. Runtime uncore counter values are not stored here.

### Dependencies And Integration Points
Definitions depend on Sandy Bridge uncore CBOX PMU semantics and package-scoped perf uncore support. They integrate with perf list/stat uncore handling and with any metrics or user workflows that inspect LLC coherence behavior. This file is adjacent to, but distinct from, core cache events in `cache.json`.

### Risks
Uncore PMUs have different unit names, scopes, and counter constraints than core PMUs. Mislabeling `Unit`, `PerPkg`, or counter availability can cause perf to expose events under the wrong PMU or fail scheduling. MESI-state umasks are compact and easy to transpose, which would corrupt LLC/coherence diagnostics.

### Test Signals
Validate JSON, ensure `perf list` exposes CBOX events, check generated unit names and package scope, and smoke-test a representative lookup and snoop response event on supported Sandy Bridge uncore hardware.
