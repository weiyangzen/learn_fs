# sources/cloud-native/ostree/tests/test-remote-add-collections.sh

## Purpose
This focused test verifies that `ostree remote add --collection-id` persists the remote collection ID in repository configuration.

## Important APIs, Types, And Functions
It uses `ostree_repo_init`, `ostree remote add`, `--collection-id`, `--gpg-import`, and `assert_file_has_content` against `repo/config`.

## Control Flow
The script creates an empty repo, adds `some-remote` with URL, collection ID `example-id`, and a GPG import key, then checks the config contains `collection-id=example-id`.

## State And Persistence
The primary persistent state is the remote stanza in `repo/config`, plus any trusted keyring state created by `--gpg-import`.

## Dependencies And Integration Points
This integrates remote configuration writing, option parsing, collection ID persistence, and GPG key import during remote add.

## Risks
A regression could silently drop collection IDs or write them under the wrong stanza, which would break collection-aware pulls and repo-finder behavior.

## Test Signals
The single TAP line `ok remote-add-collections` is emitted after matching the config line.
