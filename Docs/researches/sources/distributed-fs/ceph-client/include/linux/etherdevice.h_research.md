# sources/distributed-fs/ceph-client/include/linux/etherdevice.h

Purpose: Ethernet netdevice allocation, header handling, MAC address utilities, and packet helper API.

Important APIs/types/functions: platform MAC retrieval helpers, Ethernet header ops, `alloc_etherdev*`, `devm_alloc_etherdev*`, GRO helpers, reserved multicast bases, address predicates (`is_zero_ether_addr`, `is_multicast_ether_addr`, `is_valid_ether_addr`), address mutators/copy/equality helpers, `compare_ether_header()`, `eth_hw_addr_gen()`, `eth_skb_pkt_type()`, `eth_skb_pull_mac()`, and `eth_skb_pad()`.

Control flow: drivers allocate Ethernet devices, set or discover MAC addresses, validate/change addresses through standard helpers, parse/build Ethernet headers, and classify inbound skb packet type before upper-layer delivery.

State/persistence: netdevice MAC address and assignment type are runtime device state; platform/NVMEM firmware may persist hardware addresses. skb helpers mutate packet metadata/data pointers.

Dependencies/integration: `net_device`, skb, neighbour/header cache, random, CRC32, unaligned access capabilities, endian/BITS_PER_LONG optimizations, firmware nodes/NVMEM.

Risks/test signals: risks are alignment-sensitive fast paths, endian-specific multicast tests, invalid random/generated MACs, skb underrun/padding failures, and RCU address-list iteration. Test unaligned and aligned architectures, MAC validation, multicast/broadcast classification, NVMEM/platform MAC retrieval, GRO, and packet type assignment.
