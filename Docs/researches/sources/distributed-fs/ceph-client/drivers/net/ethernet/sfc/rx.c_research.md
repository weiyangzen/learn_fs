# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/rx.c

Purpose: this file implements the second half of the RX datapath: interpreting completion metadata, validating lengths/fragments, syncing DMA buffers, pipelining packet delivery, running XDP, building SKBs, attaching checksums/timestamps, and passing packets to GRO, channel handlers, or the stack.

Important APIs: `efx_rx_packet()` is called by NIC-specific event/RX code when a packet completion is seen. `__efx_rx_packet()` consumes the pending packet recorded on the channel and delivers it. Internal helpers validate length, build SKBs from page fragments, deliver SKBs, and run XDP.

Control flow: `efx_rx_packet()` marks flags on the first RX buffer, validates fragment count/length/scatter assumptions, discards explicit or invalid packets, syncs DMA for all fragments, advances past the RX prefix, recycles pages, flushes any previously prefetched packet, then stores the new packet in `channel->rx_pkt_*`. `__efx_rx_packet()` reads prefix length if needed, handles loopback selftest, updates RX stats, runs XDP for single-fragment packets, clears checksum flags if netdev RX checksum is disabled, and chooses GRO for TCP packets without a special channel handler or normal SKB delivery otherwise.

State and dependencies: state spans `rx_buf->flags/len/page_offset`, queue packet/byte counters, channel pending packet fields, XDP stats, loopback state, and `efx->xdp_prog`. Dependencies include RX common buffer/free/GRO helpers, XDP APIs, checksum/GRO APIs, PTP timestamp attach, and channel `receive_skb` hooks.

Risks and tests: risks include overlength handling, prefix length zero packets, fragmented packets with XDP, page ownership transfer to SKB/XDP TX/redirect, checksum metadata correctness, and pending-packet flush ordering. Test signals include RX traffic with and without RX prefixes, jumbo/scattered frames, XDP PASS/DROP/TX/REDIRECT/error cases, loopback selftests, GRO throughput, RX checksum toggles, PTP RX timestamps, and low-memory SKB allocation failures.
