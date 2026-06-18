<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/lib/cpuidle.h -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/lib/cpuidle.h

## Purpose
Public header for libcpupower CPU idle APIs. It declares functions to query and set idle-state disabled status, read latency/residency/usage/time/name/description, count states, and get global governor/driver.

## Important APIs, Types, And Functions
There is no control flow in the header; callers own returned strings and must understand negative return conventions for disable APIs. Dependencies are `cpuidle.c` and sysfs availability at runtime. Risks include no explicit free helper for returned strings, unsigned state count returning zero for unsupported/error cases, and guard closing comment naming a different header. Test signals are C/C++ compile checks, SWIG binding generation, and Python binding smoke tests.

## Control Flow
There is no control flow in the header; callers own returned strings and must understand negative return conventions for disable APIs. Dependencies are `cpuidle.c` and sysfs availability at runtime. Risks include no explicit free helper for returned strings, unsigned state count returning zero for unsupported/error cases, and guard closing comment naming a different header. Test signals are C/C++ compile checks, SWIG binding generation, and Python binding smoke tests.

## State And Persistence
There is no control flow in the header; callers own returned strings and must understand negative return conventions for disable APIs. Dependencies are `cpuidle.c` and sysfs availability at runtime. Risks include no explicit free helper for returned strings, unsigned state count returning zero for unsupported/error cases, and guard closing comment naming a different header. Test signals are C/C++ compile checks, SWIG binding generation, and Python binding smoke tests.

## Dependencies And Integration Points
There is no control flow in the header; callers own returned strings and must understand negative return conventions for disable APIs. Dependencies are `cpuidle.c` and sysfs availability at runtime. Risks include no explicit free helper for returned strings, unsigned state count returning zero for unsupported/error cases, and guard closing comment naming a different header. Test signals are C/C++ compile checks, SWIG binding generation, and Python binding smoke tests.

## Risks And Edge Cases
There is no control flow in the header; callers own returned strings and must understand negative return conventions for disable APIs. Dependencies are `cpuidle.c` and sysfs availability at runtime. Risks include no explicit free helper for returned strings, unsigned state count returning zero for unsupported/error cases, and guard closing comment naming a different header. Test signals are C/C++ compile checks, SWIG binding generation, and Python binding smoke tests.

## Test Signals
There is no control flow in the header; callers own returned strings and must understand negative return conventions for disable APIs. Dependencies are `cpuidle.c` and sysfs availability at runtime. Risks include no explicit free helper for returned strings, unsigned state count returning zero for unsupported/error cases, and guard closing comment naming a different header. Test signals are C/C++ compile checks, SWIG binding generation, and Python binding smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/lib/cpuidle.h -->
