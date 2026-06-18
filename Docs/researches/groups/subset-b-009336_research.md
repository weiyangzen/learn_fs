# Research: subset-b-009336 strace Linux architecture backends

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc/syscallent.h -->
# sources/test-tools/strace/src/linux/powerpc/syscallent.h

## Purpose

This syscall table maps numeric Linux syscall slots for powerpc to strace decoder metadata. It contains about 286 explicit table entries and then composes shared rows through includes such as "../32/syscallent-common-32.h", "syscallent-common.h", "../32/subcallent.h". It defines `SYS_socket_subcall` as 500 before including the socket subcall table, so old multiplexed socket calls occupy the architecture-specific extension range expected by strace. The table starts with entries like `[100] = { 2,	TD|TFSF|TSFA,	SEN(fstatfs),			"fstatfs"		},` and ends with entries like `[402] = { 3,	TI,		SEN(msgctl),			"msgctl"		},`, which is useful when checking generated row order.

## Important APIs, Types, And Functions

This source is classified as `syscall-table` for the `powerpc` strace backend. It has SHA-1 prefix `ea81e4e7409f`, 403 lines, and 20449 bytes. Key local interface signals: includes "../32/syscallent-common-32.h", "syscallent-common.h", "../32/subcallent.h"; defines SYS_socket_subcall; 286 table rows.

## Control Flow

There is no executable control flow. The strace build includes this data into generated lookup arrays; runtime lookup indexes by syscall number, ioctl request, errno, signal, or user offset and then dispatches to generic printers/decoders.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../32/syscallent-common-32.h", "syscallent-common.h", "../32/subcallent.h" Linux ptrace regset APIs strace syscall decoder table macros. The integration point is strace's per-architecture Linux backend under `src/linux/powerpc`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Risks are numeric table drift against kernel syscall headers, wrong argument count/flags, and mismatched compat table selection; failures appear as wrong syscall names or decoder dispatch. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Compare generated tables with current kernel headers and run decoder lookup tests for representative low, high, compat, and architecture-specific numbers. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/powerpc/syscallent.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc/syscallent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc/userent.h -->
# sources/test-tools/strace/src/linux/powerpc/userent.h

## Purpose

This user-area translation table exposes `struct user` register offsets for powerpc. It uses `XLAT`, `XLAT_UOFF`, or register-size macros so strace can print `PTRACE_PEEKUSER` offsets symbolically. It composes additional generic or compatibility fields through "userent0.h". The file defines or uses `REGSIZE` to keep offset arithmetic tied to the tracee word size rather than the host compiler default.

## Important APIs, Types, And Functions

This source is classified as `userent-table` for the `powerpc` strace backend. It has SHA-1 prefix `a8aad866bf68`, 54 lines, and 1403 bytes. Key local interface signals: includes "userent0.h"; defines PT_ORIG_R3, REGSIZE.

## Control Flow

There is no executable control flow. The strace build includes this data into generated lookup arrays; runtime lookup indexes by syscall number, ioctl request, errno, signal, or user offset and then dispatches to generic printers/decoders.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "userent0.h". The integration point is strace's per-architecture Linux backend under `src/linux/powerpc`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is architecture ABI drift: these small files encode register names, audit constants, and feature macros that must match kernel and libc headers. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Compare generated tables with current kernel headers and run decoder lookup tests for representative low, high, compat, and architecture-specific numbers. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/powerpc/userent.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc/userent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64/arch_defs_.h -->
# sources/test-tools/strace/src/linux/powerpc64/arch_defs_.h

## Purpose

This architecture definition header advertises strace compile-time capabilities for the powerpc64 backend: HAVE_ARCH_OLD_SELECT, SUPPORTED_PERSONALITIES, PERSONALITY0_AUDIT_ARCH, PERSONALITY1_AUDIT_ARCH. It enables multi-personality decoding, so the same binary can switch between native and compat syscall tables according to audit architecture or runtime register state. The `PERSONALITY*_AUDIT_ARCH` macros are the bridge from seccomp/audit syscall-info records to strace personality selection.

## Important APIs, Types, And Functions

This source is classified as `arch-defs` for the `powerpc64` strace backend. It has SHA-1 prefix `1fe25401d587`, 11 lines, and 308 bytes. Key local interface signals: defines HAVE_ARCH_OLD_SELECT, SUPPORTED_PERSONALITIES, PERSONALITY0_AUDIT_ARCH, PERSONALITY1_AUDIT_ARCH.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

Linux audit architecture constants. The integration point is strace's per-architecture Linux backend under `src/linux/powerpc64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is architecture ABI drift: these small files encode register names, audit constants, and feature macros that must match kernel and libc headers. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/powerpc64/arch_defs_.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64/arch_defs_.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64/arch_fpregset.c -->
# sources/test-tools/strace/src/linux/powerpc64/arch_fpregset.c

## Purpose

This file is a one-line architecture wrapper that includes "../powerpc/arch_fpregset.c". It intentionally has no local control flow; the selected include target supplies the real implementation for this personality or endian variant.

## Important APIs, Types, And Functions

This source is classified as `include-wrapper` for the `powerpc64` strace backend. It has SHA-1 prefix `1190e3cb48e0`, 1 lines, and 38 bytes. Key local interface signals: includes "../powerpc/arch_fpregset.c".

## Control Flow

At compile time the preprocessor substitutes the referenced implementation or table into this architecture directory. Runtime behavior is therefore the behavior of the included file under this ABI selection.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../powerpc/arch_fpregset.c". The integration point is strace's per-architecture Linux backend under `src/linux/powerpc64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is include-target drift: if the shared file changes assumptions about word size, endian, or personality, this wrapper silently inherits that behavior. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/powerpc64/arch_fpregset.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64/arch_fpregset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64/arch_fpregset.h -->
# sources/test-tools/strace/src/linux/powerpc64/arch_fpregset.h

## Purpose

This file is a one-line architecture wrapper that includes "../powerpc/arch_fpregset.h". It intentionally has no local control flow; the selected include target supplies the real implementation for this personality or endian variant.

## Important APIs, Types, And Functions

This source is classified as `include-wrapper` for the `powerpc64` strace backend. It has SHA-1 prefix `f2d34f0262a8`, 1 lines, and 38 bytes. Key local interface signals: includes "../powerpc/arch_fpregset.h".

## Control Flow

At compile time the preprocessor substitutes the referenced implementation or table into this architecture directory. Runtime behavior is therefore the behavior of the included file under this ABI selection.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../powerpc/arch_fpregset.h". The integration point is strace's per-architecture Linux backend under `src/linux/powerpc64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is include-target drift: if the shared file changes assumptions about word size, endian, or personality, this wrapper silently inherits that behavior. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/powerpc64/arch_fpregset.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64/arch_fpregset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64/arch_get_personality.c -->
# sources/test-tools/strace/src/linux/powerpc64/arch_get_personality.c

## Purpose

This file implements or selects a PowerPC 64-bit architecture hook for strace. Local functions/macros are get_personality_from_syscall_info. `get_personality_from_syscall_info` maps `PTRACE_GET_SYSCALL_INFO` audit architecture records to the compat personality for bi-ABI tracing.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `powerpc64` strace backend. It has SHA-1 prefix `50636b19be42`, 13 lines, and 303 bytes. Key local interface signals: functions get_personality_from_syscall_info.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

Linux ptrace regset APIs Linux audit architecture constants. The integration point is strace's per-architecture Linux backend under `src/linux/powerpc64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Register selection mistakes produce wrong syscall numbers, arguments, or errno state, which cascades into incorrect decoder selection and misleading traces. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/powerpc64/arch_get_personality.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64/arch_get_personality.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64/arch_prstatus_regset.c -->
# sources/test-tools/strace/src/linux/powerpc64/arch_prstatus_regset.c

## Purpose

This file is a one-line architecture wrapper that includes "../powerpc/arch_prstatus_regset.c". It intentionally has no local control flow; the selected include target supplies the real implementation for this personality or endian variant.

## Important APIs, Types, And Functions

This source is classified as `include-wrapper` for the `powerpc64` strace backend. It has SHA-1 prefix `82b0a97d4cd5`, 1 lines, and 45 bytes. Key local interface signals: includes "../powerpc/arch_prstatus_regset.c".

## Control Flow

At compile time the preprocessor substitutes the referenced implementation or table into this architecture directory. Runtime behavior is therefore the behavior of the included file under this ABI selection.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../powerpc/arch_prstatus_regset.c". The integration point is strace's per-architecture Linux backend under `src/linux/powerpc64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is include-target drift: if the shared file changes assumptions about word size, endian, or personality, this wrapper silently inherits that behavior. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Decode NT_PRSTATUS/pt_regs samples with full, truncated, and oversized sizes to validate graceful printing. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/powerpc64/arch_prstatus_regset.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64/arch_prstatus_regset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64/arch_prstatus_regset.h -->
# sources/test-tools/strace/src/linux/powerpc64/arch_prstatus_regset.h

## Purpose

This file is a one-line architecture wrapper that includes "../powerpc/arch_prstatus_regset.h". It intentionally has no local control flow; the selected include target supplies the real implementation for this personality or endian variant.

## Important APIs, Types, And Functions

This source is classified as `include-wrapper` for the `powerpc64` strace backend. It has SHA-1 prefix `0e09d7290d48`, 1 lines, and 45 bytes. Key local interface signals: includes "../powerpc/arch_prstatus_regset.h".

## Control Flow

At compile time the preprocessor substitutes the referenced implementation or table into this architecture directory. Runtime behavior is therefore the behavior of the included file under this ABI selection.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../powerpc/arch_prstatus_regset.h". The integration point is strace's per-architecture Linux backend under `src/linux/powerpc64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is include-target drift: if the shared file changes assumptions about word size, endian, or personality, this wrapper silently inherits that behavior. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Decode NT_PRSTATUS/pt_regs samples with full, truncated, and oversized sizes to validate graceful printing. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/powerpc64/arch_prstatus_regset.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64/arch_prstatus_regset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64/arch_pt_regs64.c -->
# sources/test-tools/strace/src/linux/powerpc64/arch_pt_regs64.c

## Purpose

This file implements or selects a PowerPC 64-bit architecture hook for strace. Local functions/macros are none declared locally. The pt_regs decoder prints kernel `struct pt_regs` fields for ptrace or signal-frame contexts, with compat guards on bi-ABI targets.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `powerpc64` strace backend. It has SHA-1 prefix `4c10a74904a5`, 10 lines, and 194 bytes. Key local interface signals: includes "arch_pt_regs64.h", "../powerpc/arch_pt_regs64.c".

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

preprocessor includes: "arch_pt_regs64.h", "../powerpc/arch_pt_regs64.c". The integration point is strace's per-architecture Linux backend under `src/linux/powerpc64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Structure layout drift or alignment mistakes can over/under-print register fields; the code mitigates this with size checks but depends on exact ABI offsets. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Decode NT_PRSTATUS/pt_regs samples with full, truncated, and oversized sizes to validate graceful printing. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/powerpc64/arch_pt_regs64.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64/arch_pt_regs64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64/arch_pt_regs64.h -->
# sources/test-tools/strace/src/linux/powerpc64/arch_pt_regs64.h

## Purpose

This file implements or selects a PowerPC 64-bit architecture hook for strace. Local functions/macros are STRACE_ARCH_PT_REGS64_H. The pt_regs decoder prints kernel `struct pt_regs` fields for ptrace or signal-frame contexts, with compat guards on bi-ABI targets.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `powerpc64` strace backend. It has SHA-1 prefix `c282e6b088f7`, 13 lines, and 272 bytes. Key local interface signals: defines STRACE_ARCH_PT_REGS64_H.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

strace architecture include/build system. The integration point is strace's per-architecture Linux backend under `src/linux/powerpc64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Structure layout drift or alignment mistakes can over/under-print register fields; the code mitigates this with size checks but depends on exact ABI offsets. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Decode NT_PRSTATUS/pt_regs samples with full, truncated, and oversized sizes to validate graceful printing. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/powerpc64/arch_pt_regs64.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64/arch_pt_regs64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64/arch_regs.c -->
# sources/test-tools/strace/src/linux/powerpc64/arch_regs.c

## Purpose

This file is a one-line architecture wrapper that includes "../powerpc/arch_regs.c". It intentionally has no local control flow; the selected include target supplies the real implementation for this personality or endian variant.

## Important APIs, Types, And Functions

This source is classified as `include-wrapper` for the `powerpc64` strace backend. It has SHA-1 prefix `dcc5e30bce03`, 1 lines, and 34 bytes. Key local interface signals: includes "../powerpc/arch_regs.c".

## Control Flow

At compile time the preprocessor substitutes the referenced implementation or table into this architecture directory. Runtime behavior is therefore the behavior of the included file under this ABI selection.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../powerpc/arch_regs.c". The integration point is strace's per-architecture Linux backend under `src/linux/powerpc64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is include-target drift: if the shared file changes assumptions about word size, endian, or personality, this wrapper silently inherits that behavior. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/powerpc64/arch_regs.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64/arch_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64/arch_rt_sigframe.c -->
# sources/test-tools/strace/src/linux/powerpc64/arch_rt_sigframe.c

## Purpose

This source computes the runtime address of the powerpc64 realtime signal frame from the tracee stack pointer, with ABI-specific stack-bias or compat handling where required.

## Important APIs, Types, And Functions

This source is classified as `rt-sigframe` for the `powerpc64` strace backend. It has SHA-1 prefix `a56fbdaf7f46`, 23 lines, and 576 bytes. Key local interface signals: includes "../powerpc/arch_rt_sigframe.c"; defines FUNC_GET_RT_SIGFRAME_ADDR, FUNC_GET_RT_SIGFRAME_ADDR; functions ppc_get_rt_sigframe_addr.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

preprocessor includes: "../powerpc/arch_rt_sigframe.c". The integration point is strace's per-architecture Linux backend under `src/linux/powerpc64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Structure layout drift or alignment mistakes can over/under-print register fields; the code mitigates this with size checks but depends on exact ABI offsets. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Exercise signal-delivery and sigreturn traces and verify saved mask/frame addresses for native and compat tasks. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/powerpc64/arch_rt_sigframe.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64/arch_rt_sigframe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64/arch_sigreturn.c -->
# sources/test-tools/strace/src/linux/powerpc64/arch_sigreturn.c

## Purpose

This file is a one-line architecture wrapper that includes "../powerpc/arch_sigreturn.c". It intentionally has no local control flow; the selected include target supplies the real implementation for this personality or endian variant.

## Important APIs, Types, And Functions

This source is classified as `include-wrapper` for the `powerpc64` strace backend. It has SHA-1 prefix `ef16a8604fa6`, 1 lines, and 39 bytes. Key local interface signals: includes "../powerpc/arch_sigreturn.c".

## Control Flow

At compile time the preprocessor substitutes the referenced implementation or table into this architecture directory. Runtime behavior is therefore the behavior of the included file under this ABI selection.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../powerpc/arch_sigreturn.c". The integration point is strace's per-architecture Linux backend under `src/linux/powerpc64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is include-target drift: if the shared file changes assumptions about word size, endian, or personality, this wrapper silently inherits that behavior. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Exercise signal-delivery and sigreturn traces and verify saved mask/frame addresses for native and compat tasks. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/powerpc64/arch_sigreturn.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64/arch_sigreturn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64/errnoent.h -->
# sources/test-tools/strace/src/linux/powerpc64/errnoent.h

## Purpose

This file is a one-line architecture wrapper that includes "../powerpc/errnoent.h". It intentionally has no local control flow; the selected include target supplies the real implementation for this personality or endian variant.

## Important APIs, Types, And Functions

This source is classified as `include-wrapper` for the `powerpc64` strace backend. It has SHA-1 prefix `d5fda75f0fe7`, 1 lines, and 33 bytes. Key local interface signals: includes "../powerpc/errnoent.h".

## Control Flow

At compile time the preprocessor substitutes the referenced implementation or table into this architecture directory. Runtime behavior is therefore the behavior of the included file under this ABI selection.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../powerpc/errnoent.h". The integration point is strace's per-architecture Linux backend under `src/linux/powerpc64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is include-target drift: if the shared file changes assumptions about word size, endian, or personality, this wrapper silently inherits that behavior. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/powerpc64/errnoent.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64/errnoent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64/get_error.c -->
# sources/test-tools/strace/src/linux/powerpc64/get_error.c

## Purpose

This file is a one-line architecture wrapper that includes "../powerpc/get_error.c". It intentionally has no local control flow; the selected include target supplies the real implementation for this personality or endian variant.

## Important APIs, Types, And Functions

This source is classified as `include-wrapper` for the `powerpc64` strace backend. It has SHA-1 prefix `7c8fd19a0510`, 1 lines, and 34 bytes. Key local interface signals: includes "../powerpc/get_error.c".

## Control Flow

At compile time the preprocessor substitutes the referenced implementation or table into this architecture directory. Runtime behavior is therefore the behavior of the included file under this ABI selection.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../powerpc/get_error.c". The integration point is strace's per-architecture Linux backend under `src/linux/powerpc64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is include-target drift: if the shared file changes assumptions about word size, endian, or personality, this wrapper silently inherits that behavior. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/powerpc64/get_error.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64/get_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64/get_scno.c -->
# sources/test-tools/strace/src/linux/powerpc64/get_scno.c

## Purpose

This file implements or selects a PowerPC 64-bit architecture hook for strace. Local functions/macros are arch_get_scno. `arch_get_scno` extracts the syscall number from the architecture syscall-number register or, for s390 restart_syscall, from `NT_S390_SYSTEM_CALL` when the normal register is clobbered by a negated errno.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `powerpc64` strace backend. It has SHA-1 prefix `f0c008e09342`, 22 lines, and 597 bytes. Key local interface signals: functions arch_get_scno.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

strace architecture include/build system. The integration point is strace's per-architecture Linux backend under `src/linux/powerpc64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Register selection mistakes produce wrong syscall numbers, arguments, or errno state, which cascades into incorrect decoder selection and misleading traces. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Run syscall-entry/exit tests under ptrace, including failure returns, restart_syscall where applicable, syscall tampering, and compat personality switching. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/powerpc64/get_scno.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64/get_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64/get_syscall_args.c -->
# sources/test-tools/strace/src/linux/powerpc64/get_syscall_args.c

## Purpose

This file is a one-line architecture wrapper that includes "../powerpc/get_syscall_args.c". It intentionally has no local control flow; the selected include target supplies the real implementation for this personality or endian variant.

## Important APIs, Types, And Functions

This source is classified as `include-wrapper` for the `powerpc64` strace backend. It has SHA-1 prefix `b12c6f78bac7`, 1 lines, and 41 bytes. Key local interface signals: includes "../powerpc/get_syscall_args.c".

## Control Flow

At compile time the preprocessor substitutes the referenced implementation or table into this architecture directory. Runtime behavior is therefore the behavior of the included file under this ABI selection.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../powerpc/get_syscall_args.c". The integration point is strace's per-architecture Linux backend under `src/linux/powerpc64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is include-target drift: if the shared file changes assumptions about word size, endian, or personality, this wrapper silently inherits that behavior. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/powerpc64/get_syscall_args.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64/get_syscall_args.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64/ioctls_arch0.h -->
# sources/test-tools/strace/src/linux/powerpc64/ioctls_arch0.h

## Purpose

This file is a one-line architecture wrapper that includes "../powerpc/ioctls_arch0.h". It intentionally has no local control flow; the selected include target supplies the real implementation for this personality or endian variant.

## Important APIs, Types, And Functions

This source is classified as `include-wrapper` for the `powerpc64` strace backend. It has SHA-1 prefix `2e4a863d3002`, 1 lines, and 37 bytes. Key local interface signals: includes "../powerpc/ioctls_arch0.h".

## Control Flow

At compile time the preprocessor substitutes the referenced implementation or table into this architecture directory. Runtime behavior is therefore the behavior of the included file under this ABI selection.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../powerpc/ioctls_arch0.h". The integration point is strace's per-architecture Linux backend under `src/linux/powerpc64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is include-target drift: if the shared file changes assumptions about word size, endian, or personality, this wrapper silently inherits that behavior. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/powerpc64/ioctls_arch0.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64/ioctls_arch0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64/ioctls_arch1.h -->
# sources/test-tools/strace/src/linux/powerpc64/ioctls_arch1.h

## Purpose

This file is a one-line architecture wrapper that includes "../powerpc/ioctls_arch0.h". It intentionally has no local control flow; the selected include target supplies the real implementation for this personality or endian variant.

## Important APIs, Types, And Functions

This source is classified as `include-wrapper` for the `powerpc64` strace backend. It has SHA-1 prefix `2e4a863d3002`, 1 lines, and 37 bytes. Key local interface signals: includes "../powerpc/ioctls_arch0.h".

## Control Flow

At compile time the preprocessor substitutes the referenced implementation or table into this architecture directory. Runtime behavior is therefore the behavior of the included file under this ABI selection.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../powerpc/ioctls_arch0.h". The integration point is strace's per-architecture Linux backend under `src/linux/powerpc64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is include-target drift: if the shared file changes assumptions about word size, endian, or personality, this wrapper silently inherits that behavior. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/powerpc64/ioctls_arch1.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64/ioctls_arch1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64/ioctls_inc0.h -->
# sources/test-tools/strace/src/linux/powerpc64/ioctls_inc0.h

## Purpose

This file is a one-line architecture wrapper that includes "../64/ioctls_inc.h". It intentionally has no local control flow; the selected include target supplies the real implementation for this personality or endian variant.

## Important APIs, Types, And Functions

This source is classified as `include-wrapper` for the `powerpc64` strace backend. It has SHA-1 prefix `3defd9a34cb2`, 1 lines, and 30 bytes. Key local interface signals: includes "../64/ioctls_inc.h".

## Control Flow

At compile time the preprocessor substitutes the referenced implementation or table into this architecture directory. Runtime behavior is therefore the behavior of the included file under this ABI selection.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../64/ioctls_inc.h". The integration point is strace's per-architecture Linux backend under `src/linux/powerpc64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is include-target drift: if the shared file changes assumptions about word size, endian, or personality, this wrapper silently inherits that behavior. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/powerpc64/ioctls_inc0.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64/ioctls_inc0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64/ioctls_inc1.h -->
# sources/test-tools/strace/src/linux/powerpc64/ioctls_inc1.h

## Purpose

This file is a one-line architecture wrapper that includes "../powerpc/ioctls_inc0.h". It intentionally has no local control flow; the selected include target supplies the real implementation for this personality or endian variant.

## Important APIs, Types, And Functions

This source is classified as `include-wrapper` for the `powerpc64` strace backend. It has SHA-1 prefix `3c999be3f14e`, 1 lines, and 36 bytes. Key local interface signals: includes "../powerpc/ioctls_inc0.h".

## Control Flow

At compile time the preprocessor substitutes the referenced implementation or table into this architecture directory. Runtime behavior is therefore the behavior of the included file under this ABI selection.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../powerpc/ioctls_inc0.h". The integration point is strace's per-architecture Linux backend under `src/linux/powerpc64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is include-target drift: if the shared file changes assumptions about word size, endian, or personality, this wrapper silently inherits that behavior. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/powerpc64/ioctls_inc1.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64/ioctls_inc1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64/raw_syscall.h -->
# sources/test-tools/strace/src/linux/powerpc64/raw_syscall.h

## Purpose

This file is a one-line architecture wrapper that includes "../powerpc/raw_syscall.h". It intentionally has no local control flow; the selected include target supplies the real implementation for this personality or endian variant.

## Important APIs, Types, And Functions

