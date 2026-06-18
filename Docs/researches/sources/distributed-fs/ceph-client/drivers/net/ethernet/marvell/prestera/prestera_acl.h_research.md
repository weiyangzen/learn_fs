# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_acl.h

## Purpose
`prestera_acl.h` declares the Prestera ACL public API and wire-format-like match/action structures used by flower, flow-block, counter, and hardware layers.

## Important APIs, Types, and Definitions
It defines PCL ID masks/macros, rule-match setter macros, match type enum, action enum, ACL interface types, `prestera_acl_match`, action payloads, `prestera_acl_rule_entry_key`, `prestera_acl_hw_action_info`, flat `prestera_acl_rule_entry_arg`, `prestera_acl_rule`, and `prestera_acl_iface`. Prototypes cover ACL lifecycle, rule lifecycle, stats, rule entries, rulesets, keymask/PCL ID, VTCAM IDs, and chain-to-client mapping.

## Control Flow
There is no executable flow beyond macros that copy values into match arrays. The header defines how callers build keys/masks/actions before `prestera_acl.c` resolves them into hardware objects.

## State and Persistence
`prestera_acl_rule` persists per offloaded rule and links to its ruleset, optional jump ruleset, hardware rule entry, cookie, chain, priority, and flat creation arguments. Rule entry arguments are intentionally flat so object keys can be resolved before storage in internal entries.

## Dependencies and Integration Points
The header includes `prestera_counter.h` and forward-declares switch/ACL/flow-block types. It is used by Prestera flower/flow code, ACL implementation, hardware code, and counter integration.

## Risks and Edge Cases
Match arrays are indexed by enum values, so enum reordering changes ABI between software layers. PCL ID packs user ID and chain into 10 bits; chain/user ranges must stay within masks. The flat argument struct stores both validity bits and payloads, so callers must initialize it to zero before setting actions.

## Test Signals
Compile all ACL users, validate PCL ID construction for chain/user limits, add rules with each match/action type, test jump/police/count combinations, and run sparse/struct initialization checks for uninitialized validity bits.
