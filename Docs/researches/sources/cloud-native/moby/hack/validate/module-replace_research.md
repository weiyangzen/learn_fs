# sources/cloud-native/moby/hack/validate/module-replace

## Purpose
Ensures local replace rules are present when `api` or `client` module source changes require them.

## Important APIs and Types
Uses `.validate`, `filter_diff`, `only_changes_module`, `go list -m -json`, `jq`, and `TEST_FORCE_VALIDATE`.

## Control Flow, State, and Persistence
The script gathers non-test/documentation diffs under `api` and `client`, prints current `go.mod`, and checks whether changed modules have appropriate `replace` entries. Client diffs that only update the API module revision are allowed. It exits nonzero if required replace rules are missing.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on git diff, Go module metadata, and jq. Risks include path filter omissions, noisy go.mod output, and false positives for generated/version-only changes. CI module validation is the signal.
