# sources/cloud-native/moby/integration-cli/docker_api_inspect_test.go

## Purpose
Integration tests for inspect API response shape for containers, volumes, images, and older bridge network settings.

## Important APIs and Types
Defines `TestInspectAPIContainerResponse`, `TestInspectAPIContainerVolumeDriver`, `TestInspectAPIImageResponse`, and `TestInspectAPIBridgeNetworkSettings121`.

## Control Flow, State, and Persistence
Tests create containers/images/volumes as needed, call inspect endpoints through the API, decode responses, and verify key fields such as container JSON content, mounted volume driver reporting, image inspect structure, and API-version-specific bridge network fields.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on Docker API version negotiation, daemon inspect serializers, volume metadata, and test CLI helpers. Risks include response schema regressions, omitted fields for backward compatibility, and platform-specific inspect output. These tests signal inspect contract stability.
