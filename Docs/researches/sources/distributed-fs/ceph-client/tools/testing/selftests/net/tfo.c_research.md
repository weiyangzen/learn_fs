# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tfo.c

## Purpose
`tfo.c` is a small helper binary for TCP Fast Open passive-path testing. It can run as a server that enables passive TCP Fast Open, accepts one connection, reads data, captures `SO_INCOMING_NAPI_ID` from the accepted socket, and writes that NAPI ID to an output file. It can also run as a client that sends one message with `MSG_FASTOPEN`.

## Important APIs, Functions, and Types
Global configuration is held in `cfg_server`, `cfg_client`, `cfg_port`, `cfg_addr`, and `cfg_outfile`. `parse_address` accepts IPv6 text or IPv4 text mapped into an IPv6 sockaddr. `run_server` uses `socket(AF_INET6, SOCK_STREAM)`, `SO_REUSEADDR`, `TCP_FASTOPEN`, `bind`, `listen`, `accept`, `getsockopt(SO_INCOMING_NAPI_ID)`, `read`, and `fprintf`. `run_client` uses `sendto(..., MSG_FASTOPEN, ...)`. `parse_opts` handles `-s`, `-c`, `-h`, `-p`, and `-o`.

## Control Flow
`main` parses options, then dispatches to server or client mode. Server mode requires no `-h`; it binds to `in6addr_any` on the chosen port and writes the observed NAPI ID after accepting and reading. Client mode resolves the provided server address and sends `"Hello, world!"` in the SYN via `MSG_FASTOPEN`.

## State and Persistence
The helper has no long-lived state beyond the output file written by server mode. Socket state is local to one connection. `cfg_outfile` is dynamically allocated with `strdup` and not freed because process exit follows.

## Dependencies and Integration Points
Dependencies are libc, IPv6 sockets, TCP Fast Open support, Linux `SO_INCOMING_NAPI_ID`, and the caller providing a valid output path. It integrates with `tfo_passive.sh`, which supplies namespaces, netdevsim devices, passive TFO sysctl configuration, and validation that the output NAPI ID is nonzero.

## Risks and Test Signals
Risks include missing TFO support, IPv4-mapped IPv6 assumptions, lack of explicit validation that exactly one of `-s`/`-c` is supplied, and server failure if `-o` is omitted. The key signal is a successful client/server exchange and a nonzero NAPI ID written by the server after `accept`.
