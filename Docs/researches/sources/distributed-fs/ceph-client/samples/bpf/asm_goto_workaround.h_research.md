# sources/distributed-fs/ceph-client/samples/bpf/asm_goto_workaround.h

Purpose: hides kernel inline assembly constructs from the BPF sample clang compilation path.

Important APIs/types/functions: include guard, includes `linux/types.h`, defines `asm_goto_output`, maps `asm_inline` to `asm`, and overrides `volatile(...)`.

Control flow: preprocessor-only behavior; included forcibly by the BPF Makefile for legacy BPF C compilation.

State and persistence: no state.

Dependencies and integration: integrates with the BPF sample build rule that includes kernel headers under `--target=bpf` or LLVM IR compilation. It avoids unsupported assembly from headers such as arch sysreg definitions.

Risks: macro overrides are broad and only appropriate for BPF sample compilation. Using this header outside that context could change semantics or hide real compiler diagnostics.

Test signals: successful BPF sample compilation on architectures whose headers contain unsupported inline asm.
