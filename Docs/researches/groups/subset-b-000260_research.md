# subset-b-000260 research

This grouped report covers the requested OSTree pull, summary, remote, ref, repo-finder, signing, sysroot, and utility tests plus two OverlayBD GitHub issue-template files. Each source file has a separate section wrapped in reconciliation markers so it can be split into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-subpath.sh -->
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
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-subpath.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-summary-caching.sh -->
# sources/cloud-native/ostree/tests/test-pull-summary-caching.sh

## Purpose
This test verifies that signed remote summary files and their signatures are cached and reused across repeated pulls. It specifically guards against unnecessary redownloads by comparing cache file inode numbers.

## Important APIs, Types, And Functions
The script uses `skip_without_ostree_feature gpgme`, `setup_fake_remote_repo2`, `ostree commit`, `ostree summary -u`, `ostree remote add --set=gpg-verify-summary=true`, and `ostree pull`. It uses `stat -c %i` to detect replacement of cache files.

## Control Flow
After enabling repo caching by unsetting `OSTREE_SKIP_CACHE`, the script creates a signed remote with extra `other` and `yet-another` branches, updates and signs the summary, initializes an archive client repo, configures summary verification, and pulls `origin other`. It records inodes for `repo/tmp/cache/summaries/origin` and `.sig`, performs the same pull again, and asserts that both inodes are unchanged.

## State And Persistence
The important persistent state is the client summary cache under `repo/tmp/cache/summaries/`. The remote stores signed commits, refs, `summary`, and `summary.sig`. No per-test global state should leak except the temporary GPG home supplied by the harness.

## Dependencies And Integration Points
This integrates GPGME signing, summary regeneration, summary verification, pull caching, and local HTTP service. It depends on filesystem inode semantics, so it is Unix-specific and assumes the cache directory is not transparently recreated by the filesystem.

## Risks
Summary cache update logic must avoid rewriting valid cached files on repeated pulls, otherwise clients do extra I/O and can invalidate cache coherency assumptions. The test also risks false negatives on filesystems with unusual inode behavior, but the OSTree test suite generally runs on local Unix filesystems.

## Test Signals
The single TAP result is `ok pull caches the summary files`. Any cache rewrite, missing summary, missing signature, or GPGME-unavailable environment causes skip or failure.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-summary-caching.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-summary-sigs.sh -->
# sources/cloud-native/ostree/tests/test-pull-summary-sigs.sh

## Purpose
This large shell test validates pulling from summary files, signed summary verification, cache cleanup, custom cache directories, invalid summary failures, static-delta metadata display, and race recovery for mismatched summary/signature pairs.

## Important APIs, Types, And Functions
It uses `has_ostree_feature gpgme`, `setup_fake_remote_repo1`, `ostree commit`, `ostree summary -u`, `ostree pull --mirror`, `ostree remote add --set=gpg-verify-summary=true`, `ostree prune`, `ostree static-delta generate`, `ostree remote summary`, metadata key options, and `OSTREE_REPO_TEST_ERROR=invalid-cache`. Helper `repo_reinit` resets a client repo with summary verification enabled.

## Control Flow
The test first creates a multi-branch remote and checks that mirror pull from an unsigned summary retrieves all branches and passes `fsck`. If GPGME exists, it signs the summary and runs repeated scenarios: normal signed summary pull and cache refill, pruning stale summary cache entries, using `--cache-dir`, rejecting invalid `summary.sig`, rejecting malformed `summary`, pulling a static delta with signed summary, checking human and metadata-key output from `remote summary`, and simulating races between old/new summaries and signatures. The final scenarios ensure the client preserves the last valid cache on verification failure and can recover after the remote publishes a matching pair.

## State And Persistence
State is held in remote refs, `summary`, `summary.sig`, static delta metadata, client refs, object stores, and cache files under either `repo/tmp/cache/summaries` or an external `cachedir/summaries`. The script deliberately copies `summary.1`, `summary.2`, and matching signatures to model server-side race windows.

## Dependencies And Integration Points
This covers summary parsing, GPG signature verification, cache update atomicity, pull mirror semantics, static delta indexing, remote summary CLI rendering, metadata printing, and test-only invalid-cache injection in repository code. It depends on the local HTTP server and GPGME-enabled builds for most checks.

## Risks
The highest-risk behavior is replacing a valid cache with an unverified or mismatched summary/signature pair. Other risks include accepting malformed summaries, deleting valid cache entries during prune, mishandling custom cache directories, and printing stale static-delta metadata. Timestamp manipulation is used to model races and may be sensitive to filesystem granularity.

## Test Signals
The plan is one test without GPGME and ten with GPGME. Success signals include valid checkouts of all branches, preserved cache files after failed race pulls, expected `BAD signature` and invalid-cache errors, and exact metadata keys such as `ostree.summary.indexed-deltas` and `ostree.summary.mode`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-summary-sigs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-untrusted.sh -->
# sources/cloud-native/ostree/tests/test-pull-untrusted.sh

## Purpose
This security regression test ensures `ostree pull-local --untrusted` rejects repository content with path traversal filenames.

## Important APIs, Types, And Functions
The test uses `setup_test_repository`, `tar xf ostree-path-traverse.tar.gz`, `ostree_repo_init`, and `ostree pull-local --untrusted`. It asserts the literal error `Invalid / in filename ../afile`.

## Control Flow
The script sets up a bare repository fixture, extracts a crafted archive containing a malicious OSTree repository, initializes a new archive repo, and attempts to pull `pathtraverse-test` from that untrusted local repo. Success is considered a failure; the expected path validation error is checked from stderr.

## State And Persistence
The crafted repository and target `repo2` live in `test_tmpdir`. No successful refs or objects should be persisted in `repo2` from the rejected pull.

## Dependencies And Integration Points
This integrates untrusted local pull validation, archive object import, filename sanitization, and the test fixture archive `ostree-path-traverse.tar.gz`.

## Risks
If validation regresses, malicious object names could escape repository object paths during untrusted imports. The test only covers one traversal payload but anchors the expected rejection path.

## Test Signals
The single TAP result is `ok untrusted pull-local path traversal`. Any successful pull or missing literal error indicates a security-sensitive failure.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-untrusted.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull2-bareuseronly.sh -->
# sources/cloud-native/ostree/tests/test-pull2-bareuseronly.sh

## Purpose
This wrapper runs the shared `pull-test2.sh` suite against a `bare-user-only` target repository mode. It validates the common pull matrix for user-only bare repos.

## Important APIs, Types, And Functions
It uses `setup_fake_remote_repo2 "archive" "--canonical-permissions"`, sets `repo_mode=bare-user-only`, and sources `${test_srcdir}/pull-test2.sh`.

## Control Flow
The script initializes an archive remote with canonical permissions, sets the repo mode consumed by the shared test file, and delegates all actual scenarios to `pull-test2.sh`.

## State And Persistence
State is created by the shared pull-test harness: remote repositories, client repo, refs, objects, checkouts, and any pull cache state. This wrapper's only persistent behavior is selecting `bare-user-only` mode.

## Dependencies And Integration Points
It depends directly on `libtest.sh`, `pull-test2.sh`, and OSTree support for bare-user-only repositories. It integrates the shared pull semantics with canonical permission normalization.

## Risks
Because behavior is delegated, drift in `pull-test2.sh` can change the effective coverage. The main mode-specific risks are UID/GID, mode, xattr, and object layout differences between archive and bare-user-only repos.

## Test Signals
Test output and TAP plan come from `pull-test2.sh`. Failure indicates the shared pull behavior does not hold for `bare-user-only`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull2-bareuseronly.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-refs-collections.sh -->
# sources/cloud-native/ostree/tests/test-refs-collections.sh

## Purpose
This shell test validates collection-aware ref listing, filtering, creation, deletion, remote ref visibility, and compatibility with older repositories that lack `refs/mirrors`.

## Important APIs, Types, And Functions
The test uses `ostree_repo_init --collection-id`, `ostree commit`, `ostree refs`, `ostree refs --collections`, `--list`, `--delete`, `--create=COLLECTION:REF`, `ostree remote add --collection-id`, and `ostree pull`.

## Control Flow
It creates a repo with collection ID `org.example.Collection`, commits five refs, confirms plain `refs` hides collection IDs while `--collections` shows them, tests collection filtering, exercises deletion by explicit refs and by collection ID, creates a mirrored collection ref, then pulls from a remote with a collection ID and confirms it appears in collection listings. A second remote without a collection ID is pulled and must not appear. The final phase removes `repo/refs/mirrors` before list, create, and delete operations to verify old-repo tolerance.

## State And Persistence
State is stored under normal heads and collection/mirror ref namespaces, remote config, local remote refs, and temporary remote repositories. Removing `refs/mirrors` simulates historical repository layout.

## Dependencies And Integration Points
This integrates ref storage, collection ID metadata, remote configuration, pull-created collection refs, and compatibility paths for missing mirror directories.

## Risks
Risks include leaking collection refs into plain output, deleting too broadly without `--collections`, failing on old repos, or showing remote refs for remotes without collection IDs. Ref namespace operations are especially sensitive to prefix matching.

## Test Signals
Two TAP results cover current repository behavior and old repository compatibility. Counts and regex matches verify exact ref visibility after each mutation.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-refs-collections.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-refs.sh -->
# sources/cloud-native/ostree/tests/test-refs.sh

