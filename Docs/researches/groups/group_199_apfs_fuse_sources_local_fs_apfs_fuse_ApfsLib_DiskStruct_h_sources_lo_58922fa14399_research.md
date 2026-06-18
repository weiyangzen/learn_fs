# Group Research: group_199_apfs_fuse_sources_local_fs_apfs_fuse_ApfsLib_DiskStruct_h_sources_lo_58922fa14399

Scope verified against `Docs/research_subset_a.md`: all files are under `sources/local-fs/apfs-fuse`, which is included in subset A. Each listed file was read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/DiskStruct.h -->
# File Research: sources/local-fs/apfs-fuse/ApfsLib/DiskStruct.h

This header is the central packed on-disk APFS schema definition for apfs-fuse. It contains little-endian physical structures, object type constants, feature/incompatibility flags, B-tree record layouts, filesystem object records, allocation metadata, crypto/keybag records, encryption rolling state, sealed volume hash structures, and Fusion Drive structures.

The file uses `#pragma pack(1)` around all disk structures and builds on `ApfsTypes.h` plus `Endian.h`, so almost every multibyte field is declared through `le_*` wrapper types or aliases. It defines core APFS address/id aliases such as `le_paddr_t`, `le_oid_t`, and `le_xid_t`, then defines the common object header `obj_phys_t` with checksum, object id, transaction id, type, and subtype. This header is the structural dependency for nearly every APFS parser in the library.

Major APFS container structures include `nx_superblock_t`, checkpoint mapping records, object map records, EFI jumpstart records, spaceman records, reaper records, and Fusion cache/mapping records. `nx_superblock_t` captures block size/count, feature masks, checkpoint descriptor/data ring state, spaceman/omap/reaper object IDs, volume OIDs, counters, EFI jumpstart, Fusion metadata, keylocker ranges, and newer container state. The supported feature masks are conservative: container read-only-compatible mask is zero, while supported incompatible features include version 2 and Fusion.

Major APFS volume structures include `apfs_superblock_t`, volume role constants, feature and incompatibility masks, volume encryption flags, filesystem root/extent/snapshot tree references, counts, volume UUID/name, role, volume group ID, integrity metadata, and file extent tree references. It also defines object-id/type packing through `j_key_t`, `OBJ_ID_MASK`, `OBJ_TYPE_MASK`, `OBJ_TYPE_SHIFT`, and `APFS_TYPE_ID`.

The file defines all main APFS catalog/journal object record formats used by directory and file lookup code: inode keys/values, directory records including hashed directory keys, directory stats, xattrs, physical extents, file extents, dstream records, sibling links/maps, snapshot metadata/names, crypto records, and file-info records. Variable-length records use flexible array members or zero-length arrays, matching the codebase’s C/C++ disk parsing style.

The B-tree section defines `btree_node_phys_t`, `btree_info_t`, key/value location tables, index node values, B-tree flags, and node flags. These structures establish how the APFS B-tree reader interprets table-of-contents offsets, fixed versus variable key/value layout, root/leaf status, hashed nodes, and no-header nodes.

The spaceman section models APFS allocation state: chunk info blocks, chunk address blocks, free queue keys/values, devices, allocation zones, data zones, and `spaceman_phys_t`. It includes constants for allocation-zone counts, main/tier2 devices, free queues, versioned spaceman flags, chunk count masks, and internal pool bitmap limits.

The crypto/keybag section defines wrapped crypto states, keybag entries, media keybag layout, keybag tags, protection classes, wrapped key sizes, and crypto IDs. These records are consumed by key-management code to load container and volume keybags, locate wrapped KEKs/VEKs, and derive volume keys for encrypted APFS volumes.

The later sections define encryption rolling state (`er_state_phys_t`, v1 state, recovery blocks, bitmap records, ER flags/phases), sealed-volume integrity metadata (`integrity_meta_phys_t`, APFS hash types/sizes, file data hash records), and Fusion write-back cache/list/mapping structures. This makes the header broader than the current read-only mount path: it describes many APFS features that may only be partially consumed elsewhere.

