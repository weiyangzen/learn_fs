# sources/distributed-fs/ceph-client/net/sched/sch_plug.c

Purpose: implements the `plug` qdisc, which buffers packets until explicit netlink control commands release one epoch or release indefinitely. It is designed for output buffering/commit workflows such as checkpoint-based fault tolerance.

Important APIs, types, and functions: `struct plug_sched_data` stores `unplug_indefinite`, `throttled`, byte `limit`, packet counts for current and last epochs, and packets currently allowed for release. Qdisc operations are `plug_enqueue`, `plug_dequeue`, `plug_init`, and `plug_change`; reset uses `qdisc_reset_queue`.

Control flow: enqueue enforces a byte backlog limit and, while not indefinitely unplugged, increments `pkts_current_epoch` before tail enqueue. Dequeue returns `NULL` when throttled; otherwise it drains all packets in indefinite mode or decrements `pkts_to_release` for finite release mode. When the release count reaches zero, the qdisc throttles itself until another release command. `plug_change` handles `TCQ_PLUG_BUFFER`, `TCQ_PLUG_RELEASE_ONE`, `TCQ_PLUG_RELEASE_INDEFINITE`, and `TCQ_PLUG_LIMIT`.

State and persistence behavior: epoch packet counters are volatile qdisc state. `TCQ_PLUG_BUFFER` rolls current epoch count into last epoch and starts a new one; `TCQ_PLUG_RELEASE_ONE` adds last epoch packets to the releasable count; `TCQ_PLUG_RELEASE_INDEFINITE` clears epoch counters and makes the qdisc pass-through until the next buffer command. No persistent storage exists.

Dependencies and integration points: uses basic qdisc tail/head queues, netlink `tc_plug_qopt`, `netif_schedule_queue` to restart transmission after release, device MTU/tx_queue_len for default limit, and module registration as `plug`.

Risks: release accounting is packet-count based, so drops or queue purges between buffer and release can alter what is actually available. Limit changes do not proactively trim backlog. The qdisc intentionally returns `NULL` while throttled, so watchdogs or callers must rely on release commands to reschedule. Counter overflow is possible in theory for long-running unbounded epochs.

Test signals: initialize with default and explicit limits; verify initial throttling; buffer/release-one sequencing across multiple epochs; indefinite release pass-through and re-plug behavior; limit drops; queue scheduling after release commands; reset behavior; invalid action and short netlink option rejection.
