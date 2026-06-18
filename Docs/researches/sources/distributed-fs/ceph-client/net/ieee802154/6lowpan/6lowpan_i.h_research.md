## sources/distributed-fs/ceph-client/net/ieee802154/6lowpan/6lowpan_i.h

Purpose: internal header for the IEEE 802.15.4 6LoWPAN module. It shares RX handler result codes, fragmentation dispatch constants, fragment queue key structures, and internal function prototypes across core, RX, TX, and reassembly files.

Important APIs/types/functions: `lowpan_rx_result` is a bitwise result enum with `RX_CONTINUE`, `RX_DROP_UNUSABLE`, `RX_DROP`, and `RX_QUEUED`. `LOWPAN_DISPATCH_FRAG1` and `LOWPAN_DISPATCH_FRAGN` define 6LoWPAN fragment dispatch high bits. `struct frag_lowpan_compare_key` keys reassembly by datagram tag, datagram size, source address, and destination address. `struct lowpan_frag_queue` wraps `struct inet_frag_queue`. Prototypes include `lowpan_frag_rcv()`, frag init/exit, RX init/exit, `lowpan_header_create()`, `lowpan_xmit()`, `lowpan_iphc_decompress()`, and `lowpan_rx_h_ipv6()`.

Control flow and state: this header has no runtime flow but defines the contract between the packet receive path and fragment reassembly. A fragment receiver can return `1` to mean a complete skb is ready, while intermediate fragments are consumed into inet-frag queues.

Dependencies and integration points: includes IEEE 802.15.4 netdevice types, inet fragment infrastructure, and generic 6LoWPAN helpers. It binds the module to the Linux IPv6/6LoWPAN compression stack and per-net frag directories.

Risks: fragment key equality copies full `ieee802154_addr` structs, so address initialization must be deterministic before lookup. Result-code misuse can leak or double-free skbs because each return value encodes ownership.

Test signals: compile-time type checking across all 6LoWPAN files, RX tests for each dispatch path, fragmentation/reassembly tests keyed by tag/addresses, and module load/unload tests for init/exit prototypes.
