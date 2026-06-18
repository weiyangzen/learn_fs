# sources/distributed-fs/ceph-client/Documentation/netlink/specs/fou.yaml

Purpose: specifies the legacy Generic Netlink API for Foo-over-UDP tunnel port configuration.

Important APIs/types/functions: the family is `fou`, protocol `genetlink-legacy`. The `encap-type` enum distinguishes encapsulation modes. The single `fou` attribute set includes `port`, address family, IP protocol, encapsulation type, remote checksum mode, local/peer IPv4 and IPv6 addresses, peer port, and interface index. Network-order fields are explicitly marked for UDP ports and IPv4 addresses; IPv6 binary attributes require exact 16-byte lengths.

Control flow: `add` creates a configured UDP encapsulation port using port, protocol, type, local/peer addresses, peer port, and ifindex. `del` removes a matching port using address family, ifindex, port, peer-port, and address selectors. `get` can do a targeted lookup with the same selectors or dump all tunnel info. `unspec` is reserved value zero. The operations disable strict/dump validation, preserving legacy behavior.

State and persistence: mutations affect kernel FOU tunnel configuration. The YAML has no persistent state; configured ports live in kernel networking state and normally vanish when the namespace or system resets.

Dependencies and integration points: integrates with Linux FOU/GUE tunnel handling and userspace networking tools. The schema bridges tunnel port management to netlink code generation.

Risks: legacy non-strict validation increases ambiguity around missing or extra attributes. IPv4 and IPv6 selector combinations must match address family. Endianness is mixed: ports and IPv4 addresses are big-endian, while several small fields are host-order integers. `ipproto` enforces only a minimum of 1, leaving semantic protocol validation to kernel implementation.

Test signals: cover add/get/delete round trips for IPv4 and IPv6, peer-specific and wildcard lookups, exact IPv6 length validation, port byte order, invalid protocol zero, and legacy behavior with non-strict validation.
