# sources/distributed-fs/ceph-client/include/net/geneve.h

Purpose: defines Geneve tunnel wire headers and minimal device integration. Geneve carries a UDP destination port, virtual network identifier, OAM/critical bits, and variable-length options.

Important APIs/types: `GENEVE_UDP_PORT` is 6081. `struct geneve_opt` represents one option header with class, type, reserved bits, length, and flexible data. `GENEVE_CRIT_OPT_TYPE` identifies critical option type bit. `struct genevehdr` contains version, option length, OAM/critical flags, protocol type, 24-bit VNI, reserved byte, and option data. `netif_is_geneve()` detects rtnetlink devices whose kind is `"geneve"`. Under `CONFIG_INET`, `geneve_dev_create_fb()` creates a fallback device.

Control flow and state: this header only describes on-wire layout and device detection. Runtime state lives in Geneve net devices, UDP sockets, tunnel metadata, and options parsed elsewhere.

Dependencies and integration: includes `udp_tunnel.h`, and integrates with tunnel offload, flower encap-option matching, routing, and netdev rtnl link ops.

Risks: bitfield layout is endian-sensitive and option length units must match protocol expectations. Critical options need explicit handling to avoid accepting unsupported semantics. Tests should cover encode/decode of VNI and option length, OAM/critical flags, device-kind detection, fallback device creation, offload matching on Geneve options, and malformed option truncation.
