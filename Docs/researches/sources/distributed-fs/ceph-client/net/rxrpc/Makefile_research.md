# sources/distributed-fs/ceph-client/net/rxrpc/Makefile

## Purpose
Defines the AF_RXRPC module object composition and optional feature objects.

## Important APIs, Types, and Functions
Builds `rxrpc.o` for `CONFIG_AF_RXRPC` from core files such as `af_rxrpc.o`, call/connection/local/peer objects, input/output paths, key/security, sendmsg/recvmsg, RTT, skb, txbuf, and utilities. Optional objects include `proc.o`, `rxkad.o`, `sysctl.o`, and RXGK components. `rxperf.o` is built independently for `CONFIG_RXPERF`.

## Control Flow
Kbuild links the listed objects into one rxrpc module or built-in unit. Optional lines compile features according to `CONFIG_PROC_FS`, `CONFIG_RXKAD`, `CONFIG_SYSCTL`, and `CONFIG_RXGK`.

## State and Persistence
No runtime state; it defines build structure.

## Dependencies and Integration
Integrates with Kconfig symbols and the wider RxRPC source tree. `af_rxrpc.o` supplies module init/exit and socket family registration for the aggregate object.

## Risks and Test Signals
Risks include missing an object that provides symbols referenced by `af_rxrpc.c` or optional security/sysctl code. Test signals are builds across minimal, full, RXKAD, RXGK, procfs, sysctl, and rxperf configurations.
