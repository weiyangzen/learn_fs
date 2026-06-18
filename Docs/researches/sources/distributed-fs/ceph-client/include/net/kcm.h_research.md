# sources/distributed-fs/ceph-client/include/net/kcm.h

Purpose: Defines Kernel Connection Multiplexor internal socket, psock, mux, per-net, and statistics structures for multiplexing message-oriented KCM sockets over lower transport sockets parsed by strparser.

Important APIs/types/functions: `kcm_psock_stats`, `kcm_mux_stats`, and `kcm_stats` track tx/rx counters and attach/unattach/drop/retry events. `kcm_tx_msg` tracks partial transmit progress and fragments. `kcm_sock` embeds `struct sock` and holds mux membership, tx/rx psock pointers, wait lists, tx mutex, receive disable state, sequence skb, and stats. `kcm_psock` wraps a lower sock, `strparser`, saved callbacks, BPF parser, rx/tx owner KCM sockets, ready message, and stats. `kcm_net` and `kcm_mux` aggregate per-net and mux lists, locks, waiters, queues, and stats.

Control flow: KCM clients wait for available psocks for transmit and ready psocks for receive. Lower socket callbacks are replaced/saved by psock attach; strparser frames receive messages and BPF may parse boundaries. Aggregate helpers add psock/mux stats to retained totals during teardown.

State and persistence: State is in-memory socket/netns lifetime state: mux lists, psock lists, waiters, ready queues, held rx queue, callback replacement, stats, and done/unattaching flags. Proc init/exit optionally exposes stats.

Dependencies/integration: Depends on sockets, sk_buffs, strparser, UAPI KCM, BPF program pointer, mutex/spinlock/list/workqueue primitives, and procfs.

Risks: The comment warns not to use bitfields for flags set under different locks, highlighting lock-domain risk. Callback restoration, psock detach, and wait-list cleanup are sensitive. Test signals include attach/unattach, receive ready drops, tx wait/retry, partial tx fragments, mux teardown, procfs stats, BPF parser framing, and concurrent lower socket callbacks.
