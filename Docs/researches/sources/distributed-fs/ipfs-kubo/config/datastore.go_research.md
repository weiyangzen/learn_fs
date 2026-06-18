# Research: sources/distributed-fs/ipfs-kubo/config/datastore.go

Purpose: Defines datastore configuration and default datastore path helper.

Important APIs/types/functions: Constants for default datastore directory, block key cache size, and write-through behavior. `Datastore` stores storage limits, GC period, legacy fields, datastore `Spec`, hash/cache/write-through options. `DataStorePath(configroot)` resolves the default datastore path.

Control flow, state, and persistence: `DataStorePath` delegates to config path resolution. `Datastore.Spec` persists structured datastore plugin configuration; legacy fields remain for compatibility.

Dependencies and integration points: Integrated with fsrepo datastore setup and profiles/default init specs. Uses `encoding/json` for legacy raw params.

Risks and test signals: `Spec map[string]any` is flexible but weakly typed, so errors surface in datastore plugin parsing. Legacy fields can confuse migrations if both old and new fields are present. Default specs are tested indirectly through init/profile behavior.
