# Research: sources/distributed-fs/ipfs-kubo/config/profile.go

Purpose: Defines named config profiles that transform initial or existing Kubo config for common deployment modes and import compatibility modes.

Important APIs/types/functions: `Transformer`, `Profile`, `defaultServerFilters`, `Profiles` map, helpers `getAvailablePort`, `appendSingle`, `deleteEntries`, `mapKeys`, and `applyUnixFSv02015`.

Control flow, state, and persistence: Each profile mutates a `*Config` in memory. Networking profiles add/remove address filters, disable MDNS/NAT port mapping, pick random swarm ports, or restore defaults. Datastore profiles replace `Datastore.Spec` and are marked init-only where needed. Lowpower reduces DHT/relay/connection manager settings. Announce profiles toggle `Provide`. UnixFS profiles pin import defaults for legacy CIDv0 or newer CIDv1 settings. AutoConf profiles set or clear `"auto"` fields and AutoConf enablement.

Dependencies and integration points: Profiles are used by `ipfs init --profile` and config profile commands. They coordinate with init defaults, datastore plugin specs, import config, AutoConf, routing, and provide config.

Risks and test signals: Profile transforms can overwrite operator settings. `randomports` has a TOCTOU race between finding and later binding a free port. `deleteEntries` returns map iteration order, so output order is nondeterministic. Tests in this subset cover AutoConf profile behavior; broader profile coverage is elsewhere.
