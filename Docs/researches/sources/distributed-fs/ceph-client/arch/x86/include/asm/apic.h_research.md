
# sources/distributed-fs/ceph-client/arch/x86/include/asm/apic.h

Purpose: public x86 local APIC control surface. It defines APIC verbosity, interrupt-mode identifiers, xAPIC/x2APIC register access helpers, APIC driver dispatch, vector bitmap helpers, topology registration prototypes, and SMP wakeup/IPI hooks.

Important APIs and control flow: `native_apic_mem_{read,write,eoi}` access the MMIO LAPIC window, with an `X86_BUG_11AP` alternative for writes. x2APIC helpers access APIC MSRs and gate behavior on `CONFIG_X86_X2APIC`. `struct apic` is the selected APIC driver vtable; `apic_driver()` places candidates in `.apicdrivers`; `apic_setup_apic_calls()` installs static-call wrappers such as `apic_read()`, `apic_write()`, `apic_eoi()`, and IPI send functions. Vector helpers query/set APIC IRR-style bitmaps.

State, dependencies, and risks: state is mostly global APIC mode, driver pointer, APIC ID topology, static calls, and hardware registers. Dependencies include fixmap APIC mapping, MSRs, SMP topology, posted interrupts, alternatives, and cpufeatures. Risks include early-boot ordering, APIC mode mismatch, x2APIC register exclusions, offline CPU/NMI behavior, and static-call replacement correctness. Test signals are indirect through SMP boot, interrupt delivery, x2APIC, CPU hotplug, and APIC selftests/boot logs.
