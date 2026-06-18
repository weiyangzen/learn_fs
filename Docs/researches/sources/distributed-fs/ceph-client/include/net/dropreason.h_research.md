# sources/distributed-fs/ceph-client/include/net/dropreason.h

Read `sources/distributed-fs/ceph-client/include/net/dropreason.h` completely for this pass (49 lines, 1347 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/net/dropreason.h_research.md`.

Purpose: ties core and subsystem-specific skb drop reason namespaces together and declares the RCU-protected registry used to map subsystem IDs to reason string lists.

Important APIs/types/functions: `enum skb_drop_reason_subsys` defines subsystem IDs for core, mac80211 unusable frames, Open vSwitch, qdisc, and the subsystem count. `struct drop_reason_list` stores a reason string array and count. `drop_reasons_by_subsys[]` is an RCU-protected global registry. `drop_reasons_register_subsys()` and `drop_reasons_unregister_subsys()` publish or remove subsystem reason lists.

Control flow: core drop reasons are always defined by `dropreason-core.h`. Subsystems with extended reason ranges register their string list under a subsystem ID. Tracing/diagnostic code decodes the subsystem bits from a drop reason and looks up the corresponding list under RCU.

State and persistence: registry entries are runtime pointers to static or module-owned reason lists. Access must be under RCU; modules must unregister before the list storage disappears.

Dependencies and integration points: depends on core drop reasons and RCU. It integrates with mac80211, Open vSwitch, qdisc, and any trace or drop-monitor path decoding `enum skb_drop_reason`.

Risks: subsystem lists have module lifetime constraints. Missing registration yields undecodable extended reasons. Subsystem count and IDs must stay synchronized with reason producers. Registry access outside RCU can race unregister.

Test signals: register/unregister subsystem reason lists under RCU, decode core and qdisc reason values, module unload races, missing-list fallback behavior, and trace/drop-monitor output for subsystem-encoded reasons.
