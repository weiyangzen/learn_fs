# sources/distributed-fs/ceph-client/block/blk-rq-qos.h

## Purpose

`blk-rq-qos.h` declares the block request QoS framework data structures, operation table, identifiers, and fast-path wrappers. It lets policy modules plug into bio/request throttle, track, merge, issue, requeue, completion, cleanup, queue-depth-change, exit, and debugfs behavior.

## Important APIs, Types, And Functions

`enum rq_qos_id` identifies WBT, latency, and cost policies. `struct rq_wait` contains the wait queue and inflight counter used by throttlers. `struct rq_qos` is a linked-list node with ops, owning disk, id, next pointer, and optional debugfs directory. `struct rq_qos_ops` is the callback contract. `struct rq_depth` tracks adaptive depth state. Lookup helpers include `rq_qos_id()`, `wbt_rq_qos()`, and `iolat_rq_qos()`. Fast-path wrappers include `rq_qos_throttle()`, `rq_qos_track()`, `rq_qos_merge()`, `rq_qos_issue()`, `rq_qos_requeue()`, `rq_qos_done()`, `rq_qos_done_bio()`, `rq_qos_cleanup()`, and `rq_qos_queue_depth_changed()`.

## Control Flow

Callers check queue flags through the inline wrappers rather than walking policies directly. `rq_qos_throttle()` marks `BIO_QOS_THROTTLED` before invoking policy throttles, and `rq_qos_merge()` marks `BIO_QOS_MERGED`; `rq_qos_done_bio()` uses those flags to decide whether bio completion may need policy cleanup. It then revalidates that the current queue still has QoS enabled because bios can traverse stacked devices where lower and upper queues differ. Request completion skips passthrough requests for normal QoS done callbacks.

## State And Persistence Behavior

This header defines the in-memory policy chain and per-policy state hooks but does not persist anything. Bio flags are transient markers that link throttle/merge decisions to completion cleanup. Queue flag `QUEUE_FLAG_QOS_ENABLED` is the coarse fast-path gate.

## Dependencies And Integration Points

It includes kernel, block, atomic, wait queue, blk-mq, and debugfs interfaces. It is consumed by blk-mq submission/completion, WBT, latency/cost policies, sysfs, and queue-depth update code.

## Risks And Edge Cases

The main risk is stale bio flags across stacked devices; the header explicitly guards against calling into absent QoS chains on completion. Policy ordering is linked-list order, with new policies inserted by the implementation. Missing fast-path flag updates would either bypass QoS or call into an empty chain. Passthrough request filtering avoids applying filesystem I/O QoS semantics to admin commands.

## Test Signals

Compile coverage with and without debugfs/QoS policies, stacked-device tests where only one layer enables QoS, WBT sysfs changes, passthrough completions, and bio merge/throttle cleanup tests are the best indicators.
