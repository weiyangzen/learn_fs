# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/health.h

## Purpose

`en/health.h` declares common mlx5e health reporter types, CQ/EQ diagnostic helpers, TX/RX reporter entry points, channel recovery helpers, resource dump helpers, and CQE syndrome recovery policy.

## Important APIs, Types, and Functions

- `cqe_syndrome_needs_recover()` returns true for local QP operation error, local protection error, and work request flush error syndromes.
- TX reporter declarations cover create/destroy, TX error CQE, TX timeout, and PTP SQ unhealthy reporting.
- RX reporter declarations cover create/destroy, ICOSQ/RQ CQE errors, RX timeout, and ICOSQ recovery suspend/resume.
- `struct mlx5e_err_ctx` packages recover and dump callbacks plus context for devlink health reports.
- Common helpers cover SQ-to-ready, EQ recovery, channel recovery, health report dispatch, reporter lifecycle, channel state update, resource dump fmsg streaming, and queue dump.

## Control Flow

Reporter implementations include this header to construct `mlx5e_err_ctx`, decide whether CQE syndromes are recoverable, call common diagnostic fmsg helpers, and invoke shared recovery/report routines.

## State and Persistence Behavior

Implementations mutate reporter state, queue state, channel state, and resource dump outputs. The header itself stores no state.

## Dependencies and Integration Points

Depends on `en.h` and `diag/rsc_dump.h`. It ties mlx5e TX/RX reporters, devlink health, resource dump support, and channel recovery together.

## Risks and Edge Cases

- `cqe_syndrome_needs_recover()` is a policy boundary; adding/removing syndromes changes automatic recovery behavior.
- `mlx5e_err_ctx` callbacks must remain valid until devlink health report handling completes.
- Reporter create/destroy order should match implementation dependencies: create TX then RX, destroy RX then TX.

## Test Signals

Compile TX/RX reporter implementations. Exercise recoverable and non-recoverable CQE syndromes, devlink health report/dump callbacks, queue dumps, and reporter lifecycle during netdev open/close and driver reload.
