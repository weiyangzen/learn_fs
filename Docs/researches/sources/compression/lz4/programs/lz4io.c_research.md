# sources/compression/lz4/programs/lz4io.c

Purpose: core file/stream backend for LZ4 CLI operations: frame and legacy compression, decompression, sparse output, dictionaries, metadata preservation, multithreaded chunking, pass-through, and `--list`.

Important APIs/functions: implements `LZ4IO_defaultPreferences()`, preference setters, single/multiple compression and decompression APIs, hidden legacy compression APIs, and `LZ4IO_displayCompressedFilesInfo()`. Internal structures include `LZ4IO_prefs_s`, `cRess_t`, `dRess_t`, `WriteRegister`, `ReadTracker`, buffer pools, and frame info summaries.

Control flow: compression opens files, prepares LZ4F prefs and dictionaries, selects MT or ST path, writes headers/blocks/end marks, preserves metadata, optionally removes source, and reports timing. Decompression selects decoder by magic number, handles LZ4F/legacy/skippable/pass-through streams, writes sparse output unless testing, preserves metadata, and processes concatenated streams. Listing scans frame headers and skips payload blocks for summaries.

State and persistence: global display/timing state controls progress; `g_magicRead` bridges legacy stream detection; static frame counters track concatenation. Filesystem effects include output creation/truncation, sparse seeks, chmod/chown/timestamp copying, and optional deletion.

Dependencies/integration: depends on platform/time/util/config headers, LZ4/LZ4HC/LZ4F/xxHash libraries, and `threadpool.h`; called by `lz4cli.c`.

Risks: many error paths terminate with `exit()`; MT paths require strict buffer/job lifetime discipline; disabling checksums weakens validation; sparse writes rely on seek support; list mode does not fully decode payloads.

Test signals: exercised by CLI round trips, dictionary/content-size/sparse/skippable/legacy/huge-file/list tests, valgrind, frametest/fuzzer, `checkFrame`, and decompression partial tests.
