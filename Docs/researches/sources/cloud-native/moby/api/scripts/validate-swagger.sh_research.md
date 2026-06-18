# sources/cloud-native/moby/api/scripts/validate-swagger.sh

## Purpose
This Bash script validates the API module's `swagger.yaml` for style and schema correctness. It is the lightweight spec-validation gate separate from generated-code freshness.

## Important commands
The script changes to the API module root using the script location. It runs `yamllint -f parsable -c validate/yamllint.yaml swagger.yaml`, then runs `swagger validate swagger.yaml`. The `swagger validate` output is captured so success can include the message and failure can print the message to stderr before returning a failing status.

## Control flow
`set -e` stops the script on the first failing command except inside the explicit `if out=$(swagger validate swagger.yaml); then ... else ... fi` branch. The current directory is normalized to `api`. Yamllint runs first; if it fails, swagger validation is not attempted. If swagger validation fails, the captured output is emitted to stderr and `false` produces a non-zero exit.

## State and persistence behavior
The script is read-only. It does not generate files, modify the spec, or create temp data. Its only outputs are console messages and exit status.

## Dependencies
It requires Bash, `yamllint`, the go-swagger `swagger` CLI, `validate/yamllint.yaml`, and `swagger.yaml`. The API Dockerfile installs Bash, make, and yamllint, and installs go-swagger for the dev image used by the Makefile target.

## Integration points
The API Makefile exposes this as `make validate-swagger`, running inside the Docker dev image. It complements `validate-swagger-gen.sh`: this file checks that the source swagger spec is valid, while the generation validator checks generated Go code freshness.

## Risks and edge cases
Because yamllint runs before schema validation, a style error blocks deeper validation output. The script assumes it is run in an environment with compatible `swagger` and `yamllint` versions. It validates only `swagger.yaml`, not versioned docs such as `api/docs/v*.yaml`. `set -e` without `pipefail` is acceptable here because there are no pipelines.

## Test signals
The direct test signal is the exit status of yamllint and `swagger validate`. Passing output includes `Validation done! ...`; failing output comes from yamllint or swagger validation and should fail CI/local checks.
