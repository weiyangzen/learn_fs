## sources/distributed-fs/openafs/src/vlserver/vlutils.c

Purpose: low-level VLDB storage, cache, hash, free-list, id allocation, and multihome extension-block utilities used by the VLDB RPC procedures and server diagnostics.

Important APIs/types/functions: exports `IDHash`, `NameHash`, `vlwrite`, `vlread`, `vlentrywrite`, `vlentryread`, `write_vital_vlheader`, `readExtents`, `CheckInit`, `GetExtentBlock`, `FindExtentBlock`, `AllocBlock`, `FreeBlock`, `FindByID`, `FindByName`, `EntryIDExists`, `NextUnusedID`, `HashNDump`, `HashIdDump`, `ThreadVLentry`, `UnthreadVLentry`, `HashVolid`, `UnhashVolid`, `HashVolname`, `UnhashVolname`, `NextEntry`, `vlsetcache`, and `vlsynccache`. Global caches are `rd_cheader`/`wr_cheader`, `rd_HostAddress`/`wr_HostAddress`, and `rd_ex_addr`/`wr_ex_addr`.

Control flow: `CheckInit()` uses `ubik_CheckCache()` with `UpdateCache()` to read or build the VLDB header, validate version, load server address maps, and read multihome extents. Write operations select write caches via `vlsetcache()`, mutate the cache and database through offset writes, then Ubik commit triggers `vlsynccache()` to copy write caches into read caches. Entry allocation takes from the header free pointer or grows `eofPtr`; freeing writes a `VLFREE` entry and links it into the free list. Hash insertion/removal updates header buckets and entry next pointers. Sequential iteration skips `VLCONTBLOCK` extension blocks.

State and persistence: persistent state is written through Ubik offsets in network byte order. `vlentrywrite()`/`vlentryread()` bridge old and new on-disk entry layouts based on `maxnservers` and database version. `readExtents()` keeps in-memory copies of multihome extension blocks and can mark/fix bad continuation pointers with `extent_mod`. `grow_eofPtr()` enforces the legacy 2 GiB VLDB limit.

Dependencies: Ubik transaction APIs, VLDB layout constants/types, byte-order helpers, UUID helpers, global `maxnservers`, and OpenAFS logging. It relies on `ubik_SyncWriterCacheProc` being set by `vlserver.c`.

Integration points: `vlprocs.c` is the main consumer for all RPC-visible mutations and lookups. `vlserver.c` uses hash dump helpers in signal diagnostics and installs `vlsynccache()`. `vldb_check.c` independently mirrors many layout assumptions for offline validation.

Risks: cache coherence is central; forgetting to write the header or sync write caches can expose stale state to readers. Hash updates are linked-list manipulations by raw offsets, so corrupted chains can return `VL_DBBAD`/`VL_NOENT` and require `vldb_check`. `FindExtentBlock()` encodes multihome references into server slots and upgrades the database version to `VLDBVERSION_4`; failures mid-operation depend on Ubik rollback. Several duplicate lines are present in the source, suggesting old merge or formatting artifacts. `NameHash()` assumes nonempty names and `IDHash()` uses `abs()` on signed input.

Test signals: version/header initialization for empty and existing databases; old/new entry conversion with `maxnservers` 8 and 13; hash insert/remove/find for RW/RO/BK/name chains; free-list allocate/free/reuse; `NextEntry()` skipping extension blocks; multihome extent creation, continuation validation, version upgrade, and cache sync; `NextUnusedID()` over occupied ranges; and injected Ubik read/write/seek failures.
