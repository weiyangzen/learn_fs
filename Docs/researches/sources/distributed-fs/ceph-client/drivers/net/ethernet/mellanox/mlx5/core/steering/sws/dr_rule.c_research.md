# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_rule.c

## Purpose
`dr_rule.c` creates and destroys software steering rules under a matcher. It validates concrete match values against the matcher mask, builds STE byte arrays, inserts those STEs into hash tables, handles collisions and hash-table growth, attaches action STEs, posts hardware updates, and unwinds resources on failure or deletion.

## Important APIs, Types, And Functions
The public APIs are `mlx5dr_rule_create()`, `mlx5dr_rule_destroy()`, `mlx5dr_rule_set_last_member()`, and `mlx5dr_rule_get_reverse_rule_members()`. Important internals include `dr_rule_verify()`, `dr_rule_create_rule_nic()`, `dr_rule_handle_ste_branch()`, `dr_rule_handle_empty_entry()`, `dr_rule_handle_collision()`, `dr_rule_rehash_htbl()`, `dr_rule_handle_action_stes()`, and `dr_rule_clean_rule_members()`.

## Control Flow
Rule creation increments the matcher refcount, verifies `value->match_sz`, copies match parameters, and checks every value byte is covered by the matcher mask. Domain type selects RX, TX, or both sides for FDB. FDB copies the match parameter because builder/tag functions consume fields as they encode them.

For each NIC side, `dr_rule_create_rule_nic()` skips impossible FDB directions based on source port and flow source, locks the NIC domain, selects the builder chain by outer/inner IP version, adds the matcher to the table if needed, builds STE tags, builds action STE data, then walks the STE array. Each STE is placed by CRC hash into the current hash table. Empty slots become new branches; matching non-last STEs are reused; occupied slots either trigger rehash or allocate a collision table linked through the miss list. Action STEs are appended when actions require more STEs than match builders. The queued STE updates are posted in reverse order so downstream STEs exist before upstream hit pointers expose them.

## State And Persistence
State spans `struct mlx5dr_rule`, `rule_actions_list`, RX/TX `last_rule_ste`, action refcounts, STE refcounts, miss lists, hash table collision counters, and matcher rule counters. Hardware persistence is through posted STE writes and hash table rewrites. Rehash allocates a larger table, copies entries and miss lists, posts the new table, updates the previous pointer, then releases the old table reference after the connect update is queued.

Destroy walks from the rule's last STE back to the first through `pointing_ste` and miss lists, calls `mlx5dr_ste_put()` for each, decrements matcher rule counters, and removes the matcher from the NIC table when the last rule is gone.

## Dependencies And Integration Points
This file is the central integration point for matchers, STE encoding, action encoding, ICM allocation, send-ring posting, and debug rule tracking. It calls `mlx5dr_matcher_select_builders()`, `mlx5dr_ste_build_ste_arr()`, `mlx5dr_actions_build_ste_arr()`, `mlx5dr_send_fill_and_append_ste_send_info()`, `mlx5dr_send_postsend_ste()`, `mlx5dr_send_postsend_htbl()`, and matcher table add/remove routines. It relies on domain NIC locks for per-side table mutation.

## Risks
Collision and rehash logic is complex: miss-list head replacement, `pointing_ste`, `next_htbl`, and rule last-member pointers must remain synchronized. Duplicate last-STE insertion is logged but still proceeds into collision handling, so callers should not depend on duplicate rejection. Failure unwinds must free pending send-info objects and remove table links only when no rules exist. Optimized stack STE arrays are disabled for small `CONFIG_FRAME_WARN`; changes to builder counts or action STE limits need stack-size review.

## Test Signals
Key tests include value-not-covered-by-mask rejection, RX/TX/FDB insertion and skip behavior, duplicate rules, high-collision insertion that triggers rehash, action chains that add STEs, failure injection for send-info allocation and postsend, and destruction of head, middle, and only STEs in miss lists. Runtime signals are no leaked matcher refs, correct rule counters, stable hardware after rehash, and successful reverse-order post updates.
