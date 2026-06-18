# sources/cloud-native/moby/client/service_create_test.go

## Purpose
Tests the Docker API client service-create path, including daemon errors, transport failures, successful response decoding, platform selection, and digest-pinning behavior.

## APIs, Types, And Functions
The file defines `TestServiceCreateError`, `TestServiceCreateConnectionError`, `TestServiceCreate`, `TestServiceCreateCompatiblePlatforms`, and `TestServiceCreateDigestPinning`. It exercises `Client.ServiceCreate` with `swarm.ServiceSpec`, registry auth options, `registrytypes.DistributionInspect`, OCI platform descriptors, and digest references.

## Control Flow, State, And Integration
Tests create mock HTTP clients, assert `POST /services/create`, optionally mock `GET /distribution/...`, encode JSON responses, and compare returned service IDs and warning lists. State is only test-local HTTP request/response data, but it models the daemon API contract and registry distribution resolution step.

## Risks And Test Signals
Important signals are correct errdefs propagation, connection error handling, JSON request shape, compatible-platform query behavior, and digest pinning when an image tag resolves to a content digest. Regressions would affect swarm service creation and image resolution in client callers.
