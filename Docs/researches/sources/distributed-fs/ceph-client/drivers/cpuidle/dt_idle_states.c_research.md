<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/dt_idle_states.c -->
# sources/distributed-fs/ceph-client/drivers/cpuidle/dt_idle_states.c

## Purpose

`dt_idle_states.c` parses CPU idle-state device-tree bindings into cpuidle driver state entries. It provides a common implementation for architecture drivers that describe idle states as CPU phandles.

## Important APIs, Types, And Functions

The exported entry point is `dt_init_idle_driver()`. `init_state_node()` fills a `cpuidle_state` with the matched enter function, s2idle callback, latency, target residency, flags, name, and description. `idle_state_valid()` verifies that every CPU in the driver's cpumask references the same idle-state phandle at each index.

## Control Flow

The parser selects the first CPU in the driver cpumask, walks its indexed idle-state phandles, matches each node against the caller's `of_device_id` table, skips disabled state nodes, verifies uniformity across CPUs, and initializes `drv->states` from `start_idx`. It stops on the first missing phandle and sets `drv->state_count` to the final index.

## State And Persistence Behavior

The function writes persistent cpuidle state fields in the caller's driver. It does not retain DT node references beyond parsing. Latency comes from `wakeup-latency-us` or falls back to entry plus exit latency.

## Dependencies And Integration Points

It depends on OF CPU node helpers, cpumasks, cpuidle state flags, and firmware binding properties including `min-residency-us`, `idle-state-name`, and `local-timer-stop`.

## Risks And Test Signals

Risks include firmware phandle mismatches across CPUs, state array overflow, missing latency/residency properties, and drivers passing wrong match-data enter callbacks. Test with valid and malformed DT idle-state sets, disabled nodes, heterogeneous CPU masks, and state counts near `CPUIDLE_STATE_MAX`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/dt_idle_states.c -->
