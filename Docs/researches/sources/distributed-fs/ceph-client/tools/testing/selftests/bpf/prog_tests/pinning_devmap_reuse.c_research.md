# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/pinning_devmap_reuse.c

## Purpose
Tests reuse of pinned devmap-style maps across skeleton instances and behavior when bpffs pins are swapped between loads. The source was read as a complete 51-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `test_pinning_devmap_reuse()`.
- Includes and fixtures: `#include <sys/types.h>`, `#include <sys/stat.h>`, `#include <unistd.h>`, `#include <test_progs.h>`, `#include "test_pinning_devmap.skel.h"`.
- Generated skeletons/objects referenced: `test_pinning_devmap`.
- Primary APIs and types: `test_pinning_devmap__open_and_load()`, skeleton map pin paths, map fd/pin operations, and bpffs rename/swap helpers in the test.

## Control Flow
The test loads two skeletons using devmap pinning, swaps pin paths to emulate reuse/change scenarios, then loads a third skeleton to verify libbpf handles existing pins correctly.

## State and Persistence Behavior
Persistent state is bpffs map pins for the devmap fixture. Skeleton objects own live fds; pins survive object destruction until explicit cleanup.

## Dependencies and Integration Points
Depends on generated `test_pinning_devmap.skel.h`, devmap support, bpffs, and stable pin names from the BPF object.

## Risks and Edge Cases
Stale pins or map attribute mismatches can invalidate reuse; devmap availability is kernel/config dependent.

## Test Signals
Assertions check first/second skeleton load, successful pin swap, and third skeleton load using the resulting pins. Named assertion/check labels observed in the source include: `skel_load1`, `skel_load2`, `swap pins`, `skel_load3`.
