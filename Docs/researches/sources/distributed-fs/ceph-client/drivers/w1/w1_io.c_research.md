# sources/distributed-fs/ceph-client/drivers/w1/w1_io.c

## Purpose
Low-level W1 I/O primitives and CRC8 implementation. It adapts optional master hardware callbacks to generic bit, byte, block, reset, search, select, resume, and strong-pullup operations.

## Important APIs, Types, and Functions
Module parameters are `delay_coef` and `disable_irqs`. Exported APIs include `w1_touch_bit()`, `w1_write_8()`, `w1_triplet()`, `w1_read_8()`, `w1_write_block()`, `w1_touch_block()`, `w1_read_block()`, `w1_reset_bus()`, `w1_calc_crc8()`, `w1_search_devices()`, `w1_reset_select_slave()`, `w1_reset_resume_command()`, and `w1_next_pullup()`.

## Control Flow
Each exported primitive prefers hardware callbacks when supplied; otherwise it bit-bangs using `write_bit`, `read_bit`, and calibrated microsecond delays. Strong pullup is staged by `w1_next_pullup()`, applied before the final write byte or block through `w1_pre_write()`, and cleared or slept in `w1_post_write()`. Search uses a hardware `search` callback if present, else calls the core `w1_search()`.

## State and Persistence
State is limited to module parameters, static CRC table, and per-master `pullup_duration` consumed as a one-shot. No persistent state.

## Dependencies and Integration Points
Depends on callbacks supplied by W1 master drivers, Linux delay/IRQ helpers, and internal core declarations. All slave drivers in this subset use these helpers for bus transactions.

## Risks and Test Signals
Timing is critical: IRQ disabling and delay coefficient can affect protocol reliability and system latency. `w1_read_block()` returns `u8`, limiting count reporting to 255 even if callers request more. `w1_reset_select_slave()` uses `SKIP_ROM` on single-slave buses, which some drivers intentionally avoid. Test bit-banged and hardware-callback masters, strong pullup sequencing, reset presence detection, ROM search triplets, CRC8 vectors, and boundary read lengths.
