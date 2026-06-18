# Group Research: group_1632_plan9_sources_os_plan9_plan9_sys_src_cmd_venti_srv_buildindex_c_sou_3d4e26e157da

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/buildindex.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/buildindex.c

Rebuilds a Venti index from arena contents in place. It loads a Venti config, optionally resets and rebuilds the Bloom filter, reopens arena partitions read-only for safety, initializes a disk block cache, starts one worker per selected index section, and starts arena-partition workers that scan clump directories.

The rebuild pipeline is organized around score-to-bucket routing. `arenapartproc()` walks each arena's `ClumpInfo` records backward, reconstructs `IEntry` records from clump metadata and arena-map addresses, skips `VtCorruptType`, marks Bloom bits, and sends entries to the responsible `ISect` worker.

`isectproc()` performs a three-pass external sort/rebucket operation over each index section: first sprays incoming entries into large sequential groups, then optionally repartitions them into minibuffers with `IPool`, then sorts each minibuffer and writes final `IBucket` blocks. Helpers convert scores to relative buckets, buckets to disk offsets, and offsets back to buckets.

Important behaviors include optional `-i` selection of index sections, `-b` Bloom rebuild, `-M` index memory budget splitting per section, and optional zeroing of unused bucket ranges. The tie-break sort prefers higher index addresses for duplicate scores, assuming lower-address duplicates may be corruption artifacts.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/buildindex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/checkarenas.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/checkarenas.c

Implements `checkarenas`, a normal arena-partition checker and optional fixer. It opens one arena partition, initializes its `ArenaPart`, and checks either all arenas or selected names.

`checkarena()` optionally rescans from the beginning (`-a`) by clearing in-memory stats, then repeatedly calls `syncarena()` until no header update is reported. It compares recomputed `memstats` with the old values and reports incorrect arena header fields.

With `-f`, it copies corrected `memstats` into `diskstats`, writes the arena trailer with `wbarena()`, and flushes the disk cache. Without `-f`, it sets global `readonly`. Verbose modes print arena and partition summaries and final stats.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/checkarenas.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/checkindex.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/checkindex.c

Implements `checkindex`, which rebuilds a sorted expected index stream from arenas into a temporary partition, then compares expected buckets against the on-disk index.

`checkbucket()` loads the actual bucket from the correct `ISect`, compares packed entries in sorted order, and reports missing, extra, and wrong-address entries. `checkindex()` uses `IEStream` and `buildbucket()` to generate expected buckets and can also check zero/empty buckets unless `-Z` is used.

`checkbloom()` compares the live Bloom filter with a freshly generated one, counting spurious and missing bits. With `-f`, it writes the rebuilt Bloom filter back when needed; otherwise missing bits are fatal.

The command loads the Venti config, optional existing Bloom filter, initializes enough disk cache for arenas and index sections, builds raw sorted entries with `sortrawientries()`, and fails if index or Bloom discrepancies remain.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/checkindex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/clump.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/clump.c

Provides clump write and read primitives. A Venti clump is the immutable on-disk record containing a header plus compressed or uncompressed lump data.

`storeclump()` validates size and type, optionally checks the caller-provided score, compresses with `whackblock()`, fills a `Clump` header, appends the clump through `writeiclump()`, and returns an `IAddr` suitable for indexing.

`clumpmagic()` reads the clump magic at an arena-relative address. `loadclump()` reads enough arena blocks, unpacks the clump header, rejects corrupt-marker clumps, reads more data if the caller's block estimate was too small, decompresses when needed, and optionally verifies score and type.

The file bridges raw arena append storage and score-address index records, with SHA1 score verification as the main integrity check.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/clump.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/clumpstats.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/clumpstats.c

Implements `clumpstats`, a read-only utility that summarizes stored clumps by uncompressed size and Venti type.

It loads the Venti config, initializes disk cache, then `readarenainfo()` walks every arena's clump directory in chunks of 32K `ClumpInfo` records. Valid entries increment a global `count[size][type]` table; invalid type or size entries are reported and skipped.

`clumpstats()` totals clump records across all arenas and prints one row per non-empty size, followed by per-type counts. It is diagnostic only and does not inspect clump payloads.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/clumpstats.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/cmparenas.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/cmparenas.c

