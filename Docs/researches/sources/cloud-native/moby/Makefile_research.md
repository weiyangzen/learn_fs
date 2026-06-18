<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/Makefile -->
# sources/cloud-native/moby/Makefile

## Purpose
Provides the primary developer and CI command surface for building Moby binaries/images, entering the dev environment, running unit/integration/docker-py tests, validating code, generating files, and delegating Swagger tasks to the API module.

## Important APIs, Types, And Functions
- Variables: `DOCKER`, `BUILDX`, `DOCKER_GITCOMMIT`, validation refs, `DOCKER_ENVS`, `BIND_DIR`, `DOCKER_MOUNT`, cache volumes, `DOCKER_FLAGS`, `DOCKER_IMAGE`, and build/bake commands.
- Targets include `all`, `binary`, `dynbinary`, `cross`, `clean-cache`, `install`, `run`, `build`, `shell`, `dev`, `test`, `test-docker-py`, `test-integration`, `test-integration-flaky`, `test-unit`, `validate`, `validate-generate-files`, `validate-%`, `win`, `swagger-gen`, `swagger-docs`, `generate-files`, and `validate-bind-dir`.
- The `build` target chooses `--target=dev-base` when bind-mounting `.` and `--target=dev` otherwise.

## Control Flow
Most developer commands first build or reuse the Docker dev image, then run repository scripts inside a privileged container with curated env passthrough, bind mounts, cache volumes, and optional TTY/stdin behavior. Build targets call `docker buildx bake`; test/validation targets call `hack/make.sh`, `hack/test/unit`, or `hack/validate/*` inside the dev container. `generate-files` writes BuildKit local output into a temp dir and copies it back.

## State And Persistence
Persistent state includes Docker build cache, named volumes `docker-dev-cache` and `docker-mod-cache`, `bundles`, optional bind-mounted source, and `.git` mount. `generate-files` mutates the working tree. `clean-cache` removes the named volumes.

## Dependencies And Integration Points
Integrates the root Dockerfile, Bake definitions, hack scripts, API Makefile, Docker daemon privileges, CI environment variables, and optional externally supplied Docker CLI path.

## Risks And Edge Cases
The env allowlist intentionally excludes `DOCKER_BUILDTAGS` to avoid shadowing Dockerfile defaults. Privileged container execution is powerful. `BIND_DIR` validation prevents unsafe absolute/parent paths. Interactive/CI TTY handling affects command behavior in automation.

## Test Signals
Successful Make targets and generated `bundles` are the direct signals. CI workflows rely on `make -o build ...` to skip rebuilding when images are already prepared.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/Makefile -->
