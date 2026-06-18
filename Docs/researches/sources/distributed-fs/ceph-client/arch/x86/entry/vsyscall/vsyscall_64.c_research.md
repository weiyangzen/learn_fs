## sources/distributed-fs/ceph-client/arch/x86/entry/vsyscall/vsyscall_64.c

Purpose: emulates or exposes the legacy fixed-address x86-64 vsyscall ABI for `gettimeofday`, `time`, and `getcpu`.

Important APIs/state: `vsyscall_mode` (`EMULATE`, `XONLY`, `NONE`), `vsyscall_setup()`, `warn_bad_vsyscall()`, `addr_to_vsyscall_nr()`, `write_ok_or_segv()`, `__emulate_vsyscall()`, `emulate_vsyscall_pf()`, `emulate_vsyscall_gp()`, `get_gate_vma()`, `in_gate_area()`, `in_gate_area_no_mm()`, `set_vsyscall_pgtable_user_bits()`, and `map_vsyscall()`.

Control flow: boot parameter parsing selects mode and disables LASS if necessary for emulation. Fault handlers admit only user instruction-fetch faults to vsyscall addresses, map the fixed address to a vsyscall number, validate return stack and output pointers, run seccomp checks, call the corresponding native syscall implementation, and emulate `ret` by popping the caller from user stack into RIP.

State/persistence: `vsyscall_mode` is read-only after init; `gate_vma` models the pseudo mapping; page-table user bits and fixmap state persist globally when emulation is enabled.

Integration points: page fault and GP handlers, seccomp, signal delivery, fixed mappings, ptrace gate VMA, LASS, and `vsyscall_trace.h`.

Risks: fixed-address ABI weakens ASLR, so mode handling and fault filtering are security-sensitive. Pointer faults intentionally become SIGSEGV to match hardware behavior. Test signals include `vsyscall=none/xonly/emulate`, seccomp mutation tests, bad stack/pointer tests, LASS behavior, ptrace gate-area checks, and legacy glibc workloads.
