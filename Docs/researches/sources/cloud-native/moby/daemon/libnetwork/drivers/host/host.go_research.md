# sources/cloud-native/moby/daemon/libnetwork/drivers/host/host.go

Purpose: Implements Docker's built-in `host` network driver as a local, single-instance, mostly no-op driver that attaches containers to host networking semantics managed elsewhere.

Important APIs and types: `NetworkType` is `host`. `driver` stores the single network id under a mutex. `Register` registers local data and connectivity scope. `CreateNetwork` permits exactly one network and stores its id. `DeleteNetwork` always returns a forbidden error. Endpoint, join, leave, and operational-info methods are no-ops or empty maps. `Type` and `IsBuiltIn` identify the driver.

Control flow: the only guarded state transition is `CreateNetwork`, which rejects a second instance. Deletion is prohibited regardless of id.

State and persistence: in-memory `network` string only; no datastore persistence.

Dependencies and integration points: implements `driverapi.Driver`, integrates with libnetwork registration and `types.ForbiddenErrorf`/errdefs permission mapping.

Risks: by design there is no endpoint-level validation or cleanup. The single-instance guard is process-local and depends on daemon initialization creating the host network once.

Test signals: `host_test.go` covers type, first create, second-create rejection, and deletion rejection.
