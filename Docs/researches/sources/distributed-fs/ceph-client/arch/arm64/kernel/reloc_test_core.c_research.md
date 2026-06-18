# sources/distributed-fs/ceph-client/arch/arm64/kernel/reloc_test_core.c

Purpose: this loadable module drives ARM64 relocation tests by calling assembly helpers that exercise absolute, MOVW, ADR/ADRP, and PREL relocation forms and comparing returned values against expected symbols.

Important APIs and state: `sym64_rel` is a real relocatable data symbol. `SET_ABS()` creates absolute symbols `sym64_abs`, `sym32_abs`, and `sym16_abs`. The `funcs[]` table names each relocation form, stores a function pointer to the assembly helper, and records the expected result. `reloc_test_init()` logs each result and pass/fail status; `reloc_test_exit()` is empty.

Control flow: module init prints a header, iterates the table, calls each helper, compares the return value with the expected absolute or relative address, and logs a detailed error for mismatches. The module still returns success, using logs as the test signal.

Dependencies and integration: pairs with `reloc_test_syms.S` for relocation-emitting code and with module loader relocation handling. It references `memstart_addr` for a far ADRP case.

Risks: expectations are architecture/linker-specific and validate relocation behavior rather than functional kernel logic. Since mismatches do not fail module load, automated test harnesses must parse logs or be extended to assert failure.

Test signals: `pr_info("pass")`/`"fail"` lines after loading the module. Coverage includes ABS64/32/16, signed and unsigned MOVW absolute relocations, ADRP near/far, ADR, and PREL64/32/16.