## Purpose
This test covers the core `ostree refs` CLI: sorted listing, prefix filtering, revision output, deletion, creation, validation, local versus remote namespace handling, hidden file filtering, and alias symlink refs.

## Important APIs, Types, And Functions
It uses `setup_fake_remote_repo1`, `ostree commit`, `ostree refs`, `--list`, `--revision`, `--delete`, `--create`, `--force`, `-A` alias mode, `ostree rev-parse`, `ostree summary -u`, and fixture assertion helpers.

## Control Flow
The test commits refs under flat and nested names, checks sorted output and prefix behavior, verifies revision-paired listing, exercises safe no-op and explicit deletion, validates `--create` failure modes and forced replacement, ignores hidden `.spooky` files in ref directories, rejects invalid ref names, accepts names with `._-`, checks cleanup after failed creates, tests reuse of deleted directories, distinguishes remote-style `origin:` refs from local refs, and then creates alias symlinks from stable refs to versioned refs. It verifies alias resolution follows updated targets, alias swapping works, deletion of a target with aliases is rejected, and aliases to remote or nonexistent refs fail.

## State And Persistence
Persistent state includes `repo/refs/heads`, nested ref directories, remote-style refs, alias symlinks, summary output, and commits used to update target revisions. Hidden files are manually inserted to simulate external tooling artifacts.

## Dependencies And Integration Points
This integrates ref validation, filesystem-backed ref layout, symlink alias support, summary generation, revision resolution, and remote namespace parsing. It also depends on shell brace expansion and UTF-8 filesystem support for the hidden marker file.

## Risks
Ref operations can accidentally treat directories as refs, leave temp files after failed creation, overwrite prefixes, expose hidden files, allow invalid names, or break aliases after target updates. Alias deletion semantics guard against dangling stable refs.

## Test Signals
Seven TAP results cover hidden refs, invalid refs, valid character refs, general ref operations, symlink refs, remote alias rejection, and broken alias rejection. Failures are usually visible as count mismatches, unexpected `rev-parse` results, or expected stderr text not appearing.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-refs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-remote-add-collections.sh -->
# sources/cloud-native/ostree/tests/test-remote-add-collections.sh

## Purpose
This focused test verifies that `ostree remote add --collection-id` persists the remote collection ID in repository configuration.

## Important APIs, Types, And Functions
It uses `ostree_repo_init`, `ostree remote add`, `--collection-id`, `--gpg-import`, and `assert_file_has_content` against `repo/config`.

## Control Flow
The script creates an empty repo, adds `some-remote` with URL, collection ID `example-id`, and a GPG import key, then checks the config contains `collection-id=example-id`.

## State And Persistence
The primary persistent state is the remote stanza in `repo/config`, plus any trusted keyring state created by `--gpg-import`.

## Dependencies And Integration Points
This integrates remote configuration writing, option parsing, collection ID persistence, and GPG key import during remote add.

## Risks
A regression could silently drop collection IDs or write them under the wrong stanza, which would break collection-aware pulls and repo-finder behavior.

## Test Signals
The single TAP line `ok remote-add-collections` is emitted after matching the config line.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-remote-add-collections.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-remote-add.sh -->
# sources/cloud-native/ostree/tests/test-remote-add.sh

## Purpose
This shell test validates the `ostree remote` management CLI for adding, listing, showing URLs, deleting, inheriting parent repo remotes, duplicate handling, and forced replacement.

## Important APIs, Types, And Functions
It uses `setup_test_repository`, `$OSTREE remote add`, `remote show-url`, `remote list`, `remote list --show-urls`, `remote delete`, `--if-not-exists`, `--if-exists`, `--force`, `ostree config set core.parent`, and assertions from `libtest.sh`.

## Control Flow
The script sets up a bare test repo, adds a normal remote and a no-sign-verify remote, verifies duplicate addition fails, checks idempotent add with `--if-not-exists`, lists names without URLs and then with URLs, configures a parent repository with its own remote and verifies inherited listing, deletes existing and nonexistent remotes with and without `--if-exists`, confirms removed remotes cannot be shown, checks remaining names, rejects incompatible `--if-not-exists --force`, and finally overwrites a remote URL with `--force`.

## State And Persistence
State lives in `repo/config` and parent repo config. Deletion removes remote stanzas and `show-url` visibility. The test does not pull objects, so object storage is not central.

## Dependencies And Integration Points
This integrates the CLI remote parser, repository config writing, parent repository lookup, and remote list rendering. It depends on `$OSTREE` being preconfigured by the harness to target the test repo.

## Risks
Remote management can accidentally expose URLs in default listings, ignore parent remotes, fail to delete associated configuration, or allow conflicting flags. Forced replacement must update the URL without creating duplicate stanzas.

## Test Signals
The TAP plan has sixteen results, with regex checks on list output and stderr checks for failure paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-remote-add.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-remote-cookies.sh -->
# sources/cloud-native/ostree/tests/test-remote-cookies.sh

## Purpose
This test verifies remote HTTP cookie management and confirms pull requests send exactly the configured cookies expected by the test server.

## Important APIs, Types, And Functions
It uses `setup_fake_remote_repo1 --expected-cookies`, `ostree remote add-cookie`, `ostree remote delete-cookie`, `ostree pull`, and assertions against `repo/origin.cookies.txt`.

## Control Flow
The fake HTTP remote is configured to require `foo=bar` and `baz=badger`. A pull without cookies must fail. The test adds both cookies, confirms they are persisted, and verifies pull success. It deletes one cookie, checks the cookie file no longer contains it, and confirms pull failure. Finally it re-adds the removed cookie and confirms pull succeeds again.

## State And Persistence
Cookies are persisted in `repo/origin.cookies.txt`. Remote config stores the origin URL. Pull success depends on the cookie file being consumed by the HTTP fetch layer.

## Dependencies And Integration Points
This integrates remote cookie CLI operations, libsoup or curl HTTP request cookie handling, test webserver expected-cookie validation, and repo-local cookie persistence.

## Risks
Deleting one cookie must not remove unrelated cookies. Cookie domain/path matching must match the server address used in the test. Stale cookie files could create false positives if cleanup is incomplete.

## Test Signals
Four TAP results cover setup failure without cookies, initial cookie pull, delete failure, and second successful cookie pull.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-remote-cookies.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-remote-gpg-import.sh -->
# sources/cloud-native/ostree/tests/test-remote-gpg-import.sh

## Purpose
This comprehensive shell test validates remote GPG key import, per-remote trust isolation, `gpgkeypath` option parsing, signed commit pull verification, static-delta upgrade verification, and expired/revoked key handling.

## Important APIs, Types, And Functions
It uses `ostree remote add`, `remote gpg-import --keyring`, `--stdin`, `--gpg-import`, `ostree pull`, `ostree prune --refs-only`, remote config `gpgkeypath`, `ostree static-delta generate`, `ostree summary -u --gpg-sign`, `which_gpg`, and GPG commands such as `--quick-set-expire`, `--armor --export`, and revocation import.

## Control Flow
The test first ensures deleting a remote removes its `R1.trustedkeys.gpg` keyring. It imports selected keys, all keys, and stdin keys, checking import counts. It then creates three remotes pointing at the same URL but with distinct trusted keys, signs successive commits with key1, key2, and key3, and verifies only the matching remote can pull each commit. A large matrix validates `gpgkeypath` with files, directories, multiple comma or semicolon-separated paths, missing paths, empty path elements, and mixed separators. Static delta pulls are tested to ensure commit signatures are checked even when the summary signature is trusted. If GPG is available, expired and revoked key material is imported and pulls must fail with `Key expired` or `Key revoked`.

## State And Persistence
Per-remote keyrings such as `repo/R1.trustedkeys.gpg`, repo config `gpgkeypath` values, remote commits and deltas, summary signatures, refs/remotes cleanup, and generated key files under `test_tmpdir` are central persistent states.

## Dependencies And Integration Points
This integrates GPGME verification, external GPG for key mutation, remote config parsing, static delta pull path, commit metadata signatures, and keyring lifecycle during remote delete. It depends on fixture keys from `gpghome`.

## Risks
Key trust must remain per remote. `gpgkeypath` parser bugs can either reject valid deployments or silently ignore missing/untrusted keys. Delta upgrades must not bypass commit signature verification. External GPG version differences can affect expired/revoked handling.

## Test Signals
The non-GPG test plan covers import and pull trust behavior; extra tests cover expired and revoked keys. Expected failures include `public key not found`, missing path errors, mixed-separator parser errors, `Key expired`, and `Key revoked`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-remote-gpg-import.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-remote-gpg-list-keys.sh -->
# sources/cloud-native/ostree/tests/test-remote-gpg-list-keys.sh

## Purpose
This test validates formatted key listing for remote-specific and global GPG keyrings, including update URLs, subkeys, expiration, and revocation markers.

## Important APIs, Types, And Functions
It uses `OSTREE_GPG_HOME`, `ostree remote gpg-list-keys`, `remote gpg-import --keyring`, fixture key IDs, `which_gpg`, GPG expiration and revocation commands, and exact expected output blocks.

## Control Flow
The script isolates most tests from global keyrings by setting `OSTREE_GPG_HOME` to an empty directory. It checks that an empty remote keyring lists no keys, that global keys do not appear for a specific remote, imports key1 into remote `R1` and compares exact listing output, checks global no-key and global trusted-key output, then conditionally uses GPG to expire and revoke key1 and verifies the listing marks those statuses.

