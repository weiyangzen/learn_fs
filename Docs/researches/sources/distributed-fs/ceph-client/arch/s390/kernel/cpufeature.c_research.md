# sources/distributed-fs/ceph-client/arch/s390/kernel/cpufeature.c

## Purpose
Implements s390's `cpu_have_feature()` predicate for module initialization and feature-gated code. It maps abstract Linux CPU feature IDs to ELF hwcap bits, facility bits, or machine-feature bits.

## Important APIs, Types, And Functions
`struct s390_cpu_feature` stores a feature type and number. `s390_cpu_features[]` maps `S390_CPU_FEATURE_MSA`, `VXRS`, `UV`, and `D288`. `cpu_have_feature(unsigned int num)` validates the index and dispatches to `elf_hwcap`, `test_facility()`, or `test_machine_feature()`.

## Control Flow
Callers pass a feature enum. The function warns on out-of-range IDs, then selects a backend based on the table entry type and returns a boolean capability result.

## State And Persistence
The static feature table is read-only runtime state. Actual capability state lives in global hwcap, facility, and machine-feature discovery data.

## Dependencies And Integration Points
Depends on cpufeature core, s390 ELF hwcap numbering, facility probing, and machine feature probing. It provides a generic feature API for loadable modules.

## Risks And Edge Cases
Table entries must be kept in sync with `MAX_CPU_FEATURES` and feature enum definitions. Unknown type values warn and return false. HWCAP and facility numbering mistakes silently misgate code.

## Test Signals
Signals include module tests for each feature, boot logs for WARN_ON paths under fault injection, and cross-checks against `/proc/cpuinfo` or facility data on systems with and without UV/VX/MSA.
