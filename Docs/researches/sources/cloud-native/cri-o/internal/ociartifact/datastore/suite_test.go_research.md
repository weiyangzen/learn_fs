# sources/cloud-native/cri-o/internal/ociartifact/datastore/suite_test.go

## Purpose
Ginkgo suite bootstrap for datastore tests.

## Behavior and Integration
`TestRun` registers failure handling and runs framework specs named `DataStore`. Suite setup/teardown initializes the shared CRI-O test framework. This is required for `store_test.go`.

## Risks
Global framework state is small here; failures would mostly affect test setup/cleanup rather than production code.
