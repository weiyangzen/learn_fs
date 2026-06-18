# sources/cloud-native/ostree/tests/repo-finder-mount.c

Purpose: GLib unit/integration test for `OstreeRepoFinderMount`, validating asynchronous repository discovery against mocked GIO volume/mount data.

Important APIs/types/functions: uses `OstreeRepoFinderMount`, `OstreeRepoFinder`, `OstreeCollectionRef`, `OstreeRepoFinderResult`, `GAsyncResult`, and mock helpers from `test-mock-gio.h`. `result_cb()` captures async completion. `main()` configures locale, mock mounts, refs, and event-loop waiting.

Control flow: builds a mock mount environment, calls `ostree_repo_finder_resolve_async()`, spins the main context until completion, finishes the async operation, and asserts returned results match expected mounted repository metadata and priorities.

State/persistence: no persistent repo writes; state is in memory through GObject instances and mock GIO objects. Dependencies include GLib/GIO, libglnx, private OSTree repo-finder headers, and test mock infrastructure.

Integration/risk/test signals: checks the mount finder glue between platform mount discovery and OSTree collection-ref resolution. Risks include async lifetime bugs, mock divergence from real GIO behavior, and private API changes. `g_assert_no_error()` and GLib test exit status are the signals.
