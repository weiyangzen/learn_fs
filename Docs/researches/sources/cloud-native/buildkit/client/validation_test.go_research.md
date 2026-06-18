# sources/cloud-native/buildkit/client/validation_test.go

## Purpose
This integration-test source verifies that invalid exporter and source-policy metadata is rejected with clear errors. It focuses on OCI image export validation and source-policy validation from both client solve options and gateway frontend solve requests.

## Important APIs, Types, and Functions
- `validationTests` registers the validation cases for the integration suite.
- `testValidateNullConfig` injects `containerimage.config` as JSON `null` and expects export rejection.
- `testValidateInvalidConfig` injects an image config with architecture but missing OS and expects platform validation failure.
- `testValidatePlatformsEmpty` injects null `refs.platforms` metadata and expects empty platforms index rejection.
- `testValidatePlatformsInvalid` covers empty platform IDs and platform entries missing OS/architecture values.
- `testValidateSourcePolicy` covers malformed source policies provided through `SolveOpt.SourcePolicy` and through gateway `SolveRequest.SourcePolicies`.

## Control Flow
Each image validation case opens a client, runs a gateway frontend that solves a scratch state, injects bad exporter metadata into the gateway result, and then exports through the OCI exporter to a discard writer. Source-policy validation builds an alpine image solve and runs each malformed policy once as a client option and once as a frontend-provided source policy.

## State and Persistence Behavior
The tests use no durable outputs; OCI exports write to a discard writer. The important state is metadata attached to gateway results and policy protobufs passed into the solver/exporter validation path.

## Dependencies and Integration Points
The file integrates with gateway frontends, LLB scratch/image states, OCI exporter validation, containerimage exporter metadata keys, source-policy protobuf validation, integration sandbox clients, and worker feature gates for OCI export. It requires Linux for the covered exporter path.

## Risks and Edge Cases
The tests guard against accepting malformed image configs, partial platform values, empty platform indexes, nil policy selectors, unknown policy actions, and convert policies without destinations. These are important because invalid metadata can create broken image outputs or ambiguous source-policy decisions.

## Test Signals
Passing tests indicate invalid exporter metadata and invalid source policies are rejected consistently whether supplied by the client or a frontend. Failures point to validation gaps in the exporter, gateway result handling, or policy protobuf validation.
