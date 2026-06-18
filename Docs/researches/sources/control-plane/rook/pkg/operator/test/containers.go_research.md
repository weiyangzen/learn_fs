# sources/control-plane/rook/pkg/operator/test/containers.go

## Purpose
`containers.go` implements assertion helpers for container specs used by Rook unit tests.

## Important APIs, Types, and Functions
`ContainersTester` wraps a container list. `ResourceLimitExpectations` defines optional expected CPU/memory limits and requests. `PodSpecTester.Containers()` gathers init and normal containers. `AssertArgReferencesMatchEnvVars()` ensures `$(ENV)` references in args have corresponding env vars. `AssertResourceSpec()` checks resource strings. `RunFullSuite()` runs both checks. `argEnvReferences()` and `varNames()` extract references and env names.

## Control Flow, State, and Persistence
The helpers operate in memory and report through `testing.T` assertions. Arg references are deduplicated via a map and extracted with a regular expression.

## Dependencies and Integration Points
It depends on Kubernetes container types, testify, and regexp. It integrates with `PodSpecTester` and `PodTemplateSpecTester` full-suite checks.

## Risks
The regex recognizes only names starting with ASCII letters and followed by alphanumerics/underscore, which aligns with common env names but excludes some invalid or unusual references. Resource checks apply expectations to every container in the set.

## Test Signals
No direct tests are mapped. Downstream pod-template tests using `RunFullSuite()` validate arg/env consistency and resource settings.
