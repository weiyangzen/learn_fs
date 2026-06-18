## sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_packet.c

### Purpose
`sparx5_packet.c` implements manual CPU-port packet extraction and injection for Sparx5 when FDMA is not used or for common packet handling support. It parses extraction IFHs, builds receive SKBs, injects transmit SKBs with IFHs, and handles TX queue recovery after injection watermark backpressure.

### Important APIs, Types, And Functions
Exports are `sparx5_xtr_flush()`, `sparx5_ifh_parse()`, `sparx5_port_xmit_impl()`, `sparx5_manual_injection_mode()`, `sparx5_xtr_handler()`, and `sparx5_port_inj_timer_setup()`. `sparx5_xtr_grp()` reads one frame from `QS_XTR_RD()`, `sparx5_inject()` writes SOF, IFH, payload, padding, EOF, and dummy CRC to `QS_INJ_WR()`, and `sparx5_injection_timeout()` clears watermark counters and wakes the TX queue.

### Control Flow
RX interrupt handling polls up to 64 frames while extraction data is present. Each frame starts with an IFH, which yields source port and timestamp. The body loop reads words until EOF, PRUNED, or ABORT escape words; good frames are trimmed by FCS length, optionally marked `offload_fwd_mark`, receive timestamped, protocol-decoded, counted, and delivered via `netif_rx()`. TX builds an IFH, optionally requests PTP timestamp state and adds rewrite metadata, then sends through FDMA if available or manual injection under `tx_lock`. Successful Sparx5 manual TX consumes the skb except for two-step PTP frames, which are held until timestamp completion.

### State, Persistence, And Dependencies
RX/TX state is mostly hardware FIFO state plus per-netdev stats and `sparx5->tx` counters. PTP TX state is stored in skb control block fields and per-port PTP queues. Backpressure state uses the netdev queue and per-port hrtimer. Dependencies include generated QS/DSM register macros, IFH helpers from `sparx5_netdev.c`, PTP helpers, FDMA ops, and `sparx5_get_internal_port()`.

### Integration Points
This file is used by netdev `ndo_start_xmit`, RX IRQ setup, manual injection initialization during driver bring-up, and PTP timestamp paths. It also cooperates with bridge offload by marking already-forwarded SKBs.

### Risks
RX allocation uses `mtu + ETH_HLEN`; oversized frames or malformed extraction could overrun expectations if hardware delivers unexpected lengths. EOF byte accounting and byte-swap handling are delicate. Manual TX returns `-EBUSY` from `sparx5_inject()` but the public xmit path treats negative non-busy values as drops. Two-step PTP skb ownership differs from normal TX and must match timestamp IRQ release.

### Test Signals
Exercise extraction of normal, abort, pruned, and inactive-port frames; IFH timestamp parsing; bridge offload mark; manual injection queue-not-ready and watermark recovery; FDMA and manual TX paths; small frames requiring padding; and PTP two-step busy/release behavior.
