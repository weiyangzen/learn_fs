# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z196/crypto.json

## Purpose
Defines z196 CPU-M-CF crypto counter aliases for aggregate PRNG, SHA, DEA, and AES function, cycle, blocked-function, and blocked-cycle accounting.

## APIs, Types, and Functions
The file contains 16 records with `Unit: CPU-M-CF`, event codes 64 through 79, `EventName`, `BriefDescription`, and `PublicDescription`. It follows a four-counter pattern per crypto class: functions issued, cycles busy, functions blocked by another CPU, and blocked cycles.

## Control Flow, State, and Persistence
Perf builds the records into z196 PMU event tables via `jevents.py`. Runtime behavior is alias lookup and `cpum_cf` counter programming on matched z196 CPUs. The JSON file itself has no execution or persistence beyond generated tables.

## Dependencies and Integration
Depends on z196 mapfile selection, `CPU-M-CF` unit conversion, and kernel support for the crypto activity counter set. The same event-code block is reused by zEC12 and extended by z17 `crypto6.json` with ECC counters.

## Risks and Test Signals
Risks include exposing counters when crypto counter-set authorization is absent, and semantic ambiguity where PRNG descriptions mention shared DEA/AES/SHA coprocessors. Test signals are successful event generation, `perf list` visibility, and hardware readings for each of the four counter families.
