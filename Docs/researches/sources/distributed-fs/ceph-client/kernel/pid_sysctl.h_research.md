<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/pid_sysctl.h -->
# sources/distributed-fs/ceph-client/kernel/pid_sysctl.h

Purpose: Provides the PID-namespace scoped `/proc/sys/vm/memfd_noexec` sysctl helper when both sysctl and memfd creation are enabled, with a no-op fallback otherwise.

Important APIs/types/functions: `pid_mfd_noexec_dointvec_minmax()`, `pid_ns_ctl_table_vm[]`, and `register_pid_ns_sysctl_table_vm()`. The key state is `pid_namespace.memfd_noexec_scope`.

Control flow: On sysctl access, the handler gets the current task's active PID namespace, rejects writes without `CAP_SYS_ADMIN` in that namespace's user namespace, copies the table, computes the effective current scope as the max of the namespace value and parent scope, sets the minimum to the parent scope so children cannot lower enforcement below parents, delegates to `proc_dointvec_minmax()`, and writes the namespace value back on successful write. The registration helper registers the table under `vm`.

State and persistence: State persists in each PID namespace's `memfd_noexec_scope`; the init namespace supplies the initial data pointer for sysctl registration. Parent scope acts as a dynamic lower bound.

Dependencies/integration: Depends on `CONFIG_SYSCTL`, `CONFIG_MEMFD_CREATE`, PID namespaces, user namespace capability checks, and the memfd noexec scope helpers/macros.

Risks: Because the handler rewrites a temporary effective value, bugs in parent-scope calculation could allow policy weakening or display misleading values. The header defines static functions/data and is included by PID namespace code; it must remain small and config-guarded to avoid duplicate symbol issues.

Test signals: reads/writes in init and nested PID namespaces, parent value greater than child value, attempts to lower below parent, unprivileged write rejection, range bounds 0..2, and fallback build without sysctl or memfd support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/pid_sysctl.h -->
