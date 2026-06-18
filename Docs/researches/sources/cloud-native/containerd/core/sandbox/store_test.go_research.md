# sources/cloud-native/containerd/core/sandbox/store_test.go

## Purpose
Tests typed sandbox extension helper round-tripping.

## APIs, Flow, State, Dependencies, Risks, And Tests
`TestAddExtension` registers a local `test` struct type with typeurl, adds it to a sandbox under key `"test"`, retrieves it into another struct value, and asserts the field value survived.

The test mutates only in-memory sandbox metadata. Dependencies include typeurl and testify assertions.

It verifies extension map initialization, marshal, unmarshal, and key lookup. Gaps include absent extension error tests, invalid type unmarshalling, and label helper tests.
