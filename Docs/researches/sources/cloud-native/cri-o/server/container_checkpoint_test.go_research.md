# sources/cloud-native/cri-o/server/container_checkpoint_test.go

This file tests the `CheckpointContainer` CRI endpoint in enabled and disabled configurations. The enabled suite sets up dummy config, mocks runtime config, skips if CRIU is unavailable, enables checkpoint/restore with the test injection hook, and creates the server SUT. The success test adds a container and sandbox, marks the container running, sets a minimal OCI spec, and expects checkpointing to succeed. The invalid-container test expects an error. Cleanup removes checkpoint-related files such as `config.dump`, `cp.tar`, `dump.log`, and `spec.dump`.

The disabled suite sets `CheckpointRestore` false and verifies the endpoint returns the exact `"checkpoint/restore support not available"` message. State includes test framework server/container fixtures and checkpoint artifacts on disk. Dependencies include CRIU availability checks, OCI specs, CRI runtime API, Ginkgo/Gomega, and CRI-O internal OCI state.

Integration signal is strong for the feature gate and minimal working CRIU path, but environment-sensitive because CRIU may be absent and skip the success path. Gaps include target location handling, lower-layer checkpoint failures, non-running container behavior, and validation of checkpoint archive contents.
