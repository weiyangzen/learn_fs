<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/energy.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/energy.json

## Purpose
Monaka energy-event topic table. It exposes core, L3 cache, and LDO-loss energy counters for perf power and efficiency analysis.

## APIs, Types, and Functions
The file defines three direct records: `EA_CORE` at `0x01F0`, `EA_L3` at `0x03F0`, and `EA_LDO_LOSS` at `0x03F1`. Each uses the standard perf event JSON fields `EventName`, `EventCode`, and `BriefDescription`.

## Control Flow, State, and Persistence
The event table is generated statically by `jevents.py` and selected at runtime for Monaka cores. Counter values are transient PMU readings; the only persistent behavior here is the checked-in alias-to-code mapping.

## Dependencies and Integration
Depends on Monaka hardware exposing energy events through the core PMU encoding space. It integrates with cycle, frequency-level, cache, and stall events to compute energy per work, per cycle, or per memory behavior in user tooling.

## Risks and Test Signals
Risks include unclear scaling units, model-specific counter width/overflow behavior, and unsupported counters on early silicon or virtualized environments. Test signals are `perf list` visibility, nonzero counts under active workloads, stable deltas over repeated intervals, and correlation between `EA_CORE`, `EA_L3`, workload intensity, and frequency-state counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/energy.json -->
