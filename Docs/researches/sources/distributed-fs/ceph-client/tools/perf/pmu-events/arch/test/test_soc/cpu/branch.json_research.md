# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/test/test_soc/cpu/branch.json

## Purpose
Defines two synthetic branch-prediction events for the perf test architecture. The file exists to test normal per-topic event parsing for CPU PMU JSONs.

## APIs, Types, and Functions
The array contains `bp_l1_btb_correct` with event code `0x8a` and `bp_l2_btb_correct` with event code `0x8b`, each with a brief description. There is no `Unit`, so `jevents.py` maps them to the default core PMU marker.

## Control Flow, State, and Persistence
At build/test generation time the records become generated test PMU aliases. Runtime semantics are not tied to real hardware; the file is fixture data for parser and lookup tests.

## Dependencies and Integration
Depends on the `arch/test` map/test setup and the default-unit behavior in `jevents.py`. It integrates with perf tests that compare generated events from `pmu-events.c` against expected fixture output.

## Risks and Test Signals
Risks include accidental treatment as a real hardware table, default PMU mapping regressions, and event-name case handling. Test signals are `tools/perf/tests/pmu-events.c` expectations, generated alias strings, and successful JSON traversal of the test SOC CPU directory.
