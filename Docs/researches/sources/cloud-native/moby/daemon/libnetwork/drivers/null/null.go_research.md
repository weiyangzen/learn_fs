# sources/cloud-native/moby/daemon/libnetwork/drivers/null/null.go

Purpose: Implements Docker's built-in `null` network driver as a local single-instance, no-connectivity driver.

Important APIs and types: `NetworkType` is `null`. `driver` stores a single network id under a mutex. `Register` registers local data scope. `CreateNetwork` allows exactly one network. `DeleteNetwork` always returns forbidden. Endpoint create/delete, join/leave, and operational info are no-ops or empty maps. `Type` and `IsBuiltIn` identify the driver.

Control flow: matches host driver except no explicit connectivity scope is registered. Deletion is always prohibited.

State and persistence: in-memory `network` string only.

Dependencies and integration points: integrates with libnetwork driver registration and typed forbidden errors.

Risks: intentionally no endpoint-level behavior; correctness depends on higher layers using the null network as non-connective.

Test signals: `null_test.go` covers type, single-instance create, and deletion rejection.