## State And Persistence
State lives in repo-local remote keyrings, global trusted keyring path referenced by `OSTREE_GPG_HOME`, and temporary exported expired/revoked key files.

## Dependencies And Integration Points
This integrates GPG keyring parsing, output formatting, OpenPGP key metadata, Web Key Directory URL rendering, subkey listing, and status propagation from imported key material.

## Risks
The test is intentionally exact about output and timezone (`TZ=UTC`), so formatting changes are breaking. GPG version differences around revocation import are handled by accepting status 0 or 2 in one helper.

## Test Signals
The TAP plan has five non-GPG and two GPG-dependent results. Exact `assert_files_equal` blocks catch changes in key order, dates, UIDs, update URLs, subkeys, and revoked annotations.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-remote-gpg-list-keys.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-remote-headers.sh -->
# sources/cloud-native/ostree/tests/test-remote-headers.sh

## Purpose
This test verifies that `ostree pull` sends caller-specified HTTP headers and appends a custom user-agent suffix to the default libostree user agent.

## Important APIs, Types, And Functions
It uses `skip_without_ostree_httpd`, `ostree --version` parsed with Python YAML, `setup_fake_remote_repo1 --expected-header`, `ostree pull --http-header`, and `--append-user-agent`.

## Control Flow
The script computes the current libostree version, starts a fake remote that expects `foo=bar`, `baz=badger`, and `User-Agent=libostree/$V dodo/2.15`, creates a client repo, and adds the remote. It verifies pulls fail with no headers and with missing or wrong user-agent suffix, then succeeds when both custom headers and the expected appended user agent are supplied.

## State And Persistence
The only persistent repository state is the remote configuration and pulled objects after the successful final pull. Header expectations live in the temporary HTTP server process.

## Dependencies And Integration Points
This integrates HTTP request configuration, user-agent construction, CLI option parsing, version reporting, and the test server's request validation.

## Risks
Header handling can drop duplicates, override user-agent incorrectly, or fail to combine the default agent with the appended suffix. Version parsing depends on the YAML structure of `ostree --version`.

## Test Signals
Two TAP results cover failed setup cases and successful pull. Expected failures are enforced by `assert_fail`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-remote-headers.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-remote-refs.sh -->
# sources/cloud-native/ostree/tests/test-remote-refs.sh

## Purpose
This test validates `ostree remote refs` output and `--revision` output against a known remote summary.

## Important APIs, Types, And Functions
It uses `setup_fake_remote_repo2`, `ostree summary -u`, `ostree refs`, `ostree refs --revision`, `ostree remote add --no-sign-verify`, `ostree remote refs`, and `ostree remote refs --revision`.

## Control Flow
The script creates a fake archive remote, regenerates its summary, captures local remote ref listings and ref-to-revision listings, initializes a client archive repo, adds the HTTP remote, then compares `remote refs origin` with the captured list prefixed by `origin:`. It repeats the comparison for `--revision`.

## State And Persistence
The remote summary and refs are persisted in the fake server repo. The client stores only remote configuration for listing; no pull is required.

## Dependencies And Integration Points
This integrates remote summary fetching/parsing, ref rendering, remote prefix formatting, and revision output ordering.

## Risks
Remote ref listing must match local listing semantics while adding remote prefixes. Ordering or whitespace changes can break exact comparisons.

## Test Signals
Two TAP results cover plain remote refs and revisions. `assert_files_equal` catches any output mismatch.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-remote-refs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-remotes-config-dir.js -->
# sources/cloud-native/ostree/tests/test-remotes-config-dir.js

## Purpose
This GJS test validates the libostree `Ostree.Repo` `remotes_config_dir` behavior, including reading external remote config files, deciding where new remotes are written, deleting external remotes, and replacing remote options.

## Important APIs, Types, And Functions
It imports `GLib`, `Gio`, and `OSTree`. Key APIs include `GLib.KeyFile`, `OSTree.Repo({path, remotes_config_dir})`, `repo.create`, `repo.open`, `remote_list`, `remote_add`, `remote_delete`, `copy_config`, `write_config`, `reload_config`, `remote_get_gpg_verify`, and `remote_change` with `OSTree.RepoRemoteChange.REPLACE`.

## Control Flow
The script creates `remotes.d/foo.conf`, opens a repo configured with that directory, and confirms `foo` is visible. It adds `bar` and confirms it is stored in the main config rather than `remotes.d`. Deleting `foo` removes its config file. After enabling `core.add-remotes-config-dir`, adding `baz` writes `baz.conf`. It verifies changing main-config remote `bar` through `write_config()` succeeds, while changing config-dir remote `baz` through `write_config()` fails with `G_IO_ERROR_EXISTS`. It then replaces a missing remote and existing config-dir and main-config remotes, confirming old `branches` options are removed.

## State And Persistence
State is split between the main repo config and files under `remotes.d/*.conf`. The test checks actual file existence and key file contents to validate persistence location.

## Dependencies And Integration Points
This integrates GObject introspection bindings, libostree remote config loading, config-dir precedence, config write safety, and remote replacement semantics.

## Risks
The main risks are accidentally writing external remotes into the wrong config, allowing `write_config()` to overwrite config-dir-owned remotes, or retaining stale options during replace. GPG support is optional for one check and produces a TAP skip when unsupported.

## Test Signals
Nine TAP-style printed `ok` lines cover reading, adding, deleting, write-config behavior, replace of missing remote, and replace in both config-dir and main config.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-remotes-config-dir.js -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-repo-finder-avahi.c -->
# sources/cloud-native/ostree/tests/test-repo-finder-avahi.c

## Purpose
This C unit test validates basic construction of `OstreeRepoFinderAvahi` and private Avahi TXT-record parsing used for peer repository discovery.

## Important APIs, Types, And Functions
The file includes `ostree-repo-finder-avahi-private.h` and tests `ostree_repo_finder_avahi_new()` and `_ostree_txt_records_parse()`. It uses `AvahiStringList`, `GHashTable`, `GBytes`, GLib test APIs, and autoptr cleanup for `AvahiStringList`.

## Control Flow
`test_repo_finder_avahi_init()` constructs the finder with default and explicit `GMainContext`. TXT record tests build Avahi string lists from byte vectors, call `_ostree_txt_records_parse()`, and verify accepted keys, binary values, empty values, missing values, duplicate-first behavior, and case-insensitive key normalization.

## State And Persistence
There is no persistent state. All data is in-memory Avahi TXT lists and hash tables. The finder constructor may hold a main context but no network discovery is exercised.

## Dependencies And Integration Points
This integrates GLib, GObject, Avahi TXT string structures, and private OSTree Avahi repo-finder parsing. It is a unit-level guard for DNS-SD service metadata consumed by broader repo discovery.

## Risks
TXT parsing must reject malformed records, lowercase keys consistently, preserve first duplicate values per RFC 6763, and distinguish missing values from empty byte strings. The test explicitly notes that service processing itself still lacks coverage.

## Test Signals
GLib test paths include `/repo-finder-avahi/init`, `/txt-records/parse`, `/duplicates`, `/case-sensitivity`, and `/empty-and-missing`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-repo-finder-avahi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-repo-finder-config.c -->
# sources/cloud-native/ostree/tests/test-repo-finder-config.c

## Purpose
This C unit test validates `OstreeRepoFinderConfig`, which resolves collection refs using configured remotes and their summaries. It also validates the higher-level `ostree_repo_find_remotes_async()` wrapper.

## Important APIs, Types, And Functions
Important types include `Fixture`, `OstreeRepo`, `OstreeRepoFinderConfig`, `OstreeCollectionRef`, `OstreeRepoFinderResult`, `GMainContext`, and `GAsyncResult`. Helpers include `setup`, `teardown`, `result_cb`, `assert_create_remote_config`, and variadic `assert_create_remote`. Tested APIs include `ostree_repo_finder_resolve_async/finish`, `ostree_repo_find_remotes_async/finish`, `ostree_repo_remote_add`, `ostree_repo_regenerate_summary`, and ref-setting APIs.

## Control Flow
The fixture creates a tempdir and parent repo. `no_configs` resolves two refs with no remotes and expects no results. `mixed_configs` creates collection and non-collection remote repos, configures valid, duplicate, mismatched, and no-collection remotes, resolves five collection refs, and asserts only valid collection-matching results remain. `find_remotes` repeats the scenario through `ostree_repo_find_remotes_async()` and additionally validates checksum strings and big-endian timestamps for requested and missing refs.

## State And Persistence
Temporary remote repositories are created with summaries, refs, collection IDs, commits, and remote config in the parent repo. Cleanup removes both the tempdir and harness-created parent repo source files.

## Dependencies And Integration Points
This integrates libglnx tempdirs, GLib async main-context iteration, repository summary generation, collection ref lookup, remote configuration, and result deduplication/canonicalization.

## Risks
Config finder results must ignore remotes whose configured collection ID does not match the remote summary, avoid non-collection remotes for collection refs, keep duplicates deterministic, and preserve checksum/timestamp maps for all queried refs. Async completion must happen on the expected context.

