# sources/distributed-fs/ceph-client/arch/mips/include/asm/paccess.h

Purpose: provides protected MIPS memory access helpers for addresses that may raise instruction or data bus errors, such as optional devices or missing memory.

Important APIs/types/functions: public macros `put_dbe(x, ptr)` and `get_dbe(x, ptr)` wrap size-specific protected access. Internal macros `__get_dbe`, `__get_dbe_asm`, `__put_dbe`, and `__put_dbe_asm` generate inline assembly for 1-, 2-, 4-, and 8-byte loads/stores. Externs include `handle_ibe`, `handle_dbe`, `__get_dbe_unknown`, `__put_dbe_unknown`, and `search_dbe_table`. `__PA_ADDR` selects `.word` or `.dword` exception-table entries by ABI width.

Control flow: a protected access emits an assembly load/store at label 1, sets error to zero on success, and records a fixup target in `__dbe_table`. If a DBE occurs, exception handling searches the table and jumps to the fixup, which sets `-EFAULT`, zeroes a failed load result, and resumes after the access.

State and persistence: no persistent state is maintained by the macros. The compiled binary contains `__dbe_table` metadata used by exception handling. The accessed memory/device can of course have side effects on successful stores.

Dependencies and integration points: includes `linux/errno.h`, uses MIPS exception-table/fixup sections, and integrates with architecture DBE/IBE handlers and `search_dbe_table`.

Risks: only sizes 1, 2, 4, and 8 are supported; other sizes call unknown stubs. Store side effects may partially occur if a bus error happens late. The large fake struct and `"o"` constraints are low-level compiler tricks that must not be casually rewritten. Correct operation requires exception handlers and linker sections to be wired.

Test signals: platform tests should probe valid and invalid device addresses, checking zero return and `-EFAULT` paths. Build tests should cover 32-bit and 64-bit table entry sizes.
