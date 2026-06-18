<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/opcode_helper.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/opcode_helper.c

Purpose: returns SH-2A instruction length for exception fixups.

Important APIs/types/functions: `instruction_size(unsigned short insn)`.

Control flow: decodes known 32-bit prefixes and returns 4 or default 2 so trap code can advance PC correctly.

State and persistence: no persistent state.

Dependencies/integration: integrates with exception/trap emulation that needs variable instruction sizes.

Risks: missing an opcode class advances PC incorrectly after emulation.

Test signals: unit-test representative 16-bit and 32-bit SH-2A opcodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/opcode_helper.c -->
