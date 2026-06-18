# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a6xx_hfi.c

## Purpose

`a6xx_hfi.c` implements the host-to-GMU HFI command protocol used by A6xx, A7xx-adjacent, and A8xx Adreno GMU firmware paths. It owns shared HFI queue initialization, circular queue reads/writes, blocking command/ack sequencing, target-specific performance and bandwidth table construction, firmware feature enablement, frequency/bandwidth votes, and slumber preparation.

## Important APIs, Types, And Functions

The public entry points are `a6xx_hfi_init()`, `a6xx_hfi_start()`, `a6xx_hfi_stop()`, `a6xx_hfi_set_freq()`, and `a6xx_hfi_send_prep_slumber()`, declared via `a6xx_gmu.h`. Core transport helpers are `a6xx_hfi_queue_read()`, `a6xx_hfi_queue_write()`, `a6xx_hfi_wait_for_msg_interrupt()`, `a6xx_hfi_wait_for_ack()`, and `a6xx_hfi_send_msg()`. Message helpers include GMU init/version, perf table, BW table, ACD, IFPC, core firmware start, start, test, frequency vote, and prepare-slumber commands.

The file relies heavily on packed message structs from `a6xx_hfi.h`, GMU state in `struct a6xx_gmu`, target classification helpers such as `adreno_is_a8xx()`, `adreno_is_a619()`, `adreno_is_a740_family()`, and register accessors `gmu_read/write`, `gmu_poll_timeout`, and `gmu_write()`.

## Control Flow

Queue initialization in `a6xx_hfi_init()` lays out the queue table at the front of `gmu->hfi`, followed by queue headers and three 4 KiB data rings: command, response, and debug. `a6xx_hfi_queue_init()` sets shared header metadata, initializes the spinlock and sequence number, records queue IOVA, and clears history.

Command flow starts in `a6xx_hfi_send_msg()`: a sequence number is atomically allocated, the first dword is overwritten with an HFI header, the command is written into the command ring, and the function waits for a response with the same sequence number. `a6xx_hfi_queue_write()` validates circular-buffer free space, stores packet dwords, pads non-legacy queues to 4-dword alignment, performs `dma_mb()`, publishes `write_index`, and raises `REG_A6XX_GMU_HOST2GMU_INTR_SET`. Response flow waits for `GMU2HOST_INTR_INFO_MSGQ`, clears the interrupt, drains the response queue, skips firmware error records and unrelated sequence numbers, and returns optional payload data.

Startup splits on `gmu->legacy`. Legacy `a6xx_hfi_start_v1()` sends GMU init, FW version exchange, v1 perf table, BW table, then a test/end marker. Modern `a6xx_hfi_start()` sends perf and BW tables, enables ACD and IFPC when configured, starts core firmware, and then sends the generic start message.

Performance table generation is target dependent. Classic A6xx fills fixed HFI message structs from `gmu->gx_arc_votes`, `cx_arc_votes`, `gpu_freqs`, and `gmu_freqs`. A8xx uses `HFI_H2F_MSG_TABLE` with variable-length `struct a6xx_hfi_table`, including GX ARC, dependency ARC, and GPU frequency columns plus CX votes. Bandwidth table generation either consumes catalog BCM names through command DB/TCS helpers when available or selects one of the hard-coded target tables for A618, A619, A640, A650, A660, A663, A690, 7c3, A730, A740, and generic A6xx.

## State And Persistence Behavior

Persistent runtime state lives in `gmu->queues[]`, shared queue headers/data inside the mapped HFI BO, `gmu->bw_table`, `gmu->acd_table`, frequency/vote arrays, and queue history buffers. Queue read/write indexes are shared with firmware and protected by memory barriers. Command writes are serialized with `queue->lock`; response reads are not spinlocked and rely on host-side single-reader behavior plus firmware producer semantics. `gmu->bw_table` is lazily allocated with `devm_kzalloc()` and reused across sends until device teardown.

## Dependencies And Integration Points

This code integrates with GMU boot/resume in `a6xx_gmu.c`, which allocates HFI memory, programs queue table registers, enables HFI interrupts, and calls `a6xx_hfi_start()`. GPU frequency changes call `a6xx_hfi_set_freq()`. Runtime suspend/slumber calls `a6xx_hfi_send_prep_slumber()`. Crash dump code consumes `queue->history` to decode recent HFI traffic. The code depends on Qualcomm command DB names and TCS/BCM encoding when catalog BCM tables are present.

## Risks

The response read path uses `BUG_ON(HFI_HEADER_SIZE(hdr) > dwords)`, intentionally crashing on impossible firmware/memory corruption. `a8xx_hfi_send_perf_table()` does not check `kzalloc()` failure before dereferencing `tbl`, which is a real allocation-failure risk. Message name logging indexes `a6xx_hfi_msg_id[id]`; new IDs must be added to the name table or error paths can access unset entries. Bandwidth tables are hardware-specific magic values; wrong addresses or wait masks can prevent boot, DVFS, or low-power entry. The blocking wait path loops around GPU coredump completion, so fault recovery and HFI waits are coupled.

## Test Signals

Useful signals are successful GMU boot/resume, no HFI timeout logs, no response queue empty errors, correct GPU frequency/bandwidth transitions, IFPC/ACD enablement on configured devices, and clean `a6xx_hfi_stop()` without non-empty queue warnings. Hardware tests should cover legacy and modern GMUs, A8xx variable perf tables, command DB generated BW tables, and every hard-coded target BW fallback.