Notable implementation constraints: the file assumes binary compatibility with APFS disk layout and uses packed structs plus flexible arrays, so consumers must bounds-check external block data before casting. Many constants document newer APFS features, but parser support may lag the declarations. Any changes here have high blast radius because the whole APFS library depends on the exact field offsets and masks.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/DiskStruct.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/Endian.h -->
# File Research: sources/local-fs/apfs-fuse/ApfsLib/Endian.h

This header provides endian conversion support and disk-field wrapper types for APFS parsing. It currently forces `APFS_LITTLE_ENDIAN` and undefines `APFS_BIG_ENDIAN`, then supplies platform-specific byte-swap definitions for MSVC, Linux, and macOS.

On little-endian builds, little-endian disk types are simple typedefs to native integer types, while big-endian integer fields are packed wrapper structs with assignment and conversion operators that byte-swap on access. This matches APFS’s little-endian disk layout while still allowing some big-endian fields for formats such as GPT.

The big-endian build path defines little-endian wrapper structs and native big-endian typedefs, but it is effectively dormant because the file unconditionally defines `APFS_LITTLE_ENDIAN`. The comment says this should later be configuration-driven. The big-endian branch also appears less complete than the little-endian branch, so actual cross-endian support should be treated as aspirational unless tested.

The header also includes a disabled generic `be<T>`/`le<T>` template approach under `#if 0`, suggesting the current code chose explicit typedefs/wrappers to keep disk structs simple and packed. MSVC handling temporarily defines `__attribute__` away to let packed wrappers compile.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/Endian.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/Global.h -->
# File Research: sources/local-fs/apfs-fuse/ApfsLib/Global.h

This small header declares process-wide debug and lax-mode globals used by the APFS library. `g_debug` and `g_lax` are defined elsewhere, with comments pointing to `ApfsContainer.cpp`.

It also defines debug flag bits through `DbgFlags`: errors, informational logging, directory tracing, compressed-file tracing, and crypto tracing. Utility logging functions and crypto/keybag dump paths use these flags to decide what to print.

The file has no implementation logic and exists as a shared declaration point. Because it exposes mutable globals, behavior such as logging verbosity and lax validation is configured process-wide rather than per-container or per-mount.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/Global.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/GptPartitionMap.cpp -->
# File Research: sources/local-fs/apfs-fuse/ApfsLib/GptPartitionMap.cpp

This implementation reads, verifies, lists, and searches GPT partition maps so apfs-fuse utilities can locate an APFS partition inside a whole-disk image/device. It defines packed GPT header and partition-entry structs locally, validates their expected sizes, and uses `Device` reads plus `Crc32` verification.

`LoadAndVerify()` reads the primary GPT header at one sector offset. It first assumes the device’s reported sector size, then retries with 4096-byte sectors if the EFI PART signature is not found. It validates signature, revision `0x00010000`, header size, and 128-byte partition entry size. It then zeroes the header CRC field in the in-memory header, computes CRC32 over the header, and verifies it against the stored header CRC.

After header validation, `LoadAndVerify()` reads the partition entry array, rounded up to the sector size, from `PartitionEntryLBA`, then verifies the partition array CRC. On success it stores stable pointers into `m_hdr_data` and `m_entry_data`; on failure it clears backing buffers and returns false.

`FindFirstAPFSPartition()` scans entries until an all-zero start/end entry and returns the first entry whose partition type GUID matches the hard-coded Apple APFS GPT type GUID. `GetPartitionOffsetAndSize()` converts a selected entry’s starting and ending LBAs into byte offset and byte length using `m_sector_size`. `ListEntries()` prints type GUID, unique GUID, LBA range, attributes, and the UTF-16 partition name as single-byte characters.

Notable risks: `GetPartitionOffsetAndSize()` does not bounds-check `partnum` against the loaded entry count. `ListEntries()` prints UTF-16 partition names by truncating each code unit to `char`, which is fine for ASCII names but not general Unicode. The header CRC calculation mutates `HeaderCRC32` in the buffer and does not restore it before storing `m_hdr`; this is harmless for current readers but means `m_hdr->HeaderCRC32` is zero after successful load.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/GptPartitionMap.cpp -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/GptPartitionMap.h -->
# File Research: sources/local-fs/apfs-fuse/ApfsLib/GptPartitionMap.h

