# sources/distributed-fs/ceph-client/arch/x86/lib/msr-reg.S

Purpose: implements safe MSR read/write helpers that take and update an eight-element general-purpose register array, returning `0` or `-EIO` instead of faulting on MSR exceptions.

Important APIs/functions: macro `op_safe_regs` generates `rdmsr_safe_regs` and `wrmsr_safe_regs`. The register array layout is `u32 gprs[eax, ecx, edx, ebx, esp, ebp, esi, edi]`. 64-bit and 32-bit implementations differ in stack/register handling but share the same logical ABI.

Control flow: each generated function saves callee registers, loads MSR input registers from the array, executes `rdmsr` or `wrmsr` at label `1`, then stores resulting register values back to the array and returns the saved return code. An exception table entry catches faults at the MSR instruction, sets return code to `-EIO`, and jumps to the common store/return path.

State and persistence behavior: reads or writes CPU MSR state and updates the caller-provided register array with post-instruction register values. No global memory state.

Dependencies/integration points: used by low-level MSR access code and exported via `msr-reg-export.c`. Depends on Linux exception tables, x86 MSR instructions, calling conventions, and CFI/linkage annotations on 64-bit.

Risks: MSR faults must be contained reliably; otherwise invalid MSR access can oops the kernel. Stack layout is subtle, especially on 32-bit where the return code and original pointer are staged on the stack. The array layout is ABI-like and must match declarations/users.

Test signals: MSR safe-access tests on valid and invalid MSRs, 32-bit and 64-bit build coverage, module link tests, and exception table validation.
