<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/validate/yamllint -->
# sources/cloud-native/moby/api/validate/yamllint

## Purpose
Shell wrapper that runs yamllint for the Moby API OpenAPI/Swagger validation workflow.

## Important APIs, Types, And Functions
- The file is consumed by the API validation tooling rather than exported as Go API.

## Control Flow
- The script computes its directory, resolves the YAML config, and delegates lint execution to `yamllint` with repository-specific settings.

## State And Persistence
- No runtime persistence; the validator only reports lint findings.

## Dependencies And Integration Points
- Used by API validation scripts, not linked into the Go binaries.

## Risks And Edge Cases
- Validator drift can either hide OpenAPI formatting regressions or reject generated API files unexpectedly.

## Test Signals
- No direct test file is paired with this source; coverage is mostly integration-level through daemon/client API tests and compile-time use by downstream packages.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/validate/yamllint -->
