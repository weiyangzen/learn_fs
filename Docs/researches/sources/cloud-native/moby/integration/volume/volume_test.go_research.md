# sources/cloud-native/moby/integration/volume/volume_test.go

## Purpose
Tests core volume APIs: create/list metadata, remove conflict and force behavior, removal while Swarm is enabled, inspect timestamp stability, invalid JSON error handling, anonymous-volume prune semantics, and pruning anonymous volumes created from image `VOLUME` declarations.

## Important APIs, Types, And Functions
- `TestVolumesCreateAndList` checks local driver metadata and mountpoint path.
- `TestVolumesRemove` and `TestVolumesRemoveSwarmEnabled` verify in-use conflict, successful removal after container removal, not-found behavior, and force behavior.
- `TestVolumesInspect` confirms `CreatedAt` does not change after touching the `_data` directory.
- `TestVolumesInvalidJSON` sends malformed requests to `/volumes/create`.
- `getPrefixAndSlashFromDaemonPlatform` abstracts Unix/Windows volume target syntax.
- `TestVolumePruneAnonymous` checks new API behavior pruning anonymous volumes by default and all volumes with `All: true`, plus old API v1.41 behavior.
- `TestVolumePruneAnonFromImage` builds an image with `VOLUME`, creates a container, removes it, and verifies prune removes the generated anonymous volume.

## Control Flow
Tests use setup context and API client, create containers/volumes/images, inspect daemon responses, and remove resources. The Swarm-enabled removal case starts a separate daemon and initializes Swarm to verify cluster-volume-related behavior. Invalid JSON tests run endpoint subtests in parallel and inspect HTTP status/body.

## State And Persistence
Creates named volumes, anonymous volumes, containers, daemon-side volume directories, images, and Swarm state. `TestVolumesInspect` mutates `_data` directory atime/mtime to ensure logical creation time is stable.

## Dependencies And Integration Points
Depends on Moby volume API, container helper volume creation, build helper/fakecontext for `VOLUME`, client API version selection, error definitions, and raw request helpers. Integrates with volume store metadata and prune policy compatibility.

## Risks And Edge Cases
Windows case-insensitive names and path prefixes are handled explicitly. Old API behavior is intentionally different from current API, so compatibility assertions must track API-version gates. Timestamp parsing assumes RFC3339 and minute-level tolerance.

## Test Signals
Signals include exact volume metadata, conflict errors while volumes are in use, nil error for forced missing volume removal, stable `CreatedAt`, 400 responses for invalid content type/JSON/trailing content, no 5xx for empty body, expected prune deletion lists, and pruning image-declared anonymous volumes after container removal.
