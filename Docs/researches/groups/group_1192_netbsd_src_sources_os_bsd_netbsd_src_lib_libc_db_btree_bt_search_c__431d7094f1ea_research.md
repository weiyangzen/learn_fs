# Group Research: group_1192_netbsd_src_sources_os_bsd_netbsd_src_lib_libc_db_btree_bt_search_c__431d7094f1ea

Scope: `Docs/research_subset_a.md`; source tree `sources/os/bsd/netbsd-src` is included in subset A.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/btree/bt_search.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/db/btree/bt_search.c

Implements btree keyed lookup. `__bt_search` descends from `P_ROOT`, binary-searching each page with `__bt_cmp`, maintaining `t->bt_cur` as the returned pinned page/index and `bt_stack` as the parent path needed by insertion and splitting. On internal pages it selects the child from the largest separator key less than or equal to the search key; on leaf pages it returns either an exact match or the insertion slot.

The duplicate-key path is the important special case. When duplicates are allowed and the computed leaf slot lies at a page boundary, `__bt_sprev` and `__bt_snext` inspect the adjacent leaf to recover exact matches that may have migrated across page boundaries after deletion. Those helpers also repair the saved parent stack by walking upward and then downward so later split/insert code still has the correct ancestry.

Dependencies include `mpool_get`/`mpool_put`, `PAGE`, `BINTERNAL`, `EPG`, `BT_PUSH`, `BT_POP`, and `GETBINTERNAL` from `btree.h`, plus `__bt_cmp` from `bt_utils.c`.

Risks/invariants: returned `EPG->page` is intentionally pinned; callers must release it. The fixed-size parent stack is assumed deep enough. Error paths can leave stack state partially adjusted, so callers generally treat `NULL` as hard failure.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/btree/bt_search.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/btree/bt_seq.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/db/btree/bt_seq.c

Provides the btree sequential scan implementation behind `DB->seq`. `__bt_seq` accepts `R_CURSOR`, `R_FIRST`, `R_LAST`, `R_NEXT`, `R_PREV`, `R_RNEXT`, and `R_RPREV`, unpins any page retained from a previous call, initializes or advances the cursor, records the cursor position with `__bt_setcur`, and returns data through `__bt_ret`.

`__bt_seqset` positions scans at a keyed lower-bound, first record, or last record by walking the left or right side of the tree. `__bt_seqadv` advances from the saved cursor and handles deleted-cursor states (`CURS_ACQUIRE`, `CURS_AFTER`, `CURS_BEFORE`). The `R_RNEXT`/`R_RPREV` variants use `__bt_rseq_next` and `__bt_rseq_prev` to traverse by parent stack rather than sibling leaf links.

`__bt_first` finds the first record greater than or equal to a key, walking backward across duplicates so duplicate scans start at the earliest matching entry. `__bt_setcur` clears any saved deleted key and updates the cursor page/index.

Dependencies include `__bt_search`, `__bt_cmp`, `__bt_ret`, the mpool page cache, and cursor/stack definitions in `btree.h`.

Risks/invariants: the code relies on pinned-page lifetime when `B_DB_LOCK` is not set. Comments document duplicate-key anomalies after cursor replacement via delete/add pairs.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/btree/bt_seq.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/btree/bt_split.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/db/btree/bt_split.c

Implements btree and recno page splitting. `__bt_split` splits a full leaf or internal page, inserts the pending item into the chosen half, then walks the saved parent stack to insert separator entries and propagate splits up to the root. It supports both btree leaf/internal entries and recno leaf/internal count entries.

`bt_page` splits non-root pages, allocates a right page, fixes sibling links, and has an append optimization for sorted right-edge inserts. `bt_root` allocates new left/right children for root splits. `bt_broot` and `bt_rroot` rewrite the root as a btree or recno internal page, respectively. `bt_psplit` copies page entries into left/right pages around a skipped insertion slot and adjusts any initialized cursor that pointed at the original page.

For btree internal separators, the file can use prefix compression via `bt_pfx`, and `bt_preserve` marks overflow key chains that become referenced from internal pages so deletion of the leaf copy does not reclaim them. For recno, parent entries are updated with `NEXTINDEX` or `rec_total` counts.

Dependencies include page layout macros from `btree.h`, overflow-page helpers, `mpool`, and the search stack populated by `bt_search.c` or `rec_search.c`.

Risks/invariants: a failure while propagating parent splits can leave the tree inconsistent; the code calls `__dbpanic` after releasing pins. Overflow pages allocated before later insert failure may not always be recovered.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/btree/bt_split.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/btree/bt_utils.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/db/btree/bt_utils.c

Contains shared btree return and comparison helpers. `__bt_ret` materializes a leaf key/data pair into caller-provided `DBT`s. It returns direct pointers into the pinned page for ordinary records when safe, but copies data when `copy` is requested, `B_DB_LOCK` is enabled, or the key/data lives in overflow pages.

