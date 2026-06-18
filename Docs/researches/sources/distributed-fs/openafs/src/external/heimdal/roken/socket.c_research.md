# sources/distributed-fs/openafs/src/external/heimdal/roken/socket.c

## Purpose
Supplies portable socket-address helpers and socket option wrappers for IPv4/IPv6 code, plus Windows socket-to-file-descriptor bridging and a Linux `SOCK_CLOEXEC` fallback wrapper.

## Important APIs, Types, And Functions
Exports include `socket_set_any`, `socket_set_address_and_port`, `socket_addr_size`, `socket_sockaddr_size`, `socket_get_address`, `socket_get_port`, `socket_set_port`, `socket_set_portrange`, `socket_set_debug`, `socket_set_tos`, `socket_set_nonblocking`, `socket_set_reuseaddr`, `socket_set_ipv6only`, `socket_to_fd`, `rk_SOCK_IOCTL`, and `rk_socket`.

## Control Flow
Address helpers switch on `sa_family`, filling or inspecting `sockaddr_in` and, when configured, `sockaddr_in6`. Unsupported families either return zero/NULL or terminate with `errx` for setter APIs. Option helpers call `setsockopt`, `fcntl`, or `ioctl` only when relevant compile-time constants exist. `rk_socket` retries without `SOCK_CLOEXEC` if the kernel rejects that flag with `EINVAL`.

## State And Persistence
The functions mutate socket address structures or kernel socket options. `socket_to_fd` transfers close ownership to the C runtime file descriptor on Windows.

## Dependencies And Integration Points
The file depends on `roken.h` for socket abstraction and error macros. It supports network code that needs portable address-family handling without scattering platform conditionals.

## Risks And Test Signals
Fatal `errx` on unsupported families can surprise library callers. Several option setters ignore errors. `socket_set_address_and_port` and port helpers expect ports already in network byte order. Tests should cover IPv4/IPv6 address mutation, nonblocking toggles, option-setting availability, Windows `_open_osfhandle`, and Linux `SOCK_CLOEXEC` fallback behavior.
