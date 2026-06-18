# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/arch_errno_names.c

## Purpose
This C shim includes the generated architecture-specific errno name lookup array/function implementation for perf environment handling.

## Important APIs, Types, And Functions
The file contains only `#include "trace/beauty/generated/arch_errno_name_array.c"`. The generated file is produced by `arch_errno_names.sh` and provides per-architecture errno-to-name functions plus `arch_syscalls__strerrno_function()`.

## Control Flow
There is no local control flow; compilation injects generated switch tables at this include site.

## State, Dependencies, And Integration
It depends on the build system generating `trace/beauty/generated/arch_errno_name_array.c`. `tools/perf/util/env.c` includes this shim so perf can resolve errno names according to recorded architecture rather than only the host architecture.

## Risks And Test Signals
Risks are missing generated files, stale generated tables, or incorrect include paths. Build failure is the strongest signal. Runtime issues appear as unknown or wrong errno names when processing perf data from non-host architectures.
