# sources/cloud-native/moby/hack/make/test-integration-shell

## Purpose
Runs shell-based integration tests through the shared integration environment.

## Important APIs and Types
Thin shell wrapper around integration helper functions and shell test entrypoints.

## Control Flow, State, and Persistence
Delegates daemon startup, environment setup, and execution to `.integration-test-helpers`, then runs the shell integration suite.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on shell test files, daemon helpers, and built binaries. Risks include shell portability, environment leakage, and daemon cleanup. CI shell integration results validate it.
