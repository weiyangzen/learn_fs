# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/cascadelakex/counter.json

Purpose: Declares the number of fixed and programmable counters available for Cascade Lake Xeon PMU units. This is capacity metadata consumed by the perf pmu-events generator and runtime tooling so perf can describe and schedule events for core and uncore units accurately.

Important schema and entries: The file contains 10 objects with `Unit`, `CountersNumFixed`, and `CountersNumGeneric`. The `core` unit reports 3 fixed counters and 4 generic counters. Uncore units report no fixed counters except `iMC` and `UBOX`, each with 1 fixed counter. Generic counter counts are `CHA=4`, `IIO=4`, `IRP=2`, `UPI=4`, `M2M=4`, `iMC=4`, `M3UPI=3`, `PCU=4`, and `UBOX=2`.

Control flow: Build-time traversal treats this as PMU metadata alongside event and metric files. Runtime perf uses the generated PMU descriptions with kernel-exposed PMUs to reason about which events can be placed together and how many counters are available for a unit, especially when metrics combine core events with CHA, iMC, IIO, UPI, PCU, UBOX, M2M, IRP, or M3UPI events.

State and persistence behavior: The file has no mutable state and no event aliases. Its persisted effect is the generated counter-capacity table. Changes affect scheduling behavior and user-visible PMU information even though no `EventName` or `MetricName` is introduced.

Dependencies and integration: The unit names must match the `Unit` values used in sibling uncore event JSON files and the PMU naming/mapping logic in `jevents.py` and perf's PMU discovery code. It also indirectly supports `clx-metrics.json` formulas that rely on uncore bandwidth, latency, and socket-level metrics because those formulas can require several events from the same unit in one run.

Risks: Incorrect counter counts cause practical scheduling bugs rather than parser failures. Overstating generic counters can make perf attempt impossible event groups; understating them can force unnecessary multiplexing or rejected metric groups. Unit spelling is a contract: if it drifts from event files or kernel PMU names, generated metadata may not attach to the intended PMU. Fixed-counter declarations for `iMC` and `UBOX` are especially easy to overlook because most uncore units list zero fixed counters.

Test signals: Validate JSON parsing and generated table output through a perf build and `perf test pmu-events`. On Cascade Lake hardware, check `perf list` for expected core and uncore PMUs, run multi-event groups near each unit's counter limit, and compare behavior for CHA/IIO/UPI/iMC/UBOX events against kernel PMU capabilities. Metric smoke tests that use uncore-heavy formulas from `clx-metrics.json` can expose bad capacity metadata through scheduling failures or unexpected multiplexing.
