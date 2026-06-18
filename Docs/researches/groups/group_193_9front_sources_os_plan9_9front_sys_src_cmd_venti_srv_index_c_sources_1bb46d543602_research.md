# Group Research: group_193_9front_sources_os_plan9_9front_sys_src_cmd_venti_srv_index_c_sources_1bb46d543602

Subset scope: `Docs/research_subset_a.md`; source tree covered here: `sources/os/plan9/9front`.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/index.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/index.c

`index.c` implements Venti’s persistent score-to-arena-address index. It initializes existing indexes from section config tables, creates new index maps, validates section geometry, serializes index metadata, and maps logical arena addresses back to `Arena` objects.

The lookup path hashes the top score bits into a bucket, uses the bloom filter before disk reads, loads the owning index section block, validates bucket bounds, then binary-searches sorted packed `IEntry` records by score and disk type. The write path stores clumps in arenas through `writeiclump()`, constructs `IAddr`, inserts index entries, and advances arena allocation under `ix->writing`.

Important integration points are `loadibucket()`, `bucklook()`, `ientrycmp()`, `amapitoa()`, and `wbindex()`. The file is central to correctness: section maps must be contiguous, bucket divisor math must match `2^32` key-space coverage, and bucket entries must stay sorted for binary lookup and index rebuild tooling.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/index.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/lump.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/lump.c

`lump.c` is the main Venti read/write data path for content-addressed blocks. `readlump()` handles zero-score reads, checks the lump cache, looks up index entries, loads arena clumps, validates size/type/score, and inserts successful reads back into the cache.

`writelump()` hashes incoming packet data, suppresses empty/dev-null writes, detects cache duplicates and SHA1 collisions, optionally queues writes, and delegates actual storage to `writeqlump()`. Duplicate writes can either trust the index or verify by re-reading existing data when `verifywrites` is enabled.

The file couples the RPC layer, lump cache, index lookup, arena clump loading, write queue, and cache/disk flush policy. Correctness hinges on score verification in `readilump()` and duplicate-data comparison before accepting an existing score.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/lump.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/lumpcache.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/lumpcache.c

`lumpcache.c` implements the in-memory cache of recently read or written lumps. It combines a 512-bucket hash table keyed by score hash/type, per-lump locks, a free list, and an eviction heap ordered by second-most-recent use.

`lookuplump()` always returns a locked `Lump`, creating or recycling a descriptor on misses, and updates usage timestamps and stats. `insertlump()` attaches packet data to a looked-up lump while enforcing byte budget by evicting idle descriptors. `putlump()` releases the per-lump lock and makes unused entries eligible for heap eviction.

The cache is concurrency-sensitive: the global cache lock protects hash/free/heap state, while the individual lump lock serializes readers/writers for the selected score. `checklumpcache()` is a debug invariant verifier for heap, hash, free-list, reference, and byte-accounting consistency.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/lumpcache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/lumpqueue.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/lumpqueue.c

`lumpqueue.c` provides asynchronous write queues for Venti lumps. It allocates one small ring queue per index section, starts a `queueproc` worker for each, and routes writes by `indexsect(mainindex, score)` so writes for the same section serialize through the same queue.

`queuewrite()` enqueues a `Lump`, `Packet`, creator, timestamp, and generation, sleeping when the ring is full. `flushqueue()` bumps the global generation and waits until all older queued writes drain. Workers call `writeqlump()` and then `putlump()`.

The queue depth is intentionally tiny (`MaxLumpQ` 8), so this is latency overlap rather than large buffering. The generation mechanism is the main ordering contract used by sync requests.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/lumpqueue.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/mirrorarenas.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/mirrorarenas.c

`mirrorarenas` mirrors one arena partition onto another while copying only data that has changed. It validates matching arena counts, names, versions, block sizes, and sizes before mirroring selected ranges or all arenas.

The copy logic writes header, new data region, optional sealed holes, clump directory blocks, arena tail, and sealed score. It can compute SHA1 while copying so sealed destination arenas preserve or verify the source seal. A write worker overlaps source reads with destination writes.

