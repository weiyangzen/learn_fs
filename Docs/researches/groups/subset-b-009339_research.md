# subset-b-009339 grouped research

This grouped report covers the exact subset-b-009339 source manifest. Each source file section is delimited for deterministic reconciliation into source-tree-aligned per-file research documents.


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x32/syscallent.h -->
# sources/test-tools/strace/src/linux/x32/syscallent.h

Purpose: X32 ABI syscall dispatch table. It maps x32 syscall numbers, including entries starting at the x32 compatibility range, to argument counts, tracing flag classes, decoder symbols, and display names.
Important APIs/types/functions: declarative `sysent` initializer rows using `SEN(...)`, flags such as `TD`, `TF`, `TP`, `TM`, `CST`, `CC`, and common include `syscallent-common.h`.
Control flow: there is no executable flow; the table is indexed after personality detection selects x32. Missing or reserved numbers fall back to common strace table handling.
State and persistence behavior: static read-only build data; no runtime state. Dependencies and integration points: consumed by syscall lookup, x86_64/x32 personality plumbing, and decoder implementations named by `SEN`.
Risks: wrong numbering, flags, or compat annotations cause incorrect argument decoding, path/process filtering, or injected-fault behavior. Test signals: x32 syscall-number smoke tests, generated table diff checks, and syscall output tests for high-risk entries such as `execveat`, aio, and vector I/O.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x32/syscallent.h -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x32/syscallent1.h -->
# sources/test-tools/strace/src/linux/x32/syscallent1.h

Purpose: personality table shim that reuses the i386 syscall table for the secondary x32/i386 personality lane.
Important APIs/types/functions: single include of `../i386/syscallent.h`.
Control flow: no local logic; compilation aliases the i386 table into this personality slot. State and persistence behavior: static build-time include only.
Dependencies and integration points: depends on x86 personality dispatch and i386 syscall table maintenance. Risks: if the personality ordering changes, this include could bind the wrong ABI table. Test signals: mixed x86_64/x32/i386 trace tests should verify i386 numbers decode through personality 1.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x32/syscallent1.h -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x32/userent.h -->
# sources/test-tools/strace/src/linux/x32/userent.h

Purpose: x32 user-register-name table shim.
Important APIs/types/functions: includes `../x86_64/userent.h`, sharing x86_64 register constants and names.
Control flow: no executable logic. State and persistence behavior: build-time alias only.
Dependencies and integration points: used by register printing and `-e inject`/ptrace diagnostics that reference architecture registers. Risks: x32-specific register naming differences would be hidden by the alias. Test signals: register dump and syscall tampering tests under x32 should show expected x86 register names.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x32/userent.h -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/arch_defs_.h -->
# sources/test-tools/strace/src/linux/x86_64/arch_defs_.h

Purpose: declares x86_64 architecture capabilities and personality metadata.
Important APIs/types/functions: defines `SUPPORTED_PERSONALITIES` as three lanes, names/designators for 64/i386/x32, audit-arch pairs, `__X32_SYSCALL_BIT`, old mmap/select and UID16 support, and x32 msqid sizing.
Control flow: no runtime flow; included by common arch setup to size tables and select behavior. State and persistence behavior: compile-time constants only.
Dependencies and integration points: used by syscall table loading, audit-arch matching, personality printing, and compatibility syscall code. Risks: incorrect personality order breaks table indexing across many files. Test signals: startup arch probes and mixed-personality traces should report 64 bit, 32 bit, and x32 accurately.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/arch_defs_.h -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/arch_fpregset.c -->
# sources/test-tools/strace/src/linux/x86_64/arch_fpregset.c

Purpose: decodes x86_64 `NT_FPREGSET` floating-point register-set payloads for ptrace/regset printing.
Important APIs/types/functions: `arch_decode_fpregset`, `struct_fpregset`, `umoven_or_printaddr`, `PRINT_FIELD_X`, `PRINT_FIELD_ARRAY_UPTO`, and mpers fallback to i386 for `MPERS_IS_m32`.
Control flow: rejects zero or non-8-byte-aligned sizes, fetches up to the known structure size, prints fields only when present by `offsetof`, and emits `more_data_follows` for larger kernel payloads.
State and persistence behavior: stateless; only reads tracee memory. Dependencies and integration points: paired with `arch_fpregset.h` and generic regset decoding.
Risks: size/offset mistakes can hide partial regsets or over-read changed kernel layouts. Test signals: ptrace regset tests with full, partial, and oversized fpregset buffers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/arch_fpregset.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/arch_fpregset.h -->
# sources/test-tools/strace/src/linux/x86_64/arch_fpregset.h

Purpose: defines the native x86_64 floating-point regset layout used by `arch_fpregset.c`.
Important APIs/types/functions: `struct_fpregset` fields for x87 control/status, instruction/data pointers, MXCSR, x87 stack space, XMM space, and padding; `HAVE_ARCH_FPREGSET` feature macro.
Control flow: preprocessor selects i386 layout under `MPERS_IS_m32`, otherwise guards the local definition. State and persistence behavior: type declarations only.
Dependencies and integration points: consumed by regset decoders and ptrace output. Risks: layout drift relative to kernel/user headers corrupts printed offsets. Test signals: compile-time size checks and regset decoding tests across native and m32 builds.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/arch_fpregset.h -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/arch_get_personality.c -->
# sources/test-tools/strace/src/linux/x86_64/arch_get_personality.c

Purpose: derives strace personality from `PTRACE_GET_SYSCALL_INFO` audit architecture and syscall number.
Important APIs/types/functions: `get_personality_from_syscall_info`, `struct_ptrace_syscall_info`, `AUDIT_ARCH_I386`, `__X32_SYSCALL_BIT`, and x32 build guard.
Control flow: starts as i386 when audit arch says i386; otherwise requires entry/seccomp syscall-info operations, inspects x32 syscall bit for non-negative syscall numbers, and returns -1 for unsupported operation states.
State and persistence behavior: stateless helper. Dependencies and integration points: used when syscall info is available instead of older register-based personality selection.
Risks: syscall number -1 under seccomp must not be misclassified as x32. Test signals: PTRACE_SYSCALL_INFO tests for x86_64, i386, x32, and seccomp errno cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/arch_get_personality.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/arch_kvm.c -->
# sources/test-tools/strace/src/linux/x86_64/arch_kvm.c

Purpose: architecture-specific KVM ioctl printers for x86 general and special registers.
Important APIs/types/functions: `arch_print_kvm_regs`, `arch_print_kvm_sregs`, segment/dtable helpers, `struct kvm_regs`, `struct kvm_sregs`, and `PRINT_FIELD_*` macros.
Control flow: compiled only when kernel headers expose the relevant KVM structs. Register printers emit a shortened view in abbreviated mode and full segment/control-register state otherwise.
State and persistence behavior: stateless formatting of ioctl buffers. Dependencies and integration points: included by generic KVM ioctl decoder.
Risks: kernel header feature guards and abbreviated branches can miss fields after structure growth. Test signals: KVM_GET_REGS/SREGS ioctl fixtures in abbreviated and verbose modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/arch_kvm.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/arch_prstatus_regset.c -->
# sources/test-tools/strace/src/linux/x86_64/arch_prstatus_regset.c

Purpose: decodes x86_64 `NT_PRSTATUS` general register-set data.
Important APIs/types/functions: `arch_decode_prstatus_regset`, `struct_prstatus_regset`, partial-size checks, `PRINT_FIELD_X`, and i386 mpers include.
Control flow: rejects zero/non-8-byte-aligned sizes, fetches the bounded payload, prints registers in kernel layout order only when the supplied size reaches each field, and marks trailing unknown data.
State and persistence behavior: stateless tracee-memory read. Dependencies and integration points: used by ptrace regset display and `arch_prstatus_regset.h`.
Risks: field order must match kernel ABI exactly; partial-size logic can hide valid trailing fields if offsets change. Test signals: native x86_64 regset fixtures plus oversized and truncated payload tests.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/arch_prstatus_regset.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/arch_prstatus_regset.h -->
# sources/test-tools/strace/src/linux/x86_64/arch_prstatus_regset.h

