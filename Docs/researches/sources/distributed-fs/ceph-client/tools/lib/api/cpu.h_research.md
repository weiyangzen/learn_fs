<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/cpu.h -->
# sources/distributed-fs/ceph-client/tools/lib/api/cpu.h

## Purpose
`cpu.h` is the public libapi declaration for CPU helper functions. In this subset it exposes only maximum-frequency discovery.

## Important APIs, types, and functions
The header declares `int cpu__get_max_freq(unsigned long long *freq);`. It uses a simple include guard `__API_CPU__` and introduces no types or inline helpers.

## Control flow
There is no executable control flow. Callers include the header, pass a writable `unsigned long long *`, and interpret a zero return as a valid frequency read.

## State and persistence behavior
The header owns no state. The implementation reads sysfs at call time.

## Dependencies and integration points
It is installed by `tools/lib/api/Makefile` as a public `api/cpu.h` header and consumed by tools linked against `libapi.a`.

## Risks and edge cases
The interface does not document units in the prototype; the implementation returns the sysfs `cpuinfo_max_freq` value, normally kHz. Callers must check the return value before using `*freq`.

## Test signals
Compile tests should include this header from C and C++-adjacent tool builds. Runtime behavior is covered through `cpu.c` tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/cpu.h -->
