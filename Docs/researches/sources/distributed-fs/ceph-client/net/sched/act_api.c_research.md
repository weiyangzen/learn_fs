# sources/distributed-fs/ceph-client/net/sched/act_api.c

Purpose: implements the shared Linux traffic-control action API. It owns action registration, per-net IDR lifetime management, netlink create/delete/get/dump handling, action execution graph semantics, statistics, cookies, and hardware offload add/delete/stats integration.

Important APIs/functions: exported core APIs include `tcf_register_action()`, `tcf_unregister_action()`, `tcf_action_check_ctrlact()`, `tcf_action_set_ctrlact()`, `tcf_action_exec()`, `tcf_action_init()`, `tcf_action_destroy()`, `tcf_action_dump()`, `tcf_action_update_stats()`, `tcf_action_copy_stats()`, `tcf_idr_check_alloc()`, `tcf_idr_create()`, `tcf_idr_release()`, `tcf_idr_insert_many()`, `tcf_idrinfo_destroy()`, and `tcf_action_update_hw_stats()`. `tc_ctl_action()` and `tc_dump_action()` are registered for `RTM_NEWACTION`, `RTM_DELACTION`, and `RTM_GETACTION`.

Control flow: action modules register `tc_action_ops` and per-net operations before becoming visible in `act_base`. Netlink create requests parse up to `TCA_ACT_MAX_PRIO` nested actions, load modules by action kind if needed, initialize each action through its ops, validate flags and cookies, offload standalone actions when requested, then atomically replace temporary IDR `ERR_PTR(-EBUSY)` slots with live actions. Execution iterates an action array, skips software when `SKIP_SW`, handles `PIPE`, bounded `REPEAT`, bounded `JUMP`, and `GOTO_CHAIN`, and stops at the first non-pipe result. Dump/delete walkers iterate action IDRs under locks and produce netlink notifications.

State and persistence: per-net `tc_action_net` IDRs hold actions by index, with refcount and bind count tracking. Global `act_base` stores registered action kinds under `act_mod_lock`; `act_pernet_id_list` stores pernet IDs for reoffload. Actions hold cookies, stats, goto-chain RCU pointers, flags, module refs, and hardware offload counts.

Dependencies and integration: integrates rtnetlink, netlink attributes, classifier/filter chains, per-net namespaces, module autoloading (`act_<kind>` aliases), `flow_offload`/indirect block callbacks, gnet stats, RCU, IDR, and qdisc/skb helpers. `tcf_dev_queue_xmit()` bridges optional fragmentation transmit hooks.

Risks: lifetime is subtle: IDR placeholders prevent duplicate allocation, module refs must be dropped on all paths, and bind/ref counts determine whether deletion is legal. Offload flags `SKIP_HW` and `SKIP_SW` are mutually exclusive and must match classifier flags. Action graph control opcodes are bounded but malformed jump graphs intentionally degrade to `TC_ACT_OK`.

Test signals: rtnetlink add/get/delete/flush/dump tests, concurrent create/delete on the same index, module autoload retry returning `-EAGAIN`, action cookie dump/free, skip flag validation, chain goto behavior, hardware offload add/delete/reoffload/stats paths, and KASAN/RCU/refcount checks for action teardown.
