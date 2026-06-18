# Chunk Research: sources/os/linux/linux-stable/fs/nls/nls_cp936.c lines 1-3984

## Scope

This chunk is the opening generated data section of the Linux NLS CP936/GB2312 conversion module. It contains the file header, kernel/NLS includes, and the beginning of the CP936 byte-sequence-to-Unicode mapping tables. There is no executable conversion logic in this line range; the runtime APIs are defined later in the same file.

## APIs And Dependencies

- Includes at lines 10-14 pull in module metadata, kernel primitives, string declarations, the NLS registration interface, and errno constants: `<linux/module.h>`, `<linux/kernel.h>`, `<linux/string.h>`, `<linux/nls.h>`, and `<linux/errno.h>`.
- The public API surface is not declared in this chunk. Adjacent downstream context shows these tables feed `page_charset2uni[]` at lines 4389-4422, then `char2uni()` at lines 11049-11085, and module registration through `struct nls_table` at lines 11088-11095.
- All symbols in this chunk are `static const wchar_t`, so they are translation-unit-local read-only lookup data. They become externally relevant only through the later `page_charset2uni` pointer table and the NLS callbacks.

## Data Tables

- Lines 16-3972 define complete `c2u_XX[256]` tables for CP936 lead bytes `0x81` through `0xF0`.
- Lines 3974-3984 start `c2u_F1[256]` and stop mid-definition; the rest of `c2u_F1` is in the next chunk.
- The line range contains 28,160 parsed `0xNNNN` entries, 19,885 of them nonzero. `0x0000` is used as an invalid/unmapped sentinel in these tables, not as a valid Unicode result for double-byte CP936 mappings.
- Main risk is table correctness: manual edits or lead-byte dispatch misalignment in later chunks would silently corrupt filename transcoding.

## Control Flow And State

No function bodies or branches appear in lines 1-3984. Downstream `char2uni()` indexes `page_charset2uni[ch]`, reads `charset2uni[cl]`, rejects `0x0000` as `-EINVAL`, and returns valid two-byte mappings.

The chunk has no mutable state, allocation, locking, reference counting, or I/O. It is static read-only kernel data.

## Cross-Chunk References

- Next chunk continues `c2u_F1` and defines remaining `c2u_F2` through `c2u_FE`, plus `page_charset2uni[256]`.
- Later chunks define reverse `u2c_XX[512]` tables and `page_uni2charset[256]`.
- Final logic appears near file end: `uni2char()`, `char2uni()`, `struct nls_table table`, module init/exit, and module metadata.