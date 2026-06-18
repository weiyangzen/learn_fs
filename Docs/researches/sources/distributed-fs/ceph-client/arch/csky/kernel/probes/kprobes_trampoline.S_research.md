# sources/distributed-fs/ceph-client/arch/csky/kernel/probes/kprobes_trampoline.S

Purpose: assembly trampoline used for C-SKY kretprobe return interception.

Important APIs/types/functions: No local public API surface; this file contributes declarations, constants, or selected objects to surrounding architecture code.

Control flow: Control enters through architecture entry labels, follows the architecture ABI/register convention, and branches or returns into linked C/kernel entry points.

State and persistence: No durable storage is introduced; state is limited to CPU registers, stack frames, and caller-owned kernel objects.

Dependencies and integration: Depends on `linux/linkage.h`, `abi/entry.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Main risk is architecture-specific behavior that generic CI may not exercise without target cross-build and boot/runtime coverage.

Test signals: C-SKY cross-build; ftrace, kprobes, uprobes, and jump-label selftests.