Purpose: declares the x86_64 general-purpose register-set structure used for PRSTATUS decoding.
Important APIs/types/functions: `struct_prstatus_regset` with `r15..gs` fields in kernel order and `HAVE_ARCH_PRSTATUS_REGSET`.
Control flow: preprocessor selects i386 layout for `MPERS_IS_m32`, otherwise guards the native structure. State and persistence behavior: no mutable state.
Dependencies and integration points: consumed by `arch_prstatus_regset.c` and generic regset code. Risks: any layout mismatch affects syscall number, PC/SP, and register output. Test signals: compile and trace tests comparing printed register sets with ptrace data.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/arch_prstatus_regset.h -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/arch_regs.c -->
# sources/test-tools/strace/src/linux/x86_64/arch_regs.c

Purpose: defines x86_64/i386 register storage and macros for generic ptrace register collection.
Important APIs/types/functions: `struct i386_user_regs_struct`, `x86_regs_union`, `x86_io`, `ARCH_REGS_FOR_GETREGSET`, `ARCH_IOVEC_FOR_GETREGSET`, `ARCH_PC_REG`, and `ARCH_SP_REG`.
Control flow: no functions; macros choose i386 or x86_64 PC/SP based on returned iovec length. State and persistence behavior: static register union updated by ptrace reads.
Dependencies and integration points: used by syscall entry/exit, argument extraction, error handling, and stack tracing.
Risks: i386 struct size is the ABI discriminator; overflow or wrong layout breaks mixed-personality tracing. Test signals: register-fetch tests for 64-bit and 32-bit tracees.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/arch_regs.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/arch_regs.h -->
# sources/test-tools/strace/src/linux/x86_64/arch_regs.h

Purpose: supplies numeric x86_64 register indexes for `upoke`/`upeek` operations.
Important APIs/types/functions: constants `R15` through `GS`, including `RAX`, `ORIG_RAX`, `RIP`, and `RSP`.
Control flow: no executable logic. State and persistence behavior: compile-time constants only.
Dependencies and integration points: used by `set_error.c`, `set_scno.c`, and register tampering paths. Risks: indexes are byte-scaled by callers, so a wrong ordinal writes the wrong tracee register. Test signals: syscall injection and syscall-number rewrite tests.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/arch_regs.h -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/arch_rt_sigframe.c -->
# sources/test-tools/strace/src/linux/x86_64/arch_rt_sigframe.c

Purpose: reuses the i386 runtime signal-frame decoder for x86_64 where appropriate.
Important APIs/types/functions: includes `../i386/arch_rt_sigframe.c`.
Control flow: no local logic; all behavior is delegated to the shared implementation. State and persistence behavior: none locally.
Dependencies and integration points: signal-frame decoding in `rt_sigreturn` handling. Risks: delegated decoder must handle x86_64-specific frame shape through included headers. Test signals: rt_sigreturn/signal frame tests for native and compat processes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/arch_rt_sigframe.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/arch_sigreturn.c -->
# sources/test-tools/strace/src/linux/x86_64/arch_sigreturn.c

Purpose: wires x86_64 signal-return handling to the shared i386 implementation.
Important APIs/types/functions: includes `../i386/arch_sigreturn.c`.
Control flow: no local functions. State and persistence behavior: none locally.
Dependencies and integration points: integrates with syscall decoders for `sigreturn`/`rt_sigreturn` and architecture frame definitions. Risks: include-level coupling can mask x86_64-specific changes. Test signals: signal-return decoding tests under native, i386, and x32 personalities.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/arch_sigreturn.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/asm_stat.h -->
# sources/test-tools/strace/src/linux/x86_64/asm_stat.h

Purpose: supplies a corrected x32 `struct stat` view while otherwise using generic stat definitions.
Important APIs/types/functions: include guard, temporary `stat` redirection for x32 ILP32, generic `asm_stat.h`, and replacement `struct stat` with kernel-sized fields.
Control flow: preprocessor-only selection. State and persistence behavior: type declarations only.
Dependencies and integration points: stat-family syscall decoders and x32 builds with older kernel headers. Risks: wrong x32 stat layout corrupts file metadata output. Test signals: x32 stat/lstat/fstat output tests with large inode and timestamp values.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/asm_stat.h -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/get_error.c -->
# sources/test-tools/strace/src/linux/x86_64/get_error.c

Purpose: converts architecture return registers into strace success or errno state on x86.
Important APIs/types/functions: `arch_get_error`, `is_negated_errno`, `x86_io`, `i386_regs.eax`, `x86_64_regs.rax`, `tcp->u_rval`, and `tcp->u_error`.
Control flow: sign-extends i386 `eax`, keeps x86_64/x32 64-bit `rax`, then treats negated errno values as errors when requested.
State and persistence behavior: writes only per-syscall `tcb` return fields. Dependencies and integration points: syscall exit path and `negated_errno.h`.
Risks: x32 needs 64-bit returns for calls such as llseek; truncation would be visible. Test signals: success/error return tests for i386, x86_64, and x32.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/get_error.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/get_scno.c -->
# sources/test-tools/strace/src/linux/x86_64/get_scno.c

Purpose: extracts syscall number and selects x86_64, i386, or x32 personality from registers.
Important APIs/types/functions: `arch_get_scno`, `x86_io.iov_len`, `orig_eax`, `orig_rax`, `__X32_SYSCALL_BIT`, and `update_personality`.
Control flow: i386 is detected by regset size; otherwise the x32 syscall bit selects x32 unless the number is -1 from seccomp errno handling. x32-native builds reject unsupported 64-bit mode.
State and persistence behavior: updates `tcp->scno` and current personality. Dependencies and integration points: central syscall dispatch path.
Risks: personality misclassification points at the wrong syscall table and argument ABI. Test signals: mixed-ABI exec tests and seccomp `orig_rax == -1` regression tests.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/get_scno.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/get_syscall_args.c -->
# sources/test-tools/strace/src/linux/x86_64/get_syscall_args.c

Purpose: fills `tcp->u_arg` from x86 syscall argument registers.
Important APIs/types/functions: `arch_get_syscall_args`, `tcp_sysent`, `COMPAT_SYSCALL_TYPES`, `x86_64_regs`, and `i386_regs`.
Control flow: x86_64/x32 uses `rdi,rsi,rdx,r10,r8,r9`; compat x32 syscalls zero-extend 32-bit arguments; i386 uses `ebx,ecx,edx,esi,edi,ebp` and zero-extends.
State and persistence behavior: writes the current syscall argument array only. Dependencies and integration points: every syscall decoder consumes these values.
Risks: sign extension is intentionally deferred to handlers; handlers that forget `truncate_klong_to_current_wordsize` can misprint signed compat arguments. Test signals: argument-order tests, x32 signed argument tests, and six-argument syscall fixtures.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/get_syscall_args.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/getregs_old.c -->
# sources/test-tools/strace/src/linux/x86_64/getregs_old.c

Purpose: fallback register-fetch path using older `PTRACE_GETREGS` semantics on x86.
Important APIs/types/functions: `get_regs`, `ptrace(PTRACE_GETREGS)`, x86 register union, CS selector logic, and iovec length update.
Control flow: fetches the full x86_64 user register struct, then identifies 32-bit mode from `cs == 0x23` and shrinks `x86_io.iov_len` to the i386 layout when appropriate.
State and persistence behavior: updates static register union and iovec length. Dependencies and integration points: enabled by `getregs_old.h` when GETREGSET is unavailable.
Risks: segment selector heuristics are kernel/ABI sensitive. Test signals: fallback builds or forced old-getregs tests with 64-bit and 32-bit tracees.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/getregs_old.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/getregs_old.h -->
# sources/test-tools/strace/src/linux/x86_64/getregs_old.h