This source is classified as `include-wrapper` for the `powerpc64` strace backend. It has SHA-1 prefix `215aa41c269c`, 1 lines, and 36 bytes. Key local interface signals: includes "../powerpc/raw_syscall.h".

## Control Flow

At compile time the preprocessor substitutes the referenced implementation or table into this architecture directory. Runtime behavior is therefore the behavior of the included file under this ABI selection.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../powerpc/raw_syscall.h". The integration point is strace's per-architecture Linux backend under `src/linux/powerpc64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is include-target drift: if the shared file changes assumptions about word size, endian, or personality, this wrapper silently inherits that behavior. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/powerpc64/raw_syscall.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64/raw_syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64/rt_sigframe.h -->
# sources/test-tools/strace/src/linux/powerpc64/rt_sigframe.h

## Purpose

This header models the user-space realtime signal frame layout for powerpc64, including `ucontext`, `siginfo`, or mask offsets needed by strace signal-frame decoding.

## Important APIs, Types, And Functions

This source is classified as `rt-sigframe` for the `powerpc64` strace backend. It has SHA-1 prefix `da537c5aa1c8`, 22 lines, and 435 bytes. Key local interface signals: includes "../generic/rt_sigframe.h", <signal.h>; defines STRACE_RT_SIGFRAME_H.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

preprocessor includes: "../generic/rt_sigframe.h", <signal.h>. The integration point is strace's per-architecture Linux backend under `src/linux/powerpc64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Structure layout drift or alignment mistakes can over/under-print register fields; the code mitigates this with size checks but depends on exact ABI offsets. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Exercise signal-delivery and sigreturn traces and verify saved mask/frame addresses for native and compat tasks. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/powerpc64/rt_sigframe.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64/rt_sigframe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64/set_error.c -->
# sources/test-tools/strace/src/linux/powerpc64/set_error.c

## Purpose

This file is a one-line architecture wrapper that includes "../powerpc/set_error.c". It intentionally has no local control flow; the selected include target supplies the real implementation for this personality or endian variant.

## Important APIs, Types, And Functions

This source is classified as `include-wrapper` for the `powerpc64` strace backend. It has SHA-1 prefix `171964bee29c`, 1 lines, and 34 bytes. Key local interface signals: includes "../powerpc/set_error.c".

## Control Flow

At compile time the preprocessor substitutes the referenced implementation or table into this architecture directory. Runtime behavior is therefore the behavior of the included file under this ABI selection.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../powerpc/set_error.c". The integration point is strace's per-architecture Linux backend under `src/linux/powerpc64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is include-target drift: if the shared file changes assumptions about word size, endian, or personality, this wrapper silently inherits that behavior. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/powerpc64/set_error.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64/set_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64/set_scno.c -->
# sources/test-tools/strace/src/linux/powerpc64/set_scno.c

## Purpose

This file is a one-line architecture wrapper that includes "../powerpc/set_scno.c". It intentionally has no local control flow; the selected include target supplies the real implementation for this personality or endian variant.

## Important APIs, Types, And Functions

This source is classified as `include-wrapper` for the `powerpc64` strace backend. It has SHA-1 prefix `3fe3d69f6cac`, 1 lines, and 33 bytes. Key local interface signals: includes "../powerpc/set_scno.c".

## Control Flow

At compile time the preprocessor substitutes the referenced implementation or table into this architecture directory. Runtime behavior is therefore the behavior of the included file under this ABI selection.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../powerpc/set_scno.c". The integration point is strace's per-architecture Linux backend under `src/linux/powerpc64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is include-target drift: if the shared file changes assumptions about word size, endian, or personality, this wrapper silently inherits that behavior. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/powerpc64/set_scno.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64/set_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64/syscallent.h -->
# sources/test-tools/strace/src/linux/powerpc64/syscallent.h

## Purpose

This syscall table maps numeric Linux syscall slots for powerpc64 to strace decoder metadata. It contains about 278 explicit table entries and then composes shared rows through includes such as "syscallent-common.h", "../64/subcallent.h". It defines `SYS_socket_subcall` as 500 before including the socket subcall table, so old multiplexed socket calls occupy the architecture-specific extension range expected by strace. The table starts with entries like `[100] = { 2,	TD|TFSF|TSFA,	SEN(fstatfs),			"fstatfs"		},` and ends with entries like `[402] = { 3,	TI,		SEN(msgctl),			"msgctl"		},`, which is useful when checking generated row order.

## Important APIs, Types, And Functions

This source is classified as `syscall-table` for the `powerpc64` strace backend. It has SHA-1 prefix `7c35a33e4218`, 404 lines, and 20382 bytes. Key local interface signals: includes "syscallent-common.h", "../64/subcallent.h"; defines SYS_socket_subcall; 278 table rows.

## Control Flow

There is no executable control flow. The strace build includes this data into generated lookup arrays; runtime lookup indexes by syscall number, ioctl request, errno, signal, or user offset and then dispatches to generic printers/decoders.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "syscallent-common.h", "../64/subcallent.h" Linux ptrace regset APIs strace syscall decoder table macros. The integration point is strace's per-architecture Linux backend under `src/linux/powerpc64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Risks are numeric table drift against kernel syscall headers, wrong argument count/flags, and mismatched compat table selection; failures appear as wrong syscall names or decoder dispatch. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Compare generated tables with current kernel headers and run decoder lookup tests for representative low, high, compat, and architecture-specific numbers. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/powerpc64/syscallent.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64/syscallent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64/syscallent1.h -->
# sources/test-tools/strace/src/linux/powerpc64/syscallent1.h

## Purpose

This file is a one-line architecture wrapper that includes "../powerpc/syscallent.h". It intentionally has no local control flow; the selected include target supplies the real implementation for this personality or endian variant.

## Important APIs, Types, And Functions

This source is classified as `include-wrapper` for the `powerpc64` strace backend. It has SHA-1 prefix `7dee6eaab61c`, 1 lines, and 35 bytes. Key local interface signals: includes "../powerpc/syscallent.h".

## Control Flow

At compile time the preprocessor substitutes the referenced implementation or table into this architecture directory. Runtime behavior is therefore the behavior of the included file under this ABI selection.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../powerpc/syscallent.h". The integration point is strace's per-architecture Linux backend under `src/linux/powerpc64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is include-target drift: if the shared file changes assumptions about word size, endian, or personality, this wrapper silently inherits that behavior. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/powerpc64/syscallent1.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64/syscallent1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64/userent.h -->
# sources/test-tools/strace/src/linux/powerpc64/userent.h

## Purpose

This file is a one-line architecture wrapper that includes "../powerpc/userent.h". It intentionally has no local control flow; the selected include target supplies the real implementation for this personality or endian variant.

## Important APIs, Types, And Functions

This source is classified as `include-wrapper` for the `powerpc64` strace backend. It has SHA-1 prefix `2d49048f517a`, 1 lines, and 32 bytes. Key local interface signals: includes "../powerpc/userent.h".

## Control Flow

At compile time the preprocessor substitutes the referenced implementation or table into this architecture directory. Runtime behavior is therefore the behavior of the included file under this ABI selection.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../powerpc/userent.h". The integration point is strace's per-architecture Linux backend under `src/linux/powerpc64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is include-target drift: if the shared file changes assumptions about word size, endian, or personality, this wrapper silently inherits that behavior. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/powerpc64/userent.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64/userent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64le/arch_defs_.h -->
# sources/test-tools/strace/src/linux/powerpc64le/arch_defs_.h

## Purpose

This architecture definition header advertises strace compile-time capabilities for the powerpc64le backend: HAVE_ARCH_OLD_SELECT, PERSONALITY0_AUDIT_ARCH. The `PERSONALITY*_AUDIT_ARCH` macros are the bridge from seccomp/audit syscall-info records to strace personality selection.

## Important APIs, Types, And Functions

This source is classified as `arch-defs` for the `powerpc64le` strace backend. It has SHA-1 prefix `a3c9b9a450b2`, 9 lines, and 220 bytes. Key local interface signals: defines HAVE_ARCH_OLD_SELECT, PERSONALITY0_AUDIT_ARCH.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

Linux audit architecture constants. The integration point is strace's per-architecture Linux backend under `src/linux/powerpc64le`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is architecture ABI drift: these small files encode register names, audit constants, and feature macros that must match kernel and libc headers. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/powerpc64le/arch_defs_.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64le/arch_defs_.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64le/arch_fpregset.c -->
# sources/test-tools/strace/src/linux/powerpc64le/arch_fpregset.c

## Purpose

This file is a one-line architecture wrapper that includes "../powerpc/arch_fpregset.c". It intentionally has no local control flow; the selected include target supplies the real implementation for this personality or endian variant.

## Important APIs, Types, And Functions

This source is classified as `include-wrapper` for the `powerpc64le` strace backend. It has SHA-1 prefix `1190e3cb48e0`, 1 lines, and 38 bytes. Key local interface signals: includes "../powerpc/arch_fpregset.c".

## Control Flow

At compile time the preprocessor substitutes the referenced implementation or table into this architecture directory. Runtime behavior is therefore the behavior of the included file under this ABI selection.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../powerpc/arch_fpregset.c". The integration point is strace's per-architecture Linux backend under `src/linux/powerpc64le`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is include-target drift: if the shared file changes assumptions about word size, endian, or personality, this wrapper silently inherits that behavior. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/powerpc64le/arch_fpregset.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64le/arch_fpregset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64le/arch_fpregset.h -->
# sources/test-tools/strace/src/linux/powerpc64le/arch_fpregset.h

## Purpose

This file is a one-line architecture wrapper that includes "../powerpc/arch_fpregset.h". It intentionally has no local control flow; the selected include target supplies the real implementation for this personality or endian variant.

## Important APIs, Types, And Functions

This source is classified as `include-wrapper` for the `powerpc64le` strace backend. It has SHA-1 prefix `f2d34f0262a8`, 1 lines, and 38 bytes. Key local interface signals: includes "../powerpc/arch_fpregset.h".

## Control Flow

At compile time the preprocessor substitutes the referenced implementation or table into this architecture directory. Runtime behavior is therefore the behavior of the included file under this ABI selection.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../powerpc/arch_fpregset.h". The integration point is strace's per-architecture Linux backend under `src/linux/powerpc64le`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is include-target drift: if the shared file changes assumptions about word size, endian, or personality, this wrapper silently inherits that behavior. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/powerpc64le/arch_fpregset.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64le/arch_fpregset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64le/arch_prstatus_regset.c -->
# sources/test-tools/strace/src/linux/powerpc64le/arch_prstatus_regset.c

## Purpose

This file is a one-line architecture wrapper that includes "../powerpc/arch_prstatus_regset.c". It intentionally has no local control flow; the selected include target supplies the real implementation for this personality or endian variant.

## Important APIs, Types, And Functions

This source is classified as `include-wrapper` for the `powerpc64le` strace backend. It has SHA-1 prefix `82b0a97d4cd5`, 1 lines, and 45 bytes. Key local interface signals: includes "../powerpc/arch_prstatus_regset.c".

## Control Flow

At compile time the preprocessor substitutes the referenced implementation or table into this architecture directory. Runtime behavior is therefore the behavior of the included file under this ABI selection.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../powerpc/arch_prstatus_regset.c". The integration point is strace's per-architecture Linux backend under `src/linux/powerpc64le`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is include-target drift: if the shared file changes assumptions about word size, endian, or personality, this wrapper silently inherits that behavior. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Decode NT_PRSTATUS/pt_regs samples with full, truncated, and oversized sizes to validate graceful printing. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/powerpc64le/arch_prstatus_regset.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64le/arch_prstatus_regset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64le/arch_prstatus_regset.h -->
# sources/test-tools/strace/src/linux/powerpc64le/arch_prstatus_regset.h

## Purpose

This file is a one-line architecture wrapper that includes "../powerpc/arch_prstatus_regset.h". It intentionally has no local control flow; the selected include target supplies the real implementation for this personality or endian variant.

## Important APIs, Types, And Functions

This source is classified as `include-wrapper` for the `powerpc64le` strace backend. It has SHA-1 prefix `0e09d7290d48`, 1 lines, and 45 bytes. Key local interface signals: includes "../powerpc/arch_prstatus_regset.h".

## Control Flow

At compile time the preprocessor substitutes the referenced implementation or table into this architecture directory. Runtime behavior is therefore the behavior of the included file under this ABI selection.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../powerpc/arch_prstatus_regset.h". The integration point is strace's per-architecture Linux backend under `src/linux/powerpc64le`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is include-target drift: if the shared file changes assumptions about word size, endian, or personality, this wrapper silently inherits that behavior. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Decode NT_PRSTATUS/pt_regs samples with full, truncated, and oversized sizes to validate graceful printing. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/powerpc64le/arch_prstatus_regset.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64le/arch_prstatus_regset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64le/arch_pt_regs64.c -->
# sources/test-tools/strace/src/linux/powerpc64le/arch_pt_regs64.c

## Purpose

This file is a one-line architecture wrapper that includes "../powerpc64/arch_pt_regs64.c". It intentionally has no local control flow; the selected include target supplies the real implementation for this personality or endian variant.

## Important APIs, Types, And Functions

This source is classified as `include-wrapper` for the `powerpc64le` strace backend. It has SHA-1 prefix `8f6a39c3fee2`, 1 lines, and 41 bytes. Key local interface signals: includes "../powerpc64/arch_pt_regs64.c".

## Control Flow

At compile time the preprocessor substitutes the referenced implementation or table into this architecture directory. Runtime behavior is therefore the behavior of the included file under this ABI selection.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../powerpc64/arch_pt_regs64.c". The integration point is strace's per-architecture Linux backend under `src/linux/powerpc64le`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is include-target drift: if the shared file changes assumptions about word size, endian, or personality, this wrapper silently inherits that behavior. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Decode NT_PRSTATUS/pt_regs samples with full, truncated, and oversized sizes to validate graceful printing. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/powerpc64le/arch_pt_regs64.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64le/arch_pt_regs64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64le/arch_regs.c -->
# sources/test-tools/strace/src/linux/powerpc64le/arch_regs.c

## Purpose

This file is a one-line architecture wrapper that includes "../powerpc/arch_regs.c". It intentionally has no local control flow; the selected include target supplies the real implementation for this personality or endian variant.

## Important APIs, Types, And Functions

This source is classified as `include-wrapper` for the `powerpc64le` strace backend. It has SHA-1 prefix `dcc5e30bce03`, 1 lines, and 34 bytes. Key local interface signals: includes "../powerpc/arch_regs.c".

## Control Flow

At compile time the preprocessor substitutes the referenced implementation or table into this architecture directory. Runtime behavior is therefore the behavior of the included file under this ABI selection.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../powerpc/arch_regs.c". The integration point is strace's per-architecture Linux backend under `src/linux/powerpc64le`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is include-target drift: if the shared file changes assumptions about word size, endian, or personality, this wrapper silently inherits that behavior. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/powerpc64le/arch_regs.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64le/arch_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64le/arch_rt_sigframe.c -->
# sources/test-tools/strace/src/linux/powerpc64le/arch_rt_sigframe.c

## Purpose

This source computes the runtime address of the powerpc64le realtime signal frame from the tracee stack pointer, with ABI-specific stack-bias or compat handling where required.

## Important APIs, Types, And Functions

This source is classified as `rt-sigframe` for the `powerpc64le` strace backend. It has SHA-1 prefix `41dc03b4f721`, 13 lines, and 286 bytes. Key local interface signals: no exported symbols; it is consumed through textual inclusion or generated-table compilation.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

strace architecture include/build system. The integration point is strace's per-architecture Linux backend under `src/linux/powerpc64le`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Structure layout drift or alignment mistakes can over/under-print register fields; the code mitigates this with size checks but depends on exact ABI offsets. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Exercise signal-delivery and sigreturn traces and verify saved mask/frame addresses for native and compat tasks. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/powerpc64le/arch_rt_sigframe.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64le/arch_rt_sigframe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64le/errnoent.h -->
# sources/test-tools/strace/src/linux/powerpc64le/errnoent.h

## Purpose

This file is a one-line architecture wrapper that includes "../powerpc64/errnoent.h". It intentionally has no local control flow; the selected include target supplies the real implementation for this personality or endian variant.

## Important APIs, Types, And Functions

This source is classified as `include-wrapper` for the `powerpc64le` strace backend. It has SHA-1 prefix `006f8024b668`, 1 lines, and 35 bytes. Key local interface signals: includes "../powerpc64/errnoent.h".

## Control Flow

At compile time the preprocessor substitutes the referenced implementation or table into this architecture directory. Runtime behavior is therefore the behavior of the included file under this ABI selection.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../powerpc64/errnoent.h". The integration point is strace's per-architecture Linux backend under `src/linux/powerpc64le`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is include-target drift: if the shared file changes assumptions about word size, endian, or personality, this wrapper silently inherits that behavior. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/powerpc64le/errnoent.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64le/errnoent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64le/get_error.c -->
# sources/test-tools/strace/src/linux/powerpc64le/get_error.c

## Purpose

This file is a one-line architecture wrapper that includes "../powerpc64/get_error.c". It intentionally has no local control flow; the selected include target supplies the real implementation for this personality or endian variant.

## Important APIs, Types, And Functions

This source is classified as `include-wrapper` for the `powerpc64le` strace backend. It has SHA-1 prefix `e78269c8e857`, 1 lines, and 36 bytes. Key local interface signals: includes "../powerpc64/get_error.c".

## Control Flow

At compile time the preprocessor substitutes the referenced implementation or table into this architecture directory. Runtime behavior is therefore the behavior of the included file under this ABI selection.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../powerpc64/get_error.c". The integration point is strace's per-architecture Linux backend under `src/linux/powerpc64le`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is include-target drift: if the shared file changes assumptions about word size, endian, or personality, this wrapper silently inherits that behavior. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/powerpc64le/get_error.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64le/get_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64le/get_scno.c -->
# sources/test-tools/strace/src/linux/powerpc64le/get_scno.c

## Purpose

This file implements or selects a PowerPC 64-bit architecture hook for strace. Local functions/macros are arch_get_scno. `arch_get_scno` extracts the syscall number from the architecture syscall-number register or, for s390 restart_syscall, from `NT_S390_SYSTEM_CALL` when the normal register is clobbered by a negated errno.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `powerpc64le` strace backend. It has SHA-1 prefix `287281cd2db8`, 14 lines, and 273 bytes. Key local interface signals: functions arch_get_scno.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

strace architecture include/build system. The integration point is strace's per-architecture Linux backend under `src/linux/powerpc64le`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Register selection mistakes produce wrong syscall numbers, arguments, or errno state, which cascades into incorrect decoder selection and misleading traces. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Run syscall-entry/exit tests under ptrace, including failure returns, restart_syscall where applicable, syscall tampering, and compat personality switching. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/powerpc64le/get_scno.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64le/get_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64le/get_syscall_args.c -->
# sources/test-tools/strace/src/linux/powerpc64le/get_syscall_args.c

## Purpose

This file is a one-line architecture wrapper that includes "../powerpc64/get_syscall_args.c". It intentionally has no local control flow; the selected include target supplies the real implementation for this personality or endian variant.

## Important APIs, Types, And Functions

This source is classified as `include-wrapper` for the `powerpc64le` strace backend. It has SHA-1 prefix `417c2f44b212`, 1 lines, and 43 bytes. Key local interface signals: includes "../powerpc64/get_syscall_args.c".

## Control Flow

At compile time the preprocessor substitutes the referenced implementation or table into this architecture directory. Runtime behavior is therefore the behavior of the included file under this ABI selection.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../powerpc64/get_syscall_args.c". The integration point is strace's per-architecture Linux backend under `src/linux/powerpc64le`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is include-target drift: if the shared file changes assumptions about word size, endian, or personality, this wrapper silently inherits that behavior. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/powerpc64le/get_syscall_args.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64le/get_syscall_args.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64le/ioctls_arch0.h -->
# sources/test-tools/strace/src/linux/powerpc64le/ioctls_arch0.h

## Purpose

This file is a one-line architecture wrapper that includes "../powerpc64/ioctls_arch0.h". It intentionally has no local control flow; the selected include target supplies the real implementation for this personality or endian variant.

## Important APIs, Types, And Functions

This source is classified as `include-wrapper` for the `powerpc64le` strace backend. It has SHA-1 prefix `0a459443c94d`, 1 lines, and 39 bytes. Key local interface signals: includes "../powerpc64/ioctls_arch0.h".

## Control Flow

At compile time the preprocessor substitutes the referenced implementation or table into this architecture directory. Runtime behavior is therefore the behavior of the included file under this ABI selection.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../powerpc64/ioctls_arch0.h". The integration point is strace's per-architecture Linux backend under `src/linux/powerpc64le`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is include-target drift: if the shared file changes assumptions about word size, endian, or personality, this wrapper silently inherits that behavior. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/powerpc64le/ioctls_arch0.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64le/ioctls_arch0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64le/ioctls_inc0.h -->
# sources/test-tools/strace/src/linux/powerpc64le/ioctls_inc0.h

## Purpose

This file is a one-line architecture wrapper that includes "../powerpc64/ioctls_inc0.h". It intentionally has no local control flow; the selected include target supplies the real implementation for this personality or endian variant.

## Important APIs, Types, And Functions

This source is classified as `include-wrapper` for the `powerpc64le` strace backend. It has SHA-1 prefix `0846ecd923a6`, 1 lines, and 38 bytes. Key local interface signals: includes "../powerpc64/ioctls_inc0.h".

## Control Flow

At compile time the preprocessor substitutes the referenced implementation or table into this architecture directory. Runtime behavior is therefore the behavior of the included file under this ABI selection.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../powerpc64/ioctls_inc0.h". The integration point is strace's per-architecture Linux backend under `src/linux/powerpc64le`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is include-target drift: if the shared file changes assumptions about word size, endian, or personality, this wrapper silently inherits that behavior. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/powerpc64le/ioctls_inc0.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64le/ioctls_inc0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64le/raw_syscall.h -->
# sources/test-tools/strace/src/linux/powerpc64le/raw_syscall.h

## Purpose

This file is a one-line architecture wrapper that includes "../powerpc64/raw_syscall.h". It intentionally has no local control flow; the selected include target supplies the real implementation for this personality or endian variant.

## Important APIs, Types, And Functions

This source is classified as `include-wrapper` for the `powerpc64le` strace backend. It has SHA-1 prefix `d911bb77cde2`, 1 lines, and 38 bytes. Key local interface signals: includes "../powerpc64/raw_syscall.h".

## Control Flow

At compile time the preprocessor substitutes the referenced implementation or table into this architecture directory. Runtime behavior is therefore the behavior of the included file under this ABI selection.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../powerpc64/raw_syscall.h". The integration point is strace's per-architecture Linux backend under `src/linux/powerpc64le`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is include-target drift: if the shared file changes assumptions about word size, endian, or personality, this wrapper silently inherits that behavior. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/powerpc64le/raw_syscall.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64le/raw_syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64le/rt_sigframe.h -->
# sources/test-tools/strace/src/linux/powerpc64le/rt_sigframe.h

## Purpose

This file is a one-line architecture wrapper that includes "../powerpc64/rt_sigframe.h". It intentionally has no local control flow; the selected include target supplies the real implementation for this personality or endian variant.

## Important APIs, Types, And Functions

This source is classified as `include-wrapper` for the `powerpc64le` strace backend. It has SHA-1 prefix `93dacbc734a4`, 1 lines, and 38 bytes. Key local interface signals: includes "../powerpc64/rt_sigframe.h".

