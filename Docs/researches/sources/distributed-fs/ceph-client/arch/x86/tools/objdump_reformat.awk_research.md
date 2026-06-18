<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/tools/objdump_reformat.awk -->
# sources/distributed-fs/ceph-client/arch/x86/tools/objdump_reformat.awk

## Purpose
`objdump_reformat.awk` normalizes objdump disassembly into the tab-separated instruction format consumed by `insn_decoder_test`.

## Important APIs, types, and functions
It tracks `prev_addr`, `prev_hex`, and `prev_mnemonic`, filters bad/prefix-only mnemonics with `bad_expr`, and splits `fwait` when objdump folds it into another x87 instruction.

## Control flow
For symbol lines it emits a compact symbol marker. For instruction lines it joins continuation byte lines, filters the previous instruction if needed, emits address/hex/mnemonic triples, and flushes the final instruction in `END`.

## State and persistence behavior
State is only the previous instruction accumulator in AWK variables.

## Dependencies and integration points
It depends on objdump text format and the decoder test's parser expecting tabs and contiguous hex byte text.

## Risks and edge cases
Objdump format changes can break parsing or cause malformed-line errors. Filtering bad instructions reduces false failures but can also hide decoder gaps.

## Test signals
Signals are successful `posttest` pipeline runs and spot checks around long instructions and x87 `fwait` output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/tools/objdump_reformat.awk -->
