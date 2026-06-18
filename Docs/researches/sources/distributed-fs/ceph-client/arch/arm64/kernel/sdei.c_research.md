# sources/distributed-fs/ceph-client/arch/arm64/kernel/sdei.c

Purpose: this file provides ARM64 architecture support for Software Delegated Exception Interface events. It allocates per-CPU SDEI stacks and optional shadow call stacks, selects the firmware entry point, and handles SDEI event return routing.

Important APIs and state: globals include `sdei_exit_mode`, per-CPU normal/critical SDEI stack pointers, optional per-CPU normal/critical SCS pointers, and per-CPU active event pointers. `sdei_arch_get_entry_point()` returns the handler/trampoline address firmware should call. `do_sdei_event()` reconstructs clobbered registers, calls the generic SDEI event handler, and returns a firmware action code or exception-vector address.

Control flow: stack allocation loops over possible CPUs and unwinds on failure. SCS allocation is skipped when SCS is disabled. Entry-point selection rejects nVHE configurations, records whether exit uses HVC or SMC, and returns a trampoline alias when KPTI/unmapped-at-EL0 requires it. Event handling retrieves missing register values via `sdei_api_event_context()`, calls `sdei_event_handler()`, warns if the handler took a synchronous exception, then either returns handled for masked kernel contexts or redirects to the normal IRQ vector for kernel, AArch32 user, or AArch64 user return paths.

Dependencies and integration: depends on ARM SDEI core, SMCCC conduit, VMAP stacks, SCS allocator, exception vector layout, KPTI trampoline aliases, ptrace regs, and stacktrace/kprobe annotations.

Risks: SDEI may interrupt contexts where the normal stack is unsafe, hence dedicated stacks. Entry support is unavailable in nVHE boot state. Incorrect return vector choice can skip signal/KVM handling or return to unsafe interrupted context. Stack/SCS allocation failures disable SDEI by returning zero entry point.

Test signals: firmware SDEI probe, normal and critical event delivery, KPTI trampoline entry, SCS-enabled builds, and signal delivery after user-mode SDEI interruption. Warnings about exceptions during handlers are high-risk diagnostics.
