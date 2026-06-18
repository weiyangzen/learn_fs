<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/mailbox-mchp-ipc-sbi.c -->
# sources/distributed-fs/ceph-client/drivers/mailbox/mailbox-mchp-ipc-sbi.c

## Purpose
`mailbox-mchp-ipc-sbi.c` implements a Microchip IPC mailbox that delegates hardware operations to a vendor SBI extension. It discovers IPC channels, initializes per-channel buffers, sends messages by physical address, and handles cluster aggregate IRQs for receive and clear notifications.

## Important APIs, Types, and Functions
SBI payload formats are `struct mchp_ipc_mbox_info`, `mchp_ipc_init`, `mchp_ipc_status`, and `mchp_ipc_sbi_msg`. `struct mchp_ipc_sbi_mbox` stores device, channels, cluster IRQ config, controller, and hardware type. Key functions are `mchp_ipc_sbi_send()`, `mchp_ipc_sbi_chan_send()`, `mchp_ipc_probe()`, `mchp_ipc_startup()`, `mchp_ipc_send_data()`, `mchp_ipc_cluster_aggr_isr()`, and `mchp_ipc_mbox_xlate()`.

## Control Flow
Probe verifies the Microchip vendor SBI extension, allocates a probe buffer, calls `SBI_EXT_IPC_PROBE`, creates the discovered number of channels, allocates per-channel private structs with IDs, requests per-online-CPU aggregate IRQs named by hart ID for MIV IHC hardware, and registers an IRQ-completion mailbox controller. Startup allocates TX/RX SBI payload buffers, calls channel init to learn max message size, then allocates max-size TX/RX data buffers. Send copies client data into the TX buffer, writes an SBI payload pointing to it, and calls `SBI_EXT_IPC_SEND`. The aggregate ISR identifies the source hart, asks SBI for status, maps status bits to channel IDs, performs receive SBI calls for message-present bits, and calls `mbox_chan_received_data()` or `mbox_chan_txdone()` for clear bits.

## State and Persistence
Per-channel buffers are allocated on startup and freed on shutdown. Cluster status buffers are devm-managed per online CPU. Channel IDs are stable for the controller lifetime. No software queue is maintained beyond buffers holding the latest send/receive payload.

## Dependencies and Integration Points
The driver depends on RISC-V SBI, Microchip vendor ID, hart/CPU mapping, platform IRQ names, DMA-addressable physical memory via `__pa()`, mailbox core, public `linux/mailbox/mchp-ipc.h`, and compatible `microchip,sbi-ipc`.

## Risks and Edge Cases
The channel ID computation in the ISR is subtle and tied to cluster topology and no-loopback assumptions. Buffers are allocated with `kmalloc()` and converted with `__pa()`, so platform memory mapping expectations matter. CPU hotplug after probe is not reflected in `cluster_cfg`. Send does not validate client `msg->size` against `max_msg_size` before copying.

## Test Signals
Test SBI extension absence, probe/channel-init failures, per-hart IRQ discovery, send/receive/clear interrupts, max message size enforcement by clients, shutdown buffer freeing, invalid phandle channel IDs, and multi-hart channel mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/mailbox-mchp-ipc-sbi.c -->
