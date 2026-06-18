# sources/distributed-fs/ceph-client/net/sctp/socket.c lines 9374-9729

## Scope

This chunk covers the final SCTP socket helpers and protocol operation tables in `sources/distributed-fs/ceph-client/net/sctp/socket.c`. The requested line range begins inside `sctp_wait_for_connect()` and runs through the end of the IPv6 SCTP `struct proto` definition. For complete control-flow context, the enclosing function signatures and nearby callers were also inspected.

The source tree path is under a Ceph client snapshot, but this code is generic Linux SCTP networking socket infrastructure. It does not implement CephFS behavior directly.

## Purpose

This code closes out the SCTP socket implementation by providing the wait/migration primitives that connect user-facing socket operations to SCTP association lifetime, then registering the SCTP protocol callbacks with the kernel socket layer.

The wait helpers translate SCTP association state transitions into standard socket blocking behavior:

- `sctp_wait_for_connect()` waits for an active association setup to reach `ESTABLISHED`, fail, be interrupted, or remain in progress for nonblocking callers.
- `sctp_wait_for_accept()` waits for a TCP-style SCTP listening endpoint to have an association available on the endpoint association list, which is treated as the accept queue.
- `sctp_wait_for_close()` implements TCP-style close linger waiting until all endpoint associations are gone or the timeout/signal condition ends the wait.

The migration helpers support SCTP's two ways to split an association onto a new socket: TCP-style `accept()` and UDP-style peeloff. `sctp_sock_migrate()` is the main handoff routine. It attaches the cloned socket to the same port binding, duplicates bind addresses, moves queued receive data for the selected association, preserves partial-delivery state, retargets queued receive and transmit skb ownership, moves the association's `base.sk`, and marks the new socket as established or closed.

The `sctp_prot` and `sctpv6_prot` tables are the integration boundary with the generic socket/proto layer. They bind SCTP-specific implementations for close, connect/disconnect, accept, bind, send, receive, getsockopt, setsockopt, backlog processing, hashing, memory accounting, and sysctl memory limits. The IPv6 table mirrors the IPv4/dual-stack table but uses `struct sctp6_sock`, exposes `ipv6_pinfo_offset`, and wraps initialization so IPv6 sockets use `inet6_sock_destruct()`.

## Important APIs, Types, And Functions

- `sctp_wait_for_connect(struct sctp_association *asoc, long *timeo_p)`: waits on `asoc->wait` while holding a temporary association reference. It releases the socket lock before sleeping with `schedule_timeout()` and reacquires it after waking. It returns `0` for success/acceptable exit, `-EINPROGRESS` for immediate nonblocking progress, `sock_intr_errno()` for interrupted waits, `-ECONNREFUSED` for setup failure before exhausting init attempts, and `-ETIMEDOUT` once init attempts are exhausted.
- `sctp_wait_for_accept(struct sock *sk, long timeo)`: waits on `sk_sleep(sk)` until `sctp_sk(sk)->ep->asocs` is non-empty. It validates the socket is still SCTP listening and not receive-shutdown, then returns `0`, `-EINVAL`, `-EAGAIN`, or an interrupt error.
- `sctp_wait_for_close(struct sock *sk, long timeout)`: waits on `sk_sleep(sk)` until the endpoint association list becomes empty, a signal arrives, or the timeout expires. It intentionally returns no status; close already proceeds with later socket release cleanup.
- `sctp_skb_set_owner_r_frag(struct sk_buff *skb, struct sock *sk)`: recursively walks skb fragments with `skb_walk_frags()` and applies `sctp_skb_set_owner_r()` to every skb fragment and the parent skb. This is used when receive-side ownership is moved from an old socket to a newly accepted or peeled-off socket.
- `sctp_sock_migrate(struct sock *oldsk, struct sock *newsk, struct sctp_association *assoc, enum sctp_socket_type type)`: populates the cloned SCTP socket state and migrates one association plus its queued data to the clone. It is called from `sctp_clone_sock()`, which is used by both `sctp_accept()` and UDP-style peeloff.
- `sctp_prot`: the SCTP `struct proto` for non-IPv6 object layout, using `struct sctp_sock` as `obj_size` and exposing the userspace-copy region from `subscribe` through `initmsg`.
- `sctp_v6_destruct_sock(struct sock *sk)`: IPv6-specific destructor wrapper that calls `inet6_sock_destruct()`.
- `sctp_v6_init_sock(struct sock *sk)`: calls the common `sctp_init_sock()` and, on success, installs the IPv6 destructor.
- `sctpv6_prot`: the IPv6 SCTP `struct proto`, compiled only when `CONFIG_IPV6` is enabled. It uses `struct sctp6_sock`, sets `ipv6_pinfo_offset`, and uses the same SCTP operation callbacks as IPv4 except for initialization and object layout.

