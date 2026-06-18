# sources/distributed-fs/ceph-client/tools/objtool/arch/powerpc/include/arch/special.h

Purpose: PowerPC special-section binary layout constants for exception table, jump labels, and alternatives.

Important APIs/types/functions: defines sizes and offsets for exception entries, jump entries, and alternative entries.

Control flow: none; read by generic special-section code.

State and persistence behavior: affects how special-section bytes become in-memory alternative records, which in turn influence validation graph paths.

Dependencies and integration points: tied to PowerPC kernel metadata struct layouts.

Risks: stale offsets create false or missing alternatives. PowerPC `special.c` currently aborts for main hooks, so these constants are only useful if generic special parsing is enabled with a complete implementation.

Test signals: future PowerPC alternative/jump-label objtool tests should verify parsed original/new offsets and lengths.
