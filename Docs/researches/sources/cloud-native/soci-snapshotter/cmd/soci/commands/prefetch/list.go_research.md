## sources/cloud-native/soci-snapshotter/cmd/soci/commands/prefetch/list.go

Purpose: implements `soci prefetch list`, listing prefetch artifacts and span counts.

Important APIs/types/functions: `listCommand`, local `prefetchInfo`, `addPrefetchInfo`, and `getDuration`.

Control flow: open command context, artifacts DB, and content store; walk DB entries of prefetch type; parse digest and fetch/unmarshal each artifact when possible to compute total spans; then print JSON or tabular output.

State and persistence: read-only against artifacts DB and content store.

Dependencies and integration: SOCI artifact DB, store fetch, prefetch artifact schema, tabwriter/JSON encoder.

Risks and test signals: malformed or missing artifacts are still listed with `N/A`, which is user-friendly but can hide store/DB drift unless JSON is inspected. No direct tests here.
