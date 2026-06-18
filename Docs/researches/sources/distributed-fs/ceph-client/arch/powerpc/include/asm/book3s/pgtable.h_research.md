# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/pgtable.h

Purpose: selects the correct Book3S page-table definition header for 32-bit or 64-bit PowerPC builds.

Important APIs/types/functions: includes `asm/book3s/64/pgtable.h` for 64-bit and `asm/book3s/32/pgtable.h` for 32-bit.

Control flow: compile-time include dispatch only.

State and persistence: no state; it exposes the appropriate page-table ABI to common code.

Dependencies and integration points: used by common PowerPC MM code and architecture-independent mm includes.

Risks: a bad include selection would mix incompatible PTE formats and table geometry. Header ordering must avoid recursive include issues.

Test signals: 32-bit and 64-bit Book3S builds, plus compile coverage for common MM users including swap, mprotect, and page-table allocation.
