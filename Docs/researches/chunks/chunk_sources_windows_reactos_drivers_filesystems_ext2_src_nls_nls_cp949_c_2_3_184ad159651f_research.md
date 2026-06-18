# Chunk Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp949.c lines 3838-7873

## Scope

This chunk is the middle data section of the generated CP949/UHC NLS conversion table used by the ReactOS ext2 filesystem driver copy of a Linux NLS module. It is in subset A because `sources/windows/reactos` is included by `Docs/research_subset_a.md`.

The span contains static lookup data only. It starts inside `c2u_ED[256]`, completes the remaining high CP949 byte-to-Unicode pages through `c2u_FD[256]`, defines the byte-to-Unicode dispatch table, then defines Unicode-to-CP949 reverse lookup pages from `u2c_01[512]` through `u2c_74[512]` plus the beginning of `u2c_75[512]`.

## APIs And Data Structures

- No public API, exported symbol, callback, or module registration function is declared in this chunk.
- The visible data is file-local static storage consumed by later NLS callbacks:
  - `char2uni()` uses `page_charset2uni[ch]` to map a CP949 lead byte plus trail byte into a `wchar_t`.
  - `uni2char()` uses `page_uni2charset[ch]` to map a Unicode high byte to a 512-byte reverse page and emit a two-byte CP949 sequence.
- `c2u_ED[256]` is partially visible from line 3838 to its close at line 3858. The chunk then fully defines `c2u_EE[256]` through `c2u_FD[256]`.
- `page_charset2uni[256]` is the first-level decoder index. It maps lead bytes `0x81..0xC8`, skips `0xC9`, maps `0xCA..0xFD`, and leaves other lead bytes as `NULL`.
- Complete reverse pages in this chunk include `u2c_01`, `u2c_02`, `u2c_03`, `u2c_04`, `u2c_11`, `u2c_20` through `u2c_26`, `u2c_30` through `u2c_33`, and `u2c_4E` through `u2c_74`. The chunk ends after the first entries of `u2c_75`.

## Control Flow

There is no executable control flow in this line range: no functions, branches, loops, locking, allocation, or I/O.

Runtime behavior is table-driven by code outside this chunk: `char2uni()` selects `page_charset2uni[first]` and rejects `0x0000` slots; `uni2char()` selects `page_uni2charset[high]` and rejects `{0x00, 0x00}` pairs.

## State And Dependencies

All visible state is immutable static lookup data with internal linkage. There is no per-volume, per-file, or per-call mutable state in this chunk.

`page_charset2uni[]` depends on `c2u_81` through `c2u_EC` from the previous chunk and on `c2u_ED` through `c2u_FD` at this chunk boundary. The `u2c_*` reverse pages depend on a later `page_uni2charset[]` dispatch table to become reachable from `uni2char()`.

## Risks And Edge Cases

- The arrays are positional generated data. Any inserted, deleted, or reordered literal silently changes filename encoding behavior for CP949-mounted ext2 paths.
- Chunk boundaries split declarations: `c2u_ED[256]` starts before this range, and `u2c_75[512]` continues after it.
- Sentinel zeros are semantically meaningful: `0x0000` rejects a two-byte input sequence; `{0x00, 0x00}` rejects a Unicode-to-CP949 mapping.
- The `page_charset2uni[]` omission of `0xC9`, `0xFE`, and `0xFF` appears deliberate.
- CP949 includes UHC and compatibility mappings, including `U+F9xx` and `U+FAxx` values.

## Cross-Chunk References

- The previous chunk defines the file prologue, earlier `c2u_81` through most of `c2u_ED`, and generated-table context.
- This chunk defines `page_charset2uni[]`, which references byte-to-Unicode pages from both the previous chunk and this chunk.
- The next chunk completes `u2c_75`, defines remaining reverse pages, builds `page_uni2charset[]`, adds case conversion tables, and defines `uni2char()`, `char2uni()`, the `struct nls_table`, init/exit registration, and module metadata.
- This report is only for chunk 2 and intentionally does not create or merge the final per-file report.