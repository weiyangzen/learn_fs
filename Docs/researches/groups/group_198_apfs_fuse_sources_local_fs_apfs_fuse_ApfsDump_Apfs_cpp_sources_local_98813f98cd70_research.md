# Group Research: group_198_apfs_fuse_sources_local_fs_apfs_fuse_ApfsDump_Apfs_cpp_sources_local_98813f98cd70

Scope confirmed against `Docs/research_subset_a.md`: all files are under `sources/local-fs/apfs-fuse`, which is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsDump/Apfs.cpp -->
# File Research: sources/local-fs/apfs-fuse/ApfsDump/Apfs.cpp

This is the `apfs-dump` command-line entry point. The active `main()` parses `-map`, `-fusion`, main/tier2 device paths, and output path, opens devices through `Device::OpenDevice`, initializes a `Dumper`, optionally writes a block map, and then dumps the container.

It defines the global interrupt flag `g_abort` and installs a Ctrl-C handler on Linux/macOS so long block scans can abort cooperatively. It also sets `g_debug = 255`, so dump runs enable broad diagnostic output.

The lower half is the active implementation; the earlier large `#if 0` block preserves older direct scan helpers (`MapBlocks`, `ScanBlocks`, `DumpSpaceman`) and an obsolete main path. Those disabled helpers show the historical design: raw block verification plus `BlockDumper` dispatch.

Key dependencies are `Device`, `GptPartitionMap`, `Util`, `DiskStruct`, `BlockDumper`, and local `Dumper`. The file owns CLI orchestration, not APFS parsing itself.

Notable risks: argument parsing is manual and order-sensitive; fusion mode changes positional parsing. `g_debug` is forced globally, so this tool is intentionally verbose and not a quiet library-style consumer.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsDump/Apfs.cpp -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsDump/Dumper.cpp -->
# File Research: sources/local-fs/apfs-fuse/ApfsDump/Dumper.cpp

`Dumper` implements physical APFS container dumping. `Initialize()` detects GPT APFS partition offsets for the main and optional tier2 device, reads the NX superblock, adopts the APFS block size, and verifies the superblock checksum.

`DumpContainer()` reads and dumps the NX superblock, checkpoint map, spaceman, CAB/CIB metadata, bitmap blocks, and allocated blocks. It uses spaceman allocation bitmaps to decide which physical blocks to feed into `BlockDumper`, including Fusion tier2 address translation via `FUSION_TIER2_DEVICE_BYTE_ADDR`.

`DumpBlockList()` scans the main device, and optionally tier2, printing a compact table of APFS object headers and B-tree node metadata when checksums validate, or `Data` for non-APFS/non-verified blocks.

`Read()` maps APFS physical block addresses to byte offsets in main or tier2 devices. `Decrypt()` contains a manual AES-XTS path, but encryption is gated behind disabled code that requires hardcoded VEK material.

Notable risks: some code assumes 4 KiB blocks in `DumpBlockList()` despite dynamic block size elsewhere. The tier2 block-list branch appears suspicious because it calls `Read(block + off, bid, 1)` where `off` is a huge APFS address-derived block offset, not a buffer offset.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsDump/Dumper.cpp -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsDump/Dumper.h -->
# File Research: sources/local-fs/apfs-fuse/ApfsDump/Dumper.h

This header declares the `Dumper` class used by `ApfsDump/Apfs.cpp`. Public API is `Initialize()`, `DumpContainer(std::ostream&)`, and `DumpBlockList(std::ostream&)`.

The class stores raw `Device*` handles for main and tier2 devices, partition base/size fields, dynamic APFS block size, AES-XTS state, and an encryption flag. It also exposes no ownership semantics, so callers retain responsibility for device lifetime.

Private helpers cover physical reads, vector-backed reads, optional decryption, and checkpoint-map OID lookup. It imports `Crypto/AesXts.h` and declares `extern volatile bool g_abort`.

The header is tightly coupled to APFS disk structs through private signatures using `checkpoint_map_phys_t` and `checkpoint_mapping_t`, even though `DiskStruct.h` is not included directly here in the visible file.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsDump/Dumper.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsDumpQuick/ApfsDumpQuick.cpp -->
# File Research: sources/local-fs/apfs-fuse/ApfsDumpQuick/ApfsDumpQuick.cpp

This is a second diagnostic CLI, `apfs-dump-quick`, built on the higher-level `ApfsContainer` and `ApfsVolume` APIs instead of the raw `Dumper` class. It accepts a main device, optional `-f` fusion device, and log output path.

The program opens devices, detects first APFS GPT partitions on main and tier2, initializes `ApfsContainer`, creates a `BlockDumper`, dumps the container, then iterates `NX_MAX_FILE_SYSTEMS` and dumps each mountable volume.

