# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_ct.c

## Purpose

`xe_guc_ct.c` implements the GuC Command Transport layer: bidirectional circular CT buffers, CTB registration, H2G send paths, blocking send/receive fences, G2H event parsing/dispatch, flow-control credit accounting, safe-mode polling, fast IRQ handling for critical messages, runtime state transitions, snapshots, and debug dead-CT capture.

## Important APIs, Types, and Functions

- Init/lifecycle: `xe_guc_ct_init_noalloc()`, `xe_guc_ct_init()`, `xe_guc_ct_init_post_hwconfig()`, `xe_guc_ct_enable()`, `xe_guc_ct_restart()`, `xe_guc_ct_disable()`, `xe_guc_ct_stop()`, runtime suspend/resume, and flush/stop.
- Sends: `xe_guc_ct_send()`, `xe_guc_ct_send_locked()`, `xe_guc_ct_send_g2h_handler()`, `xe_guc_ct_send_recv()`, and `xe_guc_ct_send_recv_no_fail()`.
- Receive/dispatch: `xe_guc_ct_fast_path()`, `receive_g2h()`, `dequeue_one_g2h()`, `parse_g2h_msg()`, `process_g2h_msg()`, and action-specific handler calls.
- Diagnostics: `xe_guc_ct_snapshot_capture()`, `xe_guc_ct_snapshot_print()`, `xe_guc_ct_snapshot_free()`, `xe_guc_ct_print()`, and debug-only `ct_dead_*` capture.

## Control Flow

Noalloc init sets locks, xarray, waitqueues, and workers. Alloc init creates pinned mapped H2G/G2H BOs. Enabling zeroes CTBs, initializes descriptors, self-configures descriptor/buffer addresses and sizes through MMIO, sends CT enable, marks state enabled, wakes waiters, and starts safe-mode polling when MSI is absent. H2G send reserves H2G and optional G2H credits, writes CT and HXG headers plus payload into the circular buffer, updates tail, and rings GuC. Blocking send stores a stack fence in an xarray by sequence number and waits for a matching G2H response. IRQ/workqueue receive reads complete G2H messages, validates origin/type, releases credits, wakes fences, and dispatches events to submission, page fault, TLB invalidation, page reclaim, relay, SR-IOV, capture, crash, and test handlers.

## State and Persistence Behavior

Persistent CT state includes two CTBs, a mutex for send/dequeue serialization, a fast spinlock for G2H credits and IRQ fast path, fence sequence/xarray, outstanding G2H credit count, waitqueues, workers, and state enum. State transitions cancel all in-flight fences and reset credit accounting. Debug builds also maintain dead-CT snapshots and a ring of fast-request fence origins.

## Dependencies and Integration Points

The CT layer integrates GuC ABI headers, BO mapping, MMIO self-config through `xe_guc_self_cfg*`, runtime PM, GT reset, submission, pagefault/TLB/page-reclaim handlers, relay, SR-IOV PF monitor/control, GuC log/capture, tracepoints, fault injection, and devcoredump snapshot printing.

## Risks and Edge Cases

Credit accounting must stay exact or CT deadlocks. H2G wrap writes NOPs and retries, which depends on space recalculation. Blocking sends use stack fences and require xarray erase plus mutex serialization to avoid UAF after timeout. Fast-request failures cannot be returned to senders and escalate to reset. Safe-mode polling must not race with normal IRQ handling. Runtime PM receive paths intentionally avoid waking a suspended device, so unsolicited events around suspend may be dropped.

## Test Signals

Tests should cover CTB init/register, H2G wrap, H2G/G2H room accounting, blocking response success/failure/retry/timeout/cancel, state transitions canceling fences, invalid descriptor status/head/tail handling, fast-path pagefault/TLB/page-reclaim dispatch, safe-mode polling, runtime suspend/resume invariants, snapshot printing, and debug dead-CT capture. Fault injection hooks cover init and send/receive functions.
