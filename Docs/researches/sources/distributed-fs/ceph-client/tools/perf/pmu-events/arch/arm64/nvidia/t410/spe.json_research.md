# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/spe.json

## Purpose
This 10-entry T410 Arm64 topic file exposes Statistical Profiling Extension sample-feed events: sample population, feed, filtration, collision, and feeds by branch/load/store/op/event/latency class. It lets perf users count SPE sampling pipeline behavior in addition to recording SPE samples.

## Important Data Fields
Entries consist of `ArchStdEvent` plus `PublicDescription`. The names include `SAMPLE_POP`, `SAMPLE_FEED`, `SAMPLE_FILTRATE`, `SAMPLE_COLLISION`, and class-specific `SAMPLE_FEED_*` events. No local `EventCode` fields are present.

## Control Flow And Integration
During generation, these standard-event references resolve into PMU event encodings and descriptions. Runtime integration is through perf's selected T410 event table; users can list and count these aliases with the regular PMU event path, while detailed SPE tracing remains handled by perf's Arm SPE machinery outside this JSON.

## State, Dependencies, Risks, And Tests
The file has no persistence or control logic. It depends on Arm SPE architectural event definitions and T410 PMU support. Risks include exposing events on systems where SPE or the relevant filters are unavailable, or confusion between counting sample-feed events and collecting sampled records. Tests should include JSON validation, generated alias presence, and hardware checks comparing `perf list` with supported PMU capabilities.
