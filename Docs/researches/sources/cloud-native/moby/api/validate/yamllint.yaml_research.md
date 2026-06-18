<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/validate/yamllint.yaml -->
# sources/cloud-native/moby/api/validate/yamllint.yaml

## Purpose
Configuration file for the API validation yamllint invocation.

## Important APIs, Types, And Functions
- The file is consumed by the API validation tooling rather than exported as Go API.

## Control Flow
- There is no executable control flow; the yamllint process reads this declarative rule set.

## State And Persistence
- No runtime persistence; the validator only reports lint findings.

## Dependencies And Integration Points
- Used by API validation scripts, not linked into the Go binaries.

## Risks And Edge Cases
- Validator drift can either hide OpenAPI formatting regressions or reject generated API files unexpectedly.

## Test Signals
- No direct test file is paired with this source; coverage is mostly integration-level through daemon/client API tests and compile-time use by downstream packages.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/validate/yamllint.yaml -->
