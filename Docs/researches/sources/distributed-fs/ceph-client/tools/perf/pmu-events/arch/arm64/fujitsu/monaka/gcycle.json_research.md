<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/gcycle.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/gcycle.json

## Purpose
Monaka global-cycle and frequency-level accounting table. It provides a fixed 100 MHz cycle counter plus per-frequency-level residency counters and retention transition counters.

## APIs, Types, and Functions
The file defines direct event records for `GCYCLES`, `FL0_GCYCLES` through `FL15_GCYCLES`, `RETENTION_GCYCLES`, and `RETENTION_COUNT`. Each record has `EventName`, `EventCode`, and `BriefDescription`.

## Control Flow, State, and Persistence
`jevents.py` converts the JSON records to static perf aliases. Runtime state lives in PMU counters that record frequency-level residency during the measured interval; the JSON holds no mutable state.

## Dependencies and Integration
Depends on Monaka event encodings in the 0x0880-0x08A1 range and the core PMU mapfile. It integrates with cycle, stall, energy, and retention events to normalize performance to frequency behavior and low-power residency.

## Risks and Test Signals
Risks include users treating `GCYCLES` as core clock cycles instead of fixed-rate cycles, unclear frequency-level definitions outside vendor docs, and counter availability differences across firmware. Test signals are `perf stat` visibility, frequency-scaling tests moving counts among `FL*_GCYCLES`, idle tests increasing `RETENTION_GCYCLES` and `RETENTION_COUNT`, and stable 100 MHz-derived deltas for `GCYCLES`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/gcycle.json -->