`__bt_cmp` compares a user key against a btree leaf or internal entry. It special-cases the leftmost internal separator as smaller than all user keys, loads overflow keys through `__ovfl_get`, and delegates ordering to the tree's configured `bt_cmp` function.

`__bt_defcmp` is the default bytewise comparator: it compares common-prefix bytes and then sizes. `__bt_defpfx` returns the shortest prefix length needed to distinguish two ordered keys, used by split-time internal-key compression.

Dependencies include `BLEAF`, `BINTERNAL`, `GETBLEAF`, `GETBINTERNAL`, overflow helpers, and `BTREE` flags from `btree.h`.

Risks/invariants: direct return pointers require the referenced page to remain pinned. `__bt_cmp` uses `bt_rdata` as scratch for overflow key material, so callers must not assume that buffer remains stable across later operations.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/btree/bt_utils.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/btree/btree.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/db/btree/btree.h

Defines the core on-disk and in-memory btree/recno data model. Page zero is metadata, page one is root, and `PAGE` headers carry page number, sibling links, flags, and line-pointer bounds. Page variants include btree internal (`BINTERNAL`), btree leaf (`BLEAF`), recno internal (`RINTERNAL`), recno leaf (`RLEAF`), and overflow pages.

The header defines alignment and sizing macros (`BTLALIGN`, `NBINTERNAL`, `NBLEAFDBT`, `NRLEAFDBT`), field writers (`WR_BINTERNAL`, `WR_BLEAF`, `WR_RINTERNAL`, `WR_RLEAF`), and accessors (`GETBINTERNAL`, `GETBLEAF`, `GETRINTERNAL`, `GETRLEAF`). It also defines `EPG`/`EPGNO` for pinned and unpinned page/index references.

`CURSOR` describes btree and recno cursor state, including deleted-cursor recovery flags. `BTMETA` is the disk metadata. `BTREE` holds the mpool handle, DB pointer, current and pinned pages, cursor, fixed-depth parent stack, return buffers, file descriptors, recno backing-file state, comparison/prefix callbacks, and flags for btree/recno behavior.

Dependencies are intentionally broad: this header includes `<mpool.h>` and `extern.h` and is the common contract for btree and recno implementation files.

Risks/invariants: structures must not be randomly padded because they are used as disk layouts. Many macros perform unaligned-looking casts that assume historical Berkeley DB layout constraints.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/btree/btree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/btree/extern.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/db/btree/extern.h

Declares the private btree/recno-shared implementation interface. It lists btree close, get, put, delete, sequence, sync, file-descriptor, comparison, return, search, split, page allocation/free/relink, byte-swap filters, and overflow helpers.

The exported private functions connect the public `DB` methods installed by `__bt_open` and `__rec_open` to lower-level page manipulation. The overflow declarations (`__ovfl_delete`, `__ovfl_get`, `__ovfl_put`) are shared by btree leaf data, internal separator preservation, and recno record payloads.

Conditional declarations provide debug dump and statistics entry points when `DEBUG` or `STATISTICS` is enabled.

Dependencies: included from `btree.h`, and assumes `BTREE`, `DB`, `DBT`, `EPG`, `PAGE`, and page-number types have already been defined.

Risks/invariants: this is not a public API; prototypes expose tightly coupled page-cache and tree internals, so signature changes ripple through btree and recno code.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/btree/extern.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/db/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/db/db/Makefile.inc

Build fragment for the generic DB layer. It adds `${.CURDIR}/db/db` to `.PATH` and appends `db.c` and `dbfile.c` to `SRCS`.

Dependencies: consumed by the libc DB build and paired with subdirectory Makefile fragments for btree, hash, mpool, recno, and man pages.

Risks/invariants: minimal; source names here must match the generic DB dispatch and file-helper implementation files.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/db/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/db/db.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/db/db/db.c

Implements the public `dbopen` dispatcher and panic-mode method replacement. `dbopen` validates open flags against allowed file flags and DB flags, then routes by `DBTYPE` to `__bt_open`, `__hash_open`, or `__rec_open`, passing through DB-specific flags separately from real `open(2)` flags.

The file also defines `__dbpanic`, used when an access method detects unrecoverable internal inconsistency. It replaces all operational DB methods except close with `__dberr`, making subsequent get/put/delete/seq/sync/fd calls fail with `RET_ERROR`.

Dependencies include `<db.h>` for the public DB structure and access method constants, and private open routines from btree/hash/recno compiled into libc.

Risks/invariants: `dbopen` rejects unsupported flag/type combinations with `EINVAL`. `__dbpanic` assumes `dbp` is valid and mutates function pointers in place, so callers holding a `DB *` see a permanently degraded handle until close.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/db/db.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/db/dbfile.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/db/db/dbfile.c

Provides shared file-opening helpers for DB access methods. `__dbopen` wraps `open`, forces close-on-exec using `O_CLOEXEC` or `fcntl(FD_CLOEXEC)`, optionally fills a `stat` buffer, and preserves `errno` if cleanup is needed.