This header declares the `GptPartitionMap` helper class. It exposes construction, `LoadAndVerify(Device&)`, `FindFirstAPFSPartition()`, `GetPartitionOffsetAndSize()`, and `ListEntries()`.

Internally it owns a CRC32 object, raw backing buffers for the GPT header and entries, typed pointers into those buffers, and the detected sector size. The GPT structs themselves are forward-declared here and defined privately in the `.cpp`, keeping callers independent of the on-disk GPT layout.

This class is used by APFS utilities before constructing an `ApfsContainer`, allowing a whole-disk image to be converted into the byte range of the first APFS partition.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/GptPartitionMap.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/KeyMgmt.cpp -->
# File Research: sources/local-fs/apfs-fuse/ApfsLib/KeyMgmt.cpp

This file implements APFS keybag handling and password-based volume-key recovery for encrypted volumes. It depends on `ApfsContainer`, ASN.1 DER parsing, AES-XTS, SHA-256/HMAC/PBKDF2/RFC3394 key unwrap helpers, utility formatting/logging, and disk structures from `DiskStruct.h`.

`Keybag` owns a copied keybag locker blob. `Init()` accepts a `media_keybag_t`, requires locker version 2, copies `kl_nbytes` from the locker, and stores `m_kl` as a pointer into the owned vector. `GetKeyCnt()` reports `kl_nkeys`. `GetKey()` walks aligned `keybag_entry_t` records by rounding each entry size to 16-byte alignment. `FindKey()` scans entries for matching UUID and tag.

`Keybag::dump()` prints keybag metadata and each key record. For container keybags it labels volume keys and keybag references; for volume unlock-record bags it labels KEKs and password hints. It can DER-dump key blobs, print keybag reference block ranges, and optionally dump raw key material if `DUMP_RAW_KEYS` is enabled. The debug output explicitly warns that password-derived keys, KEKs, and VEKs are sensitive.

`KeyManager` owns a reference to the container, the loaded container keybag, the container UUID, and validity/unencrypted flags. `Init()` loads the container keybag from a block range and records validity. `GetPasswordHint()` locates a volume unlock-record pointer in the container keybag, loads the volume records keybag, then extracts `KB_TAG_VOLUME_PASSPHRASE_HINT`.

`GetVolumeKey()` is the main encrypted-volume path. It loads the volume records keybag referenced by the container keybag, iterates all KEK entries, DER-decodes each KEK, derives a 256-bit password key using `PBKDF2_HMAC_SHA256(password, salt, iterations)`, and tries RFC3394 unwrapping. If the KEK blob flags indicate the AES-128 wrapping variant, it unwraps 16 bytes and records AES-128 mode; otherwise it unwraps 32 bytes using AES-256. Once a KEK works, it finds the container VEK entry, DER-decodes it, and unwraps the VEK. For the AES-128/FileVault/CoreStorage-converted variant, it derives the second half of the XTS key by hashing `(VEK || vek_blob.uuid)` and taking 16 bytes; otherwise it unwraps the full 32-byte XTS key.

`LoadKeybag()` reads a keybag block range from the APFS container. If the object type is already the expected keybag type, it marks the key manager as unencrypted. Otherwise it decrypts the blocks using AES-XTS with the supplied UUID as both halves of the key, then verifies block checksums and initializes a `Keybag`. This supports APFS keybag storage where keybag blocks may be encrypted at rest.

`DecryptBlocks()` decrypts a block range in 512-byte units with AES-XTS. The tweak starts at `block * (container_block_size / 512)` and increments per 512-byte sector. This matches APFS’s sector-based XTS treatment inside larger filesystem blocks.

The DER decoding helpers parse APFS key headers, verify an HMAC-SHA256 over the DER body using a key derived from a fixed cookie and salt, then decode KEK- or VEK-specific fields. HMAC failure is logged but currently ignored, allowing parsing to proceed.

