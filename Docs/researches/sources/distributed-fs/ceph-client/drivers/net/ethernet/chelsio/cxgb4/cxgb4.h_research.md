# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4.h

## Purpose
This is the central cxgb4 driver header. It defines adapter-wide constants, hardware/firmware parameter structures, port and queue state, filter specifications, helper inlines for register and netdev access, and prototypes shared across cxgb4 translation units.

## Important APIs, Types, And Functions
Key structures include `struct adapter_params`, `struct port_info`, `struct sge`, `struct sge_rspq`, `struct sge_fl`, `struct sge_txq`, `struct adapter`, `struct ch_filter_specification`, and `struct filter_entry`. Important helpers include `t4_read_reg()`, `t4_write_reg()`, `t4_read_reg64()`, `t4_write_reg64()`, `netdev2pinfo()`, `netdev2adap()`, `mk_adap_vers()`, `qtimer_val()`, mailbox wrappers, `hash_mac_addr()`, and feature tests such as `is_offload()`, `is_uld()`, and `is_ethofld()`. The prototype section exposes SGE, firmware, RSS, memory-window, filter, port, PTP, TC, ULD, thermal, and MAC-filter operations.

## Control Flow
The header has no main runtime flow, but its inlines directly perform MMIO and object translation. Register helpers wrap `readl`/`writel` and `readq`/`writeq`. Mailbox wrappers select sleeping or non-sleeping submission. Netdev helpers recover `port_info` and `adapter` from Linux network devices. Queue descriptor structures define how SGE allocation, interrupt handling, and CUDBG descriptor copying traverse rings.

## State And Persistence
`struct adapter` is the main persistent in-memory driver object for a PCI function. It owns MMIO bases, PCI/device pointers, mailbox identity, flags, hardware params, SGE queues/maps, netdev ports, CLIP/L2T/SMT tables, ULD handles, TID state, workqueues, mailbox logs, debugfs, PTP, TC offloads, HMA, SRQ, vmcore dump registration, thermal state, ethtool filters, and the ethtool dump descriptor. `struct port_info` persists per netdev port link/RSS/MAC/scheduler/mirror state.

## Dependencies And Integration Points
It integrates almost every cxgb4 source with Linux networking, PCI, interrupts, timers, PTP, crash dump, thermal, rhashtable, and Chelsio firmware/register APIs. Files in this work item use it for `struct adapter`, register helpers, mailbox helpers, CLIP table access, CUDBG collection, and queue descriptor layouts.

## Risks
Because this header is widely included, layout or prototype changes have broad blast radius. MMIO helpers assume valid mapped BARs and correct register offsets. Bit-field filter structures are host shadow copies and must not be treated as firmware layout. `struct adapter` has many cross-subsystem locks and lifecycle-owned pointers, so dumps and offload paths must respect initialization and teardown ordering.

## Test Signals
Full-driver build matrix across optional configs, sparse/lockdep for MMIO and locking use, probe/remove tests, netdev open/close, SGE queue allocation, firmware mailbox tests, offload registration, filter programming, PTP/thermal/debugfs paths, and CUDBG dump collection all exercise contracts from this header.
