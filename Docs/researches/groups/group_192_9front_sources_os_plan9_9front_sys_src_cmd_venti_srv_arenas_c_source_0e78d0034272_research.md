# Group Research: group_192_9front_sources_os_plan9_9front_sys_src_cmd_venti_srv_arenas_c_source_0e78d0034272

Scope checked against `Docs/research_subset_a.md`: `sources/os/plan9/9front` is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/arenas.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/arenas.c

Implements arena partition registration, arena map parsing/writing, and name lookup for Venti arena objects.

Key behavior:
- Maintains a fixed 512-bucket in-memory hash table from arena name to `Arena*` via `addarena`, `findarena`, and `delarena`.
- `initarenapart` reads the arena partition header from `PartBlank`, validates version/block geometry, reads the text arena map, initializes every listed arena, verifies map name matches arena header name, rejects duplicate arena names, then adds arenas to the global lookup table.
- `newarenapart` creates a blank arena partition layout, calculating table and arena bases from `PartBlank`, `HeadSize`, block size, and requested table size.
- `wbarenapart` writes both the packed arena partition header and arena map table back to disk after validating non-overlapping ranges.
- `okamap` enforces monotonically increasing, non-overlapping address ranges within bounds.
- `readarenamap` and `wbarenamap` adapt partition regions to `IFile`/`Fmt` text parsing and output.
- `parseamap` parses a count followed by tab-separated `name start stop` records, validates names and `MaxAMap`, and stores `AMapN`.
- `outputamap` emits the exact text form expected on disk.

Interactions:
- Depends on `conv.c` for packed arena partition headers.
- Depends on `ifile.c` for input abstraction.
- Used by config/index setup, formatters, checkers, and repair tools.

Notable details:
- `debugarena` is updated while initializing arenas to improve error messages.
- A failure after some arenas were added calls `freearenapart(..., 1)`, which attempts `delarena` for initialized arenas.
- `wbarenapart` has a `/* ZZZ set error message? */` comment on allocation failure.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/arenas.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/bloom.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/bloom.c

Implements the optional on-disk/in-memory Bloom filter used to avoid index lookups for definitely absent scores.

Key behavior:
- `bloominit` initializes size, default hash count, optional packed header parsing, bitmask, and data pointer.
- `readbloom` reads the first 512 bytes to parse the header, then bumps partition block size up to as much as 1 MiB for large Bloom I/O.
- `resetbloom` allocates a zeroed in-memory filter and updates bit-count stats.
- `loadbloom` reads the whole filter, counts set bits, and updates Bloom stats.
- `writebloom` packs the header into `b->data`, writes the whole filter to its partition, and flushes.
- `gethashes` derives up to 32 hash positions from a score using double-hashing style `a + b*i`, reserving header bits.
- `markbloomfilter` and `inbloomfilter` protect access with `RWLock lk`; marking also uses `QLock mod`.
- `startbloomproc` launches a background writer that waits on `writechan`, writes the filter, and signals completion.

Interactions:
- `icache.c` marks Bloom entries on dirty score insertion.
- `buildindex.c` can rebuild Bloom from arenas.
- `checkindex.c` compares/fixes Bloom contents.
- Packed header format is in `conv.c`.

Notable details:
- If Bloom is nil, unloaded, or `ignorebloom` is set, lookup returns “possibly present” to preserve correctness.
- `MaxBloomSize` has a special stat path because `size*8` can overflow `ulong`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/bloom.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/buildbuck.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/buildbuck.c

Provides stream-to-bucket assembly for sorted packed index entries.

Key behavior:
- Defines opaque `IEStream`, a buffered stream over sorted packed `IEntry` records stored on a `Part`.
- `initiestream` records partition, offset, remaining entry count, and allocates the read buffer.
- `peekientry` refills the buffer, preserving partial records, and returns the current packed `IEntry`.
- `iebuck` maps a packed score to an index bucket via `hashbits(score, 32) / ix->div`.
- `buildbucket` consumes consecutive entries for the same bucket into an `IBucket`, detects duplicate score/type entries, and keeps the one with the larger arena address.

