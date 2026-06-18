# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/irq.py

Purpose: Tests driver IRQ reporting and affinity behavior across queue/XDP/link reconfiguration.

Important APIs/functions: `read_affinity()`, `write_affinity()`, `check_irqs_reported()`, `_check_reconfig()`, `check_reconfig_queues()`, `check_reconfig_xdp()`, `check_down()`, `NetDrvEnv`, `EthtoolFamily`, `NetdevFamily`, `ksft_disruptive`, `ip`, `cmd`, and `defer`.

Control flow: The script reads IRQs reported through netdev/ethtool Netlink, writes and restores IRQ affinity, then runs reconfiguration callbacks such as channel count changes, XDP attach/detach, and link down/up while verifying IRQs remain reported and affinity behavior is stable.

State and persistence: Writes `/proc/irq/*/smp_affinity`, changes channels, attaches XDP, and toggles interface state. Defer restores settings where possible.

Dependencies and integration points: Requires IRQ reporting support, writable affinity, ethtool/netdev Netlink families, XDP dummy BPF, and disruptive permissions.

Risks and test signals: Affinity writes are host-sensitive. Failures indicate IRQ Netlink reporting, driver reconfiguration, XDP queue, or affinity persistence regressions.
