# sources/cloud-native/ostree/tests/test-summary-update.sh

## Purpose
This shell test validates summary update behavior, optional summary signing mtime alignment, custom metadata insertion and display, and collection-enabled `ostree-metadata` branch generation.

## Important APIs, Types, And Functions
It uses `ostree summary --update`, `--add-metadata`, `-m`, `summary --view`, `--list-metadata-keys`, `--print-metadata-key`, optional GPG signing arguments, `ostree refs --collections --create`, `ostree show --raw`, and `ostree log`.

## Control Flow
In a normal repo, the script creates five commits, generates plain and signed summaries, compares `summary` and `summary.sig` mtimes when signed, adds metadata values of string, boolean, integer, and empty map types, and verifies metadata view/list/print output. It repeats in a repo with collection ID `org.example.Collection1`, also creating mirror refs in `org.example.Collection2`. It validates the same metadata behavior and checks that `ostree-metadata` exists as a collection ref, has expected raw metadata bindings, has five commits from five summary updates, and contains only the root directory.

## State And Persistence
State includes `summary`, optional `summary.sig`, metadata entries, collection refs, and the `ostree-metadata` branch and commits in collection-enabled repos.

## Dependencies And Integration Points
This integrates summary metadata serialization, GVariant parsing from CLI strings, GPG signing, file mtimes, collection binding metadata, and metadata-branch generation.

## Risks
Metadata type parsing must be exact and stable. Signed summary mtime should match summary mtime for cache consistency. Collection repos must bind metadata commits to the correct collection/ref without adding files.

## Test Signals
Two TAP results cover normal and collection-enabled update flows. Checks include exact metadata strings, mtime equality, raw metadata bindings, commit counts, and root-only file listing.
