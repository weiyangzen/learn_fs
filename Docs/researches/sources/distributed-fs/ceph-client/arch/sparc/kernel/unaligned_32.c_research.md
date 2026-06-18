<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/unaligned_32.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/unaligned_32.c

## Purpose
Implements SPARC32 C-side handling for memory-address-not-aligned traps, emulating supported kernel integer accesses and signaling user unaligned accesses.

## Important APIs, Types, And Functions
Defines `enum direction`, instruction decoders `decode_direction`, `decode_access_size`, `decode_signedness`, register helpers `fetch_reg`, `safe_fetch_reg`, `fetch_reg_addr`, address helpers `compute_effective_address` and `safe_compute_effective_address`, `kernel_unaligned_trap`, and `user_unaligned_trap`. It calls assembly helpers `do_int_load` and `__do_int_store`.

## Control Flow
Kernel traps decode the instruction, reject floating-point and atomic/swap accesses, compute the effective address after flushing register windows if needed, record a perf alignment fault, and emulate integer load or store. If byte-wise emulation faults, `kernel_mna_trap_fault` searches exception tables and either redirects to a fixup or oopses. User traps compute a safe best-effort fault address and send `SIGBUS` with `BUS_ADRALN`.

## State And Persistence
The handler mutates `pt_regs` PC/NPC to advance successful emulation or to branch to exception-table fixups. It can read/write stack-resident register windows and touched memory but keeps no global state.

## Dependencies And Integration Points
Integrated with SPARC32 trap-table `mna_handler`, register-window mechanics, perf software counters, exception tables, uaccess, and `una_asm_32.S`.

## Risks And Edge Cases
Unsafe register-window access is acceptable only for kernel-mode emulation; user-facing effective-address calculation uses guarded loads. Unsupported floating-point or atomic unaligned kernel accesses panic. Partial byte-wise stores may occur before a fault, so correctness depends on exception semantics matching existing kernel assumptions.

## Test Signals
Signals include kernel tests or fault injection for unaligned integer loads/stores, userspace unaligned access returning `SIGBUS`, exception-table fixups for faulting kernel uaccess, and perf alignment-fault counter increments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/unaligned_32.c -->
