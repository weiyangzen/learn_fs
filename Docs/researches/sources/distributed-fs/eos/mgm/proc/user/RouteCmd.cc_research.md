# sources/distributed-fs/eos/mgm/proc/user/RouteCmd.cc

Purpose: implements protobuf-backed route table management for path-based redirection endpoints.

Important APIs and types: dispatches `RouteProto` subcommands to `ListSubcmd`, `LinkSubcmd`, and `UnlinkSubcmd`; uses `RouteEndpoint`, `gOFS->mRouting`, and `mConfigEngine` `SetConfigValue`/`DeleteConfigValue`.

Control flow: `ProcessRequest()` switches on the route subcommand. `list` calls `mRouting->GetListing` and returns ENOENT on no match. `link` requires root or admin UID/GID, converts each endpoint proto to `RouteEndpoint`, adds it to routing for the path, and persists the string endpoint representation. `unlink` requires root/admin, removes routing for the path, and deletes persistent config.

State and persistence: `link` and `unlink` mutate in-memory routing and persistent `route` config entries. Listing is read-only.

Dependencies and integration: integrates console route protobufs with the MGM path-routing subsystem and config engine.

Risks: multiple endpoints for one path call `SetConfigValue` with the same key repeatedly, so persistence semantics depend on config engine support for repeated values or overwrite behavior. Success replies are mostly empty. Tests should cover authorization, list no-match, duplicate endpoint add, multiple endpoint persistence, unlink missing path, and config rollback expectations when add/remove partially fails.
