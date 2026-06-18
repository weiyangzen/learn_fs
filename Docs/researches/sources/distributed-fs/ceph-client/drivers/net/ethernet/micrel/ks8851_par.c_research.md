# sources/distributed-fs/ceph-client/drivers/net/ethernet/micrel/ks8851_par.c

## Purpose

`ks8851_par.c` is the platform/parallel-bus frontend for the KSZ8851-16MLL variant. It maps the data and command register windows, validates the hardware endian strap, provides parallel MMIO implementations of the shared KS8851 callbacks, implements a synchronous transmit path, and registers an OF-matched platform driver for `micrel,ks8851-mll`.

## Important APIs, Types, and Functions

`struct ks8851_net_par` embeds `struct ks8851_net` and adds a spinlock, data-window MMIO pointer, command-window MMIO pointer, and command-register cache. The BE0-BE3 constants encode the parallel bus byte-enable bits. `ks8851_lock_par()` and `ks8851_unlock_par()` serialize register/FIFO access with `spin_lock_bh()`. `ks_check_endian()` detects an incorrect EESK endian strap by intentionally reading `KS_CIDER` with the byte-enable pattern that reveals swapped BE semantics.

Register access is provided by `ks8851_wrreg16_par()` and `ks8851_rdreg16_par()`, which write the command window with register offset plus computed byte enables and then access the data window. FIFO operations are `ks8851_rdfifo_par()` and `ks8851_wrfifo_par()`. TX is handled by `ks8851_start_xmit_par()`. Probe/remove are `ks8851_probe_par()` and `ks8851_remove_par()`.

## Control Flow

Probe allocates a managed Ethernet device with `struct ks8851_net_par` private data, fills the common KS8851 callback table, sets the interrupt mask to link-change, RX, and RX-process-stop events, initializes the parallel spinlock, maps two platform resources for data and command windows, checks endian strap correctness, obtains the platform IRQ, and calls `ks8851_probe_common()`.

Parallel TX is synchronous in `ndo_start_xmit`. It locks the bus, reads free TX memory from `KS_TXMIR`, and if enough space exists writes RXQCR with `RXQCR_SDA`, writes the FIFO header and aligned skb data, restores RXQCR, triggers enqueue with `TXQCR_METFE`, and polls `TXQCR_METFE` clear with `readx_poll_timeout_atomic()`. On success or timeout it currently calls `ks8851_done_tx()` in the enough-space branch, then unlocks. If space is insufficient, it returns `NETDEV_TX_BUSY`.

RX FIFO reads are invoked by common IRQ processing. The parallel callback uses `ioread16_rep()` from the data window into the caller buffer offset by one 16-bit word, matching the common layer's expectation that status/garbage bytes precede the Ethernet header in the destination.

## State and Persistence Behavior

Parallel-specific state is limited to MMIO mappings, the command cache, and the access lock. There is no deferred TX work and no bus-specific persistent configuration beyond the callback table and interrupt mask. The common layer owns power, MAC, RX filter, MDIO, and EEPROM state. `cmd_reg_cache` records the most recent computed command word but is not used as a coherency guard.

## Dependencies and Integration Points

The file integrates with the platform bus, OF matching, managed resource allocation, MMIO accessors, `readx_poll_timeout_atomic()`, and `ks8851_common.c`. It relies on two memory resources: one for the data register and one for the command register. It shares PM callbacks through `ks8851_pm_ops` and exposes a `message` module parameter for netif debug verbosity.

## Risks

Because TX is done inline while holding a bottom-half-disabled spinlock, long polling or slow MMIO can increase latency. `ks8851_start_xmit_par()` frees the skb even when the TXQCR poll times out after FIFO write, while returning `NETDEV_TX_BUSY`; that return convention can be risky because the networking stack may interpret BUSY as not consumed. FIFO writes use `ALIGN(txp->len, 4)` and 16-bit repeated writes from skb data, so unaligned or short-tail handling depends on skb data layout and hardware tolerance. The endian strap check is critical; without it, all register access can silently address wrong byte lanes.

## Test Signals

Test with device-tree compatible `micrel,ks8851-mll`, two valid MMIO resources, correct and intentionally incorrect endian strap configurations, open/close through common code, TX under full and low FIFO space, TXQCR poll timeout behavior, RX FIFO delivery, interrupt handling without TX interrupt support, suspend/resume, and platform remove. Build coverage should ensure the shared callbacks match `ks8851.h`.
