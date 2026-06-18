## sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_tc.c

Purpose: this file is the LAN966x traffic-control entry point. It dispatches qdisc offloads and classifier block callbacks to specialized modules for mqprio, taprio, tbf, cbs, ets, matchall, and flower handling.

Important APIs and functions: `lan966x_tc_setup()` is the netdev `ndo_setup_tc`-style dispatcher. It recognizes `TC_SETUP_QDISC_MQPRIO`, `TAPRIO`, `TBF`, `CBS`, `ETS`, and `TC_SETUP_BLOCK`. `lan966x_tc_setup_block()` binds clsact ingress/egress callbacks using `flow_block_cb_setup_simple()`. `lan966x_tc_block_cb_ingress()` and `_egress()` route classifier setup to `lan966x_tc_matchall()` or `lan966x_tc_flower()`.

Control flow: mqprio sets `mqprio->qopt.hw = TC_MQPRIO_HW_OFFLOAD_TCS` and adds or deletes hardware TCs based on `num_tc`. TAPRIO, TBF, and ETS switch over command enums and call add/delete helpers; CBS uses its enable flag. Block setup only supports clsact ingress and egress binder types; ingress also records `port->tc.ingress_shared_block = f->block_shared`. Unsupported qdisc, block binder, and classifier setup types return `-EOPNOTSUPP`.

State and persistence: this file stores little state directly beyond the ingress shared-block flag and the global `lan966x_tc_block_cb_list` callback registry. Hardware state persists in the modules it dispatches to. Classifier state is primarily maintained by flow block infrastructure and VCAP/filter helper modules.

Dependencies and integration: integrates with Linux `pkt_cls`, `pkt_sched`, flow block infrastructure, netdev private `lan966x_port`, and driver-local modules for shaping/scheduling and VCAP classifiers. It is the central adapter between kernel tc APIs and LAN966x offload implementations.

Risks: command dispatch must track kernel tc enum evolution. Shared block handling is only explicitly recorded for ingress, so code depending on this flag must not assume egress symmetry. Errors from leaf modules propagate directly to tc. Test signals include exercising each supported qdisc command, binding/unbinding clsact ingress and egress blocks, unsupported binder rejection, shared block behavior, and classifier replace/destroy/stats through both flower and matchall.
