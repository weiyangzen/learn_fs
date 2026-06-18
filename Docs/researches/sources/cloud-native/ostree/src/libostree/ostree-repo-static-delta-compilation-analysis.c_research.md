# sources/cloud-native/ostree/src/libostree/ostree-repo-static-delta-compilation-analysis.c

## Purpose

This file analyzes two commits to find regular-file content objects that are likely good static-delta candidates. It builds size/name indexes over commit contents and returns a map from newly reachable target checksums to similar source checksums, which the delta compiler can use for rollsum or bsdiff optimization.

## Important APIs, Types, and Functions

- `OstreeDeltaContentSizeNames` stores a content checksum, file size, and all observed basenames for that content object.
- `_ostree_delta_content_sizenames_free()` releases the checksum string and basename array.
- `build_content_sizenames_recurse()` walks a commit dirtree recursively through `OstreeRepoCommitTraverseIter`.
- `build_content_sizenames_filtered()` creates a sorted array of size/name records, optionally restricted to an include-only checksum set.
- `string_array_nonempty_intersection()` checks exact or fuzzy basename overlap.
- `sizename_is_delta_candidate()` filters out empty content and known compressed file extensions such as `xz` and `bz2`.
- `_ostree_delta_compute_similar_objects()` is the exported internal analysis entry point.

## Control Flow

The analysis builds a complete source-side sorted size list from the `from_commit` and a target-side sorted size list from `to_commit`, filtered to newly reachable regular-file content. Traversal visits files, loads `GFileInfo`, keeps only regular files, and records every basename that points to a given checksum. Directory entries load dirtree variants and recurse.

Candidate selection then iterates target records sorted by size. For each target it computes a size window from the supplied similarity percentage, advances a lower bound in the source array because both arrays are sorted, skips source and target records that are unsuitable for delta compression, and checks basename overlap. It tries exact name matching first and fuzzy matching second, where fuzzy mode compares the portion before the first dot when both names have extensions. The first match becomes the only candidate for that target checksum.

## State and Persistence Behavior

This code does not write persistent repository state. It loads commit, dirtree, and file metadata objects from the repository and constructs temporary in-memory `GHashTable` and `GPtrArray` indexes. The output map owns duplicated checksum strings and is consumed by static delta compilation.

## Dependencies and Integration Points

It depends on commit traversal from `ostree-repo-traverse.c`, object loading through `ostree_repo_load_file()` and `ostree_repo_load_variant()`, and the private static delta header for the `OstreeDeltaContentSizeNames` type. Its output feeds `generate_delta_lowlatency()` in the static delta compiler, which attempts rollsum or bsdiff only for entries returned here.

## Risks and Edge Cases

The comparator returns `sn_a->size - sn_b->size` as an `int`, which is compact but worth watching for very large size differences. Candidate choice is intentionally heuristic and single-match; a poor first match can prevent a better delta base from being considered. Empty files and pre-compressed extensions are filtered out. Fuzzy basename matching can match related library names but may also overmatch unrelated files with shared prefixes.

## Test Signals

Tests should cover duplicate content with multiple basenames, include-only filtering, nested directory recursion, exact and fuzzy name matches, size threshold boundaries, excluded compressed extensions, zero-length files, and the no-match path. Integration tests can compare generated deltas with and without analysis to confirm rollsum/bsdiff candidate counts.
