<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/charts.cc -->
# sources/distributed-fs/lizardfs/src/common/charts.cc

## Purpose

This legacy subsystem stores rolling time-series statistics and renders them as binary data, CSV, or indexed PNG charts.

## Important APIs, Types, and Functions

Public functions include `charts_init()`, `charts_term()`, `charts_add()`, `charts_store()`, `charts_get()`, `charts_datasize()`, `charts_makedata()`, `charts_make_csv()`, `charts_get_csv()`, `charts_make_png()`, and `charts_get_png()`. Important internals are fixed constants `LENG=950`, four ranges, static `series`, `pointers`, `timepoint`, chart buffers, PNG templates, optional zlib stream, `charts_load()`, old-format importers, `charts_filltab()`, `charts_makechart()`, and CRC/compression helpers.

## Control Flow

Initialization copies chart definitions, allocates fixed ring buffers, loads prior stats from disk, initializes time pointers, advances empty current slots, and initializes zlib if available. `charts_add()` maps timestamps into one-minute, six-minute, thirty-minute, and daily ranges, rolling pointers and aggregating values by add/max mode. Rendering fills display arrays, scales axes, draws chart pixels/text, packs 4-bit indexed pixels, compresses or fake-compresses, and emits PNG or CSV.

## State and Persistence Behavior

The file uses extensive process-global mutable state. `charts_store()` persists a binary stats file containing version, length, chart names, timepoint, and ring data. `charts_load()` restores matching names and imports older three/four-range formats.

## Dependencies and Integration Points

It depends on zlib when available, CRC helpers, datapack endian helpers, filesystem current-directory helpers, logging, and the definitions supplied by master/chunkserver stats code.

## Risks and Edge Cases

The subsystem is not thread-safe; PNG/CSV buffers are singletons. File IO uses fixed records and partial-write errors leave truncated files. Calculation definitions are stack-machine programs without strong validation. Large values require overflow mitigation during scaling. Date/time handling mixes localtime/gmtime and optional GMT offset behavior.

## Test Signals

Strong signals would include persistence round trips, old-format imports, chart id validation, CSV timestamp checks across ranges, PNG CRC validation, zlib/no-zlib builds, and concurrent render/add protection if used from multiple threads. No direct unit test is present in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/charts.cc -->
