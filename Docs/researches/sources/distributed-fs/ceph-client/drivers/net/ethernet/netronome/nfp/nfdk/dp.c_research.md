# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfdk/dp.c

## Purpose
Implements the NFDK datapath for the NFP NIC driver: normal SKB transmit, TX completion, RX buffer recycling, RX metadata parsing, XDP TX/pass/drop handling, NAPI polling, and control-vNIC tasklet traffic. This is the concrete `nfp_dp_ops` datapath used by `nfdk/rings.c` and selected by `nfp_net_alloc()` when firmware reports the NFDK datapath ABI.

## Important APIs, Types, and Functions
- `nfp_nfdk_tx()` is the netdev transmit entry point for NFDK devices. It builds host TX descriptors, maps SKB head/frags, adds optional metadata, handles TSO, checksum, TLS/IPsec hooks, queue stopping, and QCP kick batching.
- `nfp_nfdk_tx_complete()` reclaims transmitted SKBs by comparing software `rd_p` with hardware/QCP completion, unmaps DMA, updates `tx_pkts`, `tx_bytes`, and wakes stopped queues.
- `nfp_nfdk_rx()` consumes completed RX descriptors, parses prepend metadata, applies XDP, redirects control/repr packets, constructs SKBs, handles checksum/VLAN/IPsec, and submits via GRO or egress redirection.
- `nfp_nfdk_poll()` is the NAPI poll function and ties TX completion, RX polling, interrupt unmasking, and adaptive DIM sampling together.
- `nfp_nfdk_ctrl_tx_one()` and `nfp_nfdk_ctrl_poll()` implement control-vNIC TX/RX through the same descriptor format, with a tasklet queue and app control-message dispatch.
- Helpers such as `nfp_nfdk_tx_maybe_close_block()`, `nfp_nfdk_prep_tx_meta()`, `nfp_nfdk_parse_meta()`, `nfp_nfdk_rx_give_one()`, and `nfp_nfdk_tx_xdp_buf()` are the high-risk mechanics for descriptor block boundaries, metadata layout, freelist ownership, and zero-copy XDP reuse.

## Control Flow
TX starts in `nfp_nfdk_tx()`: the driver checks ring space, optionally pushes metadata for HW port mux, VLAN insertion, and IPsec, closes a 256-byte descriptor block with NOP descriptors if the packet would cross a block or exceed a block data budget, DMA maps head/frags, emits data descriptors, emits a metadata descriptor, optionally emits a TSO descriptor, timestamps the SKB, advances `wr_p` and `wr_ptr_add`, and flushes QCP writes when `xmit_more` allows. Errors after partial mapping unwind mapped buffers, count `tx_errors`, flush pending descriptors, and free the SKB.

RX starts when NAPI calls `nfp_nfdk_rx()`. For each descriptor with `PCIE_DESC_RX_DD`, it calculates metadata and packet offsets from `rx_offset`, synchronizes DMA for CPU, parses chained metadata, optionally runs the XDP program, routes control-port payloads to `nfp_app_ctrl_rx_raw()`, resolves representor destination with `nfp_app_dev_get()`, builds an SKB, allocates and posts a replacement buffer, unmaps the old RX buffer, fills hash/mark/protocol/checksum/VLAN/IPsec state, then passes the packet to GRO or `dev_queue_xmit()` for redirection. XDP_TX reuses the RX buffer as a TX buffer and later recycles it in `nfp_nfdk_xdp_complete()`.

Control-vNIC flow uses IRQ tasklets rather than NAPI. `nfp_nfdk_ctrl_poll()` locks the control vector, completes TX, drains queued SKBs through `nfp_nfdk_ctrl_tx_one()`, then polls RX up to a fixed budget and either unmasks IRQs or reschedules itself.

## State and Persistence Behavior
The file mutates volatile datapath state only: ring pointers `wr_p`, `rd_p`, `qcp_rd_p`, descriptor contents, DMA mappings, queued SKBs, and per-vector u64 stats protected by `u64_stats_sync`. RX buffer ownership alternates among hardware freelist, SKB/page fragment, XDP TX ring, and freshly allocated replacement buffers. No disk persistence exists, but firmware-visible BAR/QCP state persists until reset or `nfp_net_clear_config_and_disable()` in common code resets rings.

## Dependencies and Integration Points
Depends on `nfp_net.h` structures, `nfp_net_dp.h` DMA/ring helpers, metadata constants from `nfp_net_ctrl.h`, app routing from `nfp_app.h`, TLS/IPsec helpers from `crypto/`, Linux NAPI/XDP/SKB/DMA APIs, and NFDK descriptor definitions from `nfdk.h`. It is wired into the driver through `nfp_nfdk_ops` in `rings.c` and `nfp_nfdk_netdev_ops` in `nfp_net_common.c`.

## Risks
Descriptor accounting is fragile because NFDK packets must not cross descriptor block boundaries and because first descriptors have a smaller head length field than gather descriptors. DMA error unwinding is sensitive to pointer ordering. RX metadata parsing treats unknown fields as a soft stop and must keep metadata length and packet offsets consistent. XDP_TX recycles RX buffers through TX completion, so pointer tags in `nfp_nfdk_tx_buf` must remain aligned and cleared. Control-message budget exhaustion can reschedule tasklets indefinitely if firmware floods malformed or excessive messages.

## Test Signals
Useful checks include TX/RX under small and jumbo MTUs, fragmented SKBs near `NFDK_TX_DESC_GATHER_MAX`, TSO/USO, VLAN insertion/stripping, checksum modes, metadata port redirection, representor RX, XDP PASS/DROP/TX with tail adjustment, IPsec/TLS offload paths when configured, queue stop/wake under saturation, and forced DMA allocation/mapping failures. Runtime signals are `tx_errors`, `tx_busy`, checksum counters, `rx_replace_buf_alloc_fail`, WARN_ONCE block-overflow messages, NAPI budget behavior, and packet loss after ring reconfiguration.
