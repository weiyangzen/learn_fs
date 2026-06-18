# sources/compression/zstd/tests/decodecorpus.c

## Purpose
`decodecorpus.c` is a synthetic zstd frame/block corpus generator and self-tester. It creates valid but randomized compressed frames, raw compressed blocks, optional dictionaries, and original outputs for decompressor fuzzing and regression tests.

## Important APIs, types, and global state
Core types include `frameHeader_t`, `cblockStats_t`, `frame_t`, `dictInfo`, and `genType_e`. Global buffers (`CONTENT_BUFFER`, `FRAME_BUFFER`, `LITERAL_BUFFER`, sequence buffers, FSE/HUF workspaces) hold generated content and compressed output. Command-line state is in `opts`, `g_displayLevel`, `g_maxDecompressedSizeLog`, and `g_maxBlockSize`. Random generation is driven by `RAND()`, `RAND_buffer*()`, `RAND_range()`, and `RAND_exp()`.

## Control flow and algorithms
Generation starts with `writeFrameHeader()`, then writes raw, RLE, or compressed blocks. Literal paths include `writeLiteralsBlockSimple()`, `writeHufHeader()`, and `writeLiteralsBlockCompressed()` with repeat-mode state in `frame->stats`. Sequence paths initialize and populate zstd internal sequence storage, choose symbol sets and FSE modes, then write sequence headers and bitstreams. `writeCompressedBlock()`, `writeBlock()`, `writeBlocks()`, and `writeChecksum()` assemble complete frames. Dictionary support uses `genRandomDict()` and `initDictInfo()` to create valid dictionary headers/content and to drive dictionary-based frame/block generation.

## Validation, I/O, and CLI integration
Self-test paths include `testDecodeSimple()`, `testDecodeStreaming()`, `testDecodeWithDict()`, and `testDecodeRawBlock()`, which compare decompressed bytes against `frame->srcStart`. `runTestMode()` repeatedly runs frame or block tests for a count or duration. File-generation paths are `generateFile()`, `generateCorpus()`, and `generateCorpusWithDict()`, writing `z%06u.zst`, optional originals, and optional dictionary files. `main()` parses `-p`, `-o`, `-s`, `-n`, `-t`, `-T`, verbosity, `--content-size`, `--use-dict=`, `--gen-blocks`, max-size limits, forced block/literal type, `--frame-header-only`, and `--no-magic`.

## Dependencies, risks, and test signals
The file directly includes internal zstd compression implementation and deprecated block decompression APIs, so it is tightly coupled to libzstd internals. Risks include global buffer bounds, option validation gaps (`--max-block-size-log` compares against a size constant after parsing a log), path length truncation, allocation failures, and format-spec drift. Strong test signals are successful self-test mode, generated corpora accepted by fuzz harnesses, and dictionary/raw-block round trips matching original buffers.