## Test Signals
GLib paths are `/repo-finder-config/init`, `/no-configs`, `/mixed-configs`, and `/find-remotes`. Result lengths, ref hash-table membership, checksum validation, and timestamp values are primary assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-repo-finder-config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-repo-finder-mount-integration.sh -->
# sources/cloud-native/ostree/tests/test-repo-finder-mount-integration.sh

## Purpose
This shell integration test exercises repo-finder mount behavior against a real disposable USB block device formatted as ext4 and vfat. It validates `ostree create-usb`, mount-based `find-remotes`, pull from discovered media, and cross-filesystem consistency.

## Important APIs, Types, And Functions
It uses `skip_without_sudo`, `MOUNT_INTEGRATION_DEV`, `mkfs.ext4`, `mkfs.vfat`, `udisksctl mount`, `ostree_repo_init --collection-id`, `ostree commit --gpg-sign`, `ostree summary --update`, `ostree remote add --collection-id --gpg-import`, `ostree pull`, `ostree create-usb`, `ostree find-remotes --finders=mount`, `find-remotes --pull`, and `diff -ur`.

## Control Flow
The script skips unless sudo is available and `MOUNT_INTEGRATION_DEV` names an unmounted block device. It creates a signed collection repo with five refs, pulls all refs into `local-repo`, then loops over ext4 and vfat. For each filesystem it reformats the device, mounts it through udisks, writes only `test-1` and `test-2` to the USB repo with `create-usb`, validates refs and summary on the mounted media, initializes a peer repo with only the collection keyring, discovers `test-1` through `find-remotes --finders=mount`, pulls it through the same finder, verifies the collection ref exists locally, and unmounts. Finally it diffs the ext4 and vfat peer repos.

## State And Persistence
State includes the real block device contents, mounted USB `.ostree/repo`, collection refs, summaries, GPG-signed commits, keyrings in local and peer repos, and peer repositories `peer-repo_ext4` and `peer-repo_vfat`. Cleanup unmounts the configured device unless cleanup is explicitly skipped.

## Dependencies And Integration Points
This integrates shell fixture setup, sudo, udisks, mkfs tools, removable-media discovery through GIO, collection-aware repo discovery, `create-usb`, GPG keyring resolution, and pull/find-remotes behavior.

## Risks
The test is intentionally destructive to `MOUNT_INTEGRATION_DEV`, so the mounted-device guard is critical. Host dependencies are heavy and can cause skips or flakes. ext4 ownership options and vfat semantics differ, so identical peer repos are the final cross-filesystem guard.

## Test Signals
The TAP plan has three results: end-to-end USB on ext4, end-to-end USB on vfat, and identical peer repositories. It also checks discovery output contains the USB file URI and the exact checksum for `test-1`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-repo-finder-mount-integration.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-repo-finder-mount.c -->
# sources/cloud-native/ostree/tests/test-repo-finder-mount.c

## Purpose
This C unit test validates `OstreeRepoFinderMount`, which discovers OSTree repositories on mounted volumes, including `.ostree/repos.d`, well-known repo paths, symlink aliases, collection filtering, and keyring mapping.

## Important APIs, Types, And Functions
Key types include `Fixture`, `OstreeRepoFinderMount`, `GVolumeMonitor`, mock `GMount` objects from `test-mock-gio.h`, `OstreeCollectionRef`, and `OstreeRepoFinderResult`. Helpers include `assert_create_repos_dir`, `assert_create_remote_va`, `assert_create_repo_dir`, `assert_create_repo_symlink`, and `assert_create_remote_config`. Tested APIs include `ostree_repo_finder_mount_new()` and `ostree_repo_finder_resolve_async/finish()`.

## Control Flow
The init test constructs the finder with default and mock monitors. The no-mount test resolves refs with an empty monitor and expects no results. The mixed-mount test creates non-removable, empty, and repository-bearing mock mounts, adds repos and symlinks under `.ostree/repos.d`, configures parent remotes for selected collection IDs, resolves six refs, and checks four canonicalized results with correct URI, keyring, checksum maps, and ignored unsafe/dangling symlinks. The well-known test creates repos at `ostree/repo` and `.ostree/repo` and verifies both are discovered and deduplicated.

## State And Persistence
Temporary mount roots, repository directories, summaries, symlinks, parent remote config, and generated commit checksums are persisted under a tempdir. Cleanup removes tempdir and parent repo fixture files.

## Dependencies And Integration Points
This integrates libglnx, GLib async machinery, mock GIO volume/mount classes, OSTree remote internals, collection refs, keyring resolution for collections, summary generation, and path canonicalization.

## Risks
Mount discovery must avoid non-removable media when appropriate, ignore repos not matching configured collections, handle aliases without duplicate results, reject dangling and out-of-mount symlinks, and map collection IDs to the correct remote keyring. GPG-disabled builds skip the collection/keyring heavy tests.

## Test Signals
GLib paths include `/repo-finder-mount/init`, `/no-mounts`, `/mixed-mounts`, and `/well-known` when GPGME is enabled. Result count and checksum/keyring assertions are the core validation.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-repo-finder-mount.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-repo.c -->
# sources/cloud-native/ostree/tests/test-repo.c

## Purpose
This C unit test validates selected `OstreeRepo` object APIs: hashing/equality, min-free-space config parsing, inline regular file and symlink writing, autolock cleanup, recursive locking, lock misuse assertions, and inter-repo/thread lock conflict behavior.

## Important APIs, Types, And Functions
Important functions include `ostree_repo_create_at`, `ostree_repo_open_at`, `ostree_repo_hash`, `ostree_repo_equal`, `ostree_repo_copy_config`, `ostree_repo_write_config`, `ostree_repo_reload_config`, `ostree_repo_get_min_free_space_bytes`, `ostree_repo_write_regfile_inline`, `ostree_repo_write_symlink`, `ostree_repo_auto_lock_push`, `ostree_repo_lock_push`, and `ostree_repo_lock_pop`. The `Fixture` owns a `GLnxTmpDir`; `LockThreadData` coordinates the multithread test.

## Control Flow
Setup creates temporary repos. Hash and equality tests compare open repo objects, aliases, different repos, and closed repos. Min-free-space tests write valid and overflow config values and reload the repo. Write API tests write fixed regular-file contents with and without SELinux xattrs, reject an invalid expected checksum, and write a symlink with xattrs while checking exact object checksums. Lock tests cover RAII autolock, recursive lock push/pop on a single repo, subprocess assertion failures for invalid unlocks, conflict behavior between two repo handles, and multithread sequencing where exclusive locks block other handles until dropped.

## State And Persistence
Temporary archive repositories, config files, content objects, xattrs encoded in object metadata, symlink objects, and lock files are created under the tempdir. Subprocess tests intentionally fail to validate assertions.

## Dependencies And Integration Points
This integrates GLib testing, GObject repo identity, libglnx tempdir cleanup, object checksum generation, xattr metadata encoding, and file-lock semantics across repo instances and threads.

## Risks
Hash/equality must not claim equality for closed repos. Config parsing must detect integer overflow. Write APIs must keep checksum stability for xattrs and content. Lock recursion and cross-handle blocking are subtle, especially with shared versus exclusive modes and misuse diagnostics.

## Test Signals
GLib paths include `/repo/hash`, `/hash/closed`, `/equal`, `/get_min_free_space`, `/write_regfile_api`, `/autolock`, and six lock tests. Expected assertion stderr is part of the negative test contract.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-repo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-reset-nonlinear.sh -->
# sources/cloud-native/ostree/tests/test-reset-nonlinear.sh

## Purpose
This small shell test verifies `ostree reset` can reset a branch to a non-linear commit from another branch.

## Important APIs, Types, And Functions
It uses `setup_test_repository "archive"`, `$OSTREE commit -b testx`, and `$OSTREE reset test2 testx`.

## Control Flow
The script creates an archive repository fixture, commits a new branch `testx` from the files directory, returns to the tempdir, and resets `test2` to point at `testx`.

## State And Persistence
Branch refs `testx` and `test2` are modified in the temporary repository. Objects from the fixture and new commit persist until cleanup.

## Dependencies And Integration Points
This integrates ref reset behavior with commit graph ancestry rules. It ensures reset does not require the target commit to be a descendant of the original branch.

## Risks
If reset incorrectly enforces linear history, administrative workflows that repoint refs to unrelated commits would fail.

## Test Signals
The single TAP result `ok reset nonlinear` is printed after the reset succeeds.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-reset-nonlinear.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-rfc2616-dates.c -->
# sources/cloud-native/ostree/tests/test-rfc2616-dates.c

## Purpose
This C unit test validates private RFC 2616 HTTP date parsing used by OSTree date utilities.

## Important APIs, Types, And Functions
It tests `_ostree_parse_rfc2616_date_time()` from `ostree-date-utils-private.h` and uses `GDateTime`, `g_date_time_format_iso8601`, GLib version guards, and GLib test APIs.

## Control Flow
For GLib 2.62 or newer, the test loops over valid and invalid date strings. Each string is parsed once as a normal NUL-terminated buffer and once as a same-length non-NUL-terminated buffer. Valid dates are formatted to ISO 8601 and compared; invalid ones must return `NULL`. Older GLib versions skip because ISO formatting is unavailable.

## State And Persistence
There is no persistent state. All parsing happens in memory.

## Dependencies And Integration Points
This integrates OSTree's HTTP date parser with GLib date-time validation. It covers strict GMT-only HTTP-date format used by HTTP caching and summary freshness code.

