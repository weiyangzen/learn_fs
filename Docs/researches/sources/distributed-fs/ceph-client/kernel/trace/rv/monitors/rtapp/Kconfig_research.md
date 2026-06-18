# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/rtapp/Kconfig

## Purpose

This Kconfig entry exposes `RV_MON_RTAPP`, the container for monitors that detect real-time application latency hazards.

## Important APIs, Types, and Functions

It depends on `RV` and at least two per-task monitor slots through `RV_PER_TASK_MONITORS >= 2`.

## Control Flow

When selected, the container monitor is built and child monitors such as `pagefault` and `sleep` can register beneath it.

## State and Persistence Behavior

It is a compile-time container selector only.

## Dependencies and Integration Points

It integrates with per-task LTL monitor slot accounting and the RV monitor hierarchy.

## Risks and Edge Cases

Insufficient per-task monitor slots prevent this collection from being available, even if individual monitor logic compiles.

## Test Signals

Kconfig tests should vary `RV_PER_TASK_MONITORS` and verify child monitors register under `rtapp`.
