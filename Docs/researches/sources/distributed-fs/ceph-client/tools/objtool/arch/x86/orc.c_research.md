# sources/distributed-fs/ceph-client/tools/objtool/arch/x86/orc.c

Purpose: x86 ORC metadata conversion, writing, and dump formatting.

Important APIs/types/functions: `init_orc_entry()` maps generic CFI to x86 `struct orc_entry`; `write_orc_entry()` stores entries, byte-swaps offsets when needed, and emits IP relocations; `orc_print_dump()` formats ORC rows.

Control flow: handles null/undefined/end-of-stack CFI early, maps call/regs hint types, maps many CFA bases (`AX`, `DX`, `SP`, `BP`, `DI`, `R10`, `R13`, indirect SP/BP), maps BP recovery state, then writes offsets.

State and persistence behavior: modifies generated ORC section data and relocation section entries. Persistent changes are committed by shared ELF writing.

Dependencies and integration points: tied to x86 ORC kernel ABI, generic ORC creation, CFI state from `check.c`, and endian helpers.

Risks: only BP is tracked as a saved frame register in the ORC entry; unsupported CFA bases produce hard errors. Offset byte-swapping must stay consistent with target endianness.

Test signals: `objtool --orc --dump=orc` should show correct CFA/BP mapping for standard frames, DRAP cases, interrupt/reg hints, indirect SP/BP hints, and undefined/end entries.
