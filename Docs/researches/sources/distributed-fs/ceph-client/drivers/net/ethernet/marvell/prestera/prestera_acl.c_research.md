# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_acl.c

## Purpose
`prestera_acl.c` implements Prestera ACL object management: flow-block rulesets, rule hashes, VTCAM allocation/reuse, hardware rule entries, counters, policers, jump chains, and port/index binding. It bridges higher-level flower/flow code to Prestera hardware VTCAM APIs.

## Important APIs, Types, and Functions
Public APIs include ACL init/fini, ruleset get/lookup/put/offload/bind/unbind/keymask/prio/index helpers, rule create/destroy/add/del/lookup/stats, rule entry find/create/destroy, VTCAM id get/put, PCL ID setup, and chain-to-counter-client mapping. Internal types are `prestera_acl`, `prestera_acl_ruleset`, `prestera_acl_rule_entry`, and `prestera_acl_vtcam`.

## Control Flow
Ruleset creation validates chain support, allocates a UID/PCL ID, initializes a rule hash, and inserts the ruleset hash. Offload obtains or creates a matching VTCAM and binds nonzero chains by interface index. Rule add inserts the rule by cookie, stamps PCL ID into the keymask, creates a hardware rule entry with actions, binds chain 0 to all block ports on first rule, links the rule, and updates priority range. Rule delete removes hash/list state, destroys hardware entry/actions, refreshes priority range, and unbinds the block when the last base-chain rule is gone.

## State and Persistence
`struct prestera_acl` owns ruleset/rule-entry rhashtables, VTCAM list, global rule list, and UID idr. Rulesets hold refcounts, keymask, VTCAM id, PCL id, chain/block key, offload state, rule count, and priority range. Rule entries own hardware id, action resources, counters, and policers until destroyed.

## Dependencies and Integration Points
The file depends on Linux rhashtable/idr/list/refcount, `prestera_hw` VTCAM/policer APIs, `prestera_counter`, `prestera_flow_block`, and structures in `prestera_acl.h`/`prestera.h`. Flower and matchall code provide rule arguments and keymasks.

## Risks and Edge Cases
VTCAM fallback can fit a keymask into an existing broader VTCAM when creation fails; this must preserve match semantics. Refcounts across rulesets, jump rulesets, VTCAMs, and counter blocks are critical. Error unwind must release policers/counters and remove hardware rules. Egress supports only chain 0; ingress chain masks are limited. `prestera_acl_ruleset_offload()` error path calls put with `ruleset->vtcam_id` before assignment after bind failure, which deserves review.

## Test Signals
Test ruleset create/lookup/refcount/put, chain limits, keymask sharing/fallback, rule add/delete with accept/drop/trap/jump/police/count, first/last port block bind/unbind, counter stats, duplicate cookies/entries, VTCAM destroy failures, policer creation failures, and ACL fini warnings for leaked rules/VTCAMs/UIDs.