Notable risks and limitations: `LoadKeybag()` loops over `blockcnt` but calls `VerifyBlock(data.data(), blockcnt * blocksize)` each time, so the loop index is unused and it verifies the whole buffer repeatedly rather than each block. `Keybag::Init()` has a TODO noting it only works with one block. The DER HMAC check logs but does not reject invalid HMACs. `GetVolumeKey()` defaults `password` to `nullptr` in the header but passes it to `strlen(password)`, so callers must not rely on the default for encrypted volumes.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/KeyMgmt.cpp -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/KeyMgmt.h -->
# File Research: sources/local-fs/apfs-fuse/ApfsLib/KeyMgmt.h

This header declares `Keybag` and `KeyManager`, the two public key-management classes for APFS encryption support. It includes `Global.h`, which in turn provides APFS disk structures and debug flags.

`Keybag` exposes initialization from a `media_keybag_t`, key count lookup, indexed key access, UUID/tag key search, and formatted dumping. It owns the copied keybag bytes and a pointer to the locker structure inside that vector.

`KeyManager` exposes initialization from a keybag block range and container UUID, password hint retrieval, volume key derivation, validity/unencrypted status, and dumping. Private helpers load/decrypt keybags and decode DER KEK/VEK records.

The class is bound to an `ApfsContainer&`, so key operations read blocks through the container abstraction and use the container block size. The `GetVolumeKey()` declaration allows `password = nullptr`, but the implementation requires a valid C string when it reaches PBKDF2.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/KeyMgmt.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/PList.cpp -->
# File Research: sources/local-fs/apfs-fuse/ApfsLib/PList.cpp

This file implements a small XML property-list object model and parser. It defines runtime type checks for `PLObject`, concrete plist types for integer/string/data/array/dict, destructors that delete owned child objects, and a hand-written XML plist parser.

`PLObject::toInt()`, `toString()`, `toData()`, `toArray()`, and `toDict()` use `dynamic_cast` to safely downcast. Each concrete type returns its enum value through `type()` and exposes stored values through accessors declared in the header.

`PListXmlParser::Parse()` scans tags until it finds `<plist>`, then calls `ParseObject()` for the root. Parse errors are caught as `PLException`, printed to stderr, and return `nullptr`. Processing instructions and doctypes are recognized by `FindTag()` but not semantically processed.

`ParseArray()` repeatedly parses child objects until `ParseObject()` returns `nullptr`, which happens when an end tag is encountered. `ParseDict()` expects alternating `<key>text</key>` and object values until `</dict>`. It rejects empty keys and unexpected tags. `ParseObject()` handles integer, string, data, array, dict, and empty `<true/>`/`<false/>` tags. Booleans are represented as `PLInteger` values 1 and 0.

`Base64Decode()` decodes plist `<data>` contents while ignoring non-base64 whitespace and stopping at `=` padding. It pushes bytes after 2, 3, and 4 base64 characters.

`FindTag()` is a minimal tag scanner. It identifies start/end/empty/proc-instr/doctype tags and captures the tag name up to whitespace, slash, or `>`. It does not implement full XML parsing, attributes beyond skipping them, entity decoding, comments, CDATA, or robust malformed-input recovery.

At the end, the wrapper class `PList::parseXML()` is currently a stub that ignores its arguments and returns false. The usable parser is `PListXmlParser` directly, not the `PList` wrapper.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/PList.cpp -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/PList.h -->
# File Research: sources/local-fs/apfs-fuse/ApfsLib/PList.h

This header declares the plist object hierarchy and the XML parser interface. The supported plist types are integer, string, data, array, and dictionary.

`PLObject` is an abstract base with a virtual `type()` and typed downcast helpers. `PLInteger`, `PLString`, and `PLData` store scalar values. `PLArray` owns a vector of raw `PLObject*` children, and `PLDict` owns a map from strings to raw `PLObject*` values. Destructors in the `.cpp` perform deletion, so callers must respect ownership boundaries.

`PListXmlParser` is a single-pass parser over a caller-provided memory buffer. It exposes `Parse()` and privately implements array/dict/object parsing, base64 decoding, tag scanning, content extraction, and byte-wise character reads.

