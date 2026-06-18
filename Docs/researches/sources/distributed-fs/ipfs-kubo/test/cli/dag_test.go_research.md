# sources/distributed-fs/ipfs-kubo/test/cli/dag_test.go

Purpose: broad integration coverage for DAG stats, CARv2 imports, fast-provide behavior, and partial CAR local-only import/export semantics.

Important APIs/types/functions: `DagStat`, `Data`, `TestDag`, `TestDagImportCARv2`, `TestDagImportFastProvide`, helpers `dagRefs`, `countCARBlocks`, `makePartialDAG`, and local-only tests.

Control flow: fixture CARs are imported, `dag stat` JSON/text outputs are validated for dedup/shared sizes, CARv2 import through stdin is checked, fast-provide config/flag combinations assert daemon log messages and expected DHT failure propagation, and partial DAG helpers remove blocks to test `dag export --local-only` and `dag import --local-only` flag implications/conflicts.

State/persistence: fixture CAR files, temporary exported CARs, daemon stderr logs, block removal, pin removal, and fresh import nodes for block counts.

Dependencies/integration: DAG traversal/stats, CAR reader/importer, pinning, provider subsystem, config `Import.FastProvide*`, DHT availability, and CLI flag validation.

Risks/test signals: high behavioral value. Log-message assertions and DHT failure text are brittle; local-only tests pin DAG shape with chunker/max-links to reduce importer-default coupling.