Purpose: declares availability of the old x86 GETREGS fallback path.
Important APIs/types/functions: include guard plus `HAVE_GETREGS_OLD`.
Control flow: no runtime logic. State and persistence behavior: compile-time feature flag only.
Dependencies and integration points: generic register-fetch code conditionally includes `getregs_old.c`. Risks: stale feature wiring could compile fallback unintentionally. Test signals: configure/build tests that disable GETREGSET and still trace x86 syscalls.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/getregs_old.h -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/ioctls_arch0.h -->
# sources/test-tools/strace/src/linux/x86_64/ioctls_arch0.h

Purpose: native x86_64 architecture-specific ioctl number table.
Important APIs/types/functions: declarative rows mapping encoded ioctl request numbers to symbolic names and header origins.
Control flow: no executable flow; ioctl decoder searches generated tables to print known request names. State and persistence behavior: static read-only table.
Dependencies and integration points: consumed by generic ioctl lookup for personality 0. Risks: stale ioctl constants lead to numeric output or wrong names. Test signals: ioctl table generation checks and smoke tests for tty, block, input, and filesystem ioctls.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/ioctls_arch0.h -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/ioctls_arch1.h -->
# sources/test-tools/strace/src/linux/x86_64/ioctls_arch1.h

Purpose: compat i386 ioctl architecture table shim for x86_64 personality 1.
Important APIs/types/functions: includes `../i386/ioctls_arch0.h`.
Control flow: no local logic. State and persistence behavior: build-time alias.
Dependencies and integration points: ioctl decoder under i386 personality. Risks: wrong include would mislabel compat ioctl numbers. Test signals: 32-bit tracee ioctl decoding tests on x86_64 hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/ioctls_arch1.h -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/ioctls_arch2.h -->
# sources/test-tools/strace/src/linux/x86_64/ioctls_arch2.h

Purpose: x32 ioctl architecture table shim for personality 2.
Important APIs/types/functions: includes local `ioctls_arch0.h`, reusing native x86_64 ioctl encodings.
Control flow: no executable logic. State and persistence behavior: build-time alias.
Dependencies and integration points: ioctl decoder under x32 personality. Risks: x32-specific ioctl differences would be missed. Test signals: x32 ioctl decoding tests for pointer-sized structures.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/ioctls_arch2.h -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/ioctls_inc0.h -->
# sources/test-tools/strace/src/linux/x86_64/ioctls_inc0.h

Purpose: native x86_64 generated ioctl include-set shim.
Important APIs/types/functions: includes `../64/ioctls_inc.h`.
Control flow: none. State and persistence behavior: compile-time include only.
Dependencies and integration points: ioctl table generator and decoder. Risks: include-set mismatch omits architecture-visible ioctl constants. Test signals: generated ioctl-table rebuild and native ioctl symbol coverage checks.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/ioctls_inc0.h -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/ioctls_inc1.h -->
# sources/test-tools/strace/src/linux/x86_64/ioctls_inc1.h

Purpose: i386 compat ioctl include-set shim.
Important APIs/types/functions: includes `../i386/ioctls_inc0.h`.
Control flow: none. State and persistence behavior: compile-time include only.
Dependencies and integration points: x86_64 personality 1 ioctl table generation. Risks: missing compat headers reduce symbolic decoding. Test signals: i386 compat ioctl table and trace fixtures.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/ioctls_inc1.h -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/ioctls_inc2.h -->
# sources/test-tools/strace/src/linux/x86_64/ioctls_inc2.h

Purpose: x32 ioctl include-set shim.
Important APIs/types/functions: includes `../x32/ioctls_inc0.h`.
Control flow: no executable logic. State and persistence behavior: compile-time include only.
Dependencies and integration points: x32 ioctl table generation. Risks: x32 ioctl structure-size differences are concentrated here and in generated tables. Test signals: x32 ioctl generation and pointer-size-sensitive ioctl tests.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/ioctls_inc2.h -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/raw_syscall.h -->
# sources/test-tools/strace/src/linux/x86_64/raw_syscall.h

Purpose: provides a minimal inline raw syscall helper for x86_64.
Important APIs/types/functions: `raw_syscall_0`, `kernel_ulong_t`, inline `syscall` assembly, return in `rax`, and clobbers for `memory`, `cc`, `rcx`, `r11`.
Control flow: sets `*err` to zero, invokes syscall number with no arguments, returns raw kernel value. State and persistence behavior: no persistent state; affects CPU registers only.
Dependencies and integration points: low-level strace self-probing paths that need direct syscalls. Risks: assembly constraints must match ABI; no errno conversion is done here. Test signals: raw syscall helper tests for simple zero-argument syscalls.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/raw_syscall.h -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/rt_sigframe.h -->
# sources/test-tools/strace/src/linux/x86_64/rt_sigframe.h

Purpose: declares the x86_64 runtime signal-frame header used by signal-return decoders.
Important APIs/types/functions: `struct_rt_sigframe` with `pretcode` and `ucontext_t`; i386 include fallback under `__i386__`.
Control flow: preprocessor selects native or i386 definition. State and persistence behavior: type declaration only.
Dependencies and integration points: `arch_rt_sigframe.c` and signal frame printers. Risks: incomplete structure intentionally notes more data follows; consumers must not assume full frame coverage. Test signals: signal-delivery and rt_sigreturn decoding tests.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/rt_sigframe.h -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/set_error.c -->
# sources/test-tools/strace/src/linux/x86_64/set_error.c

Purpose: writes synthetic error or success return values back into x86 tracee registers.
Important APIs/types/functions: `arch_set_error`, `arch_set_success`, `tcp->u_error`, `tcp->u_rval`, `i386_regs.eax`, `x86_64_regs.rax`, `upoke`, and `RAX` register offset.
Control flow: chooses i386 or 64-bit return register by current personality, stores local mirror, then pokes the kernel register slot.
State and persistence behavior: mutates tracee register state for injection/tampering. Dependencies and integration points: fault injection and syscall return modification.
Risks: wrong personality or register offset changes the wrong register. Test signals: syscall fault injection tests on i386 and x86_64 personalities.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/set_error.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/set_scno.c -->
# sources/test-tools/strace/src/linux/x86_64/set_scno.c

Purpose: rewrites the x86 syscall number register.
Important APIs/types/functions: `arch_set_scno`, `upoke`, and `ORIG_RAX` register offset.
Control flow: writes the supplied syscall number to `orig_rax` using ptrace. State and persistence behavior: mutates tracee syscall-entry state.
Dependencies and integration points: syscall tampering and injection features. Risks: x32 bit handling is the caller's responsibility; wrong offset breaks syscall rewrite. Test signals: syscall-number injection tests and x32 bit-preservation cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/set_scno.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/shuffle_scno.c -->
# sources/test-tools/strace/src/linux/x86_64/shuffle_scno.c

Purpose: normalizes x86 syscall numbers for table lookup across x86_64, i386, and x32 personalities.
Important APIs/types/functions: `shuffle_scno`, `tcp->scno`, current personality, and `__X32_SYSCALL_BIT`.
Control flow: strips or adjusts architecture-specific syscall-number bits/offsets after personality has been selected. State and persistence behavior: modifies only the current `tcb` syscall number.
Dependencies and integration points: dispatch table indexing before decoder lookup. Risks: off-by-one or missing x32-bit handling selects the wrong `sysent` row. Test signals: table-index tests for x32 high-bit syscalls and normal x86_64 numbers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/shuffle_scno.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/syscallent.h -->
# sources/test-tools/strace/src/linux/x86_64/syscallent.h

Purpose: primary x86_64 syscall table for native personality 0.
Important APIs/types/functions: `sysent` initializer rows with argument counts, classification flags, `SEN` decoder selectors, and names; includes `syscallent-common.h`.
Control flow: no executable code; indexed by normalized syscall number during syscall dispatch. State and persistence behavior: static build artifact.
Dependencies and integration points: all x86_64 syscall decoding depends on correct entries and flags. Risks: stale syscall additions, wrong argument count, or missing flags affect filtering and output. Test signals: generated syscall table diff checks and syscall-specific tests through newest entries such as `statx`, `rseq`, and `uretprobe`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/syscallent.h -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/syscallent1.h -->
# sources/test-tools/strace/src/linux/x86_64/syscallent1.h

