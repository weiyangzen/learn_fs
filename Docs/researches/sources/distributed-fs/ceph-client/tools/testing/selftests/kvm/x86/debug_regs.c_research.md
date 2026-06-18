# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/debug_regs.c

Purpose: Exercises KVM handling of debug registers, including guest writes to DR6/DR7, general-detect behavior, and interrupt/event interactions around debug-register access.

Important APIs/types/functions: Defines debug bits `DR6_BD` and `DR7_GD`, test interrupt vector `IRQ_VECTOR`, `guest_code()` for in-guest debug-register operations, `vcpu_skip_insn()` for host-side instruction advancement, and `main()` to install handlers and interpret exits. It uses `KVM_GET/SET_REGS`, debug register instructions, APIC helpers, and exception/interrupt plumbing.

Control flow: The guest configures debug-register state, triggers cases that should produce debug exceptions or exits, and uses ucalls to synchronize. The host inspects exit reasons, may skip trapped instructions, and confirms that architectural debug bits are set or cleared as expected.

State and persistence behavior: Debug-register values are vCPU architectural state and must persist across exits. APIC/interrupt state is transient but used to validate that debug-register exceptions do not corrupt event delivery.

Dependencies and integration points: Depends on KVM x86 debug-register emulation, exception injection, APIC interrupt delivery, and selftest register helpers. It probes host/guest behavior that debuggers and VMMs rely on.

Risks and maintenance notes: Debug-register semantics are detail-heavy and differ between trap-like and fault-like paths. Instruction lengths used by `vcpu_skip_insn()` must stay aligned with the guest instruction sequence.

Test signals: Passing indicates KVM preserves and reports debug-register state correctly, honors GD/BD semantics, and handles related exits without losing pending event state. Failures usually implicate DR emulation or exception delivery.
