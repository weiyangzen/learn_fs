# sources/cloud-native/ostree/src/libostree/ostree-repo-finder-config.c

Purpose: implements the configured-remote `OstreeRepoFinder` backend, resolving collection refs against remotes already configured in a parent repository.

Important APIs/types/functions: defines final `OstreeRepoFinderConfig`, implements `resolve_async` and `resolve_finish`, and exports `ostree_repo_finder_config_new`. The main routine is `ostree_repo_finder_config_resolve_async`; `results_compare_cb` sorts with `ostree_repo_finder_result_compare`.

Control flow: resolution lists all remotes in `parent_repo`, skips remotes without a valid `collection-id`, loads each remote's collection refs, intersects them with the requested refs, and accumulates a `remote_name -> ref/checksum map`. It then looks up each inherited `OstreeRemote` and emits `OstreeRepoFinderResult` objects with priority `100` and no summary timestamp.

State and persistence: the object carries no persistent fields. It reads repository configuration, remote refs, and inherited remote definitions but does not mutate repository state. Result maps borrow requested ref keys and duplicate checksum values.

Dependencies/integration: depends on remote configuration helpers, `ostree_repo_remote_list`, `ostree_repo_remote_list_collection_refs`, collection/ref validation, inherited remote lookup, and the shared finder result type. `ostree-repo-pull.c` creates this backend for the default `config` finder.

Risks: stale or incorrect configured remote refs are trusted at this stage; later pull/find-remotes code must verify summaries and commit availability. Remotes lacking `collection-id` are ignored by design. Errors loading one remote are logged and skipped, so a partially broken configuration can silently reduce result quality.

Test signals: `tests/test-repo-finder-config.c` covers initialization, empty configs, mixed valid/invalid configs, and integration through `ostree_repo_find_remotes_async`.
