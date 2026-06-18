# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_mqprio.c

Purpose: implements the LAN966x mqprio TC offload shim by configuring Linux netdev traffic classes.

Important APIs and functions: `lan966x_mqprio_add` validates the requested traffic-class count and maps each class to one queue. `lan966x_mqprio_del` resets the netdev traffic-class configuration.

Control flow: add accepts only exactly `NUM_PRIO_QUEUES` classes, calls `netdev_set_num_tc`, and assigns each TC to queue offset `i` with count one. Delete calls `netdev_reset_tc`.

State and persistence: no driver-private state is kept. The netdev TC-to-queue mapping persists in core netdev state until reset.

Dependencies and integration points: called from LAN966x TC setup. Depends on the driver exposing eight TX queues and on `NUM_PRIO_QUEUES` matching hardware priority queues.

Risks and test signals: requests for fewer/more traffic classes are rejected even if Linux can express them. Test `tc qdisc mqprio` with exactly eight classes, invalid class counts, delete/reset, and interaction with ETS/CBS queue offloads.