Interactions:
- Used by `checkindex.c` to build expected buckets from sorted raw entries.
- Depends on packed `IEntry` layout where score is first.

Notable details:
- Duplicate index entries set an expected-operation error and choose the larger address as likely newer/correct.
- Returns `TWID32` on end/error/overflow.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/buildbuck.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/buildindex.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/buildindex.c

Command-line utility to rebuild the Venti index from arenas, optionally rebuilding Bloom too.

Key behavior:
- `threadmain` parses `-b`, `-d`, `-i isect`, `-M imem`, and debug `-m`, initializes Venti config, forces arena parts read-only, allocates dcache, starts one index-section worker per selected `ISect`, and one arena-part worker per arena partition.
- `arenapartproc` scans arena clump directories in reverse clump order, reconstructs `IEntry` addresses, skips `VtCorruptType`, sends entries to the correct index section, and marks Bloom entries.
- Bucket mapping uses score hash divided by `ix->div`; helpers convert score, bucket, and section offset.
- `isectproc` performs a three-pass rebuild:
  1. receive entries and spill them into large sequential group buffers on the index partition;
  2. optionally redistribute group buffers into minibuffers using `IPool`;
  3. sort each minibuffer by packed entry ordering with address tie-breaks, then write final buckets.
- `sortminibuffer` compacts fragment-padded spill blocks, sorts entries, groups by bucket, writes `IBucket` blocks, and optionally zeroes bucket gaps.
- Memory sizing chooses group/minigroup counts and buffer size from `isectmem`, `MinBufSize`, and `MaxBufSize`.

Interactions:
- Reuses `buildbuck.c` comparison logic concepts but writes final disk buckets directly.
- Uses `readclumpinfos`, `packientry`, `packibucket`, `markbloomfilter`, and partition I/O.
- Updates global counters `arenaentries`, `skipentries`, and `indexentries`.

Notable details:
- Many invariants are enforced with `assert`/`sysfatal`; bucket overflow means “make index bigger”.
- `-d` forces all passes for debugging even when a single pass would fit.
- `-i` can rebuild only selected index sections.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/buildindex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/checkarenas.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/checkarenas.c

Command-line arena header consistency checker and optional fixer.

Key behavior:
- `checkarena` optionally resets in-memory stats for a full scan, repeatedly calls `syncarena`, compares recomputed `memstats` with old values, and reports incorrect arena header fields.
- With `-f`, writes corrected arena header fields by copying `memstats` to `diskstats`, calling `wbarena`, and flushing dcache.
- `-a` enables full scan/recompute mode.
- `-v` prints arena details and progress.
- Optional arena-name arguments restrict which arenas are checked.

Interactions:
- Uses `initarenapart`, `syncarena`, `printarena`, `wbarena`, and dcache.
- Opens the arena partition read-only unless fixing.

Notable details:
- `syncarena` is called repeatedly while it reports `SyncHeader`, allowing progressive header repair/checking.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/checkarenas.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/checkindex.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/checkindex.c

Command-line checker comparing current on-disk index and Bloom filter against a freshly built sorted entry list.

Key behavior:
- Builds expected raw sorted index entries with `sortrawientries`.
- `checkindex` streams expected entries with `IEStream`, builds expected buckets with `buildbucket`, and compares each bucket to the live index.
- When zero checking is enabled, verifies empty buckets too.
- `checkbucket` reads an on-disk bucket, compares expected versus actual entries, and prints extra, missing, or wrong-address entries.
- `checkbloom` compares old and newly built Bloom filters, reports extra/missing bits, and with `-f` replaces the old filter.
- CLI supports `-B blockcachesize`, `-f`, and `-Z` to skip zero-bucket checking.

Interactions:
- Depends on `buildbuck.c`, `bloom.c`, `dcache.c`, and raw index sorting from elsewhere in the server.
- Uses a temporary partition argument to hold sorted entries.

Notable details:
- Error counters distinguish spurious entries, missing entries, and address mismatches.
- `/* ZZZ make buffer size configurable */` notes fixed 64 KiB stream buffer.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/checkindex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/clump.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/clump.c

Implements clump storage and loading: Venti’s immutable content block format inside arenas.

