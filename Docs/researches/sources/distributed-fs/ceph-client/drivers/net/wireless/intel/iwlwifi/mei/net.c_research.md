# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mei/net.c

## Purpose

`net.c` implements CSME packet selection for iwlmei. It evaluates CSME-provided out-of-band filters against received Ethernet/IP/ARP traffic, copies selected inbound frames into the SAP shared-memory data queue, and exports a TX-side helper that mirrors DHCP client packets to CSME.

## Important APIs, Types, and Functions

The public functions are `iwl_mei_rx_filter()` and `iwl_mei_tx_copy_to_csme()`. Local filters include `iwl_mei_rx_filter_eth()` for multicast L2 filters, `iwl_mei_rx_filter_arp()` for IPv4 ARP request/reply policy, `iwl_mei_rx_filter_ipv4()` for IPv4 and ICMP handling, `iwl_mei_rx_filter_tcp_udp()` for flex TCP/UDP port filters, and a stub `iwl_mei_rx_filter_ipv6()`.

## Control Flow

The netdev RX handler in `main.c` calls `iwl_mei_rx_filter()`. This first asks `iwl_mei_rx_pass_to_csme()` whether CSME should receive the frame and whether the host stack should still see it. If CSME should receive a pass-through packet, the code copies the skb; if CSME consumes it, it reuses the original. It restores the MAC header, appends a SAP data header through `iwl_mei_add_data_to_ring()`, and frees only copied skbs.

The TX mirror path is narrower. `iwl_mei_tx_copy_to_csme()` only copies IPv4 UDP DHCP client-to-server frames, reconstructs an Ethernet header from the 802.11 header, strips 802.11/IV/SNAP bytes while preserving the ethertype, wraps it in `SAP_MSG_CB_DATA_PACKET`, and queues it to CSME.

## State and Persistence Behavior

`net.c` itself stores no durable state. It consumes immutable snapshots of `struct iwl_sap_oob_filters` published by `main.c` and mutates transient skb header offsets while filtering. Packet copies become persistent only after `iwl_mei_add_data_to_ring()` writes them into shared SAP memory.

## Dependencies and Integration Points

It depends on Linux skb pull/headroom helpers, Ethernet/ARP/IP/UDP/ICMP headers, cfg80211/mac80211 802.11 header helpers, SAP filter structures, and `iwl_mei_add_data_to_ring()` from `main.c`.

## Risks and Edge Cases

IPv6 filtering is explicitly TODO, except for an ICMPv6 branch inside the IPv4 parser that is unreachable for true IPv6 packets. TCP filtering intentionally reads only a UDP-sized header, which matches the first source/destination port fields but relies on the earlier pull length. Header offset manipulation in the DHCP TX path is sensitive to IV length and SNAP assumptions. Filter arrays stop scanning after the first disabled entry, so CSME must send filters packed without holes.

## Test Signals

Exercise multicast L2 stop/copy flags, ARP target matching and wildcarding, ICMP echo suppression, TCP/UDP flex filters with and without IP matching, pass/copy/consume outcomes, truncated skb handling, DHCP TX mirroring, and IPv6 non-support behavior. KUnit or packet-injection tests should verify skb ownership and that consumed originals are freed only by the RX handler caller.