The tool is careful about append-only arena semantics: it refuses when destination is ahead of source, handles clumpmagic early to avoid header/tail disagreement, and reports seal mismatches rather than blindly accepting divergent sealed content. `-F` forces full copying; `-s` skips SHA1 verification.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/mirrorarenas.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/part.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/part.c

`part.c` abstracts Venti disk partitions and file-backed ranges. It parses `file:lo-hi` names with `K/M/G/T` suffixes, opens the underlying file/device, records offset and bounded size, and falls back from read-write to read-only when needed.

`rwpart()` enforces partition bounds and splits I/O into `Maxxfer` chunks before calling `pread`/`pwrite`. `readpart()` and `writepart()` are thin wrappers. `partblocksize()` records each partition’s block size and updates global `maxblocksize`.

This file is used by almost every Venti storage tool. It provides the range safety layer between arena/index code and raw devices, though `flushpart()` is currently a no-op in this tree.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/part.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/png.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/png.c

`png.c` writes `Memimage` data as PNG over an `Hio` HTTP stream. It emits PNG signature, `IHDR`, deflated `IDAT` chunks, CRCs, and `IEND`.

The encoder converts images to RGB or RGBA memory format, translates Plan 9 premultiplied alpha to non-premultiplied PNG alpha, and feeds scanlines with filter type 0 into `deflatezlib()`. Static initialization sets up flate and CRC tables once under a lock.

This supports Venti’s web graph rendering path. The implementation is minimal and write-only: no PNG parsing, filtering choices, or palette handling.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/png.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/printarena.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/printarena.c

`printarena` inspects one arena image. It reads and prints the arena header, initializes an `Arena`, then walks clumps from a requested offset or the start until free space or an invalid clump is reached.

For each clump it validates clump magic, loads data, recomputes score unless the clump is marked corrupt, validates the Venti type, and prints offset, score, type, and uncompressed size. It reports the final end offset.

The tool is read-only and useful for verifying a standalone arena dump or extracting clump listings without loading a full Venti configuration.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/printarena.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/printarenapart.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/printarenapart.c

`printarenapart` reads an arena partition header and table, then prints summary information for each listed arena. It manually reads each arena header and tail, decodes disk stats, and reports clumps, compressed clumps, used bytes, uncompressed size, seal state, creation time, and modification time.

The file contains an unused `rdarena()` helper similar to `printarena.c`, but `threadmain()` only emits partition/arena summaries. It uses raw table parsing rather than full `initarenapart()`.

This is a diagnostic view for arena partitions when the operator wants layout and usage metadata instead of all clump entries.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/printarenapart.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/printarenas.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/printarenas.c

`printarenas` emits index-entry-style rows derived from arena clump directories. It loads a full Venti config, initializes enough disk cache, and iterates every arena or selected arena names.

`dumparena()` reads clump info in chunks, converts each `ClumpInfo` into an `IEntry` with logical index address, score, type, uncompressed size, and block count, then prints it. The output mirrors index entries reconstructed from arena truth.

This tool is useful for comparing arena contents to index contents or feeding external analysis around rebuild/check workflows.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/printarenas.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/printindex.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/printindex.c

`printindex` dumps entries directly from index section buckets. It loads the Venti config, initializes disk cache, optionally filters by index section name, reads every bucket block in selected sections, unpacks `IBucket`, unpacks each `IEntry`, and prints address, score, type, and size.

The tool bypasses high-level lookup and scans raw index storage. It is a diagnostic complement to `printarenas`: differences between the two expose stale, missing, or extra index records.

The file assumes bucket blocks are readable and trusts unpacked bucket counts; deeper validation is done elsewhere by check/sync tools.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/printindex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/printmap.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/printmap.c

`printmap` is a minimal command that loads a Venti config and prints the main index map with `printindex()`. It supports a `-B` option for parity with other tools but does not use the parsed cache size.