`__dbtemp` creates an unlinked temporary file using `TMPDIR` when safe, otherwise `_PATH_TMP`. It blocks signals around `mkstemp`, `unlink`, `fcntl(FD_CLOEXEC)`, and optional `fstat` to avoid leaking a named temporary file on interruption.

Dependencies include POSIX file APIs, signals, paths, and `<db.h>`. Hash uses `__dbtemp` for anonymous backing storage; btree/recno use `__dbopen` for database or record files.

Risks/invariants: `__dbtemp` ignores `TMPDIR` under `issetugid`. It returns an open fd whose path has already been unlinked, so later persistence is impossible unless another layer copied data elsewhere.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/db/dbfile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/db2netbsd -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/db/db2netbsd

Shell helper for importing an upstream Berkeley DB distribution into the NetBSD source layout. It derives `version` and `releasetag` from the current directory name, removes unimported files and symlinks/tags, moves regression tests under `regress/lib/libc/db`, moves DB libc components under `lib/libc/db`, and prints a `cvs import` command.

Dependencies: run from the unpacked upstream DB distribution directory. It assumes historical Berkeley DB 1.85-style paths such as `btree`, `hash`, `mpool`, `recno`, `test`, `docs`, and `PORT`.

Risks/invariants: destructive by design (`rm -rf`, `mv`). It is an import-maintenance script, not runtime code.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/db2netbsd -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/hash/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/db/hash/Makefile.inc

Build fragment for the hash access method and ndbm compatibility layer. It adds `${.CURDIR}/db/hash` to `.PATH` and appends `hash.c`, `hash_bigkey.c`, `hash_buf.c`, `hash_func.c`, `hash_log2.c`, `hash_page.c`, `ndbmdatum.c`, and `ndbm.c` to `SRCS`.

Dependencies: used by libc's DB build along with common `db`, `mpool`, btree, and recno fragments.

