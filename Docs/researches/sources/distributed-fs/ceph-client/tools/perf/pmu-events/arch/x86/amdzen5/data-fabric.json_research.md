# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen5/data-fabric.json

Purpose: Defines 204 AMD Zen 5 Data Fabric PMU events for perf. The file maps package-level DFPMC counters to DRAM channel, upstream IO root complex, core-to-fabric interface, and cross-socket link traffic so `perf list`, `perf stat`, and metric expressions can name fabric bandwidth events instead of raw event/umask pairs.

Important APIs/types/functions: This is declarative PMU schema data, not executable code. Each object uses perf JSON fields `EventName`, `EventCode`, `UMask`, `Unit: DFPMC`, `PerPkg: "1"`, and `PublicDescription`. Event families encode local, remote, and local-or-remote socket read/write data beats for 12 DRAM channels, 8 IO root complexes, 16 CFI instances, and 6 cross-socket links.

Control flow: At perf build/runtime, pmu-events tooling parses the array, associates events with the Zen 5 model map, and exposes names such as `local_or_remote_socket_read_data_beats_dram_0` for command-line selection. `recommended.json` depends on many of these exact event names when computing fabric bandwidth metrics by summing channels and dividing by `duration_time`.

State and persistence: There is no mutable runtime state in this file. The persistent contract is the stable event-name to raw encoding mapping; `PerPkg` means counts are interpreted at package/socket scope rather than per logical CPU.

Dependencies and integration: Integrates with Linux perf's JSON pmu-events generator, AMD Zen 5 model tables, the `DFPMC` uncore PMU driver, and Zen 5 recommended metrics for DRAM, DMA, CFI, and link bandwidth. The channel counts and `ScaleUnit` assumptions in metrics must match these event inventories.

Risks: The large repeated matrix is vulnerable to off-by-one channel/link omissions, mismatched local/remote umasks, and stale channel counts on SKUs with fewer exposed counters. Renaming any event breaks `recommended.json` formulas. Per-package uncore events can be misread if users aggregate them like per-core counters.

Test signals: Validate JSON syntax, run `perf list` on Zen 5 hardware or generated pmu-events tables, sample representative DRAM/IO/CFI/link events, and run the dependent recommended bandwidth metrics to ensure every referenced `data_fabric` event resolves.