Key behavior:
- `storeclump` validates lump size/type, prepares a `Clump`, compresses with `whackblock` when useful, writes through `writeiclump`, and fills returned `IAddr`.
- Stored data layout is `Clump` header followed by compressed or raw data and four zero bytes.
- `clumpmagic` reads and unpacks the magic at an arena offset.
- `loadclump` reads enough arena data for a clump, unpacks the header, rejects `VtCorruptType`, reads more data if the initial block estimate was too short, decompresses if needed, and optionally verifies SHA-1 and type.

Interactions:
- Uses `whack.h` compression/decompression.
- Uses `readarena`, `writeiclump`, `pack/unpackclump`, and score helpers.
- Called from request lookup/debug paths and write path.

Notable details:
- For uncompressed clumps it computes a pre-copy SHA-1 and records an error if wrong, then copies data; final verification is controlled by `verify`.
- `blocks` is treated as a rough I/O estimate and raised to at least 1.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/clump.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/clumpstats.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/clumpstats.c

Command-line utility producing a histogram of clump sizes by Venti type.

Key behavior:
- Global `count[VtMaxLumpSize][VtMaxType]` stores frequency by uncompressed size and type.
- `readarenainfo` reads clump-info directories in 32K-entry chunks, validates type/size range, and increments counts.
- `clumpstats` iterates all arenas in the main index, totals clumps, and prints rows for nonzero sizes.
- Supports `-B blockcachesize`.

Interactions:
- Initializes Venti config, dcache, and uses `readclumpinfos`.

Notable details:
- Bad clump metadata is printed and skipped rather than aborting immediately.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/clumpstats.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/cmparenas.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/cmparenas.c

Command-line byte comparator for two arena partitions with identical arena tables.

Key behavior:
- Reads both arena-part headers/tables and requires exact table equality.
- Iterates listed or all arenas from the table.
- `cmparena` reads arena headers, validates version/length/name, prints decoded header/tail layout, then scans both arena byte ranges block by block and prints hex diffs for mismatching 16-byte chunks.
- `printheader` decodes the arena tail to print data, clump-directory, and tail ranges.
- `-b` controls compare block size, `-s` parses sleep milliseconds but is not used, and `-v` only sets a global not otherwise used meaningfully.

Interactions:
- Uses `unpackarenapart`, `unpackarenahead`, `unpackarena`, and `printarena`.

Notable issues:
- The second header parse after reading `fd1` calls `unpackarenahead(&head, data)` instead of `data1`, so validation of the second arena header appears to incorrectly re-parse the first buffer.
- `fd1` open failure reports `argv[0]` instead of `argv[1]`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/cmparenas.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/config.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/config.c

Parses Venti server configuration and initializes the global `mainindex`.

Key behavior:
- `initventi` initializes stats, runs config parsing, creates the `Index` from configured sections, and attaches optional Bloom.
- `runconfig` accepts lines for `isect`, `arenas`, `bloom`, `index`, `bcmem`, `mem`, `icmem`, `queuewrites`, `httpaddr`, `webroot`, and `addr`.
- Rejects duplicate singleton settings and illegal names/sizes.
- Dynamically grows arrays of arena partitions and index sections.
- `configisect`, `configarenas`, and `configbloom` open configured files with `initpart` and initialize corresponding objects.

Interactions:
- Uses `IFile` parsing from `ifile.c`.
- Uses `initisect`, `initarenapart`, `readbloom`, and `initindex`.
- Exports global `Index *mainindex`.

Notable details:
- `numok` effectively accepts parsed numbers with optional K/M/G suffixes but currently returns 0 even for trailing non-suffix data due to final `return 0`; caller still uses `unittoull`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/config.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/conv.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/conv.c

Defines packed on-disk format conversion for arena partitions, arenas, clumps, index sections, index entries, buckets, and Bloom headers.

