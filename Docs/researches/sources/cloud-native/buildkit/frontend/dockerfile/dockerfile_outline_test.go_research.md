# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_outline_test.go

## Purpose
This file tests the Dockerfile frontend's `frontend.outline` subrequest. Outline metadata describes a selected target, its source Dockerfile, ARGs with computed values and descriptions, secrets, SSH mounts, and request availability through `subrequests.Describe`. It is intentionally limited to the client frontend when required.

## Important APIs, Types, and Functions
Registered tests are `testOutlineArgs`, `testOutlineSecrets`, `testOutlineRecursiveArgs`, and `testOutlineDescribeDefinition`; `unmarshalOutline` decodes `result.json` into `outline.Outline`. The suite uses `workers.CheckFeatureCompat(workers.FeatureFrontendOutline)`, `client.Build`, gateway `c.Solve`, `FrontendOpt` values `frontend.caps`, `requestid=frontend.outline`, build args, target selection, `subrequests.Describe`, and `outline` model types.

## Control Flow and Assertions
The tests construct Dockerfiles with commented ARGs and stages, invoke a gateway callback through `client.Build`, and inside the callback solve `dockerfile.v0` with the outline request. `testOutlineArgs` verifies target name/description extraction, source preservation, inherited/global ARGs, target-local ARGs, build-arg overrides, skipped secret-looking ARG descriptions, and exact source line locations. `testOutlineSecrets` checks only reachable target dependencies are represented, with computed secret IDs and required flags plus SSH IDs. `testOutlineRecursiveArgs` verifies recursive ARG expansion and deduped output values. `testOutlineDescribeDefinition` confirms `frontend.outline` appears as an RPC subrequest with a version.

## State, Persistence, and Dependencies
State is transient: Dockerfile bytes are kept in temp local mounts and decoded outline metadata is held in memory. Dependencies include frontend subrequest capability support, source-location tracking, comment parsing, ARG expansion, and platform-specific Dockerfile variants.

## Integration Points
The file integrates Dockerfile parsing with frontend subrequest RPCs, target graph reachability, secrets/SSH mount analysis, build-arg substitution, source attachment, and source location serialization. It verifies the metadata contract without exporting images.

## Risks and Test Signals
Risks include outline leaking unreachable stages, losing source bytes, reporting wrong lines after parser changes, mishandling recursive ARGs, including skipped secret-like ARG descriptions incorrectly, and subrequest discovery drifting. Signals are exact equality on names, values, descriptions, source bytes, required flags, and line numbers.