It sets `g_debug = 255` and prints discovered volume names to stdout. Most direct directory/file-read experimentation is preserved under `#if 0`, showing prior manual tests with `ApfsDir`.

Notable risks: if `argc < 5` in `-f` mode, it prints syntax but does not immediately return before using `argv[4]`. It closes only the main disk at the end; the tier2 device is managed by `unique_ptr` but its explicit `Close()` is not called.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsDumpQuick/ApfsDumpQuick.cpp -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/ApfsContainer.cpp -->
# File Research: sources/local-fs/apfs-fuse/ApfsLib/ApfsContainer.cpp

`ApfsContainer` owns APFS container initialization and physical block access. It reads the NX superblock, verifies checksums, scans the checkpoint descriptor ring for the newest or requested XID, enforces Fusion tier2 presence when needed, initializes the checkpoint map and container object map, loads spaceman, optional free-queue trees, and key manager state.

`GetVolume()` maps an APFS filesystem OID through the container OMAP, constructs an `ApfsVolume`, and either initializes the live volume or mounts a requested snapshot. `GetVolumeInfo()` reads a volume superblock without constructing a full volume.

`ReadBlocks()` maps APFS physical addresses to the main or tier2 `Device` based on `FUSION_TIER2_DEVICE_BYTE_ADDR`; `ReadAndVerifyHeaderBlock()` adds checksum verification. Encryption entry points delegate to `KeyManager`.

`dump()` is a high-level diagnostic traversal for container blocks: NXSB, keybag, checkpoint descriptor/data areas, EFI jumpstart, OMAP, spaceman, IP bitmaps, free-queue trees, CABs, and CIBs.

Global debug state is defined here: `int g_debug = 0; bool g_lax = false;`. Notable risks include limited use of `m_main_part_len`/`m_tier2_part_len` bounds and reliance on raw pointer lifetime for supplied devices.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/ApfsContainer.cpp -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/ApfsContainer.h -->
# File Research: sources/local-fs/apfs-fuse/ApfsLib/ApfsContainer.h

This header defines the `ApfsContainer` class, the main object representing an APFS container over one or two `Device` instances. It exposes initialization, volume lookup, volume-info lookup, block reads, checksum-verified header reads, block size/count/free count accessors, volume key lookup, password hint lookup, and diagnostic dumping.

Internally it stores main and tier2 device pointers plus partition offsets/lengths, the current `nx_superblock_t`, a `CheckPointMap`, a B-tree-backed container OMAP, spaceman data, free queue trees, and `KeyManager`.

The constructor accepts raw non-owning device pointers. Volumes returned by `GetVolume()` are heap allocated and caller-owned. This mirrors the older code style used throughout the project.

It imports `BTree.h`, `DiskStruct.h`, `Device.h`, `CheckPointMap.h`, `ApfsNodeMapperBTree.h`, and `KeyMgmt.h`, making it the central aggregation point for container-level APFS parsing.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/ApfsContainer.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/ApfsDir.cpp -->
# File Research: sources/local-fs/apfs-fuse/ApfsLib/ApfsDir.cpp

`ApfsDir` implements APFS filesystem-tree operations: inode lookup, directory listing, name lookup, file content reads, extended attribute listing, extended attribute retrieval, xattr info retrieval, and key comparators for normal filesystem and sealed-volume extent trees.

`GetInode()` looks up `APFS_TYPE_INODE` keys and copies core inode fields plus optional xfields such as snapshot XID, delta tree OID, document ID, name, previous file size, dstream, FS UUID, and sparse-byte count.

`ListDirectory()` iterates `APFS_TYPE_DIR_REC` entries under a parent inode. It supports both legacy and hashed directory record keys depending on volume text format flags, and decodes sibling-id xfields. `LookupName()` builds the exact key, including APFS filename hash for case/normalization-insensitive volumes.

`ReadFile()` resolves file extents and reads file data through `ApfsVolume::ReadBlocks()`. For sealed volumes it uses the fext tree; otherwise it uses regular filesystem-tree file extent records. Sparse extents are zero-filled.

Xattr paths support embedded xattrs and stream-backed xattrs; stream-backed data is read through `ReadFile()` using the xattr object ID and dstream sizes.

Notable risks: many xfield size checks are `assert()`, so release builds may continue on malformed data. Several TODOs remain for Finder info, dir stats, and sealed-volume crypto handling.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/ApfsDir.cpp -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/ApfsDir.h -->
# File Research: sources/local-fs/apfs-fuse/ApfsLib/ApfsDir.h

This header declares `ApfsDir`, the read-only directory/file facade over an `ApfsVolume` filesystem B-tree. Public methods cover inode metadata, directory enumeration, name lookup, file reads, xattr listing, xattr data, and xattr metadata.