## Control Flow

At compile time the preprocessor substitutes the referenced implementation or table into this architecture directory. Runtime behavior is therefore the behavior of the included file under this ABI selection.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../powerpc64/rt_sigframe.h". The integration point is strace's per-architecture Linux backend under `src/linux/powerpc64le`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is include-target drift: if the shared file changes assumptions about word size, endian, or personality, this wrapper silently inherits that behavior. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Exercise signal-delivery and sigreturn traces and verify saved mask/frame addresses for native and compat tasks. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/powerpc64le/rt_sigframe.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64le/rt_sigframe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64le/set_error.c -->
# sources/test-tools/strace/src/linux/powerpc64le/set_error.c

## Purpose

This file is a one-line architecture wrapper that includes "../powerpc64/set_error.c". It intentionally has no local control flow; the selected include target supplies the real implementation for this personality or endian variant.

## Important APIs, Types, And Functions

This source is classified as `include-wrapper` for the `powerpc64le` strace backend. It has SHA-1 prefix `f34638b27804`, 1 lines, and 36 bytes. Key local interface signals: includes "../powerpc64/set_error.c".

## Control Flow

At compile time the preprocessor substitutes the referenced implementation or table into this architecture directory. Runtime behavior is therefore the behavior of the included file under this ABI selection.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../powerpc64/set_error.c". The integration point is strace's per-architecture Linux backend under `src/linux/powerpc64le`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is include-target drift: if the shared file changes assumptions about word size, endian, or personality, this wrapper silently inherits that behavior. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/powerpc64le/set_error.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64le/set_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64le/set_scno.c -->
# sources/test-tools/strace/src/linux/powerpc64le/set_scno.c

## Purpose

This file is a one-line architecture wrapper that includes "../powerpc64/set_scno.c". It intentionally has no local control flow; the selected include target supplies the real implementation for this personality or endian variant.

## Important APIs, Types, And Functions

This source is classified as `include-wrapper` for the `powerpc64le` strace backend. It has SHA-1 prefix `96fd6b3f244b`, 1 lines, and 35 bytes. Key local interface signals: includes "../powerpc64/set_scno.c".

## Control Flow

At compile time the preprocessor substitutes the referenced implementation or table into this architecture directory. Runtime behavior is therefore the behavior of the included file under this ABI selection.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../powerpc64/set_scno.c". The integration point is strace's per-architecture Linux backend under `src/linux/powerpc64le`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is include-target drift: if the shared file changes assumptions about word size, endian, or personality, this wrapper silently inherits that behavior. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/powerpc64le/set_scno.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64le/set_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64le/syscallent.h -->
# sources/test-tools/strace/src/linux/powerpc64le/syscallent.h

## Purpose

This file is a one-line architecture wrapper that includes "../powerpc64/syscallent.h". It intentionally has no local control flow; the selected include target supplies the real implementation for this personality or endian variant.

## Important APIs, Types, And Functions

This source is classified as `include-wrapper` for the `powerpc64le` strace backend. It has SHA-1 prefix `83e5bc2492f1`, 1 lines, and 37 bytes. Key local interface signals: includes "../powerpc64/syscallent.h".

## Control Flow

At compile time the preprocessor substitutes the referenced implementation or table into this architecture directory. Runtime behavior is therefore the behavior of the included file under this ABI selection.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../powerpc64/syscallent.h". The integration point is strace's per-architecture Linux backend under `src/linux/powerpc64le`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is include-target drift: if the shared file changes assumptions about word size, endian, or personality, this wrapper silently inherits that behavior. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/powerpc64le/syscallent.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64le/syscallent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64le/userent.h -->
# sources/test-tools/strace/src/linux/powerpc64le/userent.h

## Purpose

This file is a one-line architecture wrapper that includes "../powerpc64/userent.h". It intentionally has no local control flow; the selected include target supplies the real implementation for this personality or endian variant.

## Important APIs, Types, And Functions

This source is classified as `include-wrapper` for the `powerpc64le` strace backend. It has SHA-1 prefix `c96003afc8f5`, 1 lines, and 34 bytes. Key local interface signals: includes "../powerpc64/userent.h".

## Control Flow

At compile time the preprocessor substitutes the referenced implementation or table into this architecture directory. Runtime behavior is therefore the behavior of the included file under this ABI selection.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../powerpc64/userent.h". The integration point is strace's per-architecture Linux backend under `src/linux/powerpc64le`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is include-target drift: if the shared file changes assumptions about word size, endian, or personality, this wrapper silently inherits that behavior. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/powerpc64le/userent.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64le/userent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/riscv64/arch_defs_.h -->
# sources/test-tools/strace/src/linux/riscv64/arch_defs_.h

## Purpose

This architecture definition header advertises strace compile-time capabilities for the riscv64 backend: ARCH_NEEDS_SET_ERROR_FOR_SCNO_TAMPERING, PERSONALITY0_AUDIT_ARCH. The `PERSONALITY*_AUDIT_ARCH` macros are the bridge from seccomp/audit syscall-info records to strace personality selection.

## Important APIs, Types, And Functions

This source is classified as `arch-defs` for the `riscv64` strace backend. It has SHA-1 prefix `f07d33efd2eb`, 17 lines, and 542 bytes. Key local interface signals: defines ARCH_NEEDS_SET_ERROR_FOR_SCNO_TAMPERING, PERSONALITY0_AUDIT_ARCH.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

Linux audit architecture constants. The integration point is strace's per-architecture Linux backend under `src/linux/riscv64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is architecture ABI drift: these small files encode register names, audit constants, and feature macros that must match kernel and libc headers. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/riscv64/arch_defs_.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/riscv64/arch_defs_.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/riscv64/arch_prstatus_regset.c -->
# sources/test-tools/strace/src/linux/riscv64/arch_prstatus_regset.c

## Purpose

This decoder prints NT_PRSTATUS register-set payloads for riscv64. It bounds reads to `MIN(sizeof(regs), size)`, rejects misaligned or zero sizes, and prints only fields present in the fetched prefix. When the kernel supplies a larger blob than the known structure, it emits a more-data marker instead of over-reading unknown layout.

## Important APIs, Types, And Functions

This source is classified as `prstatus-regset` for the `riscv64` strace backend. It has SHA-1 prefix `7b6104e4fdc3`, 151 lines, and 4222 bytes. Key local interface signals: functions arch_decode_prstatus_regset.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

strace structured printing macros tracee-memory readers. The integration point is strace's per-architecture Linux backend under `src/linux/riscv64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Structure layout drift or alignment mistakes can over/under-print register fields; the code mitigates this with size checks but depends on exact ABI offsets. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Decode NT_PRSTATUS/pt_regs samples with full, truncated, and oversized sizes to validate graceful printing. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/riscv64/arch_prstatus_regset.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/riscv64/arch_prstatus_regset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/riscv64/arch_prstatus_regset.h -->
# sources/test-tools/strace/src/linux/riscv64/arch_prstatus_regset.h

## Purpose

This header defines the type alias used to decode NT_PRSTATUS register-set payloads for riscv64 and sets `HAVE_ARCH_PRSTATUS_REGSET`.

## Important APIs, Types, And Functions

This source is classified as `prstatus-regset` for the `riscv64` strace backend. It has SHA-1 prefix `702c242cc2cd`, 15 lines, and 343 bytes. Key local interface signals: defines STRACE_ARCH_PRSTATUS_REGSET_H, HAVE_ARCH_PRSTATUS_REGSET.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

strace architecture include/build system. The integration point is strace's per-architecture Linux backend under `src/linux/riscv64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Structure layout drift or alignment mistakes can over/under-print register fields; the code mitigates this with size checks but depends on exact ABI offsets. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Decode NT_PRSTATUS/pt_regs samples with full, truncated, and oversized sizes to validate graceful printing. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/riscv64/arch_prstatus_regset.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/riscv64/arch_prstatus_regset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/riscv64/arch_regs.c -->
# sources/test-tools/strace/src/linux/riscv64/arch_regs.c

## Purpose

This file implements or selects a RISC-V 64-bit architecture hook for strace. Local functions/macros are ARCH_REGS_FOR_GETREGSET, ARCH_PC_REG, ARCH_SP_REG. The file binds the generic register-fetch path to concrete global register storage plus `ARCH_PC_REG` and `ARCH_SP_REG` macros used by shared code.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `riscv64` strace backend. It has SHA-1 prefix `f9c93608fd44`, 11 lines, and 285 bytes. Key local interface signals: defines ARCH_REGS_FOR_GETREGSET, ARCH_PC_REG, ARCH_SP_REG.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

strace architecture include/build system. The integration point is strace's per-architecture Linux backend under `src/linux/riscv64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is architecture ABI drift: these small files encode register names, audit constants, and feature macros that must match kernel and libc headers. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/riscv64/arch_regs.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/riscv64/arch_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/riscv64/get_error.c -->
# sources/test-tools/strace/src/linux/riscv64/get_error.c

## Purpose

This file implements or selects a RISC-V 64-bit architecture hook for strace. Local functions/macros are arch_get_error. `arch_get_error` interprets the architecture error convention and fills `tcp->u_rval`/`tcp->u_error`, using negated errno helpers or condition-code bits as appropriate.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `riscv64` strace backend. It has SHA-1 prefix `a7a477f5d381`, 19 lines, and 383 bytes. Key local interface signals: includes "negated_errno.h"; functions arch_get_error.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

preprocessor includes: "negated_errno.h" strace `negated_errno.h` helpers. The integration point is strace's per-architecture Linux backend under `src/linux/riscv64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Register selection mistakes produce wrong syscall numbers, arguments, or errno state, which cascades into incorrect decoder selection and misleading traces. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Run syscall-entry/exit tests under ptrace, including failure returns, restart_syscall where applicable, syscall tampering, and compat personality switching. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/riscv64/get_error.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/riscv64/get_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/riscv64/get_scno.c -->
# sources/test-tools/strace/src/linux/riscv64/get_scno.c

## Purpose

This file implements or selects a RISC-V 64-bit architecture hook for strace. Local functions/macros are arch_get_scno. `arch_get_scno` extracts the syscall number from the architecture syscall-number register or, for s390 restart_syscall, from `NT_S390_SYSTEM_CALL` when the normal register is clobbered by a negated errno.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `riscv64` strace backend. It has SHA-1 prefix `11edb5bf86a5`, 14 lines, and 271 bytes. Key local interface signals: functions arch_get_scno.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

strace architecture include/build system. The integration point is strace's per-architecture Linux backend under `src/linux/riscv64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Register selection mistakes produce wrong syscall numbers, arguments, or errno state, which cascades into incorrect decoder selection and misleading traces. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Run syscall-entry/exit tests under ptrace, including failure returns, restart_syscall where applicable, syscall tampering, and compat personality switching. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/riscv64/get_scno.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/riscv64/get_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/riscv64/get_syscall_args.c -->
# sources/test-tools/strace/src/linux/riscv64/get_syscall_args.c

## Purpose

This file implements or selects a RISC-V 64-bit architecture hook for strace. Local functions/macros are arch_get_syscall_args. `arch_get_syscall_args` copies up to six syscall arguments from ABI-defined argument registers into `tcp->u_arg`; compat paths zero-extend 32-bit register values.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `riscv64` strace backend. It has SHA-1 prefix `bf3f51cf99c6`, 19 lines, and 441 bytes. Key local interface signals: functions arch_get_syscall_args.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

strace architecture include/build system. The integration point is strace's per-architecture Linux backend under `src/linux/riscv64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Register selection mistakes produce wrong syscall numbers, arguments, or errno state, which cascades into incorrect decoder selection and misleading traces. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Run syscall-entry/exit tests under ptrace, including failure returns, restart_syscall where applicable, syscall tampering, and compat personality switching. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/riscv64/get_syscall_args.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/riscv64/get_syscall_args.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/riscv64/ioctls_arch0.h -->
# sources/test-tools/strace/src/linux/riscv64/ioctls_arch0.h

## Purpose

This generated ioctl table records 0 architecture-local ioctl definitions for riscv64, with header names, symbolic names, `_IOC_*` direction, request numbers, and encoded argument sizes.

## Important APIs, Types, And Functions

This source is classified as `ioctl-arch-table` for the `riscv64` strace backend. It has SHA-1 prefix `804af0edad89`, 1 lines, and 92 bytes. Key local interface signals: no exported symbols; it is consumed through textual inclusion or generated-table compilation.

## Control Flow

There is no executable control flow. The strace build includes this data into generated lookup arrays; runtime lookup indexes by syscall number, ioctl request, errno, signal, or user offset and then dispatches to generic printers/decoders.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

strace architecture include/build system. The integration point is strace's per-architecture Linux backend under `src/linux/riscv64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Risks are stale generated ioctl metadata, request-size mismatches between 32-bit and 64-bit personalities, and duplicate request numbers resolving to the wrong symbolic name. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Compare generated tables with current kernel headers and run decoder lookup tests for representative low, high, compat, and architecture-specific numbers. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/riscv64/ioctls_arch0.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/riscv64/ioctls_arch0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/riscv64/ioctls_inc0.h -->
# sources/test-tools/strace/src/linux/riscv64/ioctls_inc0.h

## Purpose

This file is a one-line architecture wrapper that includes "../64/ioctls_inc.h". It intentionally has no local control flow; the selected include target supplies the real implementation for this personality or endian variant.

## Important APIs, Types, And Functions

This source is classified as `include-wrapper` for the `riscv64` strace backend. It has SHA-1 prefix `3defd9a34cb2`, 1 lines, and 30 bytes. Key local interface signals: includes "../64/ioctls_inc.h".

## Control Flow

At compile time the preprocessor substitutes the referenced implementation or table into this architecture directory. Runtime behavior is therefore the behavior of the included file under this ABI selection.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../64/ioctls_inc.h". The integration point is strace's per-architecture Linux backend under `src/linux/riscv64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is include-target drift: if the shared file changes assumptions about word size, endian, or personality, this wrapper silently inherits that behavior. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/riscv64/ioctls_inc0.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/riscv64/ioctls_inc0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/riscv64/raw_syscall.h -->
# sources/test-tools/strace/src/linux/riscv64/raw_syscall.h

## Purpose

This header defines an inline `raw_syscall_0` helper for riscv64 bootstrap/probing paths. It binds syscall-number and return registers with inline assembly and reports a separate error flag pointer to the generic raw syscall caller.

## Important APIs, Types, And Functions

This source is classified as `raw-syscall` for the `riscv64` strace backend. It has SHA-1 prefix `2ae0fd1528dc`, 29 lines, and 607 bytes. Key local interface signals: includes "kernel_types.h"; defines STRACE_RAW_SYSCALL_H, raw_syscall_0; functions raw_syscall_0.

## Control Flow

Callers pass a syscall number to `raw_syscall_0`; inline assembly loads the ABI syscall register, enters the kernel, records whether an error occurred, and returns the raw result without using libc wrappers.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

preprocessor includes: "kernel_types.h". The integration point is strace's per-architecture Linux backend under `src/linux/riscv64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is architecture ABI drift: these small files encode register names, audit constants, and feature macros that must match kernel and libc headers. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Compile and execute raw-syscall smoke tests for a harmless syscall such as getpid or gettid, verifying raw return and error reporting. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/riscv64/raw_syscall.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/riscv64/raw_syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/riscv64/set_error.c -->
# sources/test-tools/strace/src/linux/riscv64/set_error.c

## Purpose

This file implements or selects a RISC-V 64-bit architecture hook for strace. Local functions/macros are arch_set_error, arch_set_success. The set-error/success hooks mutate the cached register set, update condition-code/error bits when the ABI needs them, and call `set_regs(tcp->pid)` to persist the change into the tracee.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `riscv64` strace backend. It has SHA-1 prefix `53bbdc8dfddf`, 20 lines, and 346 bytes. Key local interface signals: functions arch_set_error, arch_set_success.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

It mutates the cached architecture register block and persists it into the stopped tracee with `set_regs(tcp->pid)`.

## Dependencies And Integration Points

strace architecture include/build system. The integration point is strace's per-architecture Linux backend under `src/linux/riscv64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Register tampering bugs can leave the tracee with inconsistent return values or condition-code bits, so failures are behavioral rather than cosmetic. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Run syscall-entry/exit tests under ptrace, including failure returns, restart_syscall where applicable, syscall tampering, and compat personality switching. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/riscv64/set_error.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/riscv64/set_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/riscv64/set_scno.c -->
# sources/test-tools/strace/src/linux/riscv64/set_scno.c

## Purpose

This file implements or selects a RISC-V 64-bit architecture hook for strace. Local functions/macros are arch_set_scno.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `riscv64` strace backend. It has SHA-1 prefix `ec6e7ab30875`, 15 lines, and 320 bytes. Key local interface signals: functions arch_set_scno.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

It mutates the cached architecture register block and persists it into the stopped tracee with `set_regs(tcp->pid)`.

## Dependencies And Integration Points

Linux ptrace regset APIs. The integration point is strace's per-architecture Linux backend under `src/linux/riscv64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Register tampering bugs can leave the tracee with inconsistent return values or condition-code bits, so failures are behavioral rather than cosmetic. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/riscv64/set_scno.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/riscv64/set_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/riscv64/syscallent.h -->
# sources/test-tools/strace/src/linux/riscv64/syscallent.h

## Purpose

This syscall table maps numeric Linux syscall slots for riscv64 to strace decoder metadata. It contains about 1 explicit table entries and then composes shared rows through includes such as "../64/syscallent.h". The table starts with entries like `[259] = { 3,	TM,		SEN(riscv_flush_icache),	"riscv_flush_icache"	},` and ends with entries like `[259] = { 3,	TM,		SEN(riscv_flush_icache),	"riscv_flush_icache"	},`, which is useful when checking generated row order. RISC-V adds `riscv_flush_icache` at syscall 259 after importing the generic 64-bit syscall table.

## Important APIs, Types, And Functions

This source is classified as `syscall-table` for the `riscv64` strace backend. It has SHA-1 prefix `f8d49cf186ab`, 11 lines, and 301 bytes. Key local interface signals: includes "../64/syscallent.h"; 1 table rows.

## Control Flow

There is no executable control flow. The strace build includes this data into generated lookup arrays; runtime lookup indexes by syscall number, ioctl request, errno, signal, or user offset and then dispatches to generic printers/decoders.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../64/syscallent.h" strace syscall decoder table macros. The integration point is strace's per-architecture Linux backend under `src/linux/riscv64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Risks are numeric table drift against kernel syscall headers, wrong argument count/flags, and mismatched compat table selection; failures appear as wrong syscall names or decoder dispatch. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Compare generated tables with current kernel headers and run decoder lookup tests for representative low, high, compat, and architecture-specific numbers. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/riscv64/syscallent.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/riscv64/syscallent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390/arch_defs_.h -->
# sources/test-tools/strace/src/linux/s390/arch_defs_.h

## Purpose

This architecture definition header advertises strace compile-time capabilities for the s390 backend: HAVE_ARCH_OLD_MMAP, HAVE_ARCH_OLD_MMAP_PGOFF, HAVE_ARCH_UID16_SYSCALLS, CAN_ARCH_BE_COMPAT_ON_64BIT_KERNEL, PERSONALITY0_AUDIT_ARCH. The `PERSONALITY*_AUDIT_ARCH` macros are the bridge from seccomp/audit syscall-info records to strace personality selection.

## Important APIs, Types, And Functions

This source is classified as `arch-defs` for the `s390` strace backend. It has SHA-1 prefix `4b5c36b7a720`, 12 lines, and 330 bytes. Key local interface signals: defines HAVE_ARCH_OLD_MMAP, HAVE_ARCH_OLD_MMAP_PGOFF, HAVE_ARCH_UID16_SYSCALLS, CAN_ARCH_BE_COMPAT_ON_64BIT_KERNEL, PERSONALITY0_AUDIT_ARCH.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

Linux audit architecture constants. The integration point is strace's per-architecture Linux backend under `src/linux/s390`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is architecture ABI drift: these small files encode register names, audit constants, and feature macros that must match kernel and libc headers. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/s390/arch_defs_.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390/arch_defs_.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390/arch_prstatus_regset.c -->
# sources/test-tools/strace/src/linux/s390/arch_prstatus_regset.c

## Purpose

This decoder prints NT_PRSTATUS register-set payloads for s390. It bounds reads to `MIN(sizeof(regs), size)`, rejects misaligned or zero sizes, and prints only fields present in the fetched prefix. When the kernel supplies a larger blob than the known structure, it emits a more-data marker instead of over-reading unknown layout.

## Important APIs, Types, And Functions

This source is classified as `prstatus-regset` for the `s390` strace backend. It has SHA-1 prefix `42d3e6320b34`, 63 lines, and 1678 bytes. Key local interface signals: defines TRACEE_KLONGSIZE, TRACEE_KLONGSIZE; functions arch_decode_prstatus_regset.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

strace structured printing macros tracee-memory readers. The integration point is strace's per-architecture Linux backend under `src/linux/s390`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Structure layout drift or alignment mistakes can over/under-print register fields; the code mitigates this with size checks but depends on exact ABI offsets. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Decode NT_PRSTATUS/pt_regs samples with full, truncated, and oversized sizes to validate graceful printing. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/s390/arch_prstatus_regset.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390/arch_prstatus_regset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390/arch_prstatus_regset.h -->
# sources/test-tools/strace/src/linux/s390/arch_prstatus_regset.h

## Purpose

This header defines the type alias used to decode NT_PRSTATUS register-set payloads for s390 and sets `HAVE_ARCH_PRSTATUS_REGSET`.

## Important APIs, Types, And Functions

This source is classified as `prstatus-regset` for the `s390` strace backend. It has SHA-1 prefix `586cc1a0b684`, 15 lines, and 329 bytes. Key local interface signals: defines STRACE_ARCH_PRSTATUS_REGSET_H, HAVE_ARCH_PRSTATUS_REGSET.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

strace architecture include/build system. The integration point is strace's per-architecture Linux backend under `src/linux/s390`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Structure layout drift or alignment mistakes can over/under-print register fields; the code mitigates this with size checks but depends on exact ABI offsets. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Decode NT_PRSTATUS/pt_regs samples with full, truncated, and oversized sizes to validate graceful printing. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/s390/arch_prstatus_regset.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390/arch_prstatus_regset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390/arch_regs.c -->
# sources/test-tools/strace/src/linux/s390/arch_regs.c

## Purpose

This file implements or selects a s390 32-bit architecture hook for strace. Local functions/macros are ARCH_REGS_FOR_GETREGSET, ARCH_PC_REG, ARCH_SP_REG. The file binds the generic register-fetch path to concrete global register storage plus `ARCH_PC_REG` and `ARCH_SP_REG` macros used by shared code.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `s390` strace backend. It has SHA-1 prefix `f873c8450fcb`, 12 lines, and 352 bytes. Key local interface signals: defines ARCH_REGS_FOR_GETREGSET, ARCH_PC_REG, ARCH_SP_REG.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

Linux ptrace regset APIs. The integration point is strace's per-architecture Linux backend under `src/linux/s390`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is architecture ABI drift: these small files encode register names, audit constants, and feature macros that must match kernel and libc headers. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/s390/arch_regs.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390/arch_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390/arch_sigreturn.c -->
# sources/test-tools/strace/src/linux/s390/arch_sigreturn.c

## Purpose

This file decodes the architecture-specific sigreturn frame for s390. It reads frame data from the stack pointer, prints the saved signal mask address or fields, and handles compat structure sizing where present.

## Important APIs, Types, And Functions

