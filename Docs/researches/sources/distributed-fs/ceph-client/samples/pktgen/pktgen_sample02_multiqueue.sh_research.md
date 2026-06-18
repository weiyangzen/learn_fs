# sources/distributed-fs/ceph-client/samples/pktgen/pktgen_sample02_multiqueue.sh

## Purpose

This pktgen sample shows how to transmit from multiple pktgen kernel threads against one multiqueue device by using the `dev@thread` naming convention. It is intended for CPU-scaled transmit testing with one generator instance per selected CPU/thread.

## Important APIs, Types, and Functions

The script uses the common pktgen `functions.sh` and `parameters.sh` variables, especially `DEV`, `F_THREAD`, `L_THREAD`, and `THREADS`. It writes thread membership through `pg_thread` and generator attributes through `pg_set`. It uses `QUEUE_MAP_CPU`, `UDPSRC_RND`, optional `UDPDST_RND`, and optional `UDPCSUM`.

## Control Flow

The script defaults count, clone behavior, destination IP/MAC, and UDP source-port range, then resets pktgen unless in append mode. For every thread from `F_THREAD` to `L_THREAD`, it constructs `$DEV@$thread`, clears prior devices, adds that synthetic device to the pktgen thread, binds queue selection to CPU, and applies common packet attributes. The run phase starts pgctrl once and prints a short `Result:` block for every thread device.

## State and Persistence Behavior

Each `dev@thread` has independent pktgen device state, while the physical NIC and its queues are shared. The script rewrites thread membership unless `APPEND` is set. Runtime stats accumulate in `/proc/net/pktgen/$DEV@$thread` until reset.

## Dependencies and Integration Points

It integrates with NIC multiqueue queue selection and benefits from IRQ affinity mapping configured outside the script. It requires the pktgen procfs control plane and companion helper scripts.

## Risks and Edge Cases

Thread counts beyond available CPUs or queue count can generate misleading results. `QUEUE_MAP_CPU` only helps if queues and IRQs are aligned. Default destination MAC is only a placeholder and may black-hole traffic.

## Test Signals

Expected signals are one pktgen device per selected thread, nonzero per-thread result counters, and balanced NIC queue stats when CPU/IRQ/queue affinity is correctly configured.
