# sources/distributed-fs/ceph-client/drivers/net/ethernet/myricom/myri10ge/myri10ge.c

Purpose: full Myricom Myri-10G Ethernet PCI driver. It manages firmware loading/adoption, the MCP command ABI, RX/TX DMA rings, NAPI polling, MSI/MSI-X queue slicing, ethtool operations, multicast/MAC/MTU controls, watchdog recovery, suspend/resume, and optional DCA.

Important types/functions: `struct myri10ge_priv` is device-global state; `struct myri10ge_slice_state` owns per-queue TX/RX rings, NAPI, IRQ/stat DMA, and DCA fields; `myri10ge_send_cmd` is the central firmware command path. Probe/remove are `myri10ge_probe` and `myri10ge_remove`; open/close are `myri10ge_open` and `myri10ge_close`; data path is `myri10ge_xmit`, `myri10ge_intr`, `myri10ge_poll`, `myri10ge_clean_rx_done`, and `myri10ge_rx_done`.

Control flow: probe enables PCI, sets read-request and DMA masks, maps SRAM WC, parses EEPROM strings for MAC/product/serial, selects and loads firmware, probes RSS slices/MSI-X, allocates coherent slice state, resets firmware, sets netdev features/queues/ethtool ops, tests IRQ allocation, saves PCI state, and registers the netdev. Open resets firmware, enables RSS, requests IRQs, sizes buffers, allocates rings, sets stats DMA and MTU/buffer sizes, enables Linux-style TSO, sends `ETHERNET_UP`, starts watchdog, and wakes TX queues. Close stops watchdog/NAPI/TX, sends `ETHERNET_DOWN`, waits for down IRQ, frees IRQs and rings.

State and persistence: host state includes ring indices, page/DMA mappings, per-slice counters, firmware stat blocks, command DMA memory, firmware name, EEPROM strings, link state, watchdog counters, and PCI saved state. Device state is in SRAM firmware, MCP rings, interrupt queues, and hardware link/PCI state. Firmware is reloaded or adopted at probe and watchdog recovery.

Dependencies and integration: uses PCI, DMA API, firmware loader, CRC32 validation, NAPI/GRO, ethtool, netdev queue APIs, MSI/MSI-X, VLAN helpers, GSO/TSO helpers, timers/workqueues, optional DCA, and MCP ABI headers.

Risks: bit/endian/DMA ABI is complex. TX segmentation must avoid crossing `tx_boundary`; fallback linearization is non-TSO only, while oversized IPv6 TSO may use software GSO. RX page reuse and unmap conditions are subtle. Firmware selection depends on PCIe alignment/ECRC tests. Watchdog recovery closes/reloads/reopens under RTNL and must avoid device-disappeared cases. A suspicious loop in watchdog recovery assigns `ss = mgp->ss` inside a per-slice loop, so review/test should confirm intended slice checking.

Test signals: firmware load CRC failure/adoption, EEPROM parsing, DMA benchmark, NAPI RX under small/jumbo/VLAN/GRO, TX checksum/TSO/GSO/fragments/boundary wrapping, MSI/MSI-X and RSS queue counts, ethtool stats/coalesce/pause/LED, multicast filtering including older firmware fallback, suspend/resume, watchdog reset recovery, and remove while interface is up.