Risks/invariants: source ordering is not semantically significant here, but all listed files participate in the private hash implementation contract declared in `hash/extern.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/hash/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/hash/extern.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/db/hash/extern.h

Declares private hash implementation functions shared across the hash source files. The declarations cover overflow-page allocation/free, key/data insertion and deletion, large-key handling, buffer cache lifecycle, hashing, page I/O, bitmap allocation, table expansion, and bucket splitting.

It also declares `__default_hash`, the default hash function pointer provided by `hash_func.c`, plus optional hash statistics counters.

Dependencies: included after `hash.h` and `page.h`, which define `HTAB`, `BUFHEAD`, `SPLIT_RETURN`, and page-format constants.

Risks/invariants: no include guard is present in this file; it relies on conventional include ordering. Most prototypes expose mutable `HTAB *` state and raw page buffers, so callers must maintain buffer pinning and page-format invariants.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/hash/extern.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/hash/hash.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/db/hash/hash.c

Implements the public `DB_HASH` access method. `__hash_open` validates access mode, opens or creates storage, initializes or reads `HASHHDR`, verifies magic/version/hash compatibility, allocates directory segments, initializes the buffer cache, and installs `DB` method pointers.

`hash_get`, `hash_put`, and `hash_delete` validate flags and permissions before calling `hash_access`. `hash_access` hashes the key to a bucket, pins the bucket chain, walks regular pairs and overflow/big-pair markers, performs get/put/delete behavior, and updates sequential-scan cursor state after deletion. `hash_seq` iterates buckets and overflow pages, returning ordinary or large key/data pairs.

Lifecycle helpers include `hash_close`, `hash_fd`, `hash_sync`, `flush_meta`, and `hdestroy`. Table growth is handled by `__expand_table`, which advances `MAX_BUCKET`, adjusts masks/spares/segments, and calls `__split_page`. `__call_hash` implements linear-hash bucket selection with high/low masks. Little-endian builds include header byte-swap helpers for big-endian on-disk order.

Dependencies include `hash_page.c` for page operations, `hash_buf.c` for buffers, `hash_bigkey.c` for large pairs, and `hash_func.c` for default hashing.

Risks/invariants: `DSIZE` reallocation appears size-sensitive and depends on historical layout expectations. Errors are recorded in `hashp->err` inconsistently across lower layers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/hash/hash.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/hash/hash.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/db/hash/hash.h

Defines the private hash table structures, constants, and address macros. `ACTION` enumerates internal operations. `BUFHEAD` describes LRU buffer nodes with optional overflow-page links and flags for modified, disk-backed, bucket, and pinned status. `HASHHDR` is the disk-resident header containing sizing, masks, split/overflow accounting, fill factor, key count, bitmap locations, and hash signature. `HTAB` is the memory-resident hash handle.

The header defines default sizing parameters, overflow-address encoding (`SPLITSHIFT`, `SPLITMASK`, `OADDR_OF`), bucket-to-page and overflow-address-to-page translations, and pointer-tagging macros used in the bucket directory. It also documents the hash page format for ordinary records, overflow-page pointers, partial keys, full keys, and full key/data continuations.

Dependencies: paired with `page.h` and `extern.h` in every hash implementation file.

Risks/invariants: pointer tagging assumes low address bits are available. `HASH_BSIZE` caps `MAX_BSIZE` to fit uint16_t page offsets without changing the file format. Overflow address space is limited by split/offset bit partitioning.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/hash/hash.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/hash/hash_bigkey.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/db/hash/hash_bigkey.c

Handles hash key/data pairs too large to fit as ordinary page entries. `__big_insert` writes key bytes across partial-key overflow pages, then writes data across full-key/full-key-data pages, preserving the invariant that complete data on a page leaves detectable free space.

`__big_delete` frees all overflow pages belonging to a large pair except the first page, which is rewritten to point to the following chain. `__find_bigpair` compares a candidate large key across overflow pages. `__find_last_page` locates the last page in a large pair and returns any following overflow page address.

`__big_return` materializes a large value into `hashp->tmp_buf`, using `collect_data` recursively. `__big_keydata` materializes both key and data using `collect_key` and `__big_return`, used by sequential scans and bucket splits. `__big_split` relocates a large pair during linear-hash bucket splitting, reconnecting the pair to either the old or new bucket and preserving following overflow chains.

Dependencies: uses `__get_buf`, `__add_ovflpage`, `__free_ovflpage`, `__call_hash`, and hash page markers from `hash.h`.

Risks/invariants: recursive collection assumes enough buffers remain resident; it checks saved buffer addresses and reports `EINVAL` for buffer exhaustion. Large-pair deletion and split are subtle because page links double as both continuation and bucket overflow links.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/hash/hash_bigkey.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/hash/hash_buf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/db/hash/hash_buf.c

Implements the hash access method's buffer cache. `__buf_init` initializes an LRU sentinel and computes the number of buffers allowed from the requested cache size. `__get_buf` returns a buffer for a bucket or overflow page, checking directory entries or previous-page overflow links, allocating or evicting as needed, reading page contents through `__get_page`, and moving hits to MRU position.

`newbuf` either allocates a new `BUFHEAD` and page buffer, or evicts the LRU unpinned buffer. Eviction writes dirty pages with `__put_page`, invalidates bucket directory entries, and flushes linked overflow buffers associated with the bucket. `__buf_free` writes dirty buffers on sync/close and optionally frees all buffers. `__reclaim_buf` resets a freed overflow buffer and moves it to the LRU end.

Dependencies include `hash.h` buffer flags and pointer tagging, `hash_page.c` page I/O, and directory/segment state in `HTAB`.

Risks/invariants: pinned buffers force allocation beyond the nominal cache size. Overflow-link cache pointers can become stale, so `__get_buf` validates addresses before reuse.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/hash/hash_buf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/hash/hash_func.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/db/hash/hash_func.c

Provides the default hash function pointer for DB hash tables. Historical alternative hash functions are retained inside `#if 0`; the active default is `hash4`, attributed to Chris Torek.

`hash4` consumes the key bytes in an unrolled eight-byte loop, applying the `h = h * 33 + byte` variant (`HASH4b`) and returning a 32-bit hash. `__default_hash` is initialized to `hash4` and is used unless callers supply `HASHINFO.hash`.

Dependencies: included by the hash build and declared through `hash/extern.h`.

Risks/invariants: existing on-disk hash files store `H_CHARKEY`, the hash of a fixed string, so changing the default hash breaks compatibility unless a matching custom hash is supplied at open time.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/hash/hash_func.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/hash/hash_log2.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/db/hash/hash_log2.c

Defines `__log2`, a helper returning the number of bits needed to cover a positive integer rounded up to a power-of-two bucket/segment size. It returns zero for input zero, decrements the input, then grows a `2^i - 1` limit until the limit covers the decremented value.

Dependencies: used by hash initialization, bucket-size rounding, segment sizing, spare split point calculations, and bucket-to-page address translation.

Risks/invariants: despite its name, the function computes a ceiling-style exponent used for sizing, not the mathematical floor log2 for all inputs.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/hash/hash_log2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/hash/hash_page.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/db/hash/hash_page.c

Implements low-level hash page manipulation, bucket splitting, overflow allocation, bitmap management, and disk page I/O. `putpair` appends a regular key/data pair into a page. `__delpair` removes a pair, compacts data and offset entries, and delegates large-pair deletion when needed.

`__split_page` redistributes records from an old bucket to a new bucket during linear-hash expansion. If it encounters overflow or big-pair structure, `ugly_split` handles mixed regular/large entries and allocates overflow pages for either destination. `__addel` inserts a pair into a bucket chain, using `squeeze_key`, overflow pages, or `__big_insert`, then expands the table when fill factor is exceeded.