Key behavior:
- Uses explicit big-endian `U8/U16/U32/U64` get/put macros.
- `unpack/packarenapart` handle arena partition superblock.
- `unpackarena` and `_packarena` handle arena trailer formats v4/v5 plus v5a extension fields for `memstats`.
- `unpackarenahead` and `packarenahead` handle redundant arena header.
- `unpackclump`/`packclump` and `unpackclumpinfo`/`packclumpinfo` handle clump metadata.
- `unpackisect`/`packisect` handle index-section headers v1/v2 and optional bucket magic.
- `unpackientry`/`packientry` handle packed index entries.
- `unpackibucket`/`packibucket` handle bucket entry count and bucket magic.
- `unpackbloomhead`/`packbloomhead` handle Bloom metadata.

Compatibility details:
- Arena v4 loses custom clump magic and uses `_ClumpMagic`.
- Arena memstats extension is omitted when equal to diskstats; pack clears old extension bytes to avoid stale fields.
- Unpack has a specific compatibility fix for sealed diskstats with stale unsealed memstats.

Notable issues:
- `unpackientry` contains a debug print when the high byte of `ia.addr` is nonzero.
- Conversion functions `sysfatal` on internal size mismatches, making packed-size definitions critical.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/conv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/dat.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/dat.h

Central data model and constants for the Venti server storage subsystem.

Key contents:
- Defines sentinel values `TWID32`, `TWID64`, and `TWID8`.
- Defines storage geometry constants: `ABlockLog`, `ANameSize`, `MaxDiskBlock`, `PartBlank`, `HeadSize`, `MinArenaSize`, `IndexBase`, `MaxAMap`, and I/O/cache limits.
- Defines error severities and `syncarena` return bits.
- Defines on-disk magic numbers, versions, encodings, and packed structure sizes.
- Defines dirty write-order stages: `DirtyArena`, `DirtyArenaCib`, and `DirtyArenaTrailer`.
- Declares primary structs:
  - `Config`, `Part`, `DBlock`, `Lump`
  - `AMap`, `AMapN`, `ArenaPart`, `Arena`, `ArenaHead`, `ATailStats`, `AState`
  - `ClumpInfo`, `Clump`
  - `Index`, `ISect`, `IAddr`, `IEntry`, `IBucket`
  - `ZBlock`, `IFile`, `Stats`, `Graph`, `Round`, `Bloom`
- Defines stats enum `NStat` and stat indices used by HTTP graphs and caches.
- Declares global tunables and state such as `mainindex`, `maxblocksize`, `readonly`, `compressblocks`, `manualscheduling`, `ignorebloom`, and sleep times.

Notable details:
- Comments document Venti’s append-only arena model and index mapping.
- `IEntrySize` and `IBucketSize` are intentionally compact but noted as CPU-costly due to unaligned byte copying.
- `ArenaCIGSize` drives arena-summary cache group size.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/dcache.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/dcache.c

Implements the raw disk block cache and ordered write-behind flushing.

Key behavior:
- `initdcache` allocates fixed-size cache blocks sized to `maxblocksize`, a hash table, an LRU-ish heap, write arrays, and starts flush/delay procs.
- `_getdblock` looks up blocks by `(Part*, addr)`, loads data on miss, upgrades locks as needed, and creates per-part write threads lazily for write modes.
- `putdblock` releases block read/write lock and returns clean unreferenced blocks to the victim heap.
- `dirtydblock` marks a block with a dirty phase and schedules flushes based on dirty count.
- Victim selection uses `used2` second-most-recent timestamp in a heap.
- `flushproc` collects dirty blocks, sorts by dirty phase, partition, and address, writes each phase in order via `parallelwrites`, flushes partitions, then marks blocks clean/heapable.
- `writeproc` serializes writes for one partition and updates write stats.
- `emptydcache`, `flushdcache`, `kickdcache`, and `checkdcache` expose maintenance and invariant checks.

Interactions:
- Arena writes use dirty phase ordering to ensure data, clump-info blocks, and trailer write in safe order.
- Index writes bypass dcache dirtying and update cached copies through `_getdblock(..., load=0)` in `icachewrite.c`.

Notable details:
- File-level lock ordering rules are documented: cache lock may be taken while holding a block lock, not the reverse.
- A comment says new-block usage timestamp heuristic is “not reasonable”.
- `flushpart` errors inside `parallelwrites` are not handled beyond a comment.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/dcache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/disksched.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/disksched.c

