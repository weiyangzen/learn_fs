# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/map_populate.c

## Purpose

`map_populate.c` verifies that `MAP_PRIVATE | MAP_POPULATE` faults private file-backed pages without turning them into shared views of later file updates. It protects copy-on-write semantics for populated private mappings.

## Important APIs, Types, and Functions

The test uses `tmpfile()`, `ftruncate()`, `mmap(MAP_SHARED)`, `mmap(MAP_PRIVATE | MAP_POPULATE)`, `msync()`, `socketpair()`, `fork()`, and kselftest counters. `parent_f()` coordinates a file-backed shared update, while `child_f()` validates the private populated mapping.

## Control Flow

The parent creates a one-page temporary file, shared-maps it, writes `0xdeadbabe`, and forks. The child maps the same fd as private+populate, verifies the initial value, then waits. The parent overwrites the shared mapping with `0x22222BAD` and syncs. The child confirms its private mapping still contains the original value and does not observe the parent update.

## State and Persistence Behavior

State is held in an unnamed temporary file and per-process VMAs. The socketpair enforces deterministic ordering. The parent copies child kselftest pass/fail counters out of the exit status because normal kselftest counters are process-local.

## Dependencies and Integration Points

It depends on normal file truncation support and skips through `skip_test_dodgy_fs()` if `ftruncate()` hits a known unsuitable filesystem. It integrates with mm COW and readahead/populate behavior.

## Risks and Edge Cases

The child returns the number of passed child assertions as an exit code, so the plan assumes only two child checks. Filesystems with unusual temporary file semantics can alter setup. The test validates one machine word in one page rather than a broad range.

## Test Signals

Success is the child observing the original `0xdeadbabe` after the parent writes and syncs `0x22222BAD`, with two child-side pass results surfaced to the parent.
