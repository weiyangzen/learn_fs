# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/ce.h

## Purpose
`ce.h` declares Copy Engine constants, shared firmware configuration records, host ring structures, and public CE APIs. It is the compile-time contract between core/HIF/QMI/HTC/DP code and the CE implementation.

## Important APIs, Types, And Functions
Key constants include `CE_COUNT_MAX`, `CE_ATTR_BYTE_SWAP_DATA`, `CE_ATTR_DIS_INTR`, pipe direction values, CE interrupt-enable register addresses, `CE_RING_IDX_INCR()`, and `ATH11K_CE_RX_POST_RETRY_JIFFIES`. `struct service_to_pipe` and `struct ce_pipe_config` are little-endian records shared with firmware through QMI. `struct ce_attr` describes host ring sizing and callbacks. `struct ath11k_ce_ring`, `struct ath11k_ce_pipe`, and `struct ath11k_ce` hold runtime ring, pipe, and aggregate CE state. Public functions cover pipe allocation/init/free, send, RX posting, service, polling, shadow config, and attr lookup.

## Control Flow
The header supports a lifecycle where hardware params expose CE config arrays, `ath11k_ce_alloc_pipes()` creates rings from `ce_attr`, `ath11k_ce_init_pipes()` registers them with HAL, HIF code enables interrupts, CE service functions process completions, and cleanup/free functions unwind buffers and descriptor memory.

## State And Persistence
The structs define all CE in-memory state. `ath11k_ce_ring` owns descriptor memory addresses and skb tracking slots. `ath11k_ce_pipe` owns callbacks, tasklet, and per-pipe counters. `ath11k_ce` contains the global lock and per-CE shadow timers. No state is persistent across module reload or device re-probe.

## Dependencies And Integration Points
The API depends on Linux skb, DMA, spinlock, and ath11k HAL/DP types. QMI consumes `ce_pipe_config` and `service_to_pipe`; HIF code uses CE attr flags to request and mask interrupts; HTC/DP provide callbacks stored in `ce_attr`.

## Risks And Test Signals
Because firmware consumes some structures directly, field order, endian annotations, and sizes must remain stable. Ring sizes are assumed to be powers of two after allocation, so callers must not bypass rounding. Test signals include build coverage on big-endian and little-endian configs, QMI CE map validation, and ring wraparound under sustained traffic.
