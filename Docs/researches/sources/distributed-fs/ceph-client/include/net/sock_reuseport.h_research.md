<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/sock_reuseport.h -->
# sources/distributed-fs/ceph-client/include/net/sock_reuseport.h

Purpose: Declares the SO_REUSEPORT group container and helpers that let multiple sockets share a bind bucket while selecting a concrete socket by hash, BPF program, CPU, or migration policy.

Important APIs/types/functions: `struct sock_reuseport` stores RCU lifetime, socket array capacity/counts, closed-socket count, incoming CPU, SYN queue overflow timestamp, stable group id, bind-in-any and has-connections flags, optional BPF selector program, and flexible `socks[]`. The public API includes `reuseport_alloc()`, `reuseport_add_sock()`, `reuseport_detach_sock()`, `reuseport_stop_listen_sock()`, `reuseport_select_sock()`, `reuseport_migrate_sock()`, BPF attach/detach helpers, `reuseport_has_conns()`, `reuseport_has_conns_set()`, and `reuseport_update_incoming_cpu()`.

Control flow: A listener or bound socket enters a reuseport group at allocation/add time. Incoming packet lookup calls `reuseport_select_sock()` with the hash and skb context; an attached BPF program may override selection. Closed listening sockets can be stopped or migrated through `reuseport_stop_listen_sock()` and `reuseport_migrate_sock()`. `reuseport_has_conns()` performs an RCU read-side lookup of `sk->sk_reuseport_cb`.

State and persistence behavior: State is per-group kernel memory referenced from `struct sock::sk_reuseport_cb` and protected by RCU plus the global `reuseport_lock` for mutations. The group id survives socket-array growth. `synq_overflow_ts` is shared by TCP syncookie logic for listeners in the same group.

Dependencies/integration points: Depends on `sock.h`, `skbuff.h`, filter/BPF infrastructure, and spinlocks. TCP uses the overflow timestamp, packet lookup uses it from UDP/TCP hash paths, and BPF reuseport arrays depend on the socket group.

Risks: Array resize, detach, and selection must preserve RCU safety. Incorrect closed-socket accounting can select dead listeners or block migration. BPF selector return validation is security-sensitive.

Test signals: SO_REUSEPORT selftests with TCP and UDP, BPF selector tests, listener close/migration tests, SYN flood syncookie behavior across a reuseport group, KCSAN/RCU stall checks during concurrent add/detach/select.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/sock_reuseport.h -->
