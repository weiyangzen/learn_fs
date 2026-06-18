# sources/distributed-fs/ceph-client/samples/pktgen/pktgen_sample03_burst_single_flow.sh

## Purpose

This sample targets maximum single-flow transmit performance. It intentionally avoids flow randomization and instead configures pktgen burst mode so drivers can use `skb->xmit_more` style batching to reduce hardware tail pointer updates.

## Important APIs, Types, and Functions

The script relies on `pg_ctrl`, `pg_thread`, and `pg_set` from `functions.sh`. Important pktgen attributes are `burst`, `QUEUE_MAP_CPU`, `count`, `clone_skb`, `pkt_size`, `delay`, `NO_TIMESTAMP`, `dst_mac`, `dst_min/max`, optional `udp_dst_min/max`, and optional `UDPCSUM`.

## Control Flow

After parsing shared parameters, it defaults `BURST=32`, `CLONE_SKB=0`, `COUNT=0`, destination IP, and destination MAC. It resets pktgen unless appending, then configures every requested thread as `$DEV@$thread`. Each configured generator maps queues to CPU, sets packet attributes, optional UDP destination-port randomization, and writes `burst $BURST` unless `BURST=0`. Non-append mode starts pktgen and prints each thread result.

## State and Persistence Behavior

All persistent state is pktgen procfs configuration. Because `COUNT` defaults to zero, the run persists until interrupted or pgctrl is stopped. The script does not save host tuning outside pktgen.

## Dependencies and Integration Points

It depends on kernel pktgen burst support, multiqueue NIC behavior, and the receiver's ability to handle a single UDP flow. It is a performance sample rather than a protocol correctness test.

## Risks and Edge Cases

Single-flow overload may pin one receiver CPU and hide aggregate NIC capacity. `BURST=0` disables the feature being demonstrated. Infinite count plus line-rate small packets can disrupt real networks.

## Test Signals

Useful signals are pktgen `Result:` pps/throughput output, NIC queue counters, receiver CPU saturation on one flow, and comparison of `BURST=0` versus the default burst value.
