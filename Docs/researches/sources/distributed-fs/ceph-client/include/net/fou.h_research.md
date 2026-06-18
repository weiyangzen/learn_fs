# sources/distributed-fs/ceph-client/include/net/fou.h

Purpose: declares Foo-over-UDP and Generic UDP Encapsulation helper hooks for tunnel transmit paths. It provides length calculation and header-build entry points for encapsulating an skb according to `struct ip_tunnel_encap`.

Important APIs: `fou_encap_hlen()` and `gue_encap_hlen()` report the encapsulation header length. `__fou_build_header()` and `__gue_build_header()` build protocol-specific headers, update the next protocol and source port, and consume a type selector. `register_fou_bpf()` registers BPF integration for FOU processing.

Control flow and state: the header is declarative; transmit code computes header length, reserves/pushes space, and calls the builder. No persistent state is defined here. State lives in tunnel configuration, skb metadata, UDP tunnel sockets, and optional BPF registration.

Dependencies and integration: pulls in `skbuff.h`, `flow.h`, `gue.h`, `ip_tunnels.h`, and `udp.h`. It integrates with IP tunnel encapsulation, remote checksum handling via GUE, and UDP tunnel receive/transmit paths.

Risks: header length and build functions must agree exactly or tunnel packets will be malformed. Protocol and source-port output parameters are side effects that route/NAT/checksum code may rely on. Tests should cover FOU and GUE tunnel transmit with checksum offload, BPF registration availability, malformed tunnel config, and GSO/GRO interaction with UDP encapsulation.
