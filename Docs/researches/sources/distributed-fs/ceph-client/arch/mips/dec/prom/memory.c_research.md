# sources/distributed-fs/ceph-client/arch/mips/dec/prom/memory.c

Purpose: discovers DECstation physical memory before normal memory management.

Important APIs: `prom_meminit(u32 magic)` selects PMAX probing or REX bitmap parsing. `prom_free_prom_memory()` frees unused low PROM memory after boot while optionally reserving Lance memory on IOASIC systems.

Control flow: non-REX PMAX probing installs `genexcept_early`, reads one byte at 4 MB increments in KSEG1 until an exception sets `mem_err`, restores the old handler, and adds RAM to memblock. REX path asks `rex_getbitmap()` for a bitmap and converts contiguous fully-available page runs into memblock ranges.

State and integration: `mem_err` is volatile probe state. Resulting memblock ranges become the platform RAM map.

Risks and test signals: PMAX probing assumes at least 4 MB and an upper bound below 480 MB. REX conversion ignores partial bitmap bytes. Test memory size reporting on PMAX and REX machines; verify low PROM memory is freed only after it is safe.
