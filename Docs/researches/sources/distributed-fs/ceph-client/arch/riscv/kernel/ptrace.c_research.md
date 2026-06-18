<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/ptrace.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/ptrace.c

Purpose: Implements RISC-V ptrace register access, regset views, kernel stack register queries, vector and CFI regsets, compat regsets, and architecture ptrace request dispatch.

Important APIs/types/functions: Provides GPR/FPR/vector regset get/set helpers, `tagged_addr_ctrl_get/set()`, `riscv_cfi_get/set()`, `riscv_user_regset`, `update_regset_vector_info()`, `regs_query_register_offset()`, `regs_get_kernel_stack_nth()`, `ptrace_disable()`, `arch_ptrace()`, compat GPR regsets, `compat_arch_ptrace()`, and `task_user_regset_view()`.

Control flow: Generic ptrace requests are routed to user-regset helpers. GPR/FPR paths copy `pt_regs` and FP state. Vector access validates vector availability, allocates/copies vstate including datap, rejects invalid vector CSR combinations, and reports active size dynamically. CFI and tagged-address regsets delegate to per-task control helpers.

State and persistence: Ptrace mutates `pt_regs`, `thread.fstate`, `thread.vstate`, tagged-address controls, and user CFI state. Regset metadata is read-mostly but vector size is updated once after hardware VLEN discovery.

Dependencies and integration points: Integrates with ELF core dumps, GDB, signal frame state, vector code, user CFI, compat task mode, and generic `user_regset` infrastructure.

Risks: User-supplied vector CSR state can be inconsistent with hardware constraints; the validation path protects against bad `vtype`, `vl`, `vstart`, and `vcsr`. Regset offsets must match `pt_regs` or debuggers and crash dumps misread state.

Test signals: PTRACE_GETREGSET/SETREGSET for GPR/FPR/vector/CFI/tagged controls, compat tracing, core dump note inspection, invalid vector CSR injection, and ptrace detach clearing single-step state.

Source read size: 637 lines, 16743 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/ptrace.c -->
