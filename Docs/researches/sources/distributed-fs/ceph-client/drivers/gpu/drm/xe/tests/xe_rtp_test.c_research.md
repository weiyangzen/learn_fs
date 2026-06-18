# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_rtp_test.c

## Purpose

`xe_rtp_test.c` tests Xe RTP rule processing and conversion to save/restore register entries. It covers rule matching, OR semantics, active tracking, action coalescing, field set/clear handling, duplicate/conflict detection, and regular versus MCR/masked register conflicts.

## Important APIs, Types, and Functions

- Test case types: `struct rtp_to_sr_test_case` and `struct rtp_test_case`.
- Match callbacks: `match_yes` and `match_no`.
- Case arrays: `rtp_to_sr_cases` and `rtp_cases`.
- Test functions: `xe_rtp_process_to_sr_tests` and `xe_rtp_process_tests`.
- Init/exit: `xe_rtp_test_init` and `xe_rtp_test_exit`.
- Suite: `xe_rtp_test_suite`.

## Control Flow

Initialization builds an empty fake Xe device. For RTP-to-SR cases, the test initializes a register save/restore table, enables active tracking, calls `xe_rtp_process_to_sr`, iterates the xarray of SR entries, and compares active bitmap, entry count, set/clear bits, register raw value, and error count. For pure RTP cases, the test calls `xe_rtp_process` and checks the active bitmap for named and OR-combined rule groups.

## State and Persistence Behavior

The test mutates a fake GT's `reg_sr` xarray and error count and local active bitmaps. KUnit exit frees the DRM helper device. No live hardware is touched.

## Dependencies and Integration Points

It depends on fake device helpers, `xe_reg_defs.h`, RTP macros, register save/restore infrastructure, xarray iteration, and KUnit parameter generation. It guards workaround and tuning pipelines that translate RTP entries into register programming.

## Risks and Edge Cases

- `XE_REG_MCR` is temporarily redefined to regular `XE_REG(..., .mcr = 1)` so the test can compare raw metadata; that is intentional but sensitive to macro changes.
- Active tracking uses entry count; adding entries without expected bitmap updates causes failures.
- Conflict tests encode current policy for duplicate/not-disjoint/register-type errors.

## Test Signals

Passing tests indicate RTP rules match as expected, OR syntax is validated, active tracking is correct, same-register actions coalesce safely, field masks produce expected clear/set bits, and conflicts increment SR errors without corrupting accepted entries.
