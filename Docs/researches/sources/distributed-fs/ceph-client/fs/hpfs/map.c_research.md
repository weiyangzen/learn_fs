# sources/distributed-fs/ceph-client/fs/hpfs/map.c

Purpose: this file maps HPFS metadata structures from disk into memory and performs lightweight structural validation when checks are enabled.

Important APIs and functions: `hpfs_map_dnode_bitmap()`, `hpfs_map_bitmap()`, and `hpfs_prefetch_bitmap()` access allocation bitmaps. `hpfs_load_code_page()` loads the case-conversion table. `hpfs_load_bitmap_directory()` reads the bitmap directory into memory. `hpfs_load_hotfix_map()` loads spare-sector remappings. `hpfs_map_fnode()`, `hpfs_map_anode()`, and `hpfs_map_dnode()` map and validate core metadata objects. `hpfs_fnode_dno()` returns a directory fnode’s root dnode.

Control flow: bitmap mapping validates the band index and bitmap-sector pointer, maps four sectors, and prefetches the next bitmap. Code-page loading reads the directory, selects the first code-page data entry, copies the uppercasing table, and synthesizes a lowercasing table. Fnode/anode/dnode mappers call lower-level buffer mapping, check magic values, count/free-node consistency, `first_free` offsets, EA boundaries, self pointers, dnode dirent sizes, last sentinel entries, and down pointers depending on `sb_chk`.

State and persistence: mapping itself is read-oriented, but it returns writable buffer-backed pointers that callers later dirty. Loaded bitmap directories, code-page tables, and hotfix maps become in-memory superblock state.

Dependencies and integration: it depends on `buffer.c`, raw HPFS structures, EA/dirent inline parsers, and `hpfs_error()`. Superblock mount setup uses loaders; all mutation paths use mappers before changing metadata.

Risks: validation is conditional. With low check levels, malformed media may reach later pointer arithmetic. Code-page loading trusts selected table bounds after a few checks. Hotfix map length is capped at 256; invalid spare counts are rejected.

Test signals: mount images with valid and invalid bitmap directories, code-page directories, hotfix maps, fnodes, anodes, and dnodes; run with checks off/normal/strict; test non-contiguous bitmap sectors; verify lower-case table synthesis; and craft malformed dirent lengths and EA boundaries.
