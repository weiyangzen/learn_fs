# Research: sources/distributed-fs/ipfs-kubo/config/migration_test.go

Purpose: Tests JSON decoding of migration configuration.

Important APIs/types/functions: `TestMigrationDecode` decodes `{"Migration":{"DownloadSources":["HTTPS"],"Keep":"cache"}}` into `Config`.

Control flow, state, and persistence: In-memory JSON decode only.

Dependencies and integration points: Exercises top-level config decoding for deprecated migration fields.

Risks and test signals: It only covers one valid legacy example; it does not validate deprecation behavior or modern ignored semantics.
