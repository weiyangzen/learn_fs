# sources/cloud-native/ostree/src/libostree/ostree-repo-finder-override.c

Purpose: implements a user/test override `OstreeRepoFinder` that searches an explicit list of repository URIs instead of configured remotes or discovery mechanisms.

Important APIs/types/functions: final `OstreeRepoFinderOverride`, `ostree_repo_finder_override_new`, `ostree_repo_finder_override_add_uri`, `ostree_repo_finder_override_resolve_async/finish`, `repo_remote_list_collection_refs`, and `uri_and_keyring_to_name`.

Control flow: callers append override URIs. On resolve, each URI is temporarily represented as an `OstreeRemote` so `ostree_repo_remote_list_collection_refs` can fetch/list its collection refs. For every requested ref advertised by that URI, the code resolves a local keyring remote for the ref's collection, creates a dynamic remote named from URI plus keyring, enables GPG verification, disables summary GPG verification, groups refs per remote, and emits priority `20` results.

State and persistence: the object owns an array of URI strings. During listing, it may temporarily add a remote to the parent repo and removes it afterwards if it did not already exist. Results are transient dynamic remotes.

Dependencies/integration: depends on remote add/remove/list helpers, collection keyring resolution, dynamic remote construction, and the shared finder interface. Intended for user overrides and tests; production code is expected to prefer configured remotes.

Risks: results are only returned when a keyring can be resolved for the collection, preventing unverifiable override pulls. Dynamic name generation has the same escaped URI/keyring separator caveat as other finders. URI listing errors are logged and skipped per URI, so one bad override does not fail the entire resolve. Summary timestamps are unknown and left as zero.

Test signals: used by find-remotes/pull code paths; direct dedicated tests are less visible than config finder tests. Behavior should be validated with explicit override URI tests, missing keyring cases, and duplicate URI/keyring grouping.
