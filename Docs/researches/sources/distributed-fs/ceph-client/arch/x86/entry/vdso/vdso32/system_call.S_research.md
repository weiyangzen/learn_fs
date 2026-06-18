## sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso32/system_call.S

Purpose: implements the 32-bit vDSO `__kernel_vsyscall` AT_SYSINFO entry for fast 32-bit syscalls.

Important symbols: `__kernel_vsyscall`, `int80_landing_pad`, `SYSENTER_SEQUENCE`, `SYSCALL_SEQUENCE`, and alternatives controlled by `X86_FEATURE_SYSFAST32` and `X86_FEATURE_SYSCALL32`.

Control flow: if fast 32-bit syscall support is absent, the patched path uses `int $0x80; ret`. Otherwise it saves ECX/EDX/EBP with CFI, reshuffles stack/register state so SYSENTER/SYSCALL can preserve enough information, executes the selected fast instruction, falls back through `int $0x80` at `int80_landing_pad`, then restores registers and returns.

State/persistence: no writable state; the text is patched by alternatives and its landing-pad offset is used by kernel validation.

Integration points: `entry_64_compat.S`, `syscall_32.c` fast return validation, AT_SYSINFO auxv, Android legacy compatibility, and vdso32 symbol versioning.

Risks: user code historically hardcoded this sequence, so instruction layout is ABI-sensitive. Kernel fast-return validation assumes the landing pad symbol. Test signals include 32-bit syscall benchmarks, old Android/Bionic compatibility, CPU feature alternative patch checks, and ptrace/signal restart through the landing pad.
