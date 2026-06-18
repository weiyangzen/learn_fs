# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/cgroup_helpers.h

Purpose: public cgroup test helper declarations plus a common errno logging macro.

Important APIs and macros: `log_err`, `clean_errno`, v2 helper declarations for controller/file/cgroup lifecycle, joining, ids, xattrs, setup/cleanup, and v1 net_cls declarations.

Control flow: header only.

State and persistence: no header state; implementation manipulates cgroup mounts and process membership.

Dependencies and integration points: included by tests needing cgroup setup or attachment targets.

Risks: `log_err` depends on `fprintf` being available from includer order; helper calls can have broad process/environment side effects.

Test signals: compile-time interface for cgroup tests; runtime diagnostics include source file and line.