This source is classified as `sigreturn` for the `s390` strace backend. It has SHA-1 prefix `5018087a384a`, 28 lines, and 519 bytes. Key local interface signals: defines SIGNAL_FRAMESIZE, PTR_TYPE; functions arch_sigreturn.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

strace architecture include/build system. The integration point is strace's per-architecture Linux backend under `src/linux/s390`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is architecture ABI drift: these small files encode register names, audit constants, and feature macros that must match kernel and libc headers. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Exercise signal-delivery and sigreturn traces and verify saved mask/frame addresses for native and compat tasks. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/s390/arch_sigreturn.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390/arch_sigreturn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390/check_scno.c -->
# sources/test-tools/strace/src/linux/s390/check_scno.c

## Purpose

This file implements or selects a s390 32-bit architecture hook for strace. Local functions/macros are arch_check_scno. `arch_get_scno` extracts the syscall number from the architecture syscall-number register or, for s390 restart_syscall, from `NT_S390_SYSTEM_CALL` when the normal register is clobbered by a negated errno. `arch_check_scno` validates or adjusts syscall numbers before dispatch, including architecture-specific handling of out-of-range or multiplexed encodings.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `s390` strace backend. It has SHA-1 prefix `55e2c5522295`, 32 lines, and 696 bytes. Key local interface signals: functions arch_check_scno.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

Linux ptrace regset APIs. The integration point is strace's per-architecture Linux backend under `src/linux/s390`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Register selection mistakes produce wrong syscall numbers, arguments, or errno state, which cascades into incorrect decoder selection and misleading traces. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Run syscall-entry/exit tests under ptrace, including failure returns, restart_syscall where applicable, syscall tampering, and compat personality switching. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/s390/check_scno.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390/check_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390/get_error.c -->
# sources/test-tools/strace/src/linux/s390/get_error.c

## Purpose

This file implements or selects a s390 32-bit architecture hook for strace. Local functions/macros are arch_get_error. `arch_get_error` interprets the architecture error convention and fills `tcp->u_rval`/`tcp->u_error`, using negated errno helpers or condition-code bits as appropriate.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `s390` strace backend. It has SHA-1 prefix `542930b86a93`, 23 lines, and 462 bytes. Key local interface signals: includes "negated_errno.h"; defines ARCH_REGSET; functions arch_get_error.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

preprocessor includes: "negated_errno.h" strace `negated_errno.h` helpers. The integration point is strace's per-architecture Linux backend under `src/linux/s390`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Register selection mistakes produce wrong syscall numbers, arguments, or errno state, which cascades into incorrect decoder selection and misleading traces. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Run syscall-entry/exit tests under ptrace, including failure returns, restart_syscall where applicable, syscall tampering, and compat personality switching. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/s390/get_error.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390/get_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390/get_scno.c -->
# sources/test-tools/strace/src/linux/s390/get_scno.c

## Purpose

This file implements or selects a s390 32-bit architecture hook for strace. Local functions/macros are arch_get_scno. `arch_get_scno` extracts the syscall number from the architecture syscall-number register or, for s390 restart_syscall, from `NT_S390_SYSTEM_CALL` when the normal register is clobbered by a negated errno.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `s390` strace backend. It has SHA-1 prefix `0cafc0b3a030`, 51 lines, and 1173 bytes. Key local interface signals: includes "negated_errno.h"; defines ARCH_REGSET, NT_S390_SYSTEM_CALL; functions arch_get_scno.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

preprocessor includes: "negated_errno.h" Linux ptrace regset APIs strace `negated_errno.h` helpers. The integration point is strace's per-architecture Linux backend under `src/linux/s390`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Register selection mistakes produce wrong syscall numbers, arguments, or errno state, which cascades into incorrect decoder selection and misleading traces. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Run syscall-entry/exit tests under ptrace, including failure returns, restart_syscall where applicable, syscall tampering, and compat personality switching. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/s390/get_scno.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390/get_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390/get_syscall_args.c -->
# sources/test-tools/strace/src/linux/s390/get_syscall_args.c

## Purpose

This file implements or selects a s390 32-bit architecture hook for strace. Local functions/macros are arch_get_syscall_args. `arch_get_syscall_args` copies up to six syscall arguments from ABI-defined argument registers into `tcp->u_arg`; compat paths zero-extend 32-bit register values.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `s390` strace backend. It has SHA-1 prefix `14c304fab4dc`, 23 lines, and 540 bytes. Key local interface signals: defines ARCH_REGSET; functions arch_get_syscall_args.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

strace architecture include/build system. The integration point is strace's per-architecture Linux backend under `src/linux/s390`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Register selection mistakes produce wrong syscall numbers, arguments, or errno state, which cascades into incorrect decoder selection and misleading traces. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Run syscall-entry/exit tests under ptrace, including failure returns, restart_syscall where applicable, syscall tampering, and compat personality switching. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/s390/get_syscall_args.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390/get_syscall_args.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390/ioctls_arch0.h -->
# sources/test-tools/strace/src/linux/s390/ioctls_arch0.h

## Purpose

This generated ioctl table records 185 architecture-local ioctl definitions for s390, with header names, symbolic names, `_IOC_*` direction, request numbers, and encoded argument sizes. Boundary rows include `{ "asm/chsc.h", "CHSC_INFO_CCL", _IOC_READ|_IOC_WRITE, 0x6386, 0x1014 },` and `{ "linux/kvm.h", "KVM_UNREGISTER_COALESCED_MMIO", _IOC_WRITE, 0xae68, 0x10 },`, showing the source header family and final request preserved by generation.

## Important APIs, Types, And Functions

This source is classified as `ioctl-arch-table` for the `s390` strace backend. It has SHA-1 prefix `caab416b16d6`, 186 lines, and 12702 bytes. Key local interface signals: 185 table rows.

## Control Flow

There is no executable control flow. The strace build includes this data into generated lookup arrays; runtime lookup indexes by syscall number, ioctl request, errno, signal, or user offset and then dispatches to generic printers/decoders.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

Linux ioctl encoding macros and generated `ioctls_gen.sh` output. The integration point is strace's per-architecture Linux backend under `src/linux/s390`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Risks are stale generated ioctl metadata, request-size mismatches between 32-bit and 64-bit personalities, and duplicate request numbers resolving to the wrong symbolic name. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Compare generated tables with current kernel headers and run decoder lookup tests for representative low, high, compat, and architecture-specific numbers. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/s390/ioctls_arch0.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390/ioctls_arch0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390/ioctls_inc0.h -->
# sources/test-tools/strace/src/linux/s390/ioctls_inc0.h

## Purpose

This file is a one-line architecture wrapper that includes "../32/ioctls_inc.h". It intentionally has no local control flow; the selected include target supplies the real implementation for this personality or endian variant.

## Important APIs, Types, And Functions

This source is classified as `include-wrapper` for the `s390` strace backend. It has SHA-1 prefix `d5c2d9fe71d8`, 1 lines, and 30 bytes. Key local interface signals: includes "../32/ioctls_inc.h".

## Control Flow

At compile time the preprocessor substitutes the referenced implementation or table into this architecture directory. Runtime behavior is therefore the behavior of the included file under this ABI selection.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../32/ioctls_inc.h". The integration point is strace's per-architecture Linux backend under `src/linux/s390`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is include-target drift: if the shared file changes assumptions about word size, endian, or personality, this wrapper silently inherits that behavior. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/s390/ioctls_inc0.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390/ioctls_inc0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390/raw_syscall.h -->
# sources/test-tools/strace/src/linux/s390/raw_syscall.h

## Purpose

This header defines an inline `raw_syscall_0` helper for s390 bootstrap/probing paths. It binds syscall-number and return registers with inline assembly and reports a separate error flag pointer to the generic raw syscall caller. The implementation uses an SVC-style trap sequence for the architecture.

## Important APIs, Types, And Functions

This source is classified as `raw-syscall` for the `s390` strace backend. It has SHA-1 prefix `239b5e948a14`, 29 lines, and 607 bytes. Key local interface signals: includes "kernel_types.h"; defines STRACE_RAW_SYSCALL_H, raw_syscall_0; functions raw_syscall_0.

## Control Flow

Callers pass a syscall number to `raw_syscall_0`; inline assembly loads the ABI syscall register, enters the kernel, records whether an error occurred, and returns the raw result without using libc wrappers.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

preprocessor includes: "kernel_types.h". The integration point is strace's per-architecture Linux backend under `src/linux/s390`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is architecture ABI drift: these small files encode register names, audit constants, and feature macros that must match kernel and libc headers. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Compile and execute raw-syscall smoke tests for a harmless syscall such as getpid or gettid, verifying raw return and error reporting. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/s390/raw_syscall.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390/raw_syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390/rt_sigframe.h -->
# sources/test-tools/strace/src/linux/s390/rt_sigframe.h

## Purpose

This header models the user-space realtime signal frame layout for s390, including `ucontext`, `siginfo`, or mask offsets needed by strace signal-frame decoding.

## Important APIs, Types, And Functions

This source is classified as `rt-sigframe` for the `s390` strace backend. It has SHA-1 prefix `70258f5b0489`, 27 lines, and 557 bytes. Key local interface signals: includes <signal.h>; defines STRACE_RT_SIGFRAME_H, SIGNAL_FRAMESIZE, SIGNAL_FRAMESIZE.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

preprocessor includes: <signal.h>. The integration point is strace's per-architecture Linux backend under `src/linux/s390`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Structure layout drift or alignment mistakes can over/under-print register fields; the code mitigates this with size checks but depends on exact ABI offsets. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Exercise signal-delivery and sigreturn traces and verify saved mask/frame addresses for native and compat tasks. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/s390/rt_sigframe.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390/rt_sigframe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390/set_error.c -->
# sources/test-tools/strace/src/linux/s390/set_error.c

## Purpose

This file implements or selects a s390 32-bit architecture hook for strace. Local functions/macros are arch_set_error, arch_set_success. The set-error/success hooks mutate the cached register set, update condition-code/error bits when the ABI needs them, and call `set_regs(tcp->pid)` to persist the change into the tracee.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `s390` strace backend. It has SHA-1 prefix `a93f4286d888`, 24 lines, and 419 bytes. Key local interface signals: defines ARCH_REGSET; functions arch_set_error, arch_set_success.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

It mutates the cached architecture register block and persists it into the stopped tracee with `set_regs(tcp->pid)`.

## Dependencies And Integration Points

strace architecture include/build system. The integration point is strace's per-architecture Linux backend under `src/linux/s390`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Register tampering bugs can leave the tracee with inconsistent return values or condition-code bits, so failures are behavioral rather than cosmetic. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Run syscall-entry/exit tests under ptrace, including failure returns, restart_syscall where applicable, syscall tampering, and compat personality switching. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/s390/set_error.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390/set_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390/set_scno.c -->
# sources/test-tools/strace/src/linux/s390/set_scno.c

## Purpose

This file implements or selects a s390 32-bit architecture hook for strace. Local functions/macros are arch_set_scno.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `s390` strace backend. It has SHA-1 prefix `c5d4e7e87fdd`, 19 lines, and 387 bytes. Key local interface signals: defines ARCH_REGSET; functions arch_set_scno.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

It mutates the cached architecture register block and persists it into the stopped tracee with `set_regs(tcp->pid)`.

## Dependencies And Integration Points

Linux ptrace regset APIs. The integration point is strace's per-architecture Linux backend under `src/linux/s390`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Register tampering bugs can leave the tracee with inconsistent return values or condition-code bits, so failures are behavioral rather than cosmetic. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/s390/set_scno.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390/set_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390/syscallent.h -->
# sources/test-tools/strace/src/linux/s390/syscallent.h

## Purpose

This syscall table maps numeric Linux syscall slots for s390 to strace decoder metadata. It contains about 297 explicit table entries and then composes shared rows through includes such as "../32/syscallent-common-32.h", "syscallent-common.h", "../32/subcallent.h". It defines `SYS_socket_subcall` as 500 before including the socket subcall table, so old multiplexed socket calls occupy the architecture-specific extension range expected by strace. The table starts with entries like `[100] = { 2,	TD|TFSF|TSFA,	SEN(fstatfs),			"fstatfs"		},` and ends with entries like `[402] = { 3,	TI,		SEN(msgctl),			"msgctl"		},`, which is useful when checking generated row order.

## Important APIs, Types, And Functions

This source is classified as `syscall-table` for the `s390` strace backend. It has SHA-1 prefix `80d45e65c669`, 414 lines, and 20395 bytes. Key local interface signals: includes "../32/syscallent-common-32.h", "syscallent-common.h", "../32/subcallent.h"; defines SYS_socket_subcall; 297 table rows.

## Control Flow

There is no executable control flow. The strace build includes this data into generated lookup arrays; runtime lookup indexes by syscall number, ioctl request, errno, signal, or user offset and then dispatches to generic printers/decoders.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../32/syscallent-common-32.h", "syscallent-common.h", "../32/subcallent.h" Linux ptrace regset APIs strace syscall decoder table macros. The integration point is strace's per-architecture Linux backend under `src/linux/s390`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Risks are numeric table drift against kernel syscall headers, wrong argument count/flags, and mismatched compat table selection; failures appear as wrong syscall names or decoder dispatch. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Compare generated tables with current kernel headers and run decoder lookup tests for representative low, high, compat, and architecture-specific numbers. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/s390/syscallent.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390/syscallent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390/userent.h -->
# sources/test-tools/strace/src/linux/s390/userent.h

## Purpose

This user-area translation table exposes `struct user` register offsets for s390. It uses `XLAT`, `XLAT_UOFF`, or register-size macros so strace can print `PTRACE_PEEKUSER` offsets symbolically. It composes additional generic or compatibility fields through "userent0.h", "userent1.h".

## Important APIs, Types, And Functions

This source is classified as `userent-table` for the `s390` strace backend. It has SHA-1 prefix `cacb85bf0d55`, 42 lines, and 1131 bytes. Key local interface signals: includes "userent0.h", "userent1.h".

## Control Flow

There is no executable control flow. The strace build includes this data into generated lookup arrays; runtime lookup indexes by syscall number, ioctl request, errno, signal, or user offset and then dispatches to generic printers/decoders.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "userent0.h", "userent1.h". The integration point is strace's per-architecture Linux backend under `src/linux/s390`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is architecture ABI drift: these small files encode register names, audit constants, and feature macros that must match kernel and libc headers. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Compare generated tables with current kernel headers and run decoder lookup tests for representative low, high, compat, and architecture-specific numbers. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/s390/userent.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390/userent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390/userent0.h -->
# sources/test-tools/strace/src/linux/s390/userent0.h

## Purpose

This user-area translation table exposes `struct user` register offsets for s390. It uses `XLAT`, `XLAT_UOFF`, or register-size macros so strace can print `PTRACE_PEEKUSER` offsets symbolically.

## Important APIs, Types, And Functions

This source is classified as `userent-table` for the `s390` strace backend. It has SHA-1 prefix `c22580bdf12d`, 48 lines, and 1117 bytes. Key local interface signals: no exported symbols; it is consumed through textual inclusion or generated-table compilation.

## Control Flow

There is no executable control flow. The strace build includes this data into generated lookup arrays; runtime lookup indexes by syscall number, ioctl request, errno, signal, or user offset and then dispatches to generic printers/decoders.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

strace architecture include/build system. The integration point is strace's per-architecture Linux backend under `src/linux/s390`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is architecture ABI drift: these small files encode register names, audit constants, and feature macros that must match kernel and libc headers. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Compare generated tables with current kernel headers and run decoder lookup tests for representative low, high, compat, and architecture-specific numbers. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/s390/userent0.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390/userent0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390/userent1.h -->
# sources/test-tools/strace/src/linux/s390/userent1.h

## Purpose

This user-area translation table exposes `struct user` register offsets for s390. It uses `XLAT`, `XLAT_UOFF`, or register-size macros so strace can print `PTRACE_PEEKUSER` offsets symbolically. It composes additional generic or compatibility fields through "../generic/userent0.h".

## Important APIs, Types, And Functions

This source is classified as `userent-table` for the `s390` strace backend. It has SHA-1 prefix `864e7e69fce1`, 18 lines, and 377 bytes. Key local interface signals: includes "../generic/userent0.h".

## Control Flow

There is no executable control flow. The strace build includes this data into generated lookup arrays; runtime lookup indexes by syscall number, ioctl request, errno, signal, or user offset and then dispatches to generic printers/decoders.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../generic/userent0.h". The integration point is strace's per-architecture Linux backend under `src/linux/s390`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is architecture ABI drift: these small files encode register names, audit constants, and feature macros that must match kernel and libc headers. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Compare generated tables with current kernel headers and run decoder lookup tests for representative low, high, compat, and architecture-specific numbers. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/s390/userent1.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390/userent1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390x/arch_defs_.h -->
# sources/test-tools/strace/src/linux/s390x/arch_defs_.h

## Purpose

This architecture definition header advertises strace compile-time capabilities for the s390x backend: HAVE_ARCH_OLD_MMAP, HAVE_ARCH_OLD_MMAP_PGOFF, HAVE_ARCH_UID16_SYSCALLS, SUPPORTED_PERSONALITIES, PERSONALITY0_AUDIT_ARCH, PERSONALITY1_AUDIT_ARCH. It enables multi-personality decoding, so the same binary can switch between native and compat syscall tables according to audit architecture or runtime register state. The `PERSONALITY*_AUDIT_ARCH` macros are the bridge from seccomp/audit syscall-info records to strace personality selection.

## Important APIs, Types, And Functions

This source is classified as `arch-defs` for the `s390x` strace backend. It has SHA-1 prefix `1fa733de9abd`, 13 lines, and 376 bytes. Key local interface signals: defines HAVE_ARCH_OLD_MMAP, HAVE_ARCH_OLD_MMAP_PGOFF, HAVE_ARCH_UID16_SYSCALLS, SUPPORTED_PERSONALITIES, PERSONALITY0_AUDIT_ARCH, PERSONALITY1_AUDIT_ARCH.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

Linux audit architecture constants. The integration point is strace's per-architecture Linux backend under `src/linux/s390x`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is architecture ABI drift: these small files encode register names, audit constants, and feature macros that must match kernel and libc headers. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/s390x/arch_defs_.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390x/arch_defs_.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390x/arch_get_personality.c -->
# sources/test-tools/strace/src/linux/s390x/arch_get_personality.c

## Purpose

This file implements or selects a s390 64-bit architecture hook for strace. Local functions/macros are get_personality_from_syscall_info. `get_personality_from_syscall_info` maps `PTRACE_GET_SYSCALL_INFO` audit architecture records to the compat personality for bi-ABI tracing.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `s390x` strace backend. It has SHA-1 prefix `8c74c2994bbe`, 13 lines, and 304 bytes. Key local interface signals: functions get_personality_from_syscall_info.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

Linux ptrace regset APIs Linux audit architecture constants. The integration point is strace's per-architecture Linux backend under `src/linux/s390x`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Register selection mistakes produce wrong syscall numbers, arguments, or errno state, which cascades into incorrect decoder selection and misleading traces. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/s390x/arch_get_personality.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390x/arch_get_personality.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390x/arch_prstatus_regset.c -->
# sources/test-tools/strace/src/linux/s390x/arch_prstatus_regset.c

## Purpose

This file is a one-line architecture wrapper that includes "../s390/arch_prstatus_regset.c". It intentionally has no local control flow; the selected include target supplies the real implementation for this personality or endian variant.

## Important APIs, Types, And Functions

This source is classified as `include-wrapper` for the `s390x` strace backend. It has SHA-1 prefix `0bd6cc933c02`, 1 lines, and 42 bytes. Key local interface signals: includes "../s390/arch_prstatus_regset.c".

## Control Flow

At compile time the preprocessor substitutes the referenced implementation or table into this architecture directory. Runtime behavior is therefore the behavior of the included file under this ABI selection.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../s390/arch_prstatus_regset.c". The integration point is strace's per-architecture Linux backend under `src/linux/s390x`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is include-target drift: if the shared file changes assumptions about word size, endian, or personality, this wrapper silently inherits that behavior. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Decode NT_PRSTATUS/pt_regs samples with full, truncated, and oversized sizes to validate graceful printing. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/s390x/arch_prstatus_regset.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390x/arch_prstatus_regset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390x/arch_prstatus_regset.h -->
# sources/test-tools/strace/src/linux/s390x/arch_prstatus_regset.h

## Purpose

This file is a one-line architecture wrapper that includes "../s390/arch_prstatus_regset.h". It intentionally has no local control flow; the selected include target supplies the real implementation for this personality or endian variant.

## Important APIs, Types, And Functions

This source is classified as `include-wrapper` for the `s390x` strace backend. It has SHA-1 prefix `c29b57bb4e7e`, 1 lines, and 42 bytes. Key local interface signals: includes "../s390/arch_prstatus_regset.h".

## Control Flow

At compile time the preprocessor substitutes the referenced implementation or table into this architecture directory. Runtime behavior is therefore the behavior of the included file under this ABI selection.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../s390/arch_prstatus_regset.h". The integration point is strace's per-architecture Linux backend under `src/linux/s390x`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is include-target drift: if the shared file changes assumptions about word size, endian, or personality, this wrapper silently inherits that behavior. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Decode NT_PRSTATUS/pt_regs samples with full, truncated, and oversized sizes to validate graceful printing. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/s390x/arch_prstatus_regset.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390x/arch_prstatus_regset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390x/arch_regs.c -->
# sources/test-tools/strace/src/linux/s390x/arch_regs.c

## Purpose

This file implements or selects a s390 64-bit architecture hook for strace. Local functions/macros are s390_regset, s390x_regset, ARCH_REGS_FOR_GETREGSET, ARCH_IOVEC_FOR_GETREGSET, ARCH_PC_REG, ARCH_SP_REG, ARCH_PERSONALITY_0_IOV_SIZE, ARCH_PERSONALITY_1_IOV_SIZE. The file binds the generic register-fetch path to concrete global register storage plus `ARCH_PC_REG` and `ARCH_SP_REG` macros used by shared code.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `s390x` strace backend. It has SHA-1 prefix `16d46a3bc15a`, 45 lines, and 1090 bytes. Key local interface signals: defines s390_regset, s390x_regset, ARCH_REGS_FOR_GETREGSET, ARCH_IOVEC_FOR_GETREGSET, ARCH_PC_REG, ARCH_SP_REG, ARCH_PERSONALITY_0_IOV_SIZE, ARCH_PERSONALITY_1_IOV_SIZE.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

strace architecture include/build system. The integration point is strace's per-architecture Linux backend under `src/linux/s390x`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is architecture ABI drift: these small files encode register names, audit constants, and feature macros that must match kernel and libc headers. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/s390x/arch_regs.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390x/arch_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390x/arch_sigreturn.c -->
# sources/test-tools/strace/src/linux/s390x/arch_sigreturn.c

## Purpose

This file decodes the architecture-specific sigreturn frame for s390x. It reads frame data from the stack pointer, prints the saved signal mask address or fields, and handles compat structure sizing where present. It reuses shared code through <stdint.h>, "../s390/arch_sigreturn.c", "../s390/arch_sigreturn.c" while redefining size/personality macros around the include where needed.

## Important APIs, Types, And Functions

This source is classified as `sigreturn` for the `s390x` strace backend. It has SHA-1 prefix `3bfd5ff58977`, 29 lines, and 589 bytes. Key local interface signals: includes <stdint.h>, "../s390/arch_sigreturn.c", "../s390/arch_sigreturn.c"; defines PTR_TYPE, arch_sigreturn, SIGNAL_FRAMESIZE, arch_sigreturn; functions arch_sigreturn.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

