# sources/distributed-fs/ceph-client/tools/perf/arch/x86/tests/gen-insn-x86-dat.awk

## Purpose
This AWK script converts annotated `objdump -dSw` output from `insn-x86-dat-src.o` into C initializer rows consumed by the x86 instruction decoder test. It is part of the generator pipeline for `insn-x86-dat-32.c` and `insn-x86-dat-64.c`.

## Important APIs, Variables, and Patterns
The `BEGIN` block emits a generated-file banner and initializes `op`, `branch`, `rel`, and `going`. `/ Start here /` and `/ Stop here /` delimit the source region that should become test data. Disassembly lines matching `/^\s*[0-9a-fA-F]+\:/` are parsed only while `going` is true. The script extracts bytes from fields that look like two hex digits, counts instruction length, escapes tabs in the disassembly text, and emits rows shaped like `{{ bytes }, len, rel, op, branch, "disassembly",},`.

Lines containing `Expecting:` set metadata for the next instruction row. The script scans fields after `Expecting:` into `op`, `branch`, and `rel`, then resets those values after emitting a row.

## Control Flow
Generation is streaming: banner first, toggle active region on markers, capture expected metadata when encountered, and emit one C initializer per matching disassembly line inside the active region. Metadata applies to the next emitted instruction and then returns to defaults.

## State and Persistence
The script itself writes only to stdout. Its transient state is the active-region flag and expected metadata for the next instruction. Generated persistence happens in the caller script that redirects stdout to `insn-x86-dat-32.c` or `insn-x86-dat-64.c`.

## Dependencies and Integration Points
The script depends on GNU/binutils-style `objdump -dSw` formatting: address-colon prefixes, whitespace-delimited hex byte fields, and source annotation comments containing `Expecting:`. `gen-insn-x86-dat.sh` invokes it after compiling the source fixture in 64-bit and 32-bit modes.

## Risks and Edge Cases
Parser fragility is the main risk. Changes in objdump formatting, localized output, extra non-byte tokens before instruction text, or different source annotation spacing can produce malformed C rows. The script assumes `Expecting:` fields appear in a fixed order and that instruction bytes are exactly two hex characters. It has no explicit error reporting for missing metadata or empty active regions.

## Test Signals
Useful signals are successful regeneration of `insn-x86-dat-32.c` and `insn-x86-dat-64.c`, clean compilation of the generated C includes, and passing `insn_x86` decoder tests. Diffs in generated rows should be reviewed because they may reflect either intended binutils support changes or generator/parser drift.
