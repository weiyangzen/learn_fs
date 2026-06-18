# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/test/test_soc/cpu/uncore.json

## Purpose
Provides synthetic uncore PMU event fixtures for unit-to-PMU conversion, uncore field encoding, hyphenated event names, and vendor-specific unit names.

## APIs, Types, and Functions
The file contains seven events across units `hisi_sccl,ddrc`, `CBO`, `hisi_sccl,l3c`, `imc_free_running`, and `imc`. Fields include `EventCode`, `UMask`, `Counter`, `CounterMask`, `Invert`, `EdgeDetect`, `PublicDescription`, and `Unit`. `jevents.py` maps `CBO` to `uncore_cbox`, preserves Hisilicon comma units, and maps unknown units like `imc` to `uncore_imc`.

## Control Flow, State, and Persistence
Generation reads these records and emits uncore PMU aliases with unit-specific PMU names. The entries are fixtures, so runtime behavior is focused on parser/test expectations rather than real uncore hardware.

## Dependencies and Integration
Depends on `unit_to_pmu()` mapping in `jevents.py` and PMU event tests that verify generated PMU names and event encodings. The hyphenated `event-hyphen` and `event-two-hyph` names exercise name sanitization and lookup behavior.

## Risks and Test Signals
Risks include breaking special unit mappings, mishandling comma-containing unit names, and formatting optional fields incorrectly. Test signals are generated table comparisons for `uncore_cbox`, `hisi_sccl,*`, `uncore_imc*`, and encoded fields such as `cmask`, `inv`, and `edge`.
