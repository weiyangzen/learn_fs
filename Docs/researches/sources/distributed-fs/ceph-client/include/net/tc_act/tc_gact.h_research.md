<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_gact.h -->
# sources/distributed-fs/ceph-client/include/net/tc_act/tc_gact.h

Purpose: Defines the generic TC action state and inline predicates used by classifiers and offload code to identify common action results.

Important APIs/types/functions: `struct tcf_gact` embeds `tc_action` and, with `CONFIG_GACT_PROB`, probabilistic action fields and packet counter. `__is_tcf_gact_act()` checks action identity and result, including extended actions. Helpers identify OK, SHOT, TRAP, GOTO_CHAIN, CONTINUE, RECLASSIFY, and PIPE; `tcf_gact_goto_chain_index()` extracts the chain index.

Control flow: Packet execution returns the configured action, optionally probabilistically. Offload and classifier code use helpers to reason about terminal or chaining behavior without open-coding TC action constants.

State and persistence behavior: State is per action; probabilistic mode keeps an atomic packet counter. Helpers are gated by `CONFIG_NET_CLS_ACT` and otherwise return false.

Dependencies/integration points: Depends on `act_api.h` and TC gact UAPI. Integrated with classifier chains and `tc_wrapper.h`.

Risks: Extended action comparisons must preserve chain-index bits. Disabled config can silently make helper predicates false.

Test signals: gact OK/drop/trap/reclassify/pipe/goto tests, probabilistic mode distribution, chain-index extraction, and offload translation tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_gact.h -->
