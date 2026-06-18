# sources/distributed-fs/ceph-client/include/net/libeth/rx.h

Purpose: Defines libeth receive-buffer management and packet-type metadata helpers for Ethernet drivers using page_pool, XDP, checksum/hash offloads, and descriptor-decoded packet types.

Important APIs/types/functions: Headroom and buffer sizing macros define SKB/XDP headroom, L2 overhead, maximum header size, order-0 pages, stride, and page length. `libeth_fqe` stores netmem, offset, and truesize. `libeth_fq` describes a fill queue with hotpath `libeth_fq_fp`, page pool, buffer array, count/truesize, type, header split, XDP flag, buffer length, and NUMA node. `libeth_rx_alloc`, `libeth_rx_sync_for_cpu`, and `libeth_rx_recycle_slow` manage buffers. `libeth_rx_pt`, `libeth_rx_csum`, and `libeth_rqe_info` decode packet type, checksum, and descriptor info.

Control flow: Queue creation prepares page_pool-backed buffers. `libeth_rx_alloc` allocates netmem and returns DMA address plus offset and page_pool offset. After hardware writes, `libeth_rx_sync_for_cpu` either recycles zero-length buffers or syncs DMA for CPU. Packet-type helpers decide IP version, checksum availability, hash availability, and set skb hash type.

State and persistence: State is per-queue runtime buffer state and descriptor metadata. Page_pool owns recycling; `libeth_fqe` tracks each buffer.

Dependencies/integration: Depends on VLAN, page_pool netmem helpers, XDP, net_device feature bits, pkt hash types, and IPv6 build option.

Risks: Zero-length buffer handling prevents processing stripped-FCS fragments; DMA sync offsets must match allocation offsets; IPv6 packet-type handling compiles out when IPv6 is disabled; checksum/hash helpers trust descriptor packet-type mapping. Test signals include page_pool allocation failure, zero-length recycle, XDP and SKB headroom, header split queues, checksum/hash feature toggles, IPv6-disabled builds, and packet-type hash generation.
