# sources/distributed-fs/ceph-client/arch/x86/lib/memmove_64.S

Purpose: implements 64-bit overlap-safe `memmove`/`__memmove` in noinstr text, with ERMS/FSRM alternatives and manual fallback loops.

Important APIs/functions: exports `__memmove` and aliases/exports `memmove`.

Control flow: saves original destination in `%rax`, detects overlap by comparing destination with source and source+count, and selects forward or backward copy. Forward path may use `rep movsb` for ERMS/FSRM or `rep movsq` for large aligned ranges; otherwise it uses 32-byte unrolled loops. Backward path similarly uses `std; rep movsq; cld` for aligned large copies or manual backward loops. Tail handlers cover 16-31, 8-15, 4-7, 2-3, and 1 byte.

State and persistence behavior: modifies destination memory safely for overlap and returns original destination. Temporarily sets direction flag only in backward `rep movsq` path and clears it before continuing.

Dependencies/integration points: core kernel memory API, x86 alternatives for ERMS/FSRM, noinstr validation, CFI annotations, and exported symbols.

Risks: overlap detection must be exact; otherwise memmove degenerates into corrupting memcpy behavior. Direction flag leakage would break later code. Alternative paths must preserve the same ABI and return value.

Test signals: memmove overlap tests with every relative offset and size boundary, ERMS/FSRM/non-ERMS CPU paths, DF-after-call tests, objtool noinstr checks, and sanitizer builds.
