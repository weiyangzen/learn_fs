# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/recursion.c

## Purpose
Tests recursion prevention/accounting for BPF programs that can trigger nested execution paths. The source was read as a complete 42-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `test_recursion()`.
- Includes and fixtures: `#include <test_progs.h>`, `#include "recursion.skel.h"`.
- Generated skeletons/objects referenced: `recursion`.
- Primary APIs and types: `recursion__open_and_load()`, skeleton attach/trigger helpers, BSS counters `pass1`, `pass2`, and `recursion_misses`.

## Control Flow
The test loads the skeleton, triggers recursive paths multiple times, and checks pass counters progress through expected values while recursion misses are accounted for.

## State and Persistence Behavior
BPF BSS counters persist for the skeleton lifetime and are inspected after each trigger. No external state persists.

## Dependencies and Integration Points
Depends on `recursion.skel.h`, the hook used to trigger recursive execution, and kernel recursion guard behavior.

## Risks and Edge Cases
Counters are sensitive to extra trigger events from the environment; recursion guard semantics can change with kernel internals.

## Test Signals
Assertions verify skeleton load, pass1/pass2 counter sequence, and recursion miss count. Named assertion/check labels observed in the source include: `skel_open_and_load`, `pass1 == 0`, `pass1 == 1`, `pass1 == 2`, `pass2 == 0`, `pass2 == 1`, `pass2 == 2`, `recursion_misses`.
