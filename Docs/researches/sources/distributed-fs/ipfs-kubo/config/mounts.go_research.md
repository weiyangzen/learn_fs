# Research: sources/distributed-fs/ipfs-kubo/config/mounts.go

Purpose: Defines FUSE mount path and metadata persistence configuration.

Important APIs/types/functions: Defaults for `FuseAllowOther`, `StoreMtime`, and `StoreMode`; `Mounts` fields `IPFS`, `IPNS`, `MFS`, `FuseAllowOther`, `StoreMtime`, and `StoreMode`.

Control flow, state, and persistence: No functions. Values are persisted in config and consumed by mount commands/FUSE integration. StoreMtime/StoreMode affect UnixFS metadata and therefore resulting CIDs for writable mounts.

Dependencies and integration points: Init sets `/ipfs`, `/ipns`, and `/mfs`. Uses the shared `Flag` type for optional booleans.

Risks and test signals: Enabling metadata persistence changes content addressing and interoperability expectations. `FuseAllowOther` has local security implications. No direct tests in this subset.