The command sets read-only mode unless a never-enabled `fix` variable changes, so it is intended as a non-mutating metadata display utility. Its output depends on the shared print routines rather than local formatting logic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/printmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/rdarena.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/rdarena.c

`rdarena` copies a named arena from an arena partition to standard output. It loads the partition, finds the arena by name, and writes the arena’s header, data/directory region, and tail in block-aligned chunks.

Flags allow quiet output and verbose arena-part printing. The copy range starts one block before `arena->base` and extends through the tail block, matching the standalone arena image format consumed by other tools.

This is a backup/extraction utility for moving individual arenas without copying an entire arena partition.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/rdarena.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/readifile.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/readifile.c

`readifile` is a tiny diagnostic wrapper around `readifile()`. It reads an index/config-style `IFile` from the named file and writes the underlying `ZBlock` bytes to stdout.

It does no parsing beyond the shared helper and exits fatally on read failure. Its main value is verifying or extracting how the Venti `IFile` abstraction sees a file.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/readifile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/reseal.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/reseal.c

`reseal` rewrites the tail seal of sealed arenas in an arena partition. It parses the arena-part directory, selects named arenas, verifies the existing seal hash unless forced, repacks the tail in current format, writes the new score into the final tail block, and verifies again.

The verification path hashes the arena header/data/directory and final block with the score slot zeroed, matching Venti seal semantics. `-f` allows resealing despite an existing score mismatch; `-b` controls I/O buffer size; `-s` is parsed but not used in the active verification loop.

This is a repair/migration tool for arena tail encodings, especially when older encodings need a canonical freshly packed seal.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/reseal.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/round.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/round.c

`round.c` implements a small round/kick synchronization primitive used by background cache/write processes. A `Round` has start, finish, and delayed-wait rendezvous points plus generation counters (`last`, `current`, `next`).

`kickround()` requests another round and can wait until the current requested generation completes. `waitforkick()` is called by the worker side to publish completion and sleep for the next request. `delaykickroundproc()` coalesces delayed kicks by sleeping for `delaytime` and only kicking if no newer round has started.

The code is a lightweight event coalescing mechanism for periodic flushing/prefetch work.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/round.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/score.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/score.c

`score.c` defines the global zero score and helper functions for Venti SHA1 scores. `scoremem()` hashes a memory buffer into a score, and `strscore()` parses a hex score string into 20 bytes.

`needzeroscore()` is a link anchor for environments that otherwise omit the object defining `zeroscore`. The parser accepts upper and lower hex and requires exact string termination after `2*VtScoreSize` digits.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/score.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/sortientry.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/sortientry.c

`sortientry.c` builds a sorted temporary file of all `IEntry` records implied by arena clump directories. It scans every arena, converts non-corrupt `ClumpInfo` rows into packed entries, marks scores in the bloom filter, bucket-sorts by leading score bits, spills bucket chunks to a temporary `Part`, then reloads and `qsort`s each bucket into final sorted order.

The chunk format stores a linked-list head at the end of each bucket buffer. `sortrawientries()` returns the clump count and final sorted base offset for downstream index rebuild logic.

This file is central to rebuilding indexes from arena truth. Risks are mostly operational: bucket memory sizing, temporary partition I/O failures, and ensuring corrupt clumps are skipped from index entries while still marked in bloom.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/sortientry.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/stats.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/stats.c

`stats.c` defines the Venti runtime stats table, global counters, history ring, and histogram/binning helper. `statsinit()` allocates a 90,000-sample history and starts a sampler that copies `stats` once per second.

`setstat()`, `addstat()`, and `addstat2()` update counters under `statslock`, with `collectstats` allowing increments to be disabled. `binstats()` converts a time range into graph bins by applying a caller-supplied function to consecutive `Stats` samples.

The stat descriptions must stay aligned with `dat.h:/NStat`; web graphing and status pages rely on these names and counter indices.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/stats.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/stdinc.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/stdinc.h

