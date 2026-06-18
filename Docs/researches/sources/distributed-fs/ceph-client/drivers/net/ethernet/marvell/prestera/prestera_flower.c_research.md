# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_flower.c

Purpose: Translates tc flower rules and templates into Prestera ACL rulesets, key/mask fields, hardware actions, counters, and statistics.

Important APIs/types/functions: `prestera_flower_replace()`, `prestera_flower_destroy()`, `prestera_flower_stats()`, `prestera_flower_tmplt_create/destroy()`, `prestera_flower_template_cleanup()`, and `prestera_flower_prio_get()`. Internal parsing handles metadata, control, basic L2/L3/L4 fields, VLAN, ICMP, port ranges, and actions.

Control flow: Replace first checks priority compatibility with matchall, gets or creates a ruleset for the chain, creates an ACL rule keyed by cookie, parses matches/actions into `rule->re_key`/`rule->re_arg`, offloads the ruleset if needed, then adds the rule to hardware. Destroy looks up by chain/cookie and removes hardware and software state. Stats resolve the rule and update tc delayed hardware stats. Template creation parses a rule-shaped template, fixes PCL id keymask, preserves the keymask on a ruleset, attempts offload, and stores a ruleset reference in the block template list.

State and persistence: Rules, rulesets, jump ruleset references, counters, policers, and templates are runtime kernel/firmware state. Template list entries keep ruleset refs until template destroy or block cleanup.

Dependencies/integration: Depends on Linux flow dissector/action APIs, Prestera ACL, flow block state, and matchall priority helpers. `FLOW_ACTION_GOTO` uses chain rulesets; delayed stats use ACL counters.

Risks: Only specific dissector keys and actions are supported; unsupported flags/actions return extack errors. IPv6 address match key is allowed in the mask check but parsing only explicitly handles IPv4 address payloads in this file. Multiple actions of the same kind are rejected. GOTO can only jump to a higher chain. Priority interaction with matchall differs by ingress/egress direction and can reject rule ordering.

Test signals: Flower add/delete for supported keys, unsupported key/action extack messages, GOTO chain forward-only behavior, police/count/trap/drop/accept actions, delayed stats updates, templates with later rule insertion, priority conflict tests with matchall, and cleanup after block unbind.
