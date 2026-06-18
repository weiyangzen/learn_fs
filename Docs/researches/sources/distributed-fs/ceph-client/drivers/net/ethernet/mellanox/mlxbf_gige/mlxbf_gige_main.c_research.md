# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxbf_gige/mlxbf_gige_main.c

## Purpose
`mlxbf_gige_main.c` owns the BlueField GigE platform and netdevice lifecycle. It probes ACPI resources, maps MMIO blocks, initializes MDIO/PHY, registers the netdev, opens and stops the port, manages reset/clean-port sequencing, sets MAC filters, provides netdev ops, handles link-mode policy for BF2/BF3, and detaches the interface during shutdown.

## Important APIs, Types, and Functions
Key helpers are `mlxbf_gige_alloc_skb()`, `mlxbf_gige_initial_mac()`, `mlxbf_gige_cache_stats()`, `mlxbf_gige_clean_port()`, `mlxbf_gige_open()`, `mlxbf_gige_stop()`, `mlxbf_gige_eth_ioctl()`, `mlxbf_gige_set_rx_mode()`, `mlxbf_gige_get_stats64()`, BF2/BF3 adjust-link and link-mode functions, `mlxbf_gige_probe()`, `mlxbf_gige_remove()`, and `mlxbf_gige_shutdown()`. `mlxbf_gige_netdev_ops` binds Linux netdev callbacks.

## Control Flow and State
Probe maps MAC/LLU/PLU resources, allocates `net_device`, initializes private state, reads hardware version, probes MDIO, disables filters/promiscuous mode, sets the initial MAC from hardware or random fallback, configures 64-bit DMA, obtains IRQs, finds and connects the PHY, applies version-specific link-mode restrictions, and registers the netdev. Open enables the port, caches counters that clean-port will clear, performs clean-port reset, resets RX polarity, starts PHY, initializes TX and RX rings, enables NAPI and the queue, requests IRQs, enables filters/multicast, and finally enables selected interrupts after a barrier. Stop disables interrupts, stops queue/NAPI, frees IRQs, stops PHY, tears down rings, caches stats, and cleans the port.

State persists in hardware registers, PHY state, DMA rings, `priv->valid_polarity`, MAC filter registers, cached stats, and `priv->prev_speed` for BF3 PLU reprogramming. `mlxbf_gige_alloc_skb()` enforces the hardware DMA alignment rule by overallocating and aligning packet data to a 2 KB boundary before mapping.

## Dependencies and Integration Points
The file depends on platform/ACPI resources, DMA APIs, netdevice registration, PHYLIB, NAPI, IRQ helpers in `mlxbf_gige_intr.c`, RX/TX setup, ethtool ops, and BF2/BF3 register definitions.

## Risks and Test Signals
Risks include unsupported `hw_version` indexing into link config, clean-port timeout, wrong resource order, PHY IRQ fallback behavior, missing unwind of MDIO/PHY/netdev resources, statistics lost across clean-port, and DMA alignment regressions. Test signals are ACPI probe, module load/unload, open/close cycles, shutdown path, random MAC fallback, BF2 and BF3 link negotiation, speed changes on BF3, ethtool/netdev stats, and fault injection for ring/IRQ/PHY failures.
