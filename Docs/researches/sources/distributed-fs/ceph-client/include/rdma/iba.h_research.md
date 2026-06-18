# sources/distributed-fs/ceph-client/include/rdma/iba.h

Purpose: Generic InfiniBand Architecture field access layer for packed big-endian MAD and management structures. It lets generated field descriptors drive common get/set/copy helpers.

Important APIs/types/functions: `_iba_get8/16/32/64`, `_iba_set8/16/32/64`, `IBA_GET`, `IBA_SET`, `IBA_GET_MEM`, `IBA_SET_MEM`, `IBA_FIELD_BLOC`, `IBA_FIELD8_LOC`, `IBA_FIELD16_LOC`, `IBA_FIELD32_LOC`, `IBA_FIELD64_LOC`, and `IBA_FIELD_MLOC`. The 64-bit helpers use unaligned access because larger MAD fields may not be 8-byte aligned.

Control flow: Field macros describe a struct type, offset, mask, and width. `IBA_GET` advances to the field, endian-converts the containing unit, and extracts the mask. `IBA_SET` reads, clears, prepares, and writes the target bits while preserving unrelated bits. Memory helpers copy raw byte fields with width warnings.

State and persistence behavior: No owned state. Helpers mutate caller-provided wire buffers in place and preserve bits outside the requested field mask.

Dependencies and integration points: Uses Linux `FIELD_GET`, `FIELD_PREP`, `GENMASK`, endian helpers, unaligned access, `WARN_ON`, and `memcpy`. It is the base used by IBTA communication-management message descriptors.

Risks: Bad generated offsets or bit numbering silently corrupt protocol messages. `_IBA_SET_MEM` does not clear trailing bytes when input is shorter than the field, so callers should clear buffers first if stale bytes matter.

Test signals: Round-trip tests for byte/bit fields, unaligned 64-bit fields, short memory fields, and byte-for-byte MAD layout comparisons against spec examples.
