# sources/cloud-native/cri-o/server/suite_test.go

## Purpose
Shared Ginkgo suite fixture for server package tests.

## Important APIs, Types, And Functions
Defines `TestServer`, package-level mocks and fixtures, `beforeEach`, `afterEach`, `setupSUT`, `mockNewServer`, `addContainerAndSandbox`, `mockDirs`, `createDummyState`, `createDummyConfig`, and `mockRuntimeInLibConfig`.

## Control Flow
`BeforeSuite` creates a `TestFramework` and an empty temp directory. `beforeEach` lowers logging, constructs GoMock controllers and mocks, builds a synthetic OCI manifest, initializes default CRI-O config with test paths, disables hostport mapping, creates a test sandbox/container, and initializes a streaming server. `setupSUT` calls `mockNewServer`, constructs the server, then injects storage image/runtime mocks. Cleanup removes transient files and finishes the mock controller.

## State And Persistence
Uses temp directories for graphroot, CRI-O paths, seccomp notifier path, NRI socket path, and suite scratch space. Writes optional `state.json` and `config.json` helper files in the package working directory.

## Dependencies And Integration Points
Ties together CRI-O config, sandbox and OCI container builders, memorystore, CRI streaming server, CNI mock, storage mock, runtime mock, and the common test framework.

## Risks And Test Signals
This file is foundational for many server tests; fixture drift can create misleading failures across unrelated specs. The stream service is initialized with `sut` before `sut` is assigned, then tests rely on later injection paths. The fixture gives strong constructor and storage-restoration signal but is not an integration replacement for real CRI-O daemon behavior.
