# sources/distributed-fs/ceph-client/net/smc/smc_inet.c

## Purpose
`smc_inet.c` registers SMC as an `IPPROTO_SMC` stream protocol under the IPv4 and optional IPv6 inet protocol switch. It maps normal socket operations to SMC socket handlers while creating the internal CLC TCP socket during socket initialization.

## Important APIs, Types, and Functions
Key objects are `smc_inet_prot`, `smc_inet_stream_ops`, `smc_inet_protosw`, and, under IPv6, `struct smc6_sock`, `smc_inet6_prot`, `smc_inet6_stream_ops`, and `smc_inet6_protosw`. Public lifecycle functions are `smc_inet_init()` and `smc_inet_exit()`. `smc_inet_init_sock()` initializes the common SMC socket and creates the CLC socket.

## Control Flow
`smc_inet_init()` registers the IPv4 proto, registers the IPv4 protosw, then conditionally registers IPv6 proto and protosw. Error paths unwind previously registered components in reverse order. Socket creation invokes `smc_inet_init_sock()`, which calls `smc_sk_init(net, sk, IPPROTO_SMC)` and `smc_create_clcsk()`. Socket operations then dispatch to SMC implementations such as `smc_connect`, `smc_accept`, `smc_sendmsg`, and `smc_recvmsg`.

## State and Persistence
The registered proto objects are static module state. Per-socket state is allocated as `struct smc_sock` for IPv4 and `struct smc6_sock` for IPv6, with `SLAB_TYPESAFE_BY_RCU` and protocol hash integration. No persistent storage exists.

## Dependencies and Integration Points
It depends on inet protocol registration APIs, socket/proto infrastructure, and the common SMC socket implementation in `smc.h`. It is the user-facing entry path for applications that create `IPPROTO_SMC` sockets through PF_INET or PF_INET6.

## Risks
Registration ordering and unwind correctness are critical, especially when IPv6 registration partially fails. The IPv6 object embeds `ipv6_pinfo` after `struct smc_sock`, so `ipv6_pinfo_offset` must remain correct. Any missing socket op can break expected stream behavior. CLC socket creation failure must propagate so partially initialized SMC sockets are not exposed.

## Test Signals
Create IPv4 and IPv6 `IPPROTO_SMC` stream sockets, bind/listen/connect/accept, exercise send/recv/poll/ioctl/shutdown/options, and inject registration failure in test kernels to verify cleanup. Check `/proc` or diag visibility through the SMC hash tables.
