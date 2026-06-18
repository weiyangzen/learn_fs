## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sandybridge/uncore-interconnect.json

### Purpose
`uncore-interconnect.json` defines nine Sandy Bridge uncore ARB/interconnect events. It covers coherency tracker occupancy and requests, memory-data-return tracker occupancy and requests, write and eviction allocations, and the socket uncore clock fixed counter.

### Important APIs, Types, And Data Fields
The file is an uncore event array:

- `EventName` includes `UNC_ARB_COH_TRK_OCCUPANCY.ALL`, `UNC_ARB_COH_TRK_REQUESTS.ALL`, `UNC_ARB_TRK_OCCUPANCY.*`, `UNC_ARB_TRK_REQUESTS.*`, and `UNC_CLOCK.SOCKET`.
- `Unit: "ARB"` identifies the uncore arbiter/interconnect PMU.
- `EventCode`, `UMask`, and `Counter` encode selectors and counter constraints.
- `CounterMask` appears on occupancy cycle threshold variants.
- `PerPkg: "1"` marks package-level scope.
- `BriefDescription` describes the interconnect condition.

There are no local functions/classes.

### Control Flow And Data Flow
Perf exposes these as ARB uncore events. Runtime data is collected at package scope. `snb-metrics.json` references `UNC_ARB_TRK_REQUESTS.ALL`, `UNC_ARB_COH_TRK_REQUESTS.ALL`, and `UNC_CLOCK.SOCKET` in system-level metrics such as `tma_info_system_dram_bw_use`, `tma_info_system_socket_clks`, and `UNCORE_FREQ`.

### State And Persistence
The file persists static ARB PMU metadata only. Generated perf tables may embed it; runtime counter values are external hardware state.

### Dependencies And Integration Points
The definitions depend on Sandy Bridge uncore ARB PMU support and integrate directly with system-level metrics in `snb-metrics.json`, especially DRAM bandwidth and uncore frequency calculations. They also integrate with perf's uncore PMU discovery and package-scoped event scheduling.

### Risks
Metric formulas rely on exact event names, so renames or unit changes can break system metrics. Incorrect `CounterMask` values on occupancy threshold events would change cycle filtering. `UNC_CLOCK.SOCKET` is a fixed/socket clock signal; incorrect metadata would skew uncore frequency and time-normalized bandwidth metrics.

### Test Signals
Validate JSON and generated event tables, check reference resolution from `snb-metrics.json`, verify `perf list` exposes ARB events, and smoke-test `UNC_CLOCK.SOCKET` plus tracker request events on supported hardware.
