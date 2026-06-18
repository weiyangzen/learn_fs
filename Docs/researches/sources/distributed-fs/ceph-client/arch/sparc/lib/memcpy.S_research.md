# sources/distributed-fs/ceph-client/arch/sparc/lib/memcpy.S

Purpose: SPARC32 optimized `memcpy` and `memmove`.

Important APIs/functions: Exports `memcpy` and `memmove`; uses local macro `FUNC` for symbol definitions and multiple alignment tables.

Control flow: `memmove` detects overlap and uses reverse-copy when needed. `memcpy` aligns source/destination, uses dword/word copy tables for large aligned cases, handles non-aligned cases by shifting/combining words, and finishes with short/tail byte paths.

State and persistence: Mutates destination buffer; no persistent state.

Dependencies/integration: Includes `linux/export.h`; built for `CONFIG_SPARC32`.

Risks/test signals: Overlap handling, table jumps, and unaligned word assembly are risky. Test overlapping memmove, non-overlap memcpy, all alignments, tiny sizes, and randomized buffer comparisons.
