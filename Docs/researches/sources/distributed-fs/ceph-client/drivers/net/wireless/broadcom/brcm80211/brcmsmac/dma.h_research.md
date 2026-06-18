# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/dma.h

## Purpose
`dma.h` is the public DMA interface for `brcmsmac`. It declares DMA direction constants, DMA64 register layout, TX reclaim range semantics, exported counters/state, and all packet lifecycle entry points used by the common driver while keeping private ring implementation details in `dma.c`.

## Important APIs, Types, and Functions
- `DMA_TX` and `DMA_RX` identify mapping/allocation direction.
- `struct dma32diag` documents diagnostic FIFO access registers.
- `struct dma64regs` defines the per-channel DMA64 register layout: `control`, `ptr`, `addrlow`, `addrhigh`, `status0`, and `status1`.
- `enum txd_range` controls TX reclaim: `DMA_RANGE_ALL`, `DMA_RANGE_TRANSMITTED`, and `DMA_RANGE_TRANSFERED`.
- `struct dma_pub` exposes `txavail`, `dmactrlflags`, RX counters `rxgiants`/`rxnobuf`, and TX counter `txnobuf`.
- Declared lifecycle functions include `dma_attach()`, `dma_detach()`, `dma_txinit()`, `dma_rxinit()`, `dma_txreset()`, `dma_rxreset()`, `dma_txsuspend()`, `dma_txresume()`, and `dma_txsuspended()`.
- Declared packet functions include `dma_rxfill()`, `dma_rx()`, `dma_rxreclaim()`, `dma_txfast()`, `dma_kick_tx()`, `dma_txpending()`, `dma_getnexttxp()`, `dma_txreclaim()`, and `dma_walk_packets()`.
- `dma_counterreset()` clears exported counters and `dma_getvar()` exposes selected internal variable addresses by string name.
- `dma_spin_for_len()` is a BCM47XX-specific RX workaround that waits for DMA to update the packet length field.

## Control Flow
The header describes the expected API sequence: attach a DMA object, initialize TX/RX channels, keep RX populated with `dma_rxfill()`, drain RX with `dma_rx()`, transmit with `dma_txfast()`, reclaim TX with `dma_txreclaim()` or `dma_getnexttxp()`, reset engines during down paths, reclaim buffers, and detach. The inline BCM47XX helper is called from the RX path after reading the initial length.

## State and Persistence
The header owns no state. `struct dma_pub` is embedded in the private object allocated by `dma.c`; its fields are runtime flow-control values and counters that persist only while the DMA handle exists.

## Dependencies and Integration Points
The header includes Linux delay/SKB headers and local `types.h`. It is consumed by brcmsmac common code that attaches DMA rings, sends packets, refills RX, handles interrupts, and performs reset/teardown. The BCM47XX inline depends on uncached `KSEG1ADDR()` access when that platform option is enabled.

## Risks and Edge Cases
- `struct dma_pub` is intended read-only to external users but is not type-enforced.
- The chosen `enum txd_range` matters; reclaiming all descriptors while hardware owns them can corrupt completion ownership.
- `dma_getvar()` bypasses type safety by returning an address selected by string.
- `dma_spin_for_len()` can busy-wait if hardware never writes a length.
- Locking rules are not encoded in the header and must be supplied by surrounding driver conventions.

## Test Signals
Compile all users against this header, test attach/init/fill/send/reclaim/reset/detach sequencing, exercise all TX reclaim ranges, run BCM47XX-specific RX coverage when possible, and use static analysis to catch unintended external writes to `struct dma_pub`.
