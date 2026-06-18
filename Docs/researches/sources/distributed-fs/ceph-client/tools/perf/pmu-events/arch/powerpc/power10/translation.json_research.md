# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power10/translation.json

## Purpose

This small file defines three POWER10 raw PMU events for store forwarding and store completion behavior: `PM_ST_FWD`, `PM_ST_CMPL`, and `PM_ST_MISS_L1`. Despite the directory name, the visible events are store/cache related rather than broad address-translation events.

## APIs, types, and schema

The schema is the raw event contract: `EventCode`, `EventName`, and `BriefDescription`. `PM_ST_MISS_L1` is referenced by `metrics.json` for L1 store miss rate; `PM_ST_FWD` and `PM_ST_CMPL` are direct user-visible raw events.

## Control flow and integration

Perf build generation converts these three entries into the POWER10 event table. At runtime, users can select them directly, and metrics can reference them by name. The key integration is the `L1_ST_MISS_RATE` formula in `metrics.json`, which uses `PM_ST_MISS_L1`.

## State and persistence

There is no mutable state. Persistence is the stable event-name to event-code mapping compiled into perf. Because the file is tiny, omissions are easy to detect but misplacement under `translation.json` may surprise maintainers.

## Dependencies

Dependencies are POWER10 PMU encodings and perf's `jevents.py` raw event ingestion. `metrics.json` is a direct dependent for store miss rate.

## Risks

The filename suggests translation coverage, but the content is store forwarding, completion, and L1 store miss. That mismatch can cause maintainers to add or search for events in the wrong category. Missing `PublicDescription` limits context. If `PM_ST_MISS_L1` is wrong or unavailable, the derived store miss metric breaks.

## Test signals

Validate JSON, ensure unique event codes, run PMU event generation, and check that `L1_ST_MISS_RATE` resolves. Direct `perf stat -e PM_ST_MISS_L1` on POWER10 is the most direct runtime smoke test.
