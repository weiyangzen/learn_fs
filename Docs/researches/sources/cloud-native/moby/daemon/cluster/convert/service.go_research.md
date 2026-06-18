# sources/cloud-native/moby/daemon/cluster/convert/service.go

## Purpose
Converts Docker service specs, services, task specs, resources, update policies, runtimes, modes, and supporting structures between Docker API and swarmkit gRPC representations.

## Important APIs, Types, And Functions
Exports `ErrUnsupportedRuntime`, `ErrMismatchedRuntime`, `ServiceFromGRPC`, `ServiceSpecToGRPC`, `GenericResourcesFromGRPC`, and `GenericResourcesToGRPC`. Internal helpers include `serviceSpecFromGRPC`, `resourcesFromGRPC`, `resourcesToGRPC`, restart/update/placement/driver converters, `networkAttachmentSpecFromGRPC`, and `taskSpecFromGRPC`.

## Control Flow
Inbound service conversion translates current/previous specs, endpoint, metadata, job status, and update status. Spec conversion handles container, plugin generic runtime, and rejects unknown generic runtime. Outbound conversion defaults unnamed services, validates runtime/spec consistency, forces plugin services to global, serializes plugin specs into protobuf `Any`, validates update/restart/mode combinations, defaults replicated and job values, and rejects unsupported network attachment runtime creation.

## State And Persistence
No local state. It defines how API service specs are persisted in swarmkit's raft store, including plugin runtime payloads and the legacy PidsLimit-in-container workaround.

## Dependencies And Integration Points
Central to service create/update/list/inspect and task conversion. Depends on container conversion, network conversion, runtime plugin proto helpers, names generator, genericresource helpers, and swarmkit enums.

## Risks And Test Signals
Outbound validation is strict for runtime mismatch, memory swap without memory limit, update enum values, endpoint modes, and multiple service modes. Inbound conversion remains compatible with deprecated `ServiceSpec.Networks`. `service_test.go` covers runtime, isolation, credential specs, config targets, network attachment task conversion, and volume subpath.
