# sources/distributed-fs/ceph-client/tools/objtool/arch/x86/include/arch/cfi_regs.h

Purpose: x86 CFI register numbering for objtool stack validation and ORC output.

Important APIs/types/functions: defines CFI IDs for `AX`, `CX`, `DX`, `BX`, `SP`, `BP`, `SI`, `DI`, `R8` through `R15`, `RA`, and `CFI_NUM_REGS`.

Control flow: none; constants only.

State and persistence behavior: these constants index saved register state and are serialized indirectly into ORC metadata through x86 ORC mapping.

Dependencies and integration points: consumed by generic `cfi.h`, x86 decoder, x86 ORC writer, and stack validation in `check.c`.

Risks: ordering must match `arch_reg_name`, decoder ModRM register numbering, and ORC mappings. Any mismatch corrupts validation and unwind output.

Test signals: stack validation and ORC dumps for x86 should report expected SP/BP/RA behavior across standard prologues and epilogues.
