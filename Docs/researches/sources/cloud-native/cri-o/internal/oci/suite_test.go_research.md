# sources/cloud-native/cri-o/internal/oci/suite_test.go

## Purpose
Shared Ginkgo test framework setup for the OCI package tests.

## Important APIs and State
`TestOci` registers the Gomega fail handler and runs framework specs. Global test state includes `TestFramework`, gomock controller, container storage mock, a reusable container, and config. `beforeEach` creates a basic container. `getTestContainer` creates a richer container with image reference and storage image ID. `BeforeSuite`/`AfterSuite` set up and tear down the test framework and mocks.

## Integration and Risks
This file underpins `container_test.go`, `oci_test.go`, and `runtime_oci_test.go`. Global state makes test ordering and cleanup important; gomock finish is centralized here.
