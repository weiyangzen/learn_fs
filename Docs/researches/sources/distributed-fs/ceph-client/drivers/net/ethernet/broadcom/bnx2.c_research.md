# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2.c

## Purpose

`bnx2.c` is the Linux PCI Ethernet driver for QLogic/Broadcom NetXtreme II BCM5706, BCM5708, BCM5709, and BCM5716 adapters. It registers the `bnx2` PCI driver, creates a multi-queue `net_device`, loads adapter firmware, initializes on-chip MIPS/RV2P processors, manages DMA descriptor rings, services TX/RX completions through NAPI, and exposes link, diagnostics, EEPROM/NVRAM, Wake-on-LAN, coalescing, ring, channel, and statistics controls through netdev and ethtool callbacks.

This driver is hardware-lifecycle heavy rather than protocol-layer code. Most behavior is organized around safe transitions between PCI probe/remove, netdev open/close, firmware reset/sync, PHY/link setup, interrupt mode selection, ring allocation, and error recovery.

## Important APIs, Types, and Data

- Module and PCI registration: `bnx2_pci_tbl`, `bnx2_pci_driver`, and `module_pci_driver(bnx2_pci_driver)` bind Broadcom/HP PCI IDs to `bnx2_init_one()`, `bnx2_remove_one()`, PM callbacks, PCI AER callbacks, and shutdown.
- Netdev operations: `bnx2_netdev_ops` wires open/close, transmit, stats, multicast/unicast filtering, MII ioctl, MAC address changes, MTU changes, feature changes, TX timeout reset, and optional netpoll.
- Ethtool operations: `bnx2_ethtool_ops` covers driver info, register dump, WOL, nway reset, link settings, EEPROM read/write, interrupt coalescing, ring sizing, pause settings, offline/online self tests, named stats, LED identification, and channel counts.
- Core private state: `struct bnx2` lives in `netdev_priv(dev)` and carries PCI/device pointers, MMIO mapping, chip IDs, flags, PHY state, firmware pointers, shared-memory base, ring sizing, interrupt vectors, NAPI objects, DMA status/statistics blocks, firmware mailbox sequence state, timers, and reset work.
- Ring state: each `struct bnx2_napi` owns `struct bnx2_tx_ring_info` and `struct bnx2_rx_ring_info`, with software rings for SKB/page metadata and DMA-coherent hardware descriptor rings. Descriptor types and status/statistics blocks are defined in `bnx2.h`.
- Firmware data: external firmware files are selected by chip family: 5706/5708 use `bnx2-mips-06-*` and `bnx2-rv2p-06-*`; 5709 uses `bnx2-mips-09-*` plus normal or Ax RV2P firmware. `check_fw_section()` and `check_mips_fw_entry()` validate firmware file offsets, lengths, alignment, and non-empty required sections before loading.
- Hardware access helpers: `BNX2_RD/WR/WR16` do MMIO; `bnx2_reg_rd_ind()`, `bnx2_reg_wr_ind()`, `bnx2_shmem_rd/wr()`, and `bnx2_ctx_wr()` serialize indirect register, shared-memory, and context writes behind `indirect_lock`.
- Optional CNIC integration: under `CONFIG_CNIC`, `bnx2_cnic_probe()`, `bnx2_register_cnic()`, `bnx2_unregister_cnic()`, `bnx2_cnic_start()`, and `bnx2_cnic_stop()` let the storage/offload CNIC layer share device state and an IRQ/status block.

## Control Flow

### Probe and Board Initialization

`bnx2_init_one()` allocates an Ethernet device with TX queue capacity, calls `bnx2_init_board()`, installs netdev/ethtool ops, stores driver data, waits for inherited DMA in kdump kernels, programs feature flags, registers the netdev, and logs discovered adapter information.

