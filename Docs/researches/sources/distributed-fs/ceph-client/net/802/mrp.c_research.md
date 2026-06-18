<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/802/mrp.c -->
# sources/distributed-fs/ceph-client/net/802/mrp.c

This file implements the IEEE 802.1Q Multiple Registration Protocol applicant, used by VLAN MVRP. It generalizes attribute registration with vector-attribute packing and both join and periodic timers.

State is per-device `struct mrp_port`, per-application `struct mrp_applicant`, and rbtree-backed `struct mrp_attr` entries keyed by type/length/value. Applicant state transitions come from `mrp_applicant_state_table`; transmit events map through `mrp_tx_action_table`. Public APIs include `mrp_request_join()`, `mrp_request_leave()`, `mrp_init_applicant()`, `mrp_uninit_applicant()`, `mrp_register_application()`, and `mrp_unregister_application()`.

Control flow registers a packet type with `dev_add_pack()`. Applicant init joins the group address, initializes rbtrees/queues, marks the applicant active, and arms join and periodic timers. Join/leave requests mutate attributes under lock. TX events build PDUs with message headers and vector-attribute headers, packing three events per byte and incrementing sequential attribute values. Receive flow ignores `PACKET_OTHERHOST`, verifies application version, parses messages and vector attributes with `skb_header_pointer()`/`skb_copy_bits()`, handles LeaveAll flags, and feeds remote events into the state machine.

State is volatile and synchronized with RTNL lifecycle, RCU pointers, spinlocks, timers, and skb queues. The `active` flag prevents timer rearming during teardown before final TX flushing. Dependencies include netdevice packet handlers, multicast membership, skb control-buffer sizing, and MRP UAPI structures.

Risks include packed-vector parsing mistakes, skb control-buffer overflow for long attributes, timer teardown races, malformed length/flag handling, and hardware/device unregister interaction. Tests should cover MVRP join/leave, sequential vector packing/unpacking, LeaveAll handling, periodic redeclare behavior, malformed frames, and applicant uninit final flush.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/802/mrp.c -->
