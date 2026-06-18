
# sources/distributed-fs/ceph-client/net/sched/cls_u32.c

## Purpose

`cls_u32.c` implements the universal 32-bit key traffic-control classifier. It matches packets using arrays of 32-bit value/mask tests at configurable offsets, supports hierarchical hash tables linked from key nodes, optional mark checks, optional performance counters, class binding, actions, and hardware offload through `TC_SETUP_CLSU32`.

## Important APIs, Types, and Functions

`struct tc_u_knode` is a key node containing a handle, parent/child hnode pointers, selector (`tc_u32_sel` plus flexible keys), action extensions, input device, class result, flags, offload count, optional per-CPU stats and mark state, and deferred work. `struct tc_u_hnode` is a hash table with handle, priority, divisor, IDR of keys, refcount, root marker, flags, and flexible bucket array. `struct tc_u_common` shares hnodes between protos attached to the same block/qdisc key.

Major functions are `u32_classify()`, `u32_init()`, `u32_change()`, `u32_delete()`, `u32_destroy()`, `u32_get()`, `u32_walk()`, `u32_dump()`, and `u32_reoffload()`. Helpers manage handle ID allocation (`gen_new_htid()`, `gen_new_kid()`), shared common lookup, key/hnode destruction, parameter validation, replacement cloning, and offload add/delete for hnodes and knodes.

## Control Flow

Classification starts at the root hnode and selected bucket. For each knode it honors `skip_sw`, optional mark mask/value, then evaluates every selector key by reading four bytes with `skb_header_pointer_careful()`. If all keys match and no child hnode exists, terminal nodes execute input-device checks, update optional counters, execute actions, and return. If a child hnode exists, the current node and offset are pushed on a bounded stack, the child bucket is selected by hashing a packet word with the selector mask/shift, and variable/eat offsets are applied. On child exhaustion the stack pops and terminal handling resumes. Stack overflow returns no match and logs a ratelimited warning.

Initialization allocates a root hnode, finds or creates shared `tc_u_common`, links the root into the common hnode list, and stores common data in `tp->data`. `u32_change()` handles three cases: replacing an existing knode by cloning it and swapping under RCU; creating a new hnode when `TCA_U32_DIVISOR` is present; or creating a new knode in a selected hash table. Knode creation validates selectors, allocates optional stats, initializes actions, handles `TCA_U32_LINK`, classid, input device, mark data, hardware offload, sorted bucket insertion, and common knode accounting.

Deletion removes hardware state, unlinks knodes from their parent hnode, removes IDR entries, unbinds classes, and queues/free keys. Hnode deletion is allowed only when it is not root and its refcount is one. Destroy drops the root and common references and drains any remaining shared hnodes. Dump emits either hnode divisor or knode selector/hash/class/link/flags/mark/counters/input-device/extensions and stats.

## State and Persistence Behavior

State persists in shared `tc_u_common` structures keyed by shared block or qdisc pointer, so multiple protos can reference the same hnode namespace. Hnodes and linked child hnodes are refcounted. Handles are allocated by IDR and encode htid, bucket, and node id. Optional performance counters and mark success counters are per CPU and deliberately shared across replacement clones until old readers are gone. Hardware state is in `flags` and `in_hw_count`.

## Dependencies and Integration Points

The file depends on `tc_u32_sel`, `tc_u32_key`, `tcf_exts`, `tcf_block`, IDR, RCU, per-CPU counters, optional `CONFIG_CLS_U32_PERF` and `CONFIG_CLS_U32_MARK`, and hardware offload callbacks using `TC_SETUP_CLSU32`. It registers classifier kind `u32` and can bind classes.

## Risks and Edge Cases

Handle encoding and IDR ownership are subtle and user-visible. Linked hnode refcounts must be balanced during update, error unwind, and delete or child tables can leak or be freed while referenced. Replacement clones share per-CPU stats, so freeing the wrong variant can double-free counters. Offset arithmetic and `TC_U32_EAT`/variable offset handling are packet-safety critical. Hardware-only rules must fail when not actually in hardware. This local source contains apparent duplicate lines around bucket selection and hnode allocation, which are compile/review risks for this snapshot.

## Test Signals

Test root and non-root hnode creation, handle auto-allocation and explicit handles, hash bucket matching, linked table traversal, variable/eat offsets, mark matching, input-device checks, class/action execution, replacement preserving counters, deletion of busy hnodes, dump round trips, and `skip_sw`/`skip_hw` offload behavior. Compile both with and without `CONFIG_CLS_U32_PERF` and `CONFIG_CLS_U32_MARK`.
