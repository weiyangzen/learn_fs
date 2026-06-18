# sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-self-heald.h

## Purpose

`afr-self-heald.h` declares the data structures and public functions for AFR's self-heal daemon. It separates daemon scheduling/state types from the generic self-heal APIs in `afr-self-heal.h`.

The header defines how per-subvolume healer threads, crawl statistics, split-brain history, and daemon configuration are represented in `afr_private_t`.

## Important APIs, Types, and Functions

`shd_event_t` records a split-brain or daemon event path and child index for history storage.

`crawl_event_t` records crawl counters (`healed_count`, `split_brain_count`, `heal_failed_count`), timing (`start_time`, `end_time`), crawl type, and child index.

`struct subvol_healer` is the per-child healer state: owning xlator, current crawl event, mutex, condition variable, thread, subvolume index, locality flag, running flag, and rerun flag.

`afr_self_heald_t` is the daemon aggregate embedded in AFR private state. It holds index and full healer arrays, split-brain and statistics event histories, timeout and threading limits, thin-arbiter latency setting, and enabled/iamshd flags.

The header declares `afr_selfheal_daemon_init()`, `afr_xl_op()`, and `afr_shd_entry_purge()`.

## Control Flow

Initialization code allocates `afr_self_heald_t.index_healers` and `.full_healers`, then initializes each `subvol_healer`. Runtime code signals or spawns the relevant healer for a child. CLI/control operations enter through `afr_xl_op()`.

`crawl_event_t` timing fields define crawl lifecycle: `start_time == 0` means inactive/invalid stats, nonzero start with zero end means in progress, and nonzero end means completed history.

## State and Persistence Behavior

The structures in this header are in-memory daemon state. They do not persist across process restarts. Persistent effects are caused by the daemon implementation when it calls heal, purge, and xattrop operations.

The mutex and condition in each `subvol_healer` protect `running` and `rerun` coordination. The event-history pointers retain bounded in-memory statistics and split-brain event data.

`enabled` gates whether healers should perform work, while `iamshd` identifies the self-heal daemon process role.

## Dependencies and Integration Points

The header includes `pthread.h` and assumes Gluster/AFR types such as `xlator_t`, `eh_t`, `inode_t`, `ia_type_t`, and `dict_t` are visible from including contexts.

It is included by `afr-self-heald.c` and by AFR code that needs daemon initialization or management dispatch declarations.

## Risks and Edge Cases

`crawl_event_t` comments contain a typo, but the semantics are clear and used by statistics reporting. Code must honor those timing conventions or in-progress statistics become misleading.

The header exposes thread primitives directly, so lifecycle correctness depends on every user following the same locking and signaling rules.

Bounded history sizes are defined in the `.c` file rather than the struct. Consumers should not assume unbounded statistics retention.

## Test Signals

Compile-time tests should catch struct/prototype drift between daemon code and AFR private state. Runtime tests should verify that initialized healers have valid mutex/condition state, crawl events report inactive/in-progress/completed status correctly, and `afr_xl_op()` can safely read daemon state while healers are running.