## Risks
Date parsing must reject malformed separators, invalid weekdays/months, overlong fields, underflow/overflow values, and non-GMT timezones. Handling non-NUL buffers is important for parsing byte ranges from network responses.

## Test Signals
The GLib test path is `/ostree_parse_rfc2616_date_time`. It validates boundary dates `1970-01-01T00:00:00Z` and `9999-12-31T23:59:59Z` plus many invalid variants.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-rfc2616-dates.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-rofiles-fuse.sh -->
# sources/cloud-native/ostree/tests/test-rofiles-fuse.sh

## Purpose
This integration test validates `rofiles-fuse` read-only checkout behavior, allowed creation of new mutable files, deletion, commit-back behavior, hardlink fallback, flock creation, copyup mode, xattr changes, symlink handling, and optional fsverity copyup.

## Important APIs, Types, And Functions
It uses `skip_without_fuse`, `skip_without_user_xattrs`, `setup_test_repository`, `rofiles-fuse`, `fusermount`, `ostree checkout -H/-U/-UH`, `ostree commit --link-checkout-speedup`, `setfattr`, `getfattr`, `flock`, `fsverity enable`, and helper functions `copyup_reset` and `assert_test_file`.

## Control Flow
The test creates a hardlink checkout, mounts it through `rofiles-fuse`, confirms existing content is readable, verifies truncation/chmod/chown/xattr mutation of existing read-only files fails, creates new files and directories through the mount, writes through a new symlink, sets xattrs, deletes existing files/dirs, commits the modified checkout, and verifies checkout copy fallback across the FUSE mount. It then remounts with `--copyup` several times to test truncation, xattr changes, writes through symlinks preserving symlink identity, new-file creation plus `sed -i` rename behavior, and fsverity-enabled copyup when supported.

## State And Persistence
State spans the OSTree repo, hardlink checkout `checkout-test2`, FUSE mount `mnt`, xattrs, deleted paths, new files, copied-up replacement inodes, and optional fsverity metadata. Cleanup unmounts the FUSE mount through an exit hook.

## Dependencies And Integration Points
This integrates FUSE, rofiles-fuse, checkout hardlink/copy modes, xattr tools, chown/chmod errors, commit link speedups, flock, sed rename behavior, and fsverity if available.

## Risks
Read-only existing files must not be mutated unless copyup mode is active. Copyup must replace regular file inodes while preserving symlink objects. Cross-device hardlink checkout must fall back or fail clearly. FUSE cleanup and host feature availability are common flake risks.

## Test Signals
Thirteen TAP results cover mount, failed mutations, new content, xattrs, deletion, commit, checkout fallback, flock, copyup mount, copyup behavior, and optional fsverity copyup skip/pass.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-rofiles-fuse.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-rollsum-cli.c -->
# sources/cloud-native/ostree/tests/test-rollsum-cli.c

## Purpose
This small C helper is a CLI for manually computing OSTree rollsum matches between two files. It is primarily a test/debug executable rather than a GLib TAP test.

## Important APIs, Types, And Functions
It uses `g_mapped_file_new`, `g_mapped_file_get_bytes`, `_ostree_compute_rollsum_matches()`, `OstreeRollsumMatches`, and prints `crcmatches`, `bufmatches`, `total`, and `match_size`.

## Control Flow
The program requires two path arguments, maps both files read-only into `GBytes`, computes rollsum matches, prints summary metrics to stderr, and returns nonzero on missing args or file mapping errors.

## State And Persistence
No persistent state is written. The program maps input files and allocates match structures in memory.

## Dependencies And Integration Points
This integrates the private rollsum implementation with simple file inputs. It sets `GIO_USE_VFS=local` to avoid non-local VFS behavior in tests.

## Risks
The helper does not free `matches` explicitly in the visible path, but process exit bounds leak impact. It assumes mapped files fit address space and only reports aggregate metrics, not detailed matches.

## Test Signals
Successful execution prints a line beginning `rollsum crcs=`. Errors print the GLib error message and exit with status 1.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-rollsum-cli.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-rollsum.c -->
# sources/cloud-native/ostree/tests/test-rollsum.c

## Purpose
This C unit test validates OSTree's rolling checksum matching and bupsplit checksum helper, including collision safety and randomized buffer scenarios.

## Important APIs, Types, And Functions
It uses `_ostree_compute_rollsum_matches()`, `_ostree_rollsum_matches_free()`, `OstreeRollsumMatches`, `bupsplit_find_ofs`, `bupsplit_sum`, `GBytes`, `GVariant` match tuples `(uttt)`, and GLib random/test utilities.

## Control Flow
`test_rollsum_helper()` computes matches for two buffers, checks whether matches are expected, iterates match variants, validates offsets, source/target bounds, byte equality for matched ranges, and `match_size` accounting. `test_rollsum()` checks known CRC32 collision buffers should not match, identical large random buffers should match, modified chunk-boundary buffers should retain matches, duplicated chunks should match, and fully different buffers should not. `test_bupsplit_sum()` checks sums are invariant across window-offset cases.

## State And Persistence
All buffers and match arrays are in memory. No files are written.

## Dependencies And Integration Points
This integrates rollsum, bupsplit chunking, GLib `GBytes`, and bsdiff/bspatch headers included by the test build. It guards static delta diffing and content deduplication internals.

## Risks
CRC collisions must be rejected by byte comparison. Offset and match-size accounting can overflow or point outside buffers if rollsum logic is wrong. Randomized tests may be expensive but cover realistic large data.

## Test Signals
GLib test paths `/rollsum` and `/bupsum` fail on unexpected match counts, invalid offsets, mismatched bytes, or sum invariants.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-rollsum.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-signed-commit-dummy.sh -->
# sources/cloud-native/ostree/tests/test-signed-commit-dummy.sh

## Purpose
This TAP shell test validates the opt-in dummy signing backend for commit signing and verification.

## Important APIs, Types, And Functions
It sets `OSTREE_DUMMY_SIGN_ENABLED=1` and uses `ostree commit`, `ostree sign --sign-type=dummy`, `ostree sign --verify`, `ostree show --print-detached-metadata-key=ostree.sign.dummy`, `hexdump`, and TAP helpers.

## Control Flow
The script creates an archive repo, commits an unsigned commit, signs it with dummy key `dummysign`, checks detached metadata contains the expected encoded string, verifies the signature, creates a new commit signed during commit creation, verifies it, then unsets the dummy opt-in environment and confirms verification fails with no valid signatures.

## State And Persistence
Detached commit metadata stores `ostree.sign.dummy` signatures. The repo and commits live in `test_tmpdir`.

## Dependencies And Integration Points
This integrates sign CLI commands, commit-time signing, detached metadata, the dummy backend, and environment-gated availability for test-only signing.

## Risks
Dummy signing must remain disabled by default. Detached metadata must be correctly written and read. Error text is noted as imperfect, so the test checks the stable "No valid signatures found" portion.

## Test Signals
TAP helpers report detached signature added, dummy signature verified, commit with dummy signing, and dummy signature requiring the environment variable.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-signed-commit-dummy.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-signed-commit-ed25519.sh -->
# sources/cloud-native/ostree/tests/test-signed-commit-ed25519.sh

## Purpose
This shell test validates the ed25519 signing backend for commit-time signing, detached signing, multi-backend signatures, key files, keys directories, and revocation.

## Important APIs, Types, And Functions
It uses `gen_ed25519_keys`, `gen_ed25519_random_public`, `ostree commit --sign --sign-type=ed25519`, `ostree sign --verify`, `--keys-file`, `--keys-dir`, dummy signing for multi-sign tests, and trusted/revoked directory naming `trusted.ed25519.d` and `revoked.ed25519.d`.

## Control Flow
The test generates an ed25519 keypair, signs a commit at commit time, verifies detached metadata exists, and checks verification fails with a wrong key but succeeds with the correct key among many positional keys. It creates an unsigned commit, signs it with both dummy and ed25519 backends, and verifies both outputs. It then tests empty and invalid keys-file behavior, a single-key file, a 100-key invalid file, combining file and positional key, adding the valid key to the file, signing from a secret key file, verifying from a keys file, verifying keys discovered from a trusted directory, and rejecting once the public key is present in the revoked directory.

## State And Persistence
State includes commit metadata signatures, temporary public/secret key files, trusted and revoked ed25519 directories, and random public-key lists.

## Dependencies And Integration Points
This integrates libsodium-backed ed25519 support, the sign CLI, commit metadata, key-file parsing, key-directory discovery, revocation precedence, and dummy backend coexistence.

## Risks
Verification must try multiple keys without accepting wrong keys, report useful counts for large key files, handle file/directory errors, and prioritize revocation over trust. Secret-key file handling must not confuse public and private formats.

## Test Signals
TAP results cover detached signature creation, verification, multiple signing, keys-file verification, signing with a keys file, trusted directory verification, and revocation rejection.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-signed-commit-ed25519.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-signed-commit-spki.sh -->
# sources/cloud-native/ostree/tests/test-signed-commit-spki.sh

## Purpose
This shell test mirrors the ed25519 signing tests for the SPKI signing backend, including PEM file handling, multi-backend signing, key files, key directories, and revocation.

