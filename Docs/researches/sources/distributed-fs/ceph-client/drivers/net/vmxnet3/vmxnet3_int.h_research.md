# sources/distributed-fs/ceph-client/drivers/net/vmxnet3/vmxnet3_int.h

## Purpose
`vmxnet3_int.h` is the internal contract shared by the vmxnet3 driver implementation files. It defines driver versioning, feature/capability constants, ring helpers, per-TX/RX queue structures, adapter-global state, register access macros, revision predicates, default sizes, and cross-file function prototypes.

## Important APIs, Types, And Functions
It defines version/revision constants, `struct vmxnet3_cmd_ring`, `struct vmxnet3_comp_ring`, TX/RX data and timestamp rings, buffer info structs, driver stats structs, `struct vmxnet3_tx_queue`, `struct vmxnet3_rx_queue`, `struct vmxnet3_intr`, and central `struct vmxnet3_adapter`. Inline helpers advance ring indices and compute descriptor availability. BAR access macros wrap MMIO reads/writes, and `VMXNET3_VERSION_GE_*` predicates gate revision-specific behavior.

## Control Flow
The header has no standalone runtime flow, but its helpers shape TX/RX descriptor ownership and ring wraparound. Queue and adapter fields are populated by probe/open paths, consumed by TX/RX/NAPI/ethtool/XDP paths, and reset during close, MTU changes, ethtool ring updates, and PM transitions.

## State And Persistence
`struct vmxnet3_adapter` persists for the netdev lifetime and owns coherent DMA pointers visible to the device. Queue structs persist across the adapter lifetime while their rings are allocated and freed around activation/configuration. Ring indices and generation bits are volatile ownership state. Feature/RSS/coalescing/WOL/capability fields persist and are re-applied after resets.

## Dependencies And Integration Points
Includes Linux networking, PCI, DMA, interrupts, VLAN, TCP/UDP/IP/IPv6, BPF, page_pool, XDP, and `vmxnet3_defs.h`. It is included by the main driver, ethtool support, and XDP support.

## Risks
Changes here can break queue ownership, DMA lifetime, feature negotiation, or ABI assumptions. The SKB/XDP union in TX buffer metadata requires correct `map_type`. Ring availability intentionally leaves one descriptor unused; changing that risks full/empty ambiguity. Revision predicates must remain aligned with hardware capabilities.

## Test Signals
Compile with and without MSI/RSS/XDP-related options and run ring wraparound, multiqueue, XDP enable/disable, ring resize, reset, and suspend/resume tests.
