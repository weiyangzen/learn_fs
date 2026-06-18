# sources/distributed-fs/ceph-client/tools/objtool/include/objtool/endianness.h

Purpose: Centralizes objtool byte-swap decisions for host versus target ELF endianness.

Important APIs/types/functions: `need_bswap`, `_OBJTOOL_ENDIANNESS_H`, `__bswap_if_needed`.

Control flow: `need_bswap()` compares ELF data encoding to host byte order; `__bswap_if_needed` conditionally swaps scalar fields.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Uses GElf headers and libc byte-swap support through objtool ELF code.

Risks: Wrong encoding detection corrupts relocation fields and section metadata for cross-endian analysis.

Test signals: Read and mutate big-endian and little-endian test ELFs on the host.

Source coverage: researched from the complete local file (38 lines, 1086 bytes).
