# subset-b-009334 research

Grouped research report for strace Linux architecture support files. Each section title preserves the exact source path and is wrapped for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/64/syscallent.h -->
# sources/test-tools/strace/src/linux/64/syscallent.h

Purpose: defines syscall table metadata for the `64` personality, covering 279 named entries across 289 source lines; early entries include io_setup, io_destroy, io_submit, io_cancel, io_getevents, setxattr, lsetxattr, fsetxattr.

Important APIs/types/functions: table initializers map syscall numbers to argument counts, trace flags, `SEN(...)` decoder handlers, and printable names. Flags observed here include CC, NF, PU, SI, TC, TCL, TD, TF, TFSF, TFST, TI, TM.

Control flow: strace indexes this array after `arch_get_scno` and optional syscall-number shuffling, then dispatches the selected `SEN` decoder and applies table flags to path, fd, network, signal, process, stat, memory, IPC, and pure-call formatting behavior.

State/persistence behavior: compile-time dispatch metadata only; runtime state lives in `struct tcb` fields populated from registers and syscall arguments.

Dependencies/integration: depends on decoder symbols declared elsewhere in strace, architecture syscall numbering, generated common tables, and personality selection.

Risks/test signals: off-by-one numbering, stale ABI entries, or wrong flags produce incorrect syscall names/argument classes; test with known syscall-number traces, generated table checks, and cross-architecture comparison against Linux syscall headers.

