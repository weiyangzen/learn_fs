# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/common/common/software.json

## Purpose
This 15-entry common file defines perf software event aliases: `cpu-clock`, `task-clock`, page faults, context switches, CPU migrations, minor/major faults, alignment/emulation faults, `dummy`, `bpf-output`, and `cgroup-switches`.

## Important Data Fields
Rows use `Unit` set to `software`, `EventName`, `BriefDescription`, `ConfigCode`, and sometimes `ScaleUnit`. `jevents.py` maps the `software` unit to the software PMU and produces config-based event aliases.

## Control Flow And Integration
These events become generated common aliases used directly by users and indirectly by metrics such as `CPUs_utilized`, context switches per second, migrations per second, and page faults per second. They integrate with kernel perf software counters rather than model-specific hardware PMUs.

## State, Dependencies, Risks, And Tests
The file is static but widely depended on. Risks include config-code mismatch with kernel `PERF_COUNT_SW_*`, duplicate aliases such as `faults`/`page-faults` and `cs`/`context-switches` being altered inconsistently, and unit scaling errors for clock events. Test signals are JSON validation, generated aliases, `perf stat -e task-clock,context-switches,page-faults`, and generic metric runs.
