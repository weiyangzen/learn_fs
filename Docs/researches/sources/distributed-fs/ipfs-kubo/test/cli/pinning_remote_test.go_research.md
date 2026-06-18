# sources/distributed-fs/ipfs-kubo/test/cli/pinning_remote_test.go

Purpose: validates Kubo's remote pinning CLI and MFS remote pin policy against an in-memory Remote Pinning API service. It covers service registration, credential hiding, service stats, error handling, add/list/remove operations, status transitions, force semantics, and offline warnings.

Important APIs and helpers: `runPinningService` starts a local HTTP server using `testutils/pinningservice.NewRouter`. Tests use `pin remote service add/ls/rm`, `pin remote add/ls/rm`, `Pinning.RemoteServices.*` config keys, `MFS_PIN_POLL_INTERVAL`, `gjson` for JSON assertions, and `sjson` to mutate config JSON.

Control flow: the MFS policy test enables remote MFS pinning and polls until the service receives the MFS root CID, then changes MFS and expects repinning. Credential tests ensure `config Pinning`, direct API key reads, and `config show` do not expose tokens while `config replace` preserves redacted keys but rejects injected keys. Service-stat tests distinguish valid and invalid endpoints. Remote pinning subtests simulate background status changes by mutating `PinStatus`, blocking `--background=false` until pinned, listing multiple statuses, listing by CID, removing by name with and without `--force`, removing all pins, and warning when adding in offline mode.

State and persistence: service definitions and API keys live in Kubo config. Remote pins live only in the mock service's memory. MFS pinning state is derived from MFS root changes and policy config. Credential secrecy is enforced across config display and replacement.

Dependencies and integration points: integrates Kubo CLI, daemon, config redaction, remote pinning client, MFS flush/stat, local HTTP service, bearer authorization, JSON output, DNS failure handling, and service endpoint validation.

Risks and test signals: timing-sensitive polling depends on short MFS poll intervals and daemon scheduling. The service is intentionally minimal, so failures may indicate client/API contract drift. Strong signals include leaked API keys, missing access-denied errors, force removal safeguards failing, or MFS root not repinning after change.
