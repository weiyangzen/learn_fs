<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-find-remotes.sh -->
# sources/cloud-native/ostree/tests/test-find-remotes.sh

## Purpose
`test-find-remotes.sh` exercises `ostree find-remotes` for collection-aware repositories and GPG-verified file remotes. It verifies discovery, reporting, keyring selection, mirror refs, and optional pulling of found refs.

## Important APIs, Types, And Functions
The script depends on `gpgme`, `ostree_repo_init --collection-id`, signed commits and summaries, `remote add --collection-id --gpg-import`, `pull`, `pull --mirror`, `refs --collections`, `find-remotes --finders=config`, and `find-remotes --pull`.

## Control Flow
It creates two upstream collection repos with different collection IDs and keys, pulls one app and one OS ref into a normal local repo, and mirrors them into a mirror repo where collection refs land under `refs/mirrors`. For both local forms it runs `find-remotes` with one ref, multiple refs, new refs, and missing refs, then repeats the scenarios with `--pull`. Later it updates the OS collection and validates update discovery, and covers mismatched or absent results.

## State And Persistence
Temporary repos include `apps-collection`, `os-collection`, `local`, and `local-mirror`. State is stored in ref files, collection binding metadata, imported trusted keyrings, signed summaries, and checksum scratch files.

## Dependencies And Integration Points
This test integrates remote configuration, collection ID metadata, summary signatures, GPG key import, ref namespaces, and the finder/puller code paths which convert discovered collection refs into local refs.

## Risks And Test Signals
Output assertions are detailed and therefore sensitive to CLI wording, result ordering, and keyring filenames. Passing signals include correct `(collection, ref)` rendering, correct "not found" handling, no false "No results", successful pulls for found refs, and mirror repos preserving collection mirror ref locations.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-find-remotes.sh -->
