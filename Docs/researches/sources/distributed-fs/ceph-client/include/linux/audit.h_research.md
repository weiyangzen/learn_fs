# sources/distributed-fs/ceph-client/include/linux/audit.h

## Purpose
Central in-kernel audit interface. It defines audit rule data structures, public logging helpers, syscall-audit hooks, and no-op fallbacks for builds without `CONFIG_AUDIT` or `CONFIG_AUDITSYSCALL`. Filesystem, security, IPC, networking, seccomp, timekeeping, module, fanotify, and process paths call into this API to attach audit records to kernel events.

## Important APIs, Types, And Functions
Important data structures include `audit_sig_info`, `audit_krule`, `audit_field`, `audit_ntp_data`, and enums for NTP and netfilter configuration audit operations. Public logging APIs include `audit_log()`, `audit_log_start()`, `audit_log_format()`, `audit_log_end()`, string/path/key helpers, LSM context logging, task-info logging, netfilter skb logging, rule changes, loginuid accessors, signal info, and LSM rule updates. Syscall-path APIs include `audit_alloc/free`, syscall and io_uring entry/exit hooks, filename/inode/file tracking, ptrace/seccomp hooks, IPC, socketcall, sockaddr, POSIX mqueue, capability, mmap, `openat2`, module, fanotify, time/NTP, and netfilter config helpers.

## Control Flow
The header uses two levels of conditional dispatch. With `CONFIG_AUDIT`, logging functions are externs implemented in audit core; without it, they compile to no-ops and `audit_enabled` becomes `AUDIT_OFF`. With `CONFIG_AUDITSYSCALL`, inline wrappers first check `audit_context()` or `audit_dummy_context()` and only call the heavier `__audit_*()` implementation when the current task has a real audit context. Syscall exit derives success and return code from pt_regs before forwarding. Compatibility socket calls copy up to `AUDITSC_ARGS` 32-bit arguments into native unsigned long storage before auditing.

## State And Persistence
The header exposes state stored elsewhere: `task_struct` loginuid/sessionid/audit_context fields, global `audit_enabled`, `audit_n_rules`, and `audit_signals`, rule/watch/tree objects, filter keys, LSM rule data, and buffered audit records. Records persist through the audit subsystem's queues and userspace netlink delivery rather than in this header. When auditing is disabled at compile time, all state accessors intentionally collapse to invalid or unset values.

## Dependencies And Integration Points
It includes scheduler, ptrace, architecture audit classification, UAPI audit constants, and fanotify UAPI types. It depends on implementations in audit core and syscall-audit code, architecture syscall helpers, LSM context handling, netfilter, fsnotify/fanotify, capability, IPC, and timekeeping subsystems. Filesystem clients such as Ceph interact indirectly when VFS operations call `audit_getname()`, `audit_inode()`, `audit_file()`, or path-denied logging.

## Risks
Risk centers on missing hooks in security-sensitive paths, incorrect dummy-context checks that either drop records or add overhead, ABI mistakes in compat argument handling, and build-configuration drift between real and stub implementations. Because many helpers become no-ops without config options, code must not rely on audit helpers for functional side effects beyond logging/tracking.

## Test Signals
Kernel audit tests should verify rule installation/listing, loginuid/session behavior, syscall entry/exit records, path and inode records, seccomp actions, fanotify responses, netfilter configuration records, and disabled-config builds. For distributed filesystem paths, useful signals are audit records for open/create/delete/permission-denied events over mounted Ceph filesystems and absence of crashes when audit is compiled out.
