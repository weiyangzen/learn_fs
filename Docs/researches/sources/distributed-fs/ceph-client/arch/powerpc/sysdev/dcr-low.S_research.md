<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/dcr-low.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/dcr-low.S

Purpose: native assembly implementation for indirect access to PowerPC Device Control Registers by register number.

Important APIs/types/functions: exported `__mfdcr` and `__mtdcr`, macro `DCR_ACCESS_PROLOG`, and generated jump tables `__mfdcr_table`/`__mtdcr_table` covering DCR numbers 0 through 1023.

Control flow: the prolog bounds-checks r3 against 1024, scales it to a table entry, branches through CTR to the selected `mfdcr` or `mtdcr` instruction, traps and emits a bug entry for out-of-range access, then returns. The `.rept` block emits paired read/write snippets for every DCR index.

State and persistence: no memory state. It reads or writes processor DCR state directly.

Dependencies and integration points: depends on PowerPC assembler support for DCR instructions, bug table emission, and callers in the DCR subsystem.

Risks: the generated table is large and instruction-address sensitive. Out-of-range DCR numbers deliberately trap. Caller register conventions must match r3 for DCR number and r4 for write value.

Test signals: DCR users reading/writing known registers, invalid-number bug handling, and successful link/export of `__mfdcr`/`__mtdcr` validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/dcr-low.S -->