Purpose: x86_64 personality 1 syscall table shim for i386 tracees.
Important APIs/types/functions: includes `../i386/syscallent.h`.
Control flow: no local logic; table dispatch is delegated to i386 entries. State and persistence behavior: static include alias.
Dependencies and integration points: selected after register-size/personality detection. Risks: personality ordering mistakes map 32-bit processes to the wrong syscall table. Test signals: 32-bit tracee syscall-decoding coverage on x86_64 builds.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/syscallent1.h -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/syscallent2.h -->
# sources/test-tools/strace/src/linux/x86_64/syscallent2.h

Purpose: x86_64 personality 2 syscall table shim for x32 tracees.
Important APIs/types/functions: includes `../x32/syscallent.h`.
Control flow: no executable logic. State and persistence behavior: static include alias.
Dependencies and integration points: selected when `__X32_SYSCALL_BIT` identifies x32. Risks: x32 table drift causes wrong compat decoding. Test signals: x32 syscall smoke tests and mixed-personality exec tracing.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/syscallent2.h -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/userent.h -->
# sources/test-tools/strace/src/linux/x86_64/userent.h

Purpose: maps x86_64 and inherited i386 user-register offsets to printable names.
Important APIs/types/functions: includes `../i386/userent0.h` then adds x86_64-specific names such as `r15`, `orig_rax`, `rip`, segment bases, and segment registers.
Control flow: declarative table only. State and persistence behavior: static lookup data.
Dependencies and integration points: register printing, poking, and diagnostics. Risks: wrong offsets make register names misleading and can affect user-facing tampering diagnostics. Test signals: register-name lookup tests for x86_64 and compat registers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/userent.h -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/xtensa/arch_defs_.h -->
# sources/test-tools/strace/src/linux/xtensa/arch_defs_.h

Purpose: declares Xtensa audit architecture metadata.
Important APIs/types/functions: `PERSONALITY0_AUDIT_ARCH { AUDIT_ARCH_XTENSA, 0 }`.
Control flow: compile-time metadata only. State and persistence behavior: no mutable state.
Dependencies and integration points: personality/audit matching in the generic Linux backend. Risks: wrong audit arch prevents correct syscall-info classification. Test signals: Xtensa build/config tests and audit-arch matching tests.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/xtensa/arch_defs_.h -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/xtensa/arch_regs.c -->
# sources/test-tools/strace/src/linux/xtensa/arch_regs.c

Purpose: defines Xtensa register storage and PC/SP macros.
Important APIs/types/functions: static `struct user_pt_regs xtensa_regs`, `ARCH_REGS_FOR_GETREGS`, `ARCH_PC_REG`, and windowed-stack `ARCH_SP_REG` expression.
Control flow: no functions; SP resolves through `windowbase * 4 + 1`. State and persistence behavior: static register snapshot updated by ptrace.
Dependencies and integration points: argument extraction, return handling, and stack traces. Risks: Xtensa register windows make incorrect windowbase handling especially visible. Test signals: Xtensa syscall and stack-pointer decode tests.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/xtensa/arch_regs.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/xtensa/get_error.c -->
# sources/test-tools/strace/src/linux/xtensa/get_error.c

Purpose: converts Xtensa return register state into strace return/error fields.
Important APIs/types/functions: `arch_get_error`, `is_negated_errno`, `xtensa_regs.a`, and status register index `windowbase * 4 + 2`.
Control flow: reads the current window's a2-equivalent register and treats negated errno values as errors when requested. State and persistence behavior: writes `tcp->u_rval` and `tcp->u_error` only.
Dependencies and integration points: syscall exit processing. Risks: wrong window register selection corrupts every return value. Test signals: Xtensa success/error syscall traces across register-window configurations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/xtensa/get_error.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/xtensa/get_scno.c -->
# sources/test-tools/strace/src/linux/xtensa/get_scno.c

Purpose: obtains the Xtensa syscall number.
Important APIs/types/functions: `arch_get_scno`, `upeek`, `SYSCALL_NR`, and `tcp->scno`.
Control flow: peeks the syscall-number pseudo-register and returns -1 on ptrace failure or 1 on success. State and persistence behavior: updates only current `tcb` syscall number.
Dependencies and integration points: syscall dispatch. Risks: wrong `SYSCALL_NR` constant prevents table lookup. Test signals: Xtensa syscall-number extraction tests.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/xtensa/get_scno.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/xtensa/get_syscall_args.c -->
# sources/test-tools/strace/src/linux/xtensa/get_syscall_args.c

Purpose: extracts Xtensa syscall arguments from windowed registers.
Important APIs/types/functions: `arch_get_syscall_args`, `xtensa_probe_naregs`, `set_regs`, `n_args`, and register order `{6,3,4,5,8,9}`.
Control flow: probes the number of address registers once by temporarily moving `windowbase`, restores registers, then masks window-relative register indexes while filling `tcp->u_arg`.
State and persistence behavior: caches `naregs_mask` statically and writes per-syscall arguments. Dependencies and integration points: all Xtensa syscall decoders.
Risks: the probe mutates registers temporarily; failed restore would be severe. Test signals: Xtensa argument-order tests and builds with different register-window sizes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/xtensa/get_syscall_args.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/xtensa/ioctls_arch0.h -->
# sources/test-tools/strace/src/linux/xtensa/ioctls_arch0.h

Purpose: Xtensa architecture-specific ioctl request table.
Important APIs/types/functions: declarative ioctl rows mapping encoded request numbers to names/header origins.
Control flow: no executable code; searched by the generic ioctl decoder. State and persistence behavior: static table data.
Dependencies and integration points: ioctl symbolic decoding for Xtensa personality 0. Risks: stale constants lead to numeric or wrong ioctl output. Test signals: ioctl table generation checks and Xtensa ioctl smoke tests.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/xtensa/ioctls_arch0.h -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/xtensa/ioctls_inc0.h -->
# sources/test-tools/strace/src/linux/xtensa/ioctls_inc0.h

Purpose: Xtensa ioctl include-set shim.
Important APIs/types/functions: includes `../32/ioctls_inc.h`, reflecting Xtensa's 32-bit ABI.
Control flow: no local logic. State and persistence behavior: compile-time include only.
Dependencies and integration points: generated ioctl table production. Risks: incorrect word-size include set affects encoded ioctl sizes. Test signals: generated-table diffs and 32-bit ioctl structure-size tests.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/xtensa/ioctls_inc0.h -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/xtensa/raw_syscall.h -->
# sources/test-tools/strace/src/linux/xtensa/raw_syscall.h

Purpose: provides Xtensa inline raw zero-argument syscall helper.
Important APIs/types/functions: `raw_syscall_0`, `kernel_ulong_t`, register variable bound to `a2`, and `syscall` assembly.
Control flow: places the syscall number in `a2`, executes `syscall`, returns `a2`, and leaves errno conversion to callers. State and persistence behavior: no persistent state.
Dependencies and integration points: direct syscall probing in strace runtime. Risks: Xtensa calling convention constraints must remain exact. Test signals: helper smoke tests for a simple zero-argument syscall.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/xtensa/raw_syscall.h -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/xtensa/set_error.c -->
# sources/test-tools/strace/src/linux/xtensa/set_error.c

Purpose: writes synthetic syscall return values into Xtensa registers.
Important APIs/types/functions: `arch_set_error`, `arch_set_success`, `xtensa_regs.a[windowbase * 4 + 2]`, and `set_regs`.
Control flow: stores negative errno or success value into the current window's return register and writes the register set back to the tracee. State and persistence behavior: mutates tracee registers.
Dependencies and integration points: syscall fault injection and tampering. Risks: windowbase miscalculation changes the wrong register. Test signals: Xtensa fault-injection success/error rewrite tests.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/xtensa/set_error.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/xtensa/set_scno.c -->
# sources/test-tools/strace/src/linux/xtensa/set_scno.c