preprocessor includes: <stdint.h>, "../s390/arch_sigreturn.c", "../s390/arch_sigreturn.c". The integration point is strace's per-architecture Linux backend under `src/linux/s390x`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is architecture ABI drift: these small files encode register names, audit constants, and feature macros that must match kernel and libc headers. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Exercise signal-delivery and sigreturn traces and verify saved mask/frame addresses for native and compat tasks. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/s390x/arch_sigreturn.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390x/arch_sigreturn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390x/check_scno.c -->
# sources/test-tools/strace/src/linux/s390x/check_scno.c

## Purpose

This file is a one-line architecture wrapper that includes "../s390/check_scno.c". It intentionally has no local control flow; the selected include target supplies the real implementation for this personality or endian variant.

## Important APIs, Types, And Functions

This source is classified as `include-wrapper` for the `s390x` strace backend. It has SHA-1 prefix `e0ff6c8caed1`, 1 lines, and 32 bytes. Key local interface signals: includes "../s390/check_scno.c".

## Control Flow

At compile time the preprocessor substitutes the referenced implementation or table into this architecture directory. Runtime behavior is therefore the behavior of the included file under this ABI selection.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../s390/check_scno.c". The integration point is strace's per-architecture Linux backend under `src/linux/s390x`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is include-target drift: if the shared file changes assumptions about word size, endian, or personality, this wrapper silently inherits that behavior. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/s390x/check_scno.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390x/check_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390x/get_error.c -->
# sources/test-tools/strace/src/linux/s390x/get_error.c

## Purpose

This file implements or selects a s390 64-bit architecture hook for strace. Local functions/macros are arch_get_error. `arch_get_error` interprets the architecture error convention and fills `tcp->u_rval`/`tcp->u_error`, using negated errno helpers or condition-code bits as appropriate.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `s390x` strace backend. It has SHA-1 prefix `7fcb29da5801`, 29 lines, and 623 bytes. Key local interface signals: includes "negated_errno.h", "../s390/get_error.c", "../s390/get_error.c"; defines arch_get_error, ARCH_REGSET, arch_get_error, ARCH_REGSET; functions arch_get_error.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

preprocessor includes: "negated_errno.h", "../s390/get_error.c", "../s390/get_error.c" strace `negated_errno.h` helpers. The integration point is strace's per-architecture Linux backend under `src/linux/s390x`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Register selection mistakes produce wrong syscall numbers, arguments, or errno state, which cascades into incorrect decoder selection and misleading traces. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Run syscall-entry/exit tests under ptrace, including failure returns, restart_syscall where applicable, syscall tampering, and compat personality switching. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/s390x/get_error.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390x/get_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390x/get_scno.c -->
# sources/test-tools/strace/src/linux/s390x/get_scno.c

## Purpose

This file implements or selects a s390 64-bit architecture hook for strace. Local functions/macros are arch_get_scno. `arch_get_scno` extracts the syscall number from the architecture syscall-number register or, for s390 restart_syscall, from `NT_S390_SYSTEM_CALL` when the normal register is clobbered by a negated errno.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `s390x` strace backend. It has SHA-1 prefix `3fb0374a3f66`, 27 lines, and 568 bytes. Key local interface signals: includes "../s390/get_scno.c", "../s390/get_scno.c"; defines arch_get_scno, ARCH_REGSET, arch_get_scno, ARCH_REGSET; functions arch_get_scno.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

preprocessor includes: "../s390/get_scno.c", "../s390/get_scno.c". The integration point is strace's per-architecture Linux backend under `src/linux/s390x`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Register selection mistakes produce wrong syscall numbers, arguments, or errno state, which cascades into incorrect decoder selection and misleading traces. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Run syscall-entry/exit tests under ptrace, including failure returns, restart_syscall where applicable, syscall tampering, and compat personality switching. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/s390x/get_scno.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390x/get_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390x/get_syscall_args.c -->
# sources/test-tools/strace/src/linux/s390x/get_syscall_args.c

## Purpose

This file implements or selects a s390 64-bit architecture hook for strace. Local functions/macros are arch_get_syscall_args. `arch_get_syscall_args` copies up to six syscall arguments from ABI-defined argument registers into `tcp->u_arg`; compat paths zero-extend 32-bit register values.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `s390x` strace backend. It has SHA-1 prefix `b7dac68e7bf0`, 28 lines, and 688 bytes. Key local interface signals: includes "../s390/get_syscall_args.c", "../s390/get_syscall_args.c"; defines arch_get_syscall_args, ARCH_REGSET, arch_get_syscall_args, ARCH_REGSET; functions arch_get_syscall_args.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

preprocessor includes: "../s390/get_syscall_args.c", "../s390/get_syscall_args.c". The integration point is strace's per-architecture Linux backend under `src/linux/s390x`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Register selection mistakes produce wrong syscall numbers, arguments, or errno state, which cascades into incorrect decoder selection and misleading traces. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Run syscall-entry/exit tests under ptrace, including failure returns, restart_syscall where applicable, syscall tampering, and compat personality switching. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/s390x/get_syscall_args.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390x/get_syscall_args.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390x/ioctls_arch0.h -->
# sources/test-tools/strace/src/linux/s390x/ioctls_arch0.h

## Purpose

This generated ioctl table records 185 architecture-local ioctl definitions for s390x, with header names, symbolic names, `_IOC_*` direction, request numbers, and encoded argument sizes. Boundary rows include `{ "asm/chsc.h", "CHSC_INFO_CCL", _IOC_READ|_IOC_WRITE, 0x6386, 0x1014 },` and `{ "linux/kvm.h", "KVM_UNREGISTER_COALESCED_MMIO", _IOC_WRITE, 0xae68, 0x10 },`, showing the source header family and final request preserved by generation.

## Important APIs, Types, And Functions

This source is classified as `ioctl-arch-table` for the `s390x` strace backend. It has SHA-1 prefix `4cf6fac7ba96`, 186 lines, and 12702 bytes. Key local interface signals: 185 table rows.

## Control Flow

There is no executable control flow. The strace build includes this data into generated lookup arrays; runtime lookup indexes by syscall number, ioctl request, errno, signal, or user offset and then dispatches to generic printers/decoders.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

Linux ioctl encoding macros and generated `ioctls_gen.sh` output. The integration point is strace's per-architecture Linux backend under `src/linux/s390x`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Risks are stale generated ioctl metadata, request-size mismatches between 32-bit and 64-bit personalities, and duplicate request numbers resolving to the wrong symbolic name. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Compare generated tables with current kernel headers and run decoder lookup tests for representative low, high, compat, and architecture-specific numbers. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/s390x/ioctls_arch0.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390x/ioctls_arch0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390x/ioctls_arch1.h -->
# sources/test-tools/strace/src/linux/s390x/ioctls_arch1.h

## Purpose

This file is a one-line architecture wrapper that includes "../s390/ioctls_arch0.h". It intentionally has no local control flow; the selected include target supplies the real implementation for this personality or endian variant.

## Important APIs, Types, And Functions

This source is classified as `include-wrapper` for the `s390x` strace backend. It has SHA-1 prefix `912c93d89b19`, 1 lines, and 34 bytes. Key local interface signals: includes "../s390/ioctls_arch0.h".

## Control Flow

At compile time the preprocessor substitutes the referenced implementation or table into this architecture directory. Runtime behavior is therefore the behavior of the included file under this ABI selection.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../s390/ioctls_arch0.h". The integration point is strace's per-architecture Linux backend under `src/linux/s390x`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is include-target drift: if the shared file changes assumptions about word size, endian, or personality, this wrapper silently inherits that behavior. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/s390x/ioctls_arch1.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390x/ioctls_arch1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390x/ioctls_inc0.h -->
# sources/test-tools/strace/src/linux/s390x/ioctls_inc0.h

## Purpose

This file is a one-line architecture wrapper that includes "../64/ioctls_inc.h". It intentionally has no local control flow; the selected include target supplies the real implementation for this personality or endian variant.

## Important APIs, Types, And Functions

This source is classified as `include-wrapper` for the `s390x` strace backend. It has SHA-1 prefix `3defd9a34cb2`, 1 lines, and 30 bytes. Key local interface signals: includes "../64/ioctls_inc.h".

## Control Flow

At compile time the preprocessor substitutes the referenced implementation or table into this architecture directory. Runtime behavior is therefore the behavior of the included file under this ABI selection.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../64/ioctls_inc.h". The integration point is strace's per-architecture Linux backend under `src/linux/s390x`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is include-target drift: if the shared file changes assumptions about word size, endian, or personality, this wrapper silently inherits that behavior. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/s390x/ioctls_inc0.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390x/ioctls_inc0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390x/ioctls_inc1.h -->
# sources/test-tools/strace/src/linux/s390x/ioctls_inc1.h

## Purpose

This file is a one-line architecture wrapper that includes "../s390/ioctls_inc0.h". It intentionally has no local control flow; the selected include target supplies the real implementation for this personality or endian variant.

## Important APIs, Types, And Functions

This source is classified as `include-wrapper` for the `s390x` strace backend. It has SHA-1 prefix `20e38f126769`, 1 lines, and 33 bytes. Key local interface signals: includes "../s390/ioctls_inc0.h".

## Control Flow

At compile time the preprocessor substitutes the referenced implementation or table into this architecture directory. Runtime behavior is therefore the behavior of the included file under this ABI selection.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../s390/ioctls_inc0.h". The integration point is strace's per-architecture Linux backend under `src/linux/s390x`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is include-target drift: if the shared file changes assumptions about word size, endian, or personality, this wrapper silently inherits that behavior. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/s390x/ioctls_inc1.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390x/ioctls_inc1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390x/raw_syscall.h -->
# sources/test-tools/strace/src/linux/s390x/raw_syscall.h

## Purpose

This file is a one-line architecture wrapper that includes "../s390/raw_syscall.h". It intentionally has no local control flow; the selected include target supplies the real implementation for this personality or endian variant.

## Important APIs, Types, And Functions

This source is classified as `include-wrapper` for the `s390x` strace backend. It has SHA-1 prefix `054b3c3534cf`, 1 lines, and 33 bytes. Key local interface signals: includes "../s390/raw_syscall.h".

## Control Flow

At compile time the preprocessor substitutes the referenced implementation or table into this architecture directory. Runtime behavior is therefore the behavior of the included file under this ABI selection.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../s390/raw_syscall.h". The integration point is strace's per-architecture Linux backend under `src/linux/s390x`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is include-target drift: if the shared file changes assumptions about word size, endian, or personality, this wrapper silently inherits that behavior. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/s390x/raw_syscall.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390x/raw_syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390x/rt_sigframe.h -->
# sources/test-tools/strace/src/linux/s390x/rt_sigframe.h

## Purpose

This file is a one-line architecture wrapper that includes "../s390/rt_sigframe.h". It intentionally has no local control flow; the selected include target supplies the real implementation for this personality or endian variant.

## Important APIs, Types, And Functions

This source is classified as `include-wrapper` for the `s390x` strace backend. It has SHA-1 prefix `ad71e50cb47b`, 1 lines, and 33 bytes. Key local interface signals: includes "../s390/rt_sigframe.h".

## Control Flow

At compile time the preprocessor substitutes the referenced implementation or table into this architecture directory. Runtime behavior is therefore the behavior of the included file under this ABI selection.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../s390/rt_sigframe.h". The integration point is strace's per-architecture Linux backend under `src/linux/s390x`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is include-target drift: if the shared file changes assumptions about word size, endian, or personality, this wrapper silently inherits that behavior. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Exercise signal-delivery and sigreturn traces and verify saved mask/frame addresses for native and compat tasks. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/s390x/rt_sigframe.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390x/rt_sigframe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390x/set_error.c -->
# sources/test-tools/strace/src/linux/s390x/set_error.c

## Purpose

This file implements or selects a s390 64-bit architecture hook for strace. Local functions/macros are arch_set_error, arch_set_success. The set-error/success hooks mutate the cached register set, update condition-code/error bits when the ABI needs them, and call `set_regs(tcp->pid)` to persist the change into the tracee.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `s390x` strace backend. It has SHA-1 prefix `0824531340b0`, 40 lines, and 837 bytes. Key local interface signals: includes "../s390/set_error.c", "../s390/set_error.c"; defines arch_set_error, arch_set_success, ARCH_REGSET, arch_set_error, arch_set_success, ARCH_REGSET; functions arch_set_error, arch_set_success.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

preprocessor includes: "../s390/set_error.c", "../s390/set_error.c". The integration point is strace's per-architecture Linux backend under `src/linux/s390x`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Register tampering bugs can leave the tracee with inconsistent return values or condition-code bits, so failures are behavioral rather than cosmetic. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Run syscall-entry/exit tests under ptrace, including failure returns, restart_syscall where applicable, syscall tampering, and compat personality switching. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/s390x/set_error.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390x/set_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390x/set_scno.c -->
# sources/test-tools/strace/src/linux/s390x/set_scno.c

## Purpose

This file implements or selects a s390 64-bit architecture hook for strace. Local functions/macros are arch_set_scno.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `s390x` strace backend. It has SHA-1 prefix `f437ef6a9105`, 27 lines, and 580 bytes. Key local interface signals: includes "../s390/set_scno.c", "../s390/set_scno.c"; defines arch_set_scno, ARCH_REGSET, arch_set_scno, ARCH_REGSET; functions arch_set_scno.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

preprocessor includes: "../s390/set_scno.c", "../s390/set_scno.c". The integration point is strace's per-architecture Linux backend under `src/linux/s390x`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Register tampering bugs can leave the tracee with inconsistent return values or condition-code bits, so failures are behavioral rather than cosmetic. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/s390x/set_scno.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390x/set_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390x/syscallent.h -->
# sources/test-tools/strace/src/linux/s390x/syscallent.h

## Purpose

This syscall table maps numeric Linux syscall slots for s390x to strace decoder metadata. It contains about 284 explicit table entries and then composes shared rows through includes such as "syscallent-common.h", "../64/subcallent.h". It defines `SYS_socket_subcall` as 500 before including the socket subcall table, so old multiplexed socket calls occupy the architecture-specific extension range expected by strace. The table starts with entries like `[100] = { 2,	TD|TFSF|TSFA,	SEN(fstatfs),			"fstatfs"		},` and ends with entries like `[402] = { 3,	TI,		SEN(msgctl),			"msgctl"		},`, which is useful when checking generated row order.

## Important APIs, Types, And Functions

This source is classified as `syscall-table` for the `s390x` strace backend. It has SHA-1 prefix `24ac43197527`, 399 lines, and 18940 bytes. Key local interface signals: includes "syscallent-common.h", "../64/subcallent.h"; defines SYS_socket_subcall; 284 table rows.

## Control Flow

There is no executable control flow. The strace build includes this data into generated lookup arrays; runtime lookup indexes by syscall number, ioctl request, errno, signal, or user offset and then dispatches to generic printers/decoders.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "syscallent-common.h", "../64/subcallent.h" Linux ptrace regset APIs strace syscall decoder table macros. The integration point is strace's per-architecture Linux backend under `src/linux/s390x`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Risks are numeric table drift against kernel syscall headers, wrong argument count/flags, and mismatched compat table selection; failures appear as wrong syscall names or decoder dispatch. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Compare generated tables with current kernel headers and run decoder lookup tests for representative low, high, compat, and architecture-specific numbers. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/s390x/syscallent.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390x/syscallent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390x/syscallent1.h -->
# sources/test-tools/strace/src/linux/s390x/syscallent1.h

## Purpose

This file is a one-line architecture wrapper that includes "../s390/syscallent.h". It intentionally has no local control flow; the selected include target supplies the real implementation for this personality or endian variant.

## Important APIs, Types, And Functions

This source is classified as `include-wrapper` for the `s390x` strace backend. It has SHA-1 prefix `11818daba6c5`, 1 lines, and 32 bytes. Key local interface signals: includes "../s390/syscallent.h".

## Control Flow

At compile time the preprocessor substitutes the referenced implementation or table into this architecture directory. Runtime behavior is therefore the behavior of the included file under this ABI selection.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../s390/syscallent.h". The integration point is strace's per-architecture Linux backend under `src/linux/s390x`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is include-target drift: if the shared file changes assumptions about word size, endian, or personality, this wrapper silently inherits that behavior. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/s390x/syscallent1.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390x/syscallent1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390x/userent.h -->
# sources/test-tools/strace/src/linux/s390x/userent.h

## Purpose

This user-area translation table exposes `struct user` register offsets for s390x. It uses `XLAT`, `XLAT_UOFF`, or register-size macros so strace can print `PTRACE_PEEKUSER` offsets symbolically. It composes additional generic or compatibility fields through "../s390/userent0.h", "../s390/userent1.h".

## Important APIs, Types, And Functions

This source is classified as `userent-table` for the `s390x` strace backend. It has SHA-1 prefix `2424f4c9ad79`, 26 lines, and 591 bytes. Key local interface signals: includes "../s390/userent0.h", "../s390/userent1.h".

## Control Flow

There is no executable control flow. The strace build includes this data into generated lookup arrays; runtime lookup indexes by syscall number, ioctl request, errno, signal, or user offset and then dispatches to generic printers/decoders.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../s390/userent0.h", "../s390/userent1.h". The integration point is strace's per-architecture Linux backend under `src/linux/s390x`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is architecture ABI drift: these small files encode register names, audit constants, and feature macros that must match kernel and libc headers. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Compare generated tables with current kernel headers and run decoder lookup tests for representative low, high, compat, and architecture-specific numbers. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/s390x/userent.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390x/userent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sh/arch_defs_.h -->
# sources/test-tools/strace/src/linux/sh/arch_defs_.h

## Purpose

This architecture definition header advertises strace compile-time capabilities for the sh backend: HAVE_ARCH_GETRVAL2, HAVE_ARCH_OLD_SELECT, HAVE_ARCH_UID16_SYSCALLS, PERSONALITY0_AUDIT_ARCH, PERSONALITY0_AUDIT_ARCH. The `PERSONALITY*_AUDIT_ARCH` macros are the bridge from seccomp/audit syscall-info records to strace personality selection.

## Important APIs, Types, And Functions

This source is classified as `arch-defs` for the `sh` strace backend. It has SHA-1 prefix `596849ed586c`, 15 lines, and 372 bytes. Key local interface signals: defines HAVE_ARCH_GETRVAL2, HAVE_ARCH_OLD_SELECT, HAVE_ARCH_UID16_SYSCALLS, PERSONALITY0_AUDIT_ARCH, PERSONALITY0_AUDIT_ARCH.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

Linux audit architecture constants. The integration point is strace's per-architecture Linux backend under `src/linux/sh`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is architecture ABI drift: these small files encode register names, audit constants, and feature macros that must match kernel and libc headers. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sh/arch_defs_.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sh/arch_defs_.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sh/arch_getrval2.c -->
# sources/test-tools/strace/src/linux/sh/arch_getrval2.c

## Purpose

This file implements or selects a SuperH 32-bit architecture hook for strace. Local functions/macros are getrval2. `getrval2` returns the secondary return register used by syscalls that return two values, while reporting `-1` if register fetch failed.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `sh` strace backend. It has SHA-1 prefix `9ceb59af36f7`, 12 lines, and 191 bytes. Key local interface signals: functions getrval2.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

strace architecture include/build system. The integration point is strace's per-architecture Linux backend under `src/linux/sh`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is architecture ABI drift: these small files encode register names, audit constants, and feature macros that must match kernel and libc headers. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sh/arch_getrval2.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sh/arch_getrval2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sh/arch_regs.c -->
# sources/test-tools/strace/src/linux/sh/arch_regs.c

## Purpose

This file implements or selects a SuperH 32-bit architecture hook for strace. Local functions/macros are ARCH_REGS_FOR_GETREGS, ARCH_PC_REG, ARCH_SP_REG. The file binds the generic register-fetch path to concrete global register storage plus `ARCH_PC_REG` and `ARCH_SP_REG` macros used by shared code.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `sh` strace backend. It has SHA-1 prefix `5a5caafec0bf`, 11 lines, and 268 bytes. Key local interface signals: defines ARCH_REGS_FOR_GETREGS, ARCH_PC_REG, ARCH_SP_REG.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

strace architecture include/build system. The integration point is strace's per-architecture Linux backend under `src/linux/sh`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is architecture ABI drift: these small files encode register names, audit constants, and feature macros that must match kernel and libc headers. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sh/arch_regs.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sh/arch_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sh/get_error.c -->
# sources/test-tools/strace/src/linux/sh/get_error.c

## Purpose

This file implements or selects a SuperH 32-bit architecture hook for strace. Local functions/macros are arch_get_error. `arch_get_error` interprets the architecture error convention and fills `tcp->u_rval`/`tcp->u_error`, using negated errno helpers or condition-code bits as appropriate.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `sh` strace backend. It has SHA-1 prefix `887d1034169a`, 19 lines, and 389 bytes. Key local interface signals: includes "negated_errno.h"; functions arch_get_error.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

preprocessor includes: "negated_errno.h" strace `negated_errno.h` helpers. The integration point is strace's per-architecture Linux backend under `src/linux/sh`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Register selection mistakes produce wrong syscall numbers, arguments, or errno state, which cascades into incorrect decoder selection and misleading traces. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Run syscall-entry/exit tests under ptrace, including failure returns, restart_syscall where applicable, syscall tampering, and compat personality switching. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sh/get_error.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sh/get_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sh/get_scno.c -->
# sources/test-tools/strace/src/linux/sh/get_scno.c

## Purpose

This file implements or selects a SuperH 32-bit architecture hook for strace. Local functions/macros are arch_get_scno. `arch_get_scno` extracts the syscall number from the architecture syscall-number register or, for s390 restart_syscall, from `NT_S390_SYSTEM_CALL` when the normal register is clobbered by a negated errno.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `sh` strace backend. It has SHA-1 prefix `cfd5b7f7eb34`, 14 lines, and 273 bytes. Key local interface signals: functions arch_get_scno.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

strace architecture include/build system. The integration point is strace's per-architecture Linux backend under `src/linux/sh`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Register selection mistakes produce wrong syscall numbers, arguments, or errno state, which cascades into incorrect decoder selection and misleading traces. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Run syscall-entry/exit tests under ptrace, including failure returns, restart_syscall where applicable, syscall tampering, and compat personality switching. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sh/get_scno.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sh/get_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sh/get_syscall_args.c -->
# sources/test-tools/strace/src/linux/sh/get_syscall_args.c

## Purpose

This file implements or selects a SuperH 32-bit architecture hook for strace. Local functions/macros are arch_get_syscall_args. `arch_get_syscall_args` copies up to six syscall arguments from ABI-defined argument registers into `tcp->u_arg`; compat paths zero-extend 32-bit register values.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `sh` strace backend. It has SHA-1 prefix `a9d73aff7faa`, 17 lines, and 421 bytes. Key local interface signals: functions arch_get_syscall_args.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

strace architecture include/build system. The integration point is strace's per-architecture Linux backend under `src/linux/sh`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Register selection mistakes produce wrong syscall numbers, arguments, or errno state, which cascades into incorrect decoder selection and misleading traces. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Run syscall-entry/exit tests under ptrace, including failure returns, restart_syscall where applicable, syscall tampering, and compat personality switching. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sh/get_syscall_args.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sh/get_syscall_args.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sh/ioctls_arch0.h -->
# sources/test-tools/strace/src/linux/sh/ioctls_arch0.h

## Purpose

