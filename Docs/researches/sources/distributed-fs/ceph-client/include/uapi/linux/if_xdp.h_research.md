
# sources/distributed-fs/ceph-client/include/uapi/linux/if_xdp.h

## Purpose

`if_xdp.h` defines the AF_XDP socket UAPI for high-performance packet I/O through XDP, including bind sockaddr, UMEM registration, mmap ring offsets, socket options, statistics, descriptors, multi-buffer support, and transmit metadata/offloads. The complete 184-line file was read.

## Important APIs, Types, and Functions

Key structs are `sockaddr_xdp`, `xdp_ring_offset`, `xdp_mmap_offsets`, `xdp_umem_reg`, `xdp_statistics`, `xdp_options`, `xsk_tx_metadata`, and `xdp_desc`. Important flags/options include `XDP_SHARED_UMEM`, `XDP_COPY`, `XDP_ZEROCOPY`, `XDP_USE_NEED_WAKEUP`, `XDP_USE_SG`, `XDP_UMEM_*`, socket options `XDP_MMAP_OFFSETS` through `XDP_MAX_TX_SKB_BUDGET`, mmap page offsets, unaligned buffer masks, `XDP_TXMD_FLAGS_*`, `XDP_PKT_CONTD`, and `XDP_TX_METADATA`.

## Control Flow

User space creates AF_XDP sockets, registers UMEM, configures RX/TX/fill/completion rings, mmaps ring pages, binds to an ifindex/queue, and exchanges descriptors with the kernel. Need-wakeup flags tell applications when to poll or sendto to restart driver progress.

## State and Persistence Behavior

Socket state includes UMEM address/length/chunking/headroom, ring producer/consumer positions, bind queue, shared-UMEM fd, copy/zerocopy mode, statistics, and tx metadata settings. State is per socket/UMEM and lasts until socket close or option reset.

## Dependencies and Integration Points

The header includes `linux/types.h` and integrates with XDP programs, AF_XDP sockets, network drivers supporting zero-copy, NAPI, UMEM DMA mapping, and users such as libxdp/libbpf.

## Risks and Edge Cases

Ring synchronization and memory ordering are critical. Risks include invalid descriptors, unaligned chunk address decoding, multi-buffer packet continuation handling, zerocopy fallback, tx metadata length/placement, need-wakeup stalls, and driver support variation for checksum/timestamp/launch-time offloads.

## Test Signals

AF_XDP selftests should cover copy and zerocopy modes, shared UMEM, need-wakeup, scatter-gather, unaligned chunks, invalid descriptors, ring-full/empty stats, tx timestamp/checksum/launch-time metadata, and mmap offset correctness.
