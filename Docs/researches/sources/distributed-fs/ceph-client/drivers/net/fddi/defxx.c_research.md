# sources/distributed-fs/ceph-client/drivers/net/fddi/defxx.c

## Purpose
Implements the Linux FDDI network driver for DEC PDQ-based adapters: DEFTA on TURBOchannel, DEFEA on EISA, and DEFPA on PCI. It binds bus devices, maps PDQ/PFI/ESIC register resources, allocates DMA-visible descriptor/consumer/command memory, initializes firmware-visible rings, exposes a `net_device`, and handles FDDI RX, TX, multicast filtering, MAC override, statistics, interrupts, reset, and teardown.

## Important APIs, Types, And Functions
The driver registers `pci_driver`, `eisa_driver`, and `tc_driver` instances from `dfx_init()` and unregisters them in `dfx_cleanup()`. `dfx_register()` is the common probe path and `dfx_unregister()` is the common remove path. The `net_device_ops` table wires `dfx_open()`, `dfx_close()`, `dfx_xmt_queue_pkt()`, `dfx_ctl_get_stats()`, `dfx_ctl_set_multicast_list()`, and `dfx_ctl_set_mac_address()` into the networking core.

Low-level hardware access is funneled through `dfx_port_read_long()` and `dfx_port_write_long()`, which choose MMIO or port I/O dynamically. Bus-specific setup is in `dfx_get_bars()`, `dfx_bus_init()`, `dfx_bus_uninit()`, and `dfx_bus_config_check()`. Adapter commands are issued by `dfx_hw_port_ctrl_req()` for port-control CSR commands and `dfx_hw_dma_cmd_req()` for firmware DMA commands. Receive and transmit ring routines are `dfx_rcv_init()`, `dfx_rcv_queue_process()`, `dfx_rcv_flush()`, `dfx_xmt_queue_pkt()`, `dfx_xmt_done()`, and `dfx_xmt_flush()`.

The key private state is `DFX_board_t` from `defxx.h`, especially `descr_block_virt/phys`, `cmd_req_virt`, `cmd_rsp_virt`, `cons_block_virt`, producer register shadows, CAM/filter tables, link state, receive skb pointers, transmit skb descriptors, bus base, and statistics counters.

## Control Flow
Probe allocates an FDDI netdev, enables PCI when needed, chooses MMIO first with fallback to I/O for PCI/EISA, reserves resources, maps MMIO or records port base, initializes bus logic, resets the adapter into DMA-unavailable state, reads the factory MAC address via `PI_PCTRL_M_MLA`, allocates one coherent block for descriptors, command buffers, receive storage metadata, and the consumer block, then registers the netdev.

Open requests the shared IRQ, restores the factory MAC, clears local CAM/filter state, initializes the spinlock, and calls `dfx_adap_init()`. `dfx_adap_init()` disables PDQ interrupts, resets/uninitializes DMA, clears false Type 0 interrupts and ring shadows, programs burst size, consumer block address, descriptor block address and byte-swap mode, sends `CHARS_SET`, `SNMP_SET`, CAM, filter, receive-buffer, and `START` commands, then reenables default interrupts.

Interrupt handling is split by bus. PCI checks `PFI_STATUS_M_PDQ_INT`, masks PFI interrupts, calls `dfx_int_common()`, clears PFI status, and reenables PFI. EISA checks ESIC pending status and masks/unmasks the ESIC. TURBOchannel checks PDQ pending bits directly. `dfx_int_common()` completes TX, processes RX, writes the Type 2 producer/completion shadow once, then handles Type 0 interrupts. Type 0 processing handles fatal errors, transmit flush requests, state changes, link availability, halted states, and reset/reinitialization.

Transmit validates FDDI LLC length, drops stale packets while link is unavailable, prepends the three-byte Motorola MAC packet request header, DMA-maps the skb, fills one transmit descriptor, records the skb for completion, advances the transmit producer, and writes the Type 2 producer register. Completion uses the consumer block to unmap and consume skbs. Receive walks the firmware consumer index, reads the FMC descriptor, accounts CRC/status/length errors, either copies small packets or swaps in a new skb for larger packets, strips driver padding/CRC, calls `fddi_type_trans()`, passes packets through `netif_rx()`, updates counters, then recycles descriptors.

## State And Persistence Behavior
Persistent in-kernel state lives in `DFX_board_t` for the lifetime of the netdev. Hardware state is rebuilt at each open or adapter reset from driver-maintained defaults: factory MAC, optional MAC override, CAM entries, multicast counts, promiscuous bits, burst size, full-duplex flag, requested TTRT, and receive buffer count. DMA-visible descriptor and command memory is allocated once during probe and freed during remove. RX skbs are dynamically allocated under `DYNAMIC_BUFFERS` and flushed on close/reset failure paths. TX skbs are held until adapter completion or flush.

The adapter itself persists firmware state across commands until reset; the driver intentionally resets it on initialization, close, fatal Type 0 errors, and halted-state recovery. There is no disk persistence or userspace configuration file handling.

## Dependencies And Integration Points
The file integrates with Linux PCI, EISA, TURBOchannel, DMA mapping, netdevice, FDDI helpers, shared IRQ handling, MMIO/PIO APIs, and module infrastructure. It depends heavily on constants and packed hardware ABI definitions from `defxx.h`, plus Linux FDDI constants such as `FDDI_K_ALEN`, `FDDI_K_LLC_ZLEN`, and `FDDI_K_LLC_LEN`. Bus IDs cover DEC PCI FDDI, EISA `DEC300[1-4]`, and TC `PMAF-F*` modules.

## Risks
The driver assumes 32-bit DMA addresses when writing descriptors and truncates DMA addresses to `u32`; this is historically mitigated by platform/device DMA constraints but is a key portability risk. TX error handling after a full ring returns `NETDEV_TX_BUSY` after DMA mapping and descriptor writes without unmapping in that path, so ring-full behavior is a sensitive area. The command path busy-waits with long `udelay()` loops and can consume CPU during firmware stalls. Receive processing in interrupt context can process multiple buffers and allocate skbs, so memory pressure leads to drops. MMIO/PIO fallback and EISA decoder programming are hardware-specific and hard to validate without real devices. Reset recovery reenters adapter initialization from interrupt context for serious errors, so locking and interrupt masking assumptions matter.

## Test Signals
Useful build signals are `CONFIG_DEFXX` across PCI, EISA, TC, `CONFIG_HAS_IOPORT`, and big-endian builds because producer/consumer layouts differ. Runtime smoke signals are probe resource reservation, factory MAC read, `register_netdev()`, successful `ifconfig/ip link set up`, IRQ request, link-available messages, packet RX/TX counters, multicast filter changes, MAC override, close/reopen, and module unload. Fault-oriented signals include forced link transitions, TX flush interrupt handling, adapter halt reset, DMA mapping failure paths, RX memory pressure drops, and no IRQ storms on shared lines.
