## sources/distributed-fs/ipfs-kubo/test/sharness/t0070-user-config.sh

Purpose: ensures `ipfs init` bootstrap defaults do not overwrite user-provided top-level config keys.

Important APIs and helpers: uses `test_init_ipfs`, `ipfs config Datastore.StorageMax`, `ipfs init`, and `test_cmp`.

Control flow and state: initializes a repo, sets `Datastore.StorageMax` to `42GB`, re-runs `ipfs init`, and confirms the setting remains `42GB`. The persistent state under test is the repo config JSON.

Dependencies and integration points: covers config bootstrap behavior, idempotent init, and preservation of user-edited top-level configuration.

Risks and test signals: catches accidental reapplication of defaults over existing config, which could corrupt storage limits or other user intent. The pass signal is exact equality between the configured value after reinit and the expected user value.
