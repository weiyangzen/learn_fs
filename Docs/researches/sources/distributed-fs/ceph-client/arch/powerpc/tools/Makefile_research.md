# sources/distributed-fs/ceph-client/arch/powerpc/tools/Makefile

## Purpose
This Makefile hooks PowerPC architecture build tooling into Kbuild for generating `vmlinux.arch.S`, the assembly reservation file for out-of-line ftrace stubs.

## Important APIs, Types, And Functions
It defines `quiet_cmd_gen_ftrace_ool_stubs` and `cmd_gen_ftrace_ool_stubs`, invoking `ftrace-gen-ool-stubs.sh` with the configured text-stub reserve count, 64-bit setting, objdump path, `vmlinux.o`, and output file. The target rule builds `$(obj)/vmlinux.arch.S` from the script and `vmlinux.o`, and adds the output to `targets`.

## Control Flow
During the architecture build, Kbuild detects the generated assembly target and runs the command through `if_changed`, regenerating only when inputs or command text change. The generated assembly is later linked into the kernel to reserve ftrace trampoline space.

## State And Persistence
The persistent build artifact is `vmlinux.arch.S` in the object tree. No source-tree state is modified by the Makefile itself.

## Dependencies And Integration Points
It depends on Kbuild variables `CONFIG_PPC_FTRACE_OUT_OF_LINE_NUM_RESERVE`, `CONFIG_64BIT`, `OBJDUMP`, `obj`, `src`, and `FORCE`, and integrates with `ftrace-gen-ool-stubs.sh` and the final PowerPC link.

## Risks
Incorrect argument ordering or stale dependency tracking would reserve the wrong number of stubs, causing ftrace patching failures. Because `vmlinux.o` is an input, this rule sits late enough in the build that missing tools or section format changes can break final linking.

## Test Signals
Builds with function tracing and patchable function entries enabled should generate `vmlinux.arch.S`; incremental builds should regenerate it when `vmlinux.o` or the script changes. Link-time ftrace failures are the primary downstream signal.
