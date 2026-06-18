# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sched/Kconfig

## Purpose

This Kconfig entry exposes `RV_MON_SCHED`, the scheduler monitor collection.

## Important APIs, Types, and Functions

It depends on `RV` and at least three per-task monitor slots through `RV_PER_TASK_MONITORS >= 3`.

## Control Flow

Selecting it builds the scheduler container, allowing child monitors such as `nrp`, `opid`, `sco`, `scpd`, `snep`, `snroc`, `sssw`, and `sts` to register beneath it.

## State and Persistence Behavior

It holds compile-time configuration only.

## Dependencies and Integration Points

It integrates with the RV hierarchy and scheduler monitor documentation.

## Risks and Edge Cases

Per-task slot pressure can hide the whole monitor collection even though several children are per-CPU or implicit monitors.

## Test Signals

Kconfig matrix tests should verify child availability only when the container and enough per-task slots are configured.