The `PList` wrapper class is declared but marked “Not used ... maybe later, if we need bplists ...”. Its XML parse method is not functional in the implementation. There is no binary plist parser here.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/PList.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/Unicode.cpp -->
# File Research: sources/local-fs/apfs-fuse/ApfsLib/Unicode.cpp

This file implements APFS-oriented Unicode normalization and optional case folding. It consumes generated lookup tables from `UnicodeTables_v10.h` and exposes routines used by filename hashing and normalized filename comparison.

`normalizeJimdo()` handles Hangul syllable decomposition algorithmically. Given a precomposed Hangul syllable, it emits leading consonant, vowel, and optional trailing consonant Jamo with canonical combining class zero.

`normalizeOptFoldU32Char()` is the core per-character normalization/folding routine. It rejects invalid/sentinel code points, maps supported Unicode ranges into table indices, looks up high/mid/low trie entries, handles direct identity/combining-class results, Hangul decomposition, invalid masks, two- and three-code-unit sequences, miscellaneous variable-length UTF-16 sequences, UTF-32 single mappings, and UTF-32 variable sequences. When case folding is enabled, it applies `nf_basic_cf` for code points below `0x500` and maps final combining Greek ypogegrammeni `0x345` to iota.

`CanonicalReorder()` reorders decomposed sequences by canonical combining class, preserving starter boundaries. It performs a local bubble-sort-like pass over adjacent nonzero combining-class ranges.

`NormalizeFoldString()` converts a vector of UTF-32 input characters into normalized decomposed output, optionally case-folded. It preallocates up to four output code points per input character, calls `normalizeOptFoldU32Char()` for each character, rejects invalid mappings, trims the output, and performs canonical reordering.

Important behavior: the normalization function returns false only when a character maps to `-1`; some unsupported sequence lengths return zero and effectively drop the character from output. Consumers should be aware that this is a custom APFS-matching normalization path rather than a general-purpose Unicode library.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/Unicode.cpp -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/Unicode.h -->
# File Research: sources/local-fs/apfs-fuse/ApfsLib/Unicode.h

This header declares the Unicode normalization helpers used by APFS filename logic. It exposes per-code-point normalization/folding, canonical reordering, and whole-string normalization/folding.

The public functions are `normalizeOptFoldU32Char()`, `CanonicalReorder()`, and `NormalizeFoldString()`. The whole-string API uses `std::vector<char32_t>` for input/output and a boolean to enable case folding.

This header has no implementation state. The generated lookup data is hidden in `UnicodeTables_v10.h` and included only by `Unicode.cpp`.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/Unicode.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/UnicodeTables_v10.h -->
# File Research: sources/local-fs/apfs-fuse/ApfsLib/UnicodeTables_v10.h

This header is generated/static Unicode normalization and case-folding data for `Unicode.cpp`. It contains no functions, only `static const` lookup arrays.

The file begins with `#include <cstdint>` and defines ten arrays:
`nf_trie_hi[0x300]`, `nf_trie_mid[0x7F0]`, `nf_basic_cf[0x500]`, `nf_u16_inv_masks[0x80]`, `nf_trie_lo[0x1910]`, `nf_u16_seq_2[0x610]`, `nf_u16_seq_3[0x2A0]`, `nf_u16_seq_misc[0xC8]`, `nf_u32_char[0x320]`, and `nf_u32_seq_misc[0x54]`.

The trie arrays encode compact lookup states for Unicode code point normalization. Sentinel values such as `0xFFFF`, `0xAC00`, `0xADxx`, `0xAExx`, and high-nibble classes `0xB` through `0xF` are interpreted by `normalizeOptFoldU32Char()` as invalid entries, Hangul decomposition, combining-class entries, invalid-mask entries, direct mappings, or sequence-table references.

`nf_basic_cf` provides simple case-fold mappings for code points below `0x500`, covering ASCII, Latin, Greek, Cyrillic, and adjacent basic ranges used by the normalization code’s fast case-fold path. Higher code point mappings are represented through the trie and UTF-32 mapping arrays.