This generated ioctl table records 76 architecture-local ioctl definitions for sh, with header names, symbolic names, `_IOC_*` direction, request numbers, and encoded argument sizes. Boundary rows include `{ "asm/ioctls.h", "FIOASYNC", _IOC_WRITE, 0x667d, 0x04 },` and `{ "mach-landisk/mach/gio.h", "GIODRV_IOCSGIOSETADDR", _IOC_WRITE, 0x6b07, 0x04 },`, showing the source header family and final request preserved by generation.

## Important APIs, Types, And Functions

This source is classified as `ioctl-arch-table` for the `sh` strace backend. It has SHA-1 prefix `08fef056b41e`, 77 lines, and 4643 bytes. Key local interface signals: 76 table rows.

## Control Flow

There is no executable control flow. The strace build includes this data into generated lookup arrays; runtime lookup indexes by syscall number, ioctl request, errno, signal, or user offset and then dispatches to generic printers/decoders.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

Linux ioctl encoding macros and generated `ioctls_gen.sh` output. The integration point is strace's per-architecture Linux backend under `src/linux/sh`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Risks are stale generated ioctl metadata, request-size mismatches between 32-bit and 64-bit personalities, and duplicate request numbers resolving to the wrong symbolic name. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Compare generated tables with current kernel headers and run decoder lookup tests for representative low, high, compat, and architecture-specific numbers. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sh/ioctls_arch0.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sh/ioctls_arch0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sh/ioctls_inc0.h -->
# sources/test-tools/strace/src/linux/sh/ioctls_inc0.h

## Purpose

This file is a one-line architecture wrapper that includes "../32/ioctls_inc.h". It intentionally has no local control flow; the selected include target supplies the real implementation for this personality or endian variant.

## Important APIs, Types, And Functions

This source is classified as `include-wrapper` for the `sh` strace backend. It has SHA-1 prefix `d5c2d9fe71d8`, 1 lines, and 30 bytes. Key local interface signals: includes "../32/ioctls_inc.h".

## Control Flow

At compile time the preprocessor substitutes the referenced implementation or table into this architecture directory. Runtime behavior is therefore the behavior of the included file under this ABI selection.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../32/ioctls_inc.h". The integration point is strace's per-architecture Linux backend under `src/linux/sh`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is include-target drift: if the shared file changes assumptions about word size, endian, or personality, this wrapper silently inherits that behavior. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sh/ioctls_inc0.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sh/ioctls_inc0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sh/raw_syscall.h -->
# sources/test-tools/strace/src/linux/sh/raw_syscall.h

## Purpose

This header defines an inline `raw_syscall_0` helper for sh bootstrap/probing paths. It binds syscall-number and return registers with inline assembly and reports a separate error flag pointer to the generic raw syscall caller. The SuperH implementation issues `trapa #0x10` and includes scheduling NOPs using `or r0,r0` before reading `r0`.

## Important APIs, Types, And Functions

This source is classified as `raw-syscall` for the `sh` strace backend. It has SHA-1 prefix `f06072aac61c`, 34 lines, and 739 bytes. Key local interface signals: includes "kernel_types.h"; defines STRACE_RAW_SYSCALL_H, raw_syscall_0; functions raw_syscall_0.

## Control Flow

Callers pass a syscall number to `raw_syscall_0`; inline assembly loads the ABI syscall register, enters the kernel, records whether an error occurred, and returns the raw result without using libc wrappers.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

preprocessor includes: "kernel_types.h". The integration point is strace's per-architecture Linux backend under `src/linux/sh`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is architecture ABI drift: these small files encode register names, audit constants, and feature macros that must match kernel and libc headers. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Compile and execute raw-syscall smoke tests for a harmless syscall such as getpid or gettid, verifying raw return and error reporting. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sh/raw_syscall.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sh/raw_syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sh/set_error.c -->
# sources/test-tools/strace/src/linux/sh/set_error.c

## Purpose

This file implements or selects a SuperH 32-bit architecture hook for strace. Local functions/macros are arch_set_error, arch_set_success. The set-error/success hooks mutate the cached register set, update condition-code/error bits when the ABI needs them, and call `set_regs(tcp->pid)` to persist the change into the tracee.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `sh` strace backend. It has SHA-1 prefix `1c8cc455c812`, 20 lines, and 350 bytes. Key local interface signals: functions arch_set_error, arch_set_success.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

It mutates the cached architecture register block and persists it into the stopped tracee with `set_regs(tcp->pid)`.

## Dependencies And Integration Points

strace architecture include/build system. The integration point is strace's per-architecture Linux backend under `src/linux/sh`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Register tampering bugs can leave the tracee with inconsistent return values or condition-code bits, so failures are behavioral rather than cosmetic. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Run syscall-entry/exit tests under ptrace, including failure returns, restart_syscall where applicable, syscall tampering, and compat personality switching. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sh/set_error.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sh/set_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sh/set_scno.c -->
# sources/test-tools/strace/src/linux/sh/set_scno.c

## Purpose

This file implements or selects a SuperH 32-bit architecture hook for strace. Local functions/macros are arch_set_scno.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `sh` strace backend. It has SHA-1 prefix `43e66b11e62e`, 15 lines, and 322 bytes. Key local interface signals: functions arch_set_scno.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

It mutates the cached architecture register block and persists it into the stopped tracee with `set_regs(tcp->pid)`.

## Dependencies And Integration Points

Linux ptrace regset APIs. The integration point is strace's per-architecture Linux backend under `src/linux/sh`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Register tampering bugs can leave the tracee with inconsistent return values or condition-code bits, so failures are behavioral rather than cosmetic. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sh/set_scno.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sh/set_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sh/syscallent.h -->
# sources/test-tools/strace/src/linux/sh/syscallent.h

## Purpose

This syscall table maps numeric Linux syscall slots for sh to strace decoder metadata. It contains about 292 explicit table entries and then composes shared rows through includes such as "../32/syscallent-common-32.h", "syscallent-common.h", "../32/subcallent.h". It defines `SYS_socket_subcall` as 500 before including the socket subcall table, so old multiplexed socket calls occupy the architecture-specific extension range expected by strace. The table starts with entries like `[100] = { 2,	TD|TFSF|TSFA,	SEN(fstatfs),			"fstatfs"		},` and ends with entries like `[402] = { 3,	TI,		SEN(msgctl),			"msgctl"		},`, which is useful when checking generated row order.

## Important APIs, Types, And Functions

This source is classified as `syscall-table` for the `sh` strace backend. It has SHA-1 prefix `d58fe8d01bc4`, 412 lines, and 20770 bytes. Key local interface signals: includes "../32/syscallent-common-32.h", "syscallent-common.h", "../32/subcallent.h"; defines SYS_socket_subcall; 292 table rows.

## Control Flow

There is no executable control flow. The strace build includes this data into generated lookup arrays; runtime lookup indexes by syscall number, ioctl request, errno, signal, or user offset and then dispatches to generic printers/decoders.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../32/syscallent-common-32.h", "syscallent-common.h", "../32/subcallent.h" Linux ptrace regset APIs strace syscall decoder table macros. The integration point is strace's per-architecture Linux backend under `src/linux/sh`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Risks are numeric table drift against kernel syscall headers, wrong argument count/flags, and mismatched compat table selection; failures appear as wrong syscall names or decoder dispatch. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Compare generated tables with current kernel headers and run decoder lookup tests for representative low, high, compat, and architecture-specific numbers. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sh/syscallent.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sh/syscallent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sh/userent.h -->
# sources/test-tools/strace/src/linux/sh/userent.h

## Purpose

This user-area translation table exposes `struct user` register offsets for sh. It uses `XLAT`, `XLAT_UOFF`, or register-size macros so strace can print `PTRACE_PEEKUSER` offsets symbolically. It composes additional generic or compatibility fields through "userent0.h".

## Important APIs, Types, And Functions

This source is classified as `userent-table` for the `sh` strace backend. It has SHA-1 prefix `a17eb35541ad`, 60 lines, and 1752 bytes. Key local interface signals: includes "userent0.h".

## Control Flow

There is no executable control flow. The strace build includes this data into generated lookup arrays; runtime lookup indexes by syscall number, ioctl request, errno, signal, or user offset and then dispatches to generic printers/decoders.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "userent0.h". The integration point is strace's per-architecture Linux backend under `src/linux/sh`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is architecture ABI drift: these small files encode register names, audit constants, and feature macros that must match kernel and libc headers. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Compare generated tables with current kernel headers and run decoder lookup tests for representative low, high, compat, and architecture-specific numbers. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sh/userent.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sh/userent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sh/userent0.h -->
# sources/test-tools/strace/src/linux/sh/userent0.h

## Purpose

This user-area translation table exposes `struct user` register offsets for sh. It uses `XLAT`, `XLAT_UOFF`, or register-size macros so strace can print `PTRACE_PEEKUSER` offsets symbolically. It composes additional generic or compatibility fields through "../generic/userent0.h".

## Important APIs, Types, And Functions

This source is classified as `userent-table` for the `sh` strace backend. It has SHA-1 prefix `088698fce46f`, 20 lines, and 412 bytes. Key local interface signals: includes "../generic/userent0.h".

## Control Flow

There is no executable control flow. The strace build includes this data into generated lookup arrays; runtime lookup indexes by syscall number, ioctl request, errno, signal, or user offset and then dispatches to generic printers/decoders.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../generic/userent0.h". The integration point is strace's per-architecture Linux backend under `src/linux/sh`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is architecture ABI drift: these small files encode register names, audit constants, and feature macros that must match kernel and libc headers. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Compare generated tables with current kernel headers and run decoder lookup tests for representative low, high, compat, and architecture-specific numbers. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sh/userent0.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sh/userent0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sh64/arch_defs_.h -->
# sources/test-tools/strace/src/linux/sh64/arch_defs_.h

## Purpose

This architecture definition header advertises strace compile-time capabilities for the sh64 backend: HAVE_ARCH_UID16_SYSCALLS, PERSONALITY0_AUDIT_ARCH, PERSONALITY0_AUDIT_ARCH. The `PERSONALITY*_AUDIT_ARCH` macros are the bridge from seccomp/audit syscall-info records to strace personality selection.

## Important APIs, Types, And Functions

This source is classified as `arch-defs` for the `sh64` strace backend. It has SHA-1 prefix `b871995afcbc`, 13 lines, and 316 bytes. Key local interface signals: defines HAVE_ARCH_UID16_SYSCALLS, PERSONALITY0_AUDIT_ARCH, PERSONALITY0_AUDIT_ARCH.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

Linux audit architecture constants. The integration point is strace's per-architecture Linux backend under `src/linux/sh64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is architecture ABI drift: these small files encode register names, audit constants, and feature macros that must match kernel and libc headers. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sh64/arch_defs_.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sh64/arch_defs_.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sh64/arch_regs.c -->
# sources/test-tools/strace/src/linux/sh64/arch_regs.c

## Purpose

This file implements or selects a SuperH 64-bit architecture hook for strace. Local functions/macros are ARCH_REGS_FOR_GETREGS, ARCH_PC_REG, ARCH_SP_REG. The file binds the generic register-fetch path to concrete global register storage plus `ARCH_PC_REG` and `ARCH_SP_REG` macros used by shared code.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `sh64` strace backend. It has SHA-1 prefix `1d413c7e2708`, 11 lines, and 276 bytes. Key local interface signals: defines ARCH_REGS_FOR_GETREGS, ARCH_PC_REG, ARCH_SP_REG.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

strace architecture include/build system. The integration point is strace's per-architecture Linux backend under `src/linux/sh64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is architecture ABI drift: these small files encode register names, audit constants, and feature macros that must match kernel and libc headers. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sh64/arch_regs.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sh64/arch_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sh64/get_error.c -->
# sources/test-tools/strace/src/linux/sh64/get_error.c

## Purpose

This file implements or selects a SuperH 64-bit architecture hook for strace. Local functions/macros are arch_get_error. `arch_get_error` interprets the architecture error convention and fills `tcp->u_rval`/`tcp->u_error`, using negated errno helpers or condition-code bits as appropriate.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `sh64` strace backend. It has SHA-1 prefix `428b426ef9d6`, 19 lines, and 395 bytes. Key local interface signals: includes "negated_errno.h"; functions arch_get_error.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

preprocessor includes: "negated_errno.h" strace `negated_errno.h` helpers. The integration point is strace's per-architecture Linux backend under `src/linux/sh64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Register selection mistakes produce wrong syscall numbers, arguments, or errno state, which cascades into incorrect decoder selection and misleading traces. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Run syscall-entry/exit tests under ptrace, including failure returns, restart_syscall where applicable, syscall tampering, and compat personality switching. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sh64/get_error.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sh64/get_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sh64/get_scno.c -->
# sources/test-tools/strace/src/linux/sh64/get_scno.c

## Purpose

This file implements or selects a SuperH 64-bit architecture hook for strace. Local functions/macros are arch_get_scno. `arch_get_scno` extracts the syscall number from the architecture syscall-number register or, for s390 restart_syscall, from `NT_S390_SYSTEM_CALL` when the normal register is clobbered by a negated errno.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `sh64` strace backend. It has SHA-1 prefix `e1b40e4f6d30`, 14 lines, and 275 bytes. Key local interface signals: functions arch_get_scno.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

strace architecture include/build system. The integration point is strace's per-architecture Linux backend under `src/linux/sh64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Register selection mistakes produce wrong syscall numbers, arguments, or errno state, which cascades into incorrect decoder selection and misleading traces. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Run syscall-entry/exit tests under ptrace, including failure returns, restart_syscall where applicable, syscall tampering, and compat personality switching. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sh64/get_scno.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sh64/get_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sh64/get_syscall_args.c -->
# sources/test-tools/strace/src/linux/sh64/get_syscall_args.c

## Purpose

This file implements or selects a SuperH 64-bit architecture hook for strace. Local functions/macros are arch_get_syscall_args. `arch_get_syscall_args` copies up to six syscall arguments from ABI-defined argument registers into `tcp->u_arg`; compat paths zero-extend 32-bit register values.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `sh64` strace backend. It has SHA-1 prefix `172b862db75d`, 15 lines, and 338 bytes. Key local interface signals: functions arch_get_syscall_args.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

strace architecture include/build system. The integration point is strace's per-architecture Linux backend under `src/linux/sh64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Register selection mistakes produce wrong syscall numbers, arguments, or errno state, which cascades into incorrect decoder selection and misleading traces. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Run syscall-entry/exit tests under ptrace, including failure returns, restart_syscall where applicable, syscall tampering, and compat personality switching. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sh64/get_syscall_args.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sh64/get_syscall_args.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sh64/ioctls_arch0.h -->
# sources/test-tools/strace/src/linux/sh64/ioctls_arch0.h

## Purpose

This generated ioctl table records 76 architecture-local ioctl definitions for sh64, with header names, symbolic names, `_IOC_*` direction, request numbers, and encoded argument sizes. Boundary rows include `{ "asm/ioctls.h", "FIOASYNC", _IOC_WRITE, 0x667d, 0x04 },` and `{ "mach-landisk/mach/gio.h", "GIODRV_IOCSGIOSETADDR", _IOC_WRITE, 0x6b07, 0x08 },`, showing the source header family and final request preserved by generation.

## Important APIs, Types, And Functions

This source is classified as `ioctl-arch-table` for the `sh64` strace backend. It has SHA-1 prefix `834f0ee6c9d0`, 77 lines, and 4643 bytes. Key local interface signals: 76 table rows.

## Control Flow

There is no executable control flow. The strace build includes this data into generated lookup arrays; runtime lookup indexes by syscall number, ioctl request, errno, signal, or user offset and then dispatches to generic printers/decoders.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

Linux ioctl encoding macros and generated `ioctls_gen.sh` output. The integration point is strace's per-architecture Linux backend under `src/linux/sh64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Risks are stale generated ioctl metadata, request-size mismatches between 32-bit and 64-bit personalities, and duplicate request numbers resolving to the wrong symbolic name. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Compare generated tables with current kernel headers and run decoder lookup tests for representative low, high, compat, and architecture-specific numbers. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sh64/ioctls_arch0.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sh64/ioctls_arch0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sh64/ioctls_inc0.h -->
# sources/test-tools/strace/src/linux/sh64/ioctls_inc0.h

## Purpose

This file is a one-line architecture wrapper that includes "../64/ioctls_inc.h". It intentionally has no local control flow; the selected include target supplies the real implementation for this personality or endian variant.

## Important APIs, Types, And Functions

This source is classified as `include-wrapper` for the `sh64` strace backend. It has SHA-1 prefix `3defd9a34cb2`, 1 lines, and 30 bytes. Key local interface signals: includes "../64/ioctls_inc.h".

## Control Flow

At compile time the preprocessor substitutes the referenced implementation or table into this architecture directory. Runtime behavior is therefore the behavior of the included file under this ABI selection.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../64/ioctls_inc.h". The integration point is strace's per-architecture Linux backend under `src/linux/sh64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is include-target drift: if the shared file changes assumptions about word size, endian, or personality, this wrapper silently inherits that behavior. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sh64/ioctls_inc0.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sh64/ioctls_inc0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sh64/raw_syscall.h -->
# sources/test-tools/strace/src/linux/sh64/raw_syscall.h

## Purpose

This file is a one-line architecture wrapper that includes "../sh/raw_syscall.h". It intentionally has no local control flow; the selected include target supplies the real implementation for this personality or endian variant.

## Important APIs, Types, And Functions

This source is classified as `include-wrapper` for the `sh64` strace backend. It has SHA-1 prefix `ca17712d2c18`, 1 lines, and 31 bytes. Key local interface signals: includes "../sh/raw_syscall.h".

## Control Flow

At compile time the preprocessor substitutes the referenced implementation or table into this architecture directory. Runtime behavior is therefore the behavior of the included file under this ABI selection.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../sh/raw_syscall.h". The integration point is strace's per-architecture Linux backend under `src/linux/sh64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is include-target drift: if the shared file changes assumptions about word size, endian, or personality, this wrapper silently inherits that behavior. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sh64/raw_syscall.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sh64/raw_syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sh64/rt_sigframe.h -->
# sources/test-tools/strace/src/linux/sh64/rt_sigframe.h

## Purpose

This header models the user-space realtime signal frame layout for sh64, including `ucontext`, `siginfo`, or mask offsets needed by strace signal-frame decoding.

## Important APIs, Types, And Functions

This source is classified as `rt-sigframe` for the `sh64` strace backend. It has SHA-1 prefix `55082e239cf9`, 21 lines, and 387 bytes. Key local interface signals: includes <signal.h>; defines STRACE_RT_SIGFRAME_H.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

preprocessor includes: <signal.h>. The integration point is strace's per-architecture Linux backend under `src/linux/sh64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Structure layout drift or alignment mistakes can over/under-print register fields; the code mitigates this with size checks but depends on exact ABI offsets. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Exercise signal-delivery and sigreturn traces and verify saved mask/frame addresses for native and compat tasks. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sh64/rt_sigframe.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sh64/rt_sigframe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sh64/set_error.c -->
# sources/test-tools/strace/src/linux/sh64/set_error.c

## Purpose

This file implements or selects a SuperH 64-bit architecture hook for strace. Local functions/macros are arch_set_error, arch_set_success. The set-error/success hooks mutate the cached register set, update condition-code/error bits when the ABI needs them, and call `set_regs(tcp->pid)` to persist the change into the tracee.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `sh64` strace backend. It has SHA-1 prefix `6f236ef0b5a1`, 20 lines, and 354 bytes. Key local interface signals: functions arch_set_error, arch_set_success.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

It mutates the cached architecture register block and persists it into the stopped tracee with `set_regs(tcp->pid)`.

## Dependencies And Integration Points

strace architecture include/build system. The integration point is strace's per-architecture Linux backend under `src/linux/sh64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Register tampering bugs can leave the tracee with inconsistent return values or condition-code bits, so failures are behavioral rather than cosmetic. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Run syscall-entry/exit tests under ptrace, including failure returns, restart_syscall where applicable, syscall tampering, and compat personality switching. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sh64/set_error.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sh64/set_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sh64/set_scno.c -->
# sources/test-tools/strace/src/linux/sh64/set_scno.c

## Purpose

This file implements or selects a SuperH 64-bit architecture hook for strace. Local functions/macros are arch_set_scno.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `sh64` strace backend. It has SHA-1 prefix `33473bec9e12`, 15 lines, and 324 bytes. Key local interface signals: functions arch_set_scno.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

It mutates the cached architecture register block and persists it into the stopped tracee with `set_regs(tcp->pid)`.

## Dependencies And Integration Points

Linux ptrace regset APIs. The integration point is strace's per-architecture Linux backend under `src/linux/sh64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Register tampering bugs can leave the tracee with inconsistent return values or condition-code bits, so failures are behavioral rather than cosmetic. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sh64/set_scno.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sh64/set_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sh64/syscallent.h -->
# sources/test-tools/strace/src/linux/sh64/syscallent.h

## Purpose

This syscall table maps numeric Linux syscall slots for sh64 to strace decoder metadata. It contains about 288 explicit table entries and then composes shared rows through includes such as "syscallent-common.h", "../64/subcallent.h". It defines `SYS_socket_subcall` as 500 before including the socket subcall table, so old multiplexed socket calls occupy the architecture-specific extension range expected by strace. The table starts with entries like `[100] = { 2,	TD|TFSF|TSFA,	SEN(fstatfs),			"fstatfs"		},` and ends with entries like `[393] = { 6,	TD,		SEN(pwritev2),			"pwritev2"		},`, which is useful when checking generated row order.

## Important APIs, Types, And Functions

This source is classified as `syscall-table` for the `sh64` strace backend. It has SHA-1 prefix `5a4dff1da5bd`, 405 lines, and 20306 bytes. Key local interface signals: includes "syscallent-common.h", "../64/subcallent.h"; defines SYS_socket_subcall; 288 table rows.

## Control Flow

There is no executable control flow. The strace build includes this data into generated lookup arrays; runtime lookup indexes by syscall number, ioctl request, errno, signal, or user offset and then dispatches to generic printers/decoders.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "syscallent-common.h", "../64/subcallent.h" Linux ptrace regset APIs strace syscall decoder table macros. The integration point is strace's per-architecture Linux backend under `src/linux/sh64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Risks are numeric table drift against kernel syscall headers, wrong argument count/flags, and mismatched compat table selection; failures appear as wrong syscall names or decoder dispatch. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Compare generated tables with current kernel headers and run decoder lookup tests for representative low, high, compat, and architecture-specific numbers. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sh64/syscallent.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sh64/syscallent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sh64/userent.h -->
# sources/test-tools/strace/src/linux/sh64/userent.h

## Purpose

This user-area translation table exposes `struct user` register offsets for sh64. It uses `XLAT`, `XLAT_UOFF`, or register-size macros so strace can print `PTRACE_PEEKUSER` offsets symbolically. It composes additional generic or compatibility fields through "../sh/userent0.h".

## Important APIs, Types, And Functions

This source is classified as `userent-table` for the `sh64` strace backend. It has SHA-1 prefix `e17145b52892`, 161 lines, and 3390 bytes. Key local interface signals: includes "../sh/userent0.h".

## Control Flow

There is no executable control flow. The strace build includes this data into generated lookup arrays; runtime lookup indexes by syscall number, ioctl request, errno, signal, or user offset and then dispatches to generic printers/decoders.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../sh/userent0.h". The integration point is strace's per-architecture Linux backend under `src/linux/sh64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is architecture ABI drift: these small files encode register names, audit constants, and feature macros that must match kernel and libc headers. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Compare generated tables with current kernel headers and run decoder lookup tests for representative low, high, compat, and architecture-specific numbers. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sh64/userent.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sh64/userent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc/arch_defs_.h -->
# sources/test-tools/strace/src/linux/sparc/arch_defs_.h

