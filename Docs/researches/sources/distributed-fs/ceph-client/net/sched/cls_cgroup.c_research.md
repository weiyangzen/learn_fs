# sources/distributed-fs/ceph-client/net/sched/cls_cgroup.c

Purpose: implements the `cgroup` TC classifier, which maps packets to the classid associated with the originating task/socket cgroup and optionally gates that mapping through ematches and actions.

Important APIs/types/functions: `struct cls_cgroup_head` stores the single filter handle, action extensions, ematch tree, owning proto, and deferred work. Main ops are `cls_cgroup_classify`, `cls_cgroup_change`, `cls_cgroup_destroy`, `cls_cgroup_walk`, `cls_cgroup_dump`, and the unsupported `cls_cgroup_delete`. `cgroup_policy` accepts nested `TCA_CGROUP_EMATCHES`; actions and police use `TCA_CGROUP_ACT` and `TCA_CGROUP_POLICE`. The classification key comes from `task_get_classid(skb)`.

Control flow: `cls_cgroup_init` leaves `tp->root` empty. The first `cls_cgroup_change` requires an explicit handle when no head exists, validates options, initializes extensions, parses actions and ematches, assigns the new head to `tp->root`, and queues any old head for destruction. `cls_cgroup_classify` returns no match if no head exists, if `task_get_classid` returns zero, or if ematches fail; otherwise it sets `res->classid` to the cgroup classid, clears `res->class`, and executes extensions. Delete is unsupported, so removal happens by replacing the whole classifier instance or destroying the proto.

State and persistence behavior: there is at most one runtime head per `tcf_proto`; no IDR or list is used. Replacement is an RCU pointer swap through `rcu_assign_pointer(tp->root, new)`, with old state freed through `cls_cgroup_destroy_work` when action net refs require deferred cleanup. The cgroup classid itself is external kernel/cgroup state, not persisted here. This file writes no persistent data.

Dependencies/integration points: depends on `net/cls_cgroup.h` for `task_get_classid`, the core TC classifier API, ematch helpers, TC action extension helpers, and netlink attributes from `pkt_cls.h`. It registers kind `cgroup` with the shared classifier registry.

Risks: `cls_cgroup_dump` assumes the caller supplies a valid `head`; dump paths should not pass NULL handles for this classifier because `tp->root` can be NULL after init. Since `delete` returns `-EOPNOTSUPP`, generic filter deletion behavior differs from list-based classifiers. Classification depends on skb/task association; packets without cgroup classid always miss. Replacement must not free the old head until RCU/action users are done.

Test signals: create a cgroup classifier with an explicit handle, set cgroup `net_cls` classid, send traffic from a classified task, and verify selected qdisc class/action behavior. Check zero classid miss behavior, ematch gating, action stats dumping, replacement with the same handle, rejection of missing first handle or wrong replacement handle, and `tc filter del` returning unsupported for a single filter delete.