`stdinc.h` is the common include bundle for Venti server sources. It pulls in Plan 9 libc, libventi, flate, libsec, thread, httpd, draw, and memdraw headers.

The file is intentionally small and acts as a precompiled-style local convention: most server files include it before `dat.h` and `fns.h` to get shared system types and APIs.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/stdinc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/syncarena.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/syncarena.c

`syncarena.c` reconciles an arena’s in-memory stats and clump directory with clumps found by walking arena data. `syncarena()` starts from current `memstats`, reads clump magic and clump headers, verifies data scores and types, compares or repairs clump-info directory entries, and advances used/clump/compressed/uncompressed counters.

With `fix`, broken clumps can be marked `VtCorruptType`, missing/bad directory entries can be rewritten, and cache flushes are requested. The function reports bit flags such as header drift, directory zeroes, directory mismatch, data errors, and fix errors.

It is the local arena-consistency engine used by index synchronization and repair tools.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/syncarena.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/syncindex.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/syncindex.c

`syncindex` is the command-line driver for synchronizing an index from arena contents. It loads config and bloom filter, initializes disk/lump/index caches, starts bloom maintenance, optionally prints the index, calls `syncindex(mainindex)`, then flushes index and disk caches.

It exposes cache-size flags for block and index caches plus verbose mode. This file is orchestration; the actual arena scanning and index insertion live in `syncindex0.c` and `syncarena.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/syncindex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/syncindex0.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/syncindex0.c

`syncindex0.c` implements the index synchronization algorithm. For each arena, it runs `syncarena()` with repair enabled, ignores expected header/directory-zero categories where safe, and indexes clumps present in `memstats` but not yet reflected in `diskstats`.

`syncarenaindex()` reads each new clump’s `ClumpInfo`, builds `IAddr`, updates an `AState`, and calls `insertscore()` with dirty entries. After successful insertion, `syncindex()` writes the arena tail and schedules delayed index-cache flushing.

This is the bridge from append-only arena recovery to persistent index catch-up.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/syncindex0.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/trace.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/trace.c

`trace.c` defines trace category strings and the `trace()` helper for Venti logging. When `ventilogging` is enabled, trace messages are formatted with thread names and written both to the specific category log and the aggregate `all` log as HTML snippets.

`traceinit()` and `settrace()` are stubs in this version, so runtime category filtering is not implemented here. The categories are still used throughout disk, lump, block, process, work, quiet, and RPC paths.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/trace.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/unittoull.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/unittoull.c

`unittoull.c` parses unsigned numeric strings with optional `K`, `M`, `G`, or `T` suffixes into `u64int`. It returns all-ones `TWID64` on nil input or trailing garbage.

The helper is used for command-line cache sizes, block sizes, and similar operator-provided quantities. It uses `strtoul`, so callers should treat it as a convenience parser rather than a full overflow-detecting numeric validator.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/unittoull.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/unwhack.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/unwhack.c

`unwhack.c` implements decompression for Venti’s custom `whack` LZ-style format. It decodes literals with a recent-literal history optimization, decodes short and extended match lengths, decodes offset classes, copies matches from prior output, and reports detailed errors through `Unwhack.err`.

The decoder validates output bounds, offset range, bitstream underrun/overrun, and length range. It returns the exact uncompressed length on success or `-1` on malformed compressed data.

This must remain bit-compatible with `whack.c`; it is used when reading compressed clumps from arenas.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/unwhack.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/utils.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/utils.c

`utils.c` contains common Venti server helpers: bounded arena-name compare/copy/validation, decimal `u32int`/`u64int` parsing with overflow checks, Venti type validation, error/log formatting, current time, `u64log2`, process creation wrapper, formatters, millisecond time, and bit counting.

`ventifmtinstall()` installs formatting for Venti calls, hex, index entries, time, and scores. `seterr()` updates Plan 9 `%r` error text while optionally logging severity-tagged messages.

These utilities are small but widely shared across admin tools and server paths.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/utils.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/venti.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/venti.c

`venti.c` is the Venti server entry point. It parses server address, HTTP address, config path, memory/cache sizing, readonly, logging, queueing, and webroot flags; loads config and bloom filter; sizes lump/block/index caches; starts HTTP, cache, bloom, arena sum, and optional write-queue services; synchronizes the index; then listens for Venti RPCs.

Automatic memory sizing reads `/dev/swap`, subtracts bloom-filter load impact, enforces conservative minima, and caps values to avoid signed 32-bit overflow in older internals. Config values, command-line cache sizes, and `-m` percentage sizing have explicit precedence.

`ventiserver()` handles `Tread`, `Twrite`, and `Tsync`, updating stats and using `readlump()`, `writelump()`, queue flush, and cache flush. On shutdown it flushes disk and index caches.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/venti.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/verifyarena.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/verifyarena.c

`verifyarena` verifies arena seal checksums from stdin or an arena partition. It reads each selected arena, hashes all bytes with the final score slot zeroed, unpacks the trailer, validates name/version consistency, and reports verified, unsealed, or mismatched checksum status.

When run on a partition, it parses the arena-part table and can filter by arena names. Flags control I/O block size, sleep between reads, and verbosity.

The tool does not repair; it is a read-only integrity checker for sealed arena images and partitions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/verifyarena.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/whack.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/whack.c

`whack.c` implements Venti’s custom LZ77-like compressor. It keeps a rolling hash table of recent 3-byte sequences, searches bounded candidate chains based on compression level, emits optimized literal codes, match lengths, and offset encodings, and abandons compression when output would not fit or progress is poor.

`whackinit()` sizes the search effort and initializes history. `whack()` updates compression statistics, handles match insertion, delay flushing of packed bits, and returns compressed size or `-1`. `whackblock()` is a one-shot helper using level 6.

The format is private to Venti clumps and must match `unwhack.c`. The global `compressblocks` flag can disable compression at runtime.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/whack.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/whack.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/whack.h

`whack.h` defines the shared compressor/decompressor state and constants for Venti’s whack format. It sets stats count, error string length, maximum match offset, hash table size, minimum match length, decode threshold, and sequence-mask constants.

`Whack` stores the rolling hash table, back-link ring, start time, and source pointer. `Unwhack` stores the latest error message. The header declares initialization, compression, decompression, and one-shot block compression APIs.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/whack.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/wrarena.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/wrarena.c

`wrarena` reads a standalone arena image and writes its clumps to a Venti server. It caches the arena data in memory, reads clump headers and directory entries directly, decompresses compressed clumps with `unwhack()`, verifies scores/types, then sends clumps through multiple `vtwrite` sender threads.

Options select host, arena offset, max writes, verbose score printing, and disabling libventi double-check SHA1. Host `/dev/null` skips server connection but still walks/verifies clumps.

This is a restore/import utility. It assumes the arena image is locally readable and valid enough for direct in-memory clump/directory indexing.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/wrarena.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/www/stats.js -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/www/stats.js

`stats.js` drives the Venti web statistics dashboard. It defines graph query names, labels, column layouts, logging/stat/compression controls, and log links, then dynamically builds graph tables using `/graph?...` image URLs.

Clicking a small graph promotes it to the two large 24-hour and 1-hour graphs. The settings panel updates local state and sends changes through a hidden frame URL `/set/<name>/<value>`.

The script is old-style global JavaScript/DOM code and depends on server endpoints for graph images, logs, and settings. It includes HTML snippets directly in strings.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/www/stats.js -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/www/status.js -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/www/status.js

`status.js` is a small status-page refresher. It defines a cycle of HTML fragments (`status1.html`, `status2.html`, `status3.html`) and repeatedly advances a hidden frame or location to the next fragment every five seconds.

The script is intended for older browser/frame-based status pages served by Venti’s HTTP interface. All state is global and minimal.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/www/status.js -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/www/status1.js -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/www/status1.js

`status1.js` is a variant of the status-page auto-rotator. It maintains a list of status HTML page names and replaces `parent.status.location.href` with the next page every five seconds.

It is tightly coupled to a frameset layout with a frame named `status`. Like `status.js`, it is simple global JavaScript for the Venti web UI.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/www/status1.js -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/xml.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/xml.c

`xml.c` emits XML summaries for Venti arena maps, arenas, and indexes. `xmlarena()` writes arena attributes including partition, block size, range, timestamps, seal state, score, clump counts, data bytes, compressed bytes, and storage bytes.

`xmlindex()` writes index attributes, section maps, arena maps, and nested arena summaries. `xmlamap()` emits named start/stop ranges.

The file depends on XML primitive emitters declared in `xml.h` and implemented elsewhere in the HTTP layer. It is presentation glue for machine-readable index/storage status.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/xml.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/xml.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/xml.h

`xml.h` declares XML rendering functions for `AMap`, `Arena`, and `Index`, plus lower-level helpers for names, scores, booleans, integers, and indentation.

It is a small contract between XML object renderers in `xml.c` and HTTP/XML primitive functions elsewhere in the Venti server.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/xml.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/zblock.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/zblock.c

`zblock.c` implements aligned variable-sized `ZBlock` buffers. `alloczblock()` allocates raw memory, aligns the data pointer to the requested block size, places the `ZBlock` descriptor after the data, optionally zeroes data, and writes an overflow sentinel after the logical data region.

`freezblock()` checks the sentinel before freeing, catching overwrites past `b->_size`. Helpers convert between `Packet` and `ZBlock`, and `fmtzbinit()` initializes a `Fmt` to write into a `ZBlock`.

This is a core buffer abstraction for disk blocks, config serialization, clump data, and utility I/O.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/zblock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/zeropart.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/zeropart.c

`zeropart.c` provides `zeropart()`, which clears a `Part` from `PartBlank` to the end using a zeroed `ZBlock`. It writes full `MaxIoSize` chunks first and finishes with block-size chunks, then flushes and frees the buffer.

This helper is used by formatting tools to initialize arena/index/bloom partitions before writing headers and tables.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/zeropart.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/sync.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/sync.c

`venti/sync` is a client utility that connects to a Venti server and sends `vtsync()`. It accepts an optional `-h host` and a hidden/test `-x` mode that connects and disconnects without syncing.

It installs Venti formatters, dials, performs protocol connect, optionally syncs, then hangs up. It is the client-side counterpart to the server’s `VtTsync` handling.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/sync.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/words/dumpvacroots -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/words/dumpvacroots

`dumpvacroots` is an rc script that scrapes the Venti HTTP `/index` page, derives arena print commands, runs `venti/printarena`, and extracts clumps of type 16 as `vac:<score>` roots.

The script demonstrates that anyone with physical arena access or HTTP index visibility can enumerate historical vac roots. It depends on `hget`, `sed`, `awk`, `rc`, and the `$venti` environment variable.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/words/dumpvacroots -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/words/venti.conf -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/words/venti.conf

`venti.conf` is a sample Venti configuration. It documents formatting commands for arenas, index sections, and the index, then defines index name `main`, two index sections under `/tmp/disks`, and one arena partition.

It is example/operator documentation rather than executable code, showing the minimal config directives consumed by `initventi()`/config parsing.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/words/venti.conf -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/words/wrtape -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/words/wrtape

`wrtape` is an rc backup script that selects a tape number’s 32-arena batch from the Venti HTTP index, logs each arena to `/sys/log/ventibackup`, and writes each arena stream from `venti/rdarena` to a SCSI tape device with filemarks.

It depends on site-specific host `iolaire`, `/dev/sd03`, `scuzz`, `hoc`, `hget`, and HTTP index formatting. It is operational backup glue rather than portable tooling.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/words/wrtape -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/write.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/write.c

`venti/write` reads one block from stdin, optionally zero-truncates it, writes it to a Venti server with a selected block type, prints the resulting score, and disconnects.

It enforces `VtMaxLumpSize`, accepts `-h host`, `-t type`, and `-z`, and uses libventi’s `vtwrite()`/`vtdial()`/`vtconnect()` APIs. This is the simple command-line client for adding a block to a Venti store.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/write.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vi/bpt.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vi/bpt.c

`bpt.c` implements breakpoints for the `vi` MIPS simulator/debugger. It supports instruction breakpoints plus memory read, write, access, and equality breakpoints, each with a count/repeat value.

`breakpoint()` parses breakpoint modifiers, stores the expression-derived address, and links a new `Breakpoint`. `delbpt()` removes by address. `brkchk()` is called during instruction and memory access paths to stop execution by setting `count=1` and `atbpt=1`.

`dobplist()` formats active breakpoints with symbol offsets for debugger display.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vi/bpt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vi/cmd.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vi/cmd.c

`cmd.c` is the interactive debugger command loop for `vi`, an adb-like MIPS simulator. It parses expressions, counts, commands, formatting modifiers, breakpoints, run/continue/step commands, stack/register/stat commands, memory inspection, expression evaluation, and register assignment.

Supported commands include `:b`, `:d`, `:r`, `:c`, `:s`, `$r`, `$f`, `$F`, `$b`, `$c`, `$C`, trace toggles, instruction summaries, and memory display via `?`/`/`. `pfmt()` implements numeric, character, string, instruction, symbol, source, and global formats.

The command loop uses `setjmp(errjmp)` recovery and a note handler for interrupts. It is the operator-facing shell over the simulator core.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vi/cmd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vi/float.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vi/float.c

`float.c` implements MIPS COP1 floating-point instruction simulation. It dispatches arithmetic, moves, conversions, compares, FP loads/stores, FP condition branches, and register transfers through the `cop1` table.

The code tracks each FP register’s current format (`FPs`, `FPd`, or memory), swaps word order when converting to doubles, updates the FPSR condition bit for compare predicates, handles branch delay slots, and traps unimplemented or invalid operations via `longjmp(errjmp)`.

It supports single, double, and word variants for many operations, but unimplemented COP1 opcodes intentionally stop the simulator.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vi/float.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vi/icache.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vi/icache.c

`icache.c` is a stub instruction-cache module for the MIPS simulator. `icacheinit()` and `updateicache()` currently do nothing beyond accepting the address argument.

The rest of the simulator still has `Icache` state and calls `updateicache()` from instruction fetch when enabled, so this file preserves the interface for a cache model that is not implemented here.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vi/icache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vi/mem.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vi/mem.c

`mem.c` implements virtual memory access for the MIPS simulator. It validates alignment, fetches big-endian instructions and data, triggers memory breakpoints, copies syscall buffers, and demand-loads virtual pages from text/data files or zero-filled bss/stack segments.

`vaddr1()` walks simulator segments, updates a simple random-replacement TLB model when enabled, allocates pages on demand, and reads backing file bytes for text/data. `vaddr()` traps on unmapped access. `badvaddr()` is a non-trapping probe used for trace formatting.

This file is the simulated MMU and memory bus used by instruction execution and syscall emulation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vi/mem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vi/mips.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vi/mips.h

`mips.h` is the shared simulator header. It defines MIPS user/kernel address constants, breakpoint types, instruction classes, TLB and icache models, decoded instruction table entries, register file including FP unions, memory segments, syscall memory-copy modes, global state, function prototypes, Plan 9 page/stack constants, opcode field macros, and FP compare constants.

The header is the integration point for the debugger, memory model, instruction execution, syscall layer, stats, and process setup. It also imports `/mips/include/ureg.h`, binding this tool to Plan 9 MIPS register layout.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vi/mips.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vi/run.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vi/run.c

`run.c` implements the main MIPS opcode table and most non-special integer/load/store/branch instructions. `run()` repeatedly zeros `r0`, fetches at `pc`, dispatches through `Iexec`, advances `pc`, checks instruction breakpoints, optionally prints register traces, and stops when `count` reaches zero.

Instruction handlers implement immediate arithmetic/logical ops, byte/half/word loads and stores, unaligned `lwl/lwr`, jumps, calls, branch and branch-likely forms with explicit delay-slot execution, `ll/sc` as uniprocessor `lw/sw`, and `bcond` variants.

The file tracks instruction counts through `Inst.count` and branch delay-slot use. Branch handlers update `pc` to `target-4` because the main loop adds 4 after dispatch.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vi/run.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vi/special.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vi/special.c

`special.c` implements MIPS SPECIAL opcode dispatch and register-register operations. The `ispec` table covers shifts, jumps, syscall, HI/LO moves, multiply/divide, add/subtract/logical operations, and set-less-than variants.

Handlers update simulator registers, HI/LO, and branch delay-slot execution. `jr`/`jalr` also support call-tree tracing with symbol/source output. `Snor()` recognizes the simulator’s chosen NOP instruction and increments `nopcount` instead of modifying registers.

This file complements `run.c` for opcode 0 instructions and shares the same stats/trace model.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vi/special.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vi/stats.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vi/stats.c

`stats.c` reports simulator execution statistics. `isum()` aggregates counts from primary, special, and COP1 instruction tables into instruction mix, memory cycles, loads/stores, arithmetic, floating point, special-register moves, syscalls, branches, branch-taken rate, and delay-slot usage.

`tlbsum()` reports the synthetic TLB model’s entries, accesses, hits, misses, and hit rate. `segsum()` reports segment resident bytes and references. `iprofile()` maps per-instruction fetch counters back to text symbols and prints a sorted cycle profile with source locations.

The file is diagnostic/reporting logic for performance studies of simulated MIPS binaries.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vi/stats.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vi/symbols.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vi/symbols.c

`symbols.c` provides source and stack-symbol display for the `vi` debugger. It maps PCs to `file:line`, prints local auto variables and parameters from symbol metadata, and implements stack traces with optional locals.

`stktrace()` follows frames using `.frame` symbols, saved PC, stack pointer, and return register logic until `_main` or a truncation limit. It prints called-from information with symbol offsets and source lines.

This file depends on Plan 9 `mach` symbol APIs and simulated memory reads for stack frame values.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vi/symbols.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vi/syscall.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vi/syscall.c

`syscall.c` emulates a subset of Plan 9 system calls for simulated MIPS programs. It decodes arguments from the simulated stack, copies strings/buffers through `memio()`, invokes host Plan 9 syscalls, writes return values to register `r1`, and maintains an emulated error string.

Implemented calls include bind, chdir, close, dup, exits, open, read/pread, seek/oseek, rfork without `RFPROC`, sleep, old/new stat/fstat, write/pwrite, pipe, create, fd2path, brk, remove, notify registration, segflush no-op, and `_nsec`. Many unsupported calls print “No system call” and exit.

`Ssyscall()` dispatches based on `reg.r[1]`, traces names when enabled, and flushes debugger output. This file is the compatibility boundary between simulated user code and the host environment.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vi/syscall.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vi/vi.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vi/vi.c

`vi.c` is the main program and setup code for the MIPS simulator/debugger. It opens a MIPS executable or attaches to an existing process id, initializes Bio streams, TLB defaults, executable headers, symbols, memory maps, stack, initial FP constants, then enters `cmd()`.

`initmap()` builds text, data, bss, and stack segments from executable header layout and allocates instruction profiling storage. `procinit()` snapshots `/proc/<pid>` text, segment, memory, registers, and stack into simulator state. `initstk()` constructs a Plan 9-style user stack with argc/argv and a minimal `Tos`.

The file also provides fatal/error reporting, instruction trace formatting, register dumps, allocation helpers, and signed/unsigned 32x32-to-64 multiplication helpers used by simulated multiply instructions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vi/vi.c -->