# sources/distributed-fs/ceph-client/tools/perf/arch/s390/include/dwarf-regs-table.h

Purpose: Defines the arch DWARF register number to register-name table used by perf register decoding and unwind display.

Important APIs/types/functions: `S390_DWARF_REGS_TABLE_H`, `REG_DWARFNUM_NAME`, `s390_regstr_tbl`.

Control flow: Perf includes the table in architecture register helpers to translate DWARF register numbers into user-visible names.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on architecture DWARF numbering and perf unwind/register code.

Risks: Wrong indices mislabel callchains, probe registers, and unwind diagnostics.

Test signals: Compare arch DWARF register names against ABI documentation and unwind sample output.

Source coverage: researched from the complete local file (73 lines, 2086 bytes).
