# sources/distributed-fs/ceph-client/arch/sparc/prom/bootstr_32.c

Purpose: retrieves SPARC32 boot arguments from legacy Sun PROM interfaces.

Important APIs/functions: exposes `prom_getbootargs()`. Internal state is static `barg_buf[256]` and `fetched`.

Control flow: the first call gathers arguments based on `prom_vers`. PROM V0 concatenates `argv[1..7]` from the ROM vector with spaces, preserving buffer bounds. PROM V2/V3 copies the bootargs string from `pv_v2bootargs`. Later calls return the cached buffer to tolerate boot loader patches.

State and persistence: boot arguments are cached in a static buffer for the lifetime of boot. No external persistence.

Dependencies and integration points: depends on `romvec`, `prom_vers`, and early command-line setup. The result feeds generic kernel command-line parsing.

Risks: fixed 256-byte buffer can truncate long command lines. PROM V0 concatenation can leave a trailing space. Calling before `prom_init()` would dereference unset ROM state.

Test signals: boot PROM V0, V2, and V3 paths with empty, normal, and long arguments; verify command-line parsing and cached repeated calls.
