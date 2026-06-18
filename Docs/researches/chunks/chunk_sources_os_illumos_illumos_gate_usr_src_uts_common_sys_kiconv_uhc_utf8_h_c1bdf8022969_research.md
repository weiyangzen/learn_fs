# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_uhc_utf8.h lines 16910-17136

## Scope

- Repository subset: `Docs/research_subset_a.md`; `sources/os/illumos/illumos-gate` is in scope.
- Source span read completely: lines 16910-17136 of `usr/src/uts/common/sys/kiconv_uhc_utf8.h`.
- This is chunk 3 of an oversized header. It covers the final entries of the kernel UHC-to-UTF-8 mapping table and the file's closing conditional guards.

## APIs and Data Structures

- This chunk does not add public functions, macros, typedefs, or callable APIs.
- The table declaration is before this chunk: `static kiconv_table_array_t kiconv_uhc_utf8[]`.
- The maximum mapping macro is also before this chunk: `KICONV_UHC_UTF8_MAX` is `17047`.
- `kiconv_table_array_t` comes from `kiconv_cck_common.h` and contains a `uint32_t key` plus `uchar_t u8[4]`.
- This chunk contributes 218 mapping rows, from key `0xFBE1` at line 16910 through key `0xFDFE` at line 17127.

## Control Flow

- There is no executable control flow in this span. Runtime conversion behavior is driven by code elsewhere that includes this header and searches or indexes the static table.
- The chunk closes the `kiconv_uhc_utf8[]` initializer at line 17128.
- It then closes `_KERNEL`, the C++ `extern "C"` wrapper, and the include guard `_SYS_KICONV_UHC_UTF8_H`.

## State and Dependencies

- State is compile-time static initializer data. Under `_KERNEL`, every translation unit including this header can receive a private `static` copy of the table.
- Dependencies are the earlier table declaration, `kiconv_table_array_t`, kernel typedefs such as `uint32_t` and `uchar_t`, and external kiconv conversion routines that consume the table.
- The table is licensed through file-level CDDL and Unicode data notices outside this chunk.

## Risks and Cross-Chunk References

- Correctness risk is data integrity: wrong byte literals, missing entries, duplicate keys, or unsorted keys can silently corrupt UHC-to-UTF-8 conversion.
- The full table row count was verified as 17,047 entries, matching `KICONV_UHC_UTF8_MAX`; changes in any chunk must keep that macro synchronized.
- Prior chunks contain the header preamble, macro, table declaration, and earlier `kiconv_uhc_utf8[]` rows. This chunk owns the terminal rows and syntactic closure.
- No final per-file report was created for this chunk.