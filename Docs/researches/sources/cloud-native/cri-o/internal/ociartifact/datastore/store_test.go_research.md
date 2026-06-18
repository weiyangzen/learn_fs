# sources/cloud-native/cri-o/internal/ociartifact/datastore/store_test.go

## Purpose
Unit tests for datastore `PullData` reference-resolution failures.

## Test Signals
The tests create a datastore in a temporary artifact root, inject a mocked `Impl`, and verify that `PullData` returns errors when `ParseNormalizedNamed` fails and when `DockerNewReference` fails. They assert returned data is nil and error strings include the expected wrapping context.

## Dependencies and Risks
Uses gomock, Ginkgo/Gomega, and mocked datastore implementation. Coverage is narrow; blob reading, digest verification, max-size enforcement, name/digest lookup, and pull success paths are not covered here.