Compares two arena partition files byte-for-byte at the arena level. It reads both arena partition headers and tables, requires identical tables, then compares selected arena names or all arenas.

`readap()` unpacks the arena partition header and reads the arena table. `cmparena()` validates arena headers and tail metadata, prints structural ranges using `printheader()`, then reads both arena byte streams block by block and reports hex diffs for mismatching 16-byte spans.

The command supports custom compare block size (`-b`), optional sleep between reads (`-s`), and verbosity. It is useful for replica comparison or confirming copied arena partitions remain identical.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/cmparenas.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/config.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/config.c

Parses and initializes Venti server configuration. `runconfig()` reads an `IFile`, accepts directives for `isect`, `arenas`, `bloom`, `index`, memory sizes, `queuewrites`, HTTP address, webroot, and Venti address, and rejects duplicate or malformed lines.

`initventi()` initializes stats, runs the config parser, creates `mainindex` with `initindex()`, and attaches the configured Bloom filter. `configisect()`, `configarenas()`, and `configbloom()` open underlying `Part` objects in direct read/write mode and initialize their on-disk structures.

The parser is deliberately strict: unknown lines, bad sizes, duplicate settings, and illegal names abort initialization. `needmainindex()` exists only to force data-symbol linkage on platforms that need a function reference.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/config.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/conv.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/conv.c

Contains big-endian disk-format conversion routines for Venti server structures: arena partitions, arena headers and tails, clumps, clump-info records, index sections, index entries, index buckets, and Bloom headers.

The file enforces magic numbers, supported versions, structural sizes, and clump encoding invariants. It handles arena version 4 and 5 formats, including the version-5 clump magic and the arena tail extension that distinguishes committed `diskstats` from in-memory `memstats`.

`packarena()` deliberately clears stale extension fields when no extension is needed, protecting older arenas from a historical sealed-state mismatch. `unpackibucket()` can invalidate buckets when section-specific bucket magic mismatches.

This file is the central compatibility boundary between in-memory `dat.h` structs and stable on-disk bytes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/conv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/dat.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/dat.h

Defines core Venti server constants, disk-format sizes, magic/version values, error severities, dirty-flush stages, and the primary data structures used by the server and utilities.

Key structures include `Config`, `Part`, `DBlock`, `Lump`, `AMap`, `ArenaPart`, `Arena`, `ArenaHead`, `ClumpInfo`, `Clump`, `Index`, `ISect`, `IAddr`, `IEntry`, `IBucket`, `ZBlock`, `IFile`, `Stats`, `Graph`, `Round`, and `Bloom`.

The header documents the storage model: arena partitions contain arena logs; arenas contain clumps plus reverse clump-info directories and trailers; indexes map scores to arena addresses through bucketed index sections; Bloom filters accelerate misses; caches hold disk blocks, index entries, and lumps.

It also declares global runtime controls such as `mainindex`, `maxblocksize`, `readonly`, cache sleep knobs, scheduling flags, Bloom controls, sync/compression flags, stats, and trace identifiers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/dcache.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/dcache.c

Implements the raw disk block cache used for arena and metadata blocks. `getdblock()`/`_getdblock()` locate or load a `DBlock`, apply read or write locking based on mode, and read missing bytes from the underlying `Part` unless opened as pure write.

The cache uses a hash table for lookup, a free list, and an LRU-like heap based on second-to-last use to select victims. Dirty blocks are tagged with ordered dirty stages, and `flushproc()` writes all dirty blocks in stage order after sorting by dirty tag, partition, and address.

Writes are delegated to per-partition `writeproc()` workers through `Part.writechan`, then flushed per partition. `dirtydblock()` schedules immediate or delayed flush rounds when the dirty population grows.

The file also provides cache consistency checks, eviction through `emptydcache()`, and manual/forced flush or kick functions used by HTTP controls and index-write backpressure.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/dcache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/disksched.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/disksched.c

Implements adaptive disk scheduling knobs for background work. It tracks recent level-0 disk access and level-1 index-flush disk access via `diskaccess(level)`.

