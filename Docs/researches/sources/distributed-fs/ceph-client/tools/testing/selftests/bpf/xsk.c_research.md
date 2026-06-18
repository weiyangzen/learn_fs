# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/xsk.c

## Purpose

`xsk.c` is a local AF_XDP userspace access library used by BPF selftests. It creates and tears down UMEMs and AF_XDP sockets, maps fill/completion/RX/TX rings, supports shared UMEM contexts, attaches/detaches XDP programs, updates XSK maps, queries attach mode, and changes interface MTU through rtnetlink.

## Important APIs, Types, and Functions

Core private types are `struct xsk_umem`, `struct xsk_ctx`, `struct xsk_socket`, and `struct nl_mtu_req`. Public functions include `xsk_umem__fd`, `xsk_socket__fd`, `xsk_umem__create`, `xsk_is_in_mode`, `xsk_set_mtu`, `xsk_attach_xdp_program`, `xsk_detach_xdp_program`, `xsk_clear_xskmap`, `xsk_update_xskmap`, `xsk_socket__create_shared`, `xsk_socket__create`, `xsk_umem__delete`, and `xsk_socket__delete`. Internal helpers configure defaults, read `XDP_MMAP_OFFSETS`, map rings, receive netlink ACKs, and manage shared contexts.

## Control Flow

UMEM creation validates arguments, opens an AF_XDP socket, registers user memory through `XDP_UMEM_REG`, and maps fill/completion rings. Socket creation configures RX/TX ring sizes, reuses or creates a context for ifindex/queue, maps RX/TX rings, binds `sockaddr_xdp`, and handles shared-UMEM fd selection. Deletion releases contexts, unmaps rings using current mmap offsets, closes fds when appropriate, and enforces UMEM refcount rules.

## State and Persistence Behavior

Persistent process state is heap-allocated UMEM/socket/context objects, kernel AF_XDP sockets, mmapped rings, and UMEM reference counts. External state includes XDP program attachments, XSK map entries, and interface MTU changes requested by callers.

## Dependencies and Integration Points

It depends on AF_XDP UAPI, mmap offsets, libbpf attach helpers, route netlink, ethtool/socket headers, list helpers, and memory barriers exposed in `xsk.h`. It is consumed by XSK selftests and XDP hardware metadata tests.

## Risks and Test Signals

Risks include reference-count leaks, incorrect unmap lengths, ring-size power-of-two assumptions, shared UMEM lifetime bugs, errno sign inconsistencies, and leaving interface MTU/XDP state to callers. Signals are successful UMEM/socket creation in copy/zero-copy/shared modes, descriptor ring progress, clean `-EBUSY` when deleting active UMEMs, and no leaks across repeated teardown tests.
