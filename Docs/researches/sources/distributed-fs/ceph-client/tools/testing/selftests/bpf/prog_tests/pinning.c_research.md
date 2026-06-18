# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/pinning.c

## Purpose
Covers libbpf map pinning behavior: invalid pin metadata rejection, automatic pinning, reuse of pinned maps, custom pin roots, manual pin paths, parameter-mismatch rollback, and reuse-fd pinning. The source was read as a complete 281-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `get_map_id()`, `test_pinning()`.
- Includes and fixtures: `#include <sys/types.h>`, `#include <sys/stat.h>`, `#include <unistd.h>`, `#include <test_progs.h>`.
- Generated skeletons/objects referenced: `bpf_object`.
- Primary APIs and types: `bpf_object__open_file()`, `bpf_object__load()`, `bpf_object__pin_maps()`, `bpf_object__unpin_maps()`, `bpf_map__pin()`, `bpf_map__set_pin_path()`, `bpf_map__pin_path()`, `bpf_map__reuse_fd()`, `bpf_map_create()`, `bpf_map_get_info_by_fd()`, `stat()`, `unlink()`, `rmdir()`.

## Control Flow
`test_pinning()` first verifies invalid pinning definitions fail, then loads `test_pinning.bpf.o` and checks default auto-pinning. It reloads to verify the same pinned map id is reused, tests re-pin and different-location failures, manually assigns pin paths to non-pinned maps, verifies rollback on incompatible reuse, repeats with `pin_root_path`, then pins a reused manual map fd.

## State and Persistence Behavior
This test intentionally persists bpffs entries under `/sys/fs/bpf` during execution: `pinmap`, `nopinmap*`, and `/sys/fs/bpf/custom/pinmap`. It tracks map IDs across object close/reopen and removes all paths in `out:` cleanup.

## Dependencies and Integration Points
Depends on mounted bpffs, `test_pinning.bpf.o` and invalid fixture object, libbpf object/map APIs, and root/CAP_BPF-like permissions.

## Risks and Edge Cases
Failure cleanup can leave pinned maps that affect later runs; incompatible existing bpffs entries can cause false failures; custom root path needs directory creation/removal behavior from libbpf.

## Test Signals
Checks invalid `-EINVAL`, path existence/nonexistence, map-id reuse, no-op re-pin, different path rejection, path getter values, mismatch rollback, custom root pinning, and reuse-fd pinning. Named assertion/check labels observed in the source include: `NULL map`, `err %d errno %d`, `err %d errno %d\n`, `err %d errno %d id %d id2 %d\n`, `nopinmap`, `get pin path after set`, `fd %d\n`.
