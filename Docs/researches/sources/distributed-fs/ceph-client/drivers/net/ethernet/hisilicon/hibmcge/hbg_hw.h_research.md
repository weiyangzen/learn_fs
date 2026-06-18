
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_hw.h

## Purpose

This header provides inline HIBMCGE MMIO accessors, bitfield update helpers, and declarations for hardware programming functions.

## Important APIs, Types, and Functions

- `hbg_reg_read()`, `hbg_reg_write()`, `hbg_reg_read64()`, and `hbg_reg_write64()` wrap 32-bit MMIO and lo-hi non-atomic 64-bit MMIO.
- `hbg_reg_read_field()`, `hbg_field_modify()`, and `hbg_reg_write_field()` wrap `FIELD_GET()`/`FIELD_PREP()` register bitfield access.
- Function declarations cover event notify, init, link adjustment, IRQ control, MTU/MAC/filter/pause setup, FIFO occupancy, TX descriptor write, and RX buffer fill.

## Control Flow

The header has no standalone control flow, but `hbg_reg_write_field()` performs a read-modify-write sequence at call sites.

## State and Persistence

No state is stored here. The helpers access persistent device registers through `priv->io_base`.

## Dependencies and Integration Points

It depends on `<linux/bitfield.h>` and `<linux/io-64-nonatomic-lo-hi.h>` and is included by most HIBMCGE modules that touch hardware registers.

## Risks and Edge Cases

Read-modify-write helpers are not locked, so concurrent writers to the same register can lose bits. Non-atomic 64-bit accesses assume the hardware supports lo-hi ordering. Callers must pass masks compatible with `FIELD_PREP()`, including single-bit masks.

## Test Signals

Compile coverage and register-level behavior through hardware init, IRQ operations, MAC filter updates, pause settings, and link changes validate this header.
