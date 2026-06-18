<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/debugreg.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/debugreg.h

Purpose: Exposes x86 debug register numbers, DR6 status bits, DR7 control encodings, breakpoint access types, breakpoint lengths, and reserved masks to userspace and kernel UAPI consumers.

Important APIs/types/functions: `DR_FIRSTADDR`, `DR_LASTADDR`, `DR_STATUS`, `DR_CONTROL`, `DR6_RESERVED`, `DR_TRAP*`, `DR_BUS_LOCK`, `DR_STEP`, `DR_SWITCH`, `DR_CONTROL_SHIFT`, `DR_RW_*`, `DR_LEN_*`, `DR_LOCAL_ENABLE*`, `DR_GLOBAL_ENABLE*`, `DR_CONTROL_RESERVED`, and slowdown flags.

Control flow: Debugger, ptrace, perf, and hardware-breakpoint code interpret DR6/DR7 using these constants when setting or reporting debug exceptions.

State and persistence behavior: No state is owned here; state lives in CPU debug registers, ptrace-visible debug state, and task debug contexts.

Dependencies and integration points: Integrates with ptrace, perf hardware breakpoints, KVM debug registers, bus-lock detection, RTM debug behavior, and CPU exception handling.

Risks and test signals: Risks include wrong reserved masks on newer CPUs, incorrect breakpoint length/access encoding, and 32-bit versus 64-bit mask differences. Test ptrace hardware breakpoints, single-step, bus-lock debug exceptions, KVM debug register save/restore, and perf breakpoint events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/debugreg.h -->
