<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-checkout.c -->
# sources/cloud-native/ostree/src/ostree/ot-builtin-checkout.c

## Purpose
Implements `ostree checkout`, materializing a commit or subpath into a filesystem tree, with modes for union checkout, whiteouts, SELinux labeling, hardlink/copy policy, composefs output, skip lists, and batch checkout input.

## Important APIs and Types
Exports `ostree_builtin_checkout`. Helpers include `parse_fsync_cb`, `handle_skiplist_line`, `checkout_filter`, `process_one_checkout`, and `process_many_checkouts`. Options configure user mode, cache, subpath, union modes, whiteout processing, allow-noent, stdin/file batch input, fsync policy, hardlink/copy behavior, bareuseronly dirs, skip-list, SELinux policy/prefix, and composefs/composefs-noverity.

## Control Flow
The command parses repo context and fsync policy, then either processes many null-delimited checkout records from stdin/file or resolves a single commit and destination. `process_one_checkout` chooses composefs if requested, otherwise uses the newer `ostree_repo_checkout_at` path when advanced options are set, or the older `ostree_repo_checkout_tree` path for coverage when simple options suffice. It validates incompatible modes, loads SELinux policy, builds optional skip-list filter, sets checkout flags, and executes checkout.

## State and Persistence
Writes the destination filesystem tree or composefs blob. It may update/use repo uncompressed object cache unless disabled, set xattrs/labels, create whiteout devices, hardlink/reflink/copy files, and alter fsync behavior on the repo.

## Dependencies and Integration Points
Uses repository checkout APIs, GIO input streams, Unix stdin streams, SELinux policy APIs, libglnx parsing helpers, and OSTree file abstractions. It is a major bridge from content-addressed commits to mutable filesystems.

## Risks
Option interaction is broad: union modes are mutually exclusive, union-identical requires hardlinks, SELinux prefix requires policy, composefs rejects many checkout options, and require-hardlinks conflicts with force-copy. Batch input is null-delimited and easy for callers to format incorrectly. Checkout affects real filesystem paths and can overwrite data depending on mode.

## Test Signals
Tests should cover simple checkout, subpath, allow-noent, each union mode and conflicts, whiteouts and passthrough whiteouts, hardlink/copy/fallback modes, zero-size copy, bareuseronly dirs, skip-list filtering, SELinux labeling/prefix, composefs and noverity options, fsync parsing, and batch stdin/file checkouts.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-checkout.c -->
