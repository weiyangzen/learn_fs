# sources/cloud-native/moby/api/scripts/generate-swagger-api.sh

## Purpose
This Bash script regenerates selected Go model types from `api/swagger.yaml` using go-swagger. It centralizes the list of generated model names, target packages, template overrides, and special generation flags used by the API module.

## Important functions and commands
`API_DIR` resolves to the parent of the script directory, making the script runnable from any current working directory. `generate_model package [flags...]` reads model names from stdin with `mapfile`, then invokes `swagger generate model` with `--spec`, `--target`, `--model-package`, `--config-file`, `--template-dir`, and `--allow-template-override`. Additional flags are forwarded after the package argument.

The model stanzas call `generate_model` for packages under `types/build`, `types/common`, `types/container`, `types/image`, `types/network`, `types/plugin`, `types/registry`, `types/storage`, `types/swarm`, and `types/volume`. Network generation uses `--keep-spec-order` and `--additional-initialism=IPAM`. `ImageSummary` is commented out pending a go-swagger update.

## Control flow
The script exits on unset variables or command failures via `set -eu`. Each here-document supplies a sorted model-name list to `generate_model`. The helper consumes stdin into Bash's `MAPFILE` array, builds repeated `--name=` arguments with `printf`, and runs go-swagger once per package stanza. If any generation command fails, the script stops immediately.

## State and persistence behavior
This script writes generated Go files under `API_DIR` according to the layout in `swagger-gen.yaml`. It can modify many `api/types/**` files and relies on go-swagger templates in `api/templates`. It does not use temp directories itself; callers such as `validate-swagger-gen.sh` run it in a temporary API copy for validation.

## Dependencies
It requires Bash, the `swagger` CLI from go-swagger, `swagger.yaml`, `swagger-gen.yaml`, and optional template overrides. In the API Makefile, `make swagger-gen` builds and runs the module's Docker dev image before executing this script, so the expected CLI version is provided by `api/Dockerfile`.

## Integration points
The script is invoked by the API Makefile `swagger-gen` target and by `validate-swagger-gen.sh`. The generated files are detected by the `// Code generated` marker. The output packages are the public API Go type packages used by clients and daemon code.

## Risks and edge cases
The model list is hand-maintained; missing a swagger definition means its generated type will not be refreshed. The script warns maintainers to sort stanzas and names alphabetically to reduce merge conflicts, but sorting is not enforced. The generated output is sensitive to go-swagger version, templates, and `swagger-gen.yaml` layout. The `$(printf ...)` expansion intentionally relies on shell word splitting to produce separate `--name` arguments; model names with whitespace would break, though swagger model names should not contain whitespace.

## Test signals
`validate-swagger-gen.sh` is the main regression gate: it copies current generated files, reruns this script in a temp directory, and diffs outputs. `validate-swagger.sh` separately validates the source spec. The Dockerfile pins the toolchain path used by Makefile targets.
