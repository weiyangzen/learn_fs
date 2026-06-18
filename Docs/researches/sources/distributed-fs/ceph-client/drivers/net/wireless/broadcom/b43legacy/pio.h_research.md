# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/pio.h

## Purpose
Declares b43legacy PIO register offsets, control bits, queue limits, queue/packet data structures, inline MMIO helpers, and PIO API entry points. It also provides no-op inline stubs when `CONFIG_B43LEGACY_PIO` is disabled.

## Important APIs, Types, and Functions
Defines `struct b43legacy_pio_txpacket` and `struct b43legacy_pioqueue`, plus `pio_txpacket_getindex()`, `b43legacy_pio_read()`, and `b43legacy_pio_write()`. Constants include TX/RX control/data offsets, `B43legacy_PIO_TXCTL_*`, `B43legacy_PIO_RXCTL_*`, `B43legacy_PIO_MAXTXDEVQPACKETS`, `B43legacy_PIO_TXQADJUST`, and `B43legacy_PIO_MAXTXPACKETS`.

## Control Flow, State, and Persistence
The header itself does not execute. It describes runtime queue state that persists while a wireless device is active: MMIO base, device FIFO size/usage, free/queued/running lists, tasklet, and descriptor cache.

## Dependencies and Integration Points
Includes b43legacy core definitions, Linux interrupt/list/skbuff headers, and references `struct b43legacy_txstatus`. It is consumed by PIO implementation and higher-level TX paths that need conditional PIO support.

## Risks and Test Signals
Compile-time risks are mismatched stubs when PIO is disabled and structure drift from `pio.c`. Runtime risks follow from queue constants and register bit definitions. Test build permutations with and without `CONFIG_B43LEGACY_PIO`, plus PIO TX/RX traffic if enabled.
