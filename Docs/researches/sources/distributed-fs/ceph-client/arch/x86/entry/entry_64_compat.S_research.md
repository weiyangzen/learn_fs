## sources/distributed-fs/ceph-client/arch/x86/entry/entry_64_compat.S

Purpose: provides 32-bit compatibility syscall assembly entry on a 64-bit kernel for `SYSENTER`, compat `SYSCALL`, and legacy `int $0x80` dispatch. It converts the quirky hardware entry conventions into kernel `pt_regs` and routes to C helpers in `syscall_32.c`.

Important APIs/functions: `entry_SYSENTER_compat`, `entry_SYSCALL_compat`, `sysret32_from_system_call`, `entry_SYSRETL_compat_unsafe_stack`, `int80_emulation`, and labels consumed by unwind/entry validation. Dependencies include `calling.h`, `asm-offsets`, segment constants, `nospec-branch`, CR3 switching macros, and the C functions `do_SYSENTER_32()`, `do_fast_syscall_32()`, and `do_int80_emulation()`.

Control flow: `SYSENTER` swaps GS, switches CR3, creates a partially synthetic frame because hardware did not save RIP/RSP/RFLAGS, clears/fixes flags such as NT/AC/TF, applies branch mitigations, and calls `do_SYSENTER_32()`. Compat `SYSCALL` stashes user ESP, builds a frame with user CS/SS and saved RCX/R11, calls `do_fast_syscall_32()`, then attempts the `SYSRETL` path if C validation succeeds. The `int80_emulation` stub performs BHB clearing before entering C.

State/persistence: it mutates user-visible return register state, saved frame fields, GS, CR3, and trampoline-stack exit state. It intentionally zeroes `r8-r10` before `sysretl` to avoid leaking kernel state.

Integration points: the 32-bit vDSO `__kernel_vsyscall`, IA32 emulation, `syscall_32.c`, PTI, Xen PV, BHI/IBRS mitigations, and the shared 64-bit user-return path in `entry_64.S`.

Risks: compat syscall ABI depends on exact register preservation, especially EBP/ESP for the vDSO path. Returning via `SYSRETL/SYSEXIT` requires strict CS/SS/IP/flag checks; otherwise IRET must be used. Test signals include 32-bit userspace syscall tests on Intel and AMD, ptrace signal restart tests, Android/Bionic compatibility cases, `ia32_emulation` toggles, objtool checks, and Xen PV/compat boot coverage.
