
# sources/distributed-fs/ceph-client/net/sched/cls_matchall.c

## Purpose

`cls_matchall.c` implements the `matchall` classifier: a single rule that matches every packet unless software classification is skipped. It is mainly a simple carrier for class binding, action execution, packet hit counters, and hardware offload of catch-all policies.

## Important APIs, Types, and Functions

`struct cls_mall_head` is the entire classifier instance. It stores extensions, result, handle, flags, hardware count, per-CPU hit counters, deferred destroy work, and a `deleting` marker. Key functions are `mall_classify()`, `mall_change()`, `mall_delete()`, `mall_destroy()`, `mall_walk()`, `mall_dump()`, `mall_reoffload()`, `mall_replace_hw_filter()`, `mall_destroy_hw_filter()`, and `mall_stats_hw_filter()`.

## Control Flow

Classification reads the single head under BH RCU, rejects missing head or `skip_sw`, copies the result, increments the current CPU hit counter, and executes extensions. Creation parses one options block, rejects a second rule with `-EEXIST`, validates flags, allocates the head and per-CPU counters, validates actions with offload flags, optionally binds classid, attempts hardware replacement unless `skip_hw`, updates software-use state, and publishes `tp->root`. Delete only marks the rule as deleting and reports `last=true`; final cleanup is done by destroy.

Destroy unbinds the class, destroys hardware state unless skipped, and frees extensions/per-CPU memory either immediately or through queued work. Walk skips missing or deleting heads. Dump refreshes hardware stats when applicable, emits classid, flags, aggregated per-CPU hit count, extensions, and extension stats. Reoffload rebuilds a one-rule `flow_rule` and calls the block callback for replace or destroy.

## State and Persistence Behavior

Only one head can persist per classifier. Runtime hit state lives in `struct tc_matchall_pcnt` per CPU and is aggregated on dump. Offload state is persisted in `flags` and `in_hw_count`. Action net references decide whether destruction can run immediately. The `deleting` flag hides the rule from walks while the proto is being removed.

## Dependencies and Integration Points

It depends on `tcf_exts`, per-CPU allocation, `tc_setup_offload_action()`, `tc_setup_cb_add/destroy/reoffload/call()`, and `TC_SETUP_CLSMATCHALL`. It registers as classifier kind `matchall` and supports class binding.

## Risks and Edge Cases

`skip_sw` means the software path must return no match even though the rule logically matches all packets. Hardware-only rules require at least one successful offload. A single-rule classifier means replacement is not supported by adding another rule; callers must delete first. Counter aggregation is best effort across CPUs.

## Test Signals

Test plain matchall action execution, `skip_sw`/`skip_hw` behavior, hardware stats refresh, delete/walk hiding, class binding, and dump of `TCA_MATCHALL_PCNT`. Offload tests should verify failure behavior for hardware-only rules.