Adaptive disk scheduling helper that throttles background index-cache and arena-summary work.

Key behavior:
- Tracks recent disk access timestamps at two levels via `lasttime[0]` and `lasttime[1]`.
- `disksched` adjusts `icachesleeptime` and `arenasumsleeptime` based on foreground disk activity, index-cache dirty fraction, and recent flush rate.
- During level-0 activity, arena sums are paused and index flushing is delayed unless dirty fraction is high.
- During level-1 activity, index flushing can continue but arena sums stay paused.
- With no recent activity, both sleep times go to zero.
- `diskaccess(level)` records current time for a disk activity level.

Interactions:
- Called from `icachewrite.c` during index flush loops.
- Disk read/write paths call `diskaccess`.

Notable details:
- `manualscheduling` disables adaptive changes.
- Uses stats history over the last minute when available.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/disksched.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/dump.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/dump.c

Small diagnostic print helpers for core Venti structures.

Key behavior:
- `printindex` prints index name/version/blocksize/table size, bucket divider, section bucket ranges, and arena address ranges.
- `printarenapart` prints arena partition metadata and arena map entries.
- `printarena` prints arena range, version, timestamps, sealed status, optional score, clump counts, data sizes, compressed data, and storage usage.

Interactions:
- Used by check tools and verbose diagnostics.

Notable details:
- `printarena` takes an `fd` argument but several lines print to file descriptor 2 directly.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/dump.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/findscore.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/findscore.c

Command-line brute-force score search across an arena partition.

Key behavior:
- Parses a Venti score string and opens an arena partition read-only.
- Initializes arenas and dcache.
- `findscore` scans each arena’s clump-info directory in chunks, compares scores, and prints clump number, type, sizes, and running data position for matches.
- Prints total occurrences.

Interactions:
- Uses `initarenapart`, `readclumpinfos`, and `strscore`.

Notable details:
- `clumpinfoeq` is defined here and also declared twice in `fns.h`.
- Has a `//ZZZ remove fprint?` comment near unconditional directory progress printing.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/findscore.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/fixarenas.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/fixarenas.c

Large recovery utility for damaged arena partitions or standalone arenas.

Key behavior:
- Can run read-only or with `-f` to write repairs. Supports arena size/block size hints, base name override, unsealing, verbose output, and dumping recovered arenas.
- `readdisk` handles failed reads by retrying progressively smaller chunks down to 512-byte sectors, filling unreadable regions with marker bytes and coalescing bad-sector reports.
- Uses a 4 MiB mutable paging buffer; edits are written back only when `fix` is enabled.
- `Shabuf` maintains SHA-1 state, optional debug dump output, and rollback checkpoints every 4 MiB for resealing after edits.
- `guessgeometry` scans surviving arena heads/tails to infer arena size, block size, and arena base when the partition header is corrupt.
- `checkarenas` validates/rewrites the arena partition superblock and checks selected arena ranges.
- `isclump` validates candidate clumps by magic/type/sizes, decompression if compressed, and SHA-1 score.
- Maintains recovered clump-info entries in `cibuf`, with a score tree for duplicate detection.
- `guessarena` reconstructs arena basics, scans clump data, zeros corrupt regions when fixing, creates corrupt clump-info entries as needed, reconstructs/writes clump-info directory, recomputes stats, and optionally reseals.
- `checkarena` compares packed header/tail/seal against reconstructed values and writes corrected blocks when fixing.
- `checkmap` rebuilds the arena partition map from recovered arena headers and rewrites it if different.

Interactions:
- Reuses pack/unpack routines from `conv.c`, compression from `whack.h`, and arena map output logic.
- More tolerant than normal server code because it must recover past local corruption.

Notable issues:
- `vlongcmp` appears wrong: after `if(a < b) return -1;`, it checks `if(b > a) return 1;`, which repeats the same condition rather than checking `a > b`.
- Contains unconditional debug prints such as `old arena: sealed=...` and `eoffset=...`.
- Comments note unfinished geometry/table improvements.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/fixarenas.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/fmtarenas.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/fmtarenas.c

Formats an arena partition and creates evenly spaced arenas.

