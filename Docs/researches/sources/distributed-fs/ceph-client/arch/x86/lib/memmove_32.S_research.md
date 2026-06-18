# sources/distributed-fs/ceph-client/arch/x86/lib/memmove_32.S

Purpose: implements 32-bit `memmove`, including overlap-safe forward and backward copies optimized for small and large ranges.

Important APIs/functions: defines and exports `memmove`. It uses the 32-bit `-mregparm=3` convention: destination in `%eax`, source in `%edx`, count in `%ecx`, returning original destination in `%eax`.

Control flow: saves callee-saved registers and destination return value, selects forward copy when source is at or above destination, otherwise backward copy. Large aligned ranges may use `rep movsl`; smaller or unaligned ranges use 16-byte unrolled loops. Tail handlers cover 8-15, 4-7, 2-3, and 1 byte with overlapping loads/stores. Backward `rep movsl` sets DF and clears it before return.

State and persistence behavior: copies memory in place safely for overlapping regions. No globals. Temporarily changes direction flag in backward `rep movsl` path and restores it.

Dependencies/integration points: 32-bit x86 string library, compiler/runtime out-of-line `memmove`, and exported symbol consumers.

Risks: direction flag must always be cleared. Stack/register save/restore is essential because the implementation clobbers callee-saved registers. Overlap direction tests and tail addressing must be exact to avoid corruption.

Test signals: exhaustive memmove overlap tests around small sizes, large aligned/unaligned ranges, forward/backward paths, DF state validation after calls, and 32-bit build/link tests.
