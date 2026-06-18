# sources/cloud-native/ostree/src/libostree/ostree-repo-finder-override.h

Purpose: declares the public final `OstreeRepoFinderOverride` type for resolving refs from caller-supplied repository URIs.

Important APIs/types/functions: exposes `OSTREE_TYPE_REPO_FINDER_OVERRIDE`, `G_DECLARE_FINAL_TYPE`, `ostree_repo_finder_override_new`, and `ostree_repo_finder_override_add_uri`.

Control flow: construct the finder, add one or more URIs, then resolve using the base `OstreeRepoFinder` async API. The URI list is mutable through repeated `add_uri` calls before or between resolves.

State and persistence: the header exposes no fields; implementation stores owned URI strings and creates dynamic remotes per resolve. It does not persist remote configuration.

Dependencies/integration: includes GIO/GObject, `ostree-repo-finder.h`, and `ostree-types.h`; exported in libostree symbols for applications that need controlled remote discovery.

Risks: callers must add valid reachable URIs and ensure parent repo keyring configuration can verify any matching collections. The API does not expose removal or clearing of override URIs.

Test signals: should be covered through resolve behavior and pull-from-remotes tests; the header itself only contributes ABI/type coverage.
