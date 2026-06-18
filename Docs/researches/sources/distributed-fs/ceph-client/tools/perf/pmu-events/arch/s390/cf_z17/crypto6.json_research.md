# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z17/crypto6.json

## Purpose
Defines the IBM z17 CPU Measurement Counter Facility crypto counter-set aliases for perf. The file extends the traditional s390 crypto counters with ECC activity counters and lets users name PRNG, SHA, DEA, AES, and ECC function, cycle, and blocked-work counters instead of supplying raw event numbers.

## APIs, Types, and Functions
This is a JSON array of 20 PMU event records. Each record uses `Unit: CPU-M-CF`, decimal `EventCode` values 64 through 83, `EventName`, `BriefDescription`, and `PublicDescription`. `jevents.py` converts `CPU-M-CF` to the Linux `cpum_cf` PMU name, lowercases event names for generated aliases, and emits `event=<code>` strings in generated `pmu-events.c`.

## Control Flow, State, and Persistence
There is no runtime control flow in the file. At build time the perf PMU event generator traverses the z17 directory selected by `arch/s390/mapfile.csv`, parses the array, and persists the records as compiled C string tables. At runtime perf matches an IBM 9175/9176 z17 CPU, exposes these aliases through `perf list`, and passes the selected event code to the kernel `cpum_cf` PMU.

## Dependencies and Integration
Depends on the s390 mapfile z17 entry, `tools/perf/pmu-events/jevents.py`, `pmu-events.h`, and the kernel s390 CPU-M-CF driver. It complements z17 `extended.json`, `pai_crypto.json`, and `pai_ext.json`; the same event names are used by users and may be referenced by metrics if added later.

## Risks and Test Signals
Risks are incorrect event-code numbering, mismatched z17 facility availability, and naming drift from IBM documentation. ECC counters are z17-specific additions relative to older `crypto.json` tables, so backporting or sharing this file with older CPU models would expose unsupported aliases. Test signals include `jq` schema validation, perf jevents generation, `perf list` on z17, and checking `perf stat -e cpum_cf/<alias>/` or the generated alias against kernel PMU acceptance.
