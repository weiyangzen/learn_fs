## sources/cloud-native/soci-snapshotter/cmd/soci/commands/prefetch/info.go

Purpose: implements `soci prefetch info`, displaying details of a prefetch artifact.

Important APIs/types/functions: `infoCommand` and `prettyPrintJSON`.

Control flow: parse digest, open artifacts DB, verify artifact type is prefetch, fetch artifact bytes from selected content store, unmarshal prefetch artifact, walk DB for metadata, print summary and span ranges, and optionally print raw JSON.

State and persistence: read-only against artifacts DB and content store.

Dependencies and integration: SOCI prefetch artifact unmarshalling, store abstraction, digest parsing, command context.

Risks and test signals: DB walk uses `fmt.Errorf("found")` as a sentinel to stop but ignores the returned error, which is intentional but brittle. No direct tests here.
