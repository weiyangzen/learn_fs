# sources/cloud-native/moby/hack/validate/default

## Purpose
Runs the default, non-vendor validation set.

## Important APIs and Types
Sources `pkg-imports`, `deprecate-integration-cli`, `golangci-lint`, and `shfmt`; DCO is intentionally skipped here.

## Control Flow, State, and Persistence
The script computes `SCRIPTDIR` and sources each validation script in order, failing on the first script that exits nonzero.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on shell sourcing and the individual validators. Risks include later checks not running after an early failure and sourced scripts leaking variables. CI default validation is the signal.