Nested `Inode` stores APFS inode fields plus decoded optional xfields and a bitmask of which optional fields were present. `DirRec` stores directory entry fields including APFS hash, name, file ID, date, flags, and optional sibling ID. `XAttr` stores xattr flags, data length, and stream descriptor.

Private state caches volume reference, filesystem B-tree reference, text format flags, block size, block masks/shifts, and a temporary block buffer for partial reads.

The header declares `XAttr()` and copy constructor, but those constructors are not implemented in the corresponding `ApfsDir.cpp` file in this group, which may rely on absence of use or cause link issues if instantiated directly.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/ApfsDir.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/ApfsNodeMapper.cpp -->
# File Research: sources/local-fs/apfs-fuse/ApfsLib/ApfsNodeMapper.cpp

This file contains only the trivial constructor and virtual destructor definitions for the abstract `ApfsNodeMapper` base class.

There is no mapping behavior here. Implementations are supplied by `CheckPointMap` and `ApfsNodeMapperBTree`.

Its purpose is ABI/linkage support for the polymorphic mapper interface used by `BTree` and container/volume object-map resolution.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/ApfsNodeMapper.cpp -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/ApfsNodeMapper.h -->
# File Research: sources/local-fs/apfs-fuse/ApfsLib/ApfsNodeMapper.h

This header defines `omap_res_t`, the normalized result of APFS object-map resolution: OID, XID, flags, object size, and physical address.

`ApfsNodeMapper` is an abstract interface with one operation, `Lookup(omap_res_t&, oid_t, xid_t)`. B-tree code depends on this interface to convert logical APFS object IDs into physical block addresses.

The interface keeps checkpoint maps and B-tree object maps interchangeable from the B-tree reader’s perspective.

It depends only on `ApfsTypes.h`, making it a small foundational type boundary.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/ApfsNodeMapper.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/ApfsNodeMapperBTree.cpp -->
# File Research: sources/local-fs/apfs-fuse/ApfsLib/ApfsNodeMapperBTree.cpp

This file implements object-map lookup using an APFS OMAP B-tree. `Init()` reads and verifies the `omap_phys_t` block at the OMAP OID, copies its header, validates type intent, and initializes an internal `BTree` using `om_tree_oid`.

`Lookup()` constructs an `omap_key_t` with requested OID/XID and searches the OMAP tree using a comparator that orders by OID then XID. It requests non-exact lookup, then verifies the returned OID matches, allowing the B-tree search to return the nearest mapping.

Successful lookups populate `omap_res_t` with returned OID, XID, flags, object size, and physical address from `omap_val_t`.

Notable risk: `CompareOMapKey()` asserts `ekey_len == sizeof(omap_val_t)`, but `ekey` is interpreted as `omap_key_t`; this looks like a copy/paste assert bug and can mislead debugging.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/ApfsNodeMapperBTree.cpp -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/ApfsNodeMapperBTree.h -->
# File Research: sources/local-fs/apfs-fuse/ApfsLib/ApfsNodeMapperBTree.h

This header declares `ApfsNodeMapperBTree`, an `ApfsNodeMapper` implementation backed by a `BTree`.

It stores a copied `omap_phys_t`, the B-tree itself, and a reference to `ApfsContainer` for verified block reads. Public API includes constructor, destructor, `Init()`, `Lookup()`, and `dump()` forwarding to the internal tree.

It is used for both container and volume object-map resolution. The class binds APFS logical object identity to the generic B-tree traversal code.

Dependencies are `DiskStruct.h`, `ApfsNodeMapper.h`, and `BTree.h`.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/ApfsNodeMapperBTree.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/ApfsTypes.h -->
# File Research: sources/local-fs/apfs-fuse/ApfsLib/ApfsTypes.h

This small header defines common APFS scalar aliases used across the library.

Types are `apfs_uuid_t` as a 16-byte array, `paddr_t` as `uint64_t`, `oid_t` as `uint64_t`, and `xid_t` as `uint64_t`.

The comment notes Apple treats physical addresses as signed in some contexts, but this implementation uses unsigned `uint64_t`.

It is a low-level dependency for mappers, disk structs, and APFS parsing code.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/ApfsTypes.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/ApfsVolume.cpp -->
# File Research: sources/local-fs/apfs-fuse/ApfsLib/ApfsVolume.cpp

`ApfsVolume` represents a mounted APFS volume. `Init()` reads and verifies the APFS superblock, initializes the volume OMAP, handles encrypted volumes by obtaining a VEK through `ApfsContainer`, and initializes root, extent-ref, snapshot metadata, and sealed-volume fext trees.

`MountSnapshot()` starts from a live volume superblock, looks up snapshot metadata by XID, reads the snapshot superblock, repeats encryption setup, and initializes volume trees for the snapshot view.

