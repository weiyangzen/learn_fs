# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfdk/rings.c

## Purpose
Provides NFDK-specific ring allocation, reset, debug dump, and `nfp_dp_ops` registration. It adapts common `nfp_net` ring lifecycle code to NFDK descriptor sizes and capabilities.

## Important APIs, Types, and Functions
- `nfp_nfdk_tx_ring_alloc()` allocates coherent NFDK TX descriptors and software `ktxbufs`, sets `cnt` to `dp->txd_cnt * NFDK_TX_DESC_PER_SIMPLE_PKT`, and applies XPS affinity for stack TX queues.
- `nfp_nfdk_tx_ring_reset()` walks outstanding non-XDP SKBs, unmaps head/frags, accounts for TSO extra descriptors and block padding, frees SKBs, zeroes descriptors, resets pointers, and resets the netdev TX queue.
- `nfp_nfdk_tx_ring_free()` releases `ktxbufs` and coherent descriptor memory.
- `nfp_nfdk_print_tx_descs()` emits descriptor/debug state to seq_file including host and device read/write pointer markers.
- `nfp_nfdk_ops` binds NFDK version, capability mask, DMA mask, NAPI/control poll functions, TX path, ring lifecycle callbacks, and debug printing.

## Control Flow
Common open/reconfig code calls `tx_ring_alloc` before enabling firmware and `tx_ring_reset`/`tx_ring_free` during close or failed reconfiguration. `nfp_nfdk_ops` is selected by `nfp_net_alloc()` based on the firmware datapath version and subsequently drives all datapath polymorphism.

## State and Persistence Behavior
Manages volatile ring memory, DMA addresses, descriptor counters, queue pointer mirrors, and queue accounting. It does not persist state beyond the lifetime of a vNIC open/reconfiguration cycle. Reset is designed to be idempotent after firmware disable.

## Dependencies and Integration Points
Depends on common `nfp_net` structures, `nfp_net_dp` helpers, NFDK descriptor definitions, DMA coherent allocation, seq_file debugfs output, and netdev XPS queue APIs. The capability mask intersects firmware-advertised features before common netdev feature setup.

## Risks
Reset must compute the same descriptor counts as transmit, including block padding and TSO metadata, or it can leak DMA mappings or free wrong SKBs. Empty `tx_ring_bufs_alloc/free` callbacks are intentional for NFDK but may surprise common code expecting per-buffer allocation.

## Test Signals
Open/close cycles, failed open unwinds, MTU/ring-count reconfiguration, debugfs descriptor dumps, TX timeout recovery, and ring reset with in-flight TSO/fragments are the main signals. Memory leak and DMA API debug are valuable here.