Purpose: rewrites the Xtensa syscall-number pseudo-register.
Important APIs/types/functions: `arch_set_scno`, `upoke`, and `SYSCALL_NR`.
Control flow: pokes the supplied syscall number into the tracee. State and persistence behavior: mutates tracee syscall-entry state.
Dependencies and integration points: syscall injection/tampering. Risks: wrong pseudo-register constant breaks rewrite. Test signals: Xtensa syscall-number tampering tests.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/xtensa/set_scno.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/xtensa/syscallent.h -->
# sources/test-tools/strace/src/linux/xtensa/syscallent.h

Purpose: Xtensa syscall dispatch table.
Important APIs/types/functions: `sysent` rows with argument counts, flags, `SEN` decoder symbols, includes `../32/syscallent-common-32.h` and `syscallent-common.h`.
Control flow: declarative table indexed by `tcp->scno` after `get_scno`. State and persistence behavior: static build-time data.
Dependencies and integration points: Xtensa syscall decoding, filtering, and classification. Risks: wrong numbers/flags produce incorrect output and filtering. Test signals: generated syscall-table checks and Xtensa syscall trace fixtures including architecture-specific early entries `spill` and `xtensa`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/xtensa/syscallent.h -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/xtensa/userent.h -->
# sources/test-tools/strace/src/linux/xtensa/userent.h

Purpose: Xtensa register-name lookup table.
Important APIs/types/functions: entries for `a0..a15`, `pc`, `syscall_nr`, `ar0..ar63`, loop registers, shift amount, windowbase/windowstart, and processor state.
Control flow: declarative lookup table only. State and persistence behavior: static data.
Dependencies and integration points: register display and ptrace diagnostics. Risks: wrong constants make windowed-register diagnostics misleading. Test signals: register-name output tests for general and special Xtensa registers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/xtensa/userent.h -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/lirc_ioctl.c -->
# sources/test-tools/strace/src/lirc_ioctl.c

Purpose: decodes Linux infrared remote control ioctl commands.
Important APIs/types/functions: `lirc_ioctl`, LIRC command constants, `_IOC_DIR`, `umove_or_printaddr`, `lirc_features`, and `lirc_modes` xlats.
Control flow: accepts a whitelist of LIRC get/set commands; read ioctls are decoded on exit, write ioctls on entry; prints feature flags, mode names, hexadecimal transmitter masks, or unsigned values.
State and persistence behavior: stateless tracee-memory read. Dependencies and integration points: called by the central ioctl dispatcher.
Risks: direction-sensitive timing is important because read commands populate the argument on exit. Test signals: LIRC ioctl fixtures for get features, get/set modes, masks, and unknown commands.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/lirc_ioctl.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/list.h -->
# sources/test-tools/strace/src/list.h

Purpose: small intrusive doubly linked-list utility modeled after Linux kernel lists.
Important APIs/types/functions: `struct list_item`, `EMPTY_LIST`, `list_init`, `list_is_empty`, `list_elem`, head/tail/next/prev macros, insert/append/remove/replace helpers, and iteration macros.
Control flow: inline helpers splice circular list links and reset removed/replaced nodes to self-links. `list_is_empty` also treats zeroed uninitialized nodes as empty.
State and persistence behavior: mutates caller-owned embedded list nodes; no allocation. Dependencies and integration points: depends on `containerof` from `macros.h` and is reused by internal strace collections.
Risks: macros assume valid embedded fields and are not thread-safe. Test signals: unit-style insertion/removal/iteration tests, including removal while iterating.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/list.h -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/listen.c -->
# sources/test-tools/strace/src/listen.c

Purpose: decodes the `listen` syscall.
Important APIs/types/functions: `SYS_FUNC(listen)`, `printfd`, and integer backlog printing.
Control flow: prints `sockfd` and `backlog` on entry and returns decoded status. State and persistence behavior: none.
Dependencies and integration points: socket syscall table entry maps to this decoder. Risks: minimal; only fd formatting and signed backlog presentation matter. Test signals: simple listen traces with valid, invalid, and negative backlog values.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/listen.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/listmount.c -->
# sources/test-tools/strace/src/listmount.c

Purpose: decodes the Linux `listmount` syscall and its versioned `mnt_id_req` input structure.
Important APIs/types/functions: `print_mnt_id_req`, `SYS_FUNC(listmount)`, `struct mnt_id_req`, `MNT_ID_REQ_SIZE_VER*`, `print_array`, `listmount_mnt_id`, and `listmount_flags`.
Control flow: on entry it reads `size`, conditionally fetches known fields, prints future nonzero bytes up to a page; on exit it prints returned mount IDs capped by return value, count, and flags.
State and persistence behavior: stateless; only tracee-memory reads. Dependencies and integration points: mount namespace syscall decoders and xlat tables.
Risks: versioned struct sizes and future fields need careful bounds. Test signals: short, v0, v1, oversized, failed, and successful listmount fixtures.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/listmount.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/listns.c -->
# sources/test-tools/strace/src/listns.c

Purpose: decodes the Linux `listns` syscall and versioned namespace request structure.
Important APIs/types/functions: `print_ns_id_req`, `SYS_FUNC(listns)`, `struct ns_id_req`, `ns_type`, `listns_user_ns_id`, and `print_array`.
Control flow: entry prints request size and known fields, including sparse fields only when nonzero, plus future nonzero bytes; exit prints returned namespace IDs capped by return value and requested count.
State and persistence behavior: no persistent state. Dependencies and integration points: namespace/fs syscall decoding and xlat tables.
Risks: future struct growth and size underflow can mislead output if not bounded. Test signals: fixtures for null/short requests, nonzero spare fields, and successful returned arrays.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/listns.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/lookup_dcookie.c -->
# sources/test-tools/strace/src/lookup_dcookie.c

Purpose: decodes `lookup_dcookie`, which maps a kernel dcookie to a path buffer.
Important APIs/types/functions: `SYS_FUNC(lookup_dcookie)`, `printbigval`, `printpathn`, and buffer length/return-value handling.
Control flow: prints the 64-bit cookie on entry; on exit prints either the returned path limited by `u_rval` or the raw buffer address on error, then prints buffer length.
State and persistence behavior: stateless. Dependencies and integration points: syscall table entry and path-printing helpers.
Risks: path length must be bounded by the actual return value to avoid over-reading. Test signals: success, error, and truncated-buffer lookup_dcookie traces.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/lookup_dcookie.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/loop.c -->
# sources/test-tools/strace/src/loop.c

Purpose: decodes loop-device ioctls and loop status/configuration structures.
Important APIs/types/functions: `loop_ioctl`, `decode_loop_info`, `decode_loop_info64`, `decode_loop_config`, mpers `struct_loop_info`, `loop_flags_options`, and `loop_crypt_type_options`.
Control flow: switch by ioctl code; GET operations often wait for exit, SET/CONFIGURE decode entry arguments, fd/numeric/no-arg commands are printed directly, and unknown commands fall back.
State and persistence behavior: stateless tracee-memory reads, with abbreviated output hiding less important fields. Dependencies and integration points: central ioctl dispatcher and mpers type generation.
Risks: old/new loop structs and encryption key sizes are ABI-sensitive. Test signals: LOOP_GET/SET_STATUS, STATUS64, CONFIGURE, fd-changing, and no-argument ioctl fixtures.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/loop.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/lseek.c -->
# sources/test-tools/strace/src/lseek.c

Purpose: decodes `lseek` and legacy `llseek` offset arguments.
Important APIs/types/functions: `SYS_FUNC(lseek)`, `SYS_FUNC(llseek)`, `current_klongsize`, `printnum_int64`, and `whence_codes`.
Control flow: `lseek` sign-extends offsets when kernel long is narrower; `llseek` combines high/low 32-bit words on entry and prints the result pointer plus whence on exit.
State and persistence behavior: no persistent state. Dependencies and integration points: file-position syscall table entries.
Risks: x32 and other mixed long-size ABIs require exact sign/width handling. Test signals: x32 lseek tests, negative offsets, large 64-bit llseek offsets, and failed result-pointer reads.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/lseek.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/lsm.c -->
# sources/test-tools/strace/src/lsm.c