`dump()` renders the volume superblock, volume OMAP, OMAP snapshot tree, ER state, OMAP tree, filesystem tree, snapshot metadata tree, optional integrity metadata, snapshot metadata extension, and fext tree.

`ReadBlocks()` delegates to container physical reads, then decrypts AES-XTS in 0x200-byte units when the volume is encrypted and an XTS tweak is supplied.

`CompareSnapMetaKey()` compares snapshot metadata and snapshot-name keys for snapshot lookup.

Notable risks: encrypted snapshot mounting does not check `container.IsUnencrypted()` the same way `Init()` does. Sealed-volume fext tree support is present, but some crypto handling is marked TODO elsewhere.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/ApfsVolume.cpp -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/ApfsVolume.h -->
# File Research: sources/local-fs/apfs-fuse/ApfsLib/ApfsVolume.h

This header declares `ApfsVolume`, the APFS volume abstraction over an `ApfsContainer`.

Public API includes normal initialization, snapshot mounting, volume name access, diagnostic dumping, references to filesystem and fext B-trees, text-format flags, container access, encrypted-aware block reads, and sealed-volume detection.

Private state includes the copied APFS superblock, volume OMAP, filesystem tree, extent-ref tree, snapshot metadata tree, fext tree, physical address of the APFS superblock, encryption flag, and AES-XTS state.

The class is intentionally read-only. It exposes internal B-tree references because `ApfsDir` directly performs filesystem record lookups.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/ApfsVolume.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/BTree.cpp -->
# File Research: sources/local-fs/apfs-fuse/ApfsLib/BTree.cpp

This file implements the generic APFS B-tree reader. It supports fixed-size and variable-size key/value nodes, root and non-root node layout, object-map-backed node resolution, lookup, lower/upper-bound style searches, iterators, node caching, and recursive diagnostic dumping.

`BTreeNodeFix` reads `kvoff_t` entries and uses fixed key/value sizes from root `btree_info_t`. `BTreeNodeVar` reads `kvloc_t` entries with per-entry key/value lengths. Both return borrowed pointers into the node’s owned block buffer, while `BTreeEntry` keeps a shared node reference so pointers remain valid.

`BTree::Init()` loads the root, extracts `btree_info_t`, and stores OID/XID/mapper. `Lookup()` descends internal nodes using `FindBin(..., LE)`, resolves child OIDs including hashed-node child offsets, then searches leaves using exact or less/equal mode. `GetIterator()` and `GetIteratorBegin()` provide ordered traversal.

`GetNode()` maps OIDs through an optional `ApfsNodeMapper`, reads via `ApfsVolume` when volume encryption may apply, otherwise reads verified container blocks. With `BTREE_USE_MAP`, it caches up to 8192 nodes and prunes shared_ptrs with use count 1.

Notable risks: binary search assumes comparator return is exactly -1/0/1 and indexes `resstr[rc + 1]` in debug mode. Node validation is mostly checksum-based; malformed table offsets can still drive pointer arithmetic.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/BTree.cpp -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/BTree.h -->
# File Research: sources/local-fs/apfs-fuse/ApfsLib/BTree.h

This header defines the APFS B-tree reader types: `BTreeEntry`, abstract `BTreeNode`, `BTreeNodeFix`, `BTreeNodeVar`, `BTree`, and `BTreeIterator`.

`BTCompareFunc` defines the comparator contract: compare search key to entry key and return -1, 0, or 1. `CompareStdKey()` is declared as a generic uint64 comparator.

`BTreeEntry` is non-copyable and stores key/value pointers plus lengths. `BTreeNode` owns a block buffer and exposes APFS node metadata. `BTree` owns the root, tree info, optional OMAP mapper, optional volume pointer, OID/XID, debug flag, and an optional mutex-protected node cache.

`BTreeIterator` tracks current node/index and can advance across leaf nodes by walking parent links and descending to the next leaf.

The header enables `BTREE_USE_MAP` by default and sets the cache target to 8192 nodes, documented as roughly 32 MB for 4 KiB nodes.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/BTree.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/BlockDumper.cpp -->
# File Research: sources/local-fs/apfs-fuse/ApfsLib/BlockDumper.cpp

`BlockDumper` is the central APFS diagnostic formatter. It maps APFS object types and B-tree subtypes to textual dumps, printing object headers, block-specific metadata, B-tree headers, entries, flags, timestamps, UUIDs, and trimmed hex dumps.

`DumpNode()` dispatches by `OBJECT_TYPE_MASK` to container superblocks, APFS volume superblocks, B-tree roots/nodes, spaceman/CAB/CIB/bitmap-related metadata, OMAP, checkpoint maps, reaper state, EFI jumpstart, Fusion writeback cache/list, encryption-rolling state, snapshot metadata extensions, and integrity metadata.

