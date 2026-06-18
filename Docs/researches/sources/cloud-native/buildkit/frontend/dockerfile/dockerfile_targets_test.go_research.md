# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_targets_test.go

## Purpose
This file tests the Dockerfile frontend's `frontend.targets` subrequest. Target metadata lists stages, base images, default target status, descriptions derived from comments, sources, and location data. It also checks subrequest discovery metadata.

## Important APIs, Types, and Functions
Registered tests are `testTargetsList` and `testTargetsDescribeDefinition`; `unmarshalTargets` decodes `result.json` into `targets.List`. The file uses `workers.CheckFeatureCompat(workers.FeatureFrontendTargets)`, client frontend gating, `client.Build`, gateway `c.Solve`, `FrontendOpt{"frontend.caps", "requestid": "frontend.targets"}`, `subrequests.Describe`, and platform-specific base image selection.

## Control Flow and Assertions
`testTargetsList` creates a Dockerfile with named and unnamed stages plus comments before two stages. The gateway callback invokes `frontend.targets`, unmarshals the list, and asserts source bytes, four target entries, names, base image values, descriptions, default flag only on the final named target, and exact source line numbers. `testTargetsDescribeDefinition` invokes `subrequests.Describe` and verifies `frontend.targets` appears as an RPC request with a non-empty version.

## State, Persistence, and Dependencies
The tests are metadata-only and keep state in temp Dockerfile mounts and decoded result JSON. They depend on client frontend support, subrequest capability negotiation, parser source-location tracking, and comment-to-description extraction.

## Integration Points
This file integrates Dockerfile stage parsing with gateway subrequest output, target default selection, source inclusion, and frontend capability discovery. It does not run/export target stages; it validates metadata extraction before actual build execution.

## Risks and Test Signals
Risks include incorrect default target marking, lost unnamed stages, wrong base image reporting, stale line numbers after parser changes, descriptions attaching to the wrong stage, and subrequest discovery drift. Signals are exact list length, exact per-target fields, source equality, and `Describe` metadata checks.