Purpose: decodes Linux Security Module self-attribute and module-list syscalls.
Important APIs/types/functions: `lsm_get_self_attr`, `lsm_set_self_attr`, `lsm_list_modules`, `decode_lsm_ctx_sequence`, `struct lsm_ctx`, `lsm_attrs`, `lsm_flags`, and `lsm_ids`.
Control flow: get/list syscalls save entry-side sizes in `tcb` private data, then decode exit buffers and print changed sizes; set decodes a single context on entry. Sequence decoding walks variable-length `lsm_ctx` records with truncation protection.
State and persistence behavior: per-syscall saved size only. Dependencies and integration points: new Linux LSM syscall table entries.
Risks: variable-length records can be malformed; size-change reporting must match kernel behavior. Test signals: single and multi-context buffers, changed sizes, truncation, failed syscalls, and unknown ids.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/lsm.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/macros.h -->
# sources/test-tools/strace/src/macros.h

Purpose: shared compile-time and utility macros used throughout strace.
Important APIs/types/functions: `ARRAY_SIZE`, `ARRSZ_PAIR`, `STRINGIFY`, `MIN/MAX/CLAMP`, `ROUNDUP`, `containerof`, type-comparison helpers, alignment helpers, and conditional feature macros.
Control flow: preprocessor and compile-time expressions only. State and persistence behavior: no runtime state.
Dependencies and integration points: included by many headers, including `list.h` and mpers headers. Risks: macro double-evaluation and compiler-extension assumptions must stay controlled. Test signals: full build matrix, static assertions, and code paths that exercise array/type macros.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/macros.h -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/map_shadow_stack.c -->
# sources/test-tools/strace/src/map_shadow_stack.c

Purpose: decodes `map_shadow_stack` syscall arguments.
Important APIs/types/functions: `SYS_FUNC(map_shadow_stack)`, `printaddr`, `PRINT_VAL_U`, and `shadow_stack_flags`.
Control flow: prints address, size, and symbolic flags in order and returns decoded status with hex return semantics where the common syscall layer applies it. State and persistence behavior: none.
Dependencies and integration points: memory-management syscall table entry and Linux `mman` constants. Risks: new flag constants need xlat updates. Test signals: map_shadow_stack traces with zero, known, and unknown flags.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/map_shadow_stack.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/mem.c -->
# sources/test-tools/strace/src/mem.c

Purpose: decodes memory-management syscalls such as brk, mmap variants, mprotect, mremap, madvise, mlock, msync, mincore, remap_file_pages, mseal, and powerpc subpage protection.
Important APIs/types/functions: `get_pagesize`, `print_mmap_flags`, `print_mmap`, `SYS_FUNC(mmap*)`, `do_mprotect`, `process_madvise`, `print_mincore_entry`, many `xlat` tables, and `fetch_indirect_syscall_args`.
Control flow: syscall-specific printers emit arguments in kernel ABI order; old mmap fetches an indirect six-word vector; page-offset variants multiply by cached page size; exit-side mincore prints returned residency bits.
State and persistence behavior: caches page size statically; otherwise stateless. Dependencies and integration points: generic syscall dispatch, xlat tables, iovec printers, and architecture capability macros.
Risks: offset units differ by ABI, HPPA madvise constants have old/new meanings, and mincore element count depends on page-size rounding. Test signals: mmap offset tests, old mmap indirect tests, madvise HPPA cases, mincore success/error, mremap flag combinations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/mem.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/membarrier.c -->
# sources/test-tools/strace/src/membarrier.c

Purpose: decodes `membarrier` command, flags, and optional CPU argument.
Important APIs/types/functions: `SYS_FUNC(membarrier)`, `membarrier_cmds`, `membarrier_flags`, and `MEMBARRIER_CMD_FLAG_CPU`.
Control flow: on entry prints command and flags; if the command requires CPU flag, also prints `cpu_id`, otherwise prints the third argument as raw `flags`/reserved value. State and persistence behavior: none.
Dependencies and integration points: syscall table and xlat definitions. Risks: command-specific optional arguments must track kernel API growth. Test signals: query, register, private expedited, CPU-targeted, and unknown flag traces.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/membarrier.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/memfd_create.c -->
# sources/test-tools/strace/src/memfd_create.c

Purpose: decodes `memfd_create` name and flags, including hugetlb page-size encoding.
Important APIs/types/functions: `SYS_FUNC(memfd_create)`, `printpath`, `memfd_create_flags`, `MAP_HUGE_SHIFT`, and huge-page size extraction.
Control flow: prints name string, known flags, unknown bits, and optional huge-page size shift comment/value. State and persistence behavior: stateless; returns fd through syscall return flags.
Dependencies and integration points: file-descriptor syscall decoding and Linux memfd constants. Risks: huge flag encoding overlaps generic flags and needs masking order. Test signals: normal memfd, sealing, hugetlb, huge size, and unknown flag tests.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/memfd_create.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/memfd_secret.c -->
# sources/test-tools/strace/src/memfd_secret.c

Purpose: decodes `memfd_secret` flags.
Important APIs/types/functions: `SYS_FUNC(memfd_secret)`, `kernel_fcntl.h`, and `memfd_secret_flags`.
Control flow: prints symbolic flags for the single argument and marks the return as a file descriptor. State and persistence behavior: none.
Dependencies and integration points: syscall table and fd-return handling. Risks: new flags need xlat updates; unknown bits should remain visible. Test signals: zero, known, and unknown memfd_secret flag traces.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/memfd_secret.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/mknod.c -->
# sources/test-tools/strace/src/mknod.c

Purpose: decodes `mknod` and `mknodat` path, mode, and device arguments.
Important APIs/types/functions: `decode_mknod`, `SYS_FUNC(mknod)`, `SYS_FUNC(mknodat)`, `printpath`, `print_dirfd`, `print_symbolic_mode_t`, and `print_dev_t`.
Control flow: prints path arguments first, then mode; device number is decoded only for character/block/fifo/socket cases where meaningful. State and persistence behavior: none.
Dependencies and integration points: filesystem syscall decoders. Risks: mode-type switch determines whether `dev` is printed symbolically or raw. Test signals: regular, char/block, fifo, socket, mknodat dirfd, and unusual mode tests.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/mknod.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/mmap_cache.c -->
# sources/test-tools/strace/src/mmap_cache.c

Purpose: maintains a per-tracee cache of `/proc/PID/maps` for stack tracing and address-to-mapping lookups.
Important APIs/types/functions: `mmap_cache_enable`, `mmap_cache_rebuild_if_invalid`, `mmap_cache_search`, `mmap_cache_search_custom`, `delete_mmap_cache`, `mmap_notify_register_client`, and `struct mmap_cache_t`.
Control flow: global generation is incremented by mmap notifications; stale per-tcb caches are freed; rebuild parses maps lines, validates permission fields, skips duplicates/overlaps, grows entries, and installs the cache. Search uses binary lookup over sorted ranges.
State and persistence behavior: global generation plus per-`tcb` allocated cache with free callback. Dependencies and integration points: `/proc`, mmap notification hooks, stack trace code, and large-file wrappers.
Risks: maps parsing and overlap handling affect symbolization; stale cache invalidation is critical after mapping-changing syscalls. Test signals: cache rebuild/search tests, mmap/munmap invalidation, duplicate vsyscall entries, and malformed maps lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/mmap_cache.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/mmap_cache.h -->
# sources/test-tools/strace/src/mmap_cache.h

Purpose: declares mmap-cache data structures and lookup APIs.
Important APIs/types/functions: `MMAP_CACHE_PROT_*` flags, `struct mmap_cache_entry_t`, `struct mmap_cache_t`, `mmap_cache_rebuild_result`, `mmap_cache_search_fn`, and public enable/rebuild/search functions.
Control flow: header only; callers use rebuild result to decide whether cache is ready, renewed, or unavailable. State and persistence behavior: defines per-tcb cache layout and free callback slot.
Dependencies and integration points: stack tracing and `mmap_cache.c`. Risks: structure layout changes must match allocation/free logic. Test signals: compile coverage plus cache lifecycle tests through public functions.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/mmap_cache.h -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/mmap_notify.c -->
# sources/test-tools/strace/src/mmap_notify.c

