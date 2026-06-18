# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net.h

## Purpose
Defines the core data structures, constants, BAR/QCP accessors, ring/vector state, datapath state, vNIC state, flow steering entries, mailbox async-message entries, and exported common netdev APIs for the NFP network device driver.

## Important APIs, Types, and Functions
- Constants define control/QCP BAR indices, queue/vector limits, default descriptor counts, RX headroom/non-data sizing, VXLAN port count, MSI-X vector layout, and descriptor helper macros.
- `struct nfp_net_tx_ring`, `struct nfp_net_rx_ring`, and `struct nfp_net_r_vector` hold per-ring/per-vector pointers, DMA state, queues, NAPI/tasklet state, XDP/XSK state, IRQ data, DIM, and stats.
- `struct nfp_net_dp` is the mutable datapath configuration cloned during reconfiguration: ring arrays, counts, MTU, buffer size, XDP program, ctrl bits, DMA direction, ops, and XSK pools.
- `struct nfp_net` is the full vNIC object: datapath, capabilities, RSS, IRQs, reconfig state machine, BAR locks, coalesce settings, QCP bars, TLS/IPsec state, mailbox state, debugfs, app/port pointers, async mailbox work, and flow steering.
- Inline BAR and QCP accessors (`nn_readl`, `nn_writel`, `nfp_qcp_wr_ptr_add`, etc.) centralize MMIO access.
- Prototypes expose allocation/init/clean, control open/close, firmware reconfig, mailbox, IRQ, TLS, ring reconfig, flow steering, RSS/coalesce, debugfs, and netdev ops.

## Control Flow
This header underpins the common lifecycle: allocation fills `nfp_net`, init reads capabilities and initializes netdev/control state, open prepares vectors/rings and enables firmware, NAPI/datapath updates rings/vectors, reconfiguration clones and swaps `nfp_net_dp`, and clean/free tears down registered resources.

## State and Persistence Behavior
Most state is volatile kernel runtime state mirrored to firmware through control BARs and QCP queues. The reconfiguration fields serialize synchronous and posted firmware updates. Stats are per-vector and protected with seqlocks. TLS/IPsec/mailbox/flow-steering fields track offloaded firmware resources but are cleaned during netdev teardown.

## Dependencies and Integration Points
Depends on Linux netdevice, PCI, interrupts, DIM, workqueue, XDP, semaphore, and NFP control ABI. Integrates NFD3/NFDK datapath ops, app layer, crypto offloads, XSK, devlink/debugfs, and firmware BAR configuration.

## Risks
This is a high-coupling header: layout or semantic changes affect every datapath and lifecycle file. Ring pointer math assumes power-of-two descriptor counts via `D_IDX`. BAR access locking is caller-managed; missing `nn_ctrl_bar_lock()` can corrupt mailbox/reconfig operations. Reconfig and async mailbox state require careful flush/wait during clean.

## Test Signals
Broad build coverage, lockdep around BAR/devlink locks, open/close/reconfig stress, queue-count changes, XDP/XSK toggles, RSS/coalesce operations, TLS/IPsec offload enable/disable, flow steering add/delete, and debugfs builds.
