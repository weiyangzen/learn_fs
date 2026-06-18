# sources/distributed-fs/ceph-client/drivers/net/netdevsim/tc.c

Purpose: supplies netdevsim's `ndo_setup_tc` handling for selected qdiscs and clsact/block offload tests.

Important APIs/types/functions: `nsim_setup_tc()` dispatches TC setup types. `nsim_setup_tc_taprio()` handles TAPRIO replace/destroy/stats. `nsim_setup_tc_ets()` handles ETS replace/destroy/stats. `nsim_setup_tc_block_cb()` forwards flow-block callbacks into the BPF offload helper. A global `nsim_block_cb_list` tracks simple block callbacks.

Control flow: TAPRIO and ETS accept replace/destroy commands as no-ops and return synthetic zero stats for stats requests. Block setup calls `flow_block_cb_setup_simple()` with the netdevsim private pointer as callback state. Unsupported setup types return `-EOPNOTSUPP`.

State and persistence: the only state in this file is the global block callback list. Qdisc settings themselves are not persisted in netdevsim.

Dependencies and integration: integrates with packet scheduler/qdisc APIs, flow block setup, BPF TC offload hooks from `netdevsim.h`, and `netdev.c` net_device ops.

Risks: it is a test stub, so successful replace does not imply real scheduling behavior. Block callback lifetime relies on `flow_block_cb_setup_simple()` bookkeeping. Stats are intentionally zeroed, which tests must treat as simulated output.

Test signals: attach/destroy TAPRIO and ETS qdiscs, query stats, attach TC flower/BPF blocks, disable `NETIF_F_HW_TC`, and verify unsupported setup types fail.