Purpose: implements a small notification fanout for memory-map changes.
Important APIs/types/functions: `mmap_notify_register_client`, `mmap_notify_report`, callback list storage, and `mmap_notify_client` structures.
Control flow: registration appends a callback/data pair; reporting iterates registered clients and invokes callbacks for the affected `tcb`. State and persistence behavior: process-global client list persists for the strace lifetime.
Dependencies and integration points: mmap cache invalidation and any other mapping-change consumers. Risks: callback order and lifetime ownership are simple but not thread-safe. Test signals: register multiple clients and verify all receive mmap/munmap notification events.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/mmap_notify.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/mmap_notify.h -->
# sources/test-tools/strace/src/mmap_notify.h

Purpose: declares mmap notification callback API.
Important APIs/types/functions: `mmap_notify_fn`, `mmap_notify_register_client`, and `mmap_notify_report`.
Control flow: no implementation. State and persistence behavior: exposes process-global registration contract implemented in `mmap_notify.c`.
Dependencies and integration points: memory syscall decoders notify cache clients after mapping changes. Risks: callbacks must tolerate being called from syscall decoding paths. Test signals: compile and integration tests with mmap cache enabled.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/mmap_notify.h -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/mmsghdr.c -->
# sources/test-tools/strace/src/mmsghdr.c

Purpose: decodes vectorized message syscalls `sendmmsg` and `recvmmsg`.
Important APIs/types/functions: `decode_mmsgvec`, `save_mmsgvec_namelen`, `print_struct_mmsghdr`, `dumpiov_in_mmsghdr`, `do_recvmmsg`, time32/time64 variants, and `msghdr.h` helpers.
Control flow: sendmmsg prints sockfd on entry and decodes message vector on exit with cleared syserror for partial sends; recvmmsg saves per-message name lengths and timeout text on entry, then prints only returned messages and timeout status on exit.
State and persistence behavior: stores per-syscall `mmsgvec_data` in `tcb` private data with a free callback. Dependencies and integration points: `msghdr.c`, iovec dump logic, and socket syscall table.
Risks: vector counts are capped by `IOV_MAX`; partial success and timeout formatting are subtle. Test signals: verbose/nonverbose sendmmsg, recvmmsg timeout, partial vectors, changed namelen, and time32/time64 tests.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/mmsghdr.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/mount.c -->
# sources/test-tools/strace/src/mount.c

Purpose: decodes legacy `mount` syscall arguments and flags.
Important APIs/types/functions: `SYS_FUNC(mount)`, `mount_flags`, `MS_MGC_VAL`, `MS_MGC_MSK`, `printpath`, and `printstr`.
Control flow: prints source, target, filesystem type, strips old magic flag bits when present, prints flags, and prints data as string/address depending on verbosity and pointer. State and persistence behavior: none.
Dependencies and integration points: filesystem syscall decoding. Risks: old magic mask handling must not hide real flags. Test signals: bind/remount/readonly flags, old magic value, null data, and unknown flag traces.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/mount.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/mount_setattr.c -->
# sources/test-tools/strace/src/mount_setattr.c

Purpose: decodes modern mount API calls `mount_setattr`, `open_tree`, and `open_tree_attr`.
Important APIs/types/functions: `print_mount_attr`, `decode_dfd_file_flags`, `decode_dfd_file_flags_attr`, `mount_attr_attr`, `mount_attr_propagation`, `mount_setattr_flags`, and `open_tree_flags`.
Control flow: validates `mount_attr` size, fetches bounded known fields, prints idmap user namespace fd only when relevant, emits future nonzero bytes, and shares dirfd/path/flags printing across syscalls.
State and persistence behavior: stateless. Dependencies and integration points: Linux mount API syscall table and fd/path helpers.
Risks: versioned structure growth and conditional fd interpretation are easy to misprint. Test signals: minimum/oversized attr, idmapped mounts, open_tree flags, and invalid small size cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/mount_setattr.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/move_mount.c -->
# sources/test-tools/strace/src/move_mount.c

Purpose: decodes `move_mount` source and target path/fd pairs plus flags.
Important APIs/types/functions: `SYS_FUNC(move_mount)`, `print_dirfd`, `printpath`, and `move_mount_flags`.
Control flow: prints from dirfd/path, to dirfd/path, then symbolic flags. State and persistence behavior: none.
Dependencies and integration points: mount API syscall table. Risks: dirfd/path ordering must match kernel ABI. Test signals: file-descriptor paths, `AT_FDCWD`, empty paths, and flag combinations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/move_mount.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/mpers.awk -->
# sources/test-tools/strace/src/mpers.awk

Purpose: generates mpers-compatible C type definitions from normalized DWARF debug information.
Important APIs/types/functions: awk functions `array_get`, `norm_idx`, `array_seq`, `enter/leave`, `update_upper_bound`, `what_is`, global arrays for DIE attributes, and `ARCH_FLAG`/`VAR_NAME` inputs.
Control flow: BEGIN derives pointer size and prints stdint include; parsing rules collect DIE indexes, names, sizes, encodings, types, locations, array bounds, and parent relationships; END emits `mpers_ptr_t` and a packed typedef for the requested variable type.
State and persistence behavior: all state is in awk arrays during one run. Dependencies and integration points: invoked by `mpers.sh` after `readelf` preprocessing.
Risks: DWARF format assumptions, recursive type loops, padding math, and gawk-specific `asorti` affect generated ABI structs. Test signals: `mpers_test.sh` expected-output comparison and multi-arch mpers builds.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/mpers.awk -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/mpers.sh -->
# sources/test-tools/strace/src/mpers.sh

Purpose: builds mpers type headers for parser files that declare `DEF_MPERS_TYPE`.
Important APIs/types/functions: shell pipeline using `sed`, `CPP`, `CC`, `READELF`, `gawk -f mpers.awk`, `ARCH_FLAG`, `CC_ARCH_FLAG`, and generated `mpers-$ARCH/type.h` files.
Control flow: extracts target mpers types, synthesizes small C files, preprocesses dependency visibility, compiles with DWARF, normalizes readelf output, and runs the awk generator for each type.
State and persistence behavior: writes generated/intermediate files under `mpers-$ARCH_FLAG`. Dependencies and integration points: build system, compiler, readelf, gawk, parser sources.
Risks: shell quoting, tool version differences, and DWARF output changes can break generation. Test signals: run `mpers_test.sh` and full cross-personality build.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/mpers.sh -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/mpers_test.sh -->
# sources/test-tools/strace/src/mpers_test.sh

Purpose: self-test for mpers generation using a synthetic structure with padding, arrays, unions, pointers, and integer widths.
Important APIs/types/functions: creates `sample.c`, `sample.expected`, invokes `mpers.sh`, and compares generated `sample_struct.h` with `cmp`.
Control flow: derives pointer size from the mpers name, writes fixture source/expected output, sets CPP/CFLAGS including `IN_MPERS`, runs generation, and fails on mismatch.
State and persistence behavior: creates a `mpers-$mpers_name` test directory. Dependencies and integration points: validates `mpers.awk`, `mpers.sh`, and `mpers_type.h` behavior.
Risks: expected fixture must track generator output exactly; compiler layout changes can expose bugs. Test signals: this script is itself the primary test and should be run for m32/mx32-like names.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/mpers_test.sh -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/mpers_type.h -->
# sources/test-tools/strace/src/mpers_type.h

