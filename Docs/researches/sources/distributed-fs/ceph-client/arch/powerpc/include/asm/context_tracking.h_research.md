## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/context_tracking.h

Purpose: selects the assembly branch target used when returning through user scheduling paths with or without context tracking.

Important APIs/types/functions: defines `SCHEDULE_USER` as `bl schedule_user` under `CONFIG_CONTEXT_TRACKING_USER`, otherwise `bl schedule`.

Control flow: compile-time macro selection only. Assembly code includes this macro at call sites that need the correct scheduler entry.

State and persistence: no direct state, but the selected target controls whether context tracking/accounting state is updated around user transitions.

Dependencies and integration: integrates with low-level entry/exit assembly, scheduler code, and context-tracking/NOHZ full configurations.

Risks and test signals: choosing the wrong call target can break user/kernel context accounting or add unnecessary overhead. Test signals are builds with and without `CONFIG_CONTEXT_TRACKING_USER`, NOHZ full tests, syscall/interrupt return tracing, and scheduler context tracking selftests.
