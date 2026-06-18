## `sources/distributed-fs/ceph-client/arch/x86/include/asm/acrn.h`

Purpose: x86 ACRN hypervisor guest interface definitions and inline hypercall helpers.

Important APIs and macros: defines ACRN CPUID leaves for features and timing info, privileged VM feature bit, interrupt handler registration functions, `acrn_cpuid_base()`, `acrn_get_tsc_khz()`, and `acrn_hypercall0/1/2()`.

Control flow: CPUID base detection checks the generic hypervisor CPU feature and searches for the ACRN signature. Hypercall helpers move the hypercall ID into `r8d`, pass up to two arguments in `rdi/rsi`, execute `vmcall`, and return `rax`.

State and persistence: no private state. Registered interrupt handlers are managed by implementation code elsewhere.

Dependencies and integration points: x86 CPUID helpers, ACRN platform drivers, interrupt handling, and ACRN hypercall ABI.

Risks: inline asm ABI is strict; wrong clobbers or argument registers break all ACRN hypercalls. `acrn_get_tsc_khz()` assumes the timing CPUID leaf is valid after ACRN detection.

Test signals: ACRN guest boot, CPUID feature detection, interrupt handler registration/removal, and hypercall smoke tests.
