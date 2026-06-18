# sources/distributed-fs/ceph-client/arch/csky/lib/error-inject.c

Purpose: architecture participation in function error-injection validation.

Important APIs/types/functions: functions: `override_function_with_return`

Control flow: Runtime flow is organized around `override_function_with_return`, called by generic kernel subsystems through architecture hooks.

State and persistence: No durable storage is introduced; state is limited to CPU registers, stack frames, and caller-owned kernel objects.

Dependencies and integration: Depends on `linux/error-injection.h`, `linux/kprobes.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Main risk is architecture-specific behavior that generic CI may not exercise without target cross-build and boot/runtime coverage.

Test signals: C-SKY cross-build.
