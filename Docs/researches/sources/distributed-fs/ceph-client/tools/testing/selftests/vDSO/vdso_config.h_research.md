<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vdso_config.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vdso_config.h

## Purpose
Architecture mapping table for vDSO symbol versions and symbol names.

## Important APIs, Types, and Functions
VDSO_VERSION, VDSO_NAMES, VDSO_32BIT, versions[], names[][].

## Control Flow
Preprocessor selects the version index and name family for each supported architecture, then tests index into versions/names to resolve gettimeofday, clock_gettime, time, getcpu, getrandom, and time64 symbols.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Depends on compiler architecture macros and exported vDSO ABI names.

## Risks and Edge Cases
Adding a new architecture or renamed symbol requires table updates; wrong index causes tests to skip or fail symbol lookup.

## Test Signals
All vDSO tests use this table; successful symbol resolution validates it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vdso_config.h -->
