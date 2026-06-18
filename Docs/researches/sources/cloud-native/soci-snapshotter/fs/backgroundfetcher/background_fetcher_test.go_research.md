# sources/cloud-native/soci-snapshotter/fs/backgroundfetcher/background_fetcher_test.go

Purpose: tests the background fetcher pause path and end-to-end span warming behavior using real ztoc/span-manager objects and an in-memory counting cache.

Important APIs and flow: `withPauser` injects a mock pauser. `countingPauser` records pause invocations. `TestBackgroundFetcherPause` starts `Run`, calls `Pause`, waits briefly, and asserts exactly one pause call. `TestBackgroundFetcherRun` builds one or two gzip tar ztoc readers with large random files, wraps each span manager with `NewSequentialResolver`, starts a fetcher with `WithFetchPeriod(0)`, adds the resolvers, waits, then checks that the cache saw one add per span and byte count equal to compressed archive size minus the gzip header.

State and persistence: tests are in-memory except for helper-created ztoc/tar readers. `countingCache` records write calls and bytes under a mutex. No remote registry, filesystem mount, or Prometheus registry is required.

Dependencies and integration: uses `ztoc.BuildZtocReader`, `spanmanager.New`, `cache.BlobCache` interfaces, random testutil tar entries, and OpenContainers digest. It exercises the real resolver/span-manager cache path rather than a fake resolver for the main run test.

Risks and test signals: good signal that the fetch loop requeues until `ErrExceedMaxSpan` and populates all spans. The tests use sleeps (`10ms`, `1s`, `3s`), so slow CI or scheduling changes can make them flaky. They do not assert `Close` behavior under a full queue or that metric emission stops cleanly.
