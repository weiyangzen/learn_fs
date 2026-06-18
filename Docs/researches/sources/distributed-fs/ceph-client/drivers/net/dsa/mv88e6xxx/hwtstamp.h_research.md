# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/hwtstamp.h

Purpose: defines PTP/global/per-port timestamp register constants, timestamp status bits, and conditional declarations or stubs for mv88e6xxx hardware timestamping support.

Important APIs/types/functions: constants include PTP ethertype, message type masks, arrival pointer, global config bits, per-port PTP config registers, arrival/departure status/time/sequence registers, and timestamp valid/status masks. When `CONFIG_NET_DSA_MV88E6XXX_PTP` is enabled, it declares hwtstamp DSA hooks, worker/setup/free, and enable/disable helpers; otherwise it provides no-op or `-EOPNOTSUPP` stubs.

Control flow: no runtime flow in the header beyond inline stubs. It gates PTP functionality at compile time and lets non-PTP builds avoid conditional code at call sites.

State and persistence: describes transient hardware timestamp latches and configuration registers. Software state is declared elsewhere in `chip.h`.

Dependencies/integration: includes `chip.h` and is consumed by the main switch driver, PTP implementation, and `hwtstamp.c`.

Risks: spelling-compatible constant names include hardware typos such as departure/overwritten comments; consumers must use masks exactly. Stub behavior must remain consistent with DSA expectations for non-PTP builds.

Test signals: builds with and without `CONFIG_NET_DSA_MV88E6XXX_PTP`, `ethtool -T` returning support only when enabled, and PTP timestamp registers matching ops table register offsets.
