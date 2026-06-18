# sources/distributed-fs/ipfs-kubo/core/commands/pin/remotepin.go

## Purpose

`pin/remotepin.go` implements `ipfs pin remote` and `ipfs pin remote service` commands for interacting with remote pinning services and storing their credentials in repo config.

## Important APIs, Types, and Functions

`remotePinCmd` registers `add`, `ls`, `rm`, and `service`; `remotePinServiceCmd` registers service `add`, `ls`, and `rm`. Key types are `RemotePinOutput`, `ServiceDetails`, `Stat`, `PinCount`, and sortable `PinServicesList`. Helpers include `toRemotePinOutput`, `printRemotePinDetails`, `lsRemote`, `getRemotePinServiceFromRequest`, `getRemotePinService`, `getRemotePinServiceInfo`, and `normalizeEndpoint`.

## Control Flow

`remote add` gets a configured service client, resolves the path/CID locally, validates optional name, adds origin multiaddrs when the block is local and the host is online, warns when offline text output may leave no providers, submits `c.Add`, attempts to connect to returned delegates, and unless `--background` polls request status until pinned or failed. `remote ls` builds filter options for name, CIDs, and statuses, then streams statuses from the remote service. `remote rm` reuses the same listing filters to collect request IDs, rejects multi-delete unless `--force`, and deletes each request. Service `add` opens the repo directly, normalizes the endpoint, rejects duplicates, and stores endpoint/key under `Pinning.RemoteServices`. Service `rm` deletes config entries. Service `ls` reads config, optionally probes each service for queued/pinning/pinned/failed counts concurrently, sorts by service name, and emits text or JSON.

## State and Persistence Behavior

Remote pin requests persist in the external pinning service. Service credentials persist in the local repo config. Listing and stats are read-only apart from network calls. `remote add` can also create transient swarm connections to delegates.

## Dependencies and Integration Points

Dependencies include Boxo remote pinning client, Kubo fsrepo/config/cmdenv/cmdutils, CoreAPI path and swarm APIs, libp2p host/peer address helpers, errgroup, URL/path normalization, and CID encoders. It integrates with local blockstore/provider availability and with repo config lifecycle.

## Risks and Test Signals

Risks include storing service keys in config, direct repo opens while daemon may be active, polling without upper timeout except context, delegate connection failures being logged, bulk remove filter mistakes, and endpoint normalization/security validation. Tests should cover add/list/remove filters, status parsing, duplicate service names, config nil maps, endpoint normalization, `/pins` suffix rejection, query rejection, HTTP/HTTPS-only validation, stat invalid/valid services, offline warnings, background mode, and force behavior for multiple removals.
