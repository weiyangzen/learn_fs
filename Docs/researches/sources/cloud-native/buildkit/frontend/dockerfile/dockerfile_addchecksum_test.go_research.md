# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_addchecksum_test.go

Purpose: integration-tests `ADD --checksum` for HTTP sources.

Important test cases: valid digest, digest and URL from env expansion, digest mismatch, unsupported known algorithm, unknown algorithm, missing algorithm, and checksum on local non-HTTP source.

Control flow and state: creates an HTTP test server with deterministic content, builds Dockerfiles through the frontend in an integration sandbox, and expects success or specific errors. Uses scratch/nanoserver base depending on platform.

Dependencies and integration: exercises parser, `convert_copy.go` checksum validation, LLB HTTP source checksum behavior, frontend solve, local mounts, and BuildKit client.

Risks and test signals: strong signal for HTTP checksum contract and error messages. Git checksum behavior is covered separately in ADD Git tests.
