# sources/distributed-fs/ceph-client/include/linux/net_tstamp.h

Purpose: defines in-kernel hardware timestamp provider metadata and an extensible kernel timestamp configuration wrapper around the UAPI `hwtstamp_config`.

Important APIs and types: software and hardware timestamping masks group the relevant `SOF_TIMESTAMPING_*` bits. `struct hwtstamp_provider_desc` carries provider index and qualifier. `struct hwtstamp_provider` is RCU-freed provider state with source, optional PHY device pointer, and descriptor. `struct kernel_hwtstamp_config` extends UAPI flags/tx_type/rx_filter with the original `ifreq`, copied-to-user marker for legacy lower drivers, timestamp source, and provider qualifier. Helpers copy config to/from UAPI form and compare whether flags/tx/rx fields changed.

Control flow: ioctl/netdev timestamp configuration code copies userspace `hwtstamp_config` into `kernel_hwtstamp_config`, augments it with source/provider information, may pass the original ifreq to legacy lower drivers, and copies the result back if needed. Provider objects can represent netdev or PHY timestamp sources and are released through RCU.

State and persistence: timestamp configuration is runtime netdev/PHY state. Provider objects are in-memory and RCU-managed; no durable state is owned by the header.

Dependencies and integration points: depends on timestamping UAPI and generated ethtool netlink enums. It integrates SIOCG/SIOCSHWTSTAMP, netdev timestamp providers, phylib PTP timestamping, ethtool netlink reporting, and legacy driver ioctl paths.

Risks and test signals: risks include losing extended source/qualifier state when converting to UAPI, double-copying ioctl data when `copied_to_user` is set, RCU lifetime bugs for providers, and failing to detect meaningful config changes. Test netdev versus PHY timestamp providers, legacy lower-driver ioctl handoff, ethtool provider reporting, config compare paths, RCU teardown, and software/hardware timestamp mask combinations.