Key behavior:
- CLI: `fmtarenas [-Z] [-b blocksize] [-a arenasize] name file`, plus `-4` for old arena version and `-D` trace.
- Defaults: 8 KiB block size, 512 MiB arena size, 512 KiB arena table, arena version 5.
- Optionally zeroes the partition.
- Creates a new `ArenaPart`, calculates number of arenas from available partition size and `MinArenaSize`, creates each arena with name template plus index, fills `AMap`, then writes the arena partition header/table.

Interactions:
- Uses `newarenapart`, `newarena`, `wbarenapart`, dcache.

Notable details:
- Comment notes table size should be determined from number of arenas instead of fixed 512 KiB.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/fmtarenas.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/fmtbloom.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/fmtbloom.c

Formats a Bloom filter partition/file.

Key behavior:
- CLI supports `-s size`, `-n nblocks`, and `-N nhash`.
- Defaults to full partition size and max hash count unless block count drives sizing.
- Enforces minimum 1 MiB, caps to `MaxBloomSize`, rounds down to a power of two, and may shrink if bits per block are excessive.
- Chooses near-optimal hash count as roughly `0.7 * bits-per-block`, capped at `BloomMaxHash`.
- Initializes Bloom header/data and writes it to disk.

Interactions:
- Uses `bloominit` and `writebloom`.

Notable details:
- Prints warnings when only part of the file/partition is used.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/fmtbloom.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/fmtindex.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/fmtindex.c

Formats or extends the logical Venti index mapping over configured index sections and arenas.

Key behavior:
- CLI: `fmtindex [-a] config`.
- Parses config, validates index name, counts all arenas across configured arena partitions.
- Without `-a`, creates a new index over the configured index sections.
- With `-a`, loads an existing index and appends newly configured arenas, requiring existing arena slots and addresses to match.
- Assigns index address ranges beginning at `IndexBase`, sized by arena size.
- Writes the index config/table with `wbindex`.

Interactions:
- Uses `runconfig`, `initindex`, `newindex`, and arena mappings from configured `ArenaPart`s.

Notable details:
- Fails hard on arena-order mismatch or address discontinuity in append mode.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/fmtindex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/fmtisect.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/fmtisect.c

Formats a physical index-section partition/file.

Key behavior:
- CLI: `fmtisect [-Z] [-b blocksize] name file`, plus `-1` for old section version.
- Defaults: 8 KiB block size, 512 KiB section table size, `ISectVersion2`.
- Optionally zeroes the partition.
- Creates a new `ISect` and writes its header/table with `wbisect`.
- Prints bucket count, entries per bucket, and table size.

Interactions:
- Uses `newisect`, `zeropart`, and `wbisect`.

Notable details:
- Version 1 defaults to zeroing, version 2 defaults not to zero unless `-Z`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/fmtisect.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/fns.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/fns.h

Central prototype header for the Venti server storage subsystem.

Key contents:
- Declares arena, arena partition, arena summary, index, index-section, cache, Bloom, clump, config, HTTP, stats, formatting, I/O, and utility functions.
- Exposes low-level disk functions `readpart`, `writepart`, `flushpart`, `initpart`, and block cache operations.
- Exposes index cache operations `icachelookup`, `insertscore`, `icachedirty`, `icacheclean`, and background flush controls.
- Declares pack/unpack conversion routines from `conv.c`.
- Declares command-support helpers such as `printarena`, `printindex`, and `ventifmtinstall`.
- Defines convenience macros `scorecmp`, `scorecp`, and allocation wrappers `MK`, `MKZ`, `MKN`, `MKNZ`, `MKNA`.

Notable details:
- `clumpinfoeq` is declared twice.
- Comment on `readpart`: return value is success byte count unless negative, but asking for `n == -1` always reports failure.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/graph.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/graph.c

Renders historical server statistics into in-memory PNG-ready graph images.

Key behavior:
- Initializes draw subsystem, small font, repeated color images, and fill palettes lazily under `memdrawlock`.
- `statgraph` accepts a `Graph` descriptor, chooses default dimensions, bins stats with `binstats`, computes min/max, draws axis/labels, and renders min-to-max vertical bars with two-color fills.
- Supports caller-specified min/max, time range, size, and fill palette index.