`bnx2_init_board()` performs the low-level PCI setup: enabling the device, requesting BARs, mapping registers, enabling bus mastering, setting byte swap/window registers, detecting chip family and bus type, selecting MSI/MSI-X capabilities, setting DMA masks, initializing NVRAM, locating firmware shared memory, validating that firmware is running, reading firmware/VPD strings, loading permanent MAC address, sizing rings, allocating the combined status/statistics DMA block, detecting media/PHY capabilities, setting WOL policy, applying chip errata flags, initializing firmware capability flags, setting default link and flow control, preparing the timer, registering CNIC probe state when applicable, and saving PCI config state.

### Open, Reset, and Runtime Bring-up

`bnx2_open()` requests firmware, disables interrupts, chooses INTx/MSI/MSI-X via `bnx2_setup_int_mode()`, initializes NAPI, allocates DMA memory, requests IRQs, initializes the NIC with PHY reset, starts the timer, clears `intr_sem`, enables interrupts, validates MSI delivery when using MSI, and starts TX queues.

NIC initialization is layered:

- `bnx2_reset_nic()` calls `bnx2_reset_chip()`, frees any still-owned SKBs, calls `bnx2_init_chip()`, then initializes all TX/RX rings.
- `bnx2_reset_chip()` waits for DMA quiescence, syncs reset intent with firmware through mailboxes, deposits a reset signature, triggers chip reset, verifies endian mode, waits for firmware, refreshes firmware capabilities, handles 5706 A0 bad receive-buffer blocks, and configures MSI-X tables when active.
- `bnx2_init_chip()` configures DMA engines, host coalescing, contexts, firmware CPUs, NVRAM, MAC address, queue/rule lookup, MTU/RBUF, status/statistics DMA addresses, coalescing registers, status attention bits, receive filters, 5709 DMA enablement, and final firmware reset synchronization.
- `bnx2_init_all_rings()` clears ring state, initializes TX contexts/descriptors, initializes RX contexts/descriptors, preallocates RX data buffers/pages, writes producer indexes/mailboxes, and sets up RSS/TSS when multiple rings are active.

### TX Path

`bnx2_start_xmit()` selects the TX ring from `skb_get_queue_mapping()`, verifies descriptor availability with `bnx2_tx_avail()`, maps the skb head and fragments for DMA, fills TX BDs with checksum, VLAN, and GSO/LSO metadata, uses `wmb()` before updating the hardware mailbox indexes, accounts bytes with `netdev_tx_sent_queue()`, and stops/wakes the queue based on remaining descriptors.

`bnx2_tx_int()` consumes hardware TX completion indexes during NAPI polling. It handles partial BD completions for GSO packets, unmaps the head and fragment DMA mappings, frees completed SKBs, updates BQL through `netdev_tx_completed_queue()`, stores software/hardware consumer indexes, and uses `smp_mb()` before deciding whether to wake a stopped queue.

### RX Path

RX setup uses two possible buffer classes: normal data buffers allocated by `bnx2_alloc_rx_data()` and optional page-ring buffers allocated by `bnx2_alloc_rx_page()` for jumbo/split receive. `bnx2_set_rx_ring_size()` chooses copy thresholds and page-ring sizing from MTU and chip errata.

`bnx2_rx_int()` reads the hardware RX consumer index, applies `rmb()` before touching descriptors, syncs RX data for CPU access, reads the firmware L2 header, drops frames with CRC/decode/alignment/length/giant errors, either copies small packets into a fresh skb or builds/reuses an skb around the DMA buffer with `bnx2_rx_skb()`, attaches page frags when the packet is split or jumbo, handles VLAN tag acceleration, validates packet length against MTU, sets checksum-unnecessary and RX hash metadata when hardware reported them, records the RX queue, and submits packets through GRO. It refreshes RX producer indexes and byte sequence registers after polling.

The failure paths are explicit: allocation failures recycle RX data and page descriptors through `bnx2_reuse_rx_data()` and `bnx2_reuse_rx_skb_pages()` so the hardware ring remains populated.

### Interrupts and NAPI

The driver supports shared INTx, MSI, one-shot MSI, and MSI-X. `bnx2_setup_int_mode()` chooses vectors from requested channel counts and default RSS queues, enables MSI-X where supported, falls back to MSI if allowed, and ultimately sets real TX/RX queue counts. MSI-X vectors use per-vector NAPI; legacy/MSI uses vector 0.

