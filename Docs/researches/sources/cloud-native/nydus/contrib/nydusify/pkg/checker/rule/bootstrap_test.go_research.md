# sources/cloud-native/nydus/contrib/nydusify/pkg/checker/rule/bootstrap_test.go

## Purpose
This test file validates bootstrap rule behavior without invoking a real `nydus-image` binary.

## Important APIs, Types, and Functions
It monkeypatches `tool.Builder.Check`, constructs synthetic `parser.Parsed` and `parser.Image` values, and tests `BootstrapRule.validate`.

## Control Flow
The main test writes synthetic debug JSON matching or missing manifest blob IDs, asserts success or mismatch, then marks a layer as a Nydus reference layer to ensure it is ignored. Error tests write invalid JSON or remove the expected output file and assert wrapped read/unmarshal errors.

## State, Persistence, and Dependencies
Temporary workdirs hold fake bootstrap and output paths. Dependencies include JSON, filesystem APIs, gomonkey, digest, OCI spec, parser, remote, utils, and snapshotter label constants.

## Integration Points
The tests stabilize the contract between `nydus-image check` debug output and manifest layer validation.

## Risks and Test Signals
Tests do not cover real bootstrap parsing or actual `nydus-image` execution. They focus on the rule’s interpretation of debug output and annotations.
