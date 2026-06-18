# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_xdp.h

Purpose: XDP-facing declarations for STMMAC.

Important APIs and definitions: `STMMAC_RX_DMA_ATTR` combines `DMA_ATTR_SKIP_CPU_SYNC` and `DMA_ATTR_WEAK_ORDERING` for AF_XDP pool DMA mapping. `stmmac_xdp_setup_pool()` attaches/detaches an XSK pool to a queue. `stmmac_xdp_set_prog()` attaches/detaches a BPF program and uses `netlink_ext_ack` for errors.

Control flow: included by `stmmac_main.c` and implemented by `stmmac_xdp.c`; netdev BPF/XDP operations call these entry points.

State and persistence: no header state. The functions mutate XDP program, AF_XDP queue bitmap, DMA mappings, and split-header activity in `stmmac_priv`.

Dependencies and integration: caller-provided STMMAC/BPF/XSK types and DMA API semantics. The DMA attributes must match RX buffer ownership expectations.

Risks and test signals: DMA attribute changes can affect data integrity. Validate with AF_XDP zero-copy traffic, XDP attach/detach, and builds with XDP-enabled STMMAC.
