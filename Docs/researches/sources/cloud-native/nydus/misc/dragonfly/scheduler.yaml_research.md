<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/misc/dragonfly/scheduler.yaml -->
# sources/cloud-native/nydus/misc/dragonfly/scheduler.yaml

## Purpose

This YAML configures a minimal local Dragonfly Scheduler for E2E testing.

## Important APIs, Types, and Functions

It sets server port 8002, log/cache directories, default scheduling algorithm, retry limits and intervals, Redis DBs, manager address/cluster ID, keepalive interval, empty seed peer config, and console mode.

## Control Flow

The scheduler starts on port 8002, connects to Redis and Manager, and coordinates peer scheduling for dfdaemon/SDK clients.

## State and Persistence Behavior

Logs/cache live under `/tmp/dragonfly`. Scheduling state uses local Redis DBs 1 and 2.

## Dependencies and Integration Points

It pairs with `manager.yaml`, `dfdaemon.yaml`, and nydusd SDK configs that reference `http://127.0.0.1:8002`.

## Risks and Test Signals

The fixture assumes local Redis and Manager availability. Static ports and tmp paths are suitable for isolated tests but can conflict on shared hosts.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/misc/dragonfly/scheduler.yaml -->
