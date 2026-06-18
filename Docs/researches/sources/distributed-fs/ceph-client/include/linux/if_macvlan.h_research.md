# `sources/distributed-fs/ceph-client/include/linux/if_macvlan.h`

Purpose: internal macvlan device definitions, statistics helpers, link registration hooks, lower-device access, and offload helpers.

Important APIs/types/functions: `struct macvlan_dev`, multicast filter constants, `macvlan_count_rx`, `macvlan_common_setup`, `macvlan_common_newlink`, `macvlan_dellink`, `macvlan_link_register`, `macvlan_dev_real_dev`, `macvlan_accel_priv`, `macvlan_supports_dest_filter`, and `macvlan_release_l2fw_offload`.

Control flow and state: `macvlan_dev` persists per virtual device, linking upper `dev`, lower device, port, accel private data, per-CPU stats, filters, mode, flags, and optional netpoll. `macvlan_count_rx` updates per-CPU VLAN-style counters with `u64_stats_sync`.

Dependencies/integration: depends on netdevice, VLAN stats, rtnetlink/netlink, netpoll, and UAPI macvlan modes. Integrated with macvlan/macvtap link creation and L2 forwarding offload.

Risks: stats require correct per-CPU access and sync; `macvlan_dev_real_dev` BUGs if called when macvlan is unavailable; offload release changes unicast filters on the lower device; mode checks control destination filtering behavior.

Test signals: macvlan create/delete in all modes, RX success/error/multicast stat updates on 32-bit and 64-bit, offload release, disabled-config build behavior, and lower-device unregister handling.
