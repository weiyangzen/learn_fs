<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/sandbox_store.go -->
## sources/cloud-native/moby/daemon/libnetwork/sandbox_store.go

Purpose: datastore serialization, update, delete, and restore for sandboxes.

Important APIs/types/functions: `epState`, `sbState`, datastore methods (`Key`, `KeyPrefix`, `Value`, `SetValue`, `Index`, `SetIndex`, `Exists`, `Skip`, `New`, `CopyTo`), `Sandbox.storeUpdate`, `storeDelete`, and `Controller.sandboxRestore`.

Control flow: `storeUpdate` rebuilds endpoint references from current sandbox memory, skips non-persistent endpoints, and retries on `datastore.ErrKeyModified`. Restore lists stored sandboxes, creates a `Sandbox` object, applies active sandbox options if present, recreates/opens OSL sandbox with `osl.NewSandbox`, restores endpoints from network/endpoint stores, deletes stale inactive sandboxes, restores OSL interfaces/routes/gateways for active sandboxes, and re-adds service records when appropriate.

State and persistence: persists sandbox ID, container ID, endpoint IDs/network IDs, endpoint priority, and external DNS as `ExtDNS2`. `dbIndex`/`dbExists` maintain optimistic store state.

Dependencies and integration points: controller store, OSL, endpoint/network stores, swarm scope logic, live restore.

Risks and test signals: restore must tolerate missing networks/endpoints and avoid destructive cleanup for active live-restore containers. Tests are mostly broader store/live-restore tests outside this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/sandbox_store.go -->
