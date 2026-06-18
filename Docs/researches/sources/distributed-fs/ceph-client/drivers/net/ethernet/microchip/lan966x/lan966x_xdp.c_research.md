# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_xdp.c

## Purpose
This file provides LAN966x XDP setup, XDP transmit, receive-side program execution, and XDP RX queue registration. XDP is only supported when the driver uses FDMA, because the implementation depends on page-backed receive buffers and FDMA transmit helpers.

## Important APIs, Types, And Functions
`lan966x_xdp()` dispatches `XDP_SETUP_PROG` to `lan966x_xdp_setup()`. `lan966x_xdp_xmit()` implements netdev XDP frame transmit. `lan966x_xdp_run()` executes the installed BPF program on an RX page and returns FDMA disposition codes. `lan966x_xdp_present()`, `lan966x_xdp_port_init()`, and `lan966x_xdp_port_deinit()` manage global presence detection and `xdp_rxq_info` lifetime.

## Control Flow
Program setup rejects XDP when `lan966x->fdma` is absent. It atomically swaps the port program with `xchg()`, detects whether the switch moved between no-XDP and any-XDP states, and reloads the FDMA page pool only for those global transitions. On reload failure, it restores the old program. RX builds an `xdp_buff` starting after the IFH and headroom, runs the BPF program, and maps `XDP_PASS`, `XDP_TX`, `XDP_REDIRECT`, invalid actions, `XDP_ABORTED`, and `XDP_DROP` into FDMA actions.

## State And Persistence
The only persistent-in-memory XDP state is `port->xdp_prog` and `port->xdp_rxq`. The FDMA page pool may be rebuilt when XDP presence changes globally. BPF program references are owned through `bpf_prog_put()` after replacement. No disk persistence exists.

## Dependencies And Integration Points
The file depends on Linux BPF/XDP APIs, `lan966x_fdma_reload_page_pool()`, `lan966x_fdma_xmit_xdpf()`, page allocation geometry from `lan966x->rx.page_order`, and IFH layout constants. It integrates with netdev BPF ops and the FDMA RX path that calls `lan966x_xdp_run()`.

## Risks And Edge Cases
`lan966x_xdp_run()` assumes a non-NULL `port->xdp_prog`; callers must check XDP presence before invoking it. `XDP_TX` passes a page and length to a helper whose `xdp_xmit` path also accepts `xdp_frame` objects, so helper semantics must remain clear. The setup path swaps programs before FDMA reload and restores on error, but concurrent RX must be synchronized by the surrounding driver. XDP redirect errors drop the frame.

## Test Signals
Check extack rejection without FDMA, attaching/detaching XDP on one and multiple ports, page-pool reload on first attach and last detach, XDP_PASS delivery, XDP_DROP counters or traffic disappearance, XDP_TX loopback/transmit, XDP_REDIRECT to another device or cpumap, invalid action tracing, and RX queue registration cleanup.
