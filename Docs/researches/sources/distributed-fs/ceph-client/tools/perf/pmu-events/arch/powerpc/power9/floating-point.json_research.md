# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power9/floating-point.json

## Purpose

This small POWER9 topic file defines 6 PMU events assigned to the floating-point JSON partition. The entries are mixed: one marked-load L2 dispatch-conflict latency counter, one IFU memory locality threshold counter, one radix page-walk cache reload counter, one completion flush counter, one marked DERAT miss page-size counter, and one threshold-not-met counter. The file therefore behaves more like a topic shard from the upstream PMU catalog than a pure floating-point-only event set.

## APIs, types, and schema

The JSON entries use `EventName`, `EventCode`, and `BriefDescription`. `jevents.py` maps these fields into `JsonEvent` instances and ultimately compact C event rows. No `MetricName` or `MetricExpr` objects are present, so this file contributes raw selectable events only.

## Control flow and integration

POWER9 model selection comes from `arch/powerpc/mapfile.csv`; the build then treats every JSON file under `power9` as part of the same generated PMU model. This file's events are read by `read_json_events`, assigned the topic derived from the file name, sorted with other `default_core` events, and emitted into the generated `pmu-events.c`. At runtime, perf can list and select the lower-case versions of these event names.

## State, persistence, and dependencies

The file stores static PMU metadata. It depends on the perf JSON schema and the POWER9 event encodings remaining valid. Because it includes threshold and marked-event semantics, correct use also depends on kernel PMU support for the relevant POWER9 counter modes.

## Risks and test signals

The main risk is semantic discoverability: the filename suggests floating-point, but several events relate to translation, threshold, and flush behavior. Automated users should rely on event names and descriptions rather than the file topic alone. Test signals are `jq empty`, successful `jevents.py` generation, no duplicate generated event names, and targeted `perf list` checks for the six event names on POWER9.