Source-read signal: reviewed complete local file (289 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/64/syscallent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/aarch64/arch_defs_.h -->
# sources/test-tools/strace/src/linux/aarch64/arch_defs_.h

Purpose: declares strace compile-time personality features for the `aarch64` Linux backend, including HAVE_ARCH_OLD_MMAP, HAVE_ARCH_OLD_SELECT, HAVE_ARCH_UID16_SYSCALLS, SUPPORTED_PERSONALITIES, PERSONALITY0_AUDIT_ARCH, PERSONALITY1_AUDIT_ARCH.

Important APIs/types/functions: preprocessor macros control feature gates such as old mmap/select, UID16 syscalls, dedicated error registers, supported personalities, and audit arch tuples (AUDIT_ARCH_AARCH64, 0 ; AUDIT_ARCH_ARM,     0 ).

Control flow: no executable code. The main Linux backend includes this header while building architecture-specific syscall decoding and personality setup.

State/persistence behavior: static build-time configuration only; it influences how `struct tcb` register state is interpreted but stores no runtime state itself.

Dependencies/integration: depends on Linux audit architecture constants and may include generated base-number headers (no local includes).

Risks/test signals: incorrect feature macros select wrong syscall tables or legacy decoders; validate with architecture build tests, audit-personality checks, and traces of legacy mmap/select or UID16 syscalls when enabled.

Source-read signal: reviewed complete local file (13 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/aarch64/arch_defs_.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/aarch64/arch_get_personality.c -->
# sources/test-tools/strace/src/linux/aarch64/arch_get_personality.c

Purpose: maps ptrace syscall-info audit architecture values to the strace personality index for `aarch64`.

Important APIs/types/functions: get_personality_from_syscall_info; notable register references include none in this file.

Control flow: returns the compatibility personality when the syscall-info `arch` field matches the secondary audit architecture; otherwise the generic caller treats it as personality 0.

State/persistence behavior: operates on transient tracee/register/memory snapshots or compile-time metadata; persistent program state is not introduced here.

Dependencies/integration: Depends on `struct_ptrace_syscall_info` and Linux audit architecture constants.

Risks/test signals: wrong mapping dispatches to the wrong syscall table; test mixed native/compat traced processes.

Source-read signal: reviewed complete local file (13 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/aarch64/arch_get_personality.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/aarch64/arch_prstatus_regset.c -->
# sources/test-tools/strace/src/linux/aarch64/arch_prstatus_regset.c

Purpose: pretty-prints `aarch64` regset payloads returned by ptrace/core-note style interfaces.

Important APIs/types/functions: arch_decode_prstatus_regset; notable register references include none in this file.

Control flow: rejects empty or misaligned buffers by printing the raw address, safely copies up to the known struct size from the tracee, prints fields that fit inside the supplied size, and marks extra trailing bytes with `more data follows`.

State/persistence behavior: operates on transient tracee/register/memory snapshots or compile-time metadata; persistent program state is not introduced here.

Dependencies/integration: Depends on `umoven_or_printaddr`, `PRINT_FIELD_X`, array printers, struct offset checks, and the companion regset typedef header.

Risks/test signals: field-order or alignment mistakes misdecode `PTRACE_GETREGSET` data; test short, exact-size, oversized, and misaligned regset buffers.

Source-read signal: reviewed complete local file (47 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/aarch64/arch_prstatus_regset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/aarch64/arch_prstatus_regset.h -->
# sources/test-tools/strace/src/linux/aarch64/arch_prstatus_regset.h

Purpose: declares the `aarch64` regset struct shape and enables the matching decoder.

Important APIs/types/functions: STRACE_ARCH_PRSTATUS_REGSET_H, HAVE_ARCH_PRSTATUS_REGSET; notable register references include none in this file.

Control flow: no executable flow; the typedef and `HAVE_ARCH_*` macro let generic code compile the architecture decoder.

State/persistence behavior: operates on transient tracee/register/memory snapshots or compile-time metadata; persistent program state is not introduced here.

Dependencies/integration: Depends on architecture kernel user register types or locally declared field order; includes ../arm/arch_prstatus_regset.h.

Risks/test signals: typedef drift from kernel ABI breaks register dumps; compile with current headers and run ptrace regset decoding tests.

Source-read signal: reviewed complete local file (17 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/aarch64/arch_prstatus_regset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/aarch64/arch_regs.c -->
# sources/test-tools/strace/src/linux/aarch64/arch_regs.c

Purpose: defines the register storage and program-counter/stack-pointer access macros for the `aarch64` Linux strace backend.

Important APIs/types/functions: visible register contract includes macros ARM_cpsr, ARM_pc, ARM_lr, ARM_sp, ARM_ip, ARM_fp, ARM_r10, ARM_r9, ARM_r8, ARM_r7, ARM_r6, ARM_r5; functions none; notable register fields include uregs[18], uregs[16], uregs[15], uregs[14], uregs[13], uregs[12], uregs[11], uregs[10], uregs[9], uregs[8], uregs[7], uregs[6].

Control flow: generic register-fetch code populates the declared storage via `GETREGS`/`GETREGSET`, then syscall-entry/exit, signal, and stack helpers read the macros exported here.

State/persistence behavior: per-tracee register snapshots are held in static architecture globals for the duration of a decode step and refreshed from ptrace; nothing is persisted beyond the trace event.

Dependencies/integration: integrates with generic `get_regs`, `set_regs`, `get_stack_pointer`, syscall-argument extraction, and signal-frame helpers; includes architecture kernel register structs supplied by surrounding includes.

Risks/test signals: wrong register field mapping corrupts syscall numbers, arguments, PC/SP reporting, and injected return values; validate with ptrace register fetch/set tests and known syscall traces on the architecture.

Source-read signal: reviewed complete local file (49 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/aarch64/arch_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/aarch64/arch_sigreturn.c -->
# sources/test-tools/strace/src/linux/aarch64/arch_sigreturn.c

Purpose: reuses shared strace architecture logic for `aarch64` by including `../arm/arch_sigreturn.c` from `arch_sigreturn.c`.

Important APIs/types/functions: this file exports the APIs provided by the included implementation rather than defining new local functions.

Control flow: the C preprocessor splices the target file into this architecture build, so runtime behavior is the shared implementation's behavior under this architecture's register/personality macros.

State/persistence behavior: no independent state; included code operates on the surrounding architecture register globals and `struct tcb` state.

Dependencies/integration: direct dependency on `../arm/arch_sigreturn.c` and the macro/register contract expected by that file.

Risks/test signals: changes in the shared implementation can silently affect this architecture; compile the architecture and run syscall/signal/ioctl traces that exercise the included path.

Source-read signal: reviewed complete local file (1 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/aarch64/arch_sigreturn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/aarch64/get_error.c -->
# sources/test-tools/strace/src/linux/aarch64/get_error.c

Purpose: translates the `aarch64` syscall return/error convention into `tcp->u_rval` and `tcp->u_error`.

Important APIs/types/functions: arch_get_error; key state includes `struct tcb`, `tcp->scno`, `tcp->u_arg`, `tcp->u_rval`, `tcp->u_error`, and register fields regs[0].

Control flow: on syscall exit it reads the architecture return/error register convention, optionally checks negated errno ranges or dedicated error flags, sets `u_rval=-1` for errors, and otherwise records the raw return value.

State/persistence behavior: mutates only the active trace control block and current ptrace register snapshot; any tracee register changes are applied immediately through ptrace helpers.

Dependencies/integration: participates in generic syscall enter/exit decoding; depends on negated_errno.h, ../arm/get_error.c.

Risks/test signals: Test with successful syscalls, negated errno returns, and any architecture-specific dedicated error register path.

Source-read signal: reviewed complete local file (28 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/aarch64/get_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/aarch64/get_scno.c -->
# sources/test-tools/strace/src/linux/aarch64/get_scno.c

Purpose: extracts the current syscall number for the `aarch64` backend.

Important APIs/types/functions: arch_get_scno; key state includes `struct tcb`, `tcp->scno`, `tcp->u_arg`, `tcp->u_rval`, `tcp->u_error`, and register fields regs[8], ARM_r7.

Control flow: on syscall entry it reads the ABI syscall-number register or user offset, may perform sanity checks for stray exits, then stores the result in `tcp->scno` and returns the generic status code.

State/persistence behavior: mutates only the active trace control block and current ptrace register snapshot; any tracee register changes are applied immediately through ptrace helpers.

Dependencies/integration: participates in generic syscall enter/exit decoding; depends on architecture register globals, ptrace helpers, and common tcb fields.

Risks/test signals: Test with representative syscall entries, invalid/out-of-range numbers, and personality-specific numbering when present.

Source-read signal: reviewed complete local file (28 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/aarch64/get_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/aarch64/get_syscall_args.c -->
# sources/test-tools/strace/src/linux/aarch64/get_syscall_args.c

Purpose: copies syscall arguments from `aarch64` register state or backing register-stack memory into `tcp->u_arg`.

Important APIs/types/functions: arch_get_syscall_args; key state includes `struct tcb`, `tcp->scno`, `tcp->u_arg`, `tcp->u_rval`, `tcp->u_error`, and register fields regs[0], regs[1], regs[2], regs[3], regs[4], regs[5].

Control flow: after the syscall number is known, it reads up to `n_args(tcp)` or `MAX_ARGS` arguments from ABI-defined registers, compatibility helper code, or memory addresses derived from register-stack state, returning `1` on success or `-1` on fatal fetch failure.

State/persistence behavior: mutates only the active trace control block and current ptrace register snapshot; any tracee register changes are applied immediately through ptrace helpers.

Dependencies/integration: participates in generic syscall enter/exit decoding; depends on ../arm/get_syscall_args.c.

Risks/test signals: Test with six-argument syscalls, compatibility personalities, and ptrace permission/fault cases for memory-backed argument locations.

Source-read signal: reviewed complete local file (25 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/aarch64/get_syscall_args.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/aarch64/ioctls_arch0.h -->
# sources/test-tools/strace/src/linux/aarch64/ioctls_arch0.h

Purpose: provides the `aarch64` generated architecture ioctl table, with 74 initializer rows from linux/kvm.h; examples include KVM_ARM_GET_REG_WRITABLE_MASKS, KVM_ARM_MTE_COPY_TAGS, KVM_ARM_PREFERRED_TARGET, KVM_ARM_SET_COUNTER_OFFSET, KVM_ARM_SET_DEVICE_ADDR, KVM_ARM_VCPU_FINALIZE.

Important APIs/types/functions: each row is `{'header, name, direction, number, size'}` data consumed by the common ioctl xlat machinery; observed direction flags include _IOC_NONE, _IOC_READ, _IOC_WRITE.

Control flow: no executable flow; entries are compiled into lookup arrays that let `ioctl(2)` decoding map command numbers back to symbolic names and argument direction/size.

State/persistence behavior: immutable compile-time metadata only; it neither reads traced memory nor persists runtime state.

Dependencies/integration: generated from Linux UAPI headers by `ioctls_gen.sh` and consumed by the strace ioctl decoder alongside generic include tables.

Risks/test signals: stale generated rows or wrong command sizes cause misleading ioctl names or argument decoding; test by comparing generated tables with current UAPI headers and tracing representative architecture-specific ioctl calls.

Source-read signal: reviewed complete local file (75 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/aarch64/ioctls_arch0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/aarch64/ioctls_arch1.h -->
# sources/test-tools/strace/src/linux/aarch64/ioctls_arch1.h

Purpose: reuses shared strace architecture logic for `aarch64` by including `../arm/ioctls_arch0.h` from `ioctls_arch1.h`.

Important APIs/types/functions: this file exports the APIs provided by the included implementation rather than defining new local functions.

Control flow: the C preprocessor splices the target file into this architecture build, so runtime behavior is the shared implementation's behavior under this architecture's register/personality macros.

State/persistence behavior: no independent state; included code operates on the surrounding architecture register globals and `struct tcb` state.

Dependencies/integration: direct dependency on `../arm/ioctls_arch0.h` and the macro/register contract expected by that file.

Risks/test signals: changes in the shared implementation can silently affect this architecture; compile the architecture and run syscall/signal/ioctl traces that exercise the included path.

Source-read signal: reviewed complete local file (1 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/aarch64/ioctls_arch1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/aarch64/ioctls_inc0.h -->
# sources/test-tools/strace/src/linux/aarch64/ioctls_inc0.h

Purpose: reuses shared strace architecture logic for `aarch64` by including `../64/ioctls_inc.h` from `ioctls_inc0.h`.

Important APIs/types/functions: this file exports the APIs provided by the included implementation rather than defining new local functions.

Control flow: the C preprocessor splices the target file into this architecture build, so runtime behavior is the shared implementation's behavior under this architecture's register/personality macros.

State/persistence behavior: no independent state; included code operates on the surrounding architecture register globals and `struct tcb` state.

Dependencies/integration: direct dependency on `../64/ioctls_inc.h` and the macro/register contract expected by that file.

Risks/test signals: changes in the shared implementation can silently affect this architecture; compile the architecture and run syscall/signal/ioctl traces that exercise the included path.

Source-read signal: reviewed complete local file (1 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/aarch64/ioctls_inc0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/aarch64/ioctls_inc1.h -->
# sources/test-tools/strace/src/linux/aarch64/ioctls_inc1.h

Purpose: reuses shared strace architecture logic for `aarch64` by including `../arm/ioctls_inc0.h` from `ioctls_inc1.h`.

Important APIs/types/functions: this file exports the APIs provided by the included implementation rather than defining new local functions.

Control flow: the C preprocessor splices the target file into this architecture build, so runtime behavior is the shared implementation's behavior under this architecture's register/personality macros.

State/persistence behavior: no independent state; included code operates on the surrounding architecture register globals and `struct tcb` state.

Dependencies/integration: direct dependency on `../arm/ioctls_inc0.h` and the macro/register contract expected by that file.

Risks/test signals: changes in the shared implementation can silently affect this architecture; compile the architecture and run syscall/signal/ioctl traces that exercise the included path.

Source-read signal: reviewed complete local file (1 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/aarch64/ioctls_inc1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/aarch64/nr_prefix.c -->
# sources/test-tools/strace/src/linux/aarch64/nr_prefix.c

Purpose: reuses shared strace architecture logic for `aarch64` by including `../arm/nr_prefix.c` from `nr_prefix.c`.

Important APIs/types/functions: this file exports the APIs provided by the included implementation rather than defining new local functions.

Control flow: the C preprocessor splices the target file into this architecture build, so runtime behavior is the shared implementation's behavior under this architecture's register/personality macros.

State/persistence behavior: no independent state; included code operates on the surrounding architecture register globals and `struct tcb` state.

Dependencies/integration: direct dependency on `../arm/nr_prefix.c` and the macro/register contract expected by that file.

Risks/test signals: changes in the shared implementation can silently affect this architecture; compile the architecture and run syscall/signal/ioctl traces that exercise the included path.

Source-read signal: reviewed complete local file (1 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/aarch64/nr_prefix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/aarch64/raw_syscall.h -->
# sources/test-tools/strace/src/linux/aarch64/raw_syscall.h

Purpose: implements a minimal zero-argument raw syscall helper for `aarch64`.

Important APIs/types/functions: raw_syscall_0, STRACE_RAW_SYSCALL_H, raw_syscall_0; notable register references include none in this file.

Control flow: loads the requested syscall number into the ABI register, executes the architecture trap instruction, records an error flag where the ABI exposes one, and returns the raw result register.

State/persistence behavior: operates on transient tracee/register/memory snapshots or compile-time metadata; persistent program state is not introduced here.

Dependencies/integration: Depends on inline assembly register constraints, trap instructions, clobber lists, and `kernel_ulong_t`.

Risks/test signals: incorrect constraints or clobbers can miscompile; test a harmless syscall such as getpid and an expected failing syscall on native hardware/toolchains.

Source-read signal: reviewed complete local file (29 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/aarch64/raw_syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/aarch64/set_error.c -->
# sources/test-tools/strace/src/linux/aarch64/set_error.c

Purpose: injects a synthetic syscall error or success result into `aarch64` tracee registers.

Important APIs/types/functions: arch_set_error, arch_set_success; key state includes `struct tcb`, `tcp->scno`, `tcp->u_arg`, `tcp->u_rval`, `tcp->u_error`, and register fields regs[0].

Control flow: `arch_set_error` writes the architecture error convention from `tcp->u_error`; `arch_set_success` writes `tcp->u_rval`; implementations either poke individual user offsets or call `set_regs` after mutating the saved register block.

State/persistence behavior: mutates only the active trace control block and current ptrace register snapshot; any tracee register changes are applied immediately through ptrace helpers.

Dependencies/integration: participates in generic syscall enter/exit decoding; depends on ../arm/set_error.c.

Risks/test signals: Test with syscall fault injection for both success and errno paths, including ESRCH/disappearing-tracee behavior where relevant.

Source-read signal: reviewed complete local file (32 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/aarch64/set_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/aarch64/set_scno.c -->
# sources/test-tools/strace/src/linux/aarch64/set_scno.c

Purpose: updates the tracee syscall number for `aarch64` syscall tampering/restart support.

Important APIs/types/functions: arch_set_scno; key state includes `struct tcb`, `tcp->scno`, `tcp->u_arg`, `tcp->u_rval`, `tcp->u_error`, and register fields defined by included architecture helpers.

Control flow: writes the requested syscall number into the architecture orig-syscall register using `upoke`, `set_regs`, or an architecture regset such as `NT_ARM_SYSTEM_CALL`.

State/persistence behavior: mutates only the active trace control block and current ptrace register snapshot; any tracee register changes are applied immediately through ptrace helpers.

Dependencies/integration: participates in generic syscall enter/exit decoding; depends on architecture register globals, ptrace helpers, and common tcb fields.

Risks/test signals: Test by rewriting a syscall number under ptrace and confirming the kernel executes/prints the replacement call.

Source-read signal: reviewed complete local file (29 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/aarch64/set_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/aarch64/shuffle_scno.c -->
# sources/test-tools/strace/src/linux/aarch64/shuffle_scno.c

Purpose: translates raw `aarch64` syscall numbers into the table index space used by strace.

Important APIs/types/functions: shuffle_scno_pers, shuffle_scno_pers_is_static, shuffle_scno_pers; notable register references include none in this file.

Control flow: generic dispatch calls `shuffle_scno_pers`; implementations may leave native numbers unchanged, delegate to compat helpers, or xor/add a base offset after static assertions.

State/persistence behavior: operates on transient tracee/register/memory snapshots or compile-time metadata; persistent program state is not introduced here.

Dependencies/integration: Depends on syscall table size/base-number constants and personality id.

Risks/test signals: wrong shuffling dispatches to the wrong table; test boundary syscall numbers and personality-specific tables.

Source-read signal: reviewed complete local file (21 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/aarch64/shuffle_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/aarch64/syscallent.h -->
# sources/test-tools/strace/src/linux/aarch64/syscallent.h

Purpose: reuses shared strace architecture logic for `aarch64` by including `../64/syscallent.h` from `syscallent.h`.

Important APIs/types/functions: this file exports the APIs provided by the included implementation rather than defining new local functions.

Control flow: the C preprocessor splices the target file into this architecture build, so runtime behavior is the shared implementation's behavior under this architecture's register/personality macros.

State/persistence behavior: no independent state; included code operates on the surrounding architecture register globals and `struct tcb` state.

Dependencies/integration: direct dependency on `../64/syscallent.h` and the macro/register contract expected by that file.

Risks/test signals: changes in the shared implementation can silently affect this architecture; compile the architecture and run syscall/signal/ioctl traces that exercise the included path.

Source-read signal: reviewed complete local file (13 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/aarch64/syscallent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/aarch64/syscallent1.h -->
# sources/test-tools/strace/src/linux/aarch64/syscallent1.h

Purpose: reuses shared strace architecture logic for `aarch64` by including `../arm/syscallent.h` from `syscallent1.h`.

Important APIs/types/functions: this file exports the APIs provided by the included implementation rather than defining new local functions.

Control flow: the C preprocessor splices the target file into this architecture build, so runtime behavior is the shared implementation's behavior under this architecture's register/personality macros.

State/persistence behavior: no independent state; included code operates on the surrounding architecture register globals and `struct tcb` state.

Dependencies/integration: direct dependency on `../arm/syscallent.h` and the macro/register contract expected by that file.

Risks/test signals: changes in the shared implementation can silently affect this architecture; compile the architecture and run syscall/signal/ioctl traces that exercise the included path.

Source-read signal: reviewed complete local file (1 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/aarch64/syscallent1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/alpha/arch_defs_.h -->
# sources/test-tools/strace/src/linux/alpha/arch_defs_.h

Purpose: declares strace compile-time personality features for the `alpha` Linux backend, including HAVE_ARCH_GETRVAL2, HAVE_ARCH_DEDICATED_ERR_REG, HAVE_ARCH_TIME32_SYSCALLS, PERSONALITY0_AUDIT_ARCH.

Important APIs/types/functions: preprocessor macros control feature gates such as old mmap/select, UID16 syscalls, dedicated error registers, supported personalities, and audit arch tuples (AUDIT_ARCH_ALPHA, 0 ).

Control flow: no executable code. The main Linux backend includes this header while building architecture-specific syscall decoding and personality setup.

State/persistence behavior: static build-time configuration only; it influences how `struct tcb` register state is interpreted but stores no runtime state itself.

Dependencies/integration: depends on Linux audit architecture constants and may include generated base-number headers (no local includes).

Risks/test signals: incorrect feature macros select wrong syscall tables or legacy decoders; validate with architecture build tests, audit-personality checks, and traces of legacy mmap/select or UID16 syscalls when enabled.

Source-read signal: reviewed complete local file (11 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/alpha/arch_defs_.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/alpha/arch_getrval2.c -->
# sources/test-tools/strace/src/linux/alpha/arch_getrval2.c

Purpose: returns the architecture-specific second syscall return value for `alpha`.

Important APIs/types/functions: getrval2; notable register references include none in this file.

Control flow: fetches registers if needed, then returns the ABI register used for the secondary result.

State/persistence behavior: operates on transient tracee/register/memory snapshots or compile-time metadata; persistent program state is not introduced here.

Dependencies/integration: Depends on ptrace register fetch helpers and architecture return-register layout.

Risks/test signals: validate syscalls with paired return values, plus ptrace fetch failure paths.

Source-read signal: reviewed complete local file (15 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/alpha/arch_getrval2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/alpha/arch_regs.c -->
# sources/test-tools/strace/src/linux/alpha/arch_regs.c

Purpose: defines the register storage and program-counter/stack-pointer access macros for the `alpha` Linux strace backend.

Important APIs/types/functions: visible register contract includes macros REG_R0, REG_A0, REG_A3, REG_SP, REG_PC, ARCH_PC_PEEK_ADDR, ARCH_SP_PEEK_ADDR; functions none; notable register fields include architecture struct fields referenced through macros.

Control flow: generic register-fetch code populates the declared storage via `GETREGS`/`GETREGSET`, then syscall-entry/exit, signal, and stack helpers read the macros exported here.

State/persistence behavior: per-tracee register snapshots are held in static architecture globals for the duration of a decode step and refreshed from ptrace; nothing is persisted beyond the trace event.

Dependencies/integration: integrates with generic `get_regs`, `set_regs`, `get_stack_pointer`, syscall-argument extraction, and signal-frame helpers; includes architecture kernel register structs supplied by surrounding includes.

Risks/test signals: wrong register field mapping corrupts syscall numbers, arguments, PC/SP reporting, and injected return values; validate with ptrace register fetch/set tests and known syscall traces on the architecture.

Source-read signal: reviewed complete local file (18 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/alpha/arch_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/alpha/arch_sigreturn.c -->
# sources/test-tools/strace/src/linux/alpha/arch_sigreturn.c

Purpose: decodes signal mask restoration for `alpha` `sigreturn`/`rt_sigreturn` handling.

Important APIs/types/functions: arch_sigreturn; struct typedef count 0.

Control flow: the helper locates the signal frame from the current stack pointer or architecture context, reads the relevant frame/mask fields with safe `umove` helpers, and prints the restored signal mask.

State/persistence behavior: reads transient signal-frame data from tracee memory and prints it; no durable state is stored.

Dependencies/integration: integrates with `get_stack_pointer`, `umove_or_printaddr`, sigset printers, `ucontext_t`/`sigcontext`, and generic signal-return decoding.

Risks/test signals: frame offsets and padding are ABI-sensitive; validate with signal handler traces, blocked-mask restoration, and rt_sigreturn decoding on the architecture.

Source-read signal: reviewed complete local file (18 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/alpha/arch_sigreturn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/alpha/errnoent.h -->
# sources/test-tools/strace/src/linux/alpha/errnoent.h

Purpose: maps `alpha` errno numbers to symbolic names, with 149 named errno slots such as EPERM, ENOENT, ESRCH, EINTR, EIO, ENXIO, E2BIG, ENOEXEC.

Important APIs/types/functions: string table entries indexed by numeric errno; there are no functions.

Control flow: syscall-exit decoding converts an architecture-specific error number into the indexed name for printing.

State/persistence behavior: static lookup metadata only.

Dependencies/integration: consumed by strace xlat/table-generation code; includes no additional headers.

Risks/test signals: architecture-specific errno numbering differs from generic Linux; validate by comparing against the arch UAPI errno header and tracing syscalls returning nonportable errors.

Source-read signal: reviewed complete local file (156 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/alpha/errnoent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/alpha/get_error.c -->
# sources/test-tools/strace/src/linux/alpha/get_error.c

Purpose: translates the `alpha` syscall return/error convention into `tcp->u_rval` and `tcp->u_error`.

Important APIs/types/functions: arch_get_error; key state includes `struct tcb`, `tcp->scno`, `tcp->u_arg`, `tcp->u_rval`, `tcp->u_error`, and register fields defined by included architecture helpers.

Control flow: on syscall exit it reads the architecture return/error register convention, optionally checks negated errno ranges or dedicated error flags, sets `u_rval=-1` for errors, and otherwise records the raw return value.

State/persistence behavior: mutates only the active trace control block and current ptrace register snapshot; any tracee register changes are applied immediately through ptrace helpers.

Dependencies/integration: participates in generic syscall enter/exit decoding; depends on architecture register globals, ptrace helpers, and common tcb fields.

Risks/test signals: Test with successful syscalls, negated errno returns, and any architecture-specific dedicated error register path.

Source-read signal: reviewed complete local file (17 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/alpha/get_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/alpha/get_scno.c -->
# sources/test-tools/strace/src/linux/alpha/get_scno.c

Purpose: extracts the current syscall number for the `alpha` backend.

Important APIs/types/functions: arch_get_scno; key state includes `struct tcb`, `tcp->scno`, `tcp->u_arg`, `tcp->u_rval`, `tcp->u_error`, and register fields defined by included architecture helpers.

Control flow: on syscall entry it reads the ABI syscall-number register or user offset, may perform sanity checks for stray exits, then stores the result in `tcp->scno` and returns the generic status code.

State/persistence behavior: mutates only the active trace control block and current ptrace register snapshot; any tracee register changes are applied immediately through ptrace helpers.

Dependencies/integration: participates in generic syscall enter/exit decoding; depends on architecture register globals, ptrace helpers, and common tcb fields.

Risks/test signals: Test with representative syscall entries, invalid/out-of-range numbers, and personality-specific numbering when present.

Source-read signal: reviewed complete local file (32 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/alpha/get_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/alpha/get_syscall_args.c -->
# sources/test-tools/strace/src/linux/alpha/get_syscall_args.c

Purpose: copies syscall arguments from `alpha` register state or backing register-stack memory into `tcp->u_arg`.

Important APIs/types/functions: arch_get_syscall_args; key state includes `struct tcb`, `tcp->scno`, `tcp->u_arg`, `tcp->u_rval`, `tcp->u_error`, and register fields defined by included architecture helpers.

Control flow: after the syscall number is known, it reads up to `n_args(tcp)` or `MAX_ARGS` arguments from ABI-defined registers, compatibility helper code, or memory addresses derived from register-stack state, returning `1` on success or `-1` on fatal fetch failure.

State/persistence behavior: mutates only the active trace control block and current ptrace register snapshot; any tracee register changes are applied immediately through ptrace helpers.

Dependencies/integration: participates in generic syscall enter/exit decoding; depends on architecture register globals, ptrace helpers, and common tcb fields.

Risks/test signals: Test with six-argument syscalls, compatibility personalities, and ptrace permission/fault cases for memory-backed argument locations.

Source-read signal: reviewed complete local file (16 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/alpha/get_syscall_args.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/alpha/get_syscall_result.c -->
# sources/test-tools/strace/src/linux/alpha/get_syscall_result.c

Purpose: fetches result registers needed by `alpha` before generic syscall-exit decoding.

Important APIs/types/functions: get_syscall_result_regs; key state includes `struct tcb`, `tcp->scno`, `tcp->u_arg`, `tcp->u_rval`, `tcp->u_error`, and register fields defined by included architecture helpers.

Control flow: reads the return and error-indicator registers from ptrace into static globals and reports failure if either fetch fails.

State/persistence behavior: mutates only the active trace control block and current ptrace register snapshot; any tracee register changes are applied immediately through ptrace helpers.

Dependencies/integration: participates in generic syscall enter/exit decoding; depends on architecture register globals, ptrace helpers, and common tcb fields.

Risks/test signals: Test syscall exits for both success and failure, including ptrace read errors.

Source-read signal: reviewed complete local file (13 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/alpha/get_syscall_result.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/alpha/ioctls_arch0.h -->
# sources/test-tools/strace/src/linux/alpha/ioctls_arch0.h

Purpose: provides the `alpha` generated architecture ioctl table, with 79 initializer rows from asm/ioctls.h, asm/sockios.h; examples include FIOASYNC, FIOCLEX, FIONBIO, FIONCLEX, FIONREAD, FIOQSIZE.

Important APIs/types/functions: each row is `{'header, name, direction, number, size'}` data consumed by the common ioctl xlat machinery; observed direction flags include _IOC_NONE, _IOC_READ, _IOC_WRITE.

Control flow: no executable flow; entries are compiled into lookup arrays that let `ioctl(2)` decoding map command numbers back to symbolic names and argument direction/size.

State/persistence behavior: immutable compile-time metadata only; it neither reads traced memory nor persists runtime state.

Dependencies/integration: generated from Linux UAPI headers by `ioctls_gen.sh` and consumed by the strace ioctl decoder alongside generic include tables.

Risks/test signals: stale generated rows or wrong command sizes cause misleading ioctl names or argument decoding; test by comparing generated tables with current UAPI headers and tracing representative architecture-specific ioctl calls.

Source-read signal: reviewed complete local file (80 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/alpha/ioctls_arch0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/alpha/ioctls_inc0.h -->
# sources/test-tools/strace/src/linux/alpha/ioctls_inc0.h

Purpose: reuses shared strace architecture logic for `alpha` by including `../64/ioctls_inc.h` from `ioctls_inc0.h`.

Important APIs/types/functions: this file exports the APIs provided by the included implementation rather than defining new local functions.

Control flow: the C preprocessor splices the target file into this architecture build, so runtime behavior is the shared implementation's behavior under this architecture's register/personality macros.

State/persistence behavior: no independent state; included code operates on the surrounding architecture register globals and `struct tcb` state.

Dependencies/integration: direct dependency on `../64/ioctls_inc.h` and the macro/register contract expected by that file.

Risks/test signals: changes in the shared implementation can silently affect this architecture; compile the architecture and run syscall/signal/ioctl traces that exercise the included path.

Source-read signal: reviewed complete local file (1 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/alpha/ioctls_inc0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/alpha/raw_syscall.h -->
# sources/test-tools/strace/src/linux/alpha/raw_syscall.h

Purpose: implements a minimal zero-argument raw syscall helper for `alpha`.

Important APIs/types/functions: raw_syscall_0, STRACE_RAW_SYSCALL_H, raw_syscall_0; notable register references include none in this file.

Control flow: loads the requested syscall number into the ABI register, executes the architecture trap instruction, records an error flag where the ABI exposes one, and returns the raw result register.

State/persistence behavior: operates on transient tracee/register/memory snapshots or compile-time metadata; persistent program state is not introduced here.

Dependencies/integration: Depends on inline assembly register constraints, trap instructions, clobber lists, and `kernel_ulong_t`.

Risks/test signals: incorrect constraints or clobbers can miscompile; test a harmless syscall such as getpid and an expected failing syscall on native hardware/toolchains.

Source-read signal: reviewed complete local file (31 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/alpha/raw_syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/alpha/set_error.c -->
# sources/test-tools/strace/src/linux/alpha/set_error.c

Purpose: injects a synthetic syscall error or success result into `alpha` tracee registers.

Important APIs/types/functions: arch_set_error, arch_set_success; key state includes `struct tcb`, `tcp->scno`, `tcp->u_arg`, `tcp->u_rval`, `tcp->u_error`, and register fields defined by included architecture helpers.

Control flow: `arch_set_error` writes the architecture error convention from `tcp->u_error`; `arch_set_success` writes `tcp->u_rval`; implementations either poke individual user offsets or call `set_regs` after mutating the saved register block.

State/persistence behavior: mutates only the active trace control block and current ptrace register snapshot; any tracee register changes are applied immediately through ptrace helpers.

Dependencies/integration: participates in generic syscall enter/exit decoding; depends on architecture register globals, ptrace helpers, and common tcb fields.

Risks/test signals: Test with syscall fault injection for both success and errno paths, including ESRCH/disappearing-tracee behavior where relevant.

Source-read signal: reviewed complete local file (20 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/alpha/set_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/alpha/set_scno.c -->
# sources/test-tools/strace/src/linux/alpha/set_scno.c

Purpose: updates the tracee syscall number for `alpha` syscall tampering/restart support.

Important APIs/types/functions: arch_set_scno; key state includes `struct tcb`, `tcp->scno`, `tcp->u_arg`, `tcp->u_rval`, `tcp->u_error`, and register fields defined by included architecture helpers.

Control flow: writes the requested syscall number into the architecture orig-syscall register using `upoke`, `set_regs`, or an architecture regset such as `NT_ARM_SYSTEM_CALL`.

State/persistence behavior: mutates only the active trace control block and current ptrace register snapshot; any tracee register changes are applied immediately through ptrace helpers.

Dependencies/integration: participates in generic syscall enter/exit decoding; depends on architecture register globals, ptrace helpers, and common tcb fields.

Risks/test signals: Test by rewriting a syscall number under ptrace and confirming the kernel executes/prints the replacement call.

Source-read signal: reviewed complete local file (12 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/alpha/set_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/alpha/signalent.h -->
# sources/test-tools/strace/src/linux/alpha/signalent.h

Purpose: maps `alpha` signal numbers to printable names, with 33 slots including 0, SIGHUP, SIGINT, SIGQUIT, SIGILL, SIGTRAP, SIGABRT, SIGEMT.

Important APIs/types/functions: signal-name table entries consumed by signal and sigset printers.

Control flow: signal decoders index this table when formatting signal numbers, pending masks, handlers, and signal-return state.

State/persistence behavior: static lookup metadata only.

Dependencies/integration: consumed by strace xlat/table-generation code; includes no additional headers.

Risks/test signals: signal numbering is ABI-specific; validate with signal delivery/kill traces and generated signal table comparison.

Source-read signal: reviewed complete local file (40 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/alpha/signalent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/alpha/syscallent.h -->
# sources/test-tools/strace/src/linux/alpha/syscallent.h

Purpose: defines syscall table metadata for the `alpha` personality, covering 452 named entries across 483 source lines; early entries include osf_syscall, exit, fork, read, write, osf_old_open, close, osf_wait4.

Important APIs/types/functions: table initializers map syscall numbers to argument counts, trace flags, `SEN(...)` decoder handlers, and printable names. Flags observed here include CC, NF, PU, SI, TC, TCL, TD, TF, TFSF, TFST, TI, TLST.

Control flow: strace indexes this array after `arch_get_scno` and optional syscall-number shuffling, then dispatches the selected `SEN` decoder and applies table flags to path, fd, network, signal, process, stat, memory, IPC, and pure-call formatting behavior.

State/persistence behavior: compile-time dispatch metadata only; runtime state lives in `struct tcb` fields populated from registers and syscall arguments.

Dependencies/integration: depends on decoder symbols declared elsewhere in strace, architecture syscall numbering, generated common tables, and personality selection.

Risks/test signals: off-by-one numbering, stale ABI entries, or wrong flags produce incorrect syscall names/argument classes; test with known syscall-number traces, generated table checks, and cross-architecture comparison against Linux syscall headers.

Source-read signal: reviewed complete local file (483 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/alpha/syscallent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/alpha/userent.h -->
# sources/test-tools/strace/src/linux/alpha/userent.h

Purpose: defines `alpha` `ptrace(PEEKUSER)`/`struct user` offset names for strace's user-area decoders, with 65 visible entries.

Important APIs/types/functions: xlat initializer rows or `XLAT_UOFF` macros map offsets to register/user-field names; no executable functions are defined.

Control flow: ptrace/user-offset printing indexes these rows when a trace asks for user-register offsets.

State/persistence behavior: static lookup metadata only.

Dependencies/integration: consumed by strace xlat/table-generation code; includes userent0.h.

Risks/test signals: wrong offsets make `PTRACE_PEEKUSER` output misleading; validate against the architecture `struct user` layout and register-offset trace tests.

Source-read signal: reviewed complete local file (74 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/alpha/userent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/arc/arch_defs_.h -->
# sources/test-tools/strace/src/linux/arc/arch_defs_.h

Purpose: declares strace compile-time personality features for the `arc` Linux backend, including PERSONALITY0_AUDIT_ARCH, PERSONALITY0_AUDIT_ARCH.

Important APIs/types/functions: preprocessor macros control feature gates such as old mmap/select, UID16 syscalls, dedicated error registers, supported personalities, and audit arch tuples (AUDIT_ARCH_ARCOMPACTBE, 0 ; AUDIT_ARCH_ARCOMPACT, 0 ).

Control flow: no executable code. The main Linux backend includes this header while building architecture-specific syscall decoding and personality setup.

State/persistence behavior: static build-time configuration only; it influences how `struct tcb` register state is interpreted but stores no runtime state itself.

Dependencies/integration: depends on Linux audit architecture constants and may include generated base-number headers (no local includes).

Risks/test signals: incorrect feature macros select wrong syscall tables or legacy decoders; validate with architecture build tests, audit-personality checks, and traces of legacy mmap/select or UID16 syscalls when enabled.

Source-read signal: reviewed complete local file (5 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/arc/arch_defs_.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/arc/arch_regs.c -->
# sources/test-tools/strace/src/linux/arc/arch_regs.c

Purpose: defines the register storage and program-counter/stack-pointer access macros for the `arc` Linux strace backend.

Important APIs/types/functions: visible register contract includes macros ARCH_REGS_FOR_GETREGSET, ARCH_PC_REG, ARCH_SP_REG; functions none; notable register fields include architecture struct fields referenced through macros.

Control flow: generic register-fetch code populates the declared storage via `GETREGS`/`GETREGSET`, then syscall-entry/exit, signal, and stack helpers read the macros exported here.

State/persistence behavior: per-tracee register snapshots are held in static architecture globals for the duration of a decode step and refreshed from ptrace; nothing is persisted beyond the trace event.

Dependencies/integration: integrates with generic `get_regs`, `set_regs`, `get_stack_pointer`, syscall-argument extraction, and signal-frame helpers; includes architecture kernel register structs supplied by surrounding includes.

Risks/test signals: wrong register field mapping corrupts syscall numbers, arguments, PC/SP reporting, and injected return values; validate with ptrace register fetch/set tests and known syscall traces on the architecture.

Source-read signal: reviewed complete local file (11 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/arc/arch_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/arc/get_error.c -->
# sources/test-tools/strace/src/linux/arc/get_error.c

Purpose: translates the `arc` syscall return/error convention into `tcp->u_rval` and `tcp->u_error`.

Important APIs/types/functions: arch_get_error; key state includes `struct tcb`, `tcp->scno`, `tcp->u_arg`, `tcp->u_rval`, `tcp->u_error`, and register fields defined by included architecture helpers.

Control flow: on syscall exit it reads the architecture return/error register convention, optionally checks negated errno ranges or dedicated error flags, sets `u_rval=-1` for errors, and otherwise records the raw return value.

State/persistence behavior: mutates only the active trace control block and current ptrace register snapshot; any tracee register changes are applied immediately through ptrace helpers.

Dependencies/integration: participates in generic syscall enter/exit decoding; depends on negated_errno.h.

Risks/test signals: Test with successful syscalls, negated errno returns, and any architecture-specific dedicated error register path.

Source-read signal: reviewed complete local file (19 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/arc/get_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/arc/get_scno.c -->
# sources/test-tools/strace/src/linux/arc/get_scno.c

Purpose: extracts the current syscall number for the `arc` backend.

Important APIs/types/functions: arch_get_scno; key state includes `struct tcb`, `tcp->scno`, `tcp->u_arg`, `tcp->u_rval`, `tcp->u_error`, and register fields r8.

Control flow: on syscall entry it reads the ABI syscall-number register or user offset, may perform sanity checks for stray exits, then stores the result in `tcp->scno` and returns the generic status code.

State/persistence behavior: mutates only the active trace control block and current ptrace register snapshot; any tracee register changes are applied immediately through ptrace helpers.

Dependencies/integration: participates in generic syscall enter/exit decoding; depends on architecture register globals, ptrace helpers, and common tcb fields.

Risks/test signals: Test with representative syscall entries, invalid/out-of-range numbers, and personality-specific numbering when present.

Source-read signal: reviewed complete local file (14 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/arc/get_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/arc/get_syscall_args.c -->
# sources/test-tools/strace/src/linux/arc/get_syscall_args.c

Purpose: copies syscall arguments from `arc` register state or backing register-stack memory into `tcp->u_arg`.

Important APIs/types/functions: arch_get_syscall_args; key state includes `struct tcb`, `tcp->scno`, `tcp->u_arg`, `tcp->u_rval`, `tcp->u_error`, and register fields defined by included architecture helpers.

Control flow: after the syscall number is known, it reads up to `n_args(tcp)` or `MAX_ARGS` arguments from ABI-defined registers, compatibility helper code, or memory addresses derived from register-stack state, returning `1` on success or `-1` on fatal fetch failure.

State/persistence behavior: mutates only the active trace control block and current ptrace register snapshot; any tracee register changes are applied immediately through ptrace helpers.

Dependencies/integration: participates in generic syscall enter/exit decoding; depends on architecture register globals, ptrace helpers, and common tcb fields.

Risks/test signals: Test with six-argument syscalls, compatibility personalities, and ptrace permission/fault cases for memory-backed argument locations.

Source-read signal: reviewed complete local file (17 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/arc/get_syscall_args.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/arc/ioctls_arch0.h -->
# sources/test-tools/strace/src/linux/arc/ioctls_arch0.h

Purpose: provides the `arc` generated architecture ioctl table, with 0 initializer rows from architecture kernel headers; examples include no concrete ioctl names.

Important APIs/types/functions: each row is `{'header, name, direction, number, size'}` data consumed by the common ioctl xlat machinery; observed direction flags include _IOC_NONE-style entries.

Control flow: no executable flow; entries are compiled into lookup arrays that let `ioctl(2)` decoding map command numbers back to symbolic names and argument direction/size.

State/persistence behavior: immutable compile-time metadata only; it neither reads traced memory nor persists runtime state.

Dependencies/integration: generated from Linux UAPI headers by `ioctls_gen.sh` and consumed by the strace ioctl decoder alongside generic include tables.

Risks/test signals: stale generated rows or wrong command sizes cause misleading ioctl names or argument decoding; test by comparing generated tables with current UAPI headers and tracing representative architecture-specific ioctl calls.

Source-read signal: reviewed complete local file (1 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/arc/ioctls_arch0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/arc/ioctls_inc0.h -->
# sources/test-tools/strace/src/linux/arc/ioctls_inc0.h

Purpose: reuses shared strace architecture logic for `arc` by including `../32/ioctls_inc.h` from `ioctls_inc0.h`.

Important APIs/types/functions: this file exports the APIs provided by the included implementation rather than defining new local functions.

Control flow: the C preprocessor splices the target file into this architecture build, so runtime behavior is the shared implementation's behavior under this architecture's register/personality macros.

State/persistence behavior: no independent state; included code operates on the surrounding architecture register globals and `struct tcb` state.

Dependencies/integration: direct dependency on `../32/ioctls_inc.h` and the macro/register contract expected by that file.

Risks/test signals: changes in the shared implementation can silently affect this architecture; compile the architecture and run syscall/signal/ioctl traces that exercise the included path.

Source-read signal: reviewed complete local file (1 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/arc/ioctls_inc0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/arc/raw_syscall.h -->
# sources/test-tools/strace/src/linux/arc/raw_syscall.h

Purpose: implements a minimal zero-argument raw syscall helper for `arc`.

Important APIs/types/functions: raw_syscall_0, STRACE_RAW_SYSCALL_H, ARC_TRAP_INSN, ARC_TRAP_INSN, raw_syscall_0; notable register references include r8.

Control flow: loads the requested syscall number into the ABI register, executes the architecture trap instruction, records an error flag where the ABI exposes one, and returns the raw result register.

State/persistence behavior: operates on transient tracee/register/memory snapshots or compile-time metadata; persistent program state is not introduced here.

Dependencies/integration: Depends on inline assembly register constraints, trap instructions, clobber lists, and `kernel_ulong_t`.

Risks/test signals: incorrect constraints or clobbers can miscompile; test a harmless syscall such as getpid and an expected failing syscall on native hardware/toolchains.

Source-read signal: reviewed complete local file (39 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/arc/raw_syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/arc/set_error.c -->
# sources/test-tools/strace/src/linux/arc/set_error.c

Purpose: injects a synthetic syscall error or success result into `arc` tracee registers.

Important APIs/types/functions: arch_set_error, arch_set_success; key state includes `struct tcb`, `tcp->scno`, `tcp->u_arg`, `tcp->u_rval`, `tcp->u_error`, and register fields defined by included architecture helpers.

Control flow: `arch_set_error` writes the architecture error convention from `tcp->u_error`; `arch_set_success` writes `tcp->u_rval`; implementations either poke individual user offsets or call `set_regs` after mutating the saved register block.

State/persistence behavior: mutates only the active trace control block and current ptrace register snapshot; any tracee register changes are applied immediately through ptrace helpers.

Dependencies/integration: participates in generic syscall enter/exit decoding; depends on architecture register globals, ptrace helpers, and common tcb fields.

Risks/test signals: Test with syscall fault injection for both success and errno paths, including ESRCH/disappearing-tracee behavior where relevant.

Source-read signal: reviewed complete local file (20 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/arc/set_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/arc/set_scno.c -->
# sources/test-tools/strace/src/linux/arc/set_scno.c

Purpose: updates the tracee syscall number for `arc` syscall tampering/restart support.

Important APIs/types/functions: arch_set_scno; key state includes `struct tcb`, `tcp->scno`, `tcp->u_arg`, `tcp->u_rval`, `tcp->u_error`, and register fields r8.

Control flow: writes the requested syscall number into the architecture orig-syscall register using `upoke`, `set_regs`, or an architecture regset such as `NT_ARM_SYSTEM_CALL`.

State/persistence behavior: mutates only the active trace control block and current ptrace register snapshot; any tracee register changes are applied immediately through ptrace helpers.

Dependencies/integration: participates in generic syscall enter/exit decoding; depends on architecture register globals, ptrace helpers, and common tcb fields.

Risks/test signals: Test by rewriting a syscall number under ptrace and confirming the kernel executes/prints the replacement call.

Source-read signal: reviewed complete local file (15 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/arc/set_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/arc/syscallent.h -->
# sources/test-tools/strace/src/linux/arc/syscallent.h

Purpose: defines syscall table metadata for the `arc` personality, covering 5 named entries across 15 source lines; early entries include cacheflush, arc_settls, arc_gettls, sysfs, arc_usr_cmpxchg.

Important APIs/types/functions: table initializers map syscall numbers to argument counts, trace flags, `SEN(...)` decoder handlers, and printable names. Flags observed here include NF, PU.

Control flow: strace indexes this array after `arch_get_scno` and optional syscall-number shuffling, then dispatches the selected `SEN` decoder and applies table flags to path, fd, network, signal, process, stat, memory, IPC, and pure-call formatting behavior.

State/persistence behavior: compile-time dispatch metadata only; runtime state lives in `struct tcb` fields populated from registers and syscall arguments.

Dependencies/integration: depends on decoder symbols declared elsewhere in strace, architecture syscall numbering, generated common tables, and personality selection.

Risks/test signals: off-by-one numbering, stale ABI entries, or wrong flags produce incorrect syscall names/argument classes; test with known syscall-number traces, generated table checks, and cross-architecture comparison against Linux syscall headers.

Source-read signal: reviewed complete local file (15 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/arc/syscallent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/arm/arch_defs_.h -->
# sources/test-tools/strace/src/linux/arm/arch_defs_.h

Purpose: declares strace compile-time personality features for the `arm` Linux backend, including HAVE_ARCH_OLD_MMAP, HAVE_ARCH_OLD_SELECT, HAVE_ARCH_UID16_SYSCALLS, CAN_ARCH_BE_COMPAT_ON_64BIT_KERNEL, PERSONALITY0_AUDIT_ARCH, PERSONALITY0_AUDIT_ARCH.

Important APIs/types/functions: preprocessor macros control feature gates such as old mmap/select, UID16 syscalls, dedicated error registers, supported personalities, and audit arch tuples (AUDIT_ARCH_ARMEB, 0 ; AUDIT_ARCH_ARM, 0 ).

Control flow: no executable code. The main Linux backend includes this header while building architecture-specific syscall decoding and personality setup.

State/persistence behavior: static build-time configuration only; it influences how `struct tcb` register state is interpreted but stores no runtime state itself.

Dependencies/integration: depends on Linux audit architecture constants and may include generated base-number headers (no local includes).

Risks/test signals: incorrect feature macros select wrong syscall tables or legacy decoders; validate with architecture build tests, audit-personality checks, and traces of legacy mmap/select or UID16 syscalls when enabled.

Source-read signal: reviewed complete local file (16 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/arm/arch_defs_.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/arm/arch_prstatus_regset.c -->
# sources/test-tools/strace/src/linux/arm/arch_prstatus_regset.c

Purpose: pretty-prints `arm` regset payloads returned by ptrace/core-note style interfaces.

Important APIs/types/functions: arch_decode_prstatus_regset; notable register references include none in this file.

Control flow: rejects empty or misaligned buffers by printing the raw address, safely copies up to the known struct size from the tracee, prints fields that fit inside the supplied size, and marks extra trailing bytes with `more data follows`.

State/persistence behavior: operates on transient tracee/register/memory snapshots or compile-time metadata; persistent program state is not introduced here.

Dependencies/integration: Depends on `umoven_or_printaddr`, `PRINT_FIELD_X`, array printers, struct offset checks, and the companion regset typedef header.

Risks/test signals: field-order or alignment mistakes misdecode `PTRACE_GETREGSET` data; test short, exact-size, oversized, and misaligned regset buffers.

Source-read signal: reviewed complete local file (29 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/arm/arch_prstatus_regset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/arm/arch_prstatus_regset.h -->
# sources/test-tools/strace/src/linux/arm/arch_prstatus_regset.h

Purpose: declares the `arm` regset struct shape and enables the matching decoder.

Important APIs/types/functions: STRACE_ARCH_PRSTATUS_REGSET_H, HAVE_ARCH_PRSTATUS_REGSET; notable register references include none in this file.

Control flow: no executable flow; the typedef and `HAVE_ARCH_*` macro let generic code compile the architecture decoder.

State/persistence behavior: operates on transient tracee/register/memory snapshots or compile-time metadata; persistent program state is not introduced here.

Dependencies/integration: Depends on architecture kernel user register types or locally declared field order; includes no external header in this file.

Risks/test signals: typedef drift from kernel ABI breaks register dumps; compile with current headers and run ptrace regset decoding tests.

Source-read signal: reviewed complete local file (15 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/arm/arch_prstatus_regset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/arm/arch_regs.c -->
# sources/test-tools/strace/src/linux/arm/arch_regs.c

Purpose: defines the register storage and program-counter/stack-pointer access macros for the `arm` Linux strace backend.

Important APIs/types/functions: visible register contract includes macros ARCH_REGS_FOR_GETREGS, ARCH_PC_REG, ARCH_SP_REG; functions none; notable register fields include ARM_pc, ARM_sp.

Control flow: generic register-fetch code populates the declared storage via `GETREGS`/`GETREGSET`, then syscall-entry/exit, signal, and stack helpers read the macros exported here.

State/persistence behavior: per-tracee register snapshots are held in static architecture globals for the duration of a decode step and refreshed from ptrace; nothing is persisted beyond the trace event.

Dependencies/integration: integrates with generic `get_regs`, `set_regs`, `get_stack_pointer`, syscall-argument extraction, and signal-frame helpers; includes architecture kernel register structs supplied by surrounding includes.

Risks/test signals: wrong register field mapping corrupts syscall numbers, arguments, PC/SP reporting, and injected return values; validate with ptrace register fetch/set tests and known syscall traces on the architecture.

Source-read signal: reviewed complete local file (12 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/arm/arch_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/arm/arch_sigreturn.c -->
# sources/test-tools/strace/src/linux/arm/arch_sigreturn.c

Purpose: decodes signal mask restoration for `arm` `sigreturn`/`rt_sigreturn` handling.

Important APIs/types/functions: arch_sigreturn, SIZEOF_STRUCT_SIGINFO, SIZEOF_STRUCT_SIGCONTEXT, OFFSETOF_STRUCT_UCONTEXT_UC_SIGMASK; struct typedef count 0.

Control flow: the helper locates the signal frame from the current stack pointer or architecture context, reads the relevant frame/mask fields with safe `umove` helpers, and prints the restored signal mask.

State/persistence behavior: reads transient signal-frame data from tracee memory and prints it; no durable state is stored.

Dependencies/integration: integrates with `get_stack_pointer`, `umove_or_printaddr`, sigset printers, `ucontext_t`/`sigcontext`, and generic signal-return decoding.

Risks/test signals: frame offsets and padding are ABI-sensitive; validate with signal handler traces, blocked-mask restoration, and rt_sigreturn decoding on the architecture.

Source-read signal: reviewed complete local file (28 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/arm/arch_sigreturn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/arm/get_error.c -->
# sources/test-tools/strace/src/linux/arm/get_error.c

Purpose: translates the `arm` syscall return/error convention into `tcp->u_rval` and `tcp->u_error`.

Important APIs/types/functions: arch_get_error; key state includes `struct tcb`, `tcp->scno`, `tcp->u_arg`, `tcp->u_rval`, `tcp->u_error`, and register fields ARM_r0.

Control flow: on syscall exit it reads the architecture return/error register convention, optionally checks negated errno ranges or dedicated error flags, sets `u_rval=-1` for errors, and otherwise records the raw return value.

State/persistence behavior: mutates only the active trace control block and current ptrace register snapshot; any tracee register changes are applied immediately through ptrace helpers.

Dependencies/integration: participates in generic syscall enter/exit decoding; depends on negated_errno.h.

Risks/test signals: Test with successful syscalls, negated errno returns, and any architecture-specific dedicated error register path.

Source-read signal: reviewed complete local file (19 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/arm/get_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/arm/get_scno.c -->
# sources/test-tools/strace/src/linux/arm/get_scno.c

Purpose: extracts the current syscall number for the `arm` backend.

Important APIs/types/functions: arch_get_scno; key state includes `struct tcb`, `tcp->scno`, `tcp->u_arg`, `tcp->u_rval`, `tcp->u_error`, and register fields ARM_pc, ARM_r7.

Control flow: on syscall entry it reads the ABI syscall-number register or user offset, may perform sanity checks for stray exits, then stores the result in `tcp->scno` and returns the generic status code.

State/persistence behavior: mutates only the active trace control block and current ptrace register snapshot; any tracee register changes are applied immediately through ptrace helpers.

Dependencies/integration: participates in generic syscall enter/exit decoding; depends on architecture register globals, ptrace helpers, and common tcb fields.

Risks/test signals: Test with representative syscall entries, invalid/out-of-range numbers, and personality-specific numbering when present.

Source-read signal: reviewed complete local file (62 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/arm/get_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/arm/get_syscall_args.c -->
# sources/test-tools/strace/src/linux/arm/get_syscall_args.c

Purpose: copies syscall arguments from `arm` register state or backing register-stack memory into `tcp->u_arg`.

Important APIs/types/functions: arch_get_syscall_args; key state includes `struct tcb`, `tcp->scno`, `tcp->u_arg`, `tcp->u_rval`, `tcp->u_error`, and register fields uregs[0], uregs[1], uregs[2], uregs[3], uregs[4], uregs[5].

Control flow: after the syscall number is known, it reads up to `n_args(tcp)` or `MAX_ARGS` arguments from ABI-defined registers, compatibility helper code, or memory addresses derived from register-stack state, returning `1` on success or `-1` on fatal fetch failure.

State/persistence behavior: mutates only the active trace control block and current ptrace register snapshot; any tracee register changes are applied immediately through ptrace helpers.

Dependencies/integration: participates in generic syscall enter/exit decoding; depends on architecture register globals, ptrace helpers, and common tcb fields.

Risks/test signals: Test with six-argument syscalls, compatibility personalities, and ptrace permission/fault cases for memory-backed argument locations.

Source-read signal: reviewed complete local file (19 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/arm/get_syscall_args.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/arm/ioctls_arch0.h -->
# sources/test-tools/strace/src/linux/arm/ioctls_arch0.h

Purpose: provides the `arm` generated architecture ioctl table, with 1 initializer rows from asm/ioctls.h; examples include no concrete ioctl names.

Important APIs/types/functions: each row is `{'header, name, direction, number, size'}` data consumed by the common ioctl xlat machinery; observed direction flags include _IOC_NONE-style entries.

Control flow: no executable flow; entries are compiled into lookup arrays that let `ioctl(2)` decoding map command numbers back to symbolic names and argument direction/size.

State/persistence behavior: immutable compile-time metadata only; it neither reads traced memory nor persists runtime state.

Dependencies/integration: generated from Linux UAPI headers by `ioctls_gen.sh` and consumed by the strace ioctl decoder alongside generic include tables.

Risks/test signals: stale generated rows or wrong command sizes cause misleading ioctl names or argument decoding; test by comparing generated tables with current UAPI headers and tracing representative architecture-specific ioctl calls.

Source-read signal: reviewed complete local file (2 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/arm/ioctls_arch0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/arm/ioctls_inc0.h -->
# sources/test-tools/strace/src/linux/arm/ioctls_inc0.h

Purpose: reuses shared strace architecture logic for `arm` by including `../32/ioctls_inc.h` from `ioctls_inc0.h`.

Important APIs/types/functions: this file exports the APIs provided by the included implementation rather than defining new local functions.

Control flow: the C preprocessor splices the target file into this architecture build, so runtime behavior is the shared implementation's behavior under this architecture's register/personality macros.

State/persistence behavior: no independent state; included code operates on the surrounding architecture register globals and `struct tcb` state.

Dependencies/integration: direct dependency on `../32/ioctls_inc.h` and the macro/register contract expected by that file.

Risks/test signals: changes in the shared implementation can silently affect this architecture; compile the architecture and run syscall/signal/ioctl traces that exercise the included path.

Source-read signal: reviewed complete local file (1 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/arm/ioctls_inc0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/arm/nr_prefix.c -->
# sources/test-tools/strace/src/linux/arm/nr_prefix.c

Purpose: supplies the syscall-number prefix string for `arm` personality-specific syscall rendering.

Important APIs/types/functions: nr_prefix.c; notable register references include none in this file.

Control flow: generic unknown-syscall formatting calls the prefix helper before printing raw syscall numbers.

State/persistence behavior: operates on transient tracee/register/memory snapshots or compile-time metadata; persistent program state is not introduced here.

Dependencies/integration: Depends on active personality selection and shared prefix helper contracts.

Risks/test signals: test unknown syscall rendering in native and compat personalities.

Source-read signal: reviewed complete local file (19 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/arm/nr_prefix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/arm/raw_syscall.h -->
# sources/test-tools/strace/src/linux/arm/raw_syscall.h

Purpose: implements a minimal zero-argument raw syscall helper for `arm`.

Important APIs/types/functions: raw_syscall_0, STRACE_RAW_SYSCALL_H, raw_syscall_0; notable register references include none in this file.

Control flow: loads the requested syscall number into the ABI register, executes the architecture trap instruction, records an error flag where the ABI exposes one, and returns the raw result register.

State/persistence behavior: operates on transient tracee/register/memory snapshots or compile-time metadata; persistent program state is not introduced here.

Dependencies/integration: Depends on inline assembly register constraints, trap instructions, clobber lists, and `kernel_ulong_t`.

Risks/test signals: incorrect constraints or clobbers can miscompile; test a harmless syscall such as getpid and an expected failing syscall on native hardware/toolchains.

Source-read signal: reviewed complete local file (44 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/arm/raw_syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/arm/set_error.c -->
# sources/test-tools/strace/src/linux/arm/set_error.c

Purpose: injects a synthetic syscall error or success result into `arm` tracee registers.

Important APIs/types/functions: arch_set_error, arch_set_success; key state includes `struct tcb`, `tcp->scno`, `tcp->u_arg`, `tcp->u_rval`, `tcp->u_error`, and register fields ARM_r0.

Control flow: `arch_set_error` writes the architecture error convention from `tcp->u_error`; `arch_set_success` writes `tcp->u_rval`; implementations either poke individual user offsets or call `set_regs` after mutating the saved register block.

State/persistence behavior: mutates only the active trace control block and current ptrace register snapshot; any tracee register changes are applied immediately through ptrace helpers.

Dependencies/integration: participates in generic syscall enter/exit decoding; depends on architecture register globals, ptrace helpers, and common tcb fields.

Risks/test signals: Test with syscall fault injection for both success and errno paths, including ESRCH/disappearing-tracee behavior where relevant.

Source-read signal: reviewed complete local file (20 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/arm/set_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/arm/set_scno.c -->
# sources/test-tools/strace/src/linux/arm/set_scno.c

Purpose: updates the tracee syscall number for `arm` syscall tampering/restart support.

Important APIs/types/functions: arch_set_scno; key state includes `struct tcb`, `tcp->scno`, `tcp->u_arg`, `tcp->u_rval`, `tcp->u_error`, and register fields defined by included architecture helpers.

Control flow: writes the requested syscall number into the architecture orig-syscall register using `upoke`, `set_regs`, or an architecture regset such as `NT_ARM_SYSTEM_CALL`.

State/persistence behavior: mutates only the active trace control block and current ptrace register snapshot; any tracee register changes are applied immediately through ptrace helpers.

Dependencies/integration: participates in generic syscall enter/exit decoding; depends on architecture register globals, ptrace helpers, and common tcb fields.

Risks/test signals: Test by rewriting a syscall number under ptrace and confirming the kernel executes/prints the replacement call.

Source-read signal: reviewed complete local file (25 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/arm/set_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/arm/shuffle_scno.c -->
# sources/test-tools/strace/src/linux/arm/shuffle_scno.c

Purpose: translates raw `arm` syscall numbers into the table index space used by strace.

Important APIs/types/functions: shuffle_scno_pers, ARM_SECOND_SHUFFLED_SYSCALL; notable register references include none in this file.

Control flow: generic dispatch calls `shuffle_scno_pers`; implementations may leave native numbers unchanged, delegate to compat helpers, or xor/add a base offset after static assertions.

State/persistence behavior: operates on transient tracee/register/memory snapshots or compile-time metadata; persistent program state is not introduced here.

Dependencies/integration: Depends on syscall table size/base-number constants and personality id.

Risks/test signals: wrong shuffling dispatches to the wrong table; test boundary syscall numbers and personality-specific tables.

Source-read signal: reviewed complete local file (38 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/arm/shuffle_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/arm/syscallent.h -->
# sources/test-tools/strace/src/linux/arm/syscallent.h

Purpose: defines syscall table metadata for the `arm` personality, covering 405 named entries across 443 source lines; early entries include restart_syscall, exit, fork, read, write, open, close, waitpid.

Important APIs/types/functions: table initializers map syscall numbers to argument counts, trace flags, `SEN(...)` decoder handlers, and printable names. Flags observed here include CC, NF, PU, SI, TC, TCL, TD, TF, TFSF, TFST, TI, TLST.

Control flow: strace indexes this array after `arch_get_scno` and optional syscall-number shuffling, then dispatches the selected `SEN` decoder and applies table flags to path, fd, network, signal, process, stat, memory, IPC, and pure-call formatting behavior.

State/persistence behavior: compile-time dispatch metadata only; runtime state lives in `struct tcb` fields populated from registers and syscall arguments.

Dependencies/integration: depends on decoder symbols declared elsewhere in strace, architecture syscall numbering, generated common tables, and personality selection.

Risks/test signals: off-by-one numbering, stale ABI entries, or wrong flags produce incorrect syscall names/argument classes; test with known syscall-number traces, generated table checks, and cross-architecture comparison against Linux syscall headers.

Source-read signal: reviewed complete local file (443 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/arm/syscallent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/arm/userent.h -->
# sources/test-tools/strace/src/linux/arm/userent.h

Purpose: defines `arm` `ptrace(PEEKUSER)`/`struct user` offset names for strace's user-area decoders, with 28 visible entries.

Important APIs/types/functions: xlat initializer rows or `XLAT_UOFF` macros map offsets to register/user-field names; no executable functions are defined.

Control flow: ptrace/user-offset printing indexes these rows when a trace asks for user-register offsets.

State/persistence behavior: static lookup metadata only.

Dependencies/integration: consumed by strace xlat/table-generation code; includes userent0.h.

Risks/test signals: wrong offsets make `PTRACE_PEEKUSER` output misleading; validate against the architecture `struct user` layout and register-offset trace tests.

Source-read signal: reviewed complete local file (37 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/arm/userent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/avr32/arch_defs_.h -->
# sources/test-tools/strace/src/linux/avr32/arch_defs_.h

Purpose: declares strace compile-time personality features for the `avr32` Linux backend, including PERSONALITY0_AUDIT_ARCH.

Important APIs/types/functions: preprocessor macros control feature gates such as old mmap/select, UID16 syscalls, dedicated error registers, supported personalities, and audit arch tuples (EM_AVR32, 0 ).

Control flow: no executable code. The main Linux backend includes this header while building architecture-specific syscall decoding and personality setup.

State/persistence behavior: static build-time configuration only; it influences how `struct tcb` register state is interpreted but stores no runtime state itself.

Dependencies/integration: depends on Linux audit architecture constants and may include generated base-number headers (no local includes).

Risks/test signals: incorrect feature macros select wrong syscall tables or legacy decoders; validate with architecture build tests, audit-personality checks, and traces of legacy mmap/select or UID16 syscalls when enabled.

Source-read signal: reviewed complete local file (1 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/avr32/arch_defs_.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/avr32/arch_regs.c -->
# sources/test-tools/strace/src/linux/avr32/arch_regs.c

Purpose: defines the register storage and program-counter/stack-pointer access macros for the `avr32` Linux strace backend.

Important APIs/types/functions: visible register contract includes macros ARCH_REGS_FOR_GETREGS, ARCH_PC_REG, ARCH_SP_REG; functions none; notable register fields include architecture struct fields referenced through macros.

Control flow: generic register-fetch code populates the declared storage via `GETREGS`/`GETREGSET`, then syscall-entry/exit, signal, and stack helpers read the macros exported here.

State/persistence behavior: per-tracee register snapshots are held in static architecture globals for the duration of a decode step and refreshed from ptrace; nothing is persisted beyond the trace event.

Dependencies/integration: integrates with generic `get_regs`, `set_regs`, `get_stack_pointer`, syscall-argument extraction, and signal-frame helpers; includes architecture kernel register structs supplied by surrounding includes.

Risks/test signals: wrong register field mapping corrupts syscall numbers, arguments, PC/SP reporting, and injected return values; validate with ptrace register fetch/set tests and known syscall traces on the architecture.

Source-read signal: reviewed complete local file (11 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/avr32/arch_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/avr32/get_error.c -->
# sources/test-tools/strace/src/linux/avr32/get_error.c

Purpose: translates the `avr32` syscall return/error convention into `tcp->u_rval` and `tcp->u_error`.

Important APIs/types/functions: arch_get_error; key state includes `struct tcb`, `tcp->scno`, `tcp->u_arg`, `tcp->u_rval`, `tcp->u_error`, and register fields defined by included architecture helpers.

Control flow: on syscall exit it reads the architecture return/error register convention, optionally checks negated errno ranges or dedicated error flags, sets `u_rval=-1` for errors, and otherwise records the raw return value.

State/persistence behavior: mutates only the active trace control block and current ptrace register snapshot; any tracee register changes are applied immediately through ptrace helpers.

Dependencies/integration: participates in generic syscall enter/exit decoding; depends on negated_errno.h.

Risks/test signals: Test with successful syscalls, negated errno returns, and any architecture-specific dedicated error register path.

Source-read signal: reviewed complete local file (19 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/avr32/get_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/avr32/get_scno.c -->
# sources/test-tools/strace/src/linux/avr32/get_scno.c

Purpose: extracts the current syscall number for the `avr32` backend.

Important APIs/types/functions: arch_get_scno; key state includes `struct tcb`, `tcp->scno`, `tcp->u_arg`, `tcp->u_rval`, `tcp->u_error`, and register fields r8.

Control flow: on syscall entry it reads the ABI syscall-number register or user offset, may perform sanity checks for stray exits, then stores the result in `tcp->scno` and returns the generic status code.

State/persistence behavior: mutates only the active trace control block and current ptrace register snapshot; any tracee register changes are applied immediately through ptrace helpers.

Dependencies/integration: participates in generic syscall enter/exit decoding; depends on architecture register globals, ptrace helpers, and common tcb fields.

Risks/test signals: Test with representative syscall entries, invalid/out-of-range numbers, and personality-specific numbering when present.

Source-read signal: reviewed complete local file (14 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/avr32/get_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/avr32/get_syscall_args.c -->
# sources/test-tools/strace/src/linux/avr32/get_syscall_args.c

Purpose: copies syscall arguments from `avr32` register state or backing register-stack memory into `tcp->u_arg`.

Important APIs/types/functions: arch_get_syscall_args; key state includes `struct tcb`, `tcp->scno`, `tcp->u_arg`, `tcp->u_rval`, `tcp->u_error`, and register fields r10.

Control flow: after the syscall number is known, it reads up to `n_args(tcp)` or `MAX_ARGS` arguments from ABI-defined registers, compatibility helper code, or memory addresses derived from register-stack state, returning `1` on success or `-1` on fatal fetch failure.

State/persistence behavior: mutates only the active trace control block and current ptrace register snapshot; any tracee register changes are applied immediately through ptrace helpers.

Dependencies/integration: participates in generic syscall enter/exit decoding; depends on architecture register globals, ptrace helpers, and common tcb fields.

Risks/test signals: Test with six-argument syscalls, compatibility personalities, and ptrace permission/fault cases for memory-backed argument locations.

Source-read signal: reviewed complete local file (19 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/avr32/get_syscall_args.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/avr32/ioctls_arch0.h -->
# sources/test-tools/strace/src/linux/avr32/ioctls_arch0.h

Purpose: provides the `avr32` generated architecture ioctl table, with 0 initializer rows from architecture kernel headers; examples include no concrete ioctl names.

Important APIs/types/functions: each row is `{'header, name, direction, number, size'}` data consumed by the common ioctl xlat machinery; observed direction flags include _IOC_NONE-style entries.

Control flow: no executable flow; entries are compiled into lookup arrays that let `ioctl(2)` decoding map command numbers back to symbolic names and argument direction/size.

State/persistence behavior: immutable compile-time metadata only; it neither reads traced memory nor persists runtime state.

Dependencies/integration: generated from Linux UAPI headers by `ioctls_gen.sh` and consumed by the strace ioctl decoder alongside generic include tables.

Risks/test signals: stale generated rows or wrong command sizes cause misleading ioctl names or argument decoding; test by comparing generated tables with current UAPI headers and tracing representative architecture-specific ioctl calls.

Source-read signal: reviewed complete local file (1 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/avr32/ioctls_arch0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/avr32/ioctls_inc0.h -->
# sources/test-tools/strace/src/linux/avr32/ioctls_inc0.h

Purpose: reuses shared strace architecture logic for `avr32` by including `../32/ioctls_inc.h` from `ioctls_inc0.h`.

Important APIs/types/functions: this file exports the APIs provided by the included implementation rather than defining new local functions.

Control flow: the C preprocessor splices the target file into this architecture build, so runtime behavior is the shared implementation's behavior under this architecture's register/personality macros.

State/persistence behavior: no independent state; included code operates on the surrounding architecture register globals and `struct tcb` state.

Dependencies/integration: direct dependency on `../32/ioctls_inc.h` and the macro/register contract expected by that file.

Risks/test signals: changes in the shared implementation can silently affect this architecture; compile the architecture and run syscall/signal/ioctl traces that exercise the included path.

Source-read signal: reviewed complete local file (1 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/avr32/ioctls_inc0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/avr32/raw_syscall.h -->
# sources/test-tools/strace/src/linux/avr32/raw_syscall.h

Purpose: implements a minimal zero-argument raw syscall helper for `avr32`.

Important APIs/types/functions: raw_syscall_0, STRACE_RAW_SYSCALL_H, raw_syscall_0; notable register references include r8.

Control flow: loads the requested syscall number into the ABI register, executes the architecture trap instruction, records an error flag where the ABI exposes one, and returns the raw result register.

State/persistence behavior: operates on transient tracee/register/memory snapshots or compile-time metadata; persistent program state is not introduced here.

Dependencies/integration: Depends on inline assembly register constraints, trap instructions, clobber lists, and `kernel_ulong_t`.

Risks/test signals: incorrect constraints or clobbers can miscompile; test a harmless syscall such as getpid and an expected failing syscall on native hardware/toolchains.

Source-read signal: reviewed complete local file (29 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/avr32/raw_syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/avr32/set_error.c -->
# sources/test-tools/strace/src/linux/avr32/set_error.c

Purpose: injects a synthetic syscall error or success result into `avr32` tracee registers.

Important APIs/types/functions: arch_set_error, arch_set_success; key state includes `struct tcb`, `tcp->scno`, `tcp->u_arg`, `tcp->u_rval`, `tcp->u_error`, and register fields defined by included architecture helpers.

Control flow: `arch_set_error` writes the architecture error convention from `tcp->u_error`; `arch_set_success` writes `tcp->u_rval`; implementations either poke individual user offsets or call `set_regs` after mutating the saved register block.

State/persistence behavior: mutates only the active trace control block and current ptrace register snapshot; any tracee register changes are applied immediately through ptrace helpers.

Dependencies/integration: participates in generic syscall enter/exit decoding; depends on architecture register globals, ptrace helpers, and common tcb fields.

Risks/test signals: Test with syscall fault injection for both success and errno paths, including ESRCH/disappearing-tracee behavior where relevant.

Source-read signal: reviewed complete local file (20 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/avr32/set_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/avr32/set_scno.c -->
# sources/test-tools/strace/src/linux/avr32/set_scno.c

Purpose: updates the tracee syscall number for `avr32` syscall tampering/restart support.

Important APIs/types/functions: arch_set_scno; key state includes `struct tcb`, `tcp->scno`, `tcp->u_arg`, `tcp->u_rval`, `tcp->u_error`, and register fields r8.

Control flow: writes the requested syscall number into the architecture orig-syscall register using `upoke`, `set_regs`, or an architecture regset such as `NT_ARM_SYSTEM_CALL`.

State/persistence behavior: mutates only the active trace control block and current ptrace register snapshot; any tracee register changes are applied immediately through ptrace helpers.

Dependencies/integration: participates in generic syscall enter/exit decoding; depends on architecture register globals, ptrace helpers, and common tcb fields.

Risks/test signals: Test by rewriting a syscall number under ptrace and confirming the kernel executes/prints the replacement call.

Source-read signal: reviewed complete local file (15 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/avr32/set_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/avr32/syscallent.h -->
# sources/test-tools/strace/src/linux/avr32/syscallent.h

Purpose: defines syscall table metadata for the `avr32` personality, covering 329 named entries across 339 source lines; early entries include restart_syscall, exit, fork, read, write, open, close, umask.

Important APIs/types/functions: table initializers map syscall numbers to argument counts, trace flags, `SEN(...)` decoder handlers, and printable names. Flags observed here include CC, NF, PU, SI, TC, TCL, TD, TF, TFSF, TFST, TI, TLST.

Control flow: strace indexes this array after `arch_get_scno` and optional syscall-number shuffling, then dispatches the selected `SEN` decoder and applies table flags to path, fd, network, signal, process, stat, memory, IPC, and pure-call formatting behavior.

State/persistence behavior: compile-time dispatch metadata only; runtime state lives in `struct tcb` fields populated from registers and syscall arguments.

Dependencies/integration: depends on decoder symbols declared elsewhere in strace, architecture syscall numbering, generated common tables, and personality selection.

Risks/test signals: off-by-one numbering, stale ABI entries, or wrong flags produce incorrect syscall names/argument classes; test with known syscall-number traces, generated table checks, and cross-architecture comparison against Linux syscall headers.

Source-read signal: reviewed complete local file (339 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/avr32/syscallent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/avr32/userent.h -->
# sources/test-tools/strace/src/linux/avr32/userent.h

Purpose: defines `avr32` `ptrace(PEEKUSER)`/`struct user` offset names for strace's user-area decoders, with 28 visible entries.

Important APIs/types/functions: xlat initializer rows or `XLAT_UOFF` macros map offsets to register/user-field names; no executable functions are defined.

Control flow: ptrace/user-offset printing indexes these rows when a trace asks for user-register offsets.

State/persistence behavior: static lookup metadata only.

Dependencies/integration: consumed by strace xlat/table-generation code; includes userent0.h.

Risks/test signals: wrong offsets make `PTRACE_PEEKUSER` output misleading; validate against the architecture `struct user` layout and register-offset trace tests.

Source-read signal: reviewed complete local file (37 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/avr32/userent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/bfin/arch_defs_.h -->
# sources/test-tools/strace/src/linux/bfin/arch_defs_.h

Purpose: declares strace compile-time personality features for the `bfin` Linux backend, including HAVE_ARCH_OLD_SELECT, HAVE_ARCH_UID16_SYSCALLS, PERSONALITY0_AUDIT_ARCH.

Important APIs/types/functions: preprocessor macros control feature gates such as old mmap/select, UID16 syscalls, dedicated error registers, supported personalities, and audit arch tuples (EM_BLACKFIN|__AUDIT_ARCH_LE, 0 ).

Control flow: no executable code. The main Linux backend includes this header while building architecture-specific syscall decoding and personality setup.

State/persistence behavior: static build-time configuration only; it influences how `struct tcb` register state is interpreted but stores no runtime state itself.

Dependencies/integration: depends on Linux audit architecture constants and may include generated base-number headers (no local includes).

Risks/test signals: incorrect feature macros select wrong syscall tables or legacy decoders; validate with architecture build tests, audit-personality checks, and traces of legacy mmap/select or UID16 syscalls when enabled.

Source-read signal: reviewed complete local file (10 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/bfin/arch_defs_.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/bfin/arch_regs.c -->
# sources/test-tools/strace/src/linux/bfin/arch_regs.c

Purpose: defines the register storage and program-counter/stack-pointer access macros for the `bfin` Linux strace backend.

Important APIs/types/functions: visible register contract includes macros ARCH_PC_PEEK_ADDR, ARCH_SP_PEEK_ADDR; functions none; notable register fields include architecture struct fields referenced through macros.

Control flow: generic register-fetch code populates the declared storage via `GETREGS`/`GETREGSET`, then syscall-entry/exit, signal, and stack helpers read the macros exported here.

State/persistence behavior: per-tracee register snapshots are held in static architecture globals for the duration of a decode step and refreshed from ptrace; nothing is persisted beyond the trace event.

Dependencies/integration: integrates with generic `get_regs`, `set_regs`, `get_stack_pointer`, syscall-argument extraction, and signal-frame helpers; includes architecture kernel register structs supplied by surrounding includes.

Risks/test signals: wrong register field mapping corrupts syscall numbers, arguments, PC/SP reporting, and injected return values; validate with ptrace register fetch/set tests and known syscall traces on the architecture.

Source-read signal: reviewed complete local file (10 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/bfin/arch_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/bfin/get_error.c -->
# sources/test-tools/strace/src/linux/bfin/get_error.c

Purpose: translates the `bfin` syscall return/error convention into `tcp->u_rval` and `tcp->u_error`.

Important APIs/types/functions: arch_get_error; key state includes `struct tcb`, `tcp->scno`, `tcp->u_arg`, `tcp->u_rval`, `tcp->u_error`, and register fields defined by included architecture helpers.

Control flow: on syscall exit it reads the architecture return/error register convention, optionally checks negated errno ranges or dedicated error flags, sets `u_rval=-1` for errors, and otherwise records the raw return value.

State/persistence behavior: mutates only the active trace control block and current ptrace register snapshot; any tracee register changes are applied immediately through ptrace helpers.

Dependencies/integration: participates in generic syscall enter/exit decoding; depends on negated_errno.h.

Risks/test signals: Test with successful syscalls, negated errno returns, and any architecture-specific dedicated error register path.

Source-read signal: reviewed complete local file (19 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/bfin/get_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/bfin/get_scno.c -->
# sources/test-tools/strace/src/linux/bfin/get_scno.c

Purpose: extracts the current syscall number for the `bfin` backend.

Important APIs/types/functions: arch_get_scno; key state includes `struct tcb`, `tcp->scno`, `tcp->u_arg`, `tcp->u_rval`, `tcp->u_error`, and register fields defined by included architecture helpers.

Control flow: on syscall entry it reads the ABI syscall-number register or user offset, may perform sanity checks for stray exits, then stores the result in `tcp->scno` and returns the generic status code.

State/persistence behavior: mutates only the active trace control block and current ptrace register snapshot; any tracee register changes are applied immediately through ptrace helpers.

Dependencies/integration: participates in generic syscall enter/exit decoding; depends on architecture register globals, ptrace helpers, and common tcb fields.

Risks/test signals: Test with representative syscall entries, invalid/out-of-range numbers, and personality-specific numbering when present.

Source-read signal: reviewed complete local file (13 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/bfin/get_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/bfin/get_syscall_args.c -->
# sources/test-tools/strace/src/linux/bfin/get_syscall_args.c

Purpose: copies syscall arguments from `bfin` register state or backing register-stack memory into `tcp->u_arg`.

Important APIs/types/functions: arch_get_syscall_args; key state includes `struct tcb`, `tcp->scno`, `tcp->u_arg`, `tcp->u_rval`, `tcp->u_error`, and register fields defined by included architecture helpers.

Control flow: after the syscall number is known, it reads up to `n_args(tcp)` or `MAX_ARGS` arguments from ABI-defined registers, compatibility helper code, or memory addresses derived from register-stack state, returning `1` on success or `-1` on fatal fetch failure.

State/persistence behavior: mutates only the active trace control block and current ptrace register snapshot; any tracee register changes are applied immediately through ptrace helpers.

Dependencies/integration: participates in generic syscall enter/exit decoding; depends on architecture register globals, ptrace helpers, and common tcb fields.

Risks/test signals: Test with six-argument syscalls, compatibility personalities, and ptrace permission/fault cases for memory-backed argument locations.

Source-read signal: reviewed complete local file (20 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/bfin/get_syscall_args.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/bfin/get_syscall_result.c -->
# sources/test-tools/strace/src/linux/bfin/get_syscall_result.c

Purpose: fetches result registers needed by `bfin` before generic syscall-exit decoding.

Important APIs/types/functions: get_syscall_result_regs; key state includes `struct tcb`, `tcp->scno`, `tcp->u_arg`, `tcp->u_rval`, `tcp->u_error`, and register fields defined by included architecture helpers.

Control flow: reads the return and error-indicator registers from ptrace into static globals and reports failure if either fetch fails.

State/persistence behavior: mutates only the active trace control block and current ptrace register snapshot; any tracee register changes are applied immediately through ptrace helpers.

Dependencies/integration: participates in generic syscall enter/exit decoding; depends on architecture register globals, ptrace helpers, and common tcb fields.

Risks/test signals: Test syscall exits for both success and failure, including ptrace read errors.

Source-read signal: reviewed complete local file (12 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/bfin/get_syscall_result.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/bfin/ioctls_arch0.h -->
# sources/test-tools/strace/src/linux/bfin/ioctls_arch0.h

Purpose: provides the `bfin` generated architecture ioctl table, with 11 initializer rows from asm/bfin_simple_timer.h, asm/bfin_sport.h, asm/ioctls.h; examples include BFIN_SIMPLE_TIMER_READ, BFIN_SIMPLE_TIMER_READ_COUNTER, BFIN_SIMPLE_TIMER_SET_MODE, BFIN_SIMPLE_TIMER_SET_PERIOD, BFIN_SIMPLE_TIMER_SET_WIDTH, BFIN_SIMPLE_TIMER_START.

Important APIs/types/functions: each row is `{'header, name, direction, number, size'}` data consumed by the common ioctl xlat machinery; observed direction flags include _IOC_NONE, _IOC_READ, _IOC_WRITE.

Control flow: no executable flow; entries are compiled into lookup arrays that let `ioctl(2)` decoding map command numbers back to symbolic names and argument direction/size.

State/persistence behavior: immutable compile-time metadata only; it neither reads traced memory nor persists runtime state.

Dependencies/integration: generated from Linux UAPI headers by `ioctls_gen.sh` and consumed by the strace ioctl decoder alongside generic include tables.

Risks/test signals: stale generated rows or wrong command sizes cause misleading ioctl names or argument decoding; test by comparing generated tables with current UAPI headers and tracing representative architecture-specific ioctl calls.

Source-read signal: reviewed complete local file (12 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/bfin/ioctls_arch0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/bfin/ioctls_inc0.h -->
# sources/test-tools/strace/src/linux/bfin/ioctls_inc0.h

Purpose: reuses shared strace architecture logic for `bfin` by including `../32/ioctls_inc.h` from `ioctls_inc0.h`.

Important APIs/types/functions: this file exports the APIs provided by the included implementation rather than defining new local functions.

Control flow: the C preprocessor splices the target file into this architecture build, so runtime behavior is the shared implementation's behavior under this architecture's register/personality macros.

State/persistence behavior: no independent state; included code operates on the surrounding architecture register globals and `struct tcb` state.

Dependencies/integration: direct dependency on `../32/ioctls_inc.h` and the macro/register contract expected by that file.

Risks/test signals: changes in the shared implementation can silently affect this architecture; compile the architecture and run syscall/signal/ioctl traces that exercise the included path.

Source-read signal: reviewed complete local file (1 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/bfin/ioctls_inc0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/bfin/raw_syscall.h -->
# sources/test-tools/strace/src/linux/bfin/raw_syscall.h

Purpose: implements a minimal zero-argument raw syscall helper for `bfin`.

Important APIs/types/functions: raw_syscall_0, STRACE_RAW_SYSCALL_H, raw_syscall_0; notable register references include none in this file.

Control flow: loads the requested syscall number into the ABI register, executes the architecture trap instruction, records an error flag where the ABI exposes one, and returns the raw result register.

State/persistence behavior: operates on transient tracee/register/memory snapshots or compile-time metadata; persistent program state is not introduced here.

Dependencies/integration: Depends on inline assembly register constraints, trap instructions, clobber lists, and `kernel_ulong_t`.

Risks/test signals: incorrect constraints or clobbers can miscompile; test a harmless syscall such as getpid and an expected failing syscall on native hardware/toolchains.

Source-read signal: reviewed complete local file (28 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/bfin/raw_syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/bfin/rt_sigframe.h -->
# sources/test-tools/strace/src/linux/bfin/rt_sigframe.h

Purpose: defines the `bfin` realtime signal-frame layout used by strace.

Important APIs/types/functions: STRACE_RT_SIGFRAME_H; struct typedef count 1.

Control flow: no direct runtime flow in the header; generic frame decoders use the typedef and offset macros when reading tracee memory.

State/persistence behavior: reads transient signal-frame data from tracee memory and prints it; no durable state is stored.

Dependencies/integration: integrates with `get_stack_pointer`, `umove_or_printaddr`, sigset printers, `ucontext_t`/`sigcontext`, and generic signal-return decoding.

Risks/test signals: frame offsets and padding are ABI-sensitive; validate with signal handler traces, blocked-mask restoration, and rt_sigreturn decoding on the architecture.

Source-read signal: reviewed complete local file (22 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/bfin/rt_sigframe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/bfin/set_error.c -->
# sources/test-tools/strace/src/linux/bfin/set_error.c

Purpose: injects a synthetic syscall error or success result into `bfin` tracee registers.

Important APIs/types/functions: arch_set_error, arch_set_success; key state includes `struct tcb`, `tcp->scno`, `tcp->u_arg`, `tcp->u_rval`, `tcp->u_error`, and register fields defined by included architecture helpers.

Control flow: `arch_set_error` writes the architecture error convention from `tcp->u_error`; `arch_set_success` writes `tcp->u_rval`; implementations either poke individual user offsets or call `set_regs` after mutating the saved register block.

State/persistence behavior: mutates only the active trace control block and current ptrace register snapshot; any tracee register changes are applied immediately through ptrace helpers.

Dependencies/integration: participates in generic syscall enter/exit decoding; depends on architecture register globals, ptrace helpers, and common tcb fields.

Risks/test signals: Test with syscall fault injection for both success and errno paths, including ESRCH/disappearing-tracee behavior where relevant.

Source-read signal: reviewed complete local file (20 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/bfin/set_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/bfin/set_scno.c -->
# sources/test-tools/strace/src/linux/bfin/set_scno.c

Purpose: updates the tracee syscall number for `bfin` syscall tampering/restart support.

Important APIs/types/functions: arch_set_scno; key state includes `struct tcb`, `tcp->scno`, `tcp->u_arg`, `tcp->u_rval`, `tcp->u_error`, and register fields defined by included architecture helpers.

Control flow: writes the requested syscall number into the architecture orig-syscall register using `upoke`, `set_regs`, or an architecture regset such as `NT_ARM_SYSTEM_CALL`.

State/persistence behavior: mutates only the active trace control block and current ptrace register snapshot; any tracee register changes are applied immediately through ptrace helpers.

Dependencies/integration: participates in generic syscall enter/exit decoding; depends on architecture register globals, ptrace helpers, and common tcb fields.

Risks/test signals: Test by rewriting a syscall number under ptrace and confirming the kernel executes/prints the replacement call.

Source-read signal: reviewed complete local file (12 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/bfin/set_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/bfin/syscallent.h -->
# sources/test-tools/strace/src/linux/bfin/syscallent.h

Purpose: defines syscall table metadata for the `bfin` personality, covering 391 named entries across 401 source lines; early entries include restart_syscall, exit, fork, read, write, open, close, waitpid.

Important APIs/types/functions: table initializers map syscall numbers to argument counts, trace flags, `SEN(...)` decoder handlers, and printable names. Flags observed here include CC, NF, PU, SI, TC, TCL, TD, TF, TFSF, TFST, TI, TLST.

Control flow: strace indexes this array after `arch_get_scno` and optional syscall-number shuffling, then dispatches the selected `SEN` decoder and applies table flags to path, fd, network, signal, process, stat, memory, IPC, and pure-call formatting behavior.

State/persistence behavior: compile-time dispatch metadata only; runtime state lives in `struct tcb` fields populated from registers and syscall arguments.

Dependencies/integration: depends on decoder symbols declared elsewhere in strace, architecture syscall numbering, generated common tables, and personality selection.

Risks/test signals: off-by-one numbering, stale ABI entries, or wrong flags produce incorrect syscall names/argument classes; test with known syscall-number traces, generated table checks, and cross-architecture comparison against Linux syscall headers.

Source-read signal: reviewed complete local file (401 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/bfin/syscallent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/bfin/userent.h -->
# sources/test-tools/strace/src/linux/bfin/userent.h

Purpose: defines `bfin` `ptrace(PEEKUSER)`/`struct user` offset names for strace's user-area decoders, with 8 visible entries.

Important APIs/types/functions: xlat initializer rows or `XLAT_UOFF` macros map offsets to register/user-field names; no executable functions are defined.

Control flow: ptrace/user-offset printing indexes these rows when a trace asks for user-register offsets.

State/persistence behavior: static lookup metadata only.

Dependencies/integration: consumed by strace xlat/table-generation code; includes userent0.h.

Risks/test signals: wrong offsets make `PTRACE_PEEKUSER` output misleading; validate against the architecture `struct user` layout and register-offset trace tests.

Source-read signal: reviewed complete local file (16 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/bfin/userent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/csky/arch_defs_.h -->
# sources/test-tools/strace/src/linux/csky/arch_defs_.h

Purpose: declares strace compile-time personality features for the `csky` Linux backend, including PERSONALITY0_AUDIT_ARCH.

Important APIs/types/functions: preprocessor macros control feature gates such as old mmap/select, UID16 syscalls, dedicated error registers, supported personalities, and audit arch tuples (AUDIT_ARCH_CSKY, 0 ).

Control flow: no executable code. The main Linux backend includes this header while building architecture-specific syscall decoding and personality setup.

State/persistence behavior: static build-time configuration only; it influences how `struct tcb` register state is interpreted but stores no runtime state itself.

Dependencies/integration: depends on Linux audit architecture constants and may include generated base-number headers (no local includes).

Risks/test signals: incorrect feature macros select wrong syscall tables or legacy decoders; validate with architecture build tests, audit-personality checks, and traces of legacy mmap/select or UID16 syscalls when enabled.

Source-read signal: reviewed complete local file (1 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/csky/arch_defs_.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/csky/arch_regs.c -->
# sources/test-tools/strace/src/linux/csky/arch_regs.c

Purpose: defines the register storage and program-counter/stack-pointer access macros for the `csky` Linux strace backend.

Important APIs/types/functions: visible register contract includes macros ARCH_REGS_FOR_GETREGSET, ARCH_PC_REG, ARCH_SP_REG; functions none; notable register fields include architecture struct fields referenced through macros.

Control flow: generic register-fetch code populates the declared storage via `GETREGS`/`GETREGSET`, then syscall-entry/exit, signal, and stack helpers read the macros exported here.

State/persistence behavior: per-tracee register snapshots are held in static architecture globals for the duration of a decode step and refreshed from ptrace; nothing is persisted beyond the trace event.

Dependencies/integration: integrates with generic `get_regs`, `set_regs`, `get_stack_pointer`, syscall-argument extraction, and signal-frame helpers; includes architecture kernel register structs supplied by surrounding includes.

Risks/test signals: wrong register field mapping corrupts syscall numbers, arguments, PC/SP reporting, and injected return values; validate with ptrace register fetch/set tests and known syscall traces on the architecture.

Source-read signal: reviewed complete local file (12 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/csky/arch_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/csky/get_error.c -->
# sources/test-tools/strace/src/linux/csky/get_error.c

Purpose: translates the `csky` syscall return/error convention into `tcp->u_rval` and `tcp->u_error`.

Important APIs/types/functions: arch_get_error; key state includes `struct tcb`, `tcp->scno`, `tcp->u_arg`, `tcp->u_rval`, `tcp->u_error`, and register fields defined by included architecture helpers.

Control flow: on syscall exit it reads the architecture return/error register convention, optionally checks negated errno ranges or dedicated error flags, sets `u_rval=-1` for errors, and otherwise records the raw return value.

State/persistence behavior: mutates only the active trace control block and current ptrace register snapshot; any tracee register changes are applied immediately through ptrace helpers.

Dependencies/integration: participates in generic syscall enter/exit decoding; depends on negated_errno.h.

Risks/test signals: Test with successful syscalls, negated errno returns, and any architecture-specific dedicated error register path.

Source-read signal: reviewed complete local file (18 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/csky/get_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/csky/get_scno.c -->
# sources/test-tools/strace/src/linux/csky/get_scno.c

Purpose: extracts the current syscall number for the `csky` backend.

Important APIs/types/functions: arch_get_scno; key state includes `struct tcb`, `tcp->scno`, `tcp->u_arg`, `tcp->u_rval`, `tcp->u_error`, and register fields regs[3].

Control flow: on syscall entry it reads the ABI syscall-number register or user offset, may perform sanity checks for stray exits, then stores the result in `tcp->scno` and returns the generic status code.

State/persistence behavior: mutates only the active trace control block and current ptrace register snapshot; any tracee register changes are applied immediately through ptrace helpers.

Dependencies/integration: participates in generic syscall enter/exit decoding; depends on architecture register globals, ptrace helpers, and common tcb fields.

Risks/test signals: Test with representative syscall entries, invalid/out-of-range numbers, and personality-specific numbering when present.

Source-read signal: reviewed complete local file (18 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/csky/get_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/csky/get_syscall_args.c -->
# sources/test-tools/strace/src/linux/csky/get_syscall_args.c

Purpose: copies syscall arguments from `csky` register state or backing register-stack memory into `tcp->u_arg`.

Important APIs/types/functions: arch_get_syscall_args; key state includes `struct tcb`, `tcp->scno`, `tcp->u_arg`, `tcp->u_rval`, `tcp->u_error`, and register fields regs[0], regs[1].

Control flow: after the syscall number is known, it reads up to `n_args(tcp)` or `MAX_ARGS` arguments from ABI-defined registers, compatibility helper code, or memory addresses derived from register-stack state, returning `1` on success or `-1` on fatal fetch failure.

State/persistence behavior: mutates only the active trace control block and current ptrace register snapshot; any tracee register changes are applied immediately through ptrace helpers.

Dependencies/integration: participates in generic syscall enter/exit decoding; depends on architecture register globals, ptrace helpers, and common tcb fields.

Risks/test signals: Test with six-argument syscalls, compatibility personalities, and ptrace permission/fault cases for memory-backed argument locations.

Source-read signal: reviewed complete local file (19 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/csky/get_syscall_args.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/csky/ioctls_arch0.h -->
# sources/test-tools/strace/src/linux/csky/ioctls_arch0.h

Purpose: provides the `csky` generated architecture ioctl table, with 0 initializer rows from architecture kernel headers; examples include no concrete ioctl names.

Important APIs/types/functions: each row is `{'header, name, direction, number, size'}` data consumed by the common ioctl xlat machinery; observed direction flags include _IOC_NONE-style entries.

Control flow: no executable flow; entries are compiled into lookup arrays that let `ioctl(2)` decoding map command numbers back to symbolic names and argument direction/size.

State/persistence behavior: immutable compile-time metadata only; it neither reads traced memory nor persists runtime state.

Dependencies/integration: generated from Linux UAPI headers by `ioctls_gen.sh` and consumed by the strace ioctl decoder alongside generic include tables.

Risks/test signals: stale generated rows or wrong command sizes cause misleading ioctl names or argument decoding; test by comparing generated tables with current UAPI headers and tracing representative architecture-specific ioctl calls.

Source-read signal: reviewed complete local file (1 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/csky/ioctls_arch0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/csky/ioctls_inc0.h -->
# sources/test-tools/strace/src/linux/csky/ioctls_inc0.h

Purpose: reuses shared strace architecture logic for `csky` by including `../32/ioctls_inc.h` from `ioctls_inc0.h`.

Important APIs/types/functions: this file exports the APIs provided by the included implementation rather than defining new local functions.

Control flow: the C preprocessor splices the target file into this architecture build, so runtime behavior is the shared implementation's behavior under this architecture's register/personality macros.

State/persistence behavior: no independent state; included code operates on the surrounding architecture register globals and `struct tcb` state.

Dependencies/integration: direct dependency on `../32/ioctls_inc.h` and the macro/register contract expected by that file.

Risks/test signals: changes in the shared implementation can silently affect this architecture; compile the architecture and run syscall/signal/ioctl traces that exercise the included path.

Source-read signal: reviewed complete local file (1 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/csky/ioctls_inc0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/csky/raw_syscall.h -->
# sources/test-tools/strace/src/linux/csky/raw_syscall.h

Purpose: implements a minimal zero-argument raw syscall helper for `csky`.

Important APIs/types/functions: raw_syscall_0, STRACE_RAW_SYSCALL_H, raw_syscall_0; notable register references include none in this file.

Control flow: loads the requested syscall number into the ABI register, executes the architecture trap instruction, records an error flag where the ABI exposes one, and returns the raw result register.

State/persistence behavior: operates on transient tracee/register/memory snapshots or compile-time metadata; persistent program state is not introduced here.

Dependencies/integration: Depends on inline assembly register constraints, trap instructions, clobber lists, and `kernel_ulong_t`.

Risks/test signals: incorrect constraints or clobbers can miscompile; test a harmless syscall such as getpid and an expected failing syscall on native hardware/toolchains.

Source-read signal: reviewed complete local file (32 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/csky/raw_syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/csky/set_error.c -->
# sources/test-tools/strace/src/linux/csky/set_error.c

Purpose: injects a synthetic syscall error or success result into `csky` tracee registers.

Important APIs/types/functions: arch_set_error, arch_set_success; key state includes `struct tcb`, `tcp->scno`, `tcp->u_arg`, `tcp->u_rval`, `tcp->u_error`, and register fields defined by included architecture helpers.

Control flow: `arch_set_error` writes the architecture error convention from `tcp->u_error`; `arch_set_success` writes `tcp->u_rval`; implementations either poke individual user offsets or call `set_regs` after mutating the saved register block.

State/persistence behavior: mutates only the active trace control block and current ptrace register snapshot; any tracee register changes are applied immediately through ptrace helpers.

Dependencies/integration: participates in generic syscall enter/exit decoding; depends on architecture register globals, ptrace helpers, and common tcb fields.

Risks/test signals: Test with syscall fault injection for both success and errno paths, including ESRCH/disappearing-tracee behavior where relevant.

Source-read signal: reviewed complete local file (20 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/csky/set_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/csky/set_scno.c -->
# sources/test-tools/strace/src/linux/csky/set_scno.c

Purpose: updates the tracee syscall number for `csky` syscall tampering/restart support.

Important APIs/types/functions: arch_set_scno; key state includes `struct tcb`, `tcp->scno`, `tcp->u_arg`, `tcp->u_rval`, `tcp->u_error`, and register fields regs[3].

Control flow: writes the requested syscall number into the architecture orig-syscall register using `upoke`, `set_regs`, or an architecture regset such as `NT_ARM_SYSTEM_CALL`.

State/persistence behavior: mutates only the active trace control block and current ptrace register snapshot; any tracee register changes are applied immediately through ptrace helpers.

Dependencies/integration: participates in generic syscall enter/exit decoding; depends on architecture register globals, ptrace helpers, and common tcb fields.

Risks/test signals: Test by rewriting a syscall number under ptrace and confirming the kernel executes/prints the replacement call.

Source-read signal: reviewed complete local file (19 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/csky/set_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/csky/syscallent.h -->
# sources/test-tools/strace/src/linux/csky/syscallent.h

Purpose: defines syscall table metadata for the `csky` personality, covering 2 named entries across 4 source lines; early entries include set_thread_area, cacheflush.

Important APIs/types/functions: table initializers map syscall numbers to argument counts, trace flags, `SEN(...)` decoder handlers, and printable names. Flags observed here include plain zero-flag entries.

Control flow: strace indexes this array after `arch_get_scno` and optional syscall-number shuffling, then dispatches the selected `SEN` decoder and applies table flags to path, fd, network, signal, process, stat, memory, IPC, and pure-call formatting behavior.

State/persistence behavior: compile-time dispatch metadata only; runtime state lives in `struct tcb` fields populated from registers and syscall arguments.

Dependencies/integration: depends on decoder symbols declared elsewhere in strace, architecture syscall numbering, generated common tables, and personality selection.

Risks/test signals: off-by-one numbering, stale ABI entries, or wrong flags produce incorrect syscall names/argument classes; test with known syscall-number traces, generated table checks, and cross-architecture comparison against Linux syscall headers.

Source-read signal: reviewed complete local file (4 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/csky/syscallent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/generic/arch_fpregset.c -->
# sources/test-tools/strace/src/linux/generic/arch_fpregset.c

Purpose: pretty-prints `generic` regset payloads returned by ptrace/core-note style interfaces.

Important APIs/types/functions: arch_decode_fpregset; notable register references include none in this file.

Control flow: rejects empty or misaligned buffers by printing the raw address, safely copies up to the known struct size from the tracee, prints fields that fit inside the supplied size, and marks extra trailing bytes with `more data follows`.

State/persistence behavior: operates on transient tracee/register/memory snapshots or compile-time metadata; persistent program state is not introduced here.

Dependencies/integration: Depends on `umoven_or_printaddr`, `PRINT_FIELD_X`, array printers, struct offset checks, and the companion regset typedef header.

Risks/test signals: field-order or alignment mistakes misdecode `PTRACE_GETREGSET` data; test short, exact-size, oversized, and misaligned regset buffers.

Source-read signal: reviewed complete local file (7 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/generic/arch_fpregset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/generic/arch_fpregset.h -->
# sources/test-tools/strace/src/linux/generic/arch_fpregset.h

Purpose: declares the `generic` regset struct shape and enables the matching decoder.

Important APIs/types/functions: STRACE_ARCH_FPREGSET_H, HAVE_ARCH_FPREGSET; notable register references include none in this file.

Control flow: no executable flow; the typedef and `HAVE_ARCH_*` macro let generic code compile the architecture decoder.

State/persistence behavior: operates on transient tracee/register/memory snapshots or compile-time metadata; persistent program state is not introduced here.

Dependencies/integration: Depends on architecture kernel user register types or locally declared field order; includes no external header in this file.

Risks/test signals: typedef drift from kernel ABI breaks register dumps; compile with current headers and run ptrace regset decoding tests.

Source-read signal: reviewed complete local file (13 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/generic/arch_fpregset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/generic/arch_kvm.c -->
# sources/test-tools/strace/src/linux/generic/arch_kvm.c

Purpose: plugs `generic` into shared KVM ioctl/register decoding.

Important APIs/types/functions: arch_print_kvm_regs, arch_print_kvm_sregs; notable register references include none in this file.

Control flow: provides architecture-specific KVM helpers or includes a shared implementation so generic ioctl decoding can format VM/vCPU state.

State/persistence behavior: operates on transient tracee/register/memory snapshots or compile-time metadata; persistent program state is not introduced here.

Dependencies/integration: Depends on Linux KVM UAPI structs and strace's ioctl decoder.

Risks/test signals: stale KVM struct assumptions break ioctl formatting; test KVM_GET/SET ioctl traces.

Source-read signal: reviewed complete local file (26 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/generic/arch_kvm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/generic/arch_prstatus_regset.c -->
# sources/test-tools/strace/src/linux/generic/arch_prstatus_regset.c

Purpose: pretty-prints `generic` regset payloads returned by ptrace/core-note style interfaces.

Important APIs/types/functions: arch_decode_prstatus_regset; notable register references include none in this file.

Control flow: rejects empty or misaligned buffers by printing the raw address, safely copies up to the known struct size from the tracee, prints fields that fit inside the supplied size, and marks extra trailing bytes with `more data follows`.

State/persistence behavior: operates on transient tracee/register/memory snapshots or compile-time metadata; persistent program state is not introduced here.

Dependencies/integration: Depends on `umoven_or_printaddr`, `PRINT_FIELD_X`, array printers, struct offset checks, and the companion regset typedef header.

Risks/test signals: field-order or alignment mistakes misdecode `PTRACE_GETREGSET` data; test short, exact-size, oversized, and misaligned regset buffers.

Source-read signal: reviewed complete local file (7 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/generic/arch_prstatus_regset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/generic/arch_prstatus_regset.h -->
# sources/test-tools/strace/src/linux/generic/arch_prstatus_regset.h

Purpose: declares the `generic` regset struct shape and enables the matching decoder.

Important APIs/types/functions: STRACE_ARCH_PRSTATUS_REGSET_H, HAVE_ARCH_PRSTATUS_REGSET; notable register references include none in this file.

Control flow: no executable flow; the typedef and `HAVE_ARCH_*` macro let generic code compile the architecture decoder.

State/persistence behavior: operates on transient tracee/register/memory snapshots or compile-time metadata; persistent program state is not introduced here.

Dependencies/integration: Depends on architecture kernel user register types or locally declared field order; includes no external header in this file.

Risks/test signals: typedef drift from kernel ABI breaks register dumps; compile with current headers and run ptrace regset decoding tests.

Source-read signal: reviewed complete local file (13 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/generic/arch_prstatus_regset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/generic/arch_pt_fpregs.c -->
# sources/test-tools/strace/src/linux/generic/arch_pt_fpregs.c

Purpose: declares or decodes `generic` ptrace register structures used by generic Linux support.

Important APIs/types/functions: arch_decode_pt_fpregs; notable register references include none in this file.

Control flow: used during ptrace register fetch/dump paths, often as shared fallback code.

State/persistence behavior: operates on transient tracee/register/memory snapshots or compile-time metadata; persistent program state is not introduced here.

Dependencies/integration: Depends on kernel ptrace register layouts and generic register printers.

Risks/test signals: validate register dumps against kernel headers and known ptrace output.

Source-read signal: reviewed complete local file (11 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/generic/arch_pt_fpregs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/generic/arch_pt_regs.c -->
# sources/test-tools/strace/src/linux/generic/arch_pt_regs.c

Purpose: declares or decodes `generic` ptrace register structures used by generic Linux support.

Important APIs/types/functions: arch_decode_pt_regs; notable register references include none in this file.

Control flow: used during ptrace register fetch/dump paths, often as shared fallback code.

State/persistence behavior: operates on transient tracee/register/memory snapshots or compile-time metadata; persistent program state is not introduced here.

Dependencies/integration: Depends on kernel ptrace register layouts and generic register printers.

Risks/test signals: validate register dumps against kernel headers and known ptrace output.

Source-read signal: reviewed complete local file (11 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/generic/arch_pt_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/generic/arch_pt_regs64.c -->
# sources/test-tools/strace/src/linux/generic/arch_pt_regs64.c

Purpose: declares or decodes `generic` ptrace register structures used by generic Linux support.

Important APIs/types/functions: decode_pt_regs64; notable register references include none in this file.

Control flow: used during ptrace register fetch/dump paths, often as shared fallback code.

State/persistence behavior: operates on transient tracee/register/memory snapshots or compile-time metadata; persistent program state is not introduced here.

Dependencies/integration: Depends on kernel ptrace register layouts and generic register printers.

Risks/test signals: validate register dumps against kernel headers and known ptrace output.

Source-read signal: reviewed complete local file (5 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/generic/arch_pt_regs64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/generic/arch_regs.h -->
# sources/test-tools/strace/src/linux/generic/arch_regs.h

Purpose: defines the register storage and program-counter/stack-pointer access macros for the `generic` Linux strace backend.

Important APIs/types/functions: visible register contract includes macros architecture register storage declarations; functions none; notable register fields include architecture struct fields referenced through macros.

Control flow: generic register-fetch code populates the declared storage via `GETREGS`/`GETREGSET`, then syscall-entry/exit, signal, and stack helpers read the macros exported here.

State/persistence behavior: per-tracee register snapshots are held in static architecture globals for the duration of a decode step and refreshed from ptrace; nothing is persisted beyond the trace event.

Dependencies/integration: integrates with generic `get_regs`, `set_regs`, `get_stack_pointer`, syscall-argument extraction, and signal-frame helpers; includes architecture kernel register structs supplied by surrounding includes.

Risks/test signals: wrong register field mapping corrupts syscall numbers, arguments, PC/SP reporting, and injected return values; validate with ptrace register fetch/set tests and known syscall traces on the architecture.

Source-read signal: reviewed complete local file (1 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/generic/arch_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/generic/arch_rt_sigframe.c -->
# sources/test-tools/strace/src/linux/generic/arch_rt_sigframe.c

Purpose: computes the address of the `generic` realtime signal frame.

Important APIs/types/functions: struct_rt_sigframe layout; struct typedef count 0.

Control flow: obtains the tracee stack pointer and applies the architecture's frame offset adjustment before returning the address to generic signal-frame decoders.

State/persistence behavior: reads transient signal-frame data from tracee memory and prints it; no durable state is stored.

Dependencies/integration: integrates with `get_stack_pointer`, `umove_or_printaddr`, sigset printers, `ucontext_t`/`sigcontext`, and generic signal-return decoding.

Risks/test signals: frame offsets and padding are ABI-sensitive; validate with signal handler traces, blocked-mask restoration, and rt_sigreturn decoding on the architecture.

Source-read signal: reviewed complete local file (14 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/generic/arch_rt_sigframe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/generic/arch_sigreturn.c -->
# sources/test-tools/strace/src/linux/generic/arch_sigreturn.c

Purpose: decodes signal mask restoration for `generic` `sigreturn`/`rt_sigreturn` handling.

Important APIs/types/functions: arch_sigreturn; struct typedef count 0.

Control flow: the helper locates the signal frame from the current stack pointer or architecture context, reads the relevant frame/mask fields with safe `umove` helpers, and prints the restored signal mask.

State/persistence behavior: reads transient signal-frame data from tracee memory and prints it; no durable state is stored.

Dependencies/integration: integrates with `get_stack_pointer`, `umove_or_printaddr`, sigset printers, `ucontext_t`/`sigcontext`, and generic signal-return decoding.

Risks/test signals: frame offsets and padding are ABI-sensitive; validate with signal handler traces, blocked-mask restoration, and rt_sigreturn decoding on the architecture.

Source-read signal: reviewed complete local file (11 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/generic/arch_sigreturn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/generic/asm_stat.h -->
# sources/test-tools/strace/src/linux/generic/asm_stat.h

Purpose: defines generic Linux `struct stat` compatibility layout metadata for decoders.

Important APIs/types/functions: STRACE_ASM_STAT_H, dev_t, gid_t, ino_t, loff_t, mode_t, nlink_t, off64_t; notable register references include none in this file.

Control flow: no direct flow; stat-family syscall decoders include the layout when printing traced buffers.

State/persistence behavior: operates on transient tracee/register/memory snapshots or compile-time metadata; persistent program state is not introduced here.

Dependencies/integration: Depends on Linux asm/stat ABI definitions and strace stat decoders.

Risks/test signals: wrong field sizes or ordering misprint stat buffers; test stat/lstat/fstat variants.

Source-read signal: reviewed complete local file (57 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/generic/asm_stat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/generic/check_scno.c -->
# sources/test-tools/strace/src/linux/generic/check_scno.c

Purpose: performs generic syscall-number range validation before table dispatch.

Important APIs/types/functions: arch_check_scno; notable register references include none in this file.

Control flow: checks `tcp->scno` against the active personality table size and lets the generic decoder handle unknown or out-of-range calls consistently.

State/persistence behavior: operates on transient tracee/register/memory snapshots or compile-time metadata; persistent program state is not introduced here.

Dependencies/integration: Depends on active personality syscall table metadata and `struct tcb`.

Risks/test signals: off-by-one range checks affect unknown syscall rendering; test boundary syscall numbers.

Source-read signal: reviewed complete local file (13 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/generic/check_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/generic/errnoent.h -->
# sources/test-tools/strace/src/linux/generic/errnoent.h

Purpose: maps `generic` errno numbers to symbolic names, with 148 named errno slots such as EPERM, ENOENT, ESRCH, EINTR, EIO, ENXIO, E2BIG, ENOEXEC.

Important APIs/types/functions: string table entries indexed by numeric errno; there are no functions.

Control flow: syscall-exit decoding converts an architecture-specific error number into the indexed name for printing.

State/persistence behavior: static lookup metadata only.

Dependencies/integration: consumed by strace xlat/table-generation code; includes no additional headers.

Risks/test signals: architecture-specific errno numbering differs from generic Linux; validate by comparing against the arch UAPI errno header and tracing syscalls returning nonportable errors.

Source-read signal: reviewed complete local file (155 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/generic/errnoent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/generic/getregs_old.h -->
# sources/test-tools/strace/src/linux/generic/getregs_old.h

Purpose: provides compatibility definitions for older register-fetch paths.

Important APIs/types/functions: getregs_old.h; notable register references include none in this file.

Control flow: no direct runtime flow; included by generic register code when old ptrace register APIs are needed.

State/persistence behavior: operates on transient tracee/register/memory snapshots or compile-time metadata; persistent program state is not introduced here.

Dependencies/integration: Depends on architecture/user register headers and generic register-fetch code.

Risks/test signals: compile old-kernel compatibility configurations and run register fetch tests.

Source-read signal: reviewed complete local file (8 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/generic/getregs_old.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/generic/nr_prefix.c -->
# sources/test-tools/strace/src/linux/generic/nr_prefix.c

Purpose: supplies the syscall-number prefix string for `generic` personality-specific syscall rendering.

Important APIs/types/functions: nr_prefix.c; notable register references include none in this file.

Control flow: generic unknown-syscall formatting calls the prefix helper before printing raw syscall numbers.

State/persistence behavior: operates on transient tracee/register/memory snapshots or compile-time metadata; persistent program state is not introduced here.

Dependencies/integration: Depends on active personality selection and shared prefix helper contracts.

Risks/test signals: test unknown syscall rendering in native and compat personalities.

Source-read signal: reviewed complete local file (18 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/generic/nr_prefix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/generic/ptrace_pokeuser.c -->
# sources/test-tools/strace/src/linux/generic/ptrace_pokeuser.c

Purpose: implements generic user-area register writes through `ptrace(PTRACE_POKEUSER)`.

Important APIs/types/functions: ptrace_pokeuser; notable register references include none in this file.

Control flow: writes a word to a user-area offset for syscall tampering helpers and propagates ptrace errors.

State/persistence behavior: operates on transient tracee/register/memory snapshots or compile-time metadata; persistent program state is not introduced here.

Dependencies/integration: Depends on ptrace, architecture user offsets, and register setter helpers.

Risks/test signals: wrong word size or offset corrupts tracee registers; test injected return values and syscall-number rewrites.

Source-read signal: reviewed complete local file (12 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/generic/ptrace_pokeuser.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/generic/raw_syscall.h -->
# sources/test-tools/strace/src/linux/generic/raw_syscall.h

Purpose: implements a minimal zero-argument raw syscall helper for `generic`.

Important APIs/types/functions: raw_syscall.h; notable register references include none in this file.

Control flow: loads the requested syscall number into the ABI register, executes the architecture trap instruction, records an error flag where the ABI exposes one, and returns the raw result register.

State/persistence behavior: operates on transient tracee/register/memory snapshots or compile-time metadata; persistent program state is not introduced here.

Dependencies/integration: Depends on inline assembly register constraints, trap instructions, clobber lists, and `kernel_ulong_t`.

Risks/test signals: incorrect constraints or clobbers can miscompile; test a harmless syscall such as getpid and an expected failing syscall on native hardware/toolchains.

Source-read signal: reviewed complete local file (1 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/generic/raw_syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/generic/rt_sigframe.h -->
# sources/test-tools/strace/src/linux/generic/rt_sigframe.h

Purpose: defines the `generic` realtime signal-frame layout used by strace.

Important APIs/types/functions: STRACE_RT_SIGFRAME_H; struct typedef count 1.

Control flow: no direct runtime flow in the header; generic frame decoders use the typedef and offset macros when reading tracee memory.

State/persistence behavior: reads transient signal-frame data from tracee memory and prints it; no durable state is stored.

Dependencies/integration: integrates with `get_stack_pointer`, `umove_or_printaddr`, sigset printers, `ucontext_t`/`sigcontext`, and generic signal-return decoding.

Risks/test signals: frame offsets and padding are ABI-sensitive; validate with signal handler traces, blocked-mask restoration, and rt_sigreturn decoding on the architecture.

Source-read signal: reviewed complete local file (21 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/generic/rt_sigframe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/generic/shuffle_scno.c -->
# sources/test-tools/strace/src/linux/generic/shuffle_scno.c

Purpose: translates raw `generic` syscall numbers into the table index space used by strace.

Important APIs/types/functions: shuffle_scno_pers; notable register references include none in this file.

Control flow: generic dispatch calls `shuffle_scno_pers`; implementations may leave native numbers unchanged, delegate to compat helpers, or xor/add a base offset after static assertions.

State/persistence behavior: operates on transient tracee/register/memory snapshots or compile-time metadata; persistent program state is not introduced here.

Dependencies/integration: Depends on syscall table size/base-number constants and personality id.

Risks/test signals: wrong shuffling dispatches to the wrong table; test boundary syscall numbers and personality-specific tables.

Source-read signal: reviewed complete local file (12 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/generic/shuffle_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/generic/signal.h.in -->
# sources/test-tools/strace/src/linux/generic/signal.h.in

Purpose: build-time wrapper template that makes strace include libc `<signal.h>` instead of the kernel `<linux/signal.h>` where those headers conflict.

Important APIs/types/functions: exports no functions; the key contract is the forced `#include <signal.h>` used by generated include paths.

Control flow: there is no runtime flow. During the build, this template becomes an overriding header so later strace source includes see the libc-compatible signal definitions.

State/persistence behavior: build-time include indirection only; no runtime state is read or persisted.

Dependencies/integration: integrates with the generated include directory order and all signal, sigset, and signal-frame decoders that need libc signal types without kernel header conflicts.

Risks/test signals: wrong include precedence can reintroduce `<linux/signal.h>`/libc type clashes; test by regenerating headers and compiling signal decoders on libc/kernel header combinations known to conflict.

Source-read signal: reviewed complete local file (5 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/generic/signal.h.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/generic/signalent.h -->
# sources/test-tools/strace/src/linux/generic/signalent.h

Purpose: maps `generic` signal numbers to printable names, with 33 slots including 0, SIGHUP, SIGINT, SIGQUIT, SIGILL, SIGTRAP, SIGABRT, SIGBUS.

Important APIs/types/functions: signal-name table entries consumed by signal and sigset printers.

Control flow: signal decoders index this table when formatting signal numbers, pending masks, handlers, and signal-return state.

State/persistence behavior: static lookup metadata only.

Dependencies/integration: consumed by strace xlat/table-generation code; includes no additional headers.

Risks/test signals: signal numbering is ABI-specific; validate with signal delivery/kill traces and generated signal table comparison.

Source-read signal: reviewed complete local file (40 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/generic/signalent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/generic/socket.h.in -->
# sources/test-tools/strace/src/linux/generic/socket.h.in

Purpose: build-time wrapper template around `<linux/socket.h>` that supplies `sockaddr_storage` as `__kernel_sockaddr_storage` when the kernel header does not expose the expected name.

Important APIs/types/functions: exports preprocessor compatibility for `sockaddr_storage`; no functions or runtime structs are implemented locally.

Control flow: the generated wrapper uses `#include_next <linux/socket.h>` to keep the real kernel header in the chain, then defines the missing compatibility name when needed.

State/persistence behavior: build-time header compatibility only; no runtime state is introduced.

Dependencies/integration: supports socket/network syscall decoders and headers that expect Linux socket UAPI definitions while also satisfying libc-facing `sys/socket.h` assumptions.

Risks/test signals: include-order mistakes can hide real kernel socket definitions or leave `sockaddr_storage` undefined; test generated-header compilation of socket decoders and sockaddr printers.

Source-read signal: reviewed complete local file (7 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/generic/socket.h.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/generic/subcallent.h -->
# sources/test-tools/strace/src/linux/generic/subcallent.h

Purpose: defines syscall table metadata for the `generic` personality, covering 32 named entries across 54 source lines; early entries include socket, bind, connect, listen, accept, getsockname, getpeername, socketpair.

Important APIs/types/functions: table initializers map syscall numbers to argument counts, trace flags, `SEN(...)` decoder handlers, and printable names. Flags observed here include plain zero-flag entries.

Control flow: strace indexes this array after `arch_get_scno` and optional syscall-number shuffling, then dispatches the selected `SEN` decoder and applies table flags to path, fd, network, signal, process, stat, memory, IPC, and pure-call formatting behavior.

State/persistence behavior: compile-time dispatch metadata only; runtime state lives in `struct tcb` fields populated from registers and syscall arguments.

Dependencies/integration: depends on decoder symbols declared elsewhere in strace, architecture syscall numbering, generated common tables, and personality selection.

Risks/test signals: off-by-one numbering, stale ABI entries, or wrong flags produce incorrect syscall names/argument classes; test with known syscall-number traces, generated table checks, and cross-architecture comparison against Linux syscall headers.

Source-read signal: reviewed complete local file (54 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/generic/subcallent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/generic/syscallent-common.h -->
# sources/test-tools/strace/src/linux/generic/syscallent-common.h

Purpose: provides `generic` helper logic for `syscallent-common.h`.

Important APIs/types/functions: BASE_NR; notable register references include none in this file.

Control flow: called or included by generic strace Linux backend code.

State/persistence behavior: operates on transient tracee/register/memory snapshots or compile-time metadata; persistent program state is not introduced here.

Dependencies/integration: Depends on the surrounding strace architecture contracts.

Risks/test signals: compile and run architecture trace coverage for this helper.

Source-read signal: reviewed complete local file (58 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/generic/syscallent-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/generic/syscallent_base_nr.h -->
# sources/test-tools/strace/src/linux/generic/syscallent_base_nr.h

Purpose: defines the base syscall-number offset used when an architecture table is shifted away from zero.

Important APIs/types/functions: syscallent_base_nr.h; notable register references include none in this file.

Control flow: included by arch definitions and shuffle logic so raw syscall numbers map to compact table indexes.

State/persistence behavior: operates on transient tracee/register/memory snapshots or compile-time metadata; persistent program state is not introduced here.

Dependencies/integration: Depends on syscall table generation and architecture ABI base numbers.

Risks/test signals: validate static assertions and first/last syscall dispatch on the architecture.

Source-read signal: reviewed complete local file (1 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/generic/syscallent_base_nr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/generic/userent.h -->
# sources/test-tools/strace/src/linux/generic/userent.h

Purpose: defines `generic` `ptrace(PEEKUSER)`/`struct user` offset names for strace's user-area decoders, with 0 visible entries.

Important APIs/types/functions: xlat initializer rows or `XLAT_UOFF` macros map offsets to register/user-field names; no executable functions are defined.

Control flow: ptrace/user-offset printing indexes these rows when a trace asks for user-register offsets.

State/persistence behavior: static lookup metadata only.

Dependencies/integration: consumed by strace xlat/table-generation code; includes no additional headers.

Risks/test signals: wrong offsets make `PTRACE_PEEKUSER` output misleading; validate against the architecture `struct user` layout and register-offset trace tests.

Source-read signal: reviewed complete local file (1 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/generic/userent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/generic/userent0.h -->
# sources/test-tools/strace/src/linux/generic/userent0.h

Purpose: defines `generic` `ptrace(PEEKUSER)`/`struct user` offset names for strace's user-area decoders, with 1 visible entries.

Important APIs/types/functions: xlat initializer rows or `XLAT_UOFF` macros map offsets to register/user-field names; no executable functions are defined.

Control flow: ptrace/user-offset printing indexes these rows when a trace asks for user-register offsets.

State/persistence behavior: static lookup metadata only.

Dependencies/integration: consumed by strace xlat/table-generation code; includes no additional headers.

Risks/test signals: wrong offsets make `PTRACE_PEEKUSER` output misleading; validate against the architecture `struct user` layout and register-offset trace tests.

Source-read signal: reviewed complete local file (8 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/generic/userent0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/hppa/arch_defs_.h -->
# sources/test-tools/strace/src/linux/hppa/arch_defs_.h

Purpose: declares strace compile-time personality features for the `hppa` Linux backend, including HAVE_ARCH_SA_RESTORER, ARCH_NEEDS_SET_ERROR_FOR_SCNO_TAMPERING, PERSONALITY0_AUDIT_ARCH.

Important APIs/types/functions: preprocessor macros control feature gates such as old mmap/select, UID16 syscalls, dedicated error registers, supported personalities, and audit arch tuples (AUDIT_ARCH_PARISC, 0 ).

Control flow: no executable code. The main Linux backend includes this header while building architecture-specific syscall decoding and personality setup.

State/persistence behavior: static build-time configuration only; it influences how `struct tcb` register state is interpreted but stores no runtime state itself.

Dependencies/integration: depends on Linux audit architecture constants and may include generated base-number headers (no local includes).

Risks/test signals: incorrect feature macros select wrong syscall tables or legacy decoders; validate with architecture build tests, audit-personality checks, and traces of legacy mmap/select or UID16 syscalls when enabled.

Source-read signal: reviewed complete local file (17 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/hppa/arch_defs_.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/hppa/arch_regs.c -->
# sources/test-tools/strace/src/linux/hppa/arch_regs.c

Purpose: defines the register storage and program-counter/stack-pointer access macros for the `hppa` Linux strace backend.

Important APIs/types/functions: visible register contract includes macros ARCH_REGS_FOR_GETREGSET, ARCH_PC_REG, ARCH_SP_REG; functions none; notable register fields include gr[30].

Control flow: generic register-fetch code populates the declared storage via `GETREGS`/`GETREGSET`, then syscall-entry/exit, signal, and stack helpers read the macros exported here.

State/persistence behavior: per-tracee register snapshots are held in static architecture globals for the duration of a decode step and refreshed from ptrace; nothing is persisted beyond the trace event.

Dependencies/integration: integrates with generic `get_regs`, `set_regs`, `get_stack_pointer`, syscall-argument extraction, and signal-frame helpers; includes architecture kernel register structs supplied by surrounding includes.

Risks/test signals: wrong register field mapping corrupts syscall numbers, arguments, PC/SP reporting, and injected return values; validate with ptrace register fetch/set tests and known syscall traces on the architecture.

Source-read signal: reviewed complete local file (11 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/hppa/arch_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/hppa/arch_rt_sigframe.c -->
# sources/test-tools/strace/src/linux/hppa/arch_rt_sigframe.c

Purpose: computes the address of the `hppa` realtime signal frame.

Important APIs/types/functions: SIGFRAME; struct typedef count 0.

Control flow: obtains the tracee stack pointer and applies the architecture's frame offset adjustment before returning the address to generic signal-frame decoders.

State/persistence behavior: reads transient signal-frame data from tracee memory and prints it; no durable state is stored.

Dependencies/integration: integrates with `get_stack_pointer`, `umove_or_printaddr`, sigset printers, `ucontext_t`/`sigcontext`, and generic signal-return decoding.

Risks/test signals: frame offsets and padding are ABI-sensitive; validate with signal handler traces, blocked-mask restoration, and rt_sigreturn decoding on the architecture.

Source-read signal: reviewed complete local file (45 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/hppa/arch_rt_sigframe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/hppa/errnoent.h -->
# sources/test-tools/strace/src/linux/hppa/errnoent.h

Purpose: maps `hppa` errno numbers to symbolic names, with 152 named errno slots such as EPERM, ENOENT, ESRCH, EINTR, EIO, ENXIO, E2BIG, ENOEXEC.

Important APIs/types/functions: string table entries indexed by numeric errno; there are no functions.

Control flow: syscall-exit decoding converts an architecture-specific error number into the indexed name for printing.

State/persistence behavior: static lookup metadata only.

Dependencies/integration: consumed by strace xlat/table-generation code; includes no additional headers.

Risks/test signals: architecture-specific errno numbering differs from generic Linux; validate by comparing against the arch UAPI errno header and tracing syscalls returning nonportable errors.

Source-read signal: reviewed complete local file (159 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/hppa/errnoent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/hppa/get_error.c -->
# sources/test-tools/strace/src/linux/hppa/get_error.c

Purpose: translates the `hppa` syscall return/error convention into `tcp->u_rval` and `tcp->u_error`.

Important APIs/types/functions: arch_get_error; key state includes `struct tcb`, `tcp->scno`, `tcp->u_arg`, `tcp->u_rval`, `tcp->u_error`, and register fields gr[28].

Control flow: on syscall exit it reads the architecture return/error register convention, optionally checks negated errno ranges or dedicated error flags, sets `u_rval=-1` for errors, and otherwise records the raw return value.

State/persistence behavior: mutates only the active trace control block and current ptrace register snapshot; any tracee register changes are applied immediately through ptrace helpers.

Dependencies/integration: participates in generic syscall enter/exit decoding; depends on negated_errno.h.

Risks/test signals: Test with successful syscalls, negated errno returns, and any architecture-specific dedicated error register path.

Source-read signal: reviewed complete local file (19 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/hppa/get_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/hppa/get_scno.c -->
# sources/test-tools/strace/src/linux/hppa/get_scno.c

Purpose: extracts the current syscall number for the `hppa` backend.

Important APIs/types/functions: arch_get_scno; key state includes `struct tcb`, `tcp->scno`, `tcp->u_arg`, `tcp->u_rval`, `tcp->u_error`, and register fields gr[20].

Control flow: on syscall entry it reads the ABI syscall-number register or user offset, may perform sanity checks for stray exits, then stores the result in `tcp->scno` and returns the generic status code.

State/persistence behavior: mutates only the active trace control block and current ptrace register snapshot; any tracee register changes are applied immediately through ptrace helpers.

Dependencies/integration: participates in generic syscall enter/exit decoding; depends on architecture register globals, ptrace helpers, and common tcb fields.

Risks/test signals: Test with representative syscall entries, invalid/out-of-range numbers, and personality-specific numbering when present.

Source-read signal: reviewed complete local file (14 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/hppa/get_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/hppa/get_syscall_args.c -->
# sources/test-tools/strace/src/linux/hppa/get_syscall_args.c

Purpose: copies syscall arguments from `hppa` register state or backing register-stack memory into `tcp->u_arg`.

Important APIs/types/functions: arch_get_syscall_args; key state includes `struct tcb`, `tcp->scno`, `tcp->u_arg`, `tcp->u_rval`, `tcp->u_error`, and register fields gr[26 - i].

Control flow: after the syscall number is known, it reads up to `n_args(tcp)` or `MAX_ARGS` arguments from ABI-defined registers, compatibility helper code, or memory addresses derived from register-stack state, returning `1` on success or `-1` on fatal fetch failure.

State/persistence behavior: mutates only the active trace control block and current ptrace register snapshot; any tracee register changes are applied immediately through ptrace helpers.

Dependencies/integration: participates in generic syscall enter/exit decoding; depends on architecture register globals, ptrace helpers, and common tcb fields.

Risks/test signals: Test with six-argument syscalls, compatibility personalities, and ptrace permission/fault cases for memory-backed argument locations.

Source-read signal: reviewed complete local file (15 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/hppa/get_syscall_args.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/hppa/ioctls_arch0.h -->
# sources/test-tools/strace/src/linux/hppa/ioctls_arch0.h

Purpose: provides the `hppa` generated architecture ioctl table, with 93 initializer rows from asm/grfioctl.h, asm/ioctls.h, asm/perf.h; examples include GCAOFF, GCAON, GCDESCRIBE, GCFASTLOCK, GCID, GCLOCK.

Important APIs/types/functions: each row is `{'header, name, direction, number, size'}` data consumed by the common ioctl xlat machinery; observed direction flags include _IOC_NONE, _IOC_READ, _IOC_WRITE.

Control flow: no executable flow; entries are compiled into lookup arrays that let `ioctl(2)` decoding map command numbers back to symbolic names and argument direction/size.

State/persistence behavior: immutable compile-time metadata only; it neither reads traced memory nor persists runtime state.

Dependencies/integration: generated from Linux UAPI headers by `ioctls_gen.sh` and consumed by the strace ioctl decoder alongside generic include tables.

Risks/test signals: stale generated rows or wrong command sizes cause misleading ioctl names or argument decoding; test by comparing generated tables with current UAPI headers and tracing representative architecture-specific ioctl calls.

Source-read signal: reviewed complete local file (94 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/hppa/ioctls_arch0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/hppa/ioctls_inc0.h -->
# sources/test-tools/strace/src/linux/hppa/ioctls_inc0.h

Purpose: reuses shared strace architecture logic for `hppa` by including `../32/ioctls_inc.h` from `ioctls_inc0.h`.

Important APIs/types/functions: this file exports the APIs provided by the included implementation rather than defining new local functions.

Control flow: the C preprocessor splices the target file into this architecture build, so runtime behavior is the shared implementation's behavior under this architecture's register/personality macros.

State/persistence behavior: no independent state; included code operates on the surrounding architecture register globals and `struct tcb` state.

Dependencies/integration: direct dependency on `../32/ioctls_inc.h` and the macro/register contract expected by that file.

Risks/test signals: changes in the shared implementation can silently affect this architecture; compile the architecture and run syscall/signal/ioctl traces that exercise the included path.

Source-read signal: reviewed complete local file (1 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/hppa/ioctls_inc0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/hppa/raw_syscall.h -->
# sources/test-tools/strace/src/linux/hppa/raw_syscall.h

Purpose: implements a minimal zero-argument raw syscall helper for `hppa`.

Important APIs/types/functions: raw_syscall_0, STRACE_RAW_SYSCALL_H, raw_syscall_0; notable register references include r28.

Control flow: loads the requested syscall number into the ABI register, executes the architecture trap instruction, records an error flag where the ABI exposes one, and returns the raw result register.

State/persistence behavior: operates on transient tracee/register/memory snapshots or compile-time metadata; persistent program state is not introduced here.

Dependencies/integration: Depends on inline assembly register constraints, trap instructions, clobber lists, and `kernel_ulong_t`.

Risks/test signals: incorrect constraints or clobbers can miscompile; test a harmless syscall such as getpid and an expected failing syscall on native hardware/toolchains.

Source-read signal: reviewed complete local file (32 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/hppa/raw_syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/hppa/rt_sigframe.h -->
# sources/test-tools/strace/src/linux/hppa/rt_sigframe.h

Purpose: defines the `hppa` realtime signal-frame layout used by strace.

Important APIs/types/functions: STRACE_RT_SIGFRAME_H; struct typedef count 2.

Control flow: no direct runtime flow in the header; generic frame decoders use the typedef and offset macros when reading tracee memory.

State/persistence behavior: reads transient signal-frame data from tracee memory and prints it; no durable state is stored.

Dependencies/integration: integrates with `get_stack_pointer`, `umove_or_printaddr`, sigset printers, `ucontext_t`/`sigcontext`, and generic signal-return decoding.

Risks/test signals: frame offsets and padding are ABI-sensitive; validate with signal handler traces, blocked-mask restoration, and rt_sigreturn decoding on the architecture.

Source-read signal: reviewed complete local file (26 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/hppa/rt_sigframe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/hppa/set_error.c -->
# sources/test-tools/strace/src/linux/hppa/set_error.c

Purpose: injects a synthetic syscall error or success result into `hppa` tracee registers.

Important APIs/types/functions: arch_set_error, arch_set_success; key state includes `struct tcb`, `tcp->scno`, `tcp->u_arg`, `tcp->u_rval`, `tcp->u_error`, and register fields gr[28].

Control flow: `arch_set_error` writes the architecture error convention from `tcp->u_error`; `arch_set_success` writes `tcp->u_rval`; implementations either poke individual user offsets or call `set_regs` after mutating the saved register block.

State/persistence behavior: mutates only the active trace control block and current ptrace register snapshot; any tracee register changes are applied immediately through ptrace helpers.

Dependencies/integration: participates in generic syscall enter/exit decoding; depends on architecture register globals, ptrace helpers, and common tcb fields.

Risks/test signals: Test with syscall fault injection for both success and errno paths, including ESRCH/disappearing-tracee behavior where relevant.

Source-read signal: reviewed complete local file (20 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/hppa/set_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/hppa/set_scno.c -->
# sources/test-tools/strace/src/linux/hppa/set_scno.c

Purpose: updates the tracee syscall number for `hppa` syscall tampering/restart support.

Important APIs/types/functions: arch_set_scno; key state includes `struct tcb`, `tcp->scno`, `tcp->u_arg`, `tcp->u_rval`, `tcp->u_error`, and register fields gr[20].

Control flow: writes the requested syscall number into the architecture orig-syscall register using `upoke`, `set_regs`, or an architecture regset such as `NT_ARM_SYSTEM_CALL`.

State/persistence behavior: mutates only the active trace control block and current ptrace register snapshot; any tracee register changes are applied immediately through ptrace helpers.

Dependencies/integration: participates in generic syscall enter/exit decoding; depends on architecture register globals, ptrace helpers, and common tcb fields.

Risks/test signals: Test by rewriting a syscall number under ptrace and confirming the kernel executes/prints the replacement call.

Source-read signal: reviewed complete local file (15 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/hppa/set_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/hppa/signalent.h -->
# sources/test-tools/strace/src/linux/hppa/signalent.h

Purpose: maps `hppa` signal numbers to printable names, with 33 slots including 0, SIGHUP, SIGINT, SIGQUIT, SIGILL, SIGTRAP, SIGABRT, SIGSTKFLT.

Important APIs/types/functions: signal-name table entries consumed by signal and sigset printers.

Control flow: signal decoders index this table when formatting signal numbers, pending masks, handlers, and signal-return state.

State/persistence behavior: static lookup metadata only.

Dependencies/integration: consumed by strace xlat/table-generation code; includes no additional headers.

Risks/test signals: signal numbering is ABI-specific; validate with signal delivery/kill traces and generated signal table comparison.

Source-read signal: reviewed complete local file (40 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/hppa/signalent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/hppa/syscallent.h -->
# sources/test-tools/strace/src/linux/hppa/syscallent.h

Purpose: defines syscall table metadata for the `hppa` personality, covering 355 named entries across 364 source lines; early entries include restart_syscall, exit, fork, read, write, open, close, waitpid.

Important APIs/types/functions: table initializers map syscall numbers to argument counts, trace flags, `SEN(...)` decoder handlers, and printable names. Flags observed here include CC, NF, PU, SI, TC, TCL, TD, TF, TFSF, TFST, TI, TLST.

Control flow: strace indexes this array after `arch_get_scno` and optional syscall-number shuffling, then dispatches the selected `SEN` decoder and applies table flags to path, fd, network, signal, process, stat, memory, IPC, and pure-call formatting behavior.

State/persistence behavior: compile-time dispatch metadata only; runtime state lives in `struct tcb` fields populated from registers and syscall arguments.

Dependencies/integration: depends on decoder symbols declared elsewhere in strace, architecture syscall numbering, generated common tables, and personality selection.

Risks/test signals: off-by-one numbering, stale ABI entries, or wrong flags produce incorrect syscall names/argument classes; test with known syscall-number traces, generated table checks, and cross-architecture comparison against Linux syscall headers.

Source-read signal: reviewed complete local file (364 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/hppa/syscallent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/hppa/userent.h -->
# sources/test-tools/strace/src/linux/hppa/userent.h

Purpose: defines `hppa` `ptrace(PEEKUSER)`/`struct user` offset names for strace's user-area decoders, with 1 visible entries.

Important APIs/types/functions: xlat initializer rows or `XLAT_UOFF` macros map offsets to register/user-field names; no executable functions are defined.

Control flow: ptrace/user-offset printing indexes these rows when a trace asks for user-register offsets.

State/persistence behavior: static lookup metadata only.

Dependencies/integration: consumed by strace xlat/table-generation code; includes no additional headers.

Risks/test signals: wrong offsets make `PTRACE_PEEKUSER` output misleading; validate against the architecture `struct user` layout and register-offset trace tests.

Source-read signal: reviewed complete local file (69 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/hppa/userent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/i386/arch_defs_.h -->
# sources/test-tools/strace/src/linux/i386/arch_defs_.h

Purpose: declares strace compile-time personality features for the `i386` Linux backend, including HAVE_ARCH_OLD_MMAP, HAVE_ARCH_OLD_SELECT, HAVE_ARCH_UID16_SYSCALLS, CAN_ARCH_BE_COMPAT_ON_64BIT_KERNEL, PERSONALITY0_AUDIT_ARCH.

Important APIs/types/functions: preprocessor macros control feature gates such as old mmap/select, UID16 syscalls, dedicated error registers, supported personalities, and audit arch tuples (AUDIT_ARCH_I386, 0 ).

Control flow: no executable code. The main Linux backend includes this header while building architecture-specific syscall decoding and personality setup.

State/persistence behavior: static build-time configuration only; it influences how `struct tcb` register state is interpreted but stores no runtime state itself.

Dependencies/integration: depends on Linux audit architecture constants and may include generated base-number headers (no local includes).

Risks/test signals: incorrect feature macros select wrong syscall tables or legacy decoders; validate with architecture build tests, audit-personality checks, and traces of legacy mmap/select or UID16 syscalls when enabled.

Source-read signal: reviewed complete local file (12 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/i386/arch_defs_.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/i386/arch_fpregset.c -->
# sources/test-tools/strace/src/linux/i386/arch_fpregset.c

Purpose: pretty-prints `i386` regset payloads returned by ptrace/core-note style interfaces.

Important APIs/types/functions: arch_decode_fpregset; notable register references include none in this file.

Control flow: rejects empty or misaligned buffers by printing the raw address, safely copies up to the known struct size from the tracee, prints fields that fit inside the supplied size, and marks extra trailing bytes with `more data follows`.

State/persistence behavior: operates on transient tracee/register/memory snapshots or compile-time metadata; persistent program state is not introduced here.

Dependencies/integration: Depends on `umoven_or_printaddr`, `PRINT_FIELD_X`, array printers, struct offset checks, and the companion regset typedef header.

Risks/test signals: field-order or alignment mistakes misdecode `PTRACE_GETREGSET` data; test short, exact-size, oversized, and misaligned regset buffers.

Source-read signal: reviewed complete local file (58 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/i386/arch_fpregset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/i386/arch_fpregset.h -->
# sources/test-tools/strace/src/linux/i386/arch_fpregset.h

Purpose: declares the `i386` regset struct shape and enables the matching decoder.

Important APIs/types/functions: STRACE_ARCH_FPREGSET_H, HAVE_ARCH_FPREGSET; notable register references include none in this file.

Control flow: no executable flow; the typedef and `HAVE_ARCH_*` macro let generic code compile the architecture decoder.

State/persistence behavior: operates on transient tracee/register/memory snapshots or compile-time metadata; persistent program state is not introduced here.

Dependencies/integration: Depends on architecture kernel user register types or locally declared field order; includes no external header in this file.

Risks/test signals: typedef drift from kernel ABI breaks register dumps; compile with current headers and run ptrace regset decoding tests.

Source-read signal: reviewed complete local file (24 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/i386/arch_fpregset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/i386/arch_kvm.c -->
# sources/test-tools/strace/src/linux/i386/arch_kvm.c

Purpose: reuses shared strace architecture logic for `i386` by including `../x86_64/arch_kvm.c` from `arch_kvm.c`.

Important APIs/types/functions: this file exports the APIs provided by the included implementation rather than defining new local functions.

Control flow: the C preprocessor splices the target file into this architecture build, so runtime behavior is the shared implementation's behavior under this architecture's register/personality macros.

State/persistence behavior: no independent state; included code operates on the surrounding architecture register globals and `struct tcb` state.

Dependencies/integration: direct dependency on `../x86_64/arch_kvm.c` and the macro/register contract expected by that file.

Risks/test signals: changes in the shared implementation can silently affect this architecture; compile the architecture and run syscall/signal/ioctl traces that exercise the included path.

Source-read signal: reviewed complete local file (1 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/i386/arch_kvm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/i386/arch_prstatus_regset.c -->
# sources/test-tools/strace/src/linux/i386/arch_prstatus_regset.c

Purpose: pretty-prints `i386` regset payloads returned by ptrace/core-note style interfaces.

Important APIs/types/functions: arch_decode_prstatus_regset; notable register references include ebx, ecx, edx, esi, edi, ebp, eax, orig_eax, eip, esp.

Control flow: rejects empty or misaligned buffers by printing the raw address, safely copies up to the known struct size from the tracee, prints fields that fit inside the supplied size, and marks extra trailing bytes with `more data follows`.

State/persistence behavior: operates on transient tracee/register/memory snapshots or compile-time metadata; persistent program state is not introduced here.

Dependencies/integration: Depends on `umoven_or_printaddr`, `PRINT_FIELD_X`, array printers, struct offset checks, and the companion regset typedef header.

Risks/test signals: field-order or alignment mistakes misdecode `PTRACE_GETREGSET` data; test short, exact-size, oversized, and misaligned regset buffers.

Source-read signal: reviewed complete local file (91 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/i386/arch_prstatus_regset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/i386/arch_prstatus_regset.h -->
# sources/test-tools/strace/src/linux/i386/arch_prstatus_regset.h

Purpose: declares the `i386` regset struct shape and enables the matching decoder.

Important APIs/types/functions: STRACE_ARCH_PRSTATUS_REGSET_H, HAVE_ARCH_PRSTATUS_REGSET; notable register references include ebx, ecx, edx, esi, edi, ebp, eax, orig_eax, eip, esp.

Control flow: no executable flow; the typedef and `HAVE_ARCH_*` macro let generic code compile the architecture decoder.

State/persistence behavior: operates on transient tracee/register/memory snapshots or compile-time metadata; persistent program state is not introduced here.

Dependencies/integration: Depends on architecture kernel user register types or locally declared field order; includes no external header in this file.

Risks/test signals: typedef drift from kernel ABI breaks register dumps; compile with current headers and run ptrace regset decoding tests.

Source-read signal: reviewed complete local file (33 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/i386/arch_prstatus_regset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/i386/arch_regs.c -->
# sources/test-tools/strace/src/linux/i386/arch_regs.c

Purpose: defines the register storage and program-counter/stack-pointer access macros for the `i386` Linux strace backend.

Important APIs/types/functions: visible register contract includes macros ARCH_REGS_FOR_GETREGS, ARCH_PC_REG, ARCH_SP_REG, ARCH_MIGHT_USE_SET_REGS; functions none; notable register fields include eip, esp.

Control flow: generic register-fetch code populates the declared storage via `GETREGS`/`GETREGSET`, then syscall-entry/exit, signal, and stack helpers read the macros exported here.

State/persistence behavior: per-tracee register snapshots are held in static architecture globals for the duration of a decode step and refreshed from ptrace; nothing is persisted beyond the trace event.

Dependencies/integration: integrates with generic `get_regs`, `set_regs`, `get_stack_pointer`, syscall-argument extraction, and signal-frame helpers; includes architecture kernel register structs supplied by surrounding includes.

Risks/test signals: wrong register field mapping corrupts syscall numbers, arguments, PC/SP reporting, and injected return values; validate with ptrace register fetch/set tests and known syscall traces on the architecture.

Source-read signal: reviewed complete local file (15 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/i386/arch_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/i386/arch_rt_sigframe.c -->
# sources/test-tools/strace/src/linux/i386/arch_rt_sigframe.c

Purpose: computes the address of the `i386` realtime signal frame.

Important APIs/types/functions: struct_rt_sigframe layout; struct typedef count 0.

Control flow: obtains the tracee stack pointer and applies the architecture's frame offset adjustment before returning the address to generic signal-frame decoders.

State/persistence behavior: reads transient signal-frame data from tracee memory and prints it; no durable state is stored.

Dependencies/integration: integrates with `get_stack_pointer`, `umove_or_printaddr`, sigset printers, `ucontext_t`/`sigcontext`, and generic signal-return decoding.

Risks/test signals: frame offsets and padding are ABI-sensitive; validate with signal handler traces, blocked-mask restoration, and rt_sigreturn decoding on the architecture.

Source-read signal: reviewed complete local file (12 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/i386/arch_rt_sigframe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/i386/arch_sigreturn.c -->
# sources/test-tools/strace/src/linux/i386/arch_sigreturn.c

Purpose: decodes signal mask restoration for `i386` `sigreturn`/`rt_sigreturn` handling.

Important APIs/types/functions: arch_sigreturn; struct typedef count 0.

Control flow: the helper locates the signal frame from the current stack pointer or architecture context, reads the relevant frame/mask fields with safe `umove` helpers, and prints the restored signal mask.

State/persistence behavior: reads transient signal-frame data from tracee memory and prints it; no durable state is stored.

Dependencies/integration: integrates with `get_stack_pointer`, `umove_or_printaddr`, sigset printers, `ucontext_t`/`sigcontext`, and generic signal-return decoding.

Risks/test signals: frame offsets and padding are ABI-sensitive; validate with signal handler traces, blocked-mask restoration, and rt_sigreturn decoding on the architecture.

Source-read signal: reviewed complete local file (30 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/i386/arch_sigreturn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/i386/get_error.c -->
# sources/test-tools/strace/src/linux/i386/get_error.c

Purpose: translates the `i386` syscall return/error convention into `tcp->u_rval` and `tcp->u_error`.

Important APIs/types/functions: arch_get_error; key state includes `struct tcb`, `tcp->scno`, `tcp->u_arg`, `tcp->u_rval`, `tcp->u_error`, and register fields eax.

Control flow: on syscall exit it reads the architecture return/error register convention, optionally checks negated errno ranges or dedicated error flags, sets `u_rval=-1` for errors, and otherwise records the raw return value.

State/persistence behavior: mutates only the active trace control block and current ptrace register snapshot; any tracee register changes are applied immediately through ptrace helpers.

Dependencies/integration: participates in generic syscall enter/exit decoding; depends on negated_errno.h.

Risks/test signals: Test with successful syscalls, negated errno returns, and any architecture-specific dedicated error register path.

Source-read signal: reviewed complete local file (19 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/i386/get_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/i386/get_scno.c -->
# sources/test-tools/strace/src/linux/i386/get_scno.c

Purpose: extracts the current syscall number for the `i386` backend.

Important APIs/types/functions: arch_get_scno; key state includes `struct tcb`, `tcp->scno`, `tcp->u_arg`, `tcp->u_rval`, `tcp->u_error`, and register fields orig_eax.

Control flow: on syscall entry it reads the ABI syscall-number register or user offset, may perform sanity checks for stray exits, then stores the result in `tcp->scno` and returns the generic status code.

State/persistence behavior: mutates only the active trace control block and current ptrace register snapshot; any tracee register changes are applied immediately through ptrace helpers.

Dependencies/integration: participates in generic syscall enter/exit decoding; depends on architecture register globals, ptrace helpers, and common tcb fields.

Risks/test signals: Test with representative syscall entries, invalid/out-of-range numbers, and personality-specific numbering when present.

Source-read signal: reviewed complete local file (14 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/i386/get_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/i386/get_syscall_args.c -->
# sources/test-tools/strace/src/linux/i386/get_syscall_args.c

Purpose: copies syscall arguments from `i386` register state or backing register-stack memory into `tcp->u_arg`.

Important APIs/types/functions: arch_get_syscall_args; key state includes `struct tcb`, `tcp->scno`, `tcp->u_arg`, `tcp->u_rval`, `tcp->u_error`, and register fields ebx, ecx, edx, esi, edi, ebp.

Control flow: after the syscall number is known, it reads up to `n_args(tcp)` or `MAX_ARGS` arguments from ABI-defined registers, compatibility helper code, or memory addresses derived from register-stack state, returning `1` on success or `-1` on fatal fetch failure.

State/persistence behavior: mutates only the active trace control block and current ptrace register snapshot; any tracee register changes are applied immediately through ptrace helpers.

Dependencies/integration: participates in generic syscall enter/exit decoding; depends on architecture register globals, ptrace helpers, and common tcb fields.

Risks/test signals: Test with six-argument syscalls, compatibility personalities, and ptrace permission/fault cases for memory-backed argument locations.

Source-read signal: reviewed complete local file (19 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/i386/get_syscall_args.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/i386/ioctls_arch0.h -->
# sources/test-tools/strace/src/linux/i386/ioctls_arch0.h

Purpose: provides the `i386` generated architecture ioctl table, with 132 initializer rows from asm/amd_hsmp.h, asm/mce.h, asm/msr.h, asm/mtrr.h; examples include HSMP_IOCTL_CMD, MCE_GETCLEAR_FLAGS, MCE_GET_LOG_LEN, MCE_GET_RECORD_LEN, X86_IOC_RDMSR_REGS, X86_IOC_WRMSR_REGS.

Important APIs/types/functions: each row is `{'header, name, direction, number, size'}` data consumed by the common ioctl xlat machinery; observed direction flags include _IOC_NONE, _IOC_READ, _IOC_WRITE.

Control flow: no executable flow; entries are compiled into lookup arrays that let `ioctl(2)` decoding map command numbers back to symbolic names and argument direction/size.

State/persistence behavior: immutable compile-time metadata only; it neither reads traced memory nor persists runtime state.

Dependencies/integration: generated from Linux UAPI headers by `ioctls_gen.sh` and consumed by the strace ioctl decoder alongside generic include tables.

Risks/test signals: stale generated rows or wrong command sizes cause misleading ioctl names or argument decoding; test by comparing generated tables with current UAPI headers and tracing representative architecture-specific ioctl calls.

Source-read signal: reviewed complete local file (133 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/i386/ioctls_arch0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/i386/ioctls_inc0.h -->
# sources/test-tools/strace/src/linux/i386/ioctls_inc0.h

Purpose: reuses shared strace architecture logic for `i386` by including `../32/ioctls_inc.h` from `ioctls_inc0.h`.

Important APIs/types/functions: this file exports the APIs provided by the included implementation rather than defining new local functions.

Control flow: the C preprocessor splices the target file into this architecture build, so runtime behavior is the shared implementation's behavior under this architecture's register/personality macros.

State/persistence behavior: no independent state; included code operates on the surrounding architecture register globals and `struct tcb` state.

Dependencies/integration: direct dependency on `../32/ioctls_inc.h` and the macro/register contract expected by that file.

Risks/test signals: changes in the shared implementation can silently affect this architecture; compile the architecture and run syscall/signal/ioctl traces that exercise the included path.

Source-read signal: reviewed complete local file (1 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/i386/ioctls_inc0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/i386/raw_syscall.h -->
# sources/test-tools/strace/src/linux/i386/raw_syscall.h

Purpose: implements a minimal zero-argument raw syscall helper for `i386`.

Important APIs/types/functions: raw_syscall_0, STRACE_RAW_SYSCALL_H, raw_syscall_0; notable register references include none in this file.

Control flow: loads the requested syscall number into the ABI register, executes the architecture trap instruction, records an error flag where the ABI exposes one, and returns the raw result register.

State/persistence behavior: operates on transient tracee/register/memory snapshots or compile-time metadata; persistent program state is not introduced here.

Dependencies/integration: Depends on inline assembly register constraints, trap instructions, clobber lists, and `kernel_ulong_t`.

Risks/test signals: incorrect constraints or clobbers can miscompile; test a harmless syscall such as getpid and an expected failing syscall on native hardware/toolchains.

Source-read signal: reviewed complete local file (28 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/i386/raw_syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/i386/rt_sigframe.h -->
# sources/test-tools/strace/src/linux/i386/rt_sigframe.h

Purpose: defines the `i386` realtime signal-frame layout used by strace.

Important APIs/types/functions: STRACE_RT_SIGFRAME_H; struct typedef count 1.

Control flow: no direct runtime flow in the header; generic frame decoders use the typedef and offset macros when reading tracee memory.

State/persistence behavior: reads transient signal-frame data from tracee memory and prints it; no durable state is stored.

Dependencies/integration: integrates with `get_stack_pointer`, `umove_or_printaddr`, sigset printers, `ucontext_t`/`sigcontext`, and generic signal-return decoding.

Risks/test signals: frame offsets and padding are ABI-sensitive; validate with signal handler traces, blocked-mask restoration, and rt_sigreturn decoding on the architecture.

Source-read signal: reviewed complete local file (23 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/i386/rt_sigframe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/i386/set_error.c -->
# sources/test-tools/strace/src/linux/i386/set_error.c

Purpose: injects a synthetic syscall error or success result into `i386` tracee registers.

Important APIs/types/functions: arch_set_error, arch_set_success; key state includes `struct tcb`, `tcp->scno`, `tcp->u_arg`, `tcp->u_rval`, `tcp->u_error`, and register fields eax.

Control flow: `arch_set_error` writes the architecture error convention from `tcp->u_error`; `arch_set_success` writes `tcp->u_rval`; implementations either poke individual user offsets or call `set_regs` after mutating the saved register block.

State/persistence behavior: mutates only the active trace control block and current ptrace register snapshot; any tracee register changes are applied immediately through ptrace helpers.

Dependencies/integration: participates in generic syscall enter/exit decoding; depends on architecture register globals, ptrace helpers, and common tcb fields.

Risks/test signals: Test with syscall fault injection for both success and errno paths, including ESRCH/disappearing-tracee behavior where relevant.

Source-read signal: reviewed complete local file (20 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/i386/set_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/i386/set_scno.c -->
# sources/test-tools/strace/src/linux/i386/set_scno.c

Purpose: updates the tracee syscall number for `i386` syscall tampering/restart support.

Important APIs/types/functions: arch_set_scno; key state includes `struct tcb`, `tcp->scno`, `tcp->u_arg`, `tcp->u_rval`, `tcp->u_error`, and register fields defined by included architecture helpers.

Control flow: writes the requested syscall number into the architecture orig-syscall register using `upoke`, `set_regs`, or an architecture regset such as `NT_ARM_SYSTEM_CALL`.

State/persistence behavior: mutates only the active trace control block and current ptrace register snapshot; any tracee register changes are applied immediately through ptrace helpers.

Dependencies/integration: participates in generic syscall enter/exit decoding; depends on architecture register globals, ptrace helpers, and common tcb fields.

Risks/test signals: Test by rewriting a syscall number under ptrace and confirming the kernel executes/prints the replacement call.

Source-read signal: reviewed complete local file (12 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/i386/set_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/i386/syscallent.h -->
# sources/test-tools/strace/src/linux/i386/syscallent.h

Purpose: defines syscall table metadata for the `i386` personality, covering 393 named entries across 411 source lines; early entries include restart_syscall, exit, fork, read, write, open, close, waitpid.

Important APIs/types/functions: table initializers map syscall numbers to argument counts, trace flags, `SEN(...)` decoder handlers, and printable names. Flags observed here include CC, NF, PU, SI, TC, TCL, TD, TF, TFSF, TFST, TI, TLST.

Control flow: strace indexes this array after `arch_get_scno` and optional syscall-number shuffling, then dispatches the selected `SEN` decoder and applies table flags to path, fd, network, signal, process, stat, memory, IPC, and pure-call formatting behavior.

State/persistence behavior: compile-time dispatch metadata only; runtime state lives in `struct tcb` fields populated from registers and syscall arguments.

Dependencies/integration: depends on decoder symbols declared elsewhere in strace, architecture syscall numbering, generated common tables, and personality selection.

Risks/test signals: off-by-one numbering, stale ABI entries, or wrong flags produce incorrect syscall names/argument classes; test with known syscall-number traces, generated table checks, and cross-architecture comparison against Linux syscall headers.

Source-read signal: reviewed complete local file (411 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/i386/syscallent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/i386/userent.h -->
# sources/test-tools/strace/src/linux/i386/userent.h

Purpose: defines `i386` `ptrace(PEEKUSER)`/`struct user` offset names for strace's user-area decoders, with 17 visible entries.

Important APIs/types/functions: xlat initializer rows or `XLAT_UOFF` macros map offsets to register/user-field names; no executable functions are defined.

Control flow: ptrace/user-offset printing indexes these rows when a trace asks for user-register offsets.

State/persistence behavior: static lookup metadata only.

Dependencies/integration: consumed by strace xlat/table-generation code; includes userent0.h.

Risks/test signals: wrong offsets make `PTRACE_PEEKUSER` output misleading; validate against the architecture `struct user` layout and register-offset trace tests.

Source-read signal: reviewed complete local file (26 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/i386/userent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/i386/userent0.h -->
# sources/test-tools/strace/src/linux/i386/userent0.h

Purpose: defines `i386` `ptrace(PEEKUSER)`/`struct user` offset names for strace's user-area decoders, with 14 visible entries.

Important APIs/types/functions: xlat initializer rows or `XLAT_UOFF` macros map offsets to register/user-field names; no executable functions are defined.

Control flow: ptrace/user-offset printing indexes these rows when a trace asks for user-register offsets.

State/persistence behavior: static lookup metadata only.

Dependencies/integration: consumed by strace xlat/table-generation code; includes ../generic/userent0.h.

Risks/test signals: wrong offsets make `PTRACE_PEEKUSER` output misleading; validate against the architecture `struct user` layout and register-offset trace tests.

Source-read signal: reviewed complete local file (22 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/i386/userent0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/ia64/arch_defs_.h -->
# sources/test-tools/strace/src/linux/ia64/arch_defs_.h

Purpose: declares strace compile-time personality features for the `ia64` Linux backend, including HAVE_ARCH_GETRVAL2, HAVE_ARCH_UID16_SYSCALLS, HAVE_ARCH_SA_RESTORER, HAVE_ARCH_DEDICATED_ERR_REG, PERSONALITY0_AUDIT_ARCH.

Important APIs/types/functions: preprocessor macros control feature gates such as old mmap/select, UID16 syscalls, dedicated error registers, supported personalities, and audit arch tuples (AUDIT_ARCH_IA64, SYSCALLENT_BASE_NR ).

Control flow: no executable code. The main Linux backend includes this header while building architecture-specific syscall decoding and personality setup.

State/persistence behavior: static build-time configuration only; it influences how `struct tcb` register state is interpreted but stores no runtime state itself.

Dependencies/integration: depends on Linux audit architecture constants and may include generated base-number headers (syscallent_base_nr.h).

Risks/test signals: incorrect feature macros select wrong syscall tables or legacy decoders; validate with architecture build tests, audit-personality checks, and traces of legacy mmap/select or UID16 syscalls when enabled.

Source-read signal: reviewed complete local file (14 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/ia64/arch_defs_.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/ia64/arch_getrval2.c -->
# sources/test-tools/strace/src/linux/ia64/arch_getrval2.c

Purpose: returns the architecture-specific second syscall return value for `ia64`.

Important APIs/types/functions: getrval2; notable register references include gr[9].

Control flow: fetches registers if needed, then returns the ABI register used for the secondary result.

State/persistence behavior: operates on transient tracee/register/memory snapshots or compile-time metadata; persistent program state is not introduced here.

Dependencies/integration: Depends on ptrace register fetch helpers and architecture return-register layout.

Risks/test signals: validate syscalls with paired return values, plus ptrace fetch failure paths.

Source-read signal: reviewed complete local file (14 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/ia64/arch_getrval2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/ia64/arch_regs.c -->
# sources/test-tools/strace/src/linux/ia64/arch_regs.c

Purpose: defines the register storage and program-counter/stack-pointer access macros for the `ia64` Linux strace backend.

Important APIs/types/functions: visible register contract includes macros ARCH_REGS_FOR_GETREGS, ARCH_PC_REG, ARCH_SP_REG; functions none; notable register fields include br[0], gr[12].

Control flow: generic register-fetch code populates the declared storage via `GETREGS`/`GETREGSET`, then syscall-entry/exit, signal, and stack helpers read the macros exported here.

State/persistence behavior: per-tracee register snapshots are held in static architecture globals for the duration of a decode step and refreshed from ptrace; nothing is persisted beyond the trace event.

Dependencies/integration: integrates with generic `get_regs`, `set_regs`, `get_stack_pointer`, syscall-argument extraction, and signal-frame helpers; includes architecture kernel register structs supplied by surrounding includes.

Risks/test signals: wrong register field mapping corrupts syscall numbers, arguments, PC/SP reporting, and injected return values; validate with ptrace register fetch/set tests and known syscall traces on the architecture.

Source-read signal: reviewed complete local file (12 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/ia64/arch_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/ia64/arch_regs.h -->
# sources/test-tools/strace/src/linux/ia64/arch_regs.h

Purpose: reuses shared strace architecture logic for `ia64` by including `asm/ptrace_offsets.h` from `arch_regs.h`.

Important APIs/types/functions: this file exports the APIs provided by the included implementation rather than defining new local functions.

Control flow: the C preprocessor splices the target file into this architecture build, so runtime behavior is the shared implementation's behavior under this architecture's register/personality macros.

State/persistence behavior: no independent state; included code operates on the surrounding architecture register globals and `struct tcb` state.

Dependencies/integration: direct dependency on `asm/ptrace_offsets.h` and the macro/register contract expected by that file.

Risks/test signals: changes in the shared implementation can silently affect this architecture; compile the architecture and run syscall/signal/ioctl traces that exercise the included path.

Source-read signal: reviewed complete local file (1 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/ia64/arch_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/ia64/arch_rt_sigframe.c -->
# sources/test-tools/strace/src/linux/ia64/arch_rt_sigframe.c

Purpose: computes the address of the `ia64` realtime signal frame.

Important APIs/types/functions: struct_rt_sigframe layout; struct typedef count 0.

Control flow: obtains the tracee stack pointer and applies the architecture's frame offset adjustment before returning the address to generic signal-frame decoders.

State/persistence behavior: reads transient signal-frame data from tracee memory and prints it; no durable state is stored.

Dependencies/integration: integrates with `get_stack_pointer`, `umove_or_printaddr`, sigset printers, `ucontext_t`/`sigcontext`, and generic signal-return decoding.

Risks/test signals: frame offsets and padding are ABI-sensitive; validate with signal handler traces, blocked-mask restoration, and rt_sigreturn decoding on the architecture.

Source-read signal: reviewed complete local file (12 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/ia64/arch_rt_sigframe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/ia64/get_error.c -->
# sources/test-tools/strace/src/linux/ia64/get_error.c

Purpose: translates the `ia64` syscall return/error convention into `tcp->u_rval` and `tcp->u_error`.

Important APIs/types/functions: arch_get_error; key state includes `struct tcb`, `tcp->scno`, `tcp->u_arg`, `tcp->u_rval`, `tcp->u_error`, and register fields gr[10], gr[8].

Control flow: on syscall exit it reads the architecture return/error register convention, optionally checks negated errno ranges or dedicated error flags, sets `u_rval=-1` for errors, and otherwise records the raw return value.

State/persistence behavior: mutates only the active trace control block and current ptrace register snapshot; any tracee register changes are applied immediately through ptrace helpers.

Dependencies/integration: participates in generic syscall enter/exit decoding; depends on negated_errno.h.

Risks/test signals: Test with successful syscalls, negated errno returns, and any architecture-specific dedicated error register path.

Source-read signal: reviewed complete local file (19 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/ia64/get_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/ia64/get_scno.c -->
# sources/test-tools/strace/src/linux/ia64/get_scno.c

Purpose: extracts the current syscall number for the `ia64` backend.

Important APIs/types/functions: arch_get_scno; key state includes `struct tcb`, `tcp->scno`, `tcp->u_arg`, `tcp->u_rval`, `tcp->u_error`, and register fields gr[15].

Control flow: on syscall entry it reads the ABI syscall-number register or user offset, may perform sanity checks for stray exits, then stores the result in `tcp->scno` and returns the generic status code.

State/persistence behavior: mutates only the active trace control block and current ptrace register snapshot; any tracee register changes are applied immediately through ptrace helpers.

Dependencies/integration: participates in generic syscall enter/exit decoding; depends on architecture register globals, ptrace helpers, and common tcb fields.

Risks/test signals: Test with representative syscall entries, invalid/out-of-range numbers, and personality-specific numbering when present.

Source-read signal: reviewed complete local file (14 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/ia64/get_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/ia64/get_syscall_args.c -->
# sources/test-tools/strace/src/linux/ia64/get_syscall_args.c

Purpose: copies syscall arguments from `ia64` register state or backing register-stack memory into `tcp->u_arg`.

Important APIs/types/functions: arch_get_syscall_args; key state includes `struct tcb`, `tcp->scno`, `tcp->u_arg`, `tcp->u_rval`, `tcp->u_error`, and register fields ar[PT_AUR_BSP].

Control flow: after the syscall number is known, it reads up to `n_args(tcp)` or `MAX_ARGS` arguments from ABI-defined registers, compatibility helper code, or memory addresses derived from register-stack state, returning `1` on success or `-1` on fatal fetch failure.

State/persistence behavior: mutates only the active trace control block and current ptrace register snapshot; any tracee register changes are applied immediately through ptrace helpers.

Dependencies/integration: participates in generic syscall enter/exit decoding; depends on asm/rse.h.

Risks/test signals: Test with six-argument syscalls, compatibility personalities, and ptrace permission/fault cases for memory-backed argument locations.

Source-read signal: reviewed complete local file (32 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/ia64/get_syscall_args.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/ia64/ioctls_arch0.h -->
# sources/test-tools/strace/src/linux/ia64/ioctls_arch0.h

Purpose: provides the `ia64` generated architecture ioctl table, with 0 initializer rows from architecture kernel headers; examples include no concrete ioctl names.

Important APIs/types/functions: each row is `{'header, name, direction, number, size'}` data consumed by the common ioctl xlat machinery; observed direction flags include _IOC_NONE-style entries.

Control flow: no executable flow; entries are compiled into lookup arrays that let `ioctl(2)` decoding map command numbers back to symbolic names and argument direction/size.

State/persistence behavior: immutable compile-time metadata only; it neither reads traced memory nor persists runtime state.

Dependencies/integration: generated from Linux UAPI headers by `ioctls_gen.sh` and consumed by the strace ioctl decoder alongside generic include tables.

Risks/test signals: stale generated rows or wrong command sizes cause misleading ioctl names or argument decoding; test by comparing generated tables with current UAPI headers and tracing representative architecture-specific ioctl calls.

Source-read signal: reviewed complete local file (1 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/ia64/ioctls_arch0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/ia64/ioctls_inc0.h -->
# sources/test-tools/strace/src/linux/ia64/ioctls_inc0.h

Purpose: reuses shared strace architecture logic for `ia64` by including `../64/ioctls_inc.h` from `ioctls_inc0.h`.

Important APIs/types/functions: this file exports the APIs provided by the included implementation rather than defining new local functions.

Control flow: the C preprocessor splices the target file into this architecture build, so runtime behavior is the shared implementation's behavior under this architecture's register/personality macros.

State/persistence behavior: no independent state; included code operates on the surrounding architecture register globals and `struct tcb` state.

Dependencies/integration: direct dependency on `../64/ioctls_inc.h` and the macro/register contract expected by that file.

Risks/test signals: changes in the shared implementation can silently affect this architecture; compile the architecture and run syscall/signal/ioctl traces that exercise the included path.

Source-read signal: reviewed complete local file (1 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/ia64/ioctls_inc0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/ia64/raw_syscall.h -->
# sources/test-tools/strace/src/linux/ia64/raw_syscall.h

Purpose: implements a minimal zero-argument raw syscall helper for `ia64`.

Important APIs/types/functions: raw_syscall_0, STRACE_RAW_SYSCALL_H, raw_syscall_0; notable register references include r15, r8, r10, r28.

Control flow: loads the requested syscall number into the ABI register, executes the architecture trap instruction, records an error flag where the ABI exposes one, and returns the raw result register.

State/persistence behavior: operates on transient tracee/register/memory snapshots or compile-time metadata; persistent program state is not introduced here.

Dependencies/integration: Depends on inline assembly register constraints, trap instructions, clobber lists, and `kernel_ulong_t`.

Risks/test signals: incorrect constraints or clobbers can miscompile; test a harmless syscall such as getpid and an expected failing syscall on native hardware/toolchains.

Source-read signal: reviewed complete local file (41 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/ia64/raw_syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/ia64/rt_sigframe.h -->
# sources/test-tools/strace/src/linux/ia64/rt_sigframe.h

Purpose: defines the `ia64` realtime signal-frame layout used by strace.

Important APIs/types/functions: STRACE_RT_SIGFRAME_H, OFFSETOF_SIGMASK_IN_RT_SIGFRAME; struct typedef count 1.

Control flow: no direct runtime flow in the header; generic frame decoders use the typedef and offset macros when reading tracee memory.

State/persistence behavior: reads transient signal-frame data from tracee memory and prints it; no durable state is stored.

Dependencies/integration: integrates with `get_stack_pointer`, `umove_or_printaddr`, sigset printers, `ucontext_t`/`sigcontext`, and generic signal-return decoding.

Risks/test signals: frame offsets and padding are ABI-sensitive; validate with signal handler traces, blocked-mask restoration, and rt_sigreturn decoding on the architecture.

Source-read signal: reviewed complete local file (25 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/ia64/rt_sigframe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/ia64/set_error.c -->
# sources/test-tools/strace/src/linux/ia64/set_error.c

Purpose: injects a synthetic syscall error or success result into `ia64` tracee registers.

Important APIs/types/functions: arch_set_error, arch_set_success; key state includes `struct tcb`, `tcp->scno`, `tcp->u_arg`, `tcp->u_rval`, `tcp->u_error`, and register fields gr[8], gr[10].

Control flow: `arch_set_error` writes the architecture error convention from `tcp->u_error`; `arch_set_success` writes `tcp->u_rval`; implementations either poke individual user offsets or call `set_regs` after mutating the saved register block.

State/persistence behavior: mutates only the active trace control block and current ptrace register snapshot; any tracee register changes are applied immediately through ptrace helpers.

Dependencies/integration: participates in generic syscall enter/exit decoding; depends on architecture register globals, ptrace helpers, and common tcb fields.

Risks/test signals: Test with syscall fault injection for both success and errno paths, including ESRCH/disappearing-tracee behavior where relevant.

Source-read signal: reviewed complete local file (24 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/ia64/set_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/ia64/set_scno.c -->
# sources/test-tools/strace/src/linux/ia64/set_scno.c

Purpose: updates the tracee syscall number for `ia64` syscall tampering/restart support.

Important APIs/types/functions: arch_set_scno; key state includes `struct tcb`, `tcp->scno`, `tcp->u_arg`, `tcp->u_rval`, `tcp->u_error`, and register fields gr[15].

Control flow: writes the requested syscall number into the architecture orig-syscall register using `upoke`, `set_regs`, or an architecture regset such as `NT_ARM_SYSTEM_CALL`.

State/persistence behavior: mutates only the active trace control block and current ptrace register snapshot; any tracee register changes are applied immediately through ptrace helpers.

Dependencies/integration: participates in generic syscall enter/exit decoding; depends on architecture register globals, ptrace helpers, and common tcb fields.

Risks/test signals: Test by rewriting a syscall number under ptrace and confirming the kernel executes/prints the replacement call.

Source-read signal: reviewed complete local file (15 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/ia64/set_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/ia64/shuffle_scno.c -->
# sources/test-tools/strace/src/linux/ia64/shuffle_scno.c

Purpose: translates raw `ia64` syscall numbers into the table index space used by strace.

Important APIs/types/functions: shuffle_scno_pers; notable register references include none in this file.

Control flow: generic dispatch calls `shuffle_scno_pers`; implementations may leave native numbers unchanged, delegate to compat helpers, or xor/add a base offset after static assertions.

State/persistence behavior: operates on transient tracee/register/memory snapshots or compile-time metadata; persistent program state is not introduced here.

Dependencies/integration: Depends on syscall table size/base-number constants and personality id.

Risks/test signals: wrong shuffling dispatches to the wrong table; test boundary syscall numbers and personality-specific tables.

Source-read signal: reviewed complete local file (11 lines).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/ia64/shuffle_scno.c -->
