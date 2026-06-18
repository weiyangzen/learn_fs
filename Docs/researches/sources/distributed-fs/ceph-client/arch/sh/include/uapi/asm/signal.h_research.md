<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/signal.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/signal.h

Purpose: adds SH-specific signal action ABI details.

Important APIs/types/functions: `SA_RESTORER` and `struct old_sigaction`.

Control flow: sigaction syscalls translate between old/new action layouts and optional restorer trampoline.

State and persistence: state is per-process signal disposition stored by generic signal code.

Dependencies/integration: integrates with libc signal handling and arch signal delivery.

Risks: incorrect restorer semantics break signal return on old userspace.

Test signals: test old and new sigaction paths including custom restorer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/signal.h -->
