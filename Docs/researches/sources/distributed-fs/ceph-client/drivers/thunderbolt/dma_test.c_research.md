# sources/distributed-fs/ceph-client/drivers/thunderbolt/dma_test.c

## Purpose

`dma_test.c` is a Thunderbolt service driver that exposes an XDomain DMA traffic test through debugfs. It registers a `dma_test` property directory/service, binds to matching XDomain services, allocates TX/RX rings and XDomain paths on demand, sends or receives bounded 4 KiB frames, and reports packet, CRC, overflow, speed, width, and configuration errors.

## Important APIs, Types, and Functions

`struct dma_test` holds the bound service, parent XDomain, TX/RX rings and HopIDs, configured packet counts, expected link speed/width, actual packet counters, CRC/overflow counters, last result, error code, completion, lock, and debugfs directory. `struct dma_test_frame` wraps a frame buffer and `ring_frame`.

Core helpers are `dma_test_start_rings()`, `dma_test_stop_rings()`, `dma_test_free_rings()`, `dma_test_submit_rx()`, `dma_test_submit_tx()`, `dma_test_rx_callback()`, `dma_test_tx_callback()`, `dma_test_set_bonding()`, `dma_test_validate_config()`, `dma_test_check_errors()`, and `test_store()`.

Debugfs attributes expose `lanes`, `speed`, `packets_to_receive`, `packets_to_send`, `status`, and write-only `test`. Module lifecycle is handled by `dma_test_init()` and `dma_test_exit()`; service lifecycle by `dma_test_probe()` and `dma_test_remove()`.

## Control Flow

Module init allocates a 4 KiB pattern buffer, fills it with an incrementing data pattern, creates and registers the `dma_test` property directory, then registers the Thunderbolt service driver. Probe allocates private state, initializes its mutex and completion, stores drvdata, and creates debugfs files.

Writing `1` to `test` resets counters, validates that at least one direction is configured and bidirectional runs use equal packet counts, applies requested lane bonding, creates TX/RX rings, allocates XDomain HopIDs, enables paths, starts rings, submits RX buffers first, submits TX frames, waits for RX completion if needed, stops and frees rings, checks expected speed/width and counters, and stores pass/fail status.

RX callbacks unmap and free buffers, count received packets, record descriptor CRC/overflow flags, and complete the run when the expected number arrives. TX callbacks unmap and free transmitted buffers. The suspend hook relies on interruptible completion waits returning so an in-progress debugfs write can unwind and tear down rings.

## State and Persistence Behavior

Per-service state persists for the service lifetime. Test configuration and last-result counters persist until the service is removed or another run overwrites them. Rings, HopIDs, DMA mappings, and packet buffers are transient and should be fully released after each run.

No disk state is persisted. Hardware state changes include temporary XDomain DMA paths and optional lane-bonding configuration. Paths are disabled in `dma_test_stop_rings()` even when buffer submission or wait fails after ring startup.

## Dependencies and Integration Points

The file depends on Thunderbolt service registration, property directories, XDomain path allocation/enable/disable helpers, NHI ring allocation, DMA mapping APIs, completions, debugfs, module lifecycle, and service driver matching through `TB_SERVICE("dma_test", 1)`.

It integrates with `domain.c` through the Thunderbolt service bus and with the debugfs infrastructure through the service debugfs directory.

## Risks and Edge Cases

`dma_test_submit_rx()` and `dma_test_submit_tx()` return immediately on allocation or DMA mapping failure but do not clean up frames already submitted in the same loop. Later `dma_test_stop_rings()` stops rings, which should cancel queued frames and run callbacks, but this depends on ring stop semantics for partially submitted buffers.

`dma_test_submit_tx()` increments `packets_sent` before checking the return value of `tb_ring_tx()`, and it ignores any `tb_ring_tx()` failure. If TX submission can fail after ring setup, the result may misreport packets and leak the frame unless the ring takes ownership.

The generated pattern writes through a `u32 *` while incrementing a `u64` value, so the actual pattern uses truncated 32-bit values rather than full 64-bit chunks. The current driver never validates received payload contents, only packet counts and descriptor errors.

Removal deletes debugfs under the lock but does not actively stop an in-progress test outside the debugfs call path. The debugfs write holds the same lock, so removal waits, but long receive waits can delay removal until interrupt or completion.

## Test Signals

Tests should cover service registration/probe/remove, debugfs validation bounds, send-only, receive-only, and loopback send+receive runs, invalid mismatched packet counts, lane bonding enable/disable failures, speed/width mismatch reporting, RX descriptor CRC/overflow flags, interruptible wait during suspend, allocation failures after partial submissions, and repeated runs with no stale rings or HopIDs.
