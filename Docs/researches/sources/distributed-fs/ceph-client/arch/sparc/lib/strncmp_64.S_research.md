# sources/distributed-fs/ceph-client/arch/sparc/lib/strncmp_64.S

Purpose: compact SPARC64 assembly implementation of `strncmp`.

Important APIs/functions: `ENTRY(strncmp)` returns zero for non-positive length, otherwise compares bytes from `%o0` and `%o1`. It uses `lduba [%o0] (ASI_PNF)` for the initial source load and exports `strncmp`.

Control flow: after a `brlez` zero-length guard, it loads one byte, increments both pointers, exits on NUL or mismatch, decrements the count, and loops while bytes remain. The return value is `%o3 - %o4`; zero-count returns clear `%o0`.

State and persistence: no persistent state and no writes. It reads memory only.

Dependencies/integration: includes `linux/export.h`, `linux/linkage.h`, and `asm/asi.h`. It plugs into kernel string calls for SPARC64.

Risks: the first load uses a non-faulting primary ASI while later loads use regular `ldub`; this asymmetry should match intended kernel address behavior. Count is decremented after comparison, so boundary tests are important. It is byte-wise and simple but not exception-table protected.

Test signals: generic string selftests for `n <= 0`, exact-length equality, mismatch at last byte, NUL before count, high-bit byte ordering, and invalid/unmapped first pointer behavior if non-faulting ASI semantics are relied on.
