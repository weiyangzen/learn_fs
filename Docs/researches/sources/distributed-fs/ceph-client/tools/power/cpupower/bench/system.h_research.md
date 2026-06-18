<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/bench/system.h -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/bench/system.h

## Purpose
Declares cpufreq-bench system helper functions and includes `parse.h` for `struct config`. It exposes timing, governor/affinity/priority setters, and user/system preparation routines.

## Important APIs, Types, And Functions
There is no runtime control flow or state in the header. Dependencies are `parse.h` and the implementations in `system.c`. Risks include no include guard, `get_time()` declaration missing an explicit `int`-free prototype style distinction from implementation `long long int`, and exposing setters that mutate global process/kernel state without documenting restoration. Test signals are strict compiler warnings and successful linkage from `main.c`/`benchmark.c`.

## Control Flow
There is no runtime control flow or state in the header. Dependencies are `parse.h` and the implementations in `system.c`. Risks include no include guard, `get_time()` declaration missing an explicit `int`-free prototype style distinction from implementation `long long int`, and exposing setters that mutate global process/kernel state without documenting restoration. Test signals are strict compiler warnings and successful linkage from `main.c`/`benchmark.c`.

## State And Persistence
There is no runtime control flow or state in the header. Dependencies are `parse.h` and the implementations in `system.c`. Risks include no include guard, `get_time()` declaration missing an explicit `int`-free prototype style distinction from implementation `long long int`, and exposing setters that mutate global process/kernel state without documenting restoration. Test signals are strict compiler warnings and successful linkage from `main.c`/`benchmark.c`.

## Dependencies And Integration Points
There is no runtime control flow or state in the header. Dependencies are `parse.h` and the implementations in `system.c`. Risks include no include guard, `get_time()` declaration missing an explicit `int`-free prototype style distinction from implementation `long long int`, and exposing setters that mutate global process/kernel state without documenting restoration. Test signals are strict compiler warnings and successful linkage from `main.c`/`benchmark.c`.

## Risks And Edge Cases
There is no runtime control flow or state in the header. Dependencies are `parse.h` and the implementations in `system.c`. Risks include no include guard, `get_time()` declaration missing an explicit `int`-free prototype style distinction from implementation `long long int`, and exposing setters that mutate global process/kernel state without documenting restoration. Test signals are strict compiler warnings and successful linkage from `main.c`/`benchmark.c`.

## Test Signals
There is no runtime control flow or state in the header. Dependencies are `parse.h` and the implementations in `system.c`. Risks include no include guard, `get_time()` declaration missing an explicit `int`-free prototype style distinction from implementation `long long int`, and exposing setters that mutate global process/kernel state without documenting restoration. Test signals are strict compiler warnings and successful linkage from `main.c`/`benchmark.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/bench/system.h -->
