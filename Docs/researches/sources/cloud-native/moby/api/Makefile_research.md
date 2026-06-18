<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/Makefile -->
# sources/cloud-native/moby/api/Makefile

## Purpose
Provides API-module commands for building the swagger dev image, generating swagger-derived API types, serving rendered API docs, validating `swagger.yaml`, and checking generated output freshness.

## Important APIs, Types, And Functions
- Variables: `DOCKER`, `BUILDX`, `API_DIR`, `PROJECT_PATH`, `DOCKER_MOUNT`, `DOCKER_IMAGE`, `DOCKER_WORKDIR`, `DOCKER_RUN`, `DOCKER_BUILD_ARGS`, and `SWAGGER_DOCS_PORT`.
- Targets: `build`, `swagger-gen`, `swagger-docs`, `validate-swagger`, `validate-swagger-gen`, and `help`.
- `swagger-docs` runs `redocly/redoc:v2.5.1` with `SPEC_URL=swagger/swagger.yaml`.

## Control Flow
`swagger-gen` and validation targets build the dev image first, then run scripts from `api/scripts` inside a container with the API directory mounted into the project path. `swagger-docs` starts a Redoc container serving the current directory on the configured port.

## State And Persistence
Swagger generation mutates files under the mounted API directory. Validation targets should leave the tree unchanged. The docs preview container is ephemeral.

## Dependencies And Integration Points
Called by the root Makefile and GitHub `validate-api-swagger` job. Depends on `api/Dockerfile`, API scripts, Docker Buildx, and Redoc.

## Risks And Edge Cases
Only the API directory is mounted, so scripts needing repository-wide context must work within that constraint. The build arg `SWAGGER_VERSION` does not match the Dockerfile's `GO_SWAGGER_VERSION` arg. Docs preview binds a local port that can conflict with other services.

## Test Signals
Successful `make validate-swagger` and `make validate-swagger-gen` are CI signals. `swagger-gen` should leave generated files matching the swagger spec.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/Makefile -->