`__add_ovflpage` allocates and links an overflow page. `__get_page` and `__put_page` translate bucket/overflow addresses to file pages, initialize new pages, and perform byte swapping for non-native byte order. `__ibitmap`, `overflow_page`, `__free_ovflpage`, and `fetch_bitmap` manage overflow-page bitmap allocation and reclamation.

Dependencies include `hash_buf.c`, `hash_bigkey.c`, page macros from `page.h`, address macros from `hash.h`, and `__dbtemp`.

Risks/invariants: page offsets are 16-bit and depend on `HASH_BSIZE`. Overflow exhaustion writes a diagnostic to stderr and returns `EFBIG`. The split path is complex and historically fragile.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/hash/hash_page.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/hash/ndbm.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/db/hash/ndbm.c

Implements part of the `ndbm` compatibility API on top of the hash access method. `dbm_open` appends `DBM_SUFFIX` to the supplied base path, configures a small `HASHINFO`, converts write-only opens to read/write because hash needs reads, and calls `__hash_open`.

`dbm_close` calls the underlying DB close method. `dbm_error` and `dbm_clearerr` expose/reset `HTAB.err`. `dbm_dirfno` returns the hash file descriptor.

Dependencies: `<ndbm.h>`, hash internals, and the hash DB method table.

Risks/invariants: `strncpy`/`strncat` build the suffixed path in a fixed `MAXPATHLEN` buffer; very long input truncates rather than returning `ENAMETOOLONG`. The DBM handle is cast from `DB *`, relying on ABI compatibility between the old wrapper type and the DB structure.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/hash/ndbm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/hash/ndbmdatum.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/db/hash/ndbmdatum.c

Implements datum-oriented `ndbm` operations using the underlying `DB` methods. `dbm_fetch` maps a `datum` key to `DBT`, calls `get`, and returns a null datum on failure. `dbm_firstkey` and `dbm_nextkey` call `seq` with `R_FIRST` and `R_NEXT`. `dbm_delete` calls `del` and translates any nonzero status to `-1`. `dbm_store` calls `put`, mapping `DBM_INSERT` to `R_NOOVERWRITE`.

Dependencies include `<ndbm.h>`, `DBT`, DB method pointers, and `datum_truncate`, which can be overridden by platform headers to fit old `datum.dsize` width.

Risks/invariants: returned data/key pointers are those provided by the hash method and are valid only according to DB method lifetime rules. The API compresses DB status values into older ndbm conventions, losing some distinction between not-found and internal errors.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/hash/ndbmdatum.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/hash/page.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/db/hash/page.h

Documents and defines the hash page layout. A page begins with a uint16_t offset table: count, alternating key/data offsets, free-space amount, and free-area pointer. Data grows downward from the end of the page while offset metadata grows upward.

Macros compute pair size, big-pair overhead, overflow marker size, free space, current data offset, metadata size, and whether a regular pair fits while still leaving room for a future overflow marker. `SPLIT_RETURN` carries page pointers and continuation addresses for complex split handling involving big key/data chains.

Dependencies: included with `hash.h`; uses `DBT` and `BUFHEAD`.

Risks/invariants: all offsets fit in `uint16_t`, so hash bucket size constraints are central. `PAIRFITS` intentionally requires extra room for an overflow pointer to avoid later impossible split states.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/hash/page.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/man/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/db/man/Makefile.inc

Build fragment for DB manual pages. It adds `${.CURDIR}/db/man` to `.PATH`, installs `btree.3`, `dbm_clearerr.3`, `dbopen.3`, `hash.3`, `recno.3`, and `mpool.3`, and defines manual links for ndbm, dbopen/db, and mpool entry points.

Dependencies: libc manpage build machinery.

Risks/invariants: documentation link names must track public function names exported by the DB and mpool implementations.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/man/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/mpool/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/db/mpool/Makefile.inc

Build fragment for the memory-pool page cache. It adds `${.CURDIR}/db/mpool` to `.PATH` and appends `mpool.c` to `SRCS`.

Dependencies: included by libc DB build; btree/recno use mpool for page caching.

Risks/invariants: minimal; only one implementation file is listed.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/mpool/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/mpool/mpool.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/db/mpool/mpool.c

Implements the generic fixed-size page cache used by btree and recno. `mpool_open` validates a regular file, initializes LRU and hash queues, records page size, max cache, file descriptor, and current file page count. `mpool_filter` installs optional page-in/page-out byte-order or transformation callbacks.

`mpool_newf`/`mpool_new` allocate a new page number or requested page, acquire a cache bucket, mark it pinned/in-use, and insert it into hash/LRU queues. `mpool_get` returns a pinned page from cache or disk, moving hits to MRU position and running `pgin` after reads. `mpool_put` unpins pages and marks them dirty. `mpool_delete` removes a pinned page from queues and frees it.

