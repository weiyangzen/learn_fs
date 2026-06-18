<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/.github/workflows/test.yml -->
# sources/cloud-native/moby/.github/workflows/test.yml

## Purpose
Top-level Linux test workflow. It builds reusable dev images, invokes reusable integration and unit workflows for selected architectures/storage backends, runs validation scripts, validates API swagger, and runs cross-platform binary smoke tests.

## Important APIs, Types, And Functions
- Jobs: `validate-dco`, `build-dev`, `test`, `test-unit`, `validate-prepare`, `validate`, `validate-api-swagger`, `smoke-prepare`, and `smoke`.
- `build-dev` matrix covers amd64/arm64 and normal/systemd/firewalld modes.
- `test` delegates to `.test.yml` for amd64 snapshotter, amd64 graphdriver, and arm64 snapshotter.
- `test-unit` delegates to `.test-unit.yml`.
- Validation matrix derives scripts from `hack/validate`, excluding `all`, `default`, and `dco`, then adds `generate-files`.

## Control Flow
DCO runs first. Dev images are built and cached by architecture/mode. Reusable test workflows consume those caches. Validation restores the amd64 dev image, loads it into Docker, and runs `make -o build validate-<script>`. API swagger validation runs in the `api` directory. Smoke tests derive platforms from Bake `binary-smoketest` and run with QEMU/buildx.

## State And Persistence
Dev image tarballs are stored in GHA cache keyed by run id. Test reports and coverage are persisted by reusable workflows. Validation and smoke outputs are temporary.

## Dependencies And Integration Points
Coordinates the root Dockerfile, Makefile, `api/Makefile`, reusable workflows, setup-runner action, Docker Buildx/Bake, and hack validation scripts.

## Risks And Edge Cases
Large matrix cost and cache coupling are the main risks. `validate` depends on the amd64 normal dev image cache; cache miss fails intentionally. Validate-only PRs skip heavy test and smoke jobs but still run validation.

## Test Signals
Signals include successful dev image builds, delegated reusable workflow results, validation script pass/fail, swagger validation, smoke target completion, and artifact/coverage outputs from child workflows.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/.github/workflows/test.yml -->