Important data structures and fields:

- `struct sctp_association`: provides `base.sk`, `state`, `base.dead`, `wait`, `init_err_counter`, `max_init_attempts`, `ulpq`, `peer`, and association queues used by wait and migration paths.
- `struct sctp_sock`: SCTP per-socket extension reached via `sctp_sk(sk)`, including `ep`, `type`, `bind_hash`, `pd_lobby`, `pd_mode`, `subscribe`, and `initmsg`.
- `struct sctp_endpoint`: owns `asocs`, the endpoint association list. In TCP-style listen sockets this list is used as the accept queue.
- `struct sk_buff` and `struct sctp_ulpevent`: receive messages in `sk_receive_queue` and `pd_lobby` are associated with an SCTP association through `sctp_skb2event(skb)->asoc`.
- `struct sctp_bind_bucket` and `struct sctp_bind_hashbucket`: the migration path attaches `newsk` to the same SCTP port bind bucket as `oldsk` under the bind hash bucket spinlock.
- `struct proto`: the kernel protocol-operation table consumed by inet registration code in `net/sctp/protocol.c` and `net/sctp/ipv6.c`.

## Control Flow

### Connect Wait

`sctp_wait_for_connect()` is entered after active association setup has been started, such as through the `__sctp_connect()` path. The caller passes the remaining send timeout by pointer. The helper first takes an association reference with `sctp_association_hold()` so that the association cannot disappear while the task sleeps.

The loop registers the current task on `asoc->wait` as an exclusive interruptible waiter. It then checks immediate exit conditions in priority order. A zero timeout produces `-EINPROGRESS`, which is the expected nonblocking-connect result. Receive shutdown exits the wait with the current `err` value. Socket errors, association shutdown-pending-or-later state, or a dead association enter the error mapping path. Pending signals return `sock_intr_errno(*timeo_p)`. If the association is already `ESTABLISHED`, the loop succeeds.

When the association is not yet established, the helper releases the socket lock, sleeps with `schedule_timeout(current_timeo)`, reacquires the socket lock, and writes the remaining timeout back through `timeo_p`. On all exits it removes the wait entry with `finish_wait()` and drops the temporary association reference.

The state-machine side wakes this queue when an association reaches `ESTABLISHED`, `CLOSED`, or `SHUTDOWN_RECEIVED`, so connect waiters see both successful and failed setup transitions.

### Accept Wait

`sctp_wait_for_accept()` is used by `sctp_accept()` after the caller has already verified TCP-style listening state and computed the receive timeout. It uses the endpoint association list as the readiness condition. If `ep->asocs` is empty, it releases the socket lock, calls `schedule_timeout(timeo)`, and reacquires the lock.

After each sleep opportunity, it revalidates that the socket is still listening and not receive-shutdown. This matters because another thread can close or disconnect the listening socket while the accept path sleeps. If an association is now present, it returns success. Otherwise, a pending signal returns `sock_intr_errno(timeo)`, and an exhausted timeout returns `-EAGAIN`.

On success, the caller takes the first association from `sctp_sk(sk)->ep->asocs` and calls `sctp_clone_sock(sk, asoc, SCTP_SOCKET_TCP)`. The clone path creates a new endpoint and then delegates the actual association and skb migration to `sctp_sock_migrate()`.

### Close Wait

