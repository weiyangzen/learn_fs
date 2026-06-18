# sources/control-plane/external-snapshotter/client/hack/update-crd.sh

## Purpose
Regenerates CRD YAML from API type definitions using controller-gen.

Source size: 45 lines, 1279 bytes.

## Important APIs, Types, and Functions
- External commands/helpers: `controller-gen`, `find`, `go`, `mktemp`, `which`.

## Control Flow
- Computes `SCRIPT_ROOT` as the client directory.
- Looks for `controller-gen`; if absent, installs controller-gen v0.15.0 in a temporary Go module.
- Runs `controller-gen crd paths=${SCRIPT_ROOT}/apis/...`.

## State and Persistence
- Writes generated CRD manifests under controller-gen default output paths in the client tree.
- Uses a temporary directory for tool bootstrap and removes it afterward.

## Dependencies and Integration Points
- Go toolchain, controller-gen v0.15.0, API marker comments under `client/apis`.

## Risks and Edge Cases
- `set -o errexit` is commented out, so some failures may not abort as strictly as expected.
- Generated CRDs must be reviewed for schema/CEL drift before release.

## Test Signals
- Diff of generated CRDs and CEL test execution provide validation.
