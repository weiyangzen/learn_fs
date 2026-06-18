# sources/distributed-fs/beegfs/client_module/source/common/net/sock/IpAddress.h

Purpose: Centralizes BeeGFS kernel helpers for IPv4-mapped IPv6 addresses and typed socket-address construction.

Important APIs/types/functions: `beegfs_mapped_ipv4`, `beegfs_make_sockaddr_in`, `beegfs_make_sockaddr_in6`, `beegfs_get_sockaddr`, `beegfs_get_port`, `Beegfs_Sockaddr`, `bsa_ptr`, `bsa_size`, `bsa_make`, and `bsa_make_for_recv` handle AF_INET/AF_INET6 conversion without unsafe casts at call sites.

Control flow: `bsa_make` emits IPv4 sockaddr data only for v4-mapped, any, or loopback IPv6 values when the requested domain is AF_INET; otherwise it returns false so callers can skip impossible IPv6-on-IPv4 connections.

State and persistence behavior: Pure value helpers; no persistent state.

Dependencies and integration points: Used by standard and RDMA sockets, NIC discovery, and `SocketTk` address formatting across IPv4/IPv6 compatibility paths.

Risks: The AF_INET fallback deliberately special-cases only common addresses; real IPv6 targets fail when IPv6 is disabled. `bsa_size` depends on a populated family and returns full union size for receive buffers.

Test signals: Cover v4-mapped, any, loopback, non-v4 IPv6 with AF_INET, normal AF_INET6, and receive-buffer sizing.
