# sources/distributed-fs/ceph-client/drivers/net/netdevsim/psample.c

Purpose: generates synthetic psample packets and metadata from netdevsim through a debugfs-controlled delayed-work producer.

Important APIs/types/functions: `struct nsim_dev_psample` stores work, psample group, sampling parameters, metadata fields, and active state. `nsim_dev_psample_init()` creates debugfs controls. `nsim_dev_psample_enable()`/`disable()` start and stop reporting. `nsim_dev_psample_report_work()` builds and emits sample packets.

Control flow: init allocates state, initializes delayed work, creates `psample` debugfs directory, and exposes rate, group number, truncation size, in/out ifindex, output traffic class, occupancy max, latency max, and enable. Enabling obtains a psample group in the devlink netns and schedules work. Each work tick builds a fake Ethernet/IPv4/UDP skb with random L4 ports, fills metadata, calls `psample_sample_packet()`, consumes the skb, and reschedules after 100 ms.

State and persistence: debugfs values control volatile reporting behavior. Active state holds a psample group reference until disable or exit. Randomized metadata is not persisted.

Dependencies and integration: depends on `CONFIG_PSAMPLE`, devlink netns lookup, psample group APIs, debugfs, delayed work, random helpers, and IP/UDP header construction.

Risks: `out_tc_occ_max` and `latency_max` are used in bitmask expressions assuming useful power-of-two-like ranges; zero disables each field. Enable returns `-EBUSY` if already active and `-EINVAL` if the group cannot be acquired. Exit must cancel work before putting the group.

Test signals: toggle enable, observe psample netlink packets, change metadata debugfs fields, validate busy/invalid paths, and unload while active to ensure delayed work and group references are released.