`sctp_wait_for_close()` is called during `sctp_close()` for TCP-style sockets with a linger timeout. It waits on the socket sleep queue while the endpoint association list is non-empty. The loop releases the socket lock around `schedule_timeout(timeout)` so state-machine and receive/backlog work can progress. It stops when all associations are gone, a signal is pending, or the timeout reaches zero. The helper does not report a result because close cleanup continues regardless.

### Receive skb Ownership Migration

`sctp_skb_set_owner_r_frag()` handles receive-side socket accounting for both ordinary skbs and fragmented skbs. If an skb has `data_len`, each fragment is visited recursively and retargeted before the parent skb is retargeted. This prevents receive-memory accounting and destructor behavior from remaining tied to `oldsk` after queued data has moved to `newsk`.

### Association Migration

`sctp_sock_migrate()` assumes `newsk` was cloned from `oldsk` and already has a freshly allocated SCTP endpoint. Because cloning copied the old `struct sctp_sock`, the first step restores `newsp->ep` to that new endpoint.

The new socket is then attached to the same SCTP bind bucket as the old socket. The code computes the bind hash bucket from the old socket net namespace and local port, takes `head->lock`, adds `newsk` to `pp->owner`, records `newsk`'s `bind_hash`, copies `inet_num`, and unlocks. This keeps the accepted or peeled-off socket bound to the same local SCTP port.

Next, the new endpoint receives a duplicate of the original endpoint bind address list through `sctp_bind_addr_dup()`. This is required for restart handling and local address awareness. Failure returns immediately before association migration. On success, `sctp_auto_asconf_init(newsp)` initializes automatic address-configuration state for the new SCTP socket.

Queued receive events are then split by association. The old socket receive queue is scanned with `sctp_skb_for_each()`. Any skb whose `sctp_ulpevent` points at the migrating association is unlinked from `oldsk->sk_receive_queue`, appended to `newsk->sk_receive_queue`, and has its receive owner changed recursively.

Partial delivery receives special handling. The new socket's `pd_mode` is set from `assoc->ulpq.pd_mode`. If the old socket is in partial-delivery mode, skbs in `oldsp->pd_lobby` for the migrating association are moved either to `newsp->pd_lobby` when this association itself remains in partial delivery, or to `newsk->sk_receive_queue` when the migrating association is not the partial-delivery association. In the former case, `sctp_clear_pd(oldsk, NULL)` clears the old socket partial-delivery state for skbs waiting behind the migration.

The helper also retargets receive skbs still held inside the association ULP queues (`ulpq.lobby`, `ulpq.reasm`, and `ulpq.reasm_uo`) via `sctp_for_each_rx_skb()`.

After data queues are handled, `newsp->type` is set to the requested socket type: TCP style for `accept()` or high-bandwidth UDP style for peeloff. The new socket is then locked with `lock_sock_nested(newsk, SINGLE_DEPTH_NESTING)` before the association object is moved. This deliberately marks the new socket in use so packets racing with the migration are queued to the backlog rather than processed concurrently.

Transmit data chunks need socket ownership retargeting too. Before moving the association, `sctp_for_each_tx_datachunk(assoc, true, sctp_clear_owner_w)` clears ownership on chunks that still point to the old association socket. `sctp_assoc_migrate(assoc, newsk)` updates the association's socket binding. A second pass, `sctp_for_each_tx_datachunk(assoc, false, sctp_set_owner_w)`, assigns write ownership for chunks that now need to point to the new socket. This covers transmitted, retransmit, sacked, abandoned, and unsent output-queue chunks through the helper defined earlier in the file.

Finally, socket state is published. A closed association accepted from a TCP-style listening socket sets `SCTP_SS_CLOSED` and `RCV_SHUTDOWN`; otherwise the new socket is marked `SCTP_SS_ESTABLISHED`. The new socket lock is released and migration succeeds.

### Protocol Table Registration

The `sctp_prot` table is a static operation vector consumed when SCTP is registered with the inet protocol layer. It wires common socket operations to SCTP implementations:

