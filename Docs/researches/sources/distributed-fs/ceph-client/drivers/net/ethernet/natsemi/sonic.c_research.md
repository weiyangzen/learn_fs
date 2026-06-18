# sources/distributed-fs/ceph-client/drivers/net/ethernet/natsemi/sonic.c

## Purpose
`sonic.c` is the shared DP83932/DP83934 SONIC Ethernet controller implementation included by machine-specific wrappers such as `macsonic.c` and `xtsonic.c`. It owns descriptor allocation layout, open/close, TX, interrupt handling, RX buffer turnover, multicast CAM programming, statistics, timeout recovery, and controller initialization, while wrappers provide register access macros and probe/remove logic.

## Important APIs, types, and functions
The file operates on `struct sonic_local` from `sonic.h`. Key functions are `sonic_msg_init()`, `sonic_alloc_descriptors()`, `sonic_open()`, `sonic_close()`, `sonic_tx_timeout()`, `sonic_send_packet()`, `sonic_interrupt()`, `sonic_rx()`, `sonic_get_stats()`, `sonic_multicast_list()`, and `sonic_init()`. It uses wrapper-provided `SONIC_READ()`/`SONIC_WRITE()` and inline descriptor accessors from `sonic.h`.

## Control flow
Wrapper probe allocates a netdev and calls `sonic_alloc_descriptors()`. Open allocates and DMA maps receive SKBs, then calls `sonic_init()`, which resets the controller, initializes RRA/RDA/TDA/CAM areas, loads resource pointers, loads CAM, enables interrupts, and starts RX. TX pads short packets, maps the SKB, appends a descriptor after `eol_tx`, clears the previous EOL, issues `SONIC_CR_TXP`, and stops the netdev queue if the ring becomes full. Interrupt handling loops over masked status bits, acknowledges them, calls `sonic_rx()` for packets, reaps completed TX descriptors, updates error counters, restarts aborted TX when appropriate, and disables interrupts on bus retry. RX hands completed buffers to the stack, allocates replacement buffers, updates the receive resource area, advances descriptor EOL, and clears RBE when safe.

## State and persistence
Runtime state lives in `struct sonic_local`: coherent descriptor page subdivisions, logical DMA addresses, RX/TX SKB arrays, ring indices, `eol_rx`, `eol_tx`, stats, message mask, and lock. Hardware state includes CAM entries, tally counters, command/status registers, and receive resource pointers. No state persists beyond driver lifetime except hardware/firmware-provided MAC setup done by wrappers.

## Dependencies and integration points
The shared core depends on `sonic.h` constants, descriptor helpers, netdevice APIs, DMA mapping APIs, SKB allocation, interrupt context semantics, and wrapper-provided register access. It integrates with the networking stack through wrapper `net_device_ops`.

## Risks and edge cases
This file is included into wrapper translation units, so macro definitions and local variable assumptions are part of the ABI. SONIC descriptors and buffers must remain within addressing constraints described in `sonic.h`; descriptor EOL manipulation is central to both RX and TX correctness. TX and interrupt paths share descriptor state and rely on `lp->lock`. Multicast CAM loading must not overlap with TXP, so it quiesces TX first. Timeout recovery resets hardware and drops pending TX SKBs rather than resending. RX replacement allocation failure reuses the old buffer and increments drops, which avoids starving the RRA but may hide memory pressure.

## Test signals
Tests should exercise wrapper-driven open/close, RX buffer replacement, TX ring full stop/wake, TX timeout recovery, multicast list changes with small and all-multicast sets, promisc mode, stats counter rollover, bus retry interrupt handling, DMA mapping failure paths, and both 16-bit and 32-bit descriptor modes. Because this file is included by wrappers, build coverage must include each wrapper target rather than compiling `sonic.c` alone.