B-tree entry dumpers cover filesystem tree records, OMAP entries, physical extent refs, snapshot metadata/name records, OMAP snapshots, spaceman free queues, gbitmap records, Fusion middle tree records, sealed-volume fext tree records, and unknown entries.

Filesystem-tree formatting decodes inode records, xattrs including symlink/quarantine/decmpfs special cases, sibling links/maps, dstream IDs, crypto states, file extents, directory records, and file-info hashes. It also decodes APFS xfields for inodes and directory records.

The file contains extensive flag-description tables for APFS/NX/inode/xattr/B-tree/Fusion flags and helper formatters `flagstr`, `enumstr`, `GetNodeType`, `tstamp`, and overloaded `dumpm()` field printers.

Notable risks: this is diagnostic code and uses many `assert()` calls and direct struct casts. Unknown or malformed blocks may produce noisy output or hex dumps rather than robust error recovery.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/BlockDumper.cpp -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/BlockDumper.h -->
# File Research: sources/local-fs/apfs-fuse/ApfsLib/BlockDumper.h

This header declares `FlagDesc` and `BlockDumper`.

Public API is small: constructor, destructor, text-flag setter, block-size getter/setter, `DumpNode()`, stream accessor, and static `GetNodeType()`. The rest is private dump dispatch and formatting machinery.

Private methods include block dumpers for APFS/NX object types, B-tree node/entry dumpers for known subtypes, xfield dumping, hex dumping, flag/enum formatting, timestamp formatting, and typed field printers.

State consists of APFS text flags, output stream reference, current block pointer, and current block size. It is not thread-safe and is designed for synchronous diagnostic rendering.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/BlockDumper.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/CheckPointMap.cpp -->
# File Research: sources/local-fs/apfs-fuse/ApfsLib/CheckPointMap.cpp

`CheckPointMap` implements `ApfsNodeMapper` for APFS checkpoint maps. `Init()` reads a contiguous checkpoint-map block range from the container, verifies each header block, and ensures object type is `OBJECT_TYPE_CHECKPOINT_MAP`.

`Lookup()` linearly scans all stored checkpoint map blocks and entries for a matching OID, ignoring the requested XID. It returns OID, checkpoint XID, size, and physical address in `omap_res_t`.

`dump()` passes the stored checkpoint map data to `BlockDumper`.

This mapper is used early during container initialization before the normal OMAP B-tree can be used, especially to resolve spaceman and free-queue objects.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/CheckPointMap.cpp -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/CheckPointMap.h -->
# File Research: sources/local-fs/apfs-fuse/ApfsLib/CheckPointMap.h

This header declares `CheckPointMap`, an `ApfsNodeMapper` backed by in-memory checkpoint-map block data.

It stores an `ApfsContainer&`, a vector of checkpoint-map bytes, the root checkpoint-map OID, and block size.

Public API includes construction, destruction, `Init(root_oid, blk_count)`, `Lookup()`, and diagnostic `dump()`.

It is intentionally simple and linear because checkpoint maps are small bootstrap metadata compared with APFS object-map B-trees.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/CheckPointMap.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/Crc32.cpp -->
# File Research: sources/local-fs/apfs-fuse/ApfsLib/Crc32.cpp

This file implements a table-driven CRC-32 helper with reflected and non-reflected modes.

The constructor builds the 256-entry lookup table from the supplied polynomial, reversing the polynomial bit order when reflected mode is requested. `Calc()` dispatches each byte to little/reflected or big/non-reflected update logic.

`GetDataCRC()` sets the initial XOR value, processes a buffer, and returns final-XOR-adjusted CRC.

The class is used by disk image and GPT-related code, not APFS block checksum verification, which uses APFS Fletcher-style checksum utilities elsewhere.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/Crc32.cpp -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/Crc32.h -->
# File Research: sources/local-fs/apfs-fuse/ApfsLib/Crc32.h

This header declares `Crc32`, a reusable CRC-32 calculator.

Public API includes constructor with reflect flag and optional polynomial, destructor, `SetCRC`, `GetCRC`, incremental `Calc`, and one-shot `GetDataCRC`.

Private state is the 256-entry CRC table, current CRC value, and reflect-mode flag. Private helpers perform little/reflected and big/non-reflected byte updates.

It includes `Global.h`, though the class itself only needs standard integer and size types in this header.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/Crc32.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/Decmpfs.cpp -->
# File Research: sources/local-fs/apfs-fuse/ApfsLib/Decmpfs.cpp