`disksched()` sets `icachesleeptime` and `arenasumsleeptime` based on recent activity. During foreground disk access, it may pause index cache flushing unless dirty pressure is high. During index flush activity, it suppresses arena summary work. When idle, it removes throttling.

The adaptive path estimates write rate and desired dirty-entry target from one minute of stats history, trying to keep the index cache around 70% dirty without interfering with foreground disk work. `manualscheduling` disables this automatic adjustment.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/disksched.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/dump.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/dump.c

Provides text dump helpers for Venti structures.

`printindex()` prints index name, version, block size, table size, bucket divisor, section map, and arena map. `printarenapart()` prints arena partition metadata and arena table entries. `printarena()` prints arena name, address range, version, timestamps, seal state, score if present, clump counts, data sizes, and storage use.

These are shared by command-line diagnostics such as `checkarenas` and `findscore`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/dump.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/findscore.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/findscore.c

Implements `findscore`, a read-only utility that searches an arena partition's clump directories for a given score.

`findscore()` walks each arena's `ClumpInfo` records in chunks, compares scores, and reports matching clump number, type, uncompressed size, compressed size, and arena-relative data position. It tracks positions by summing `ClumpSize + ci->size`.

The command parses a score string, opens an arena partition, initializes cache, scans all arenas, and reports total occurrences. `clumpinfoeq()` is a small equality helper for complete `ClumpInfo` comparisons.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/findscore.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/fixarenas.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/fixarenas.c

Implements `fixarenas`, a forensic arena-partition checker and repair tool designed to keep recovering usable clumps despite local corruption. Unlike `checkarenas`, it can infer geometry, scan raw data, rewrite metadata, zero corrupt spans, rebuild clump directories, and reseal arenas.

It first guesses arena geometry from intact arena heads/tails when needed, including arena size, block size, arena base, table base, and table size. It validates or rewrites the arena partition superblock and can check selected ranges.

The repair path uses paged read/write buffers, robust fallback reads down to 512-byte sectors, and SHA1 streaming buffers with rollback checkpoints for resealing. `isclump()` recognizes candidate clumps by magic, type, sizes, encoding, decompression, and score verification.

`guessarena()` reconstructs one arena: it loads basic name/version/magic hints from head/tail, scans clump payloads, tracks corrupt regions as synthetic `VtCorruptType` directory entries, computes stats and timestamps, adjusts directory space, rewrites clump-info blocks, optionally zeros bad data, unseals if there is large unused space, and computes new seal scores when fixing.

`checkarena()` compares reconstructed headers and tails against disk bytes with field-aware diff output, writes corrected bytes in `-f` mode, and can dump repaired arena images with `-x`. `checkmap()` rebuilds the arena partition map from recovered arena heads and rewrites it if different.

Important options include `-f` for write repair, `-U` to unseal, `-a`/`-b` to override arena/block size guesses, `-n` for base arena name, `-v` for detail, and optional arena ranges.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/fixarenas.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/fmtarenas.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/fmtarenas.c

Implements `fmtarenas`, which formats an arena partition. It accepts a name template and file, with options for arena size, block size, version 4 output, and zeroing.

The command opens the target part, optionally zeros it, initializes disk cache, creates a new `ArenaPart`, divides available space from `arenabase` into arena-sized ranges, creates each arena with `newarena()`, fills the arena map, and writes the arena partition header/table with `wbarenapart()`.

Defaults are 8 KiB blocks, 512 MiB arenas, 512 KiB arena table, and Arena version 5. Version 4 defaults to zeroing for older format expectations.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/fmtarenas.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/fmtbloom.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/fmtbloom.c

Implements `fmtbloom`, which creates a Bloom filter partition/file. It chooses a power-of-two byte size, caps at `MaxBloomSize`, requires at least 1 MiB, and computes hash count from either explicit `-N` or expected block count `-n`.

When `-n` is supplied, it avoids using more bits than useful and chooses roughly `ln(2)` times the bits per block, capped at `BloomMaxHash`. Without explicit sizing, it uses the part size.

The command initializes the Bloom header/data with `bloominit()`, sets `nhash`, allocates zeroed data, attaches the target `Part`, and writes it with `writebloom()`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/fmtbloom.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/fmtindex.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/fmtindex.c