- Lifetime and connection: `sctp_close`, `sctp_disconnect`, `sctp_accept`, `sctp_init_sock`, `sctp_destroy_sock`, `sctp_shutdown`.
- Userspace APIs: `sctp_ioctl`, `sctp_setsockopt`, `sctp_getsockopt`, `sctp_bpf_bypass_getsockopt`, `sctp_sendmsg`, `sctp_recvmsg`, `sctp_bind`, `sctp_bind_add`.
- Internal networking hooks: `sctp_backlog_rcv`, `sctp_hash`, `sctp_unhash`.
- Socket allocation and accounting: `obj_size`, `useroffset`, `usersize`, SCTP memory sysctls, memory-pressure counters, forward-allocation counters, and sockets-allocated counters.

The IPv6 table is compiled under `IS_ENABLED(CONFIG_IPV6)` and mirrors these callbacks. Its key differences are object layout (`struct sctp6_sock`), IPv6 private-info offset, and `sctp_v6_init_sock()`, which installs `sctp_v6_destruct_sock()` after common initialization succeeds.

## State And Persistence Behavior

All state in this chunk is in-memory kernel networking state. There is no filesystem or durable persistence.

Important state transitions and ownership effects include:

- Association references: `sctp_wait_for_connect()` holds the association across sleeps and releases it on every exit path.
- Wait queues: connect waits use `asoc->wait`, while accept and close waits use `sk_sleep(sk)`. State-machine code wakes these queues when association state changes.
- Socket locks: all three wait helpers release the socket lock before sleeping and reacquire it after wakeup. This is necessary for SCTP state-machine, backlog, close, and receive paths to make progress.
- Endpoint association list: `sctp_wait_for_accept()` and `sctp_wait_for_close()` treat `sctp_sk(sk)->ep->asocs` as the durable in-memory readiness/lifetime condition.
- Bind state: migrated sockets are added to the same bind bucket owner list and copy `inet_num`, so the new socket remains bound to the original local SCTP port.
- Bind addresses: the new endpoint receives a duplicate bind-address list from the old endpoint. This persists local address state across peeloff/accept and supports restart/address-management behavior.
- Receive queue state: skbs for the migrated association are moved from old socket queues to new socket queues, with skb owner/accounting rewritten for parent and fragment skbs.
- Partial-delivery state: `pd_mode` is copied from the association to the new socket, and `pd_lobby` entries are moved or released according to whether the migrating association is the active partial-delivery association.
- Association socket pointer: `sctp_assoc_migrate()` moves the association from `oldsk` to `newsk`; queued transmit chunks have write owners cleared and restored around this change.
- Socket state: migration publishes `SCTP_SS_ESTABLISHED` for normal accepted/peeled-off associations and `SCTP_SS_CLOSED` plus `RCV_SHUTDOWN` for already-closed TCP-style associations.
- Protocol accounting state: the `struct proto` tables bind SCTP sockets to global/per-net memory accounting counters, sysctl memory thresholds, and socket allocation counters.

## Dependencies And Integration Points

This chunk depends on core SCTP socket, endpoint, association, ULP event, and queue helpers defined earlier in the same file and in SCTP headers:

- Association state and references: `sctp_state()`, `sctp_association_hold()`, `sctp_association_put()`, `sctp_assoc_migrate()`.
- Socket and endpoint accessors: `sctp_sk()`, `sctp_style()`, `sctp_sstate()`, `inet_sk_set_state()`, `sk_sleep()`, `lock_sock()`, `release_sock()`.
- Queue/event helpers: `sctp_skb_for_each()`, `sctp_skb2event()`, `sctp_skb_set_owner_r()`, `sctp_clear_pd()`, `sctp_for_each_rx_skb()`, `sctp_for_each_tx_datachunk()`, `sctp_clear_owner_w()`, `sctp_set_owner_w()`.
- Bind/address helpers: `sctp_phashfn()`, `sctp_port_hashtable`, `sk_add_bind_node()`, `sctp_bind_addr_dup()`, `sctp_auto_asconf_init()`.
- Linux wait and scheduling primitives: `DEFINE_WAIT`, `prepare_to_wait_exclusive()`, `prepare_to_wait()`, `finish_wait()`, `schedule_timeout()`, `TASK_INTERRUPTIBLE`, and `signal_pending()`.
- Socket error/timeout conventions: `sock_intr_errno()`, `sock_rcvtimeo()`, `sock_sndtimeo()`, nonblocking `-EINPROGRESS`/`-EAGAIN`, and shutdown flags such as `RCV_SHUTDOWN`.
- Memory/accounting integration: skb owner APIs, `sk_wmem_queued`, protocol memory-pressure counters, SCTP sysctl memory arrays, and proto `useroffset`/`usersize` support.
- IPv6 integration: `inet6_sock_destruct()`, `struct sctp6_sock`, `struct ipv6_pinfo`, and `CONFIG_IPV6` registration paths.

