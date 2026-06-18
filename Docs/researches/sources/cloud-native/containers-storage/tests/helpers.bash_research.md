# sources/cloud-native/containers-storage/tests/helpers.bash

Purpose: shared Bats helpers for the `containers-storage` CLI test suite. It centralizes temporary storage setup, teardown, command invocation, random test-file creation, and reusable layer/diff assertions.

Important APIs and control flow: `setup` creates a random `TESTDIR` under `BATS_TMPDIR`, with `root` and `runroot` subdirectories, and disables overlay idmapped mounts for tests that expect legacy idmap behavior. `teardown` runs `storage wipe`, `storage shutdown`, and removes the temp directory. `storage`, `storagewithsorting`, and `storagewithsorting2` wrap the test binary with `--graph`, `--run`, driver, transient-store, and optional storage options. `populate` constructs three layered filesystems, capturing layer IDs in global variables; `checkchanges` and `checkdiffs` assert exact change lists and tar members from those layers.

State and persistence: state is intentionally temporary and isolated in `TESTDIR`; transient store mode changes lock-root expectations through `CONTAINERS_LOCK_ROOT` and `--transient-store`. Random files are timestamped to the epoch for deterministic archive/dedup behavior.

Dependencies and integration: depends on Bash, Bats `run/status/output/lines`, `dd`, `base64`, `touch`, `tar`, `sort`, and the `containers-storage` CLI. It is sourced by `test_runner.bash` and used by multiple Bats tests.

Risks: `eval` is not used here, but unquoted path expansion appears in several commands, so paths with spaces are not robust. `touch -d` is GNU-specific despite the comment about portability. Assertions encode exact diff ordering after sorted output, so driver-specific whiteout behavior can break tests.

Test signals: this file is itself test infrastructure; failures surface as Bats assertion failures in layer creation, diff generation, change detection, cleanup, or CLI shutdown paths.
