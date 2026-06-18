# sources/cloud-native/moby/hack/validate/all

## Purpose
Runs the full validation set.

## Important APIs and Types
Sources `default` and `vendor` from the validation directory.

## Control Flow, State, and Persistence
The script computes `SCRIPTDIR`, then sequentially executes default validation and vendoring validation in the current shell.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on every sourced validation script and shared `.validate`. Risks include sourced scripts mutating shell state and early exit preventing later checks. CI validation pass/fail is the signal.
