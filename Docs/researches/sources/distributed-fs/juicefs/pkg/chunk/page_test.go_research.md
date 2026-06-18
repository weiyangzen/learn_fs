## sources/distributed-fs/juicefs/pkg/chunk/page_test.go

Purpose: verifies `Page` refcount/slice behavior and `pageReader` read semantics.

Important tests: `TestPage` exercises `NewOffPage`, slicing, acquire/release interactions, and data availability through dependent pages. `TestPageReader` checks sequential `Read`, random `ReadAt`, EOF behavior, and close/released-page error handling.

State and persistence: in-memory only.

Dependencies and integration points: uses Go testing and `Page` APIs used by cache code.

Risks and test signals: catches basic lifetime and reader contract regressions, but cannot prove absence of all refcount leaks in concurrent cache paths.
