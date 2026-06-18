# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mmio.c

## Purpose
MMIO bus backend for mt76 devices. It implements register read/write/read-modify-write, copy helpers, register-pair helpers, IRQ-mask synchronization, and bus initialization for memory-mapped chipsets.

## Important APIs, Types, And Functions
- `mt76_mmio_rr()`, `mt76_mmio_wr()`, and `mt76_mmio_rmw()` perform traced `readl`/`writel` accesses through `dev->mmio.regs`.
- `mt76_mmio_write_copy()` and `mt76_mmio_read_copy()` transfer little-endian 32-bit words to/from MMIO windows with aligned length.
- `mt76_mmio_wr_rp()` and `mt76_mmio_rd_rp()` write/read arrays of `struct mt76_reg_pair`.
- `mt76_set_irq_mask()` updates `dev->mmio.irqmask` under `irq_lock` and writes either WED IRQ mask or the provided device register.
- `mt76_mmio_init()` installs the static `MT76_BUS_MMIO` ops table, stores the base pointer, and initializes IRQ locking.

## Control Flow
Chip probe maps registers, allocates `struct mt76_dev`, then calls `mt76_mmio_init()`. Thereafter generic macros route through `dev->bus`. IRQ mask callers specify bits to clear/set; the helper updates the cached mask and immediately pushes it to hardware when an address is supplied.

## State And Persistence
State is the MMIO base pointer, bus ops pointer, IRQ spinlock, and cached IRQ mask. Hardware registers persist only as device runtime state.

## Dependencies And Integration Points
Depends on Linux I/O accessors, mt76 tracing, WED offload helpers, and `struct mt76_bus_ops`. Chip drivers may wrap these ops for address remapping, as mt7603 does.

## Risks
The copy helpers round length up to 4 bytes and assume the backing buffer is safe for rounded access. IRQ-mask updates must be the only writer of `dev->mmio.irqmask` to avoid lost bits. WED-active devices bypass direct register writes, so offload mask state must remain synchronized.

## Test Signals
Trace register access during probe, verify IRQ enable/disable paths, ensure WED and non-WED IRQ masks behave identically, and run suspend/remove paths under interrupt load to catch stale mask or register-base use.
