# sources/distributed-fs/ceph-client/block/blk-ioprio.c

## Purpose
`blk-ioprio.c` implements a blk-cgroup policy that rewrites bio I/O priority class according to a cgroup setting. It is an rq-qos-adjacent cgroup mechanism intended to affect I/O that task-local `ioprio_set()` may miss, including writeback I/O when the filesystem associates writeback with a cgroup.

## Important APIs, Types, And Functions
The central type is `struct ioprio_blkcg`, which embeds `struct blkcg_policy_data` and stores an `enum prio_policy`. Supported policies are `no-change`, `promote-to-rt`, `restrict-to-be`, `idle`, and `none-to-rt`. The public entry point is `blkcg_set_ioprio(struct bio *bio)`. Cgroup file handling is via `ioprio_show_prio_policy()` and `ioprio_set_prio_policy()` for `prio.class`. Policy allocation/free hooks are `ioprio_alloc_cpd()` and `ioprio_free_cpd()`.

## Control Flow
At module init, `ioprio_init()` registers `ioprio_policy` with blk-cgroup. Each cgroup gets a zeroed `ioprio_blkcg` defaulting to `POLICY_NO_CHANGE`. Writes to `prio.class` must start at offset zero and are parsed with `sysfs_match_string()` against `policy_name`. During bio preparation, `blkcg_set_ioprio()` fetches the bio's cgroup policy data through `bio->bi_blkg->blkcg`. If the policy is promotion to RT, non-RT priorities become RT class with level 4. For restrictive policies, the code computes a class value with `IOPRIO_PRIO_VALUE()` and uses `max_t()` because larger non-NONE priority values represent lower priority.

## State And Persistence
State is per-cgroup kernel memory containing only the selected policy enum. It is exposed through cgroupfs but not persisted by this file. The policy is read locklessly in the bio path, so correctness depends on the enum-sized store/load being safe for concurrent readers.

## Dependencies And Integration Points
The file depends on blk-cgroup policy registration, cgroup seq/kernfs helpers, `linux/ioprio.h` class encoding, and bio `bi_ioprio`. It is declared to other block code through `blk-ioprio.h`.

## Risks And Test Signals
Risk centers on policy semantics and class encoding: RT promotion must not downgrade existing RT I/O, `restrict-to-be` must turn NONE/RT into best-effort without changing lower-priority classes incorrectly, and `idle` must force the idle class. Tests should cover cgroup file parsing, offset write rejection, default no-op behavior, writeback bio priority assignment, and interaction with task-set I/O priorities.
