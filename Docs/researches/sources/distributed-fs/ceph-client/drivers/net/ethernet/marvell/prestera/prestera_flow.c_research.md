# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_flow.c

Purpose: Provides the tc block setup dispatcher for Prestera hardware offload, binding shared flow blocks to ports and routing flower/matchall classifier operations to their implementations.

Important APIs/types/functions: Public `prestera_flow_block_setup()`. Internal `prestera_flow_block_cb()` dispatches `TC_SETUP_CLSFLOWER` to flower and `TC_SETUP_CLSMATCHALL` to matchall. `prestera_flow_block_get/put/create/destroy`, `prestera_flow_block_bind/unbind`, and `prestera_setup_flow_block_clsact()` manage flow block callback references and port bindings.

Control flow: On `FLOW_BLOCK_BIND`, the driver looks up or allocates a shared `flow_block_cb`, allocates a port binding, optionally binds existing ACL ruleset zero to the port, registers the callback with tc, and records the block on ingress or egress port state. On unbind it destroys matchall state, removes the port binding, unbinds ACL rulesets, drops callback references, and clears the port pointer.

State and persistence: Runtime state lives in `struct prestera_flow_block`: binding list, template list, ruleset pointer, block callback, matchall priority bounds, rule count, net namespace, switch, and ingress flag. A global `prestera_block_cb_list` tracks registered callbacks for tc.

Dependencies/integration: Depends on Linux flow block APIs, Prestera ACL, flower, matchall, and span modules. Called from `ndo_setup_tc` in `prestera_main.c`.

Risks: Shared block reference counting must be exact across multiple ports. `prestera_setup_flow_block_unbind()` calls `prestera_mall_destroy()` for the whole block, so matchall state is block-wide rather than per-port. Error paths must avoid leaking bindings or callback refs. ACL ruleset binding must be consistent when a block is already offloaded.

Test signals: `tc qdisc add clsact`, flower and matchall add/delete/stats, shared block bound to multiple ports, ingress and egress blocks, unbind cleanup, and error injection around ACL bind failures.
