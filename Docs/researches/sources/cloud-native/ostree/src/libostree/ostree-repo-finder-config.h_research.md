# sources/cloud-native/ostree/src/libostree/ostree-repo-finder-config.h

Purpose: declares the public final `OstreeRepoFinderConfig` type, the finder backend that resolves refs using locally configured remotes.

Important APIs/types/functions: exposes `OSTREE_TYPE_REPO_FINDER_CONFIG`, `G_DECLARE_FINAL_TYPE`, and `ostree_repo_finder_config_new`. All resolution methods are used through the base `OstreeRepoFinder` interface.

Control flow: callers instantiate the type and pass it to `ostree_repo_finder_resolve_async` or `ostree_repo_finder_resolve_all_async`. The header has no custom properties or lifecycle calls.

State and persistence: no public state. Implementation is stateless beyond the `GObject` instance and reads parent repository configuration on each resolve.

Dependencies/integration: includes GLib/GIO/GObject, `ostree-repo-finder.h`, and `ostree-types.h`; exported in libostree symbols and used by default pull remote discovery.

Risks: the compact API leaves all behavior to implementation docs; callers must supply a parent repo with configured remotes and valid collection refs.

Test signals: API construction and behavior are covered by `tests/test-repo-finder-config.c`.
