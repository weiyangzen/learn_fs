# sources/cloud-native/moby/daemon/server/imagebackend/image.go

## Purpose
Defines image-backend request/response option contracts for pull, push, remove, list, get, inspect, attestations, and inspect data compatibility.

## Important APIs, Types, And Functions
Important structs include `PullOptions`, `PushOptions`, `RemoveOptions`, `ListOptions`, `GetImageOpts`, `ImageInspectOpts`, `AttestationOpts`, and `InspectData`.

## Control Flow
This file contains type definitions only.

## State And Persistence
The structs carry API request parameters and image inspection data. `InspectData` embeds the modern inspect response and includes legacy fields such as `Parent`, `DockerVersion`, `Container`, `ContainerConfig`, and `GraphDriverLegacy` for older API versions.

## Dependencies And Integration Points
Used by image API routers and daemon image service. Depends on Docker API image/container/registry/storage types, daemon filters, HTTP headers, and OCI platform specs.

## Risks And Edge Cases
API-version compatibility is embedded in field comments: some fields are removed or changed in newer API versions but retained for older responses. Attestation options can avoid content-store reads when statements are not requested.

## Test Signals
Image route and inspect tests validate field inclusion/exclusion and option handling.
