# sources/cloud-native/ostree/manual-tests/static-delta-generate-crosscheck.sh

Purpose: This manual Bash test cross-checks static delta generation variants against a test repository. It verifies that a client can pull from an initial revision to a target revision using required static deltas and pass `ostree fsck`.

Important functions and commands: Inputs are repository path and branch. It resolves `from` as the branch parent and `to` as the branch head. `cleanup_tmpdir` removes the temporary workspace unless `PRESERVE_TMP` is set. `fatal` and `assert_streq` provide simple assertions. `validate_delta_options` initializes a bare-user test repo, disables fsync for speed, adds a local file remote with GPG verification disabled, generates a delta with supplied options, updates the summary, pulls the old revision, pulls the branch with `--require-static-deltas`, checks revision equality, runs `fsck`, and removes the test repo.

Control flow and state: The script uses `set -euo pipefail`, creates a `/var/tmp/ostree-delta-check.*` directory, marks it with `.tmp`, and optionally registers an EXIT trap. It invokes `validate_delta_options` three times: default, `--inline`, and `--disable-bsdiff`.

Dependencies and integration points: Depends on the `ostree` CLI, revision syntax with `^`, static delta generation, summary updates, local file remotes, pull behavior with required deltas, and repository fsck. It directly validates the manpage behavior for static delta generation.

Risks: Arguments are mostly unquoted, so paths or branch names with spaces would break. `assert_streq` uses unquoted `test`, which can misbehave on empty or special values. It disables fsync, which is acceptable for a temporary manual test but not representative of durability. Running against large repos may consume significant `/var/tmp` space.

Test signals: Success is no command failure under `set -e` and matching rev-parse outputs before and after delta pull. It should be run against content with meaningful parent/child revisions and should be extended if new delta generation options are added.
