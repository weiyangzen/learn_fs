# sources/distributed-fs/ceph-client/include/net/6lowpan.h

Purpose: This header defines 6LoWPAN core data structures and helpers for IPv6 header compression/decompression over low-power link layers such as IEEE 802.15.4 and BTLE.

Important APIs, types, and functions: Constants define EUI-64 length, next-header compression bounds, IPHC buffer sizes, context table size, and dispatch bytes for raw IPv6 and IPHC. Helpers `lowpan_is_ipv6()` and `lowpan_is_iphc()` classify dispatch bytes. `struct lowpan_iphc_ctx` and `struct lowpan_iphc_ctx_table` represent compression contexts with active and compression flags. `struct lowpan_dev` is the per-netdev private root with link-layer type, debugfs entry, context table, and flexible link-layer private data. IEEE 802.15.4 specific structs track neighbor short address, lowpan device info, and skb control block fragmentation fields. Address helpers build link-local IPv6 addresses from EUI-64 or EUI-48 link-layer addresses. `lowpan_fetch_skb()` safely pulls inline header data. `lowpan_register_netdevice()`, `lowpan_register_netdev()`, unregister variants, `lowpan_header_decompress()`, and `lowpan_header_compress()` are the public operations.

Control flow: A link-layer adaptation driver allocates a netdev with `LOWPAN_PRIV_SIZE()`, registers it with a lowpan link-layer type, and uses compression/decompression around packet transmit and receive. Receive paths inspect the dispatch byte, fetch compressed fields from the skb, reconstruct IPv6 headers using link-layer addresses and context table state, and pass IPv6 packets upward. Transmit paths compress IPv6 headers into IPHC form with optional next-header compression and push link-layer frames.

State and persistence behavior: Runtime state lives in `lowpan_dev`, the IPHC context table guarded by a spinlock, per-neighbor short addresses, fragment tags, and skb control blocks. Context active/compression flags influence compression decisions until changed by the context ops implementation.

Dependencies and integration points: It depends on IPv6, net namespaces, debugfs, mac802154, sk_buff helpers, and net_device private storage. It integrates with IEEE 802.15.4 neighbors, fragmentation/reassembly code, and IPv6 packet paths.

Risks: `lowpan_fetch_skb()` returns true on failure, which can be misread by callers. Header compression requires sufficient headroom and unshared skbs on transmit. Context table updates must be synchronized. Address reconstruction must correctly flip the universal/local bit for EUI-64 but not for all EUI-48 variants. Fragment tag handling is small and wraparound-sensitive.

Test signals: Dispatch classification, raw IPv6 and IPHC receive, EUI-64/EUI-48 link-local reconstruction, context-based address compression, insufficient skb pull failures, transmit with minimal headroom, short-address validation, fragment tag wraparound, and registration/unregistration for BTLE and IEEE 802.15.4 devices.
