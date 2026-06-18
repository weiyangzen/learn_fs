# Research: sources/cloud-native/buildkit/executor/resources/monitor_linux.go

## Purpose
Linux entry point for resource monitor creation.

## Important APIs, Types, and Functions
Build-tag platform glue for real cgroup/proc monitoring.

## Control Flow
Routes monitor creation to the Linux implementation.

## State and Persistence
State is defined in `monitor.go`.

## Dependencies and Integration Points
Depends on Linux build tags and cgroup availability. Used by executors that enable resource collection.

## Risks and Edge Cases
Non-cgroup-v2 hosts degrade to no-op recorders.

## Test Signals
Build/resource integration tests.
