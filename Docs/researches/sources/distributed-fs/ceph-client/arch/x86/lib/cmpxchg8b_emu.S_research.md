# sources/distributed-fs/ceph-client/arch/x86/lib/cmpxchg8b_emu.S

Purpose: emulates 64-bit `cmpxchg8b` operations on 32-bit x86 for CPUs or contexts without direct support, including normal memory and per-CPU memory variants.

Important APIs/functions: conditionally defines and exports `cmpxchg8b_emu` when `CONFIG_X86_CX8` is disabled. Also defines `this_cpu_cmpxchg8b_emu` except under UML. Inputs are `%esi` pointer, `%edx:%eax` old value, `%ecx:%ebx` new value. Success/failure is returned via ZF in flags and actual memory is returned in `%edx:%eax` on failure.

Control flow: both variants push flags, disable interrupts, compare low and high 32-bit halves, write new halves on exact match, set ZF in saved flags, restore flags, and return. Failure paths reload current memory and clear ZF.

State and persistence behavior: modifies target 8-byte memory and transient interrupt state. No persistent globals.

Dependencies/integration points: used by 32-bit atomic/per-CPU code and exported for non-CX8 builds. Relies on x86 per-CPU addressing macros, processor flags, exception-free memory accesses, and Linux symbol exports.

Risks: not lock-prefixed, so safety is limited to UP/local-interrupt serialization for the non-CX8 emulation and per-CPU contexts. NMI races can observe or interleave partial operations. Callers must not use it as a general SMP atomic primitive unless configuration guarantees make that safe.

Test signals: non-CX8 32-bit build/link coverage, atomic cmpxchg success/failure tests, per-CPU cmpxchg tests, and interrupt/NMI call-site audits.
