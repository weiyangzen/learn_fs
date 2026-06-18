# sources/distributed-fs/ceph-client/include/net/failover.h

Read `sources/distributed-fs/ceph-client/include/net/failover.h` completely for this pass (37 lines, 1210 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/net/failover.h_research.md`.

Purpose: declares the generic netdevice failover coordination API used by master failover devices to manage standby/primary slave netdevices.

Important APIs/types/functions: `struct failover_ops` contains callbacks for slave pre-register/register/pre-unregister/unregister, slave link/name changes, and RX frame handling. `struct failover` stores list membership, RCU pointer to the failover netdev with tracker, and RCU pointer to ops. APIs are `failover_register()`, `failover_unregister()`, and `failover_slave_unregister()`.

Control flow: a failover master registers with a netdev and ops. As matching slave devices appear, change link state, change names, receive frames, or unregister, the failover core calls the relevant callbacks so the master can bind/unbind and route traffic. Unregister tears down the relationship and trackers.

State and persistence: runtime state includes registered failover instances, RCU-protected master device pointer, ops pointer, and netdevice tracker. No durable state is stored.

Dependencies and integration points: depends on netdevice, RCU conventions, RX handlers, and users such as netvsc/virtio-net failover patterns.

Risks: slave/master lifetime and RCU pointer dereference must be synchronized. Callback failures in pre-register paths must roll back cleanly. RX handler must return correct `rx_handler_result_t`. Name/link-change ordering can race with unregister.

Test signals: register/unregister master, hotplug slaves, pre-register failure rollback, slave link/name changes, RX handler forwarding/consume/pass behavior, concurrent slave unregister, and netdevice tracker leak checks.
