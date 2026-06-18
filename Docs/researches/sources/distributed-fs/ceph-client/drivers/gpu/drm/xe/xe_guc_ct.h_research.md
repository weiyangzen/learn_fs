# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_ct.h

## Purpose

`xe_guc_ct.h` declares the public Command Transport API and small inline helpers for CT state and IRQ handling.

## Important APIs, Types, and Functions

It exposes CT init, post-hwconfig, enable/restart/disable/stop, runtime suspend/resume, send/send-recv variants, G2H-handler send, no-fail send-recv, queue processing time, snapshot capture/print/free, and immediate print. Inline helpers include `xe_guc_ct_initialized()`, `xe_guc_ct_enabled()`, `xe_guc_ct_irq_handler()`, `xe_guc_ct_send_block()`, `xe_guc_ct_send_block_no_fail()`, and `xe_guc_ct_wake_waiters()`.

## Control Flow

The IRQ helper checks that CT is enabled, wakes CT waiters, queues the G2H worker, and invokes the fast path. Send APIs are split between nonblocking events, blocking request/response, locked callers, and G2H-handler contexts.

## State and Persistence Behavior

State is stored in `struct xe_guc_ct` from `xe_guc_ct_types.h`. The inline enabled/initialized checks use `READ_ONCE()` paired with implementation `WRITE_ONCE()`.

## Dependencies and Integration Points

It includes CT types and forward-declares DRM/device objects. It is included by GuC lifecycle, ADS, capture, submission, TLB, reset, and IRQ code.

## Risks and Edge Cases

`xe_guc_ct_irq_handler()` must only be called with an initialized CT and a valid workqueue. Locked send APIs require the caller to already hold the CT mutex where documented by implementation. No-fail send is intended for reset-in-progress paths, not arbitrary commands.

## Test Signals

Compile tests catch prototype drift. Runtime tests should verify IRQ helper behavior when disabled/enabled, send-block wrappers, and state helper consistency across transitions.
