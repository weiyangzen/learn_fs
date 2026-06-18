
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_diagnose.c

## Purpose

This file implements a driver-to-BMC diagnostic push channel. When firmware requests data, the driver pushes IRQ counters, link status, and selected software/hardware statistics through message registers.

## Important APIs, Types, and Functions

- `struct hbg_diagnose_message` is the temporary message container with opcode, status, data count, device pointer, and up to 64 `u32` data words.
- `hbg_push_irq_list` and `hbg_push_stats_list` map stable numeric IDs to IRQ masks and `struct hbg_stats` offsets.
- `hbg_push_msg_send()` writes message data registers, formats the header, starts the push, and polls until hardware clears the status bit.
- `hbg_push_data()` and `hbg_push_data_u64()` chunk arbitrary `u32`/`u64` arrays into the 64-word payload limit.
- `hbg_diagnose_message_push()` is the public service-task entry point.

## Control Flow

The service task calls `hbg_diagnose_message_push()`. It exits during reset or unless `HBG_REG_PUSH_REQ_ADDR` equals 1. It then pushes IRQ counts, link status, and stats in order. Any failure logs an error and skips to completion. Completion always clears the push request register.

## State and Persistence

The file reads persistent counters from `priv->vectors.stats_array` and `priv->stats`; it does not own long-lived state. Message payload buffers are allocated transiently with `kcalloc()`. Hardware message registers hold the in-flight payload and response code.

## Dependencies and Integration Points

It depends on hardware register access helpers, `hbg_ethtool.h` stats-offset macros, PHY link state, IRQ metadata, and the periodic service task in `hbg_main.c`.

## Risks and Edge Cases

`hbg_push_msg_send()` ignores the return value of `readl_poll_timeout()` and derives the return from the response-code field, so a timeout is only visible if the register retains the initialized response code. `hbg_push_link_status()` dereferences `priv->mac.phydev`, so diagnostics require successful PHY/fixed-PHY init. Stats list IDs must stay synchronized with the BMC consumer. The u64-to-u32 cast assumes endianness and word order agreed with firmware/BMC.

## Test Signals

Signals include BMC-triggered push request clearing, successful IRQ/link/stats messages, timeout/error logging on unresponsive hardware, correct ID/value pairs in the BMC receiver, and no pushes while reset is active.