IRQ handlers mask/ack interrupts and schedule NAPI:

- `bnx2_interrupt()` handles shared INTx, including a status-block flush read to filter unrelated interrupts.
- `bnx2_msi()` and `bnx2_msi_1shot()` schedule NAPI without shared-IRQ filtering.
- `bnx2_poll()` handles link attention, TX/RX work, CNIC polling, and interrupt re-arming for legacy/MSI.
- `bnx2_poll_msix()` handles per-vector fast TX/RX work and re-arms the vector.

`bnx2_timer()` periodically checks for missed MSI, sends firmware heartbeat messages, snapshots firmware RX drops, works around broken stats counters, and runs SERDES-specific link timers.

### Link, PHY, and Firmware Mailboxes

PHY access goes through `bnx2_read_phy()` and `bnx2_write_phy()`, including auto-polling suppression when needed. Link state is guarded by `phy_lock` and represented by `bp->link_up`, `line_speed`, `duplex`, `autoneg`, `advertising`, `req_flow_ctrl`, and `flow_ctrl`.

`bnx2_init_phy()` selects copper, 5706 SERDES, 5708 SERDES, 5709 SERDES, or remote PHY setup. `bnx2_setup_phy()` dispatches to `bnx2_setup_copper_phy()` or `bnx2_setup_serdes_phy()`, while remote PHY-capable firmware is controlled by `bnx2_setup_remote_phy()`.

`bnx2_set_link()` reads BMSR/status, handles 5706 SERDES parallel detection quirks, resolves speed/duplex via family-specific helpers, computes pause flow control, reports netif carrier and firmware link status, and reprograms MAC mode with `bnx2_set_mac_link()`.

Firmware synchronization uses `bnx2_fw_sync()` and shared-memory mailboxes. It increments a driver sequence, writes `BNX2_DRV_MB`, optionally waits for `BNX2_FW_MB` acknowledgement, reports timeouts with MCP state dumps, and returns firmware status. Heartbeat and remote PHY events are also shared-memory mailbox based.

### Close, Reset, PM, and Error Recovery

`bnx2_close()` disables interrupts synchronously, disables NAPI and TX queues, deletes the timer, asks firmware/chip to shut down with a WOL-aware reset code, frees IRQs, frees SKBs and DMA memory, deletes NAPI, and drops carrier.

`bnx2_tx_timeout()` dumps FTQ, PCI/MAC/state, and MCP details before scheduling `bnx2_reset_task()`. The reset task stops the network path, restores PCI state if needed, reinitializes the NIC, and restarts queues/interrupts; failure closes the device.

Suspend detaches and stops the running netdev, deletes the timer, shuts down the chip, frees IRQs/SKBs, and programs WOL. Resume restores D0, reattaches, requests IRQs, initializes the NIC, and restarts the network path. PCI error recovery detaches the device, stops/reset paths on error detection, re-enables/restores PCI state in slot reset, and restarts traffic in resume.

## State and Persistence Behavior

- Persistent hardware state comes from NVRAM/shared memory: flash type/size, VPD firmware version fields, permanent MAC address, WOL enablement, ASF/MFW state, port features, default link policy, remote PHY information, and firmware capability bits.
- Runtime state is kept in `struct bnx2` and reset/rebuilt during open, MTU/ring/channel changes, TX timeout recovery, PM resume, and PCI error recovery.
- Firmware blobs are cached in `bp->mips_firmware` and `bp->rv2p_firmware` after first request and released on failed open/remove.
- Statistics are split between the DMA `statistics_block` and `temp_stats_blk`; `bnx2_save_stats()` accumulates counters before resets that would clear hardware stats.
- Ring state is volatile: DMA descriptor rings, context pages, RX buffers, RX pages, status blocks, and IRQ registrations are allocated on open or reconfiguration and freed on close/error paths.
- NVRAM writes are page-aware and preserve unmodified data on non-buffered flash by reading pages, erasing, and writing back preserved plus new data. Access is protected by the hardware NVRAM arbitration lock and access-enable/write-enable sequences.