`nf_u16_seq_2`, `nf_u16_seq_3`, and `nf_u16_seq_misc` store canonical decomposition sequences made of 16-bit code units, including Latin accent decompositions, Greek decompositions, Hebrew marks, Japanese voiced/semi-voiced kana decompositions, ligatures, and other compatibility/canonical sequences. The miscellaneous table stores length metadata in-band.

`nf_u32_char` and `nf_u32_seq_misc` store mappings requiring 32-bit code points, including supplementary-plane case folds and decompositions. `Unicode.cpp` selects these for table entries whose class requires UTF-32 output.

Because this header is static table data, its correctness is tightly coupled to the decoder logic in `Unicode.cpp`. Manual edits are high risk unless regenerated from the same Unicode/APFS normalization source assumptions.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/UnicodeTables_v10.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/Util.cpp -->
# File Research: sources/local-fs/apfs-fuse/ApfsLib/Util.cpp

This file implements shared APFS utility functions: checksums, block validation, zero checks, hex/debug formatting, UUID/key formatting, UTF-8/UTF-32 helpers, APFS filename hashing/comparison, password input, multiple compression decoders, an integer log2 helper, and debug logging.

Checksum logic includes `Fletcher64()`, used by `VerifyBlock()` to validate APFS object checksums. `VerifyBlock()` rejects all-zero and all-ones checksums, computes Fletcher64 over the block data after the checksum field and then over the checksum field, and expects the final result to be zero. `IsZero()` and `IsEmptyBlock()` provide byte-wise and 64-bit-word zero checks.

Formatting helpers include `DumpHex()`, `DumpBuffer()`, `uuidstr()`, `hexstr()`, `dump_utf8()`, and `dump_utf32()`. These are used by debug paths, dump utilities, crypto diagnostics, and block inspection code.

Filename helpers include `HashFilename()`, `apfs_strncmp()`, and `StrCmpUtf8NormalizedFolded()`. `HashFilename()` converts UTF-8 to UTF-32, normalizes and optionally folds with the APFS Unicode code, computes CRC32C using polynomial `0x1EDC6F41`, and packs the low 22 hash bits with the APFS directory-record name length. `StrCmpUtf8NormalizedFolded()` normalizes both strings and performs lexicographic UTF-32 comparison. `apfs_strncmp()` is a bounded byte comparison for APFS byte strings.

`Utf8toUtf32()` implements a small UTF-8 decoder. It accepts up to four-byte sequences, stops at NUL, and returns false on malformed continuation bytes or invalid leading bytes. It does not enforce all modern UTF-8 validity constraints such as overlong encodings or Unicode scalar range exclusions.

`GetPassword()` reads a password line from stdin. On Linux/macOS it disables terminal echo with `termios`, restores terminal state, and prints a newline. Other platforms read normally.

Compression helpers support APFS compressed file/resource data: zlib (`DecompressZLib()`), Apple Data Compression-style backreferences (`DecompressADC()`), LZVN via lzfse’s decoder state, bzip2, LZFSE, and a custom `DecompressLZBITMAP()` decoder. `DecompressLZBITMAP()` parses a `ZBM` stream with flag `0x09`, handles stored blocks, token maps, RLE-expanded token streams, literal/distance/bitmap sections, and reconstructs output with backreferences.

Logging is controlled by global debug flags from `Global.h`. `log_debug()` prints only when `Dbg_Cmpfs` is enabled, `log_warn()` when `Dbg_Info` is enabled, and `log_error()` when `Dbg_Errors` is enabled. All log to global `g_log`, initialized to stderr.

Notable risks: several decompressors rely on assertions or minimal boundary checks and should not be treated as hardened parsers for hostile input. `DecompressADC()` asserts exact source/output consumption and may read/write past bounds before an assertion in malformed streams. `DecompressLZBITMAP()` has more explicit error checks but still contains assumptions such as flag `0x09` and fixed scratch sizing.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/Util.cpp -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/Util.h -->
# File Research: sources/local-fs/apfs-fuse/ApfsLib/Util.h

This header declares the utility surface implemented in `Util.cpp`. It includes APFS UUID types and standard C++ string/vector/ostream support.