This file implements APFS/HFS-style `com.apple.decmpfs` compressed-file expansion. It supports algorithms 3/4 zlib, 7/8 LZVN, 9/10 uncompressed, 11/12 LZFSE, and 13/14 LZBITMAP, with even-numbered variants stored in the resource fork.

`IsDecompAlgoSupported()` and `IsDecompAlgoInRsrc()` classify algorithm IDs. `DecompressFile()` validates the compression header, logs algorithm details when debug is enabled, and either decodes inline attribute data or reads `com.apple.ResourceFork` through `ApfsDir`.

Resource-fork zlib mode parses a resource fork header and `CmpfRsrc` entries. Other resource-fork modes use an offset list of 64 KiB chunks. Inline modes decode directly from xattr payload after `CompressionHeader`.

It uses decompression helpers from `Util.h`: zlib, LZVN, LZFSE, and LZBITMAP. It also handles uncompressed marker bytes for several formats.

Notable risks: many format assumptions are enforced with `assert()` or comments like “Assuming”. Bounds checks exist for some chunk sizes but not every pointer derived from resource-fork offsets.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/Decmpfs.cpp -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/Decmpfs.h -->
# File Research: sources/local-fs/apfs-fuse/ApfsLib/Decmpfs.h

This header declares the decmpfs compression interface.

`CompressionHeader` contains little-endian signature, algorithm, and uncompressed size. Public helpers classify supported algorithms and whether compressed bytes live in a resource fork.

`DecompressFile()` takes an `ApfsDir`, inode number, output vector, and compressed xattr payload. The `ApfsDir` dependency is required because some decmpfs formats store data chunks in `com.apple.ResourceFork`.

This is an APFS file-content helper, not a block-device decompressor.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/Decmpfs.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/Device.cpp -->
# File Research: sources/local-fs/apfs-fuse/ApfsLib/Device.cpp

This file implements the abstract `Device` base constructor/destructor and the `Device::OpenDevice()` factory.

The factory recognizes Windows physical drive names, `.dmg` files, `.sparseimage` files, then falls back to platform-specific regular device/file implementations: `DeviceWinFile`, `DeviceLinux`, or `DeviceMac`.

`.dmg` and `.sparseimage` are opened via image-aware adapters that may understand compression/encryption. VDI support is included by header but not selected by extension in this factory.

The base constructor sets default sector size to 0x200. Returned devices are raw heap pointers; callers own deletion and closing.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/Device.cpp -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/Device.h -->
# File Research: sources/local-fs/apfs-fuse/ApfsLib/Device.h

This header declares the abstract block/byte device interface used by APFS container code and tools.

Required virtual methods are `Open`, `Close`, `Read(data, offs, len)`, and `GetSize`. It also provides sector-size accessors and the static `OpenDevice()` factory.

Offsets and lengths are byte-based at this layer; APFS block addressing is handled above by `ApfsContainer`, `ApfsVolume`, or `Dumper`.

The interface is read-only. There are no write, flush, or mutation paths.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/Device.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/DeviceDMG.cpp -->
# File Research: sources/local-fs/apfs-fuse/ApfsLib/DeviceDMG.cpp

`DeviceDMG` implements a read-only device adapter for Apple DMG images. It wraps `DiskImageFile`, which may decrypt encrypted DMGs, then parses the trailing `koly` header and block-run metadata.

If no `koly` signature is found, it treats the file as raw. For normal DMG, it uses XML plist metadata, finds `resource-fork/blkx` arrays, extracts `mish` data blobs, and converts `MishEntry` runs into `DmgSection` records.

`Read()` binary-searches the section containing the requested logical byte offset, reads raw sections directly, zero-fills ignored sections, and decompresses ADC, zlib, bzip2, or LZFSE sections. With `DMG_CACHE` enabled, it caches one decompressed compressed section globally.

`ProcessHeaderRsrc()` is unimplemented and returns false, so legacy resource-fork-only DMGs are unsupported. `ProcessMish()` skips terminator/special methods `0xFFFFFFFF` and `0x7FFFFFFE`.

Notable risks: decompressor return lengths are not validated in all paths, section ordering is assumed for binary search, and large compressed sections can allocate full uncompressed section buffers.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/DeviceDMG.cpp -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/DeviceDMG.h -->
# File Research: sources/local-fs/apfs-fuse/ApfsLib/DeviceDMG.h

This header declares `DeviceDMG`, a `Device` implementation for DMG files.

Internal `DmgSection` stores compression method, comment, logical disk offset/length, source DMG offset/length, and optional per-section cache. The class stores `DiskImageFile`, logical size, data-fork offset, raw-image flag, CRC helper, section vector, optional debug stream, and optional global cache.

Public methods implement the standard `Device` interface: open, close, read, and size.

