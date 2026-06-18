
# sources/distributed-fs/ceph-client/arch/x86/include/asm/doublefault.h

Purpose: double-fault initialization and shim declarations.

Important APIs and control flow: `doublefault_init_cpu_tss()` is declared on 32-bit and is a no-op inline on other builds. `doublefault_shim()` is declared `asmlinkage` and `__noreturn` for the low-level double-fault path.

State, dependencies, and risks: state includes the 32-bit double-fault TSS/stack setup and fatal exception path. Dependencies include entry assembly and descriptor setup. Risks include bad TSS setup causing triple faults, stack exhaustion, and no-return control flow assumptions. Test signals are fault-injection/entry tests and 32-bit boot coverage.