Important external callers and registration points:

- `__sctp_connect()` starts association setup and calls `sctp_wait_for_connect()` with send-timeout semantics.
- `sctp_accept()` calls `sctp_wait_for_accept()`, selects the first endpoint association, and calls `sctp_clone_sock()`, which delegates to `sctp_sock_migrate()`.
- UDP-style peeloff calls `sctp_do_peeloff()`, which validates namespace/style/association ID, creates a lightweight socket, clones the SCTP socket, and relies on `sctp_sock_migrate()` to move the association.
- `sctp_close()` calls `sctp_wait_for_close()` for TCP-style sockets when linger waiting is requested.
- `net/sctp/protocol.c` registers `sctp_prot` for IPv4/inet SCTP operation, and `net/sctp/ipv6.c` registers `sctpv6_prot` when IPv6 support is enabled.
- SCTP state-machine side effects in `sm_sideeffect.c` wake `asoc->wait` and `sk->sk_state_change()` so these socket waiters observe association transitions.

## Risks And Edge Cases

- Sleep paths must always release the socket lock before `schedule_timeout()`. Holding it while sleeping would block the state-machine and backlog work needed to satisfy the wait condition.
- `sctp_wait_for_connect()` checks the original timeout pointer before sleeping and writes back the remaining `current_timeo` after wakeup. Callers depend on this remaining-time behavior for connect timeout semantics.
- Connect failure mapping depends on `init_err_counter + 1 > max_init_attempts`. Changing init retry accounting can alter whether userspace sees `-ECONNREFUSED` or `-ETIMEDOUT`.
- Accept readiness is represented by `ep->asocs`, not a separate accept queue object. Any code that adds or removes associations from a TCP-style listening endpoint must preserve the wakeup and list invariants expected here.
- `sctp_wait_for_accept()` can sleep with zero timeout, but `schedule_timeout(0)` returns immediately and the later timeout check returns `-EAGAIN`. This preserves nonblocking accept behavior but is easy to misread.
- `sctp_wait_for_close()` ignores the final reason for wakeup. That is intentional for close, but callers cannot distinguish clean association drain from signal/timeout based on this helper alone.
- Socket migration has several ownership domains that must move together: bind-hash membership, endpoint bind addresses, receive queues, partial-delivery lobby, association ULP queues, association socket pointer, and transmit skb owners. Missing one can leak memory accounting, deliver data on the wrong descriptor, or leave retransmission chunks charged to the wrong socket.
- The bind-hash insertion happens before `sctp_bind_addr_dup()`. If address duplication fails, cleanup relies on the caller's `sk_common_release(newsk)` path to unwind the partially attached clone correctly.
- Receive skb migration filters by `event->asoc == assoc`. Any skb queued without a valid SCTP ULP event association would not migrate and could remain attached to the old socket.
- Fragment ownership is recursive. A future change that only retargets the parent skb would leave fragment memory ownership inconsistent.
- Partial delivery is subtle. If the migrated association is in partial delivery, its lobby must remain in the new socket's partial-delivery lobby; if not, its skbs should become ordinary receive-queue data. Incorrect handling can stall partial delivery or reorder user-visible data.
- Lock ordering during migration is constrained. The old socket is already locked by the caller, and the newly allocated socket is locked with `SINGLE_DEPTH_NESTING`. The code relies on the new socket not being reachable by other paths yet, preventing lock-order inversions.
- The migration code deliberately locks `newsk` before `sctp_assoc_migrate()` so packets arriving after the association socket pointer changes go to backlog. Removing this would reopen a race between old-socket backlog processing and new-socket packet processing.
- Transmit chunk owner retargeting must bracket `sctp_assoc_migrate()`. If ownership is set before association migration or not restored after it, send-buffer accounting and write-space wakeups can be wrong.
- Closed associations can still be accepted from a TCP-style listening socket. The migration path sets `RCV_SHUTDOWN` for this case; callers and tests must not assume accept always returns an established live association.
- `struct proto.useroffset` and `usersize` expose a contiguous region of SCTP socket state for userspace-copy handling. Layout changes to `struct sctp_sock` or `struct sctp6_sock` must keep this range intentional.
- IPv6 sockets depend on `sctp_v6_init_sock()` replacing the destructor only after common SCTP initialization succeeds. Installing it too early or failing to install it can break IPv6 private-state cleanup.
- Protocol table changes are broad blast-radius changes. A wrong callback, object size, memory counter, or hash/unhash hook can affect all SCTP sockets, including both Ceph-adjacent kernels and unrelated SCTP applications.

