# sources/distributed-fs/ceph-client/net/phonet/pep-gprs.c

## Purpose
`pep-gprs.c` adapts a Phonet pipe endpoint socket into a point-to-point network device carrying IPv4/IPv6 packets. It is the `PNPIPE_ENCAP_IP` implementation used by PEP sockets for GPRS-style data connectivity.

## Important APIs, types, and functions
`struct gprs_dev` binds a PEP socket to a `struct net_device` and stores original socket callbacks. Netdevice callbacks are `gprs_open()`, `gprs_close()`, and `gprs_xmit()` via `gprs_netdev_ops`; setup is `gprs_setup()`. Socket callbacks are `gprs_state_change()`, `gprs_data_ready()`, and `gprs_write_space()`. Public functions are `gprs_attach()` and `gprs_detach()`.

`gprs_type_trans()` classifies received payloads as IPv4 or IPv6. `gprs_recv()` converts PEP data skbs into netif RX skbs, including a frag-list wrapper for misaligned payloads. `gprs_xmit()` validates outbound skb protocol, transfers ownership to the PEP socket, sends with `pep_write()`, updates netdev stats, and gates the netdev TX queue based on `pep_writeable()`.

## Control flow and state
Attach allocates and registers a `gprs%d` netdev, then under the socket lock verifies no existing `sk_user_data`, rejects closed/listening/dead sockets, installs callback overrides, stores the adapter in `sk_user_data`, releases the socket, and takes an extra socket reference. Detach restores original callbacks under the lock, unregisters the netdev, and drops the socket reference.

Inbound flow is callback-driven: PEP data readiness drains `pep_read()` until empty, orphans each skb, and passes it to `gprs_recv()` for protocol classification and `netif_rx()`. Outbound flow is netdev-driven: `ndo_start_xmit` sends only IPv4/IPv6, calls `pep_write()`, updates stats, stops the queue, and wakes it again if PEP credits allow.

## State and persistence behavior
Runtime state persists while the socket is attached: `sk_user_data` points to `gprs_dev`, netdev private data points back to the socket, and overridden callbacks route socket events into netdev queue/carrier behavior. No disk persistence exists. Close paths in `pep.c` call `gprs_detach()` when `pn->ifindex` is set.

## Dependencies and integration points
The file depends on PEP helpers (`pep_writeable()`, `pep_write()`, `pep_read()`), netdevice registration, IP/EtherType definitions, and TCP state constants used by PEP. It exposes a netdev of type `ARPHRD_PHONET_PIPE`, with `NETIF_F_FRAGLIST` support and no hardware header.

## Risks and edge cases
Key risks are socket callback hijacking/restoration races, attach/detach lifetime ordering, misaligned PEP data, nested frag-list cleanup, netdev stats consistency, and TX queue wake/stop correctness with PEP credit flow control. `gprs_attach()` registers the netdev before taking the socket lock, so failures after registration must unregister correctly.

## Test signals
Tests should enable `PNPIPE_ENCAP_IP`, verify a `gprs%d` device appears and disappears, send IPv4/IPv6 through the device, reject non-IP protocols, exercise PEP close/reset behavior, check queue wake on credits, test attach failure on already attached/dead/listening sockets, and validate RX stats/drop counters for malformed payloads.
