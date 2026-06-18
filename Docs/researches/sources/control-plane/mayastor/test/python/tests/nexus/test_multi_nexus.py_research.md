# sources/control-plane/mayastor/test/python/tests/nexus/test_multi_nexus.py

## Purpose
Tests multiple simultaneous nexuses and replica behavior across all compose nodes.

## Important APIs, Types, And Functions
Fixtures create temp files, pools, multiple replicas on all nodes, nexuses, connected devices, and mounted filesystems. Tests include restart behavior and multiple raw, filesystem, and SPDK fio workloads.

## Control Flow
The setup creates one pool per node from `/tmp/<node>.img`, creates several replicas with shared UUIDs across nodes, creates nexuses over those replicas, connects NVMe devices, optionally mounts filesystems, then runs fio while containers may restart or multiple nexuses run concurrently.

## State And Persistence
State includes per-node image files, pools, replicas, nexuses, kernel NVMe devices, mounts, and fio workloads. Fixtures attempt cleanup through destroy/disconnect/unmount paths.

## Dependencies And Integration Points
Depends on `MayastorHandle`, common command/NVMe/fio/SPDK helpers, docker fixtures, asyncio, and pytest-asyncio.

## Risks
Concurrent IO and container restarts make timing and cleanup sensitive. Reusing UUID patterns across nodes requires precise teardown to avoid stale resources.

## Test Signals
Passing tests signal that multiple nexuses can coexist and survive restart/data path scenarios without corrupting IO.