## Important APIs, Types, And Functions
It uses `gen_spki_keys`, `gen_spki_random_public`, `gen_spki_random_public_pem`, `ostree commit --sign-type=spki`, `ostree sign --verify --sign-type=spki`, `--keys-file`, `--keys-dir`, dummy signing, and `trusted.spki.d`/`revoked.spki.d`.

## Control Flow
The script generates SPKI key material, signs a commit, checks detached metadata, verifies failure with wrong public key and success with correct key in several argument positions, signs another commit with dummy and SPKI signatures, validates empty and invalid keys-file behavior, tests a PEM public key file, a 100-key invalid PEM list, adding the valid PEM key, signing with a PEM secret key file, verifying trusted directory discovery, and rejecting after adding the key to the revoked directory.

## State And Persistence
State includes SPKI detached metadata, PEM public/secret temp files, random key lists, trusted and revoked SPKI directories, and the test repository.

## Dependencies And Integration Points
This integrates the SPKI signing backend, PEM parsing, sign CLI, detached metadata, multi-signature coexistence, and directory-based trust/revocation.

## Risks
PEM parsing and binary/string key formats can diverge from ed25519 behavior. The verification path must count attempted keys correctly, reject wrong keys, and make revoked keys invalid even when trusted.

## Test Signals
TAP results match the ed25519 structure: detached SPKI signature, verification, multiple signing, keys-file verification, secret-file signing, trusted directory verification, and revocation.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-signed-commit-spki.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-signed-pull-summary.sh -->
# sources/cloud-native/ostree/tests/test-signed-pull-summary.sh

## Purpose
This shell test validates summary signing and signed-summary pulls through non-GPG signing backends, currently dummy and ed25519, including cache behavior and race recovery.

## Important APIs, Types, And Functions
It uses `OSTREE_DUMMY_SIGN_ENABLED`, `gen_ed25519_keys`, `setup_fake_remote_repo1`, `ostree commit --sign-type`, `ostree summary -u --sign-type --sign`, remote config keys `sign-verify-summary`, `verification-<engine>-key`, `ostree pull --mirror`, `--cache-dir`, `ostree prune`, `ostree static-delta generate`, `ostree remote summary`, and `OSTREE_REPO_TEST_ERROR=invalid-cache`.

## Control Flow
For each engine, the script creates a signed multi-branch remote, confirms mirror pull works with signature verification disabled, then enables summary sign verification with the public key and tests normal pulls, cache refill, prune of stale cache entries, external cache directories, invalid signature rejection, and static-delta pull. If ed25519 support exists, it additionally checks `remote summary` metadata output and models cache races using old/new summary-signature pairs, ensuring mismatched pairs do not replace the last good cache and a later valid pair recovers.

## State And Persistence
State includes signed commit metadata, signed `summary.sig`, client summary caches, external cache directories, static delta metadata, and copied `summary.1`/`summary.2` race fixtures.

## Dependencies And Integration Points
This integrates signapi summary verification, non-GPG signature storage in `summary.sig`, pull caching, static delta metadata, remote summary rendering, and invalid-cache test injection. Ed25519 portions depend on the `sign-ed25519` feature.

## Risks
Non-GPG summary verification must not be confused with GPG verification flags. Cache update ordering must avoid persisting mismatched summary/signature pairs. The script has a subtle dependency on the `engine` variable after the loop for ed25519-only scenarios.

## Test Signals
The TAP plan is fourteen, with skips for missing ed25519 support. Expected failures include `No signatures found`, ed25519 verification errors, and `OSTREE_REPO_TEST_ERROR_INVALID_CACHE`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-signed-pull-summary.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-signed-pull.sh -->
# sources/cloud-native/ostree/tests/test-signed-pull.sh

## Purpose
This test validates commit signature verification during pulls using the signapi dummy and ed25519 backends, including remote configuration parsing, missing key failures, inline key options, re-pulling missing commit metadata, and invalid sign-verify arguments.

## Important APIs, Types, And Functions
It uses `setup_fake_remote_repo1`, `ostree remote add` with `--set` and `--sign-verify=...`, `ostree config set/unset`, `ostree commit --sign` or `--sign-from-file`, `ostree summary -u`, `ostree pull --depth=0`, `repo_init`, and helper `test_signed_pull`.

## Control Flow
`repo_init` recreates the client repo with GPG verification disabled and summary sign verification disabled. `test_signed_pull` creates a signed remote commit, temporarily removes its remote `.commitmeta` file to ensure pull fails without signature metadata, restores it, pulls successfully, deletes the local `.commitmeta`, and pulls again to ensure signatures for stored commits are refetched. The dummy section checks failures with no keys, wrong keys, bad key file, correct config key, inline remote option, explicit sign type, missing configured keys, unknown sign type, and invalid remote-add sign-verify syntax. If ed25519 support exists, it signs from a secret file and verifies using config key, config file with wrong keys plus correct key, file-only correct key, and inline key option.

## State And Persistence
State includes remote and local commit metadata object files, remote config keys such as `sign-verify` and `verification-dummy-key`, temporary ed25519 key files, refs, summaries, and pulled objects.

## Dependencies And Integration Points
This integrates signapi pull verification, remote option parser, commit metadata fetching, summary refresh, dummy backend gating, and optional ed25519 support.

## Risks
Pull must not accept signed commits without trusted keys or without commit metadata. Re-pulling metadata for already stored commits is easy to miss because object content is already present. Inline option parsing must reject unknown systems and malformed key references.

## Test Signals
The TAP plan has twenty results with ed25519 skips when unavailable. Expected failure messages include missing keys, unknown sign type, invalid key reference, and no-signature pull failure.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-signed-pull.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-sizes.js -->
# sources/cloud-native/ostree/tests/test-sizes.js

## Purpose
This GJS test validates generation and encoding of `ostree.sizes` commit metadata when committing with `OSTree.RepoCommitModifierFlags.GENERATE_SIZES`.

## Important APIs, Types, And Functions
It uses GJS imports `GLib`, `Gio`, and `OSTree`; helper functions `readVarint`, `unpackByteArray`, and `validateSizes`; APIs `Repo.create/open`, `RepoCommitModifier.new`, `prepare_transaction`, `write_directory_to_mtree`, `write_mtree`, `write_commit`, `commit_transaction`, `load_variant`, and checksum/object formatting helpers.

## Control Flow
The script creates test files, a duplicate, a symlink, and another file, then commits them into an archive-z2 repo with size generation, canonical permissions, and skipped xattrs. `validateSizes` loads the commit variant, reads `ostree.sizes`, decodes each entry as checksum bytes, compressed varint, uncompressed varint, and object type, and compares exact expected sizes. It then deletes one file, updates expected objects and dirtree checksum, commits again, validates sizes, and repeats the same commit with cached objects to ensure metadata is still correct.

## State And Persistence
Persistent state includes the test data directory, archive-z2 object store, three commits, and `ostree.sizes` metadata in commit objects. The expected object map stores exact compressed and uncompressed sizes.

## Dependencies And Integration Points
This integrates GJS bindings, commit modifiers, varint encoding, archive-z2 compression, checksum/object naming, symlink object handling, duplicate object reuse, and commit metadata loading.

## Risks
Exact compressed sizes can change if compression, object serialization, or canonical permissions change. Metadata must be regenerated per commit rather than reused from cached objects, especially after deletion and repeated commits.

## Test Signals
Three printed TAP lines cover initial sizes, file-deleted sizes, and repeated cached-object sizes. Any mismatch throws a JS error with object and size details.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-sizes.js -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-summary-collections.sh -->
# sources/cloud-native/ostree/tests/test-summary-collections.sh

## Purpose
This test validates collection-aware summary generation and summary view output for local collection refs, mirrored collection refs, and pulled remote collection refs.

## Important APIs, Types, And Functions
It uses `ostree_repo_init --collection-id`, `ostree commit`, `ostree summary --update`, `ostree summary --view`, `ostree refs --collections --create`, `ostree remote add --collection-id`, and `ostree pull`.

## Control Flow
The script creates a collection-enabled repo with five commits, updates the summary, and checks all refs are shown with the repo collection ID and that the summary collection ID metadata is present. It creates a mirrored collection ref under another collection and verifies it appears. It then pulls from a remote with a collection ID and confirms that ref appears in summary view, then pulls from a remote without a collection ID and verifies that ref is omitted.

## State And Persistence
State includes local collection refs, mirror refs, remote refs, summary metadata, and temporary collection/no-collection remote repos.

## Dependencies And Integration Points
This integrates summary generation, collection ID metadata, collection ref namespace, remote pull behavior, and summary human-readable rendering.

## Risks
Summary generation must include only refs with meaningful collection IDs and avoid leaking no-collection remote refs into collection-aware output. Mirrored refs need correct collection association.

## Test Signals
The single TAP result follows regex checks for all expected collection/ref tuples and absence of no-collection `rcommit2`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-summary-collections.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-summary-update.sh -->
# sources/cloud-native/ostree/tests/test-summary-update.sh

## Purpose
This shell test validates summary update behavior, optional summary signing mtime alignment, custom metadata insertion and display, and collection-enabled `ostree-metadata` branch generation.

## Important APIs, Types, And Functions
It uses `ostree summary --update`, `--add-metadata`, `-m`, `summary --view`, `--list-metadata-keys`, `--print-metadata-key`, optional GPG signing arguments, `ostree refs --collections --create`, `ostree show --raw`, and `ostree log`.

