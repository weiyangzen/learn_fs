# File Research: sources/block-storage/thin-provisioning-tools/src/thin/metadata_repair.rs

This file contains superblock/root repair logic. It scans metadata blocks, infers plausible mapping and details roots, validates compatibility, and rebuilds usable superblock state when the on-disk superblock is corrupt or inconsistent.

Key elements:
- `SuperblockOverrides` lets callers override transaction ID, data block size, and number of data blocks.
- `devices_identical()` checks that mapping top-level and details trees have identical thin IDs.
- `lower_bound()` and `upper_bound()` support finding details-root candidates by mapping count.
- `DevInfo`, `MappingsInfo`, and `DetailsInfo` summarize candidate btree subtrees.
- `NodeCollector` scans every metadata block:
  - verifies node blocks
  - classifies value sizes as top-level/mapping/details candidates
  - recursively gathers subtree summaries
  - tracks examined and referenced blocks
  - separates unreferenced roots into mapping-device and details candidates
- `compare_time_counts()` ranks mapping roots by newest mapping times and counts.
- `find_root_pairs()` pairs mapping and details candidates with matching device counts/mapping counts and identical device ID sets.
- `to_found_roots()` creates full on-disk root candidates.
- `to_partial_found_roots()` handles the case where mapping trees exist but details trees are missing by constructing in-core device details.
- `find_roots()` drives scanning and candidate pairing.
- `is_superblock_consistent()` checks normal superblock mapping/details root consistency.
- `is_superblock_consistent_()` checks whether an existing superblock matches found roots.
- `rebuild_superblock()` constructs either an on-disk or in-core `ThinSuperblock`, selecting data block size, transaction ID, data block count, and time from overrides, reference superblock, and inferred roots.
- `Override for Superblock` applies user overrides conservatively.
- `read_or_rebuild_superblock()` first tries the on-disk superblock, then falls back to rebuilt state.

Interactions:
- Used by `thin/dump.rs` repair mode and `thin/repair.rs`.
- Uses btree key-set/map helpers, `DeviceDetail`, `BlockTime`, `SMRoot`, and superblock pack/unpack helpers.

Risks and notes:
- Root recovery is heuristic when details trees are missing; in-core rebuilt details assume all devices are shared snapshots for data safety.
- `NodeCollector::collect_infos()` scans every block, which is expensive but appropriate for repair.
- Candidate selection uses `found_roots[0]` when rebuilding; logging exposes candidates for diagnosis, but automatic choice can matter.
- Overrides never shrink inferred transaction/data block counts below recovered values.
