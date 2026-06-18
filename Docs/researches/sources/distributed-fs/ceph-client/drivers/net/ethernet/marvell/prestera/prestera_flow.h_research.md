# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_flow.h

Purpose: Defines the shared tc flow block data structures and setup entry point.

Important APIs/types/functions: `struct prestera_flow_block_binding` stores a port, list node, and SPAN id. `struct prestera_flow_block` stores bindings, switch/net pointers, ACL ruleset, tc block callback, flower template list, matchall priority state, rule count, and direction. Declares `prestera_flow_block_setup()`.

Control flow: No inline behavior. The structures are populated in `prestera_flow.c` and consumed by flower/matchall/span/ACL code.

State and persistence: All fields are runtime-only and tied to tc block lifetime. No persistent storage.

Dependencies/integration: Includes `<net/flow_offload.h>` and forward-declares Prestera switch/port types. It is the contract connecting netdev tc setup with classifier-specific modules.

Risks: This struct is shared across multiple feature modules; changing field semantics can affect ACL binding, SPAN mirror rules, and template cleanup. Direction (`ingress`) drives ACL client selection and matchall priority constraints.

Test signals: Build coverage across flow, flower, matchall, and span modules; runtime block bind/unbind with multiple ports and both directions.
