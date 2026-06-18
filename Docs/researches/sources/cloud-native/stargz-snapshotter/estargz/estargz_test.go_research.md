## sources/cloud-native/stargz-snapshotter/estargz/estargz_test.go

Purpose: this focused unit test validates `Reader.ChunkEntryForOffset` offset-to-chunk selection for regular files represented by a first `reg` TOC entry and optional later `chunk` entries. It is a narrow guard around the reader's chunk lookup math.

Important APIs and helpers: `TestChunkEntryForOffset` drives table cases over `fileSize`, requested offset, expected hit/miss, expected `ChunkOffset`, and expected `ChunkSize`. `regularFileReader` builds a minimal in-memory `Reader` with `m` and `chunks` maps rather than constructing a tar/eStargz blob. The helper emits a single regular entry when the file fits in one chunk and additional `chunk` entries when it spans chunks.

Control flow: each case builds a fake reader, calls `ChunkEntryForOffset(name, reqOffset)`, checks the boolean result, and compares chunk metadata only for hits. Boundary cases cover offsets at chunk starts and exactly at EOF for one- and two-chunk files.

State and persistence: no persistent state is used. The test constructs transient `TOCEntry` pointers and reader maps; pointer reuse intentionally models the first `reg` entry becoming the first chunk.

Dependencies and integration points: this test depends on package-internal `Reader`, `TOCEntry`, and `ChunkEntryForOffset` behavior from `estargz.go`. It complements the larger compression suite in `testutil.go`, which validates chunk lookup against real archives.

Risks: coverage is limited to simple same-sized chunk boundaries and does not cover negative offsets, non-zero `InnerOffset`, sparse/multi-payload chunks, missing `chunks` map entries, or offsets inside last partial chunks. It also assumes `ChunkEntryForOffset` interprets EOF as no hit.

Test signals: strong regression signal for basic offset arithmetic; weak signal for full archive parsing because it bypasses footer, TOC parse, and decompression paths.
