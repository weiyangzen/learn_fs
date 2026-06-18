# sources/distributed-fs/ceph-client/drivers/net/ethernet/synopsys/dwc-xlgmac-common.c

Purpose: Provides common XLGMAC driver initialization/removal, module metadata, default configuration, operation-table hookup, hardware feature discovery/printing, and debug packet/descriptor dumps.

Important APIs/functions: `xlgmac_drv_probe()` allocates a multiqueue netdev, stores device resources, initializes RSS mutex/debug level, calls `xlgmac_init()`, and registers the netdev. `xlgmac_init()` sets defaults, assigns IRQ/base/MAC, initializes desc/hw ops, resets hardware, reads feature registers, sets DMA mask, sizes TX/RX queues/rings from CPU and hardware capabilities, seeds RSS key/table/options, attaches netdev/ethtool ops, configures feature flags, and initializes coalescing. `xlgmac_drv_remove()` unregisters/frees the netdev. `xlgmac_get_all_hw_features()` decodes `MAC_HWF*` registers into `struct xlgmac_hw_features`; `xlgmac_print_all_hw_features()` logs decoded capabilities. Dump helpers print descriptors and packet bytes under debug.

Control flow and state: Persistent runtime state is `struct xlgmac_pdata` in netdev private memory. It stores register base, feature flags, queue counts, RSS tables, coalescing values, pause settings, stats, and operation tables. The file currently uses a static test MAC address instead of firmware/platform-provided addressing.

Dependencies and integration points: Called by PCI glue and bus-specific front ends. Integrates with `dwc-xlgmac-desc.c`, `dwc-xlgmac-hw.c`, `dwc-xlgmac-net.c`, `dwc-xlgmac-ethtool.c`, DMA mask APIs, netdev queue APIs, RSS helpers, and hardware register definitions.

Risks and test signals: Static MAC address is unsuitable for multiple devices. `dma_set_mask_and_coherent()` depends on decoded `dma_width`; bad feature reads can break DMA. Queue count selection must not exceed allocated `XLGMAC_MAX_DMA_CHANNELS`. Test probe/remove, multiple devices, feature combinations with/without TSO/RSS/RXCSUM/VLAN hash, DMA mask failures, and register feature decoding against known hardware revisions.
