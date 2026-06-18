<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/tools/gen_opcode_table.c -->
# sources/distributed-fs/ceph-client/arch/s390/tools/gen_opcode_table.c

Purpose: This host tool converts the s390 opcode list into C initializers for the in-kernel disassembler: instruction format enums, long-name storage, opcode table entries, and opcode group offsets.

Important APIs/types/functions: Data types are `struct insn_type`, `struct insn`, `struct insn_group`, `struct insn_format`, and `struct gen_opcode`. Main helpers include `insn_format_to_type`, `read_instructions`, sorting comparators, `print_formats`, `print_long_insn`, `print_opcode`, `add_to_group`, `print_opcode_table`, `print_opcode_table_offsets`, and `main`.

Control flow: The tool reads `opcode name format` triples from stdin, maps each format to an opcode-position/mask type, stores uppercase names, and then prints generated code in several sorted passes. Formats are sorted to emit unique `INSTR_*` enum entries. Long instruction names are sorted and emitted into a separate initializer. Opcodes are sorted by opcode string; multi-byte opcodes are emitted first and grouped by leading byte/mask/offset/count, followed by one-byte opcodes.

State and persistence: Dynamic arrays of instructions and groups exist only while the tool runs. Persistent output is `dis-defs.h`, used by the kernel disassembler.

Dependencies and integration points: It depends on standard C library scanf/qsort/realloc/string helpers and the format vocabulary in `opcodes.txt`. It integrates with s390 disassembly tables and any tool/tests that decode instruction bytes.

Risks and test signals: Format-to-type mapping must match s390 instruction encoding locations for second/third/fourth opcode nibbles. Grouping by leading opcode and mask drives lookup efficiency and correctness; bad grouping can make the disassembler miss or misidentify instructions. Tests include generated-header golden comparisons, disassembly of representative one-byte/three-nibble/two-byte/six-byte formats, long mnemonic handling, malformed input rejection, and valgrind/ASAN for host-tool memory handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/tools/gen_opcode_table.c -->
