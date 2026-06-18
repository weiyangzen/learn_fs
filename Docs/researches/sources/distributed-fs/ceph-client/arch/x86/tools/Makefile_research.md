<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/tools/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/tools/Makefile

## Purpose
`tools/Makefile` builds x86 host utilities used for instruction-decoder tests, relocation extraction, and vDSO conversion.

## Important APIs, types, and functions
It defines `posttest`, `insn_decoder_test`, `insn_sanity`, `relocs`, and `vdso2c`, including host include paths for generated instruction tables and UAPI headers.

## Control flow
`posttest` disassembles `.text` from `vmlinux`, reformats objdump output, runs decoder length comparison, then runs random decoder sanity testing. The host programs are built as kbuild host tools.

## State and persistence behavior
No runtime kernel state exists. Build artifacts and test outputs are the only persistence.

## Dependencies and integration points
It depends on objdump, awk, generated `inat-tables.c`, x86 tools library sources, and configuration-derived 32/64-bit mode flags.

## Risks and edge cases
Host include path skew can test against stale generated decoder tables. The tests can be expensive at the one-million-iteration sanity setting.

## Test signals
Signals are successful host-tool builds, `make arch/x86/tools/posttest`, and decoder success output for both 32-bit and 64-bit configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/tools/Makefile -->