## Purpose

This architecture definition header advertises strace compile-time capabilities for the sparc backend: ARCH_SIZEOF_STRUCT_MSQID64_DS, HAVE_ARCH_GETRVAL2, HAVE_ARCH_UID16_SYSCALLS, HAVE_ARCH_SA_RESTORER, HAVE_ARCH_DEDICATED_ERR_REG, CAN_ARCH_BE_COMPAT_ON_64BIT_KERNEL, PERSONALITY0_AUDIT_ARCH. The `PERSONALITY*_AUDIT_ARCH` macros are the bridge from seccomp/audit syscall-info records to strace personality selection.

## Important APIs, Types, And Functions

This source is classified as `arch-defs` for the `sparc` strace backend. It has SHA-1 prefix `1b46dadd1e02`, 14 lines, and 408 bytes. Key local interface signals: defines ARCH_SIZEOF_STRUCT_MSQID64_DS, HAVE_ARCH_GETRVAL2, HAVE_ARCH_UID16_SYSCALLS, HAVE_ARCH_SA_RESTORER, HAVE_ARCH_DEDICATED_ERR_REG, CAN_ARCH_BE_COMPAT_ON_64BIT_KERNEL, PERSONALITY0_AUDIT_ARCH.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

Linux audit architecture constants. The integration point is strace's per-architecture Linux backend under `src/linux/sparc`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is architecture ABI drift: these small files encode register names, audit constants, and feature macros that must match kernel and libc headers. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sparc/arch_defs_.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc/arch_defs_.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc/arch_getrval2.c -->
# sources/test-tools/strace/src/linux/sparc/arch_getrval2.c

## Purpose

This file implements or selects a SPARC 32-bit architecture hook for strace. Local functions/macros are getrval2. `getrval2` returns the secondary return register used by syscalls that return two values, while reporting `-1` if register fetch failed.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `sparc` strace backend. It has SHA-1 prefix `01bcad55b449`, 14 lines, and 274 bytes. Key local interface signals: functions getrval2.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

Linux ptrace regset APIs. The integration point is strace's per-architecture Linux backend under `src/linux/sparc`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is architecture ABI drift: these small files encode register names, audit constants, and feature macros that must match kernel and libc headers. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sparc/arch_getrval2.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc/arch_getrval2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc/arch_prstatus_regset.c -->
# sources/test-tools/strace/src/linux/sparc/arch_prstatus_regset.c

## Purpose

This decoder prints NT_PRSTATUS register-set payloads for sparc. It bounds reads to `MIN(sizeof(regs), size)`, rejects misaligned or zero sizes, and prints only fields present in the fetched prefix. When the kernel supplies a larger blob than the known structure, it emits a more-data marker instead of over-reading unknown layout.

## Important APIs, Types, And Functions

This source is classified as `prstatus-regset` for the `sparc` strace backend. It has SHA-1 prefix `74c0a8cabb4f`, 74 lines, and 2140 bytes. Key local interface signals: functions arch_decode_prstatus_regset.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

strace structured printing macros tracee-memory readers. The integration point is strace's per-architecture Linux backend under `src/linux/sparc`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Structure layout drift or alignment mistakes can over/under-print register fields; the code mitigates this with size checks but depends on exact ABI offsets. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Decode NT_PRSTATUS/pt_regs samples with full, truncated, and oversized sizes to validate graceful printing. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sparc/arch_prstatus_regset.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc/arch_prstatus_regset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc/arch_prstatus_regset.h -->
# sources/test-tools/strace/src/linux/sparc/arch_prstatus_regset.h

## Purpose

This header defines the type alias used to decode NT_PRSTATUS register-set payloads for sparc and sets `HAVE_ARCH_PRSTATUS_REGSET`.

## Important APIs, Types, And Functions

This source is classified as `prstatus-regset` for the `sparc` strace backend. It has SHA-1 prefix `4c8b4d2cfa42`, 26 lines, and 521 bytes. Key local interface signals: defines STRACE_ARCH_PRSTATUS_REGSET_H, HAVE_ARCH_PRSTATUS_REGSET.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

strace architecture include/build system. The integration point is strace's per-architecture Linux backend under `src/linux/sparc`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Structure layout drift or alignment mistakes can over/under-print register fields; the code mitigates this with size checks but depends on exact ABI offsets. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Decode NT_PRSTATUS/pt_regs samples with full, truncated, and oversized sizes to validate graceful printing. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sparc/arch_prstatus_regset.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc/arch_prstatus_regset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc/arch_pt_regs.c -->
# sources/test-tools/strace/src/linux/sparc/arch_pt_regs.c

## Purpose

This file implements or selects a SPARC 32-bit architecture hook for strace. Local functions/macros are arch_decode_pt_regs. The pt_regs decoder prints kernel `struct pt_regs` fields for ptrace or signal-frame contexts, with compat guards on bi-ABI targets.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `sparc` strace backend. It has SHA-1 prefix `93452eba6b5c`, 38 lines, and 702 bytes. Key local interface signals: functions arch_decode_pt_regs.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

strace structured printing macros. The integration point is strace's per-architecture Linux backend under `src/linux/sparc`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Structure layout drift or alignment mistakes can over/under-print register fields; the code mitigates this with size checks but depends on exact ABI offsets. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Decode NT_PRSTATUS/pt_regs samples with full, truncated, and oversized sizes to validate graceful printing. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sparc/arch_pt_regs.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc/arch_pt_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc/arch_regs.c -->
# sources/test-tools/strace/src/linux/sparc/arch_regs.c

## Purpose

This file implements or selects a SPARC 32-bit architecture hook for strace. Local functions/macros are U_REG_G1, U_REG_O0, U_REG_O1, U_REG_FP, ARCH_REGS_FOR_GETREGS, ARCH_PC_REG, ARCH_SP_REG. The file binds the generic register-fetch path to concrete global register storage plus `ARCH_PC_REG` and `ARCH_SP_REG` macros used by shared code.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `sparc` strace backend. It has SHA-1 prefix `d9cb24a431fe`, 19 lines, and 523 bytes. Key local interface signals: defines U_REG_G1, U_REG_O0, U_REG_O1, U_REG_FP, ARCH_REGS_FOR_GETREGS, ARCH_PC_REG, ARCH_SP_REG.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

strace architecture include/build system. The integration point is strace's per-architecture Linux backend under `src/linux/sparc`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is architecture ABI drift: these small files encode register names, audit constants, and feature macros that must match kernel and libc headers. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sparc/arch_regs.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc/arch_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc/arch_sigreturn.c -->
# sources/test-tools/strace/src/linux/sparc/arch_sigreturn.c

## Purpose

This file decodes the architecture-specific sigreturn frame for sparc. It reads frame data from the stack pointer, prints the saved signal mask address or fields, and handles compat structure sizing where present.

## Important APIs, Types, And Functions

This source is classified as `sigreturn` for the `sparc` strace backend. It has SHA-1 prefix `820c32bd223c`, 43 lines, and 1099 bytes. Key local interface signals: defines SIZEOF_STRUCT_SPARC_STACKF, SIZEOF_STRUCT_PT_REGS, PERSONALITY_WORDSIZE; functions arch_sigreturn.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

strace architecture include/build system. The integration point is strace's per-architecture Linux backend under `src/linux/sparc`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is architecture ABI drift: these small files encode register names, audit constants, and feature macros that must match kernel and libc headers. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Exercise signal-delivery and sigreturn traces and verify saved mask/frame addresses for native and compat tasks. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sparc/arch_sigreturn.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc/arch_sigreturn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc/errnoent.h -->
# sources/test-tools/strace/src/linux/sparc/errnoent.h

## Purpose

This file supplies 53 SPARC-specific errno name slots, including high-numbered Linux/SPARC errors, for strace errno decoding.

## Important APIs, Types, And Functions

This source is classified as `errno-table` for the `sparc` strace backend. It has SHA-1 prefix `c858c732f49f`, 159 lines, and 3159 bytes. Key local interface signals: 53 table rows.

## Control Flow

There is no executable control flow. The strace build includes this data into generated lookup arrays; runtime lookup indexes by syscall number, ioctl request, errno, signal, or user offset and then dispatches to generic printers/decoders.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

strace architecture include/build system. The integration point is strace's per-architecture Linux backend under `src/linux/sparc`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is architecture ABI drift: these small files encode register names, audit constants, and feature macros that must match kernel and libc headers. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Compare generated tables with current kernel headers and run decoder lookup tests for representative low, high, compat, and architecture-specific numbers. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sparc/errnoent.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc/errnoent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc/get_error.c -->
# sources/test-tools/strace/src/linux/sparc/get_error.c

## Purpose

This file implements or selects a SPARC 32-bit architecture hook for strace. Local functions/macros are arch_get_error. `arch_get_error` interprets the architecture error convention and fills `tcp->u_rval`/`tcp->u_error`, using negated errno helpers or condition-code bits as appropriate.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `sparc` strace backend. It has SHA-1 prefix `e7486e865871`, 19 lines, and 380 bytes. Key local interface signals: includes <asm/psr.h>; functions arch_get_error.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

preprocessor includes: <asm/psr.h>. The integration point is strace's per-architecture Linux backend under `src/linux/sparc`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Register selection mistakes produce wrong syscall numbers, arguments, or errno state, which cascades into incorrect decoder selection and misleading traces. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Run syscall-entry/exit tests under ptrace, including failure returns, restart_syscall where applicable, syscall tampering, and compat personality switching. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sparc/get_error.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc/get_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc/get_scno.c -->
# sources/test-tools/strace/src/linux/sparc/get_scno.c

## Purpose

This file implements or selects a SPARC 32-bit architecture hook for strace. Local functions/macros are arch_get_scno. `arch_get_scno` extracts the syscall number from the architecture syscall-number register or, for s390 restart_syscall, from `NT_S390_SYSTEM_CALL` when the normal register is clobbered by a negated errno.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `sparc` strace backend. It has SHA-1 prefix `e9586671589c`, 14 lines, and 285 bytes. Key local interface signals: functions arch_get_scno.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

strace architecture include/build system. The integration point is strace's per-architecture Linux backend under `src/linux/sparc`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Register selection mistakes produce wrong syscall numbers, arguments, or errno state, which cascades into incorrect decoder selection and misleading traces. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Run syscall-entry/exit tests under ptrace, including failure returns, restart_syscall where applicable, syscall tampering, and compat personality switching. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sparc/get_scno.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc/get_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc/get_syscall_args.c -->
# sources/test-tools/strace/src/linux/sparc/get_syscall_args.c

## Purpose

This file implements or selects a SPARC 32-bit architecture hook for strace. Local functions/macros are arch_get_syscall_args. `arch_get_syscall_args` copies up to six syscall arguments from ABI-defined argument registers into `tcp->u_arg`; compat paths zero-extend 32-bit register values.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `sparc` strace backend. It has SHA-1 prefix `bdb2e88094f1`, 19 lines, and 549 bytes. Key local interface signals: functions arch_get_syscall_args.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

strace architecture include/build system. The integration point is strace's per-architecture Linux backend under `src/linux/sparc`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Register selection mistakes produce wrong syscall numbers, arguments, or errno state, which cascades into incorrect decoder selection and misleading traces. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Run syscall-entry/exit tests under ptrace, including failure returns, restart_syscall where applicable, syscall tampering, and compat personality switching. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sparc/get_syscall_args.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc/get_syscall_args.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc/ioctls_arch0.h -->
# sources/test-tools/strace/src/linux/sparc/ioctls_arch0.h

## Purpose

This generated ioctl table records 121 architecture-local ioctl definitions for sparc, with header names, symbolic names, `_IOC_*` direction, request numbers, and encoded argument sizes. Boundary rows include `{ "asm/apc.h", "APCIOCGBPORT", _IOC_READ, 0x4104, 0x04 },` and `{ "asm/watchdog.h", "WIOCSTOP", _IOC_NONE, 0x570b, 0x00 },`, showing the source header family and final request preserved by generation.

## Important APIs, Types, And Functions

This source is classified as `ioctl-arch-table` for the `sparc` strace backend. It has SHA-1 prefix `ea76bd7d2849`, 122 lines, and 7326 bytes. Key local interface signals: 121 table rows.

## Control Flow

There is no executable control flow. The strace build includes this data into generated lookup arrays; runtime lookup indexes by syscall number, ioctl request, errno, signal, or user offset and then dispatches to generic printers/decoders.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

Linux ioctl encoding macros and generated `ioctls_gen.sh` output. The integration point is strace's per-architecture Linux backend under `src/linux/sparc`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Risks are stale generated ioctl metadata, request-size mismatches between 32-bit and 64-bit personalities, and duplicate request numbers resolving to the wrong symbolic name. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Compare generated tables with current kernel headers and run decoder lookup tests for representative low, high, compat, and architecture-specific numbers. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sparc/ioctls_arch0.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc/ioctls_arch0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc/ioctls_inc0.h -->
# sources/test-tools/strace/src/linux/sparc/ioctls_inc0.h

## Purpose

This file is a one-line architecture wrapper that includes "../32/ioctls_inc.h". It intentionally has no local control flow; the selected include target supplies the real implementation for this personality or endian variant.

## Important APIs, Types, And Functions

This source is classified as `include-wrapper` for the `sparc` strace backend. It has SHA-1 prefix `d5c2d9fe71d8`, 1 lines, and 30 bytes. Key local interface signals: includes "../32/ioctls_inc.h".

## Control Flow

At compile time the preprocessor substitutes the referenced implementation or table into this architecture directory. Runtime behavior is therefore the behavior of the included file under this ABI selection.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../32/ioctls_inc.h". The integration point is strace's per-architecture Linux backend under `src/linux/sparc`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is include-target drift: if the shared file changes assumptions about word size, endian, or personality, this wrapper silently inherits that behavior. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sparc/ioctls_inc0.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc/ioctls_inc0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc/raw_syscall.h -->
# sources/test-tools/strace/src/linux/sparc/raw_syscall.h

## Purpose

This header defines an inline `raw_syscall_0` helper for sparc bootstrap/probing paths. It binds syscall-number and return registers with inline assembly and reports a separate error flag pointer to the generic raw syscall caller. The SPARC implementation uses trap instructions and condition-code handling to distinguish success from syscall errors.

## Important APIs, Types, And Functions

This source is classified as `raw-syscall` for the `sparc` strace backend. It has SHA-1 prefix `4ec99e077cce`, 38 lines, and 974 bytes. Key local interface signals: includes "kernel_types.h"; defines STRACE_RAW_SYSCALL_H, raw_syscall_0; functions raw_syscall_0.

## Control Flow

Callers pass a syscall number to `raw_syscall_0`; inline assembly loads the ABI syscall register, enters the kernel, records whether an error occurred, and returns the raw result without using libc wrappers.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

preprocessor includes: "kernel_types.h". The integration point is strace's per-architecture Linux backend under `src/linux/sparc`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is architecture ABI drift: these small files encode register names, audit constants, and feature macros that must match kernel and libc headers. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Compile and execute raw-syscall smoke tests for a harmless syscall such as getpid or gettid, verifying raw return and error reporting. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sparc/raw_syscall.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc/raw_syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc/rt_sigframe.h -->
# sources/test-tools/strace/src/linux/sparc/rt_sigframe.h

## Purpose

This header models the user-space realtime signal frame layout for sparc, including `ucontext`, `siginfo`, or mask offsets needed by strace signal-frame decoding.

## Important APIs, Types, And Functions

This source is classified as `rt-sigframe` for the `sparc` strace backend. It has SHA-1 prefix `9606529111af`, 25 lines, and 507 bytes. Key local interface signals: includes "ptrace.h", <signal.h>; defines STRACE_RT_SIGFRAME_H, OFFSETOF_SIGMASK_IN_RT_SIGFRAME.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

preprocessor includes: "ptrace.h", <signal.h> Linux ptrace regset APIs. The integration point is strace's per-architecture Linux backend under `src/linux/sparc`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Structure layout drift or alignment mistakes can over/under-print register fields; the code mitigates this with size checks but depends on exact ABI offsets. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Exercise signal-delivery and sigreturn traces and verify saved mask/frame addresses for native and compat tasks. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sparc/rt_sigframe.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc/rt_sigframe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc/set_error.c -->
# sources/test-tools/strace/src/linux/sparc/set_error.c

## Purpose

This file implements or selects a SPARC 32-bit architecture hook for strace. Local functions/macros are sparc_set_o0_psr, arch_set_error, arch_set_success. The set-error/success hooks mutate the cached register set, update condition-code/error bits when the ABI needs them, and call `set_regs(tcp->pid)` to persist the change into the tracee.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `sparc` strace backend. It has SHA-1 prefix `08cb736ecc5f`, 28 lines, and 596 bytes. Key local interface signals: functions sparc_set_o0_psr, arch_set_error, arch_set_success.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

It mutates the cached architecture register block and persists it into the stopped tracee with `set_regs(tcp->pid)`.

## Dependencies And Integration Points

strace architecture include/build system. The integration point is strace's per-architecture Linux backend under `src/linux/sparc`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Register tampering bugs can leave the tracee with inconsistent return values or condition-code bits, so failures are behavioral rather than cosmetic. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Run syscall-entry/exit tests under ptrace, including failure returns, restart_syscall where applicable, syscall tampering, and compat personality switching. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sparc/set_error.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc/set_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc/set_scno.c -->
# sources/test-tools/strace/src/linux/sparc/set_scno.c

## Purpose

This file implements or selects a SPARC 32-bit architecture hook for strace. Local functions/macros are arch_set_scno.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `sparc` strace backend. It has SHA-1 prefix `98813656a8f0`, 20 lines, and 462 bytes. Key local interface signals: functions arch_set_scno.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

It mutates the cached architecture register block and persists it into the stopped tracee with `set_regs(tcp->pid)`.

## Dependencies And Integration Points

Linux ptrace regset APIs. The integration point is strace's per-architecture Linux backend under `src/linux/sparc`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Register tampering bugs can leave the tracee with inconsistent return values or condition-code bits, so failures are behavioral rather than cosmetic. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sparc/set_scno.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc/set_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc/signalent.h -->
# sources/test-tools/strace/src/linux/sparc/signalent.h

## Purpose

This file provides the SPARC signal numbering table, ending at `SIGRTMIN`, so strace does not assume the generic signal order.

## Important APIs, Types, And Functions

This source is classified as `signal-table` for the `sparc` strace backend. It has SHA-1 prefix `5e563a166cd2`, 40 lines, and 803 bytes. Key local interface signals: no exported symbols; it is consumed through textual inclusion or generated-table compilation.

## Control Flow

There is no executable control flow. The strace build includes this data into generated lookup arrays; runtime lookup indexes by syscall number, ioctl request, errno, signal, or user offset and then dispatches to generic printers/decoders.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

strace architecture include/build system. The integration point is strace's per-architecture Linux backend under `src/linux/sparc`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is architecture ABI drift: these small files encode register names, audit constants, and feature macros that must match kernel and libc headers. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Compare generated tables with current kernel headers and run decoder lookup tests for representative low, high, compat, and architecture-specific numbers. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sparc/signalent.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc/signalent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc/syscallent.h -->
# sources/test-tools/strace/src/linux/sparc/syscallent.h

## Purpose

This syscall table maps numeric Linux syscall slots for sparc to strace decoder metadata. It contains about 275 explicit table entries and then composes shared rows through includes such as "../32/syscallent-common-32.h", "syscallent-common.h", "../32/subcallent.h". It defines `SYS_socket_subcall` as 500 before including the socket subcall table, so old multiplexed socket calls occupy the architecture-specific extension range expected by strace. The table starts with entries like `[100] = { 2,	0,		SEN(getpriority),		"getpriority"		},` and ends with entries like `[402] = { 3,	TI,		SEN(msgctl),			"msgctl"		},`, which is useful when checking generated row order.

## Important APIs, Types, And Functions

This source is classified as `syscall-table` for the `sparc` strace backend. It has SHA-1 prefix `67735ee54bdb`, 389 lines, and 19881 bytes. Key local interface signals: includes "../32/syscallent-common-32.h", "syscallent-common.h", "../32/subcallent.h"; defines SYS_socket_subcall; 275 table rows.

## Control Flow

There is no executable control flow. The strace build includes this data into generated lookup arrays; runtime lookup indexes by syscall number, ioctl request, errno, signal, or user offset and then dispatches to generic printers/decoders.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../32/syscallent-common-32.h", "syscallent-common.h", "../32/subcallent.h" Linux ptrace regset APIs strace syscall decoder table macros. The integration point is strace's per-architecture Linux backend under `src/linux/sparc`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Risks are numeric table drift against kernel syscall headers, wrong argument count/flags, and mismatched compat table selection; failures appear as wrong syscall names or decoder dispatch. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Compare generated tables with current kernel headers and run decoder lookup tests for representative low, high, compat, and architecture-specific numbers. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sparc/syscallent.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc/syscallent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc/userent.h -->
# sources/test-tools/strace/src/linux/sparc/userent.h

## Purpose

This file is a one-line architecture wrapper that includes "userent0.h". It intentionally has no local control flow; the selected include target supplies the real implementation for this personality or endian variant.

## Important APIs, Types, And Functions

This source is classified as `include-wrapper` for the `sparc` strace backend. It has SHA-1 prefix `032354376d52`, 1 lines, and 22 bytes. Key local interface signals: includes "userent0.h".

## Control Flow

At compile time the preprocessor substitutes the referenced implementation or table into this architecture directory. Runtime behavior is therefore the behavior of the included file under this ABI selection.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "userent0.h". The integration point is strace's per-architecture Linux backend under `src/linux/sparc`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is include-target drift: if the shared file changes assumptions about word size, endian, or personality, this wrapper silently inherits that behavior. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sparc/userent.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc/userent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc64/arch_defs_.h -->
# sources/test-tools/strace/src/linux/sparc64/arch_defs_.h

## Purpose

This architecture definition header advertises strace compile-time capabilities for the sparc64 backend: ARCH_M32_SIZEOF_STRUCT_MSQID64_DS, HAVE_ARCH_GETRVAL2, HAVE_ARCH_UID16_SYSCALLS, HAVE_ARCH_SA_RESTORER, SUPPORTED_PERSONALITIES, PERSONALITY0_AUDIT_ARCH, PERSONALITY1_AUDIT_ARCH, HAVE_ARCH_DEDICATED_ERR_REG. It enables multi-personality decoding, so the same binary can switch between native and compat syscall tables according to audit architecture or runtime register state. The `PERSONALITY*_AUDIT_ARCH` macros are the bridge from seccomp/audit syscall-info records to strace personality selection.

## Important APIs, Types, And Functions

This source is classified as `arch-defs` for the `sparc64` strace backend. It has SHA-1 prefix `7d6325507d04`, 15 lines, and 461 bytes. Key local interface signals: defines ARCH_M32_SIZEOF_STRUCT_MSQID64_DS, HAVE_ARCH_GETRVAL2, HAVE_ARCH_UID16_SYSCALLS, HAVE_ARCH_SA_RESTORER, SUPPORTED_PERSONALITIES, PERSONALITY0_AUDIT_ARCH, PERSONALITY1_AUDIT_ARCH, HAVE_ARCH_DEDICATED_ERR_REG.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

