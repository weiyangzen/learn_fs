# sources/distributed-fs/ceph-client/include/asm-generic/audit_signal.h

Purpose: Lists signal-sending syscall numbers for generic audit signal classification.

Important APIs, types, and functions: Emits `__NR_kill`, `__NR_tgkill`, and `__NR_tkill`.

Control flow: No conditionals in this fragment; architectures including it are expected to define these syscall numbers.

State and persistence: No runtime state; entries become audit syscall class metadata.

Dependencies and integration points: Used by audit code for process signal operations.

Risks and test signals: Risks are build failures on unusual syscall sets and missing newer signal-related syscalls if the class expectations expand. Test audit signal rules for kill/tgkill/tkill and architecture syscall tables.
