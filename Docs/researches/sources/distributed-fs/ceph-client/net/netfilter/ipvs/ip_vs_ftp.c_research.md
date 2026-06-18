# sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_ftp.c

## Purpose
`ip_vs_ftp.c` is the IPVS FTP application helper. It inspects FTP control connections, detects active and passive data-channel negotiation commands/responses, creates controlled IPVS connection entries for the related data connections, enables conntrack/NAT expectations, and rewrites passive server responses so clients connect to the virtual address and port instead of the real server.

## Important APIs, types, and functions
The module parameter `ports` controls which TCP control ports are registered, defaulting to 21. The main helpers are `ip_vs_ftp_data_ptr()`, `ip_vs_ftp_init_conn()`, `ip_vs_ftp_done_conn()`, `ip_vs_ftp_get_addrport()`, `ip_vs_ftp_out()`, and `ip_vs_ftp_in()`. The registered `struct ip_vs_app ip_vs_ftp` supplies `init_conn`, `done_conn`, `pkt_out`, and `pkt_in` callbacks. Per-netns lifecycle is handled by `__ip_vs_ftp_init()` and `__ip_vs_ftp_exit()`, with module-level `ip_vs_ftp_init()` and `ip_vs_ftp_exit()`.

## Control flow
When a matching FTP control connection is bound to the app, `ip_vs_ftp_init_conn()` marks the control connection with `IP_VS_CONN_F_NFCT` so conntrack can support later mangling/expectations. Incoming client-to-server packets are scanned only in established TCP state after ensuring a writable linear skb. `PASV` and `EPSV` commands store passive mode in `cp->app_data`. `PORT` and `EPRT` commands parse the client address/port and create or find a controlled active data connection from that client endpoint to the virtual service data port (`vport - 1`), targeting the same real server data port (`dport - 1`), then move that connection to TCP listen state.

Outgoing server-to-client packets are also processed only after the control connection is established. If `app_data` indicates a pending `PASV` or `EPSV`, the helper parses `227` or `229` response data, creates or finds a related passive data connection from the client to the virtual passive port, targets the real server address/port, and adds the control relationship. It then rewrites the server response to advertise the virtual address/port for PASV or the virtual port for EPSV using `nf_nat_mangle_tcp_packet()`, registers a related conntrack expectation with `ip_vs_nfct_expect_related()`, normalizes checksum state when needed, resets `app_data` to active, moves the data connection to listen state, and releases it.

`ip_vs_ftp_get_addrport()` parses old IPv4 comma-separated `PORT`/`227` payloads and extended delimiter-based `EPRT`/`EPSV` payloads. Extended parsing validates family compatibility and supports EPSV responses that omit address family and address while using a preset address from the real server.

## State and persistence behavior
The helper stores mode state in `cp->app_data` using small integer sentinel values for active, PASV, and EPSV. It creates controlled `struct ip_vs_conn` objects for data channels and links them to the FTP control connection with `ip_vs_control_add()`, so control lifetime and packet counters are related. It mutates skb payload bytes for passive responses through NAT helper APIs and intentionally leaves `diff` at zero because conntrack/NAT sequence adjustment already handles the payload-size change. Module state includes the configured port list and `exiting_module` flag used to decide whether per-netns exit should unregister the app.

## Dependencies and integration points
The file integrates with the IPVS application framework, IPVS connection lookup/creation, TCP state transitions, control-connection relationships, conntrack and NAT helper APIs, `nf_nat_mangle_tcp_packet()`, `nf_conntrack_expect`, skb linearization/writability, IPv4/IPv6 address parsers, and pernet registration. It depends on the core packet path invoking app `pkt_in` and `pkt_out` callbacks for registered TCP control ports.

## Risks and edge cases
Parsing is payload-string based and can return partial-match `-1` without buffering across packets, so split FTP commands may be missed until retransmission or later data. The helper only supports old `PORT`/`PASV` forms for IPv4, while `EPRT`/`EPSV` handle IPv4 or IPv6 with family validation. It assumes FTP data port is control port minus one for active mode. Payload mangling can fail under memory pressure and causes packet drop. Passive rewrite depends on conntrack being present; without a conntrack object the helper cannot rewrite and returns failure for that response path. `EPSV ALL` is not supported. The `exiting_module` guard means netns exit skips unregister unless module unload is in progress.

## Test signals
Test active FTP `PORT` and `EPRT` for IPv4/IPv6 family correctness, passive `PASV` and `EPSV` response rewrite, related connection creation and listen-state transition, conntrack expectation registration, checksum behavior after mangling, configured non-21 ports, malformed and partial FTP payloads, unsupported `EPSV ALL`, memory-pressure mangle failure, module unload/pernet cleanup, and NAT FTP service behavior requiring conntrack registration from the control plane.
