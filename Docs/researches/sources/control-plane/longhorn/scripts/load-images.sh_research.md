# sources/control-plane/longhorn/scripts/load-images.sh

## Purpose
Loads a Longhorn image archive if provided, tags listed images into an optional private registry namespace, and pushes them.

## Important APIs and Variables
`list` defaults to `longhorn-images.txt`; `CONTAINER_CLI` defaults to `docker` and can be set to `podman`. Flags are `--registry`, `--image-list`, `--images`, and `--help`.

## Control Flow
The script parses flags, appends a slash to non-empty registry, enables `errexit` and `xtrace`, loads an archive when `--images` is set, then iterates every line of the image list. It normalizes images of forms `a/b/c`, `a/b`, or bare name into `${registry}longhornio/<final-name>`, then tags and pushes.

## State and Persistence
Mutates local container image storage by loading/tagging images and remote registry state by pushing tags. It persists no repo files.

## Dependencies and Integration Points
Depends on Docker or Podman, registry credentials, and an image-list file. Integrates with air-gapped/private registry workflows for Longhorn deployments.

## Risks
Unquoted variables allow breakage with spaces or glob characters in paths. The usage text contains a typo for `--image-list`. The path normalization assumes Longhorn images should be pushed under `longhornio/` regardless of source registry. No retry or digest verification is performed after push.

## Test Signals
Use a temporary local registry and short image list to assert load/tag/push behavior. Validate both Docker and Podman paths when supported, with and without `--images`.
