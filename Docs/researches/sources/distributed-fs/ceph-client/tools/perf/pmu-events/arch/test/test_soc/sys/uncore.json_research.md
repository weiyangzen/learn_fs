# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/test/test_soc/sys/uncore.json

## Purpose
Defines synthetic system uncore PMU fixtures for alternate config fields, compatibility matching, node-type filtering, and sys PMU unit names.

## APIs, Types, and Functions
The file has three records: `sys_ddr_pmu.write_cycles` with `EventCode`, `sys_ccn_pmu.read_cycles` with `ConfigCode`, and `sys_cmn_pmu.hnf_cache_miss` with `EventidCode` plus `NodeType`. All include `Unit` and `Compat`; the compatibility values cover a plain string, a hex-like value, and a regex-style pattern.

## Control Flow, State, and Persistence
During generation `jevents.py` chooses the event encoding field in priority order: `ConfigCode` becomes `config=...`, `EventidCode` becomes `eventid=...`, otherwise `EventCode` becomes `event=...`. Runtime tests can then verify generated sys-PMU aliases and compatibility metadata. The JSON itself stores no mutable state.

## Dependencies and Integration
Depends on parser support for `ConfigCode`, `EventidCode`, `NodeType`, `Compat`, and sys PMU `Unit` names. It integrates with PMU event tests that check system PMU handling separately from core CPU fixtures.

## Risks and Test Signals
Risks include wrong precedence between event/config/eventid fields, dropped `NodeType`, and broken compatibility-pattern serialization. Test signals are generated output comparisons for `config=0x2c`, `eventid=0x1`, `event=0x2b`, retained `Compat`, and retained `NodeType`.