## Dependencies and Integration Points

- Linux PCI, PM, DMA, firmware loader, netdevice, NAPI, ethtool, VLAN, checksum/GSO/GRO, MII, workqueue, timer, CRC32, and optional netpoll APIs.
- Hardware register definitions, descriptors, status/statistics layouts, chip constants, firmware section layouts, and CPU register tables come from `bnx2.h` and `bnx2_fw.h`.
- Userspace integration is standard netdev plus ethtool: link settings, EEPROM access, ring/channel tuning, coalescing, WOL, self tests, stats, register dump, MII ioctls, feature toggles, MTU, MAC address, and carrier reporting.
- Optional `CONFIG_CNIC` integration exposes this Ethernet device to the CNIC offload/storage layer and coordinates CNIC interrupts/status-block information across MSI-X and non-MSI-X modes.
- Firmware integration is mandatory for normal operation. The driver loads MIPS and RV2P firmware into multiple on-chip processors and coordinates resets, link state, heartbeat, and remote PHY events through shared-memory mailboxes.

## Risks and Edge Cases

- Firmware availability and format are critical; missing or malformed firmware prevents open. Firmware mailbox timeouts indicate a serious MCP/device synchronization problem and trigger diagnostic dumps.
- Reset ordering is delicate: DMA is explicitly quiesced before chip reset, firmware is consulted before reset, endian mode is verified after reset, and no memory access is allowed after D3hot transition.
- Interrupt mode fallback is important. MSI may be disabled by module parameter, chip errata, bridge detection, or runtime MSI self-test failure; the driver then falls back to INTx.
- Descriptor ring accounting relies on memory barriers and wrap rules. TX queue wake/stop correctness depends on `smp_mb()` ordering between completion and xmit paths.
- RX memory pressure paths must recycle descriptors correctly; otherwise receive rings can drain. Jumbo/page-ring paths add extra frag accounting risk.
- PHY handling is chip- and media-specific, with SERDES 2.5G, remote PHY, 5706 parallel detect, forced link-down, auto-MDIX, CRC fix, and early-DAC errata paths.
- NVRAM writes are destructive if page preservation, erase, alignment, locking, or write-enable sequencing is wrong. Ettool EEPROM write access therefore has real device persistence impact.
- Hardware stats can be broken on older chips; the driver gates skipped counters and periodically forces stats collection for errata workarounds.
- Runtime reconfiguration through ring size, channel count, coalescing, MTU, VLAN RX feature changes, pause settings, or link settings can stop/reset/restart the device and must coordinate with CNIC and firmware.

## Test Signals

- Build-time: this file depends on kernel networking, PCI, firmware, DMA, ethtool, and optional `CONFIG_CNIC`/`CONFIG_PM_SLEEP`/`CONFIG_NET_POLL_CONTROLLER` symbols plus generated register definitions from `bnx2.h`.
- Probe/open signals: successful `register_netdev()`, firmware load messages absent, adapter discovery log, and optional "using MSI" or "using MSIX" log after open.
- Ettool self-tests: `bnx2_self_test()` exposes register, memory, loopback, NVRAM, interrupt, and link tests. Offline mode stops/resets the device and runs register/memory/loopback diagnostics; online tests include NVRAM CRC, interrupt generation, and link state.
- Datapath signals: TX completions update BQL, RX uses GRO, checksum offload and RX hash are reflected in skb metadata, VLAN acceleration changes visible behavior depending on `NETIF_F_HW_VLAN_CTAG_RX`, and hardware stats appear through `get_stats64`/ethtool stats.
- Failure diagnostics: TX timeout logs FTQ, CPU, PCI, EMAC, HC, MSI-X PBA, and MCP shared-memory state before scheduling reset. Firmware sync timeout dumps MCP state.
- PM/error recovery signals: suspend/resume with and without WOL, shutdown to D3hot, PCI AER error recovery, and kdump-kernel DMA quiescence should not hang or access MMIO after prohibited transitions.
