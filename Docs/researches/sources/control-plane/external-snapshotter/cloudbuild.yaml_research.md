# sources/control-plane/external-snapshotter/cloudbuild.yaml

## Purpose
Cloud Build pipeline for building external-snapshotter container images.

Source size: 47 lines, 2334 bytes.

## Important APIs, Types, and Functions
- Cloud Build config with 1 steps.

## Control Flow
- Cloud Build executes configured build steps in order using repository source context.
- Steps build command images such as csi-snapshotter, snapshot-controller, and conversion webhook and publish tagged outputs.
- Dockerfiles under `cmd/*` provide per-binary image definitions.

## State and Persistence
- No repository runtime state; build artifacts are container images in the configured registry.
- Build substitutions/tags determine image names and versions.

## Dependencies and Integration Points
- Google Cloud Build, Docker/build tooling, command Dockerfiles, repository Go binaries.

## Risks and Edge Cases
- Tag/substitution drift can publish images under unexpected names.
- Dockerfile or binary path mismatches fail builds late in the pipeline.

## Test Signals
- Successful Cloud Build execution and runnable images are the validation signal.
