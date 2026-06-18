# sources/compression/zstd/lib/compress/zstd_compress_sequences.c

## Purpose
Implements FSE table selection, FSE table construction, entropy cost estimation, and bitstream encoding for zstd sequence sections. It decides whether literal-length, match-length, and offset-code streams should use RLE, default, repeat, or newly compressed FSE tables, then encodes sequences in reverse order into a bitstream.

## Important APIs, Types, And Functions
`ZSTD_selectEncodingType()` selects `set_rle`, `set_basic`, `set_repeat`, or `set_compressed` for a symbol stream using frequency counts, prior repeat mode, default distributions, sequence count, strategy, and estimated costs. `ZSTD_buildCTable()` materializes the selected FSE table and writes any required normalized-count header bytes. `ZSTD_encodeSequences()` is the public sequence body encoder with optional dynamic BMI2 dispatch.

Cost helpers include `ZSTD_fseBitCost()`, `ZSTD_crossEntropyCost()`, `ZSTD_NCountCost()`, `ZSTD_entropyCost()`, `ZSTD_getFSEMaxSymbolValue()`, and `ZSTD_useLowProbCount()`. `ZSTD_BuildCTableWksp` overlays the entropy workspace for normalization and table building.

## Control Flow
Encoding-type selection first handles the all-one-symbol case as RLE, with a small special case favoring default tables for two or fewer symbols when allowed. For strategies below `ZSTD_lazy`, it uses heuristics to prefer repeat or default tables for small/cheap streams. For lazy and stronger strategies, it estimates basic, repeat, and newly compressed costs and chooses the cheapest valid mode. A compressed-table choice moves repeat mode to `FSE_repeat_check`.

`ZSTD_buildCTable()` then follows the selected mode: RLE builds an RLE table and writes one symbol byte, repeat copies the previous table, basic builds from default norms without output bytes, and compressed normalizes counts, writes an NCount header, and builds a new table. The compressed path may reduce the last symbol count by one to match zstd's sequence coding convention.

`ZSTD_encodeSequences_body()` initializes FSE states from the last sequence, writes raw extra bits for that last sequence, then walks sequences backward. For each sequence it FSE-encodes offset/match/literal symbols and writes literal-length, match-length, and offset extra bits with careful flush scheduling for 32-bit and 64-bit bit accumulators. Long offsets are split so the bit accumulator never overflows. Finally it flushes the three FSE states and closes the bitstream.

## State And Persistence
The file mutates FSE repeat modes passed by pointer and writes `nextCTable` instances that persist into the next block's entropy state. `ZSTD_buildCTable()` may copy `prevCTable` for repeat mode. The code tables (`llCodeTable`, `mlCodeTable`, `ofCodeTable`) are read from the sequence store and not owned here. The entropy workspace is temporary and reused by callers.

## Dependencies And Integration Points
It includes `zstd_compress_sequences.h`, which brings in FSE and compression internals. It depends on common FSE bit-cost, normalized-count, bitstream, and default distribution tables (`LL_defaultNorm`, `ML_defaultNorm`, `OF_defaultNorm`, `LL_bits`, `ML_bits`). It integrates with entropy-stat building in other compression files and with `zstd_compress_superblock.c` for sub-block sequence emission.

## Risks And Edge Cases
The encoder depends on reverse-order sequence emission and exact bit flush thresholds; changes can break decoder compatibility. Repeat table reuse must be rejected when a previous CTable cannot represent a counted symbol or has zero probability for a used symbol. `ZSTD_crossEntropyCost()` assumes `accuracyLog <= 8` and valid non-zero norm values. The compressed-table path mutates `count` by decrementing the last symbol in some cases, so callers must provide a mutable count buffer and expect that adjustment.

Long offsets are sensitive on 32-bit accumulators and when `windowLog > STREAM_ACCUMULATOR_MIN`. The intentional unsigned-underflow loop over `size_t n=nbSeq-2; n<nbSeq; n--` requires `nbSeq > 0`, which callers ensure by writing a separate zero-sequence header path.

## Test Signals
Round-trip coverage should include zero, one, and many sequences; RLE/default/repeat/compressed table modes for LL/ML/OF; repeat-table reuse after dictionaries; high-window long offsets; 32-bit builds; dynamic BMI2 and non-BMI2 paths; and fuzz cases around tiny destination capacities. Compatibility tests should include older decoder guard cases through the superblock path.
