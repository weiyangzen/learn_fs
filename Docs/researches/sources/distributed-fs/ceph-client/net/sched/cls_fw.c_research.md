
# sources/distributed-fs/ceph-client/net/sched/cls_fw.c

## Purpose

`cls_fw.c` implements the legacy `fw` traffic-control classifier. It maps `skb->mark`, optionally masked and input-device constrained, to a class result and action chain. It also preserves the older mode where no classifier table is allocated and the packet mark itself is interpreted as a classid for non-shared blocks.

## Important APIs, Types, and Functions

`struct fw_head` stores the global mark mask and 256 hash buckets. `struct fw_filter` stores a mark id, class result, input ifindex, action extensions, owning proto, and deferred free work. `fw_hash()` folds the 32-bit mark into a bucket. The `tcf_proto_ops` implementation is `fw_classify()`, `fw_init()`, `fw_get()`, `fw_change()`, `fw_delete()`, `fw_destroy()`, `fw_walk()`, `fw_dump()`, and `fw_bind_class()`.

`fw_set_parms()` validates actions/police, resolves `TCA_FW_INDEV`, enforces a single head-wide mask, and binds classid. `__fw_delete_filter()` and `fw_delete_filter_work()` destroy actions and release their net references after RCU/action users are gone.

## Control Flow

`fw_classify()` reads `tp->root` under BH RCU. If a head exists, it masks `skb->mark`, scans the matching bucket, verifies id and input device, executes extensions, and returns the action result. If no head exists, it falls back to the old mark-as-classid method unless the block is shared.

`fw_change()` accepts an empty options block only for the old mode. Otherwise it parses netlink options. Replacing an existing filter allocates a new filter, initializes extensions, copies stable fields, validates parameters, swaps it into the bucket with RCU assignment, unbinds and queues the old filter for destruction, and returns the new pointer. Creating the first explicit filter allocates `fw_head`, records the mask, allocates a filter, validates parameters, and inserts it at the bucket head.

Deletion unlinks the exact filter from its bucket, unbinds its class, takes an extension net reference, queues deferred destruction, and reports whether all buckets are empty. Destroy drains every bucket, unbinds each class, queues or performs final destruction, and RCU-frees the head. Dump emits classid, input device, non-default mask, extensions, and stats.

## State and Persistence Behavior

Persistent state is only in the classifier head and its RCU bucket chains. The mark mask is global to the head; later filters must use the same mask or the update is rejected. Class bindings are maintained through `tcf_bind_filter()` and `tcf_unbind_filter()`. Filter destruction is deferred when actions still need net context. The old fallback mode stores no classifier state.

## Dependencies and Integration Points

The classifier integrates with `cls_api` via `register_tcf_proto_ops()`, with netfilter or other producers of `skb->mark`, with qdisc classes through `tcf_result`, with action extensions through `tcf_exts`, and with block sharing checks through `tcf_block_shared()` and `tcf_block_q()`.

## Risks and Edge Cases

The head-wide mask is an important compatibility constraint; changing it per filter would make hash lookup ambiguous. Old mark-as-classid mode is disabled for shared blocks because there is no single qdisc handle to compare. Replacement must preserve RCU list integrity while old filters can still be read. This snapshot contains a duplicated local declaration in `fw_set_parms()`, which is a compile risk in the local tree.

## Test Signals

Use `tc filter add fw handle ... classid ...`, masked mark tests, input-device match tests, replacement and deletion tests, dump round trips, and action execution checks. Shared block tests should verify that explicit marks are required and old mode is rejected.
