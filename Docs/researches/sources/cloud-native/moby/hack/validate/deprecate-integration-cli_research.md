# sources/cloud-native/moby/hack/validate/deprecate-integration-cli

## Purpose
Prevents adding new tests to deprecated `integration-cli` API/CLI test files.

## Important APIs and Types
Uses `.validate`, `validate_diff`, grep for added `func ... Test` lines, and GitHub Actions `::error::` output.

## Control Flow, State, and Persistence
The script diffs changed `integration-cli/*_api_*.go` and `integration-cli/*_cli_*.go` files, looking only at added lines. If new test functions are found, it prints an error instructing authors to add tests under `integration/COMPONENT/`; otherwise it prints success.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on diff context and naming conventions. Risks include missing tests with nonstandard names or blocking helper functions that match the regex. CI validation protects migration away from integration-cli.
