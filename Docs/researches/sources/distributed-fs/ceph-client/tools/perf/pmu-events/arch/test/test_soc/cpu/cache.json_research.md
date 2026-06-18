# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/test/test_soc/cpu/cache.json

## Purpose
Tests the `ArchStdEvent` dereference mechanism for perf PMU event JSONs by importing the synthetic standard `L3_CACHE_RD` event.

## APIs, Types, and Functions
The file contains one object with `ArchStdEvent: L3_CACHE_RD`. It intentionally omits `EventName`, `EventCode`, and descriptions so the generator must resolve them from `arch/test/arch-std-events.json`.

## Control Flow, State, and Persistence
During generation, `jevents.py` detects `ArchStdEvent`, looks up the standard event by name, and substitutes/merges the referenced metadata into the generated output. The fixture has no independent runtime state or hardware behavior.

## Dependencies and Integration
Depends directly on `arch/test/arch-std-events.json` and the architecture-standard lookup path described in the pmu-events README. It is part of the test SOC CPU fixture set consumed by perf PMU event tests.

## Risks and Test Signals
Risks are missing or duplicate standard-event names and regressions where local fields no longer inherit correctly. Test signals include generated output containing event code `0x40` and description text from the standard event, plus PMU event unit tests that validate standard-event expansion.