The API covers Fletcher64 checksum calculation, APFS block verification, zero checks, hex dumping, UUID and byte-string formatting, UTF-8/UTF-32 dump helpers, APFS filename hashing, APFS byte-string comparison, normalized/folded UTF-8 comparison, UTF-8 to UTF-32 conversion, six decompression helpers, password input, integer log2, and printf-style logging helpers.

The logging declarations use GCC-style `format(printf)` attributes, which helps catch mismatched format strings on compatible compilers. MSVC compatibility depends on `Endian.h`’s handling of `__attribute__` in translation units where this header is included indirectly.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsLib/Util.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsUtil/ApfsUtil.cpp -->
# File Research: sources/local-fs/apfs-fuse/ApfsUtil/ApfsUtil.cpp

This file implements the `apfsutil` command-line utility. It opens an APFS device or image, optionally detects an APFS GPT partition, initializes an `ApfsContainer`, and prints basic volume information and snapshots.

The utility expects one argument: the device/image path. It sets `g_debug = 0`, opens the device through `Device::OpenDevice()`, defaults the APFS container byte range to the whole device, then attempts GPT detection through `GptPartitionMap`. If GPT validation succeeds, it lists partitions, finds the first APFS partition, and adjusts the offset/size passed to `ApfsContainer`.

After `container->Init()`, the program iterates up to `NX_MAX_FILE_SYSTEMS` and calls `GetVolumeInfo()` for each volume slot. For each present volume it prints volume index, UUID, role, name, case sensitivity derived from incompatible feature bits, consumed capacity in bytes, and a FileVault yes/no string based on APFS crypto flags.

If a volume has a snapshot metadata tree, the utility opens that B-tree at the volume superblock transaction ID, iterates entries from the beginning, filters for `APFS_TYPE_SNAP_METADATA`, and prints snapshot object IDs and names.

The helper `print_role()` maps APFS role bit flags and newer enum-shifted roles to human-readable labels. `print_filevault()` treats flags value `1` as not encrypted and everything else as encrypted.

Limitations: the utility is informational only and does not mount or repair. Partition names and volume names are printed directly with simple formatting. Snapshot iteration assumes the metadata tree is readable and stops when the key type no longer matches snapshot metadata.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/ApfsUtil/ApfsUtil.cpp -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/CMakeLists.txt -->
# File Research: sources/local-fs/apfs-fuse/CMakeLists.txt

This CMake file defines the apfs-fuse build. It requires CMake 3.0, names the project `Apfs`, enables C99 and C++11, sets Release build type, and adds `-Wall -Wextra` to C and C++ flags. It includes the project root and bundled `3rdparty/lzfse/src`.

It declares an option `USE_FUSE3` defaulting ON. For Linux/non-Apple FUSE builds, this chooses between linking `fuse3` and linking `fuse` with `USE_FUSE2` defined.

The build creates three libraries. `lzfse` is built from bundled Apple LZFSE/LZVN C sources. `crypto` is built from local AES, AES-XTS, ASN.1 DER, crypto, DES, SHA-1, SHA-256, and Triple-DES sources. `apfs` is the main library and includes container, directory, node mapping, volume, dumping, B-tree, checkpoint map, CRC32, decompression, device backends, disk image formats, GPT partition map, key management, plist, utility, and Unicode sources.

`apfs` links against `z`, `bz2`, `lzfse`, and `crypto`, and publicly defines `_FILE_OFFSET_BITS=64` and `_DARWIN_USE_64_BIT_INODE`. These definitions are important for large-file support and Darwin inode behavior.

The file defines four executables: `apfs-dump`, `apfs-dump-quick`, `apfs-fuse`, and `apfsutil`. `apfs-fuse` links to OSXFUSE directly on Apple using `/usr/local/lib/libosxfuse.dylib`; otherwise it links to FUSE2 or FUSE3 depending on the option. Install rules install `apfs-fuse` and `apfsutil` into the runtime bindir.

Notable build constraints: dependency discovery is manual rather than using `find_package` for zlib, bzip2, or FUSE. The hard-coded OSXFUSE include/library path may need local adjustment on modern macOS systems.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/CMakeLists.txt -->