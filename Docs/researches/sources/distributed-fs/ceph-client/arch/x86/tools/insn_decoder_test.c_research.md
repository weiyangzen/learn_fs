<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/tools/insn_decoder_test.c -->
# sources/distributed-fs/ceph-client/arch/x86/tools/insn_decoder_test.c

## Purpose
`insn_decoder_test.c` is a host test that compares the x86 instruction decoder's computed length with objdump's instruction byte length.

## Important APIs, types, and functions
Key functions are `parse_args()`, `malformed_line()`, `dump_field()`, `dump_insn()`, and `main()`. It directly includes `inat.c` and `insn.c` from tools.

## Control flow
The program reads reformatted objdump lines, tracks symbol context, parses hex bytes into a 16-byte buffer, calls `insn_decode()` in 32-bit or 64-bit mode, and reports mismatches or decode errors.

## State and persistence behavior
State is process-local counters, symbol name, verbosity, and architecture mode. It does not write persistent files.

## Dependencies and integration points
It depends on `objdump_reformat.awk`, generated inat tables, `tools/arch/x86/lib` decoder sources, and `linux/kallsyms.h` for symbol buffer sizing.

## Risks and edge cases
Input format is strict tab-delimited output from the AWK reformatter. Decoder false positives may come from objdump syntax quirks or unsupported instruction encodings.

## Test signals
Signals are zero-warning posttest runs on `vmlinux` and verbose dumps for any decoder-length mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/tools/insn_decoder_test.c -->
