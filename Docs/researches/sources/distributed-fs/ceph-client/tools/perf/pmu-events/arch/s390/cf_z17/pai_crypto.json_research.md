# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z17/pai_crypto.json

## Purpose
Defines z17 Processor Activity Instrumentation crypto-function events for perf. It provides fine-grained aliases for s390 cryptographic instructions and function variants, including symmetric cipher operations, hashing, message authentication, ECC operations, random number generation, digital signatures, and key wrapping.

## APIs, Types, and Functions
The JSON array has 173 records using `Unit: PAI-CRYPTO`, decimal `EventCode` values starting at 4096, `EventName`, and descriptions. The first alias is `CRYPTO_ALL`, followed by families such as `KM*`, `KMC*`, `KMA_GCM*`, `KMF*`, `KMCTR*`, `KMO*`, `KIMD*`, `KLMD*`, `KMAC*`, `PCC*`, `PRNO*`, `KDSA*`, and `PCKMO*`. `jevents.py` maps `PAI-CRYPTO` to the Linux `pai_crypto` PMU name and emits the codes as event configs.

## Control Flow, State, and Persistence
The file is a static build input. During perf build, every record becomes a generated PMU event. At runtime the aliases are available only when the selected z17 PMU table is active and the kernel exposes the `pai_crypto` PMU. Counts are hardware-maintained PAI counters, not software state in perf.

## Dependencies and Integration
Depends on z17 mapfile selection, the `PAI-CRYPTO` unit mapping in `jevents.py`, and kernel support for the s390 `pai_crypto` PMU. It complements `crypto6.json`: `crypto6.json` exposes aggregate CPU-M-CF coprocessor activity, while this file exposes per-instruction/per-function PAI categories.

## Risks and Test Signals
Risks include off-by-one code mapping across the long contiguous block, retaining IBM-reserved aliases (`IBM_RESERVED_155`, `IBM_RESERVED_156`) as user-visible events, and confusion between encrypted-key and clear-key variants. Because these are specialized hardware counters, build tests only prove syntax and generation, not semantic correctness. Useful signals are JSON parsing, generated alias inspection, `perf list pai_crypto`, and hardware `perf stat` runs for representative KM/KIMD/KDSA/PCKMO events.
