# Research: sources/cloud-native/moby/daemon/cluster/secrets.go

## sources/cloud-native/moby/daemon/cluster/secrets.go

Purpose: implements swarm secret CRUD operations for the daemon swarm backend.

Important APIs: `GetSecret`, `GetSecrets`, `CreateSecret`, `RemoveSecret`, and `UpdateSecret`. Control flow resolves secrets through `getSecret`, validates list filters through `newListSecretsFilters`, lists via SwarmKit with a large receive limit, converts secret specs and objects through `convert`, and sends versioned update/remove/create requests to the SwarmKit control client.

State is SwarmKit manager store state. Dependencies include Engine swarm API types, cluster convert package, daemon swarm backend option types, SwarmKit control client, and gRPC receive-size settings. Risks include manager lock/availability requirements, ambiguous name/prefix lookup, update version conflicts, and limited direct validation in this file. Tests in `filters_test.go` cover accepted filter keys; CRUD behavior is integration-tested elsewhere.
