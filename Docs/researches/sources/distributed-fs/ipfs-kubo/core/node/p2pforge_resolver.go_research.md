# sources/distributed-fs/ipfs-kubo/core/node/p2pforge_resolver.go

Purpose: implements local DNS resolution for p2p-forge hostnames that encode IP addresses, avoiding network DNS for AutoTLS A/AAAA lookups. Important APIs are `p2pForgeResolver`, `NewP2PForgeResolver`, `LookupIPAddr`, and `LookupTXT`.

Control flow: suffixes are normalized. `LookupIPAddr` lowercases/trims the hostname, matches configured suffixes, requires `<encoded-ip>.<peerID>.<suffix>`, validates the peer ID, rejects labels starting/ending with hyphen, parses IPv4 by replacing hyphens with dots, parses IPv6 by replacing hyphens with colons, and falls back to the underlying resolver on any mismatch. `LookupTXT` always delegates to fallback for ACME DNS-01 compatibility.

State and persistence: no persistent state; stores suffix list and fallback resolver.

Dependencies/integration: libp2p peer ID validation, net/netip, multiaddr-dns. Used by `DNSResolver` when AutoTLS DNS lookup skipping is enabled.

Risks: fallback is essential for future DNS record formats and invalid hostnames; TXT delegation must remain for certificate issuance. Tests cover IPv4, IPv6, multiple suffixes, fallback, errors, and TXT delegation.
