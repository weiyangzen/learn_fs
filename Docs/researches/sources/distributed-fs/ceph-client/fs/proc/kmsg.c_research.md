<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/kmsg.c -->
## sources/distributed-fs/ceph-client/fs/proc/kmsg.c

Purpose: implements `/proc/kmsg`, a legacy privileged stream over the kernel printk/syslog buffer.

Important APIs and functions: `kmsg_open`, `kmsg_release`, `kmsg_read`, and `kmsg_poll` wrap `do_syslog` actions `SYSLOG_ACTION_OPEN`, `CLOSE`, `READ`, and `SIZE_UNREAD`. `kmsg_proc_ops` marks the entry permanent and uses generic llseek; `proc_kmsg_init` creates the file with mode `S_IRUSR`.

Control flow: opening notifies syslog with `SYSLOG_FROM_PROC`. Reads return `-EAGAIN` for nonblocking callers when no unread data is available, otherwise delegate to `do_syslog`. Poll waits on `log_wait` and reports readable events when unread bytes exist. Release closes the proc syslog session.

State and persistence behavior: no proc-private persistent state exists. State is held by the global printk/syslog subsystem and any syslog permission/rate semantics implemented there.

Dependencies and integration points: depends on procfs, poll, syslog/printk internals, `log_wait`, and VFS file flags. It coexists with `/dev/kmsg` and syslog syscalls but uses the `SYSLOG_FROM_PROC` source tag.

Risks: kernel log access can disclose sensitive data, so permissions and syslog capability checks in `do_syslog` are security-critical. Blocking/nonblocking behavior must match legacy readers. Multiple readers interact through global syslog buffer state, not isolated per-file queues.

Test signals: read as root and unprivileged user under different `dmesg_restrict` settings; nonblocking empty read returns `-EAGAIN`; poll wakes on printk; open/close interactions with other syslog consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/kmsg.c -->
