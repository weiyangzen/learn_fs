# sources/distributed-fs/ceph-client/tools/net/ynl/tests/wireguard.c

Purpose: small command-line demo/test for generated WireGuard YNL bindings. It dumps a WireGuard device by ifindex or ifname and prints peers and allowed IPs.

Important APIs/functions: `build_request()` parses the argument as positive integer ifindex using `strtol()` or falls back to ifname setter. `print_allowed_ip()` formats IPv4/IPv6 allowed IPs. `print_peer_header()` prints 32-byte public keys in hex. `print_peer()` prints peer counters and iterates `allowedips`.

Control flow/state: `main()` requires one argument, creates a YNL socket for `ynl_wireguard_family`, allocates a request, performs `wireguard_get_device_dump()`, iterates devices and nested peers, frees list/request/socket, and returns distinct error codes for usage, socket, and dump failures.

Dependencies/integration: includes generated `wireguard-user.h`, YNL runtime, and libc networking helpers. Requires kernel WireGuard generic netlink family and an existing device.

Risks/test signals: public key formatting is explicitly not constant-time and is only for display. It covers nested multi-attrs (`peers`, `allowedips`), binary key lengths, ifname/ifindex setters, and dump list frees. No kselftest harness or setup wrapper is provided in this subset.
