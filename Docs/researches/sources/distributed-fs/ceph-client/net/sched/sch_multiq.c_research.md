# sources/distributed-fs/ceph-client/net/sched/sch_multiq.c

Purpose: implements the legacy `multiq` qdisc, a classful scheduler that maps packets to child bands based on `skb_get_queue_mapping()` and services bands round-robin while avoiding stopped hardware TX queues.

Important APIs, types, and functions: `struct multiq_sched_data` stores active band count, max bands, current round-robin band, root filter block/list, and an array of child qdiscs. Main functions are `multiq_classify`, `multiq_enqueue`, `multiq_dequeue`, `multiq_peek`, `multiq_tune`, `multiq_init`, `multiq_graft`, class dump/stat helpers, and `multiq_tcf_block`.

Control flow: enqueue runs root filters for actions only, then chooses the band from `skb_get_queue_mapping`; out-of-range mappings fall back to band 0. The selected child receives the skb, and root qlen increments only on success. Dequeue cycles from the last served band, skips stopped TX queues using `netif_xmit_stopped`, and dequeues the first available child packet. Tune sets `bands` to `real_num_tx_queues`, purges and removes children above the new band count, and creates default pfifo children for active bands that are still noop.

State and persistence behavior: runtime state consists of the child qdisc array and `curband`. `max_bands` follows `num_tx_queues`; `bands` follows `real_num_tx_queues`. Reset clears children and resets `curband`. No persistent storage exists; netlink dump emits bands and max bands.

Dependencies and integration points: depends on multiqueue netdev state, packet classifier blocks, child qdisc replacement, qdisc hash registration, and pfifo defaults. Unlike root `mq`, this qdisc is a normal enqueue/dequeue scheduler with one device queue as its parent qdisc queue.

Risks: tune allocation uses `q->max_bands - qopt->bands`, so assumptions about `real_num_tx_queues <= num_tx_queues` are important. Class/graft operations assume valid class indices returned by `multiq_find`. Filters do not choose a class; they only permit action handling before queue mapping. Stopped-queue skipping prevents head-of-line blocking but may starve a stopped band until hardware wakes.

Test signals: create on non-multiqueue devices should fail; changing real queue count should add/remove children; enqueue should honor queue mappings and fallback; dequeue should skip stopped queues and rotate fairly; grafting should replace one band; filter actions should drop/stolen packets correctly; dumps should report band counts and child handles.
