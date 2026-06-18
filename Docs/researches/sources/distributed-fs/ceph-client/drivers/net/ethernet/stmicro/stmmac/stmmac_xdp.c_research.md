# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_xdp.c

Purpose: XDP program attachment and AF_XDP zero-copy pool setup for STMMAC.

Important APIs and functions: `stmmac_xdp_enable_pool()` validates queue bounds and XSK frame size, DMA maps the pool, stops live queues/NAPI when needed, sets `priv->af_xdp_zc_qps`, restarts queues, and wakes XSK RX. `stmmac_xdp_disable_pool()` disables live queue/NAPI, synchronizes RCU, unmaps the pool, clears the bitmap, and restores normal queues/NAPI. `stmmac_xdp_setup_pool()` selects enable or disable. `stmmac_xdp_set_prog()` rejects jumbo MTU with XDP, swaps `priv->xdp_prog`, releases/opens XDP resources around enabled-state changes, updates split-header state, and manages XDP redirect-target features.

Control flow: netdev BPF setup in `stmmac_main.c` calls these functions. Program attach/detach triggers XDP open/release only when running and the enabled/disabled boolean changes. AF_XDP pool transitions are per queue and stop the affected queue when live.

State and persistence: `priv->xdp_prog`, `af_xdp_zc_qps`, XSK DMA mappings, NAPI mode, and `sph_active` persist across operations. Old BPF programs are released with `bpf_prog_put()`.

Dependencies and integration: AF_XDP helpers, BPF lifetime rules, STMMAC queue control, XDP open/release routines, NAPI, netdev XDP feature helpers, and DMA attrs from `stmmac_xdp.h`.

Risks and test signals: jumbo frames are unsupported with XDP. NAPI transitions must match main-driver queue mode assumptions. XSK frame size must fit Q-in-Q frames. Test XDP attach/detach up/down, AF_XDP bind/unbind, XSK wakeup, redirect features, and traffic after queue transitions.
