# Research: sources/cloud-native/buildkit/codecov.yml

Purpose: configures Codecov reporting behavior for the BuildKit repository.

Important settings: pull-request comments are disabled. Project coverage uses an automatic target with a 1% threshold. Patch coverage status is disabled. GitHub check annotations are disabled. Generated protobuf files matching `**/*.pb.go` are ignored.

State and dependencies: this is CI configuration consumed by Codecov, not runtime BuildKit code. It affects repository coverage gates and reporting noise.

Risks and test signals: disabling patch status and annotations reduces friction but can hide localized coverage regressions. Ignoring generated protobuf files is appropriate because generated code would distort coverage. There are no local tests for this YAML.
