# sources/distributed-fs/ceph-client/kernel/audit.c

## Purpose
`audit.c` is the core kernel audit gateway between kernel audit producers, LSMs, and userspace audit daemons. It initializes audit netlink sockets, tracks the audit daemon connection, receives audit control messages, queues audit records, performs rate/backlog/failure handling, formats audit buffers, logs task/path/network/security-context information, and exposes exported `audit_log*` APIs.

## Important APIs, types, and functions
Global control state includes `audit_initialized`, `audit_enabled`, `audit_default`, `audit_failure`, rate/backlog tunables, lost counters, audit feature bits, LSM context provider arrays, and audit queues (`audit_queue`, `audit_retry_queue`, `audit_hold_queue`). `struct auditd_connection` tracks auditd PID, portid, and net namespace under RCU. `struct audit_buffer` wraps one or more skb records sharing an audit timestamp/serial. `struct audit_net` holds the per-netns netlink socket.

Key public/exported functions include `audit_log_start()`, `audit_log_end()`, `audit_log_format()`, `audit_log()`, `audit_log_n_hex()`, `audit_log_n_string()`, `audit_log_n_untrustedstring()`, `audit_log_d_path()`, `audit_log_task_info()`, `audit_log_task_context()`, `audit_log_subj_ctx()`, `audit_log_obj_ctx()`, `audit_log_nf_skb()`, `audit_set_loginuid()`, `audit_signal_info()`, `audit_serial()`, `audit_panic()`, `audit_ctl_lock()`, and `audit_ctl_unlock()`.

## Control flow
`audit_init()` allocates the buffer cache, initializes skb queues and inode hash buckets, registers per-netns audit netlink sockets, starts `kauditd`, and emits an initialization record. Boot parameters `audit=` and `audit_backlog_limit=` set initial state. Incoming netlink messages arrive through `audit_receive()`, are serialized by `audit_cmd_mutex`, authorized by `audit_netlink_ok()`, and handled by `audit_receive_msg()`. Control cases cover status get/set, auditd registration, feature get/set, user messages, rule add/delete/list, tree trim/equivalence, signal info, and TTY audit settings.

Audit record generation starts with `audit_log_start()`: it checks initialization, exclude filters, backlog limits, and allocates an audit buffer with a timestamp/serial prefix. Formatting appends to the skb, expanding if needed. `audit_log_end()` enqueues all skbs and wakes `kauditd`. `kauditd_thread()` drains hold, retry, and main queues; it attempts unicast to auditd, multicasts to listeners, moves failed records between retry/hold queues, prints last-resort records, and wakes backlog waiters.

## State and persistence behavior
Audit records persist only after userspace auditd receives and stores them; the kernel maintains transient queues and counters. Lost records are counted in `audit_lost`, and backlog wait time is accumulated. Audit loginuid/session state is stored in each task. Feature locks and `AUDIT_LOCKED` can make configuration immutable until reboot. The auditd connection holds references to its PID and network namespace and is replaced under RCU.

## Dependencies and integration points
The file integrates with netlink, per-network namespace operations, kthreads/freezer, skbuffs, LSM security context APIs, audit filters from `auditfilter.c`, syscall audit context from `auditsc.c`, path and tty helpers, credentials, capabilities, PID/user namespaces, netfilter packet structures, and kernel panic/printk paths.

## Risks and invariants
The highest-risk areas are loss/backpressure behavior, auditd connection lifetime, and sleeping while holding the audit control mutex. The code deliberately avoids blocking auditd itself or the control-lock owner in backlog handling. `auditd_reset()` must not dereference possibly stale connection pointers. Netlink authorization is intentionally restricted to the initial user and PID namespaces for control operations. Formatting untrusted strings must preserve audit log parseability by hex-encoding unsafe content.

## Test signals
Use auditctl/auditd integration tests for status changes, daemon replacement, locked mode, feature locks, rule operations, multicast read-log listeners, backlog overflow, rate limiting, auditd disconnect/reconnect, and user messages. Add LSM multi-context tests, network skb logging tests for IPv4/IPv6/TCP/UDP/SCTP, loginuid permission tests, and fault injection for skb/kmem allocation and netlink send failures.
