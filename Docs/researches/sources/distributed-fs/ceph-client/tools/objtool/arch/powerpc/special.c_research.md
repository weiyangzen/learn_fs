# sources/distributed-fs/ceph-client/tools/objtool/arch/powerpc/special.c

Purpose: placeholder PowerPC special-section hooks.

Important APIs/types/functions: `arch_support_alt_relocation()` and `arch_find_switch_table()` call `exit(-1)`. `arch_cpu_feature_name()` returns `NULL`.

Control flow: any attempt to validate alternative relocation support or find switch tables through these hooks terminates the process.

State and persistence behavior: no persistent writes. It prevents unsupported paths from silently producing bad results.

Dependencies and integration points: compiled into the generic special/jump-table pipeline when building objtool for PowerPC.

Risks: hard exits are hostile for diagnostics and can surprise new objtool actions. Full PowerPC support requires real implementations before enabling alternatives or dynamic jump-table validation.

Test signals: tests should ensure current PowerPC workflows avoid these hooks, and future feature work should replace hard exits with deterministic support or graceful errors.