Interactions:
- Used by `httpd.c` `/graph` endpoint, then encoded with `writepng`.

Notable details:
- Uses a 2000-bin stack array and calls `needstack(8192)`.
- If graph width exceeds bin count, it is clamped.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/graph.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/hdisk.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/hdisk.c

HTTP disk inspection and score-debug support for the Venti admin server.

Key behavior:
- `/disk` without args lists arena partitions, index sections, and Bloom partition from `mainindex`.
- `/disk?disk=...&type=a` opens an arena partition read-only, decodes the arena-part header/table, lists arenas, or inspects a selected arena.
- Arena inspection decodes header/tail, prints stats, and either lists clump-info TOC, finds a score in the TOC, or decodes a clump by offset.
- `diskarenaclump` reads a clump, tries alternate magic if magic mismatch, decompresses when needed, and recomputes score.
- `hdebug` supports `op=amap`, `op=mem`, and `op=read`.
- `debugread` compares icache, on-disk index, lookupscore, arena mapping, and clump load results for a score; optional brute-force arena search.

Interactions:
- Registered by `httpd.c` at `/disk` and `/debug`.
- Uses `initpart`, unpackers, `icachelookup`, `loadientry`, `lookupscore`, `amapitoa`, `loadclump`, and `findintoc`.

Notable details:
- `diskbloom` and `diskisect` are stubs.
- The `disk` query parameter is opened as a path with no visible authorization in this file; trust depends on how the admin HTTP service is exposed.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/hdisk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/hproc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/hproc.c

HTTP `/proc` debugger exposing process, thread, stack, symbol, segment, and file-descriptor views of the running Venti process.

Key behavior:
- Uses Plan 9 `/proc`, libmach, and libthread internals to open self text, map memory, resolve symbols, inspect registers, and walk stacks.
- Serves endpoints under `/proc/`: `all`, `segment`, `fd`, `procs`, `threads`, `stacks`, and `symbols`.
- `procapply` walks the libthread process queue `_threadpq`.
- `threadapply` maps each proc pid and walks its thread queue.
- `threadfmt` prints thread pointer, state, likely source line, moribund status, and command name.
- `stacktracepcsp`/`ptrace` print function calls, parameters, locals, and source lines.

Interactions:
- Registered by `httpd.c` for prefix `/proc/`.
- Depends on specific libthread internal structs and jump-buffer offsets.

Notable details:
- A single static 64 KiB output buffer is protected by `debug.lock`; concurrent requests report debugger busy.
- This is an introspection/admin endpoint and should not be exposed to untrusted clients.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/hproc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/httpd.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/httpd.c

Built-in HTTP admin server for Venti status, control, graphs, logs, disk/debug views, and static files.

Key behavior:
- `httpdinit` registers endpoints: `/stats`, `/index`, `/storage`, `/xindex`, cache flush/kick/empty routes, `/graph`, `/set`, `/log`, `/disk`, `/debug`, and `/proc/`.
- `listenproc` announces, accepts connections, and starts one `httpproc` per connection.
- `httpproc` parses requests, dispatches by exact or prefix route, falls back to static file serving from `webroot`, supports keep-alive/chunking.
- `hsettype`, `hsethtml`, `hsettext`, and `hnotfound` handle HTTP response boilerplate.
- `fromwebdir` serves static files, blocks `..`, defaults directories to `index.html`, and chooses content type by extension.
- `/set` reads or writes runtime integer tunables including compression, devnull writes, logging, stats, scheduling, Bloom ignore, sync writes, and icache prefetch.
- `/storage` and `/index` summarize arena/index state.
- Cache routes empty, kick, or flush lump/disk/index caches.
- `/graph` renders stat graphs as PNG or text, supporting raw/diff/pct/bandwidth graph functions.
- `/log` lists and dumps Venti logs.
- `/xindex` emits XML index data.
- Also contains XML helper attribute writers and HTTP log rendering helpers.