`mpool_sync` writes all dirty pages then `fsync`s. `mpool_close` frees cached pages and the pool. `mpool_bkt` allocates or evicts an unpinned bucket, flushing dirty victims with `mpool_write`. `mpool_write` runs `pgout`, writes by page number, then reruns `pgin` to restore the in-memory representation. `mpool_look` searches the page hash table.

Risks/invariants: callers must pair every pinned `mpool_get`/new with `mpool_put` or delete. If all buffers are pinned, the cache grows beyond `maxcache`. Offset multiplication is checked for overflow.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/mpool/mpool.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/recno/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/db/recno/Makefile.inc

Build fragment for the recno access method. It adds `${.CURDIR}/db/recno` to `.PATH` and appends close, delete, get, open, put, search, sequence, and utility implementation files to `SRCS`.

Dependencies: recno builds on the btree implementation and includes btree private headers.

Risks/invariants: source list must remain synchronized with private prototypes in `recno/extern.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/recno/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/recno/extern.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/db/recno/extern.h

Declares private recno functions and includes the btree private declarations. The API covers DB method implementations (`__rec_close`, `__rec_delete`, `__rec_fd`, `__rec_get`, `__rec_put`, `__rec_seq`, `__rec_sync`), leaf deletion/return helpers, record insertion, record-number search, and backing-file import/export functions for fixed and variable records via mmap or pipe/file streams.

Dependencies: requires `BTREE`, `PAGE`, `EPG`, `DB`, `DBT`, `recno_t`, and `enum SRCHOP`.

Risks/invariants: recno is not independent; it mutates and reuses btree internals while changing DB method pointers after `__bt_open`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/recno/extern.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/recno/rec_close.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/db/recno/rec_close.c

Implements recno close and sync. `__rec_close` unpins any retained page, calls `__rec_sync`, unmaps mapped input if used, closes the backing record file or `FILE *`, then delegates to `__bt_close`.

`__rec_sync` has two modes. With `R_RECNOSYNC`, it only syncs the underlying btree. Otherwise, if the recno backing file is writable and modified, it imports all remaining source records, rewinds the backing file, serializes records in record-number order with either fixed-length writes or variable-length `writev` including the delimiter byte, restores the saved cursor, truncates the file to the new length, and clears `R_MODIFIED`.

Dependencies include btree sequence methods, `__bt_sync`, mpool pin handling, and recno state in `BTREE`.

Risks/invariants: sync rewrites the entire backing file. Any write/truncate failure returns error after partial output may already have occurred. Cursor restoration only restores the recno numeric cursor, not necessarily every btree cursor flag.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/recno/rec_close.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/recno/rec_delete.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/db/recno/rec_delete.c

Implements record deletion. `__rec_delete` validates flags and record numbers, supports explicit-key deletion and `R_CURSOR`, unpins retained pages, and delegates to `rec_rdelete`. On success it marks both btree and recno state modified.

`rec_rdelete` finds the zero-based record with `__rec_search(..., SDELETE)`, which decrements internal subtree counts during descent, then removes the leaf entry with `__rec_dleaf`.

`__rec_dleaf` deletes one `RLEAF` entry from a leaf page, frees overflow data if present, compacts payload bytes and line pointers, updates page bounds, and decrements `bt_nrecs`. Empty pages are not reclaimed, but become usable for future inserts.

Dependencies include recno search/count maintenance, btree overflow deletion, page layout macros, and mpool dirty-page handling.

Risks/invariants: internal count updates happen before leaf deletion; `__rec_search` contains recovery logic for descent errors, but failures after leaf mutation can still leave higher-level state sensitive.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/recno/rec_delete.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/recno/rec_get.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/db/recno/rec_get.c

Implements record retrieval and lazy import from backing files. `__rec_get` validates flags and one-based record keys, imports records up to the requested number if not already loaded, searches the btree by zero-based record index, and returns data with `__rec_ret`, retaining or releasing the page depending on `B_DB_LOCK`.

The file also defines backing-file readers. `__rec_fpipe` reads fixed-length records from a `FILE *`, padding short final records with `bt_bval`. `__rec_vpipe` reads delimiter-separated variable records from a `FILE *`, growing `bt_rdata` as needed. `__rec_fmap` and `__rec_vmap` perform analogous fixed/variable imports from an mmap region, advancing `bt_cmap`. All import helpers insert records using `__rec_iput` and set `R_EOF` when the source is exhausted.

Dependencies include `__rec_search`, `__rec_ret`, `__rec_iput`, and recno state configured by `rec_open.c`.

Risks/invariants: record keys are one-based externally and zero-based internally. Variable import treats delimiter bytes as separators and does not include them in stored data.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/recno/rec_get.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/recno/rec_open.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/db/recno/rec_open.c

Opens a recno database by wrapping a btree. `__rec_open` optionally opens the user's record file, creates a btree backing store with `__bt_open`, copies recno options into the `BTREE` state, marks the tree as `R_RECNO`, selects fixed or variable record handling, and installs recno DB method pointers.

For named files it handles read-only versus read/write modes, detects non-seekable input via `lseek`/`ESPIPE`, and uses a `FILE *` reader for pipe-like sources. The mmap path is present but compiled out unless `MMAP_NOT_AVAILABLE` is defined in a way that enables it; otherwise regular files also use the slow `FILE *` path. The root page is converted from `P_BLEAF` to `P_RLEAF`. `R_SNAPSHOT` forces import of the full backing file at open.

`__rec_fd` returns the backing record file descriptor and rejects in-memory recno databases with `ENOENT`.

Risks/invariants: recno uses btree storage but changes page type and method table after open. Some flag combinations are rejected with `EINVAL`, especially writable pipe-like inputs.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/recno/rec_open.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/recno/rec_put.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/db/recno/rec_put.c

Implements record insertion and replacement. `__rec_put` validates fixed-length record constraints, pads short fixed records with `bt_bval`, interprets `R_CURSOR`, `R_SETCURSOR`, `R_IAFTER`, `R_IBEFORE`, `R_NOOVERWRITE`, and default replacement/append semantics, imports backing-file records as needed, fills skipped records with empty or padded records, calls `__rec_iput`, updates cursor state, marks recno modified, and returns the resulting record number.

`__rec_iput` performs the actual btree insertion/replacement. It stores oversized record data in btree overflow pages, searches for the insertion/replacement leaf with `__rec_search`, deletes an existing record unless doing before/after insertion, splits the page through `__bt_split` when necessary, otherwise shifts line pointers, writes an `RLEAF`, increments `bt_nrecs`, marks the tree modified, and releases the page dirty.

Dependencies include overflow handling, `__rec_search`, `__rec_dleaf`, `__bt_split`, and recno/btree page macros.

Risks/invariants: if overflow allocation succeeds but a later insert fails, comments note those pages are not recovered. External keys are one-based; insertion into gaps creates synthetic records.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/recno/rec_put.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/recno/rec_search.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/db/recno/rec_search.c

Searches the recno btree by ordinal record number. `__rec_search` descends from root through `RINTERNAL` pages, using each internal entry's `nrecs` subtree count to find the child containing the target zero-based record number. At an `RLEAF`, it returns `t->bt_cur` with the pinned page and leaf index.

For insert and delete operations, the function increments or decrements `nrecs` in internal entries during descent and marks those pages dirty. If a later mpool lookup fails, it walks the saved parent stack and reverses the count adjustments before returning `NULL`.

Dependencies: page macros from `btree.h`, `enum SRCHOP` from `recno.h`, `BT_PUSH`/`BT_POP` stack handling, and mpool.

Risks/invariants: correctness depends on accurate internal subtree counts. The returned page is pinned and must be released by the caller.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/recno/rec_search.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/recno/rec_seq.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/db/recno/rec_seq.c

Implements recno sequential scans. `__rec_seq` handles `R_CURSOR`, `R_FIRST`, `R_LAST`, `R_NEXT`, and `R_PREV`, using `bt_cursor.rcursor` as a one-based current record number. It unpins any page retained from a previous call, computes the target record number, lazily imports backing-file records if needed, searches with `__rec_search`, initializes the cursor, and returns key/data via `__rec_ret`.

`R_LAST` forces full import of the backing file when EOF is not known, because the last record number is unknown until import completes. `R_NEXT` and `R_PREV` require an initialized cursor or fall through to first/last behavior.

Dependencies include recno lazy import callback `bt_irec`, `__rec_search`, `__rec_ret`, and mpool pin management.

Risks/invariants: end-of-file and in-memory flags determine whether missing records are final or trigger import. As elsewhere, page retention depends on `B_DB_LOCK`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/recno/rec_seq.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/recno/rec_utils.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/db/recno/rec_utils.c

Provides `__rec_ret`, the recno return-value builder. It copies the one-based record number into `bt_rkey` when a key is requested, because recno keys are implicit and not stored on leaf pages. For data, it loads overflow payloads through `__ovfl_get`, copies ordinary data into `bt_rdata` when `B_DB_LOCK` is set, or returns a direct pointer into the pinned `RLEAF` otherwise.

Dependencies include `GETRLEAF`, `RLEAF`, overflow helpers, and `BTREE` return buffers.

Risks/invariants: direct data pointers require the page to remain pinned by the caller. The function uses reusable buffers in `BTREE`, so returned copied data is overwritten by later DB operations on the same handle.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/recno/rec_utils.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/recno/recno.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/db/recno/recno.h

Small recno private header. It defines `enum SRCHOP` with `SDELETE`, `SINSERT`, and `SEARCH`, controlling whether `__rec_search` adjusts internal record counts while descending. It then includes the shared btree internals and recno private prototypes.

Dependencies: `../btree/btree.h` and `recno/extern.h`.

Risks/invariants: inclusion pulls in the full btree private API, reflecting that recno is implemented as a specialized btree rather than an independent access method.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/recno/recno.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/dlfcn/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/dlfcn/Makefile.inc

Build fragment for libc `dlfcn` support. It adds include paths for `libexec/ld.elf_so` and the local `dlfcn` directory, and appends `dlfcn_elf.c` to `SRCS`.

Dependencies: requires dynamic linker headers, especially `rtld.h`, for shared structure and auxiliary-vector declarations.

Risks/invariants: libc's fallback `dlfcn` stubs must stay ABI-compatible with runtime linker implementations that override them.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/dlfcn/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/dlfcn/dlfcn_elf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/dlfcn/dlfcn_elf.c

Provides weak ELF `dlfcn` symbols in libc. Dynamic programs have these services resolved directly to the runtime linker; these definitions exist so static links or missing runtime linker services have linkable fallback symbols. `dlopen`, `dlsym`, and `dlvsym` return `NULL`; `dlclose` and `dlinfo` return `-1`; `dladdr` returns `0`; `dlerror` returns the static string "Service unavailable".

`dl_iterate_phdr` is the meaningful fallback. It lazily initializes static `dlpi_*` fields from `_dlauxinfo()` auxiliary-vector entries (`AT_BASE`, `AT_PHDR`, `AT_PHNUM`, `AT_SUN_EXECNAME`), adjusts the load address by scanning for `PT_PHDR`, uses producer/consumer memory barriers around the one-time setup flag, fills a `dl_phdr_info`, and invokes the caller callback once.

`___dl_cxa_refcount` is a no-op weak compatibility hook.

Dependencies include `<elf.h>`, `<sys/atomic.h>`, `rtld.h`, and weak alias support.

Risks/invariants: first-call setup can race but only stores pointer-sized or smaller fields. Static fallback dynamic-loading operations intentionally do not work.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/dlfcn/dlfcn_elf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/Makefile.inc

Build fragment for David M. Gay's gdtoa floating-point conversion code in libc. It adds include paths for local gdtoa and locale headers, sets floating-rounding or VAX-specific preprocessor flags, requires architecture-specific `arith.h` and `gd_qnan.h`, and includes `${ARCHDIR}/gdtoa/Makefile.inc` for machine-dependent conversion module selection.

It appends public and private conversion sources such as `strtod.c`, `dtoa.c`, `ldtoa.c`, `hdtoa.c`, `gdtoa.c`, locking, hexadecimal parsing/formatting, miscellaneous bigint support, `strtodg.c`, and `strtord.c` on non-VAX architectures. Lint flags suppress known conversion warnings in selected files.

Dependencies: machine architecture make fragments and headers are required to choose float/long-double formats.

Risks/invariants: correct conversion behavior depends on matching architecture arithmetic headers and selected source variants to actual ABI floating-point formats.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/arithchk.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/arithchk.c

Standalone generator/check program that deduces floating-point arithmetic properties for gdtoa's `arith.h`. It tests the binary representation of `1e13` through unions using `long`, `int`, or `long`-sized double layouts to identify IEEE little-endian, IEEE big-endian, VAX, IBM, or Cray formats.

`Lcheck`, `icheck`, and `ccheck` perform representation checks and detect double alignment padding. `fzcheck` detects sudden underflow by repeated squaring. `main` writes preprocessor defines to stdout or `arith.h` when `WRITE_ARITH_H` is set, including arithmetic kind, `Long int` override, `Intcast`, `Double_Align`, `X64_bit_pointers`, `NO_LONG_LONG`, and `Sudden_Underflow` as applicable.

Dependencies: standard I/O only; used as a build/configuration tool rather than libc runtime code.

Risks/invariants: relies on type-punning through unions and magic representation constants. Unknown formats emit a comment and exit nonzero.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/arithchk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/dmisc.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/dmisc.c

Provides miscellaneous dtoa allocation and bigint division helpers. `rv_alloc` allocates a `Bigint` block large enough for a returned string and stores the allocation size class just before the returned character pointer; in non-threaded builds it also records `dtoa_result`. `nrv_alloc` allocates and copies a null-terminated string and optionally returns the end pointer. `freedtoa` converts a returned string pointer back to its owning `Bigint` block and frees it.

`quorem` divides a `Bigint` numerator by another `Bigint` denominator known to produce a single decimal digit quotient. It estimates `q`, subtracts `q*S` from `b` with carry/borrow handling for 32-bit, packed-16, or `ULLong` arithmetic, normalizes word counts, then subtracts once more if the remainder is still at least `S`.

Dependencies: `gdtoaimp.h` for `Bigint`, `Balloc`, `Bfree`, `cmp`, arithmetic typedefs, and packing macros.

Risks/invariants: returned dtoa strings must be freed with `freedtoa`, especially in threaded builds. `quorem` assumes `b->wds <= S->wds` plus quotient digit bounds enforced by callers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/dmisc.c -->