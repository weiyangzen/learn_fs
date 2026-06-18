# Group Research: group_1633_plan9_sources_os_plan9_plan9_sys_src_cmd_venti_srv_lump_c_sources_o_314f309ea2b2

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/plan9`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/lump.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/lump.c

Purpose: Implements Venti score-addressed lump read/write operations for the server.

Key behavior:
- `readlump` returns an empty packet for the zero score, checks the lump cache first, then looks up the score in the index and reads the clump from its arena.
- `writelump` computes the SHA1 score, ignores empty or configured dev-null writes, detects cached duplicate data, and either queues or directly writes the lump.
- `writeqlump` handles duplicate-on-disk checks, optional write verification, stores new clumps with `storeclump`, inserts successful writes into the lump cache, and optionally flushes caches synchronously.
- `readilump` maps an index address to an arena, loads the clump, verifies size/type/score consistency, converts the zblock to a packet, and populates the cache.

Dependencies:
- Uses packet APIs, index lookup/store, arena load, score utilities, cache APIs, statistics, tracing, and global flags from the Venti server.

Notable details:
- Duplicate writes can be treated as success without disk read unless `verifywrites` is enabled.
- Error handling distinguishes missing scores, too-small reads, index/clump mismatch, score mismatch, and possible SHA1 collisions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/lump.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/lumpcache.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/lumpcache.c

Purpose: Provides the in-memory lump cache keyed by score and block type.

Key behavior:
- `initlumpcache` allocates a fixed descriptor pool, hash table, victim heap, and byte budget.
- `lookuplump` finds or allocates a `Lump`, pins it with a refcount, updates two-generation usage timestamps, and locks the returned lump.
- `insertlump` attaches packet data to a lump while evicting victims until enough packet memory is available.
- `putlump` releases the lump lock, decrements the refcount, and returns unreferenced entries to the eviction heap.
- `bumplump` evicts the oldest eligible lump from the heap, removes it from the hash table, frees packet data, and returns the descriptor to the free list.
- Heap helpers maintain a victim heap ordered by second-most-recent use.

Dependencies:
- Uses Plan 9 `QLock`/`Rendez`, packet ownership, hash/score helpers, stats counters, and server tracing.

Notable details:
- The replacement policy uses the “second to last use” timestamp, approximating LRU with protection for recently reused entries.
- `CHECK(checklumpcache())` is compiled out by default but can validate heap, hash, free-list, refcount, and memory accounting invariants.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/lumpcache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/lumpqueue.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/lumpqueue.c

Purpose: Implements asynchronous queued writes for Venti lumps.

Key behavior:
- `initlumpqueues` creates one queue worker per index section.
- `queuewrite` maps a lump score to an index section, appends a `WLump` to that section’s small ring buffer, and wakes its worker.
- `flushqueue` advances a generation counter and waits for queued entries from older generations to drain.
- `queueproc` removes queued writes, calls `writeqlump`, reports failures, and releases the lump reference.

Dependencies:
- Uses `indexsect`, `writeqlump`, `putlump`, `Rendez`, `QLock`, and global `mainindex`.

Notable details:
- Ring size is only 8 entries per queue.
- Writes are sharded by index section, preserving locality and reducing lock contention.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/lumpqueue.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/mirrorarenas.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/mirrorarenas.c

Purpose: Mirrors one Venti arena partition to another, copying only data that has changed or is missing.

Key behavior:
- Opens source read-only and destination read/write, loads both arena partitions, and verifies matching arena count, version, block size, size, and name.
- `copy` overlaps reads and destination writes through a write thread and two 1 MiB buffers.
- `mirror` copies arena headers, new data, directory blocks, holes for sealed arenas, and trailer blocks as needed.
- For sealed arenas, it can compute/validate SHA1 across the destination and write the final seal score.
- `mirrormany` mirrors all arenas or a comma/range selection.

Dependencies:
- Uses Venti arena/partition metadata, `readpart`, `writepart`, arena pack/unpack helpers, SHA1, and Plan 9 thread channels.

Notable details:
- Refuses unsafe states such as destination sealed while source is unsealed, or source used size less than destination used size.
- `-F` forces full copy; `-s` disables SHA1 verification while mirroring sealed arenas.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/mirrorarenas.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/part.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/part.c

Purpose: Wraps file/device partitions with optional byte-range slicing and bounded I/O.

Key behavior:
- Parses names like `file:lo-hi`, with `k/m/g/t` suffixes.
- `initpart` opens the backing file/device, applies global read-only mode, validates range bounds, and records partition size/offset.
- `rwpart` checks partition bounds and performs chunked `pread`/`pwrite` operations capped at `Maxxfer`.
- `readpart` and `writepart` are simple wrappers.
- `readfile` loads an entire partition/file into a `ZBlock`.

Dependencies:
- Uses Plan 9 file APIs, `Dir`, `ZBlock`, and Venti allocation/error helpers.

Notable details:
- `flushpart` is a no-op in this implementation.
- `Maxxfer` is 64 KiB, documented as a workaround for old NCR SCSI controller limits.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/part.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/png.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/png.c

Purpose: Writes Plan 9 `Memimage` images as PNG streams through the HTTP I/O layer.

Key behavior:
- Emits PNG signature, IHDR, compressed IDAT chunks, and IEND.
- Converts source images to RGB/RGBA channel layouts suitable for PNG.
- Uses zlib deflate callbacks to stream scanlines with filter type 0.
- Converts Plan 9 premultiplied alpha to non-premultiplied alpha for RGBA output.
- Lazily initializes deflate and CRC tables once under a lock.

Dependencies:
- Uses `Memimage`, `Hio`, Plan 9 draw/memdraw locking, flate, and CRC helpers.

Notable details:
- IDAT chunks are capped at 20,000 bytes.
- Only non-interlaced 8-bit RGB/RGBA output is generated.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/png.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/printarena.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/printarena.c

Purpose: Command-line utility to inspect a single arena file.

Key behavior:
- Opens an arena file read-only/direct, reads and prints the arena head, initializes an arena object, and walks clumps from a specified or zero offset.
- For each clump, checks magic, loads data, verifies score/type unless marked corrupt, and prints offset, score, type, and uncompressed size.
- Prints the final end offset.

Dependencies:
- Uses arena metadata parsing, clump loading, score validation, partition I/O, and disk cache setup.

Notable details:
- Supports `-o` to choose the arena file offset.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/printarena.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/printarenapart.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/printarenapart.c

Purpose: Prints summary information for every arena in an arena partition.

Key behavior:
- Opens an arena partition read-only/direct, unpacks the arena partition header, computes and reads the arena table, then scans entries.
- For each table entry, reads the arena head and tail, unpacks the tail, and prints arena offset, clump counts, compressed clump counts, used bytes, uncompressed bytes, sealed state, and timestamps.

Dependencies:
- Uses arena partition metadata, arena head/tail unpacking, `partblocksize`, and disk cache initialization.

Notable details:
- Contains a local `rdarena` routine similar to `printarena.c`, but `threadmain` only prints arena summaries and does not call it.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/printarenapart.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/printarenas.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/printarenas.c

Purpose: Dumps clump-derived index entries from arenas in a configured Venti index.

Key behavior:
- Loads Venti configuration, initializes disk cache, and iterates selected or all arenas.
- `dumparena` reads clump directory entries in chunks, converts each `ClumpInfo` into an `IEntry`, and prints address, score, type, and size.
- Uses the index arena map to compute logical addresses.

Dependencies:
- Uses `initventi`, `readclumpinfos`, `IEntry`, `Biobuf`, and Venti formatting.

Notable details:
- The `nskip` variable is initialized but not used to filter corrupt clumps in this utility.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/printarenas.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/printindex.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/printindex.c

Purpose: Dumps entries from Venti index sections.

Key behavior:
- Loads a Venti config and initializes disk cache.
- Iterates selected or all index sections, reads each index bucket block, unpacks the bucket, unpacks each `IEntry`, and prints address, score, type, and size.

Dependencies:
- Uses index section structures, bucket magic, `unpackibucket`, `unpackientry`, and Plan 9 buffered output.

Notable details:
- `-B` controls disk block cache memory, with a minimum derived from index/arena geometry.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/printindex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/printmap.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/printmap.c

Purpose: Prints the configured Venti index layout/map.

Key behavior:
- Parses `-B` but does not use the value.
- Forces read-only mode, loads the Venti config, and calls `printindex` on `mainindex`.

Dependencies:
- Uses `initventi`, global `mainindex`, and Venti index printing helpers.

Notable details:
- The local `fix` variable is always zero, so the tool always runs read-only.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/printmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/rdarena.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/rdarena.c

Purpose: Extracts a named arena from an arena partition to standard output.

Key behavior:
- Opens an arena partition read-only/direct, locates the named arena, and writes the arena header, body, and trailer to stdout.
- Uses a buffer at least as large as the arena block size and otherwise `MaxIoSize`.
- Optional `-q` suppresses progress output; `-v` prints arena partition metadata.

Dependencies:
- Uses arena partition loading, disk cache, partition reads, and raw stdout writes.

Notable details:
- Output is binary arena data suitable for backup or transfer.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/rdarena.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/readifile.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/readifile.c

Purpose: Small utility to read an index file and write its raw block data to stdout.

Key behavior:
- Expects exactly one filename.
- Calls `readifile`, then writes `ifile.b->data` with length `ifile.b->len`.

Dependencies:
- Uses `IFile` and Venti index-file reader helpers.

Notable details:
- Minimal wrapper with no extra interpretation of the index file contents.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/readifile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/reseal.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/reseal.c

Purpose: Verifies and rewrites sealed arena trailer/checksum data.

Key behavior:
- Reads an arena partition table, optionally filters named arenas, and reseals matching sealed arenas.
- `verify` hashes all arena bytes with the seal slot treated as zero, compares with the stored score unless forced, repacks the arena trailer, computes the new score, and writes it into the trailer.
- `resealarena` validates the arena head/tail, skips unsealed arenas, writes the new tail, and verifies again.
- Supports block-size override, force mode, and optional sleep delay.

Dependencies:
- Uses low-level `pread`/`pwrite`, arena head/trailer packing, SHA1, partition metadata parsing, and `unittoull`.

Notable details:
- `force` allows resealing even when the old checksum does not match, with a warning.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/reseal.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/round.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/round.c

Purpose: Provides a reusable “round” synchronization primitive for background server tasks.

Key behavior:
- `waitforkick` blocks a worker until another round is requested, then advances current/next counters.
- `kickround` requests a round and optionally waits until it completes.
- `delaykickround` and `delaykickroundproc` coalesce delayed kicks: if no newer kick arrives before the delay, a synchronous kick is issued.

Dependencies:
- Uses Plan 9 `QLock`, `Rendez`, sleep, and tracing.

Notable details:
- Used for tasks where repeated requests can be collapsed into one later pass, such as cache writeback.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/round.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/score.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/score.c

Purpose: Score helpers for Venti SHA1 content addresses.

Key behavior:
- Defines global `zeroscore`.
- `scoremem` computes SHA1 over a memory buffer.
- `strscore` parses a fixed-width hex score string into bytes.

Dependencies:
- Uses `libsec` SHA1 and Venti score constants.

Notable details:
- `needzeroscore` exists solely to force linking of `score.o` on OS X.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/score.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/sortientry.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/sortientry.c

Purpose: Builds a sorted temporary file of index entries derived from all arena clump directories.

Key behavior:
- `sortrawientries` initializes 256 external sort buckets, scans all arenas, fills a bloom filter, and sorts bucket contents into final index-entry order.
- `readarenainfo` reads `ClumpInfo` records in large chunks, converts them to `IEntry`, skips corrupt clumps from the sorted set, and marks bloom bits.
- `sprayientry` hashes each score into an in-memory bucket and flushes full buckets to chained chunks on disk.
- `sortiebucks` flushes buckets, allocates a final per-bucket buffer, reads chained bucket chunks, `qsort`s entries, and writes sorted entries to the temp partition.

Dependencies:
- Uses arena clump directories, `IEntry` pack/unpack, `hashbits`, `ientrycmp`, bloom filter marking, and partition I/O.

Notable details:
- Contains a debug `xabort()` path on bucket write failure.
- `freeiebucks` frees `ib->buf`, while the original allocation pointer is `ib->xbuf`; later sorting also reassigns `ib->buf`. This is a maintenance hazard in the allocator ownership model.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/sortientry.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/stats.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/stats.c

Purpose: Defines Venti server statistic descriptors, counters, history collection, and binning.

Key behavior:
- `statdesc` maps `NStat` counter indices to display names.
- `statsinit` allocates a 90,000-sample ring and starts `statsproc`.
- `statsproc` snapshots global `stats` once per second.
- `setstat`, `addstat`, and `addstat2` update counters under `statslock`.
- `binstats` turns historical samples into min/max/avg bins over an absolute or relative time interval.

Dependencies:
- Uses `Stats`, `Statbin`, stat IDs from `dat.h`, Plan 9 locks, and `vtproc`.

Notable details:
- `statdesc` must remain synchronized with `dat.h:/NStat`.
- `printstats` is currently empty.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/stats.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/stdinc.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/stdinc.h

Purpose: Common include umbrella for Venti server code.

Key behavior:
- Includes Plan 9 base, libc, Venti protocol, flate, libsec, thread, httpd, draw, and memdraw headers.

Dependencies:
- Establishes common system/library dependencies for the server subtree.

Notable details:
- No declarations of its own.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/stdinc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/syncarena.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/syncarena.c

Purpose: Synchronizes an arena’s in-memory/directory metadata with clumps found on disk.

Key behavior:
- `syncarena` scans clumps from the arena’s current `memstats.used`, validates clump magic, loads clumps, verifies scores/types, compares directory `ClumpInfo`, and updates `memstats`.
- Can mark broken clumps as `VtCorruptType` and rewrite clump headers/directories when `fix` is enabled.
- Reports header/directory/data/fix flags to callers.
- `writeclumphead` and `writeclumpmagic` perform targeted arena repair writes.

Dependencies:
- Uses arena clump loading, score computation, clump info reads/writes, disk cache flushing, and sync error flags.

Notable details:
- Treats a mismatched score in an uncompressed clump as likely partial write and stops rather than repairing through it.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/syncarena.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/syncindex.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/syncindex.c

Purpose: Command-line wrapper for synchronizing a Venti index.

Key behavior:
- Loads config and bloom filter, initializes disk/lump/index caches, optionally prints the index, calls `syncindex`, then flushes caches.
- Supports `-B` disk cache memory, `-I` index cache memory, and `-v`.

Dependencies:
- Uses `initventi`, `loadbloom`, `initdcache`, `initlumpcache`, `initicache`, `syncindex`, and cache flush helpers.

Notable details:
- Allocates a small 1 MiB lump cache for the maintenance run.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/syncindex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/syncindex0.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/syncindex0.c

Purpose: Core index synchronization logic used by the server and `syncindex` tool.

Key behavior:
- `syncindex` calls `syncarena` for each arena, tolerates header and clump-info zero/directory repairs as configured, then indexes newly discovered clumps.
- `syncarenaindex` reads clump info from the arena’s diskstats position to memstats position, constructs `IAddr`, inserts scores into the index, and advances arena stats.
- Writes updated arena metadata with `wbarena` and triggers delayed index-cache writeback.

Dependencies:
- Uses arena sync, clump info reading, score insertion, disk cache, index cache, and arena writeback.

Notable details:
- Corrupt clumps are not explicitly skipped here; indexing follows directory entries returned by `readclumpinfo`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/syncindex0.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/trace.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/trace.c

Purpose: Provides named trace categories and HTML log trace emission.

Key behavior:
- Defines trace category strings for disk, lump, block, proc, work, quiet, and rpc.
- `trace` formats messages into category-specific and all-category `vtlog` streams when `ventilogging` is enabled.
- `traceinit` and `settrace` are stubs.

Dependencies:
- Uses `vtlog`, thread names, Venti time formatting, and global `ventilogging`.

Notable details:
- Runtime trace filtering is not implemented here; category strings are passed through to log destinations.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/trace.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/unittoull.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/unittoull.c

Purpose: Parses unsigned integer strings with storage-size suffixes.

Key behavior:
- Accepts plain numeric strings plus `k`, `m`, `g`, or `t` suffixes.
- Returns all-ones `TWID64` on nil input or invalid trailing characters.

Dependencies:
- Uses Plan 9 integer types from `stdinc.h`.

Notable details:
- Parses the base number with `strtoul`, so very large inputs depend on host `ulong` width before suffix multiplication.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/unittoull.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/unwhack.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/unwhack.c

Purpose: Decompresses data encoded by the custom Venti `whack` compressor.

Key behavior:
- Maintains a bit buffer and decodes either literals or length/offset backreferences.
- Uses compact literal encoding influenced by recent literal history.
- Handles short and large match lengths, decodes offset classes, and copies from already produced output.
- Reports bounded errors through `Unwhack.err`.

Dependencies:
- Uses tables shared conceptually with `whack.c` and definitions from `whack.h`.

Notable details:
- Checks for too much output, offset before beginning of output, length overflow, and compressed data overrun.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/unwhack.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/utils.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/utils.c

Purpose: Miscellaneous Venti server utility functions.

Key behavior:
- Name helpers compare/copy/validate fixed-size arena names.
- Decimal parsing helpers detect overflow for 32-bit and 64-bit unsigned values.
- Error/log helpers format messages, optionally log by severity, and set `%r`.
- Allocation wrappers zero or poison memory, tag allocations, and abort/sysfatal on failure.
- Provides time, process creation, `IEntry` formatting, Venti formatter registration, millisecond clock, and bit counting.

Dependencies:
- Uses Plan 9 formatting, allocation tagging, thread process creation, Venti formatters, and server error conventions.

Notable details:
- `vtproc` ignores `proccreate` failure and always returns 0.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/utils.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/venti.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/venti.c

Purpose: Main Venti server executable.

Key behavior:
- Parses server options for addresses, config, web root, cache sizes, memory percentage, read-only mode, debug/foreground mode, logging, and queued writes.
- Loads config, bloom filter, sizes caches, initializes lump/index/disk caches, synchronizes the index, starts optional HTTP service and bloom/summing background tasks, then listens for Venti RPCs.
- `ventiserver` handles `VtTread`, `VtTwrite`, and `VtTsync` requests using `readlump`, `writelump`, and cache/queue flushes.
- Tracks RPC counters, byte counts, timing, cache hit/miss read timing, and failures.

Dependencies:
- Integrates almost all Venti server subsystems: config, index, bloom, caches, queues, HTTP, stats, tracing, and libventi server RPC.

Notable details:
- Automatic cache sizing uses observed free memory and subtracts bloom filter memory load.
- Read-only mode rejects writes and skips index synchronization.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/venti.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/verifyarena.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/verifyarena.c

Purpose: Verifies arena checksums and trailer consistency.

Key behavior:
- Can verify a single arena from stdin or selected arenas from an arena partition.
- Hashes arena data with the final score slot treated as zero, compares computed score to trailer score, and distinguishes sealed, unsealed, and mismatch cases.
- Validates header/trailer name and version consistency and prints arena metadata.

Dependencies:
- Uses raw file reads, arena partition parsing, arena head/tail unpacking, SHA1, and Venti formatting.

Notable details:
- Supports throttling via `-s ms`; `-v` is parsed but not used beyond incrementing a variable.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/verifyarena.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/whack.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/whack.c

Purpose: Custom LZ77-style compressor used by Venti.

Key behavior:
- `whackinit` sizes the hash-chain search limit from the compression level and initializes the dictionary state.
- `whackmatch` searches recent dictionary entries for a match within `WhackMaxOff`.
- `whack` emits literals or length/offset matches using variable-length encodings and updates compression statistics.
- Bails out when compression is disabled, input too small, output would exceed input size, or poor compression progress is detected.
- `whackblock` compresses one block with default level 6.

Dependencies:
- Uses structures/constants from `whack.h`; paired with `unwhack.c`.

Notable details:
- Match offset is limited to 16 KiB.
- `compressblocks` is a global switch.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/whack.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/whack.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/whack.h

Purpose: Public definitions for the `whack` compressor/decompressor.

Key behavior:
- Defines compressor stats count, error buffer length, max offset, hash table sizing, minimum match length, and decode constants.
- Defines `Whack` dictionary state and `Unwhack` error state.
- Declares `whackinit`, `unwhackinit`, `whack`, `unwhack`, and `whackblock`.

Dependencies:
- Used by `whack.c`, `unwhack.c`, and server code that selects compression.

Notable details:
- Compressor state contains a 16K hash table and 16K next-link table.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/whack.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/wrarena.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/wrarena.c

Purpose: Replays/copies clumps from an arena file into a Venti server.

Key behavior:
- Opens an arena file, initializes the arena, optionally connects to a Venti server, and starts multiple sender threads.
- `rdarena` walks clump directory entries, skips corrupt clumps and optional initial offsets, loads clumps, validates score/type unless `-f`, and sends valid clumps to sender threads.
- Sender threads call `vtwrite` and free zblocks.
- Supports host override, fast mode, max writes, verbose scores, and offset reporting.

Dependencies:
- Uses arena loading, clump info reads, `vtwrite`, `vtsync`, Venti connection APIs, channels, and stats/dcache initialization.

Notable details:
- Host `/dev/null` suppresses server connection and just reads/validates.
- Sender threads intentionally block at exit as a workaround for historical libthread/NPTL shutdown trouble.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/wrarena.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/www/stats.js -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/www/stats.js

Purpose: Client-side JavaScript for the Venti HTTP statistics dashboard.

Key behavior:
- Defines graph URL/name mappings for disk/network/I/O bandwidth, arena/index I/O, bloom filter, disk cache, index cache, lump cache, RPC timing, and stalls.
- Builds three graph columns and two large selected graphs via DOM table manipulation and `/graph?...` image URLs.
- Handles click selection of small graphs to replace the large graph.
- Renders settings links for logging, stats, compression mode, index/storage pages, and log pages.
- Sends setting changes by navigating a hidden frame to `/set/name/value`.

Dependencies:
- Expects server endpoints `/graph`, `/set`, `/index`, `/storage`, and `/log/...`.

Notable details:
- Uses old pre-modern JavaScript style: global variables, `new Array`, inline `javascript:` URLs, and `innerHTML`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/www/stats.js -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/www/status.js -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/www/status.js

Purpose: Loads initial Venti web status settings with numeric choices.

Key behavior:
- `loadsettings` sets logging off, stats on, compression to `whack`, compression choices to none/flate/smack/whack, and log names.
- Logging and stats choices are `"0"`/`"1"`.

Dependencies:
- Intended to be used by the web dashboard JavaScript settings renderer.

Notable details:
- Differs from `status1.js`, which uses textual `"off"`/`"on"` choices.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/www/status.js -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/www/status1.js -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/www/status1.js

Purpose: Defines default Venti web status settings as globals.

Key behavior:
- Sets logging on, stats on, compression to `whack`, compression choices, and log names.
- Logging and stats choices are `"off"`/`"on"`.

Dependencies:
- Intended for inclusion by the Venti HTTP UI.

Notable details:
- Contains no functions; it directly initializes global variables.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/www/status1.js -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/xml.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/xml.c

Purpose: Emits XML fragments for Venti arena/index metadata.

Key behavior:
- `xmlarena` writes an empty element with arena name, version, partition, block size, start/stop, created/modified times, sealed state, score, clump counts, and storage/data sizes.
- `xmlindex` writes index metadata and nested sections, arena maps, and arenas.
- `xmlamap` writes a map entry with name/start/stop.

Dependencies:
- Uses `Hio`, Venti index/arena structures, XML helper functions declared in `xml.h`, and clump size constants.

Notable details:
- Other XML scalar escaping/formatting helpers are declared in the header but implemented elsewhere.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/xml.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/xml.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/xml.h

Purpose: Declares XML output helpers for Venti HTTP/status code.

Key behavior:
- Declares complex emitters for `AMap`, `Arena`, and `Index`.
- Declares scalar helpers for arena names, scores, sealed flags, integers, and indentation.

Dependencies:
- Used by XML-producing server modules.

Notable details:
- Header only; implementations are split across `xml.c` and other server files.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/xml.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/zblock.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/zblock.c

Purpose: Manages aligned byte buffers (`ZBlock`) and packet conversion.

Key behavior:
- `alloczblock` allocates one raw block containing aligned data, overflow sentinel bytes, and the `ZBlock` descriptor.
- `freezblock` verifies the overflow sentinel before freeing.
- `packet2zblock` copies packet bytes into a zblock.
- `zblock2packet` creates a packet from zblock bytes.
- `fmtzbinit` initializes a formatter to write into a zblock buffer.

Dependencies:
- Uses Plan 9 `Fmt`, packet APIs, and server allocation/error conventions.

Notable details:
- Sentinel size is 32 bytes and aborts on overwrite detection.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/zblock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/zeropart.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/zeropart.c

Purpose: Zeros most of a Venti partition/device.

Key behavior:
- Allocates a zeroed `MaxIoSize` zblock and writes zeros from `PartBlank` to the partition end in large chunks, then block-size chunks.
- Flushes the partition and frees the zblock.

Dependencies:
- Uses `writepart`, `flushpart`, and `alloczblock`.

Notable details:
- Starts at `PartBlank`, preserving the initial partition area before that offset.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/zeropart.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/sync.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/sync.c

Purpose: Client utility that sends a Venti sync request.

Key behavior:
- Connects to a Venti server, performs `vtconnect`, optionally calls `vtsync`, then hangs up.
- `-h` selects host; hidden `-x` sets `donothing` and skips `vtsync`.

Dependencies:
- Uses libventi client APIs and Plan 9 thread main.

Notable details:
- Installs Venti score and fcall formatters for diagnostics.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/sync.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/words/dumpvacroots -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/words/dumpvacroots

Purpose: RC script to extract historical vac root scores from a Venti server.

Key behavior:
- Derives an HTTP host/port from `$venti`.
- Fetches `/index`, generates `venti/printarena` commands for arena ranges, executes them, and filters clumps of type `16` into `vac:<score>` output.

Dependencies:
- Uses `hget`, `sed`, `awk`, `rc`, and `venti/printarena`.

Notable details:
- Comment warns that physical disk access exposes stored vac roots.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/words/dumpvacroots -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/words/venti.conf -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/words/venti.conf

Purpose: Sample Venti configuration file.

Key behavior:
- Documents formatting commands for arenas, index sections, and index.
- Defines index name `main`, two index sections under `/tmp/disks`, and an arenas partition under `/tmp/disks/arenas`.

Dependencies:
- Used by `venti/venti` and formatting utilities.

Notable details:
- This is an example, not executable code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/words/venti.conf -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/words/wrtape -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/words/wrtape

Purpose: RC script to back up a range of Venti arenas to tape.

Key behavior:
- Computes arena range from tape number, rewinds tape device, fetches arena names from an HTTP index, locates their devices, logs backup progress, writes each arena with `venti/rdarena` piped through `scuzz`, writes file marks, then rewinds.

Dependencies:
- Uses `hoc`, `scuzz`, `hget`, `grep`, `sed`, `date`, `venti/rdarena`, and `/sys/log/ventibackup`.

Notable details:
- Hard-codes host `iolaire` and tape device `/dev/sd03`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/words/wrtape -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/write.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/write.c

Purpose: Client utility to write one data block from stdin to a Venti server.

Key behavior:
- Reads up to `VtMaxLumpSize+1`, rejects oversized input, connects to a server, optionally zero-truncates the block, writes it with selected Venti type, prints the returned score, and exits.
- Supports `-h host`, `-t type`, and `-z`.

Dependencies:
- Uses libventi connection/write APIs and score formatting.

Notable details:
- Defaults block type to `VtDataType`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/write.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vi/bpt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vi/bpt.c

Purpose: Breakpoint management for the Plan 9 MIPS interpreter/debugger.

Key behavior:
- Lists instruction, access, read, write, and equal-value breakpoints.
- Adds breakpoints with type suffixes, resolving addresses through the command expression parser.
- Deletes breakpoints by address.
- `brkchk` tests breakpoints on instruction/memory events and stops execution by setting `count` and `atbpt`.

Dependencies:
- Uses debugger globals, `symoff`, memory access helpers, and command parsing from `cmd.c`.

Notable details:
- In `delbpt`, deleting a non-instruction breakpoint increments `membpt`; this looks counterintuitive because adding one also increments it.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vi/bpt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vi/cmd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vi/cmd.c

Purpose: Interactive command interpreter for the MIPS simulator.

Key behavior:
- Parses adb-like commands for running, continuing, stepping, resetting, setting breakpoints, dumping registers, stack traces, instruction/stat summaries, expression evaluation, memory display, and register assignment.
- Supports symbolic and numeric expressions using `+`, `-`, `%`, `&`, and `|`.
- `pfmt` implements memory/value formats for octal, decimal, hex, bytes, chars, strings, symbols, instructions, source lines, and globals.
- Handles repeat counts and repeats the last command on blank input.
- Installs an interrupt note handler that stops the run loop.

Dependencies:
- Uses Plan 9 `Biobuf`, `mach` symbols, memory accessors, run loop, breakpoints, stats, and source/symbol helpers.

Notable details:
- This `vi` is a simulator/debugger command shell, not the visual editor.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vi/cmd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vi/float.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vi/float.c

Purpose: Implements MIPS COP1 floating-point instruction simulation.

Key behavior:
- Defines the COP1 function table for arithmetic, moves, conversions, and comparisons.
- Handles single, double, and word formats with register format tracking.
- Implements `lwc1`, `swc1`, `mfc1`, `mtc1`, branch-on-FP-condition, arithmetic ops, abs/neg/move, conversions, and condition comparisons.
- Sets or clears the FP condition bit in `fpsr` according to compare predicates and NaN handling.

Dependencies:
- Uses MIPS register state, memory accessors, instruction decode macros, tracing, and `isNaN`.

Notable details:
- Many COP1 operations are deliberately unimplemented and trap through `unimp`.
- Double register byte/word ordering is adjusted through register format state.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vi/float.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vi/icache.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vi/icache.c

Purpose: Placeholder instruction-cache simulation hooks.

Key behavior:
- `icacheinit` is empty.
- `updateicache` accepts an address and marks it used but performs no work.

Dependencies:
- Included by the simulator memory fetch path when `icache.on` is set.

Notable details:
- Instruction cache simulation is effectively disabled in this file.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vi/icache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vi/mem.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vi/mem.c

Purpose: Simulated memory/TLB/page mapping for the MIPS interpreter.

Key behavior:
- `ifetch` validates alignment, updates icache/profile counters, maps the page, and fetches big-endian instructions.
- Provides aligned and byte/half/word memory read/write helpers with breakpoint checks.
- `memio` copies strings/buffers between simulated and host memory.
- `dotlb` simulates a random-replacement TLB.
- `vaddr1` lazily maps text/data pages from the executable and zero-fills bss/stack pages.
- `vaddr` traps on unmapped addresses; `badvaddr` checks alignment and mapping.

Dependencies:
- Uses segment metadata from `mips.h`, executable fd `text`, profiler array, random functions, and longjmp-based traps.

Notable details:
- Memory is modeled as page tables per segment, with pages allocated on first touch.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vi/mem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vi/mips.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vi/mips.h

Purpose: Shared declarations and machine model for the MIPS simulator/debugger.

Key behavior:
- Defines breakpoints, TLB, instruction cache, instruction table entries, register file, floating register formats, multiply results, segment/memory structures, opcode decode macros, constants, prototypes, and globals.
- Defines Plan 9/MIPS user address constants, stack layout constants, and instruction dispatch macro `Iexec`.

Dependencies:
- Includes Plan 9 MIPS `ureg.h` and relies on `mach` library types.

Notable details:
- The register file stores GPRs, HI/LO, FPSR, and a union view over double/float/integer FP registers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vi/mips.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vi/run.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vi/run.c

Purpose: Main integer/control-flow instruction interpreter for MIPS.

Key behavior:
- Defines the primary opcode dispatch table.
- `run` repeatedly fetches, dispatches, advances PC, checks instruction breakpoints, and optionally traces registers.
- Implements loads/stores, arithmetic/logical immediates, jumps, branches, branch-likely variants, LL/SC as load/store, and `bcond` variants.
- Executes MIPS delay slots explicitly on taken branches and jumps.
- Tracks instruction counts and branch delay-slot usage.

Dependencies:
- Uses register state, memory accessors, special/COP1/syscall dispatch, breakpoints, tracing, and decode macros.

Notable details:
- Undefined opcodes print a trap and return to the command loop via `longjmp`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vi/run.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vi/special.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vi/special.c

Purpose: Implements MIPS SPECIAL opcode instructions.

Key behavior:
- Defines the secondary function dispatch table.
- Implements shifts, logical ops, set-less-than, add/sub variants, jumps through registers, syscall dispatch, HI/LO moves, multiply, and divide.
- Handles delay slots for `jr` and `jalr`.
- Treats `nor r0,r0,r0` as the simulator’s nop marker and counts nops.

Dependencies:
- Uses multiply helpers from `vi.c`, syscall handler, register state, tracing, source/call-tree helpers, and decode macros.

Notable details:
- Some instruction handlers decode destination register with masks wider than 5 bits, but operands originate from MIPS instruction fields.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vi/special.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vi/stats.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vi/stats.c

Purpose: Reports simulator execution statistics.

Key behavior:
- `isum` prints per-instruction counts and aggregate cycle/load/store/arithmetic/float/syscall/branch/delay-slot summaries.
- `tlbsum` prints TLB accesses, hits, misses, and hit rate.
- `segsum` prints segment base/end, resident bytes, and reference counts.
- `iprofile` aggregates instruction fetch profile counters by text symbol and prints hot functions with source locations.

Dependencies:
- Uses instruction tables from `run.c`, `special.c`, and `float.c`, segment state, TLB state, symbol lookup, and profile counters.

Notable details:
- `cop1` aggregate count is zeroed so floating-point operations are not counted twice.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vi/stats.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vi/symbols.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vi/symbols.c

Purpose: Source and stack-symbol support for the MIPS simulator.

Key behavior:
- `printsource` prints `file:line` for an address.
- `printlocals` and `printparams` use local symbol metadata to print frame locals and parameters.
- `stktrace` walks stack frames using `.frame` symbols, prints calls, source locations, and optionally locals.

Dependencies:
- Uses Plan 9 `mach` symbol APIs, simulated memory reads, register state, and debugger output.

Notable details:
- Stack traces stop at `_main` or after 40 frames.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vi/symbols.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vi/syscall.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vi/syscall.c

Purpose: Emulates Plan 9 MIPS system calls on the host.

Key behavior:
- Maps syscall numbers to names and handler functions.
- Implements common file/process-memory syscalls including errstr, fd2path, bind, chdir, close, dup, exits, open, read/pread, seek/oseek, rfork without RFPROC, sleep, stat/fstat old and new forms, write/pwrite, pipe, create, brk, remove, notify, and segflush.
- Copies syscall arguments/results between simulated stack/memory and host buffers.
- Unimplemented syscalls print a message and exit.

Dependencies:
- Uses `/sys/src/libc/9syscall/sys.h`, memory accessors, simulated registers, host Plan 9 syscalls, and debugger tracing.

Notable details:
- Many namespace/process syscalls are stubs, so simulated programs using mount, wait, exec, segment attach/detach, rendezvous, etc. will stop.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vi/syscall.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vi/vi.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vi/vi.c

Purpose: Main program and runtime setup for the Plan 9 MIPS interpreter/debugger.

Key behavior:
- Loads a MIPS executable or initializes from a live `/proc/<pid>` snapshot.
- Sets up text/data/bss/stack segment maps, symbols, initial stack/TOS, registers, and default floating constants.
- Provides process snapshot initialization from `/proc/<pid>/mem`, `/proc/<pid>/text`, and `/proc/<pid>/segment`.
- Implements fatal/error output, instruction tracing, register dumps, allocation wrappers, and 32x32-to-64 multiply helpers.

Dependencies:
- Uses Plan 9 `mach`, executable headers, proc files, memory helpers, command loop, and MIPS shared state.

Notable details:
- `reset` contains `for(i = 0; i > Nseg; i++)`, so the loop body never runs; segment page freeing appears ineffective.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vi/vi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vl/asm.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vl/asm.c

Purpose: MIPS linker backend assembly/output emitter.

Key behavior:
- Provides endian-aware byte/half/word/vlong output helpers.
- `entryvalue` resolves entry point names or numeric addresses.
- Emits multiple output header formats: Plan 9 boot images, Plan 9 MIPS a.out-style headers, and ELF32/ELF64 variants.
- `asmb` writes text instructions, padding/text holes, data, symbols, line tables, and final headers.
- `asmsym` emits text/data/bss/file/frame/auto/param symbols.
- `asmlc` emits compressed line-number tables.
- `datblk` materializes initialized data/string blocks from linker data progs with endian conversion.
- `asmout` converts linker `Prog` instructions to one or more MIPS machine words across many instruction templates.
- `oprrr`, `opirr`, and `vshift` map assembler opcodes to MIPS encoding fields.

Dependencies:
- Uses linker IR/state from `l.h`, opcode tables from the MIPS assembler headers, ELF helpers, symbol table, data progs, and output file descriptor `cout`.

Notable details:
- Supports both big- and little-endian MIPS output.
- Contains several synthesized-instruction paths for large constants/addresses and floating-point loads/stores.
- `opirr` aborts after reporting an unknown immediate-format opcode.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vl/asm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vl/compat.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vl/compat.c

Purpose: Compatibility allocation and utility shims for the linker.

Key behavior:
- Replaces `malloc` with hunk-based allocation from linker-managed memory.
- `free` is a no-op.
- `calloc` allocates through the hunk allocator and zeroes memory.
- `realloc` is unsupported and aborts.
- `mysbrk` wraps `sbrk`.
- `setmalloctag` is a no-op.
- `fileexists` tests whether `stat` succeeds.

Dependencies:
- Uses linker globals `hunk`, `nhunk`, and `gethunk` from the linker core.

Notable details:
- Designed for linker lifetime allocation, not general-purpose memory management.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vl/compat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vl/l.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vl/l.h

Purpose: Central declarations for the Plan 9 MIPS linker.

Key behavior:
- Defines linker address, program, symbol, auto, opcode table, opcode range, and count structures.
- Defines symbol classes, operand classes, scheduler flags, sizing constants, and global state.
- Declares output layout parameters, buffers, current program/text state, symbol hash, library lists, op tables, debug flags, and statistics.
- Declares all major linker passes and helpers.

Dependencies:
- Includes Plan 9 headers, MIPS object definitions from `../vc/v.out.h`, and ELF definitions from `../8l/elf.h`.

Notable details:
- Uses the Plan 9 style `EXTERN` pattern so the same header can define or declare globals depending on including source.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vl/l.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vl/list.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vl/list.c

Purpose: Formatting and diagnostics for linker programs and operands.

Key behavior:
- `listinit` installs custom formatters for assembler opcodes, addresses, programs, strings, and name-bearing addresses.
- `Pconv` formats a `Prog` instruction, including scheduler marker and optional third register.
- `Aconv` maps opcode numbers to assembler names.
- `Dconv` formats address modes and constants.
- `Nconv` formats symbol-relative names such as SB/SP/FP references.
- `Sconv` escapes fixed-size string constants.
- `diag` prints current text symbol context, increments error count, and exits after too many errors.

Dependencies:
- Uses linker structures/globals from `l.h`, assembler name table, and Plan 9 formatting.

Notable details:
- Diagnostic context defaults to the current function symbol when available.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vl/list.c -->