## Control Flow
In a normal repo, the script creates five commits, generates plain and signed summaries, compares `summary` and `summary.sig` mtimes when signed, adds metadata values of string, boolean, integer, and empty map types, and verifies metadata view/list/print output. It repeats in a repo with collection ID `org.example.Collection1`, also creating mirror refs in `org.example.Collection2`. It validates the same metadata behavior and checks that `ostree-metadata` exists as a collection ref, has expected raw metadata bindings, has five commits from five summary updates, and contains only the root directory.

## State And Persistence
State includes `summary`, optional `summary.sig`, metadata entries, collection refs, and the `ostree-metadata` branch and commits in collection-enabled repos.

## Dependencies And Integration Points
This integrates summary metadata serialization, GVariant parsing from CLI strings, GPG signing, file mtimes, collection binding metadata, and metadata-branch generation.

## Risks
Metadata type parsing must be exact and stable. Signed summary mtime should match summary mtime for cache consistency. Collection repos must bind metadata commits to the correct collection/ref without adding files.

## Test Signals
Two TAP results cover normal and collection-enabled update flows. Checks include exact metadata strings, mtime equality, raw metadata bindings, commit counts, and root-only file listing.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-summary-update.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-summary-view.sh -->
# sources/cloud-native/ostree/tests/test-summary-view.sh

## Purpose
This test verifies human-readable and raw viewing of a pulled summary file.

## Important APIs, Types, And Functions
It uses `setup_fake_remote_repo1`, `ostree commit`, `ostree summary -u`, `ostree pull --mirror`, `OSTREE summary --view`, and `OSTREE summary --raw`.

## Control Flow
The script creates a signed or unsigned fake remote depending on GPGME availability, adds an `other` branch, regenerates the summary, initializes a client repo, adds the remote with GPG verification disabled, and mirror-pulls it. It then runs `ostree summary --view` in the repo and checks branch names and metadata labels, followed by `ostree summary --raw` and checks raw tuple and metadata serialization.

## State And Persistence
The mirror pull persists `repo/summary`, refs, and objects. Output files `summary.txt` and `raw-summary.txt` are temporary assertions.

## Dependencies And Integration Points
This integrates summary generation, mirror pull storing the summary, CLI default repo/context behavior for `OSTREE summary`, and summary rendering code.

## Risks
View output is user-facing and can break tests if labels change. Raw output must retain GVariant structure for consumers and diagnostics.

## Test Signals
Two TAP results cover view and raw view. Assertions check branches `main` and `other`, `ostree.summary.last-modified`, commit timestamp/version labels, and raw tuple strings.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-summary-view.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-symbols.sh -->
# sources/cloud-native/ostree/tests/test-symbols.sh

## Purpose
This shell test enforces the public libostree symbol ABI and documentation contract.

## Important APIs, Types, And Functions
It uses released and optional devel symbol files, `eu-readelf`, `grep`, `sed`, `sort`, `diff`, `assert_file_has_content_once`, `assert_not_file_has_content`, documentation file `apidoc/ostree-sections.txt`, and `sha256sum -c`.

## Control Flow
The script builds `expected-symbols.txt` from symbol definition files and `found-symbols.txt` from exported dynamic symbols in `.libs/libostree-1.so`, then diffs them. It checks the example devel symbol exists only in devel symbols and not released symbols. It filters private exceptions and verifies all public symbols are documented. Finally it checks the released symbol file SHA-256, with a comment that it should change only in release commits.

## State And Persistence
Temporary expected/found text files are written in the test directory. It reads build artifacts and source symbol/docs files but does not modify them.

## Dependencies And Integration Points
This integrates build-system output, ELF symbol versioning, API docs, devel feature gating, and release ABI policy.

## Risks
Any new public symbol must update symbol files, documentation, and sometimes the release checksum. Tooling availability (`eu-readelf`) and symbol version grep patterns are required.

## Test Signals
Three TAP results cover exported symbols, documented symbols, and released symbol checksum stability.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-symbols.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-sysroot-c.c -->
# sources/cloud-native/ostree/tests/test-sysroot-c.c

## Purpose
This C integration test validates `ostree_sysroot_load_if_changed()` around real sysroot deployment changes.

## Important APIs, Types, And Functions
It uses `ot_test_setup_sysroot`, `ostree_sysroot_load`, `ostree_sysroot_load_if_changed`, `g_spawn_command_line_sync`, `g_spawn_check_exit_status`, and CLI commands `ostree pull-local` and `ostree admin deploy`.

## Control Flow
`run_sync()` executes shell commands and validates exit status. `test_sysroot_reload()` loads the sysroot, confirms `load_if_changed` initially reports unchanged, pulls a test ref into the sysroot repo, deploys it with kernel args and OS name, then confirms `load_if_changed` reports changed once and unchanged on the next call.

## State And Persistence
State includes the test sysroot, sysroot repository, pulled local ref, deployment directories, bootloader/deployment metadata, and in-memory sysroot loaded state.

## Dependencies And Integration Points
This integrates libostree sysroot APIs with command-line admin deployment, local pull, boot deployment metadata, and the test sysroot fixture.

## Risks
Change detection must update after deployment writes and then become stable. CLI command failure is surfaced through GLib errors. The test assumes the fixture creates `sysroot` and `testos-repo` in the working directory.

## Test Signals
The GLib path `/sysroot-reload` fails on command execution errors or incorrect `changed` booleans.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-sysroot-c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-sysroot.js -->
# sources/cloud-native/ostree/tests/test-sysroot.js

## Purpose
This GJS integration test validates sysroot deployment lifecycle through libostree introspection bindings: initial empty deployments, remote setup, pull, deploy, write deployments, delete deployments, upgrade deployment, and boot checksum behavior.

## Important APIs, Types, And Functions
It uses `libtestExec()` to source `libtest.sh`, `OSTree.Repo`, `OSTree.Sysroot`, `sysroot.get_repo`, `remote_add`, `pull`, `get_merge_deployment`, `origin_new_from_refspec`, `deploy_tree`, `write_deployments`, `get_deployments`, `get_deployment_directory`, and deployment getters `get_csum` and `get_bootcsum`.

## Control Flow
The script creates an OS repository with syslinux fixture, enables mutable-deployments debug mode, opens the upstream repo and resolves the runtime ref, loads an empty sysroot, adds a file remote to the sysroot repo, and pulls. It deploys one tree, writes deployments, verifies the directory exists, then writes an empty deployment list and confirms deletion. It redeploys, creates a new upstream commit, pulls it, deploys an upgrade using the previous deployment as merge deployment, verifies two deployments and different boot/content checksums, creates a third commit with a flag that preserves boot checksum, deploys it, and verifies three deployments.

## State And Persistence
State includes upstream `testos-repo`, sysroot repo config and objects, deployment directories, origin metadata, boot checksums, and deployment lists written to sysroot state.

## Dependencies And Integration Points
This integrates GJS bindings, sysroot deployment internals, remote pull, OS repository fixture helpers, boot checksum generation, and mutable deployment cleanup.

## Risks
Deployment list ordering and directory cleanup must be correct. Merge deployment selection influences boot checksum reuse. JS binding tuple returns must be handled correctly.

## Test Signals
The script prints `1..1` but has multiple internal assertions and status prints: one deployment, empty deployments, two deployments, and final `ok test-sysroot`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-sysroot.js -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-varint.c -->
# sources/cloud-native/ostree/tests/test-varint.c

## Purpose
This C unit test validates OSTree variable-length unsigned 64-bit integer encoding and decoding round trips.

## Important APIs, Types, And Functions
It tests `_ostree_write_varuint64()` and `_ostree_read_varuint64()` from `ostree-varint.h`, using `GString`, `GVariant` debug printing in verbose mode, and GLib test APIs.

## Control Flow
`check_one_roundtrip()` writes a value into a string buffer, optionally prints encoded bytes, reads it back, asserts decoding succeeded, asserts no more than ten bytes were read, and compares the value. `test_roundtrips()` runs values including small boundaries, hex constants, `G_MAXUINT64`, `G_MAXUINT64 - 1`, and half max.

## State And Persistence
No persistent state is written. `GIO_USE_VFS=local` is set for deterministic local behavior.

## Dependencies And Integration Points
This integrates private varint helpers used by OSTree metadata such as sizes and deltas. It is also mirrored conceptually by the GJS varint reader in `test-sizes.js`.

## Risks
Boundary values near 127/128 and `G_MAXUINT64` catch continuation-bit and length bugs. Decode byte count must remain bounded to avoid malformed input issues elsewhere.

## Test Signals
The GLib path `/ostree/varint` fails on encode/decode mismatch, unsuccessful decode, or overlong encoded size.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-varint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-xattrs.sh -->
# sources/cloud-native/ostree/tests/test-xattrs.sh

## Purpose
This shell test is currently skipped. The dead code below the skip would validate committing and checking out `user.*` extended attributes.

## Important APIs, Types, And Functions
The active API is `skip` from `libtest.sh`, with the message that there is no current use case for committing user xattrs. Dead code uses `skip_without_user_xattrs`, `ostree checkout`, `setfattr`, `ostree commit --tree=dir=...`, `getfattr`, and assertion helpers.

## Control Flow
Execution stops immediately at `skip`. If re-enabled, it would set two user xattrs on `firstfile` in a checkout, commit the checkout to `test2`, check it out again, and verify both xattr names and values are preserved.

