
# sources/distributed-fs/ceph-client/tools/perf/util/parse-branch-options.h

Purpose: declares branch-stack option parsing helpers.

Important APIs/types/functions: exposes `parse_branch_stack` for subcmd option callbacks and `parse_branch_str` for direct conversion of comma-separated branch filter strings into kernel branch sample masks.

Control flow: none. Callers pass storage through `struct option` or an explicit `__u64 *`.

State and persistence: no state; functions mutate caller-owned masks.

Dependencies: stdint for integer types and `struct option` through including users.

Integration points: perf record options and parse-events term handling.

Risks: the header uses `__u64` without directly including its defining Linux type header, relying on include order. Test signals are compile coverage in all users and branch option parser tests.
