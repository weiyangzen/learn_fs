# sources/distributed-fs/ceph-client/include/linux/cn_proc.h

Purpose: This header exposes process-event connector hooks used to publish fork, exec, id/session, ptrace, comm, coredump, and exit events to the connector subsystem.

Important APIs/types/functions: With `CONFIG_PROC_EVENTS`, it declares `proc_fork_connector`, `proc_exec_connector`, `proc_id_connector`, `proc_sid_connector`, `proc_ptrace_connector`, `proc_comm_connector`, `proc_coredump_connector`, and `proc_exit_connector`. Without the config, all helpers are inline no-ops. It includes the UAPI event definitions from `<uapi/linux/cn_proc.h>`.

Control flow: Process lifecycle code calls the relevant helper at event points. The implementation emits connector messages when proc events are enabled; otherwise calls compile away.

State and persistence behavior: The header stores no state. Runtime state belongs to task structs, connector sockets, and proc-event listener configuration.

Dependencies and integration points: It integrates scheduler/process lifecycle paths with the connector/netlink UAPI and userspace event listeners.

Risks: Event hooks must be placed where task identity fields are stable and locking is appropriate. No-op stubs mean code must not depend on side effects. Connector event ordering matters for monitoring tools.

Test signals: Userspace proc connector listener tests for fork/exec/exit and credential/session changes, config-off build coverage, and lifecycle stress tests are relevant.