Linux audit architecture constants. The integration point is strace's per-architecture Linux backend under `src/linux/sparc64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is architecture ABI drift: these small files encode register names, audit constants, and feature macros that must match kernel and libc headers. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sparc64/arch_defs_.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc64/arch_defs_.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc64/arch_get_personality.c -->
# sources/test-tools/strace/src/linux/sparc64/arch_get_personality.c

## Purpose

This file implements or selects a SPARC 64-bit architecture hook for strace. Local functions/macros are get_personality_from_syscall_info. `get_personality_from_syscall_info` maps `PTRACE_GET_SYSCALL_INFO` audit architecture records to the compat personality for bi-ABI tracing.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `sparc64` strace backend. It has SHA-1 prefix `2f237a871604`, 13 lines, and 305 bytes. Key local interface signals: functions get_personality_from_syscall_info.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

Linux ptrace regset APIs Linux audit architecture constants. The integration point is strace's per-architecture Linux backend under `src/linux/sparc64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Register selection mistakes produce wrong syscall numbers, arguments, or errno state, which cascades into incorrect decoder selection and misleading traces. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sparc64/arch_get_personality.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc64/arch_get_personality.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc64/arch_getrval2.c -->
# sources/test-tools/strace/src/linux/sparc64/arch_getrval2.c

## Purpose

This file is a one-line architecture wrapper that includes "../sparc/arch_getrval2.c". It intentionally has no local control flow; the selected include target supplies the real implementation for this personality or endian variant.

## Important APIs, Types, And Functions

This source is classified as `include-wrapper` for the `sparc64` strace backend. It has SHA-1 prefix `a12ca1b4ab74`, 1 lines, and 36 bytes. Key local interface signals: includes "../sparc/arch_getrval2.c".

## Control Flow

At compile time the preprocessor substitutes the referenced implementation or table into this architecture directory. Runtime behavior is therefore the behavior of the included file under this ABI selection.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../sparc/arch_getrval2.c". The integration point is strace's per-architecture Linux backend under `src/linux/sparc64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is include-target drift: if the shared file changes assumptions about word size, endian, or personality, this wrapper silently inherits that behavior. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sparc64/arch_getrval2.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc64/arch_getrval2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc64/arch_prstatus_regset.c -->
# sources/test-tools/strace/src/linux/sparc64/arch_prstatus_regset.c

## Purpose

This decoder prints NT_PRSTATUS register-set payloads for sparc64. It bounds reads to `MIN(sizeof(regs), size)`, rejects misaligned or zero sizes, and prints only fields present in the fetched prefix. When the kernel supplies a larger blob than the known structure, it emits a more-data marker instead of over-reading unknown layout.

## Important APIs, Types, And Functions

This source is classified as `prstatus-regset` for the `sparc64` strace backend. It has SHA-1 prefix `6cd69d2dfce6`, 72 lines, and 2013 bytes. Key local interface signals: includes "../sparc/arch_prstatus_regset.c"; functions arch_decode_prstatus_regset.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

preprocessor includes: "../sparc/arch_prstatus_regset.c" strace structured printing macros tracee-memory readers. The integration point is strace's per-architecture Linux backend under `src/linux/sparc64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Structure layout drift or alignment mistakes can over/under-print register fields; the code mitigates this with size checks but depends on exact ABI offsets. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Decode NT_PRSTATUS/pt_regs samples with full, truncated, and oversized sizes to validate graceful printing. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sparc64/arch_prstatus_regset.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc64/arch_prstatus_regset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc64/arch_prstatus_regset.h -->
# sources/test-tools/strace/src/linux/sparc64/arch_prstatus_regset.h

## Purpose

This header defines the type alias used to decode NT_PRSTATUS register-set payloads for sparc64 and sets `HAVE_ARCH_PRSTATUS_REGSET`.

## Important APIs, Types, And Functions

This source is classified as `prstatus-regset` for the `sparc64` strace backend. It has SHA-1 prefix `3045590168a1`, 26 lines, and 567 bytes. Key local interface signals: includes "../sparc/arch_prstatus_regset.h"; defines STRACE_ARCH_PRSTATUS_REGSET_H, HAVE_ARCH_PRSTATUS_REGSET.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

preprocessor includes: "../sparc/arch_prstatus_regset.h". The integration point is strace's per-architecture Linux backend under `src/linux/sparc64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Structure layout drift or alignment mistakes can over/under-print register fields; the code mitigates this with size checks but depends on exact ABI offsets. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Decode NT_PRSTATUS/pt_regs samples with full, truncated, and oversized sizes to validate graceful printing. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sparc64/arch_prstatus_regset.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc64/arch_prstatus_regset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc64/arch_pt_regs.c -->
# sources/test-tools/strace/src/linux/sparc64/arch_pt_regs.c

## Purpose

This file implements or selects a SPARC 64-bit architecture hook for strace. Local functions/macros are arch_decode_pt_regs. The pt_regs decoder prints kernel `struct pt_regs` fields for ptrace or signal-frame contexts, with compat guards on bi-ABI targets.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `sparc64` strace backend. It has SHA-1 prefix `c8ff5d91a2a7`, 18 lines, and 321 bytes. Key local interface signals: includes "../sparc/arch_pt_regs.c"; functions arch_decode_pt_regs.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

preprocessor includes: "../sparc/arch_pt_regs.c". The integration point is strace's per-architecture Linux backend under `src/linux/sparc64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Structure layout drift or alignment mistakes can over/under-print register fields; the code mitigates this with size checks but depends on exact ABI offsets. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Decode NT_PRSTATUS/pt_regs samples with full, truncated, and oversized sizes to validate graceful printing. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sparc64/arch_pt_regs.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc64/arch_pt_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc64/arch_pt_regs64.c -->
# sources/test-tools/strace/src/linux/sparc64/arch_pt_regs64.c

## Purpose

This file implements or selects a SPARC 64-bit architecture hook for strace. Local functions/macros are decode_pt_regs64. The pt_regs decoder prints kernel `struct pt_regs` fields for ptrace or signal-frame contexts, with compat guards on bi-ABI targets.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `sparc64` strace backend. It has SHA-1 prefix `a85344e7c31c`, 34 lines, and 646 bytes. Key local interface signals: functions decode_pt_regs64.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

strace structured printing macros. The integration point is strace's per-architecture Linux backend under `src/linux/sparc64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Structure layout drift or alignment mistakes can over/under-print register fields; the code mitigates this with size checks but depends on exact ABI offsets. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Decode NT_PRSTATUS/pt_regs samples with full, truncated, and oversized sizes to validate graceful printing. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sparc64/arch_pt_regs64.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc64/arch_pt_regs64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc64/arch_regs.c -->
# sources/test-tools/strace/src/linux/sparc64/arch_regs.c

## Purpose

This file implements or selects a SPARC 64-bit architecture hook for strace. Local functions/macros are ARCH_PC_REG. The file binds the generic register-fetch path to concrete global register storage plus `ARCH_PC_REG` and `ARCH_SP_REG` macros used by shared code.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `sparc64` strace backend. It has SHA-1 prefix `887dc3916bbb`, 10 lines, and 217 bytes. Key local interface signals: includes "../sparc/arch_regs.c"; defines ARCH_PC_REG.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

preprocessor includes: "../sparc/arch_regs.c". The integration point is strace's per-architecture Linux backend under `src/linux/sparc64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is architecture ABI drift: these small files encode register names, audit constants, and feature macros that must match kernel and libc headers. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sparc64/arch_regs.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc64/arch_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc64/arch_rt_sigframe.c -->
# sources/test-tools/strace/src/linux/sparc64/arch_rt_sigframe.c

## Purpose

This source computes the runtime address of the sparc64 realtime signal frame from the tracee stack pointer, with ABI-specific stack-bias or compat handling where required. The SPARC64 variant applies the 2047-byte stack bias for native 64-bit frames and masks to 32 bits for compat personality 1.

## Important APIs, Types, And Functions

This source is classified as `rt-sigframe` for the `sparc64` strace backend. It has SHA-1 prefix `f8348e0b77d5`, 17 lines, and 334 bytes. Key local interface signals: defines STACK_BIAS.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

strace architecture include/build system. The integration point is strace's per-architecture Linux backend under `src/linux/sparc64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Structure layout drift or alignment mistakes can over/under-print register fields; the code mitigates this with size checks but depends on exact ABI offsets. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Exercise signal-delivery and sigreturn traces and verify saved mask/frame addresses for native and compat tasks. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sparc64/arch_rt_sigframe.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc64/arch_rt_sigframe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc64/arch_sigreturn.c -->
# sources/test-tools/strace/src/linux/sparc64/arch_sigreturn.c

## Purpose

This file decodes the architecture-specific sigreturn frame for sparc64. It reads frame data from the stack pointer, prints the saved signal mask address or fields, and handles compat structure sizing where present. It reuses shared code through "../sparc/arch_sigreturn.c", "../sparc/arch_sigreturn.c" while redefining size/personality macros around the include where needed.

## Important APIs, Types, And Functions

This source is classified as `sigreturn` for the `sparc64` strace backend. It has SHA-1 prefix `65920b8efb3c`, 26 lines, and 663 bytes. Key local interface signals: includes "../sparc/arch_sigreturn.c", "../sparc/arch_sigreturn.c"; defines arch_sigreturn, SIZEOF_STRUCT_SPARC_STACKF, SIZEOF_STRUCT_PT_REGS, PERSONALITY_WORDSIZE, arch_sigreturn; functions arch_sigreturn.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

preprocessor includes: "../sparc/arch_sigreturn.c", "../sparc/arch_sigreturn.c". The integration point is strace's per-architecture Linux backend under `src/linux/sparc64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is architecture ABI drift: these small files encode register names, audit constants, and feature macros that must match kernel and libc headers. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Exercise signal-delivery and sigreturn traces and verify saved mask/frame addresses for native and compat tasks. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sparc64/arch_sigreturn.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc64/arch_sigreturn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc64/errnoent.h -->
# sources/test-tools/strace/src/linux/sparc64/errnoent.h

## Purpose

This file is a one-line architecture wrapper that includes "../sparc/errnoent.h". It intentionally has no local control flow; the selected include target supplies the real implementation for this personality or endian variant.

## Important APIs, Types, And Functions

This source is classified as `include-wrapper` for the `sparc64` strace backend. It has SHA-1 prefix `ee0bc7ddaa3d`, 1 lines, and 31 bytes. Key local interface signals: includes "../sparc/errnoent.h".

## Control Flow

At compile time the preprocessor substitutes the referenced implementation or table into this architecture directory. Runtime behavior is therefore the behavior of the included file under this ABI selection.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../sparc/errnoent.h". The integration point is strace's per-architecture Linux backend under `src/linux/sparc64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is include-target drift: if the shared file changes assumptions about word size, endian, or personality, this wrapper silently inherits that behavior. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sparc64/errnoent.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc64/errnoent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc64/get_error.c -->
# sources/test-tools/strace/src/linux/sparc64/get_error.c

## Purpose

This file implements or selects a SPARC 64-bit architecture hook for strace. Local functions/macros are arch_get_error. `arch_get_error` interprets the architecture error convention and fills `tcp->u_rval`/`tcp->u_error`, using negated errno helpers or condition-code bits as appropriate.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `sparc64` strace backend. It has SHA-1 prefix `67723ef154e3`, 17 lines, and 370 bytes. Key local interface signals: functions arch_get_error.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

strace architecture include/build system. The integration point is strace's per-architecture Linux backend under `src/linux/sparc64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Register selection mistakes produce wrong syscall numbers, arguments, or errno state, which cascades into incorrect decoder selection and misleading traces. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Run syscall-entry/exit tests under ptrace, including failure returns, restart_syscall where applicable, syscall tampering, and compat personality switching. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sparc64/get_error.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc64/get_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc64/get_scno.c -->
# sources/test-tools/strace/src/linux/sparc64/get_scno.c

## Purpose

This file implements or selects a SPARC 64-bit architecture hook for strace. Local functions/macros are arch_get_scno. `arch_get_scno` extracts the syscall number from the architecture syscall-number register or, for s390 restart_syscall, from `NT_S390_SYSTEM_CALL` when the normal register is clobbered by a negated errno.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `sparc64` strace backend. It has SHA-1 prefix `f5d5752745ae`, 32 lines, and 687 bytes. Key local interface signals: functions arch_get_scno.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

Linux ptrace regset APIs. The integration point is strace's per-architecture Linux backend under `src/linux/sparc64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Register selection mistakes produce wrong syscall numbers, arguments, or errno state, which cascades into incorrect decoder selection and misleading traces. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Run syscall-entry/exit tests under ptrace, including failure returns, restart_syscall where applicable, syscall tampering, and compat personality switching. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sparc64/get_scno.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc64/get_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc64/get_syscall_args.c -->
# sources/test-tools/strace/src/linux/sparc64/get_syscall_args.c

## Purpose

This file implements or selects a SPARC 64-bit architecture hook for strace. Local functions/macros are arch_get_syscall_args. `arch_get_syscall_args` copies up to six syscall arguments from ABI-defined argument registers into `tcp->u_arg`; compat paths zero-extend 32-bit register values.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `sparc64` strace backend. It has SHA-1 prefix `9870ef7615da`, 35 lines, and 1145 bytes. Key local interface signals: functions arch_get_syscall_args.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

strace architecture include/build system. The integration point is strace's per-architecture Linux backend under `src/linux/sparc64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Register selection mistakes produce wrong syscall numbers, arguments, or errno state, which cascades into incorrect decoder selection and misleading traces. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Run syscall-entry/exit tests under ptrace, including failure returns, restart_syscall where applicable, syscall tampering, and compat personality switching. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sparc64/get_syscall_args.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc64/get_syscall_args.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc64/ioctls_arch0.h -->
# sources/test-tools/strace/src/linux/sparc64/ioctls_arch0.h

## Purpose

This generated ioctl table records 121 architecture-local ioctl definitions for sparc64, with header names, symbolic names, `_IOC_*` direction, request numbers, and encoded argument sizes. Boundary rows include `{ "asm/apc.h", "APCIOCGBPORT", _IOC_READ, 0x4104, 0x04 },` and `{ "asm/watchdog.h", "WIOCSTOP", _IOC_NONE, 0x570b, 0x00 },`, showing the source header family and final request preserved by generation.

## Important APIs, Types, And Functions

This source is classified as `ioctl-arch-table` for the `sparc64` strace backend. It has SHA-1 prefix `da88d6929e94`, 122 lines, and 7326 bytes. Key local interface signals: 121 table rows.

## Control Flow

There is no executable control flow. The strace build includes this data into generated lookup arrays; runtime lookup indexes by syscall number, ioctl request, errno, signal, or user offset and then dispatches to generic printers/decoders.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

Linux ioctl encoding macros and generated `ioctls_gen.sh` output. The integration point is strace's per-architecture Linux backend under `src/linux/sparc64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Risks are stale generated ioctl metadata, request-size mismatches between 32-bit and 64-bit personalities, and duplicate request numbers resolving to the wrong symbolic name. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Compare generated tables with current kernel headers and run decoder lookup tests for representative low, high, compat, and architecture-specific numbers. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sparc64/ioctls_arch0.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc64/ioctls_arch0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc64/ioctls_arch1.h -->
# sources/test-tools/strace/src/linux/sparc64/ioctls_arch1.h

## Purpose

This file is a one-line architecture wrapper that includes "../sparc/ioctls_arch0.h". It intentionally has no local control flow; the selected include target supplies the real implementation for this personality or endian variant.

## Important APIs, Types, And Functions

This source is classified as `include-wrapper` for the `sparc64` strace backend. It has SHA-1 prefix `da574b2c858d`, 1 lines, and 35 bytes. Key local interface signals: includes "../sparc/ioctls_arch0.h".

## Control Flow

At compile time the preprocessor substitutes the referenced implementation or table into this architecture directory. Runtime behavior is therefore the behavior of the included file under this ABI selection.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../sparc/ioctls_arch0.h". The integration point is strace's per-architecture Linux backend under `src/linux/sparc64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is include-target drift: if the shared file changes assumptions about word size, endian, or personality, this wrapper silently inherits that behavior. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sparc64/ioctls_arch1.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc64/ioctls_arch1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc64/ioctls_inc0.h -->
# sources/test-tools/strace/src/linux/sparc64/ioctls_inc0.h

## Purpose

This file is a one-line architecture wrapper that includes "../64/ioctls_inc.h". It intentionally has no local control flow; the selected include target supplies the real implementation for this personality or endian variant.

## Important APIs, Types, And Functions

This source is classified as `include-wrapper` for the `sparc64` strace backend. It has SHA-1 prefix `3defd9a34cb2`, 1 lines, and 30 bytes. Key local interface signals: includes "../64/ioctls_inc.h".

## Control Flow

At compile time the preprocessor substitutes the referenced implementation or table into this architecture directory. Runtime behavior is therefore the behavior of the included file under this ABI selection.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../64/ioctls_inc.h". The integration point is strace's per-architecture Linux backend under `src/linux/sparc64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is include-target drift: if the shared file changes assumptions about word size, endian, or personality, this wrapper silently inherits that behavior. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sparc64/ioctls_inc0.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc64/ioctls_inc0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc64/ioctls_inc1.h -->
# sources/test-tools/strace/src/linux/sparc64/ioctls_inc1.h

## Purpose

This file is a one-line architecture wrapper that includes "../sparc/ioctls_inc0.h". It intentionally has no local control flow; the selected include target supplies the real implementation for this personality or endian variant.

## Important APIs, Types, And Functions

This source is classified as `include-wrapper` for the `sparc64` strace backend. It has SHA-1 prefix `aa3bf9bf5a61`, 1 lines, and 34 bytes. Key local interface signals: includes "../sparc/ioctls_inc0.h".

## Control Flow

At compile time the preprocessor substitutes the referenced implementation or table into this architecture directory. Runtime behavior is therefore the behavior of the included file under this ABI selection.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../sparc/ioctls_inc0.h". The integration point is strace's per-architecture Linux backend under `src/linux/sparc64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is include-target drift: if the shared file changes assumptions about word size, endian, or personality, this wrapper silently inherits that behavior. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sparc64/ioctls_inc1.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc64/ioctls_inc1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc64/raw_syscall.h -->
# sources/test-tools/strace/src/linux/sparc64/raw_syscall.h

## Purpose

This header defines an inline `raw_syscall_0` helper for sparc64 bootstrap/probing paths. It binds syscall-number and return registers with inline assembly and reports a separate error flag pointer to the generic raw syscall caller. The SPARC implementation uses trap instructions and condition-code handling to distinguish success from syscall errors.

## Important APIs, Types, And Functions

This source is classified as `raw-syscall` for the `sparc64` strace backend. It has SHA-1 prefix `78c8dca0f914`, 40 lines, and 1116 bytes. Key local interface signals: includes "kernel_types.h"; defines STRACE_RAW_SYSCALL_H, raw_syscall_0; functions raw_syscall_0.

## Control Flow

Callers pass a syscall number to `raw_syscall_0`; inline assembly loads the ABI syscall register, enters the kernel, records whether an error occurred, and returns the raw result without using libc wrappers.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

preprocessor includes: "kernel_types.h". The integration point is strace's per-architecture Linux backend under `src/linux/sparc64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is architecture ABI drift: these small files encode register names, audit constants, and feature macros that must match kernel and libc headers. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Compile and execute raw-syscall smoke tests for a harmless syscall such as getpid or gettid, verifying raw return and error reporting. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sparc64/raw_syscall.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc64/raw_syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc64/rt_sigframe.h -->
# sources/test-tools/strace/src/linux/sparc64/rt_sigframe.h

## Purpose

This header models the user-space realtime signal frame layout for sparc64, including `ucontext`, `siginfo`, or mask offsets needed by strace signal-frame decoding.

## Important APIs, Types, And Functions

This source is classified as `rt-sigframe` for the `sparc64` strace backend. It has SHA-1 prefix `a29ba33ffc68`, 31 lines, and 634 bytes. Key local interface signals: includes "../sparc/rt_sigframe.h", "ptrace.h", <signal.h>; defines STRACE_RT_SIGFRAME_H, OFFSETOF_SIGMASK_IN_RT_SIGFRAME.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

preprocessor includes: "../sparc/rt_sigframe.h", "ptrace.h", <signal.h> Linux ptrace regset APIs. The integration point is strace's per-architecture Linux backend under `src/linux/sparc64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Structure layout drift or alignment mistakes can over/under-print register fields; the code mitigates this with size checks but depends on exact ABI offsets. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Exercise signal-delivery and sigreturn traces and verify saved mask/frame addresses for native and compat tasks. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sparc64/rt_sigframe.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc64/rt_sigframe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc64/set_error.c -->
# sources/test-tools/strace/src/linux/sparc64/set_error.c

## Purpose

This file implements or selects a SPARC 64-bit architecture hook for strace. Local functions/macros are sparc64_set_o0_tstate, arch_set_error, arch_set_success. The set-error/success hooks mutate the cached register set, update condition-code/error bits when the ABI needs them, and call `set_regs(tcp->pid)` to persist the change into the tracee.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `sparc64` strace backend. It has SHA-1 prefix `00bc8fa103e2`, 29 lines, and 660 bytes. Key local interface signals: functions sparc64_set_o0_tstate, arch_set_error, arch_set_success.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

It mutates the cached architecture register block and persists it into the stopped tracee with `set_regs(tcp->pid)`.

## Dependencies And Integration Points

strace architecture include/build system. The integration point is strace's per-architecture Linux backend under `src/linux/sparc64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Register tampering bugs can leave the tracee with inconsistent return values or condition-code bits, so failures are behavioral rather than cosmetic. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Run syscall-entry/exit tests under ptrace, including failure returns, restart_syscall where applicable, syscall tampering, and compat personality switching. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sparc64/set_error.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc64/set_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc64/set_scno.c -->
# sources/test-tools/strace/src/linux/sparc64/set_scno.c

## Purpose

This file is a one-line architecture wrapper that includes "../sparc/set_scno.c". It intentionally has no local control flow; the selected include target supplies the real implementation for this personality or endian variant.

## Important APIs, Types, And Functions

This source is classified as `include-wrapper` for the `sparc64` strace backend. It has SHA-1 prefix `c1bff9a71e87`, 1 lines, and 31 bytes. Key local interface signals: includes "../sparc/set_scno.c".

## Control Flow

At compile time the preprocessor substitutes the referenced implementation or table into this architecture directory. Runtime behavior is therefore the behavior of the included file under this ABI selection.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../sparc/set_scno.c". The integration point is strace's per-architecture Linux backend under `src/linux/sparc64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is include-target drift: if the shared file changes assumptions about word size, endian, or personality, this wrapper silently inherits that behavior. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sparc64/set_scno.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc64/set_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc64/signalent.h -->
# sources/test-tools/strace/src/linux/sparc64/signalent.h

## Purpose

This file is a one-line architecture wrapper that includes "../sparc/signalent.h". It intentionally has no local control flow; the selected include target supplies the real implementation for this personality or endian variant.

## Important APIs, Types, And Functions

This source is classified as `include-wrapper` for the `sparc64` strace backend. It has SHA-1 prefix `9d217d03ad48`, 1 lines, and 32 bytes. Key local interface signals: includes "../sparc/signalent.h".

## Control Flow

At compile time the preprocessor substitutes the referenced implementation or table into this architecture directory. Runtime behavior is therefore the behavior of the included file under this ABI selection.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../sparc/signalent.h". The integration point is strace's per-architecture Linux backend under `src/linux/sparc64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is include-target drift: if the shared file changes assumptions about word size, endian, or personality, this wrapper silently inherits that behavior. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sparc64/signalent.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc64/signalent.h -->
