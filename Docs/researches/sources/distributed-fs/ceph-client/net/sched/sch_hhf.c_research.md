# sources/distributed-fs/ceph-client/net/sched/sch_hhf.c

## Purpose
`sch_hhf.c` implements the Heavy-Hitter Filter qdisc. It separates traffic into heavy-hitter and non-heavy-hitter buckets using a multi-stage approximate counter filter plus an exact heavy-hitter table, then serves the buckets with weighted deficit round robin that favors non-heavy-hitter traffic.

## Important APIs, Types, And Functions
`struct hhf_sched_data` owns two WDRR buckets, hash perturbation key, quantum, heavy-hitter flow table, approximate filter arrays/valid bits, counters, bucket lists, and configurable thresholds/timeouts. `struct hh_flow_state` stores exact heavy-hitter hash and last-hit timestamp. Key functions are `hhf_classify()`, `seek_list()`, `alloc_new_hh()`, `hhf_enqueue()`, `hhf_drop()`, `hhf_dequeue()`, `hhf_change()`, `hhf_init()`, `hhf_dump()`, and `hhf_dump_stats()`.

## Control Flow
Classification periodically resets approximate filter valid bits, hashes the packet with a random perturbation, checks the exact heavy-hitter table, and if absent indexes four counter arrays using three 10-bit hash chunks plus an XOR-derived fourth. If all counters exceed `hhf_admit_bytes`, it allocates or reuses exact heavy-hitter state and classifies into the heavy-hitter bucket without incrementing filter counters. Otherwise it conservatively updates counters to the minimum candidate value and classifies as non-heavy-hitter. Enqueue appends to the selected bucket, activates heavy hitters on old bucket list with weight 1 and non-heavy hitters on new bucket list with configurable higher weight, and drops from heavy hitters first when qdisc limit is exceeded. Dequeue serves new buckets before old buckets by WDRR deficit.

## State And Persistence
Runtime state includes the fixed exact table of list heads, dynamically allocated heavy-hitter flow entries, four counter arrays, four valid-bit arrays, two skb buckets, activity lists, and stats counters. Configuration persists in qdisc memory: backlog limit, quantum, max HH flows, reset/admit/evict parameters, and non-HH weight. Dump emits these parameters and xstats emit HH/drop counters.

## Dependencies And Integration Points
HHF uses skb flow hashing with `siphash_key_t`, generic qdisc queue/stat helpers, netlink policies, jiffies-based timing, `kvcalloc`/`kvzalloc` allocation, and qdisc internal dequeue when shrinking limits. It has no classifier block and no child qdiscs.

## Risks
The approximate filter has false positives by design, though not false negatives for sustained heavy hitters under the algorithm assumptions. Resetting valid bits rather than counters reduces cost but makes valid-bit correctness essential. Heavy-hitter table allocation is capped; when full, new heavy hitters fall back to non-HH classification and increment overlimit stats. Limit drops always target heavy-hitter bucket first if possible, so accounting must handle cases where the enqueued packet’s bucket differs from the dropped bucket. `hhf_reset()` drains through dequeue, so stats/backlog side effects should be expected.

## Test Signals
Test filter admission threshold, conservative counter update, periodic valid-bit reset, exact table hit and eviction, HH flow cap behavior, WDRR weight preference for non-HH bucket, heavy-first overlimit drops, return code difference when dropping from same versus other bucket, netlink validation for zero/overflow non-HH quantum product, limit shrink drops, dump/xstats counters, allocation failure cleanup in init, and destroy freeing flow table/filter arrays.
