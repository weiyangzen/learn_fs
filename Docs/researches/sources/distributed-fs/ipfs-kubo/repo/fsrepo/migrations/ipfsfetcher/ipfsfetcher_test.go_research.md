# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/ipfsfetcher/ipfsfetcher_test.go

Purpose: tests IPFS-based migration fetching, temporary node initialization, and config parsing.

Important APIs and control flow: setup initializes plugins. `TestIpfsFetcher` and `TestInitIpfsFetcher` are gated by an `EPIC_TEST` style skip helper for heavier network/node behavior. `TestReadIpfsConfig` writes config with bootstrap and peering entries and verifies parsed outputs. Bad bootstrap and peering config tests ensure malformed data does not crash parsing. Helpers create config files and load plugins.

State and persistence: creates temp repos/configs, may start temp Kubo nodes and fetch paths in epic tests, and validates cleanup via fetcher close behavior indirectly.

Dependencies and integration: exercises `NewIpfsFetcher`, `initTempNode`, `readIpfsConfig`, Kubo plugin setup, and migration fetcher interface.

Risks and test signals: regular test runs likely skip the most expensive network/node behavior, so coverage for live IPFS retrieval is conditional. Config parsing is intentionally forgiving and logs errors instead of failing.
