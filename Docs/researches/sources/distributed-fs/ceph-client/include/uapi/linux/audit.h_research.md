<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/audit.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/audit.h

## Purpose
Defines the Linux audit netlink ABI: message type ranges, audit rule constants, filter/action fields, status and feature structures, architecture identifiers, multicast groups, and variable-length rule records.

## Important APIs, Types, And Functions
Exports command messages `AUDIT_GET`, `AUDIT_SET`, rule add/delete/list commands, TTY and feature commands, large event type ranges for syscall/path/LSM/crypto/integrity/anomaly records, filter constants, field ids, operators, status masks, feature bitmaps, `AUDIT_ARCH_*` values, `audit_status`, `audit_features`, `audit_tty_status`, and `audit_rule_data`.

## Control Flow
Audit userspace uses netlink to get/set audit status, configure auditd pid/rate/backlog/failure policy, add/list/delete syscall rules, configure TTY auditing, and query/set feature locks. The kernel emits audit records in the numeric event ranges to auditd or multicast read-only listeners.

## State And Persistence
Kernel audit state includes enabled/failure mode, auditd pid, rate/backlog counters, feature locks, TTY settings, syscall/filter rule lists, watches, and lost-message counters. Persistence is external through auditd rules/config reloaded at boot.

## Dependencies And Integration Points
Depends on Linux types and ELF machine ids. Integrates with netlink, auditd/libaudit, LSMs, seccomp, io_uring, BPF, integrity/IMA/EVM, netfilter, fanotify, and filesystem watches.

## Risks And Edge Cases
Numeric message ranges are ABI; renumbering is forbidden. Rule arrays have fixed maxima, `buf[]` carries variable string fields, architecture ids encode bitness/endian/convention, and feature locks can make settings immutable. Backlog/rate failure policy can drop logs or panic the system.

## Test Signals
Netlink get/set status tests, rule add/list/delete with integer and string fields, syscall arch filtering, TTY auditing, feature lock behavior, multicast read-log listener tests, lost/backlog counters, and malformed rule buffer rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/audit.h -->
