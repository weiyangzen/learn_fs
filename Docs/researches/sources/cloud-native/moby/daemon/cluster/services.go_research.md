# Research: sources/cloud-native/moby/daemon/cluster/services.go

## sources/cloud-native/moby/daemon/cluster/services.go

Purpose: implements service list/inspect/create/update/remove/logs and image digest pinning for swarm services.

Important APIs: `GetServices`, `GetService`, `CreateService`, `UpdateService`, `RemoveService`, `ServiceLogs`, `convertSelector`, `imageWithDigestString`, and `digestWarning`. List filters accept name/id/label/mode/runtime and default to container runtime; service status is fetched through a separate `ListServiceStatuses` call. Create/update populate network IDs, convert specs, reject network-attachment runtime for services, validate plugin runtime requirements, carry registry auth, optionally pin image tags to digests by querying registries, and invoke SwarmKit create/update with version and rollback options.

Service logs translate Docker log options to SwarmKit log subscription options, including tail semantics, stream selection, since timestamp conversion, selector resolution by service/task, and conversion back to backend log messages with context attributes. State is remote SwarmKit service/task/log state; registry auth may be preserved from current or previous specs during update.

Dependencies include auth config decoding, registry repositories, swarm API types, convert package, backend log options, errdefs, SwarmKit control/log clients, gRPC size limits, and OpenContainers digest. Risks include slow registry lookup requiring context replacement, warning-only digest pin failures that can lead to nodes pulling different tag contents, registry-auth preservation complexity, log stream blocking/cancellation, and runtime-specific validation gaps. Tests are mostly indirect; this subset does not include direct service tests.