## State And Persistence
Active execution creates no repo state beyond any pre-skip harness setup. Dead code would persist user xattrs in file metadata and object commits.

## Dependencies And Integration Points
The skipped path would integrate user xattr support, checkout, commit, and metadata round-tripping. It requires filesystem support and `attr` tools.

## Risks
Because the test is skipped, regressions in user xattr commit/checkout behavior are not caught here. The skip references ostreedev issue 758 as rationale.

## Test Signals
The only active signal is a skip. Re-enabled dead code would produce two TAP results for commit and checkout with xattrs.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-xattrs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/webserver.py -->
# sources/cloud-native/ostree/tests/webserver.py

## Purpose
This Python helper daemonizes a simple threaded HTTP server on an automatically selected port and writes the port number to a file for tests.

## Important APIs, Types, And Functions
It uses `http.server.SimpleHTTPRequestHandler`, `ThreadingHTTPServer`, `socket.getaddrinfo`, `os.fork`, `os.setsid`, `os.rename`, `threading.Thread`, and `argparse`. Functions are `_get_best_family()`, `run()`, and `main()`.

## Control Flow
`main()` double-forks to daemonize, starts a daemon watcher thread that exits if the original working directory is deleted, parses a single `port_path` argument, and calls `run()`. `run()` selects address family, sets protocol version to HTTP/1.1, starts the server on the requested or random port, writes the chosen port atomically via `port_path.tmp` then rename, prints the port, and serves forever until keyboard interrupt.

## State And Persistence
The helper writes the port file and serves files from its current working directory. It holds an HTTP server socket and exits when the served directory disappears.

## Dependencies And Integration Points
This is used by shell tests needing an HTTP remote without the richer OSTree expected-header/cookie server. It integrates with test harness process cleanup through working-directory deletion.

## Risks
Double-forking can make failures harder to observe. The watcher calls `sys.exit()` from a thread, which exits that thread rather than forcibly terminating the process in standard Python semantics, so cleanup depends on surrounding harness behavior. Atomic port-file write is important to avoid races.

## Test Signals
There are no direct tests in this file. Consumers wait for the port file and then perform HTTP requests against the served directory.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/webserver.py -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/xtask/Cargo.toml -->
# sources/cloud-native/ostree/tests/xtask/Cargo.toml

## Purpose
This manifest defines a standalone dev-only Rust `ostree-xtask` binary used for OSTree integration testing tasks.

## Important APIs, Types, And Functions
It declares package metadata, a separate `[workspace]`, binary `ostree-xtask` at `src/main.rs`, and dependencies `anyhow`, `clap` with derive, `serde` with derive, `serde_json`, `tempfile`, and `xshell`.

## Control Flow
Cargo uses this manifest to compile the xtask binary outside the root workspace. Runtime behavior is implemented in `src/main.rs` and `src/tmt.rs`.

## State And Persistence
The manifest stores tool dependency policy and prevents publishing with `publish = false`. Cargo build artifacts are generated externally under the chosen target directory.

## Dependencies And Integration Points
This integrates with Rust Cargo tooling and external commands used by the xtask, especially `bcvk` and `tmt` through `xshell`.

## Risks
Because it declares a separate workspace, dependency versions are not inherited from the root. Dependency drift can affect dev tooling while leaving main project builds untouched.

## Test Signals
Successful `cargo run --manifest-path tests/xtask/Cargo.toml -- run-tmt ...` or `cargo check` validates the manifest and dependency graph.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/xtask/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/xtask/src/main.rs -->
# sources/cloud-native/ostree/tests/xtask/src/main.rs

## Purpose
This Rust entry point parses the xtask command line and dispatches to the TMT runner module.

## Important APIs, Types, And Functions
It uses `anyhow::Result`, `clap::Parser`, module `tmt`, enum `Opt`, and `xshell::Shell`. The only enum variant is `RunTmt(tmt::RunTmtArgs)`.

## Control Flow
`main()` parses `Opt`, constructs an `xshell::Shell`, matches the selected command, and calls `tmt::run_tmt(&sh, args)` for `RunTmt`.

## State And Persistence
No persistent state is stored here. It creates a shell context for subprocess execution.

## Dependencies And Integration Points
This integrates the Rust clap CLI with the TMT implementation in `tmt.rs` and external command execution through `xshell`.

## Risks
Any new xtask command must be added to the enum and match. Currently all behavior is delegated, so argument parsing is the main local risk.

## Test Signals
Compilation and `--help` output validate this file. Runtime validation comes from `run-tmt` execution in `tmt.rs`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/xtask/src/main.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/xtask/src/tmt.rs -->
# sources/cloud-native/ostree/tests/xtask/src/tmt.rs

## Purpose
This Rust module implements `ostree-xtask run-tmt`, running selected TMT plans inside isolated `bcvk` libvirt VMs.

## Important APIs, Types, And Functions
Key items include constants `SSH_TIMEOUT_SECS` and `SSH_POLL_INTERVAL_SECS`, `RunTmtArgs`, deserializable `BcvkInspect`, and functions `run_tmt`, `check_dependencies`, `discover_plans`, `run_plan`, `wait_for_ssh`, `cleanup_vm`, and `sanitize_plan_name`. It uses `anyhow`, `clap`, `serde_json`, `tempfile`, and `xshell::cmd`.

## Control Flow
`run_tmt()` checks `bcvk` and `tmt`, discovers plans with optional filters, builds a PID-derived VM name suffix, and runs each plan in sequence. `run_plan()` launches a detached VM from the requested image, waits for SSH by polling `bcvk libvirt ssh`, inspects JSON for SSH port and private key, writes the key to a temporary file, and runs `tmt run` with the connect provisioner against localhost. Each VM is cleaned up after the plan, and failures are collected and reported together. `sanitize_plan_name()` converts plan names into VM-safe suffixes.

## State And Persistence
State includes transient libvirt VMs, temporary private-key files, TMT run IDs named after VMs, and in-memory failure lists. `cleanup_vm()` attempts forced VM removal regardless of plan result.

## Dependencies And Integration Points
This integrates OSTree's dev tooling with `bcvk`, libvirt, TMT, SSH, container boot images, JSON inspection, and shell command orchestration. Extra `tmt_args` pass through after the plan selector.

## Risks
VM names use process ID plus sanitized final path component, so concurrent same-process reuse is unlikely but not globally unique. SSH polling has a fixed 300-second timeout. Failures in cleanup are ignored, which is pragmatic but can leave VMs behind. The temporary key file permissions rely on `tempfile` defaults.

## Test Signals
Dependency version checks, plan discovery output, per-plan pass/fail messages, SSH readiness messages, and final aggregate failure reporting are the observable signals. Unit tests are absent.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/xtask/src/tmt.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/.github/ISSUE_TEMPLATE/bug-report.yaml -->
# sources/cloud-native/overlaybd/.github/ISSUE_TEMPLATE/bug-report.yaml

## Purpose
This GitHub issue form defines the OverlayBD bug report template, collecting environment, expected behavior, reproduction steps, version, OS, and contributor willingness.

## Important APIs, Types, And Functions
The YAML uses GitHub issue forms schema fields: `name`, `description`, `labels`, `body`, `type: markdown`, `type: textarea`, `type: input`, `type: checkboxes`, `attributes`, `validations.required`, and checkbox `options`.

## Control Flow
When a user opens a bug report, GitHub renders the markdown preface, required environment and reproduction text areas, optional expected behavior, required version and OS fields, and an optional checkbox asking whether the reporter is willing to submit a PR.

## State And Persistence
The template persists issue metadata by applying label `bug` and serializing submitted form fields into the GitHub issue body. No repository runtime state is affected.

## Dependencies And Integration Points
This integrates with GitHub Issues, release links at `github.com/containerd/overlaybd/releases`, CNCF Slack `#overlaybd`, and repository triage workflows.

## Risks
The `environment` label asks "What happened in your environment?", which may mix symptom and environment data. Required fields improve triage but can discourage quick reports. External links can become stale.

## Test Signals
Validation is through GitHub issue-template rendering or YAML/schema linting. Required fields are `environment`, `reproduce`, `version`, and `os`.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/.github/ISSUE_TEMPLATE/bug-report.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/.github/ISSUE_TEMPLATE/config.yml -->
# sources/cloud-native/overlaybd/.github/ISSUE_TEMPLATE/config.yml

## Purpose
This GitHub issue-template configuration allows blank issues and provides a community support contact link for OverlayBD.

## Important APIs, Types, And Functions
The YAML uses GitHub issue template config keys `blank_issues_enabled` and `contact_links`, with link fields `name`, `url`, and `about`.

## Control Flow
When users open a new issue, GitHub permits blank issues and displays a contact link directing support questions to the repository discussions page.

## State And Persistence
This file only affects GitHub issue creation UI. It does not apply labels or modify project state.

## Dependencies And Integration Points
It integrates with GitHub Discussions at `https://github.com/containerd/overlaybd/discussions/` and complements the bug-report form in the same directory.

## Risks
Allowing blank issues may increase low-structure reports, but the contact link offers a softer path for support questions. The URL must remain valid if repository ownership changes.

## Test Signals
Validation is via GitHub issue-template config parsing. Expected behavior is blank issue availability plus a visible support/discussions contact link.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/.github/ISSUE_TEMPLATE/config.yml -->
