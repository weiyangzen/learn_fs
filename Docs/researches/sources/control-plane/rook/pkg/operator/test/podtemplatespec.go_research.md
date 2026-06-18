# sources/control-plane/rook/pkg/operator/test/podtemplatespec.go

## Purpose
`podtemplatespec.go` wraps Kubernetes `PodTemplateSpec` objects with reusable Rook test assertions.

## Important APIs, Types, and Functions
`PodTemplateSpecTester` stores `testing.T` and a template pointer. `NewPodTemplateSpecTester()` constructs the wrapper. `AssertLabelsContainRookRequirements()` delegates to the package-level label assertion. `RunFullSuite()` checks labels and then runs pod-spec/container/volume checks.

## Control Flow, State, and Persistence
The file has no persistence. It composes other assertion helpers and reports through `testing.T`.

## Dependencies and Integration Points
It depends on Kubernetes core/v1 pod templates and local test helpers. It is used by operator tests for Deployments, DaemonSets, Jobs, and other template-bearing resources.

## Risks
The label requirements are currently minimal, checking only `app=<appName>`. The full suite can fail on intentionally unused volumes or per-container resource differences unless tests choose expectations carefully.

## Test Signals
No direct tests are mapped. Downstream full-suite tests provide signal that generated pod templates include expected labels, volume mounts, env references, and resources.
