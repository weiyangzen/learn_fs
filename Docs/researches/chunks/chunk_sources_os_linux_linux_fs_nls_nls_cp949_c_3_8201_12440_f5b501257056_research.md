# Chunk Research: sources/os/linux/linux/fs/nls/nls_cp949.c lines 8201-12440

## Scope

This report covers only `sources/os/linux/linux/fs/nls/nls_cp949.c` lines 8201-12440 in learn_fs subset A (`Docs/research_subset_a.md`). I read the requested range completely and used adjacent context to identify the enclosing conversion-table declarations and their consumers. The chunk is immutable CP949 Unicode-to-charset lookup data, not executable control code.

## APIs And Data Surface

This chunk contributes `static const unsigned char u2c_*[512]` tables used by the file-local `uni2char()` callback registered with the Linux NLS core. Each table is keyed by the high byte of a Unicode code point; the low byte indexes a pair of bytes at `cl * 2` and `cl * 2 + 1`. A `{0x00, 0x00}` pair means there is no CP949 mapping for that Unicode code point.

The chunk begins inside `u2c_7A` and includes its tail through line 8261. It then contains complete tables `u2c_7B` through `u2c_C5`, and starts `u2c_C6` at line 12405. The requested range ends inside `u2c_C6` after entries for low-byte range `0x84-0x87` at line 12440.

## Control Flow

There are no functions, branches, loops, allocations, locking operations, I/O calls, or module side effects in this chunk. Runtime control flow is indirect through adjacent `uni2char()` code, which selects `page_uni2charset[ch]`, copies two bytes from the selected table, and rejects zero-pair mappings with `-EINVAL`.

CP949-to-Unicode conversion uses separate `c2u_*` tables and `page_charset2uni[]` from earlier chunks.

## State And Dependencies

All state in this range is file-local, read-only, and initialized at compile time. There is no mutable state and no synchronization requirement.

The chunk depends on the later `page_uni2charset[256]` dispatcher, which references the Unicode pages defined here, and on `uni2char()` for bounds checks and zero-pair rejection. Kernel-facing integration comes from the adjacent `struct nls_table table`, exposed as charset `cp949` with alias `euc-kr`.

## Risks And Invariants

The critical invariant is the fixed 512-byte shape: each table must contain 256 two-byte mappings, and offsets are positional. Sparse ranges must use explicit `0x00, 0x00` pairs.

A single incorrect byte changes transcoding semantics and can create non-round-tripping behavior against the earlier `c2u_*` tables. Boundary risk is high because this chunk begins inside `u2c_7A` and ends inside `u2c_C6`; both require adjacent chunks for full validation.

## Cross-Chunk References

Previous chunk: defines the start of `u2c_7A` and earlier reverse-conversion tables.

Next chunk: continues `u2c_C6`, then defines later `u2c_*` tables, `page_uni2charset[]`, case tables, `uni2char()`, `char2uni()`, the NLS table, and module registration.