Private methods parse XML plist headers, resource-fork headers, and `mish` block maps. Resource-fork parsing is declared but not implemented in the `.cpp`.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/DeviceDMG.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/DeviceLinux.cpp -->
# File Research: sources/local-fs/apfs-fuse/ApfsLib/DeviceLinux.cpp

This Linux-only implementation opens a path read-only with `O_LARGEFILE`, determines size via `fstat64` for regular files or `BLKGETSIZE64` for block devices, and reads via `pread64`.

`Close()` closes the file descriptor and resets size. Destructor calls `Close()`.

The class logs open failures and optional debug info using `g_debug`.

Notable risk: `Read()` stores `pread64()` result in `size_t`; errors return `-1`, which converts to a large unsigned value. The equality check still fails for ordinary lengths, but the type is semantically wrong.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/DeviceLinux.cpp -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/DeviceLinux.h -->
# File Research: sources/local-fs/apfs-fuse/ApfsLib/DeviceLinux.h

This Linux-only header declares `DeviceLinux`, a `Device` backed by a POSIX file descriptor.

It exposes standard open/close/read/size methods and stores `int m_device` plus `uint64_t m_size`.

Compilation is guarded by `#ifdef __linux__`.

It is the default fallback device implementation selected by `Device::OpenDevice()` on Linux.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/DeviceLinux.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/DeviceMac.cpp -->
# File Research: sources/local-fs/apfs-fuse/ApfsLib/DeviceMac.cpp

This macOS-only implementation opens files/devices read-only and determines size by `stat` for regular files or `DKIOCGETBLOCKCOUNT`/`DKIOCGETBLOCKSIZE` for block/character devices.

Reads are performed with `pread`. `Close()` closes the descriptor and resets state; destructor calls `Close()`.

It prints some device mode and geometry information unconditionally, plus optional debug open info.

Notable risk: like the Linux version, `Read()` stores `pread()` return in `size_t`, which is not ideal for error handling. It also does not check ioctl return codes before computing size.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/DeviceMac.cpp -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/DeviceMac.h -->
# File Research: sources/local-fs/apfs-fuse/ApfsLib/DeviceMac.h

This macOS-only header declares `DeviceMac`, a `Device` backed by a POSIX file descriptor and macOS disk ioctls.

It exposes open, close, read, and size methods, and stores descriptor plus byte size.

Compilation is guarded by `#ifdef __APPLE__`.

It is selected by `Device::OpenDevice()` as the fallback device implementation on macOS.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/DeviceMac.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/DeviceSparseImage.cpp -->
# File Research: sources/local-fs/apfs-fuse/ApfsLib/DeviceSparseImage.cpp

`DeviceSparseImage` implements Apple sparseimage band mapping. It opens the underlying `DiskImageFile`, handles possible disk-image encryption, reads the sparseimage header node, validates the `sprs` signature, computes logical size and band size, and builds a logical-band-to-file-offset table.

The first header node contributes up to `0x3F0` band IDs; chained index nodes contribute up to `0x3F2` band IDs each. Non-present bands are represented as zero offsets.

`Read()` splits reads across bands, reading present bands from the image file and zero-filling absent bands.

Notable risks: `Read()` computes `chunk = offs >> 20`, hardcoding a 1 MiB band shift even though `m_band_size` is read from the header. `Open()` checks `hdr.signature` inside the index-node loop instead of `idx.magic`, likely a bug.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/DeviceSparseImage.cpp -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/DeviceSparseImage.h -->
# File Research: sources/local-fs/apfs-fuse/ApfsLib/DeviceSparseImage.h

This header declares `DeviceSparseImage`, a `Device` implementation for `.sparseimage` files.

It stores a vector mapping logical bands to physical file offsets, logical image size, band size, and the underlying `DiskImageFile`.

Public methods implement the standard device API.

The adapter is read-only and sparse-aware, returning zeroes for unallocated bands.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/DeviceSparseImage.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/DeviceVDI.cpp -->
# File Research: sources/local-fs/apfs-fuse/ApfsLib/DeviceVDI.cpp

`DeviceVDI` implements a minimal VirtualBox VDI reader. It parses the preheader and version 1+ header, validates signature `0xBEDA107F` and version `0x00010001`, extracts disk size, block size, total block count, data offset, and block map.

`Read()` splits reads across VDI blocks, maps logical block numbers through the block map, zero-fills unallocated blocks (`0xFFFFFFFF`), and reads allocated blocks from `data_offset + map_entry * block_size + block_offs`.

The implementation uses C `FILE*` I/O and `fopen_s`, which is MSVC-oriented and may need portability support elsewhere.

Notable risks: block number is computed as `offs >> 20`, assuming 1 MiB blocks even though `m_block_size` is read from the VDI header. There are no bounds checks for `block_nr` against `m_block_map`.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/DeviceVDI.cpp -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/DeviceVDI.h -->
# File Research: sources/local-fs/apfs-fuse/ApfsLib/DeviceVDI.h

