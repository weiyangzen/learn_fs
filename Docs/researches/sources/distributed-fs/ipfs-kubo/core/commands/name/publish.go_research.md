# sources/distributed-fs/ipfs-kubo/core/commands/name/publish.go

## Purpose

`name/publish.go` implements `ipfs name publish`, the high-level path that signs and publishes an IPNS record for an IPFS path using a local key. It manages record lifetime, TTL, key selection, V1 compatibility, optional custom sequence number, and offline/delegated publishing modes.

## Important APIs, Types, and Functions

`PublishCmd` uses options for `key`, `resolve`, `lifetime`, `ttl`, `quieter`, `v1compat`, `allow-offline`, `allow-delegated`, `sequence`, and IPNS base formatting. It emits `IpnsEntry`. It relies on `api.Name().Publish`, `api.ResolveNode`, `cmdutils.PathOrCidPath`, `options.Name.*`, and `iface.ErrOffline`.

## Control Flow

The command obtains CoreAPI, validates that `--allow-offline` and `--allow-delegated` are not combined, parses and validates lifetime if explicitly set, then builds publish options for offline/delegated behavior, key name, valid time, and V1 compatibility. TTL is parsed separately: explicit negative TTL is rejected, explicit TTL greater than lifetime is rejected, and default TTL is capped to the chosen lifetime. If provided, a custom sequence option is appended. The target argument is parsed as a path/CID path; when `--resolve` is true, the command resolves the node before publishing. Finally it calls `api.Name().Publish`; `iface.ErrOffline` is replaced with a more actionable error message. Text output prints either only the IPNS name (`--quieter`) or "Published to <name>: <path>".

## State and Persistence Behavior

Publishing signs and stores a new IPNS record through the CoreAPI name system. Depending on flags and node configuration, the record can be stored locally, announced on the DHT, and/or sent to delegated publishers. The command itself does not directly mutate repo config.

## Dependencies and Integration Points

Dependencies include Boxo IPNS defaults, Kubo CoreAPI name/resolve APIs, key encoding options, path utilities, and command encoders. It integrates with keys created by `ipfs key`, IPNS resolution, delegated publisher config, and path availability in the local/network DAG.

## Risks and Test Signals

Risks include TTL/lifetime validation mistakes, sequence regressions, path verification causing network fetches, and user confusion between offline and delegated modes. Tests should cover defaults, explicit lifetime/TTL parsing, TTL cap behavior, invalid negative/too-large values, custom key names and peer IDs, `--resolve=false`, offline error mapping, delegated/offline mutual exclusion, V1 compatibility flag propagation, custom sequence propagation, and quiet output escaping.
