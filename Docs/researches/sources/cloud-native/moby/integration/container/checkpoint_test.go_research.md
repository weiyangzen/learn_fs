## sources/cloud-native/moby/integration/container/checkpoint_test.go

Purpose: intended checkpoint/restore integration test using CRIU, but the test is currently unconditionally skipped as broken. It documents desired behavior for creating checkpoints with and without stopping the container, listing checkpoints, restoring from a checkpoint, and removing checkpoints.

Control flow after the skip would require non-Windows experimental daemon, run `criu check`, start a container with tmpfs, bind `true` over ip6tables tools to avoid missing modules, create checkpoint `test` with `Exit:false`, create a file, create checkpoint `test2` with `Exit:true`, restore with `CheckpointID:test2`, verify file existence, and remove both checkpoints.

State would include CRIU dump files, container running/exited state, checkpoint metadata, tmpfs contents, and temporary bind mounts on host binaries. Dependencies include CRIU, experimental daemon, request API client, internal container helpers, and host mount privileges. Risks are high and acknowledged by the skip: host mutation, CRIU/kernel variability, dump-log parsing, and cleanup complexity. Test signal is currently only the skip.
