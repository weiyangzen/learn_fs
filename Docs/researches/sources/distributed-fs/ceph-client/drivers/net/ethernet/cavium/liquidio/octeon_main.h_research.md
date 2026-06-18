# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_main.h

Purpose: Provides common LiquidIO driver definitions used across host driver files: device-private tasklet data, TX buffer free metadata, BAR mapping helpers, endian helpers, soft-command wait semantics, and rounding macros.

Important APIs, types, and functions: `struct octeon_device_priv` ties a device to DROQ tasklet/NAPI state. `struct octnet_buf_free_info` stores the `lio`, `skb`, gather list, DMA pointer, and optional piggybacked soft command needed when TX descriptors are reclaimed. BQL hooks are declared for sent/completed byte accounting. `octeon_swap_8B_data()` converts 64-bit blocks to big endian. `octeon_map_pci_barx()` and `octeon_unmap_pci_barx()` request/release PCI BAR regions and ioremap/iounmap them. `wait_for_sc_completion_timeout()` centralizes blocking wait and timeout/error translation for soft commands.

Control flow: Probe/setup code maps BARs through the inline helpers. Control-command senders wait on `sc->complete`; response-manager code completes the soft command or marks timeout, while this helper sets `caller_is_done` when wait exits abnormally.

State and persistence: The file manipulates volatile PCI BAR mappings, soft-command lifetime flags, and netdev/BQL state. No durable storage is involved.

Dependencies and integration: Includes Linux signal scheduling, PCI/netdev structures, LiquidIO `struct lio`, `octeon_soft_command`, and response status codes. It is included widely and therefore defines cross-module contracts.

Risks: BAR index multiplication assumes LiquidIO BAR layout. Soft-command waiting is race-sensitive: callers must set `caller_is_done` after consuming successful responses so response cleanup can safely free buffers.

Test signals: Probe failure paths for BAR request/ioremap, soft-command wait timeout/interruption/fatal timeout, BQL accounting on TX reclaim, and big/little endian command preparation.
