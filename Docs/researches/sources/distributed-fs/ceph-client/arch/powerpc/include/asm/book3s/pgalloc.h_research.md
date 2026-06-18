# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/pgalloc.h

Purpose: selects the correct Book3S page-table allocation header for 32-bit or 64-bit builds.

Important APIs/types/functions: includes either `asm/book3s/64/pgalloc.h` or `asm/book3s/32/pgalloc.h` based on architecture configuration.

Control flow: compile-time include dispatch only.

State and persistence: no state. It determines which allocation helpers are compiled into callers.

Dependencies and integration points: included by generic PowerPC pgalloc users that do not want to know the Book3S word size.

Risks: wrong config guards would include incompatible page-table allocation APIs. This wrapper must track directory layout and architecture symbols.

Test signals: build Book3S 32-bit and 64-bit configs and verify page-table allocation symbols resolve.
