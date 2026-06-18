# sources/distributed-fs/ceph-client/net/sched/sch_ingress.c

Purpose: implements the `ingress` and `clsact` pseudo-qdiscs used to attach classifier/action chains to device ingress and egress paths without normal enqueue/dequeue behavior. They are control-plane objects that bind `tcf_block`s into TCX mini qdisc entries.

Important APIs, types, and functions: `struct ingress_sched_data` owns one `tcf_block`, `tcf_block_ext_info`, and `mini_Qdisc_pair`; `struct clsact_sched_data` owns separate ingress and egress versions. `ingress_init` and `clsact_init` validate parent handles, create/fetch TCX entries with `tcx_entry_fetch_or_create`, initialize `mini_qdisc_pair`, and acquire blocks with `tcf_block_get_ext`. Destroy paths release blocks, decrement miniq references, remove inactive TCX entries, and decrement ingress/egress queue counters. Class ops expose `find`, `bind_tcf`, `tcf_block`, and block index setters/getters.

Control flow: creating an ingress qdisc only works under `TC_H_INGRESS`; clsact only works under `TC_H_CLSACT`. On init, the code increments the global ingress/egress queue accounting, installs a mini qdisc pair connected to the device TCX ingress or egress entry, configures binder type and `chain_head_change`, obtains the filter block, then binds the block into the miniq pair. Chain head changes call `mini_qdisc_pair_swap`, allowing packet path readers to see updated classifier heads. No packet enqueue/dequeue occurs in this file.

State and persistence behavior: runtime state is the filter block pointer, TCX entry reference, block index, and mini qdisc pair. Block indexes are set through qdisc ops and returned to userspace for shared block reporting. Destroy is responsible for releasing TCX entries only when no other TCX users remain. There is no persistent storage; netlink dump returns an empty options nest.

Dependencies and integration points: integrates with `net/tcx.h`, `pkt_cls`, `tcf_block_get_ext`, mini qdisc pairs, global ingress/egress queue counters, and module registration for `ingress` and `clsact`. Binder types distinguish `FLOW_BLOCK_BINDER_TYPE_CLSACT_INGRESS` and `FLOW_BLOCK_BINDER_TYPE_CLSACT_EGRESS`.

Risks: init error paths after TCX reference increments can leak references if future changes add failures without unwind. Parent handle validation is essential because these qdiscs are not normal root children. Destroy assumes RTNL-style protection and uses `rtnl_dereference` for TCX entries. clsact has two independent blocks, so partial init failure handling is a sensitive area.

Test signals: verify invalid parent rejection, creation/destruction of ingress and clsact, shared block indexes, filter attach/detach propagation through `chain_head_change`, TCX entry cleanup when no programs/mini qdiscs remain, and module registration rollback if clsact registration fails after ingress registration.
