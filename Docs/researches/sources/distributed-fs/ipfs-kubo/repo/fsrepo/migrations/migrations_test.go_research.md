# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/migrations_test.go

Purpose: validates migration orchestration helpers and legacy migration fetcher configuration.

Important APIs and control flow: tests cover forward and reverse `findMigrations`, fake executable discovery, concurrent `fetchMigrations` logging/output, `RunMigration` downgrade denial and reverse execution failure shape, `ReadMigrationConfig` defaults and errors, and `GetMigrationFetcher` behavior for bad schemes, HTTP sources, HTTPS alias expansion, rejected IPFS sources, nil/empty sources, and mixed sources.

State and persistence: creates fake binaries, temp repos/configs, version files, and uses the CAR-backed test gateway.

Dependencies and integration: exercises `ExeName`, `migrationName`, `FetchBinary`, config defaults, and fetcher constructors.

Risks and test signals: strong coverage for source parsing and migration step discovery. It does not fully execute successful external migrations because fake binaries are empty, and does not cover `RunHybridMigrations` matrix directly.
