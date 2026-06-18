# sources/distributed-fs/openafs/src/afs/AIX/osi_assem32.s

Purpose: 32-bit variant of the AIX RS/6000 assembly helpers.

Important APIs and functions: exports `get_toc` and `get_ret_addr`, using `.long` descriptor entries for procedure descriptors and TOC pointers.

Control flow: `get_toc` returns r2; `get_ret_addr` loads the caller's saved stack pointer from r1 and then the caller's saved link register at offset 8.

State and persistence: no persistent state or side effects.

Dependencies and integration: linked into 32-bit AIX kernel/client builds that need TOC-aware import resolution.

Risks and test signals: tied to 32-bit AIX ABI assumptions. A wrong descriptor width would break calls before C code runs; successful module load and `kluge_init` import completion are signals.
