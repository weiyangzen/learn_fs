# Chunk Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp949.c lines 7874-11936

## Scope

This report covers only `sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp949.c` lines 7874-11936 in learn_fs subset A (`Docs/research_subset_a.md`). I read the requested range completely and used adjacent context only to identify enclosing declarations and the later lookup dispatch/consumer functions. The chunk is generated/static CP949 Unicode-to-charset lookup data, not filesystem control logic.

## APIs And Data

This chunk contributes file-local `static unsigned char u2c_*[512]` tables used by the NLS `uni2char` path:

- Starts inside `u2c_75`, covering entries for low-byte offsets `0x34-0xFF`; the declaration begins before this chunk at line 7860.
- Fully defines pages `u2c_76` through `u2c_BE`, with sparse and dense 512-byte mapping arrays.
- Starts `u2c_BF` at line 11929 and covers entries through low-byte offsets `0x18-0x1B`; the rest continues in the next chunk.

Each table represents one Unicode high-byte page. A Unicode code point `0xHHLL` maps through `u2c_HH[LL * 2]` and `u2c_HH[LL * 2 + 1]` to a two-byte CP949 sequence. `0x00, 0x00` marks an unmapped code point.

## Control Flow

There are no functions, loops, conditionals, calls, allocation, locking, or I/O in this chunk. Runtime behavior is indirect: later `uni2char()` indexes `page_uni2charset[ch]`, then reads the two-byte pair from the selected `u2c_*` table, returning `-EINVAL` when the pair is all zero and `-ENAMETOOLONG` when the caller's output buffer cannot hold the result.

## State And Dependencies

The data is static internal translation state for the ReactOS ext2 NLS table named `cp949`. It is consumed by `page_uni2charset[256]` later in the same file, which references this chunk's pages `u2c_75` through `u2c_BF`. The exported NLS surface is the later `struct nls_table table`, whose `.uni2char` callback depends on these arrays.

Several arrays in this generated section are sparse and rely on C zero-initialization for omitted trailing entries. The dense Hangul pages beginning at `u2c_AC` contain many nonzero CP949 pairs, including both standard KS X 1001-style `0xB0..0xBB` byte ranges and CP949 extension byte ranges such as `0x81..0x96`.

## Risks

The primary risk is silent filename conversion error: a single wrong byte pair maps a Unicode character to the wrong CP949 sequence, while a stray `0x00, 0x00` makes a valid character unencodable. Because this data participates in filename NLS conversion, such errors can cause lookup mismatches, inaccessible names, or non-round-tripping directory entries rather than obvious control-flow failures.

The table shape is also fragile. Every page must remain exactly 512 addressable bytes because `uni2char()` indexes by `cl * 2` without per-page bounds checks. File-scope zero-fill makes short initializers safe, but moving these tables to automatic storage or generated binary blobs would need explicit padding.

## Cross-Chunk References

Previous chunks define earlier `u2c_*` pages and the beginning of `u2c_75`; this chunk finishes `u2c_75`. The next chunk continues `u2c_BF` and later pages through the final `page_uni2charset` pointer table. The later dispatch table at lines 13755-13788 references all pages from this chunk, and `uni2char()` at lines 13862-13890 is the direct consumer.