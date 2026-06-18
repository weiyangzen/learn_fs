# sources/distributed-fs/ceph-client/net/xdp/Kconfig

Purpose: defines AF_XDP socket and diagnostic monitoring build options.

Important symbols: `XDP_SOCKETS` is a bool depending on `BPF_SYSCALL` and enables channels between XDP programs and userspace. `XDP_SOCKETS_DIAG` is a tristate depending on `XDP_SOCKETS` and enables SOCK_DIAG monitoring used by `ss`.

Control flow: Kconfig selection decides whether core AF_XDP socket, UMEM, queue, buffer-pool, and XSKMAP objects are compiled and whether the diagnostic module/object is available.

State and persistence: build configuration persists in `.config`; no runtime state is directly managed here.

Dependencies and integration: aligns with BPF redirect map support, AF_XDP socket registration, and the Makefile object list under `net/xdp`.

Risks and test signals: dependency mistakes could expose AF_XDP without BPF syscall support or diag without sockets. Tests should include `CONFIG_BPF_SYSCALL=n`, `XDP_SOCKETS=y`, diag as built-in/module, and AF_XDP selftests matching selected features.
