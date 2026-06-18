<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/utils/src/verity.rs -->
## sources/cloud-native/nydus/utils/src/verity.rs

### Purpose
This module computes SHA-256 Merkle tree layout and digest generation for data integrity verification. It maps digest pages into a file-backed region and produces the root digest used by verity-style verification.

### APIs, Types, and Control Flow
`MerkleTree::new()` currently asserts 4096 byte pages and SHA-256, computes 128 digests per page, and derives `max_levels` by repeatedly rounding data pages up by digests-per-page. Layout helpers return digest algorithm, max levels, pages and entries per level, entry index for a data page, byte base per level, and total digest pages. `VerityGenerator::new()` creates a tree, grows the target file if needed, and maps the digest region with `FileMapState` when there is more than one data page. `initialize()` fills every digest entry with `NON_EXIST_ENTRY_DIGEST`. `set_digest()` validates level, index, and digest size, with a special one-page root case. `generate_level_digests()` hashes lower-level digest pages into upper-level digest entries, and `generate_all_digests()` walks levels then returns the root.

### State, Dependencies, and Integration
State consists of `MerkleTree`, a `Mutex<FileMapState>`, and a cached `root_digest` for zero/one-page trees. It depends on `crate::digest::{Algorithm, RafsDigest, DigestData}`, `div_round_up`, and memory mapping helpers. Persistent effects include resizing and modifying the target verity data file region.

### Risks and Test Signals
Assertions restrict the implementation to SHA-256 and 4 KiB pages. Offset plus total-size overflow is checked, but mapped writes still rely on `FileMapState` safety. Level numbering is subtle: level 1 stores data-page digests, higher levels store digest-page digests, and level 0 is only a query helper. Tests cover layout boundaries from 0/1 pages to `u32::MAX`, invalid set operations, one/two/many entry roots, overflow/error paths, digest algorithm exposure, and initialization.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/utils/src/verity.rs -->
