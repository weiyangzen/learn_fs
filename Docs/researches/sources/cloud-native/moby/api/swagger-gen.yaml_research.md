# sources/cloud-native/moby/api/swagger-gen.yaml

## Purpose
This YAML file configures go-swagger output layout for generated API code. It tells the generator where model and operation files should be written and how names should be converted into Go file names.

## Important configuration
Under `layout.models`, the `definition` layout uses `asset:model` as the source template, targets `{{ joinFilePath .Target .ModelPackage }}`, and writes files named `{{ (snakize (pascalize .Name)) }}.go`. Under `layout.operations`, the `handler` layout uses `asset:serverOperation`, targets `{{ joinFilePath .Target .APIPackage .Package }}`, and uses the same file-name transformation.

## Control flow
This file is declarative. go-swagger reads it during `swagger generate model` calls from `generate-swagger-api.sh`. The templating expressions are evaluated by go-swagger using the generation context for target directory, model package, API package, operation package, and model or operation names.

## State and persistence behavior
The file persists generation layout policy in version control. It does not write files itself, but it directly controls where generator output lands and what filenames are considered canonical. Changes can rename or move many generated Go files.

## Dependencies
It depends on go-swagger's config schema, built-in assets `asset:model` and `asset:serverOperation`, and template helper functions `joinFilePath`, `snakize`, and `pascalize`. It is consumed by `generate-swagger-api.sh` and copied by `validate-swagger-gen.sh`.

## Integration points
The model layout is used for generated files under `api/types/**`. The operation layout is configured even though the assigned generator script currently invokes `swagger generate model`, making it available for operation generation if used by other tooling or future scripts. The naming rule explains generated filenames such as `root_f_s_storage.go` from model names with initialisms.

## Risks and edge cases
Changing filename transformation can create churn or leave stale generated files behind if cleanup is not handled. The current `snakize(pascalize(.Name))` behavior can produce awkward initialism splitting, but that may already be part of the checked-in API module's generated-file contract. The operation layout should be kept in sync with template overrides if operation generation is reintroduced.

## Test signals
`validate-swagger-gen.sh` copies this file into a temporary workspace before regenerating and diffing generated files. Any layout change that affects existing generated files should be caught by that validation. There is no schema-only test for this YAML in the assigned files.