Interactions:
- Calls `hdisk`, `hdebug`, `hproc`, `statgraph`, `writepng`, cache maintenance functions, and stats history.
- `graphname` must stay in sync with the stats enum in `dat.h`.

Notable details:
- No authentication or authorization is visible in this file; endpoints can mutate runtime settings and flush caches.
- `fromwebdir` path filtering is minimal: only `..` substring is rejected.
- `/stats` body is mostly commented out; current handler mainly sets text response and flushes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/httpd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/icache.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/icache.c

Implements the in-memory index-entry cache and arena-summary prefetch cache.

Key behavior:
- `initicache` sizes the main cache from memory, reserves about one eighth for summary cache, initializes clean/dirty/free lists, hash tables, and summary slots.
- Main cache stores `IEntry` records in free, clean LRU, and dirty lists.
- `icachelookup` checks main hash first, then summary-cache hash; summary hits are promoted into the main clean cache.
- `insertscore` inserts clean or dirty entries, updates newest dirty arena state for flush safety, schedules flushes, and marks Bloom for dirty inserts.
- `lookupscore` checks cache, then loads from disk index via `loadientry` and inserts a clean entry.
- `icachedirty` returns dirty entries in a hash range and below an address limit for index-section writers.
- `icacheclean` moves written dirty entries to the clean list and wakes waiters.
- `emptyicache` evicts clean entries and clears summary cache.
- Summary cache (`ISum`) tracks arena clump-info groups; first miss reserves a group, second miss loads `asumload` entries if prefetch is enabled.

Interactions:
- Used by read/write lookup paths, `icachewrite.c`, HTTP debug, and Bloom update.
- Summary cache depends on arena summary loading and `amapitoag`.

Notable details:
- Dirty insert without `AState` prints a warning; dirty address moving backward also prints.
- If no cache entry can be evicted, insertion waits after kicking dcache/icache flushes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/icache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/icachewrite.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/icachewrite.c

Background writer for dirty index-cache entries.

Key behavior:
- `initicachewrite` creates a `Round`, starts one writer proc per index section, starts a coordinator, and starts delayed kick handling.
- `icachewritecoord` waits for kicks, snapshots the newest safe arena state from `icachestate`, sends work to all index-section writers and Bloom writer, waits for completion, then advances arena tail state with `setatailstate`.
- `icachewritesect` gets dirty entries for one section range, sorts them by score, chunks nearby disk buckets into up to 8 MiB reads, updates/creates bucket entries in memory, writes the chunk back, updates any dcache-resident bucket copies, and marks entries clean.
- `nextchunk` groups dirty entries whose target bucket blocks fall within `Bufsize`.
- `iesort` merge-sorts dirty single-linked lists by score.
- Exposes `flushicache`, `kickicache`, and `delaykickicache`.

Interactions:
- Uses `disksched` to throttle writes.
- Uses `icachedirty`, `icacheclean`, `bucklook`, `packientry`, `packibucket`, and `_getdblock`.
- Coordinates Bloom write via `ix->bloom->writechan`.

Notable details:
- Bucket overflow and bad bucket paths print `XXX` diagnostics and skip affected dirty entries from that chunk.
- Flush only advances arena tail state if all section/Bloom writes succeed.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/icachewrite.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/ifile.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/ifile.c

Simple text input abstraction for config files and text tables stored either as normal files or embedded in partitions.

Key behavior:
- `readifile` opens a name as a `Part`; if larger than `PartBlank`, treats it as a Venti partition and reads the 8 KiB config area ending at `PartBlank`, requiring magic `venti config\n`.
- For small files, reads the file directly.
- `partifile` reads an arbitrary partition region into an `IFile`.
- `ifileline` returns the next nonblank line, trims leading spaces/tabs/CR, strips `#` comments, and null-terminates the line in-place.
- `ifilename` reads a line into an arena/name-sized field after length validation.
- `ifileu32int` reads a line as a `u32int`.
- `freeifile` frees the backing `ZBlock`.

Interactions:
- Used by config parsing, arena map parsing, and index table parsing.

Notable details:
- For embedded partition configs it adjusts `b->data`, `_size`, and `len` after the magic, with a comment noting `freezblock` constraints.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/ifile.c -->