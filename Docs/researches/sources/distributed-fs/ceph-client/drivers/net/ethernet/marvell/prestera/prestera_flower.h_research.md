# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_flower.h

Purpose: Declares the tc flower offload API used by the generic flow block dispatcher and matchall priority coordination.

Important APIs/types/functions: Prototypes for replace, destroy, stats, template create/destroy/cleanup, and `prestera_flower_prio_get()`.

Control flow: `prestera_flow.c` dispatches tc flower commands to these functions. `prestera_matchall.c` uses `prestera_flower_prio_get()` to prevent unsupported ordering between mirror matchall and flower ACL rules.

State and persistence: No direct state; functions operate on `struct prestera_flow_block` and tc offload objects.

Dependencies/integration: Includes `<net/pkt_cls.h>` for tc classifier structs and forward-declares the flow block.

Risks: Header API is small but central to classifier dispatch; signature drift affects flow and matchall modules.

Test signals: Compile/link coverage and tc flower command routing through `prestera_flow_block_setup()`.
