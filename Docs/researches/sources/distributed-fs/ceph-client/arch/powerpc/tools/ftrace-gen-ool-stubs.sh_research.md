# sources/distributed-fs/ceph-client/arch/powerpc/tools/ftrace-gen-ool-stubs.sh

## Purpose
This generator counts patchable function-entry relocations in `vmlinux.o` and emits assembly reserving out-of-line ftrace stub space for normal text and init text.

## Important APIs, Types, And Functions
Inputs are reserve count, 64-bit flag, objdump path, `vmlinux.o`, and output assembly path. It selects relocation type `R_PPC64_ADDR64` or `R_PPC_ADDR32`, counts total and init-text relocations in `__patchable_function_entries`, computes text-end stubs beyond the built-in reserve, and writes symbols `ftrace_ool_stub_text_end_count`, `ftrace_ool_stub_text_end`, `ftrace_ool_stub_inittext_count`, and `ftrace_ool_stub_inittext`.

## Control Flow
With `set -e`, objdump/grep/count failures stop the build. The script counts relocations, subtracts init/startup entries from total text entries, clamps extra text-end stubs at zero, then writes an assembly file with `.tramp.ftrace.text` and `.tramp.ftrace.init` sections sized by `FTRACE_OOL_STUB_SIZE`.

## State And Persistence
The persistent output is the generated `vmlinux.arch.S`. It derives entirely from the current `vmlinux.o` relocation table and configuration inputs.

## Dependencies And Integration Points
It depends on objdump output format, `grep`, POSIX shell arithmetic, and assembly macros from `asm/asm-offsets.h`, `asm/ppc_asm.h`, and `linux/linkage.h`. The Makefile uses it during the PowerPC final build.

## Risks
Relocation naming or section naming changes can miscount stubs. The generated file is critical for ftrace patch reachability, so under-reservation can break runtime tracing while over-reservation wastes text space. The script overwrites its output path directly.

## Test Signals
Builds with `CONFIG_FUNCTION_TRACER` and patchable entries should produce nonzero counts when functions exist. The downstream `ftrace_check.sh` and successful boot with ftrace enabled are practical validation signals.