Purpose: abstracts mpers type includes and pointer representation for native and personality builds.
Important APIs/types/functions: `DEF_MPERS_TYPE`, `MPERS_PREFIX`, `MPERS_DEFS`, `mpers_ptr_t`, and guards for `IN_MPERS`, `MPERS_IS_m32`, and `MPERS_IS_mx32`.
Control flow: preprocessor maps parser declarations to generated headers during mpers generation and to `empty.h`/`native_defs.h` during normal builds. State and persistence behavior: declarations only.
Dependencies and integration points: all mpers-aware ioctl/socket decoders. Risks: wrong macro branch makes native builds include generated compat headers or vice versa. Test signals: mpers generation tests and native parser compilation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/mpers_type.h -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/mq.c -->
# sources/test-tools/strace/src/mq.c

Purpose: decodes POSIX message queue syscalls.
Important APIs/types/functions: `mq_open`, `do_mq_timedsend`, time32/time64 send/receive variants, `mq_notify`, `mq_getsetattr`, `printmqattr`, `print_timespec*`, and fd/path helpers.
Control flow: `mq_open` conditionally prints mode/attr for `O_CREAT`; timed send prints message bytes and timeout on entry; timed receive prints buffer and priority on exit but timeout as entry-read data; notify and getsetattr print sigevent/attributes according to syscall phase.
State and persistence behavior: no persistent state beyond syscall phase. Dependencies and integration points: mqueue syscall table and time64 compatibility. Risks: receive buffer length is return-value bounded; timeout must print even on failure. Test signals: create/no-create open, send/receive success/error, priority pointer failures, notify, and getsetattr tests.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/mq.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/msghdr.c -->
# sources/test-tools/strace/src/msghdr.c

Purpose: decodes `msghdr` structures, control messages, and `sendmsg`/`recvmsg` syscalls.
Important APIs/types/functions: `print_struct_msghdr`, `decode_msg_control`, `print_cmsg_type_data`, cmsg printer arrays for `SCM_*` and `IP_*`, `get_optmem_max`, `dumpiov_in_msghdr`, `SYS_FUNC(sendmsg)`, and `SYS_FUNC(recvmsg)`.
Control flow: fetches msghdr, decodes sockaddr/name length changes, chooses netlink-aware iovec printing, bounds control buffer by `/proc/sys/net/core/optmem_max`, walks aligned cmsg headers, and decodes known ancillary data by level/type.
State and persistence behavior: caches optmem_max statically and saves entry-side `msg_namelen` in `tcb` private ulong for recvmsg. Dependencies and integration points: socket syscalls, mmsghdr vector decoder, netlink decoder, fd printers, and time printers.
Risks: cmsg alignment differs by word size; malformed lengths and huge control buffers must be bounded. Test signals: SCM_RIGHTS/CREDENTIALS/PIDFD, timestamps old/new, IP_PKTINFO/RECVERR, truncated control buffers, netlink payloads, and namelen change tests.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/msghdr.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/msghdr.h -->
# sources/test-tools/strace/src/msghdr.h

Purpose: declares msghdr/mmsghdr fetch and print helpers shared by socket message decoders.
Important APIs/types/functions: `struct msghdr`, `struct mmsghdr` fetch wrappers, `sizeof_struct_mmsghdr`, `print_struct_msghdr`, `dumpiov_in_msghdr`, and `dumpiov_in_mmsghdr` declarations.
Control flow: header only; implementation is split between `msghdr.c` and `mmsghdr.c`. State and persistence behavior: no state.
Dependencies and integration points: `sendmsg`, `recvmsg`, `sendmmsg`, and `recvmmsg` decoders. Risks: prototypes must match mpers/native structure fetch implementations. Test signals: compile coverage and socket message syscall tests.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/msghdr.h -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/mtd.c -->
# sources/test-tools/strace/src/mtd.c

Purpose: decodes Memory Technology Device ioctls and associated ABI structures.
Important APIs/types/functions: `mtd_ioctl`, mpers `struct_mtd_oob_buf`, decoders for erase info, OOB buffers, OTP info, write requests, MTD info, NAND OOB/ECC layouts, ECC stats, and xlat tables for modes/types/flags.
Control flow: switch by ioctl code; writes decode on entry, reads often wait for exit; `MEMGETREGIONINFO` prints a partial struct on entry and completes it on successful exit. Unknown commands fall back to generic decoded state.
State and persistence behavior: stateless tracee-memory reads; relies on syscall phase. Dependencies and integration points: central ioctl dispatcher and mpers generation for old OOB buffer layout.
Risks: many structs are version/word-size sensitive; entry/exit split for read ioctls must match kernel direction. Test signals: fixtures for erase, OOB 32/64, MEMWRITE, OTP, info, ECC, badblock, and region info commands.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/mtd.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/native_defs.h -->
# sources/test-tools/strace/src/native_defs.h

Purpose: maps mpers printer macro names to native printer declarations in non-mpers builds.
Important APIs/types/functions: includes `native_printer_decls.h` and defines `MPERS_PRINTER_NAME(printer_name)` as identity.
Control flow: preprocessor-only adapter. State and persistence behavior: no runtime state.
Dependencies and integration points: mpers-aware decoder compilation such as loop and mtd ioctl printers. Risks: wrong macro mapping breaks symbol names between native and compat printer builds. Test signals: native build and mpers-enabled build link checks.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/native_defs.h -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/nbd_ioctl.c -->
# sources/test-tools/strace/src/nbd_ioctl.c

Purpose: decodes Network Block Device ioctls.
Important APIs/types/functions: `nbd_ioctl`, NBD ioctl constants, `nbd_ioctl_flags`, `printfd`, `PRINT_VAL_U`, and generic xlat command names.
Control flow: no-argument commands are marked decoded; `NBD_SET_SOCK` prints fd, size/block/time commands print unsigned values, and `NBD_SET_FLAGS` prints symbolic flags. Unknown codes fall back.
State and persistence behavior: stateless. Dependencies and integration points: ioctl dispatcher. Risks: some NBD arguments are scalar kernel_ulong_t values rather than pointers; treating them as pointers would be wrong. Test signals: each NBD_SET_* command, disconnect/no-arg commands, and unknown ioctl tests.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/nbd_ioctl.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/negated_errno.h -->
# sources/test-tools/strace/src/negated_errno.h

Purpose: common helper for detecting Linux negative errno return values with ABI-width awareness.
Important APIs/types/functions: `is_negated_errno`, `current_klongsize`, `MAX_ERRNO_VALUE`, and kernel-long truncation logic.
Control flow: truncates/comparses the supplied value to the current kernel long width and returns true for the conventional `-MAX_ERRNO_VALUE..-1` range. State and persistence behavior: pure helper.
Dependencies and integration points: architecture `get_error.c` files. Risks: wrong word-size handling misclassifies large successful returns as errors or vice versa. Test signals: boundary tests for `-1`, `-MAX_ERRNO_VALUE`, just outside range, and 32-bit compat returns.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/negated_errno.h -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/net.c -->
# sources/test-tools/strace/src/net.c

Purpose: decodes core socket/network syscalls and many socket option payloads.
Important APIs/types/functions: `socket`, `accept/accept4`, `send/sendto`, `recv/recvfrom`, `socketpair`, `pipe/pipe2`, `getsockopt`, `setsockopt`, `decode_sockbuf`, `decode_sockname`, `print_sockopt_fd_level_name`, and numerous protocol/socket-option xlat tables.
Control flow: socket creation prints protocol names by address family; accept/getname paths save entry-side length and print changed exit lengths; send paths decode buffers immediately, receive paths decode buffers on exit; sockopt decoding switches by level/name to print typed structures, integers, fd values, filters, packet stats, TCP AO keys, TIPC groups, and defaults.
State and persistence behavior: stores entry-side socklen/optlen in `tcb` private ulong for exit-side comparison; otherwise stateless. Dependencies and integration points: sockaddr decoders, netlink decoder, BPF filter decoder, fd protocol cache, xlat tables, and iovec/string printers.
Risks: socket APIs have many level/name-specific payload sizes; malformed lengths and changed optlen values must be rendered without over-reading. Test signals: domain/protocol matrix, accept/getpeername length changes, send/recv success/error, getsockopt/setsockopt for special options, netlink sockets, and unknown option fallbacks.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/net.c -->
