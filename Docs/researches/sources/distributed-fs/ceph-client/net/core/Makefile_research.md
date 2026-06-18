# sources/distributed-fs/ceph-client/net/core/Makefile

## Purpose
This kbuild file defines the object composition for the Linux networking core under `net/core`. It selects always-built core networking objects, conditionally includes feature-specific modules based on `CONFIG_*` symbols, and ensures foundational facilities such as sockets, skbuffs, datagram helpers, device registration, rtnetlink, XDP, GRO/GSO, flow offload, page pool, BPF socket maps, and diagnostic/debug helpers are linked into the kernel or module build as configured.

## Important APIs, Types, and Functions
The file does not define C APIs directly; its interface is kbuild object selection. Key always-built objects include `sock.o`, `skbuff.o`, `datagram.o`, `stream.o`, `scm.o`, `net_namespace.o`, `flow_dissector.o`, `dev.o`, `dst.o`, `rtnetlink.o`, `filter.o`, `sock_diag.o`, `xdp.o`, `gro.o`, `gso.o`, `net-sysfs.o`, `hotdata.o`, and queue/config helpers. Conditional objects expose feature APIs when their configs are enabled, for example `page_pool.o`, `netpoll.o`, `fib_rules.o`, `drop_monitor.o`, `timestamping.o`, `lwt_bpf.o`, `sock_map.o`, `bpf_sk_storage.o`, and debug/fault-injection objects.

## Control Flow
Kbuild evaluates `obj-y` and `obj-$(CONFIG_...)` assignments during kernel build generation. Objects listed in `obj-y` are linked unconditionally for this directory. Objects listed under a config symbol are included only when that symbol evaluates to built-in or module as appropriate. The ordering matters because it influences link order and therefore initcall ordering and symbol resolution within the core networking subsystem.

## State and Persistence
There is no runtime state in the Makefile itself. Its persistent effect is the compiled networking-core artifact: enabling or disabling config symbols changes which code paths, exported symbols, sysctls, procfs files, BPF helpers, debug hooks, and test objects exist in the resulting kernel.

## Dependencies and Integration Points
The Makefile depends on kernel kbuild semantics and Kconfig symbols such as `CONFIG_BPF_SYSCALL`, `CONFIG_PAGE_POOL`, `CONFIG_PROC_FS`, `CONFIG_NETPOLL`, `CONFIG_LWTUNNEL_BPF`, `CONFIG_NET_DEVMEM`, and `CONFIG_DEBUG_NET`. It integrates the two researched C files directly: `datagram.o` is part of the always-built networking core, while `bpf_sk_storage.o` is included when `CONFIG_BPF_SYSCALL` is enabled. Downstream protocols and drivers depend on the exported functions and subsystems made available by these objects.

## Risks
The primary risks are build- and integration-level. Accidentally moving a common object behind a config gate can break protocols that assume exported networking helpers are always present. Adding objects in the wrong order can affect init sequencing. Gating BPF, devmem, procfs, tracing, or debug files under the wrong symbol can produce missing symbols or dead code. Because this file controls a dense subsystem, small changes can have broad build-matrix impact.

## Test Signals
Useful signals include allmodconfig/allnoconfig/defconfig builds, targeted builds with `CONFIG_BPF_SYSCALL`, `CONFIG_PAGE_POOL`, `CONFIG_NET_DEVMEM`, and debug/test options toggled, link-time missing-symbol checks, and boot smoke tests that exercise sockets, netdevice registration, BPF socket storage, datagram receive paths, and rtnetlink/sysfs/procfs exposure.
