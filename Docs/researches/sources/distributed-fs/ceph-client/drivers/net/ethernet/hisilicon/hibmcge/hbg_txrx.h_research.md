
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_txrx.h

## Purpose

This header declares HIBMCGE TX/RX lifecycle and transmit functions and provides inline helpers for frame length, FIFO capacity/fullness, and software ring occupancy.

## Important APIs, Types, and Functions

- `hbg_spec_max_frame_len()` returns TX max frame length or RX buffer size according to direction.
- `hbg_get_spec_fifo_max_num()` returns TX or RX FIFO capacity from device specs.
- `hbg_fifo_is_full()` compares live hardware FIFO occupancy against capacity.
- `hbg_get_queue_used_num()` reads ring `ntu`, `ntc`, and `len` safely enough for diagnostics.
- It declares `hbg_net_start_xmit()`, `hbg_txrx_init()`, and `hbg_txrx_uninit()`.

## Control Flow

No standalone control flow exists. Inline helpers are used by TX/RX, debugfs, and netdev operations.

## State and Persistence

No state is stored here; helpers read `struct hbg_priv` and `struct hbg_ring`.

## Dependencies and Integration Points

The header depends on netdevice/etherdevice declarations and hardware FIFO helpers. It connects `hbg_main.c`, `hbg_irq.c`, and `hbg_debugfs.c` to TX/RX implementation details.

## Risks and Edge Cases

The helpers assume direction is either TX or RX; unexpected combined direction values would select RX in some ternaries. Queue occupancy returns zero when `len` is zero, which is useful for debugfs during teardown.

## Test Signals

Build coverage plus debugfs ring occupancy, TX frame length checks, and RX FIFO full behavior validate this header.