This header declares `DeviceVDI`, a `Device` implementation for VirtualBox VDI files.

It stores logical disk size, VDI block size/count, data offset, block map, and `FILE*`.

Public API is the standard `Device` open/close/read/size interface.

Although included by `Device.cpp`, `.vdi` extension dispatch is not implemented in `Device::OpenDevice()` in the read file set.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/DeviceVDI.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/DeviceWinFile.cpp -->
# File Research: sources/local-fs/apfs-fuse/ApfsLib/DeviceWinFile.cpp

This Windows-only implementation reads a regular file via `std::ifstream`.

`Open()` opens the file in binary mode, seeks to end to determine size, then rewinds. `Close()` closes the stream. `Read()` seeks to the requested offset and reads the requested length.

Notable risk: `Read()` always returns true and has a TODO for error handling, so short reads or stream failures are not reported to callers.

It is selected as the default fallback by `Device::OpenDevice()` on Windows when the path is not a physical drive or recognized image type.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/DeviceWinFile.cpp -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/DeviceWinFile.h -->
# File Research: sources/local-fs/apfs-fuse/ApfsLib/DeviceWinFile.h

This Windows-only header declares `DeviceWinFile`, a `Device` backed by `std::ifstream`.

It stores the input stream and byte size, and implements open, close, read, and size.

Compilation is guarded by `_WIN32`.

The class is simple regular-file support for Windows APFS image use.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/DeviceWinFile.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/DeviceWinPhys.cpp -->
# File Research: sources/local-fs/apfs-fuse/ApfsLib/DeviceWinPhys.cpp

This Windows-only implementation reads physical drives using Win32 APIs. `Open()` converts the UTF-8 path to wide chars, opens it with `CreateFile`, queries `IOCTL_DISK_GET_DRIVE_GEOMETRY_EX`, and stores disk size.

`Read()` seeks with `SetFilePointerEx` and reads with `ReadFile`. `Close()` closes the handle and resets state.

It is selected by `Device::OpenDevice()` for paths beginning with `\\.\PhysicalDrive`.

Notable risks: `Read()` returns only the `ReadFile` boolean and does not verify `read_bytes == len`. `Open()` does not close the handle if geometry query fails with zero bytes returned.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/DeviceWinPhys.cpp -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/DeviceWinPhys.h -->
# File Research: sources/local-fs/apfs-fuse/ApfsLib/DeviceWinPhys.h

This Windows-only header declares `DeviceWinPhys`, a `Device` backed by a Win32 `HANDLE` to a physical disk.

It exposes open, close, read, and size methods. Private state is the drive handle and byte size.

The header includes `Windows.h` and `tchar.h`, guarded by `_WIN32`.

It supports read-only raw disk access for Windows APFS containers and Fusion components.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/DeviceWinPhys.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/DiskImageFile.cpp -->
# File Research: sources/local-fs/apfs-fuse/ApfsLib/DiskImageFile.cpp

`DiskImageFile` is a lower-level file wrapper for raw and encrypted Apple disk images. It opens an `ifstream`, detects encryption signatures, sets up decryption, and reads decrypted byte ranges.

`CheckSetupEncryption()` detects v1 encrypted DMGs by trailing `cdsaencr` and v2 by leading `encrcdsa`. V1 setup reads the trailing crypto header; V2 reads key pointer/key data records from the front of the image.

Both setup paths prompt for a password, derive a 3DES wrapping key with PBKDF2-HMAC-SHA1, unwrap AES and HMAC keys, and configure AES-CBC content decryption. Read-time IVs are derived as HMAC-SHA1 over the big-endian block number.

`Read()` handles unencrypted direct reads or encrypted block-aligned/unaligned reads through a temporary 0x1000 buffer and AES-CBC decryption with per-block IV.

Notable risks: password prompts are interactive, limiting automation. The encrypted read buffer is fixed at 0x1000, so images with larger crypto block sizes would overflow. HMAC/integrity verification is not performed; HMAC is only used for IV derivation.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/DiskImageFile.cpp -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/DiskImageFile.h -->
# File Research: sources/local-fs/apfs-fuse/ApfsLib/DiskImageFile.h

This header declares `DiskImageFile`, a read-only file wrapper with optional encrypted-DMG decoding.

Public API includes open, close, reset, byte-range read, content-size accessor, and encryption setup detection.

Private methods implement v1/v2 encryption setup and PKCS unpadding. Private state includes the image stream, encryption flag, encrypted-content offset/size/block size, HMAC key, and AES context.

It is used by `DeviceDMG` and `DeviceSparseImage` as the underlying byte source.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/DiskImageFile.h -->