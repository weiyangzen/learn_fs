# sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/Kconfig

## Purpose

`Kconfig` declares the `RDMA_SIW` tristate option for the software iWARP driver, enabling RDMA over TCP/IP using standard Ethernet hardware.

## Important APIs, Types, and Functions

The option depends on `INET`, `INFINIBAND`, and `INFINIBAND_VIRT_DMA`, and selects `CRC32` and `NET_CRC32C`. Help text documents kernel/user verbs support, libsiw requirements, and TCP socket integration.

## Control Flow

Kconfig resolution controls whether Kbuild compiles SIW built-in, as a module, or not at all. Dependencies ensure networking, RDMA, virtual DMA, and checksum support are present.

## State and Persistence Behavior

The persistent state is the kernel `.config` selection. It determines module availability and build inclusion.

## Dependencies and Integration Points

The symbol gates the SIW Makefile target and integrates the RDMA subsystem with INET/TCP and checksum helpers. It is conceptually parallel to RXE as a software RDMA transport.

## Risks and Edge Cases

Dependency drift can cause build failures. Userspace provider mismatch, especially missing `libsiw`, can make a built driver unusable from libibverbs.

## Test Signals

Build with `RDMA_SIW=y`, `=m`, and disabled; test dependency-disabled configs; load the module; and run a basic iWARP connection smoke test.
