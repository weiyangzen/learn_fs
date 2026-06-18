# sources/cloud-native/ostree/src/ostree/ot-builtin-init.c

## Purpose
Implements `ostree init`, creating a new repository with a selected storage mode and optional collection ID.

## Important APIs, Types, And Functions
`ostree_builtin_init()` is the entry point. It uses `ostree_repo_mode_from_string()`, `ostree_repo_set_collection_id()`, and `ostree_repo_create()`. Options are `--mode` and `--collection-id`.

## Control Flow
The command parses options while allowing the shared option layer to construct the target `OstreeRepo`, converts the mode string to an `OstreeRepoMode`, sets the collection ID on the repo object, and creates the repository in that mode. Any invalid mode, collection ID, or filesystem creation error aborts.

## State And Persistence
Successful execution creates the repository directory structure, config, object store layout, and collection ID configuration if supplied. It does not create refs, commits, or summaries.

## Dependencies And Integration Points
The file is a thin CLI wrapper over repo creation APIs. The selected mode affects later commit, checkout, pull, and object storage behavior. The collection ID is consumed by collection refs, summary metadata, commit binding, find-remotes, and create-usb workflows.

## Risks And Edge Cases
The default mode is `bare`, which may not be suitable for unprivileged or archive distribution use. Invalid collection IDs are expected to be rejected by the repo API. Re-running on an existing repo depends on `ostree_repo_create()` semantics outside this file.

## Test Signals
Signals include creation for each supported mode, invalid mode rejection, collection ID persistence in config, opening the created repo, and behavior when the target path already exists or is unwritable.
