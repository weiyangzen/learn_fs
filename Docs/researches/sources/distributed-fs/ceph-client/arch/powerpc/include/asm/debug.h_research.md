## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/debug.h

Purpose: declares PowerPC debugger hook function pointers and safe inline dispatch wrappers.

Important APIs/types/functions: optional hook pointers include `__debugger`, `__debugger_ipi`, `__debugger_bpt`, `__debugger_sstep`, `__debugger_iabr_match`, `__debugger_break_match`, and `__debugger_fault_handler`. `DEBUGGER_BOILERPLATE()` generates wrappers returning zero when hooks are absent.

Control flow: with debugger or kexec support, each wrapper tests the corresponding function pointer with `unlikely()` and calls it if installed. Without support, all wrappers are inline no-ops.

State and persistence: global hook pointers persist as debugger registration state. The header only reads them.

Dependencies and integration: includes hardware breakpoint definitions and integrates with exception handlers, KGDB/xmon-style debuggers, kexec crash paths, and breakpoint/fault handling.

Risks and test signals: hooks execute in exception contexts, so null checks and calling conventions are critical. Test signals include debugger breakpoint/single-step/IPI tests, kexec crash entry, builds without debugger support, and hardware breakpoint exception handling.