Implements `fmtindex`, which writes or extends the textual index configuration replicated across index sections.

It reads the Venti config, counts all arenas from configured arena partitions, and either creates a fresh `Index` with `newindex()` or loads an existing one with `-a`. It builds a new arena address map starting at `IndexBase`, preserving existing arena map entries when extending and appending new arenas after the prior stop address.

The command reports arena count, index bucket count, and storage bytes, then writes index config and section headers through `wbindex()`. It validates index name legality and existing arena ordering when appending.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/fmtindex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/fmtisect.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/fmtisect.c

Implements `fmtisect`, which formats a single index section. It accepts a section name and target file, with options for block size, version 1 section format, and zeroing.

The command opens the part, optionally zeros it, creates a new `ISect` via `newisect()`, prints bucket count, bucket capacity, and index-map table size, then writes the section header with `wbisect()`.

Defaults are 8 KiB bucket blocks, 512 KiB config table size, and ISect version 2, which includes a randomized bucket magic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/fmtisect.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/fns.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/fns.h

Central function-prototype header for the Venti server and its utilities. It declares arena, arena-partition, index, index-section, clump, cache, Bloom, HTTP, graph, stats, config, parsing, disk-part, and formatting functions.

It exposes the main cross-file API: arena lifecycle and sync/writeback, index lookup/writeback, cache init/flush/kick, clump store/load, Bloom load/write/mark/test, config parsing, HTTP handlers, graph generation, part I/O, text-file parsing, raw conversion pack/unpack routines, and utility helpers.

It also defines common score copy/compare macros and allocation convenience macros. The sorted-by-name comment indicates the file is intended as a broad manual symbol index for this directory.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/graph.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/graph.c

Renders server statistics graphs into `Memimage` objects for HTTP PNG output. It initializes memdraw resources, small font, solid-color fill images, and shared drawing lock state.

`statgraph()` bins stats through `binstats()`, derives graph dimensions and min/max bounds, draws axes and numeric labels, and renders each bin as a vertical high/low filled column. It supports caller-provided width, height, min/max, and fill palette selection.

The file is used by `httpd.c`'s `/graph` endpoint, which turns the returned `Memimage` into PNG.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/graph.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/hdisk.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/hdisk.c

Implements HTTP disk and debug inspection handlers. `/disk` lists configured arena partitions, index sections, and Bloom filter, or opens a selected disk as an arena partition, index section, or Bloom filter.

For arena partitions, it reads the partition table, prints the arena table as links, unpacks selected arena head and tail metadata, displays stats and seal score, lists clump directory entries, and can inspect a clump by offset or score. Clump inspection retries with the raw clump magic when the expected magic fails, decompresses compressed clumps, and recomputes scores.

`hdebug()` supports `op=amap`, `op=mem`, and `op=read`. The read debug path compares cache lookup, disk index lookup, score lookup across all types, arena mapping, and `loadclump()` verification, with optional brute-force arena directory search.

Index-section and Bloom disk pages are stubs in this file.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/hdisk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/hproc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/hproc.c

Implements HTTP `/proc/...` introspection for the running Venti process using Plan 9 `libmach` and `libthread` internals.

It opens the current process text and memory, initializes symbol and register metadata, maps process memory, and reads thread/proc structures by address. It can print process lists, threads, thread stack summaries, full stack traces with parameters and locals, memory segments, file descriptors, and symbols.

`hproc()` dispatches `/proc/all`, `/proc/segment`, `/proc/fd`, `/proc/procs`, `/proc/threads`, `/proc/stacks`, and `/proc/symbols`, serializing access with a `QLock` because the global debug state is mutable. Output is plain text.

This file is highly Plan 9 specific and depends on private thread structure offsets from `/sys/src/libthread/threadimpl.h`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/hproc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/httpd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/httpd.c

Implements the Venti server HTTP interface. `httpdinit()` registers handlers for stats, index/storage summaries, XML index export, cache flush/kick/empty controls, graphing, runtime knob setting, logs, disk inspection, debug reads, and proc introspection, then starts a listener process.

`listenproc()` accepts connections and starts `httpproc()` per connection. `httpproc()` parses HTTP requests, dispatches exact or prefix URI handlers, serves static files from `webroot` when no handler matches, flushes responses, and honors close semantics.

