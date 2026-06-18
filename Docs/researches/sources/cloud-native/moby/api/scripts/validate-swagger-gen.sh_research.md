# sources/cloud-native/moby/api/scripts/validate-swagger-gen.sh

## Purpose
This Bash script verifies that checked-in generated swagger model files are up to date with `swagger.yaml`, `swagger-gen.yaml`, templates, and `generate-swagger-api.sh`. It is intended for CI or local validation before committing generated API types.

## Important commands and variables
`SCRIPT_DIR` and `API_DIR` locate the API module. `TMP_DIR="$(mktemp -d)"` creates an isolated validation workspace and a trap removes it on exit. `GEN_FILES` is populated by `grep -rl "// Code generated" "${API_DIR}/types" || true`, which identifies generated Go files by marker comment.

The script copies generated files into a source-tree-shaped temp folder, copies `swagger.yaml`, `swagger-gen.yaml`, and `templates`, runs `generate-swagger-api.sh` inside the temp folder, then diffs every generated file against the repository copy.

## Control flow
The script exits on errors, unset variables, and pipeline failures with `set -euo pipefail`. It gathers generated files, copies each file preserving path relative to `API_DIR`, stages the swagger inputs, executes generation in a subshell rooted at `TMP_DIR`, then loops over original generated files. Any difference prints the relative file name and unified diff, sets `DIFF_FOUND=true`, and continues so all differences can be reported. At the end, any difference prints the remediation command and exits `1`; otherwise it prints that the swagger file is up to date.

## State and persistence behavior
The script should not modify the working tree. It writes only to `TMP_DIR`, which is deleted by the exit trap. Its persistent effect is through process exit status and diff output consumed by CI logs or developers.

## Dependencies
It requires Bash, `grep`, `mktemp`, `mkdir`, `cp`, `diff`, and the generator script. The generator requires the `swagger` CLI. In the Makefile, `make validate-swagger-gen` runs this inside the Docker dev image built by `api/Dockerfile`.

## Integration points
This is the validation counterpart to `generate-swagger-api.sh`. It integrates with `api/Makefile` target `validate-swagger-gen` and with generated files under `api/types`. It also depends on `swagger-gen.yaml` layout and `api/templates` remaining in sync with generated source.

## Risks and edge cases
If there are no generated files, `GEN_FILES` stays empty and the script can still print success after running generation, potentially missing newly generated files that were absent from the original marker scan. It diffs only files that already had the marker in the source tree, so newly required generated files may need a separate manifest or generated-file discovery. Suppressing generator stdout/stderr makes failures less verbose unless the command error itself is enough. The trap string does not quote `TMP_DIR` robustly for spaces, although `mktemp -d` normally returns a safe path.

## Test signals
The script itself is a test gate. Passing means all currently tracked generated files match a fresh generation run. Failing output includes exact diffs and tells the developer to run `./scripts/generate-swagger-api.sh` and commit updates.
