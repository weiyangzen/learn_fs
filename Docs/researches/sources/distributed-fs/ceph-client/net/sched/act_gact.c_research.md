# sources/distributed-fs/ceph-client/net/sched/act_gact.c

Purpose: implements the generic TC action `gact`, returning configured control actions such as pass, drop, trap, goto chain, pipe, reclassify, or probabilistic alternatives.

Important APIs/functions: `tcf_gact_init()` creates/replaces an action; `tcf_gact_act()` returns the runtime action and updates stats; `tcf_gact_dump()` reports configuration; `tcf_gact_stats_update()` merges hardware stats; `tcf_gact_offload_act_setup()` maps supported actions to flow offload entries. Optional `CONFIG_GACT_PROB` adds random and deterministic probability functions.

Control flow: init parses `TCA_GACT_PARMS`, optionally validates probability parameters, allocates or finds an IDR action, validates the primary control action and goto chain, then updates action and probability state under lock. Runtime reads the configured action, optionally substitutes a probability fallback based on random or packet-count modulo, updates bstats/lastuse, counts drops for `TC_ACT_SHOT`, and returns the result.

State and persistence: action state is stored in the TC IDR and includes primary action, optional probability action/type/value, packet counter for deterministic mode, stats, and goto-chain pointer. No external durable state is created.

Dependencies and integration: shared TC action API, optional random number generation, flow offload mapping for accept/drop/trap/goto, module/pernet registration.

Risks: probability fallback does not allow goto-chain fallback. Memory barriers pair probability value/type updates with runtime reads. Offload supports only a subset of software control actions; unsupported actions return `-EOPNOTSUPP`.

Test signals: basic pass/drop/trap/goto execution, bind and replace semantics, probability random/deterministic distribution, dump output, hardware offload acceptance/rejection, and stats update behavior for drop actions.
