# sources/distributed-fs/ceph-client/drivers/net/ethernet/sun/sunqe.h

## Purpose
`sunqe.h` is the hardware map and private-state definition header for the Sun QuadEthernet SBUS driver. It describes QEC global registers, per-channel QEC registers, AMD 79C940 MACE registers, descriptor layouts, fixed ring/buffer geometry, and the parent/child state objects used by `sunqe.c`.

## Important APIs, Types, And Constants
- QEC global register offsets and masks: `GLOB_*`, `GLOB_CTRL_*`, `GLOB_STAT_*`, packet/local-memory sizing fields, and `GLOB_STAT_PER_QE()`.
- Per-channel QEC fields: `CREG_*`, control bits, status/error masks, QEC error masks, MACE error masks, and inter-frame-gap controls.
- MACE register offsets and bit masks: `MREGS_*`, including TX/RX frame controls/status, interrupt masks, BIU/FIFO/MAC/PLS/PHY config, internal address config, filter, counters, and test bits.
- Descriptor types `struct qe_rxd` and `struct qe_txd` plus `RXD_*` and `TXD_*` ownership, update, SOP/EOP, and length masks.
- Ring and buffer geometry: active 16-entry rings in 256-entry descriptor arrays, `NEXT_*` and `PREV_*` wrap over max-size descriptors, `TX_BUFFS_AVAIL`, `PKT_BUF_SZ`, `RXD_PKT_SZ`, `struct qe_init_block`, and `struct sunqe_buffers`.
- State containers: `struct sunqec` for a global QEC and `struct sunqe` for one channel/netdev.

## Control Flow And State Behavior
This header encodes the two-level hardware model. `struct sunqec` represents the parent QEC and points to four `struct sunqe` channels. Each child has its own QEC channel registers, MACE registers, coherent descriptor block, coherent packet buffers, and RX/TX cursors. RX descriptors are preposted with `RXD_OWN`; TX descriptors are populated on demand and reclaimed lazily. The QEC local memory layout is computed in the C file from global memory-size registers and channel numbers.

## Dependencies And Integration Points
The header is consumed by `sunqe.c` and assumes SBUS-style register access and DMA-visible 32-bit addresses. It integrates with Linux netdev state through the `struct net_device *` member, with platform/OF through `struct platform_device *`, and with the parent QEC interrupt fan-out through the `qes[4]` array.

## Risks And Edge Cases
- `NEXT_RX()` and `NEXT_TX()` wrap over `*_RING_MAXSIZE` rather than active ring size; this supports delayed descriptor reposting but requires careful masking when indexing the fixed packet buffers.
- Packet buffers are fixed-size arrays; MTU assumptions must match `PKT_BUF_SZ` and `TXD_LENGTH`/`RXD_LENGTH` limits.
- Register masks are dense and hardware-specific; incorrect masks can disable interrupts or miss fatal DMA errors.
- Parent/child pointers have no reference counting in the structures themselves, relying on platform-driver and module ordering.

## Test Signals
Build coverage should compile the header with `sunqe.c` on SPARC. Runtime signals include correct QEC global mode detection, channel number assignment, ring cursor wrap through 256 descriptors, multicast hash programming, MACE link status reads, and per-channel stats updates under shared IRQ load.
