# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_matchall.h

Purpose: Declares the matchall/SPAN offload API used by the flow dispatcher and flower priority checks.

Important APIs/types/functions: Prototypes for matchall replace/destroy and `prestera_mall_prio_get()`.

Control flow: `prestera_flow.c` dispatches `TC_SETUP_CLSMATCHALL` commands here; `prestera_flower.c` consults matchall priority bounds through this header.

State and persistence: No direct state; functions mutate `struct prestera_flow_block` state.

Dependencies/integration: Includes `<net/pkt_cls.h>` and forward-declares `struct prestera_flow_block`.

Risks: API signature changes must be coordinated with flow and flower modules.

Test signals: Compile/link coverage and matchall tc command execution.
