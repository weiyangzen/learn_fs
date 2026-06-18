# sources/cloud-native/ostree/tests/test-pull-subpath.sh

## Purpose
This shell TAP test validates `ostree pull --subpath` for partial commit pulls over both HTTP and local `file://` remotes. It ensures selected directories and files become accessible, unrelated objects remain absent until a full pull, commitpartial state is persisted, and pruning keeps metadata needed by partial pulls.

## Important APIs, Types, And Functions
The script uses `setup_fake_remote_repo1`, `ostree_repo_init`, `ostree remote add`, `ostree pull --subpath`, `ostree ls`, `ostree rev-parse`, `ostree prune --refs-only`, and `ostree fsck`. Assertions come from `libtest.sh`, especially `assert_file_has_content`, `assert_has_file`, `assert_not_has_file`, and `assert_not_reached`.

## Control Flow
The test clones a fake archive remote, then loops over HTTP and local remote URLs. For each URL it initializes a client repo, disables GPG verification, pulls two subdirectories, confirms those paths exist and `/firstfile` fails, and checks `repo/state/<rev>.commitpartial`. It then pulls `/firstfile`, performs a full pull, confirms the commitpartial marker disappears, and runs `fsck`. A second repo pulls only `/baz/deeper`, prunes refs-only, and verifies that the pulled subdirectory remains readable.

## State And Persistence
Persistent state includes remote config, fetched object files, refs, the partial commit marker under `repo/state`, and pruned object reachability. The remote is copied to `.orig` but the main flow mutates only temporary repos under `test_tmpdir`.

## Dependencies And Integration Points
This depends on the OSTree CLI, local test HTTP server setup from `libtest.sh`, archive-mode remote fixtures, and partial object semantics in the repository layer. It integrates with pull, object lookup, commitpartial tracking, and prune reachability.

## Risks
Subpath pulls are sensitive to object graph traversal order, missing dirmeta objects, and cleanup rules. A bug may incorrectly make unrelated paths visible, drop metadata during prune, or leave stale commitpartial state after a full pull. HTTP and file remotes exercise slightly different fetch paths, so both are important.

## Test Signals
The TAP plan reports four assertions: subpath behavior and prune behavior for each remote transport. Failure signals include "Couldn't find file object", missing commitpartial markers, failed `ostree ls`, or `ostree fsck` errors.
