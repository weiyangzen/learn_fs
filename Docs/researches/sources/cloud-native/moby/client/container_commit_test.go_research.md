<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_commit_test.go -->
# sources/cloud-native/moby/client/container_commit_test.go

Purpose: tests `ContainerCommit` request construction and error behavior.

Important coverage: daemon internal errors, invalid container ids, method/path `POST /commit`, query parameters for container, repo/tag/comment/author/changes, `pause=0` when `NoPause` is true, and decoding the returned image ID.

Control flow and dependencies: mock callbacks inspect the request and return JSON commit responses. It depends on `assertRequest`, `errorMock`, and container API types.

State and risks: no local persistence. This is high-signal for compatibility with Docker image reference handling and commit query conventions.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_commit_test.go -->
