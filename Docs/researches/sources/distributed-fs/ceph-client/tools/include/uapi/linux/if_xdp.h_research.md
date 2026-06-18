# sources/distributed-fs/ceph-client/tools/include/uapi/linux/if_xdp.h

Purpose: defines the AF_XDP socket ABI for high-performance packet I/O between userspace rings and XDP-capable network drivers.

Important APIs/types: `sockaddr_xdp` binds a socket to interface/queue and optional shared UMEM. Ring and mmap types include `xdp_ring_offset` and `xdp_mmap_offsets`. `xdp_umem_reg` registers packet memory with chunk size, headroom, flags, and optional Tx metadata length. `xdp_statistics` and `xdp_options` report drops, invalid descriptors, ring starvation, and zero-copy. Socket options configure ring sizes, UMEM, statistics, options, and Tx budget. Descriptor-related definitions cover mmap offsets, unaligned chunk address masks, and Tx metadata requests/completion flags.

Control flow, state, and persistence: userspace creates an AF_XDP socket, configures Rx/Tx/fill/completion rings and UMEM, mmaps rings, binds to a queue, then advances producer/consumer indices. Kernel/driver and userspace share ring state until socket/UMEM teardown.

Dependencies and integration points: depends on Linux types. It integrates XDP programs, netdev queue configuration, zero-copy driver support, libxdp/libbpf, and high-throughput packet processors.

Risks and test signals: risks include producer/consumer ordering bugs, invalid descriptors, UMEM alignment/chunk masking mistakes, zero-copy fallback assumptions, need-wakeup handling, and multi-buffer packet drops if `XDP_USE_SG` is absent. Tests should run copy and zero-copy modes, shared UMEM, unaligned chunks, need-wakeup polling, multi-buffer Rx, Tx metadata, and statistics validation under packet loss/backpressure.
