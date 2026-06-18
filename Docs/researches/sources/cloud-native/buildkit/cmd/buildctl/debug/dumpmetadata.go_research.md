# Research: sources/cloud-native/buildkit/cmd/buildctl/debug/dumpmetadata.go

Purpose: implements `buildctl debug dump-metadata`, an offline inspection command for worker `metadata_v2.db` Bolt databases. It intentionally requires the daemon not to be running to avoid concurrent metadata access issues.

Important APIs and flow: `DumpMetadataCommand` accepts `--root`, finds per-worker `metadata_v2.db` files under root subdirectories, prints file headers, opens each database read-only with a timeout, and recursively prints buckets and key/value entries through `dumpBucket`.

State and dependencies: reads persistent BuildKit metadata databases but does not modify them. It depends on app default root paths, filesystem traversal, and bbolt read-only transactions.

Risks and test signals: raw key/value stringification can produce noisy or binary-looking output, and the command assumes the daemon is stopped. There are no direct tests here; operational safety relies on read-only Bolt open and user discipline.