## Test Signals

Useful validation signals for this chunk include:

- Build coverage with SCTP enabled both with and without `CONFIG_IPV6`, verifying that `sctp_prot` and `sctpv6_prot` register with the expected object sizes and callbacks.
- Active connect tests for blocking connect success, nonblocking connect returning `-EINPROGRESS`, interrupted connect returning the expected restart/interrupted errno, setup refusal, and timeout after exhausting init attempts.
- Connect race tests where the association reaches `ESTABLISHED`, `CLOSED`, `SHUTDOWN_RECEIVED`, shutdown-pending, or dead state while a task sleeps in `sctp_wait_for_connect()`.
- Lockdep and scheduling tests that exercise connect, accept, and close waits under load, ensuring no socket lock is held across blocking sleeps and no waitqueue entries leak.
- TCP-style accept tests for blocking accept, nonblocking accept returning `-EAGAIN`, interrupted accept, accept after listener shutdown returning `-EINVAL`, and accepting an already-closed association with `RCV_SHUTDOWN` set on the new socket.
- Close/linger tests where associations drain before timeout, timeout expires with associations still present, and a signal interrupts the close wait.
- UDP-style peeloff tests for valid association ID, invalid association ID, wrong socket style, already peeled-off sockets, and namespace mismatch rejection.
- Migration tests that queue receive data for multiple associations on a UDP-style socket, peel off one association, and confirm only that association's events move to the new socket.
- Fragmented receive skb tests confirming parent and fragment skb receive ownership/accounting move to `newsk`.
- Partial-delivery tests covering migration of the active partial-delivery association, migration of a non-partial association while the old socket is in partial-delivery mode, and clearing of old partial-delivery state.
- ULP reassembly/lobby tests verifying skbs in `assoc->ulpq.lobby`, `reasm`, and `reasm_uo` have ownership retargeted during accept or peeloff.
- Transmit queue tests with chunks in transmitted, retransmit, sacked, abandoned, and unsent queues during migration, checking send-buffer accounting, retransmission behavior, and write-space wakeups after migration.
- Bind/address tests confirming accepted and peeled-off sockets retain the original local port, bind hash membership, and bind address list, including multihoming/restart scenarios.
- Concurrency tests with packets arriving during `sctp_sock_migrate()`, verifying they queue to the new socket backlog and are not processed concurrently on old and new sockets.
- Security/LSM integration tests around `sctp_clone_sock()` and migration, ensuring later `security_sctp_sk_clone()` sees the migrated association and new socket state expected by policy.
- IPv6 SCTP socket lifecycle tests confirming `sctp_v6_init_sock()` uses the common SCTP initialization path and that IPv6 socket destruction releases IPv6 private state.
- Memory diagnostics with KASAN/KCSAN/KMEMLEAK/refcount debugging around accept, peeloff, connect timeout, and close to catch use-after-free, leaked association references, bind bucket leaks, or skb accounting mismatches.