Helpers parse query arguments, validate GET/HEAD requests, set content types with chunked HTTP/1.1 output, handle errors/not-found, and serve static files with simple extension-based MIME types.

Operational endpoints expose storage summaries, index layout, arena stats, cache controls, runtime integer settings, graph PNG or text bins, Venti logs, and XML serialization helpers. The `/set` endpoint can mutate global tuning flags such as compression, logging, cache sleeps, scheduler mode, Bloom ignore, sync writes, and icache prefetch.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/httpd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/icache.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/icache.c

Implements the in-memory index-entry cache plus an arena-summary prefetch cache. The main cache stores `IEntry` records by score/type in hash buckets and maintains circular free, clean LRU, and dirty lists.

`initicache()` sizes entry and summary-cache populations from memory budget. `icachelookup()` checks dirty/clean entries first, then summary-cache entries, promoting summary hits into the main clean cache. `lookupscore()` fills misses from disk via `loadientry()`.

`insertscore()` inserts clean or dirty entries. Dirty inserts update the latest `AState`, schedule index-cache writeback, and mark the Bloom filter. Clean inserts may trigger two-step summary prefetch: first miss reserves a summary slot, second miss loads arena group summaries via `asumload()`.

`icachedirty()` returns dirty entries in a hash range below a committed arena-address limit for writeback. `icacheclean()` marks written dirty entries clean and wakes waiters. `emptyicache()` evicts clean entries and clears summary caches.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/icache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/icachewrite.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/icachewrite.c

Implements asynchronous writeback of dirty index-cache entries. Random index updates are batched into section workers so writes happen in large sorted disk chunks.

`initicachewrite()` creates per-index-section write/done channels and starts one `icachewriteproc()` per section plus a coordinator. `icachewritecoord()` waits for kicks, snapshots `icachestate()`, starts section writebacks and Bloom writeback, waits for completion, then advances arena tail state with `setatailstate()` on success.

`icachewritesect()` gathers dirty entries for an index-section hash range up to the current arena address, sorts them by score, groups nearby buckets into up to 8 MiB chunks, reads the affected bucket range, inserts or replaces packed `IEntry` records, writes the range back, updates any matching disk-cache blocks, and marks successfully written entries clean.

The scheduler respects `icachesleeptime` and `minicachesleeptime`, calling `disksched()` between chunks. Bucket overflow or bad bucket validation leaves entries dirty and reports errors.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/icachewrite.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/ifile.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/ifile.c

Provides simple input-file handling for Venti config-like text. `readifile()` opens either a regular config file or a Venti partition-embedded config stored near `PartBlank`, checks the `"venti config\n"` magic for embedded configs, and stores the contents in a `ZBlock`.

`partifile()` reads a text table from a `Part` range, used for replicated index config. `ifileline()` returns the next nonblank line, strips comments beginning with `#`, and removes leading whitespace. `ifilename()` and `ifileu32int()` parse specific line types.

The file is shared by server config parsing and on-disk index configuration parsing.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/ifile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/index.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/index.c

Implements Venti index and index-section initialization, serialization, arena mapping, clump append indexing, and disk lookup helpers.

`initindex()` reads replicated textual index config from an index section, validates configured sections against `ISect` headers, computes bucket divisor state, and maps configured arenas. `newindex()` builds a fresh section map over available section blocks, caps index size below 2^32 buckets, and avoids over-coarse divisors. `wbindex()` writes config to every section and writes each section header.

`initisect()`/`newisect()` load or create an index section, compute bucket capacity and layout offsets, validate block size and ranges, and support version 2 bucket magic. Free functions release section/index state.

`writeiclump()` appends a clump to the first arena with space, computes its index address and `IAddr`, inserts a dirty score into `icache`, and advances `mapalloc`. `amapitoa()` and `amapitoag()` map index addresses back to arenas and arena groups.

Lookup code uses score prefix hashing: `indexsect0()` maps bucket to section, `loadibucket()` loads the responsible bucket, `bucklook()` binary-searches packed sorted entries by score and type, and `loadientry()` checks Bloom first, validates bucket size, and unpacks the matching entry.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/index.c -->