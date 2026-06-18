<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/fixtures/completions/git-lfs-completion.fish -->
# sources/sync-backup/git-lfs/t/fixtures/completions/git-lfs-completion.fish

## Purpose
Fish shell completion fixture for `git-lfs`, generated from Cobra completion support and used as the expected output by the completion integration tests. It translates Fish command-line state into a `git-lfs __completeNoDesc` request, then adapts the completion directive protocol to Fish's `complete` command.

## Important APIs, Functions, and Control Flow
The main helpers are `__git_lfs_debug`, `__git_lfs_perform_completion`, `__git_lfs_perform_completion_once`, `__git_lfs_clear_perform_completion_once_result`, `__git_lfs_requires_order_preservation`, and `__git_lfs_prepare_completions`. Completion starts from `commandline -opc` and `commandline -ct`, disables active help with `GIT_LFS_ACTIVE_HELP=0`, evaluates the request, strips trailing blank lines, separates candidates from the final `:<directive>` line, and prefixes flag-value completions when the current token matches `-.*=`.

## State, Persistence, and Dependencies
The script uses global Fish variables `__git_lfs_perform_completion_once_result` and `__git_lfs_comp_results` to cache one completion invocation per completion cycle. It depends on Fish builtins (`commandline`, `string`, `math`, `complete`) and on the installed `git-lfs` binary. Debug output appends to `BASH_COMP_DEBUG_FILE` when set.

## Integration Points, Risks, and Test Signals
It registers completions for `git-lfs`, first clearing any prior completions after triggering lazy completion loading. Directive bits handle error, no-space, no-file, extension filtering, directory filtering, and keep-order behavior; Fish lacks direct support for some filtering modes, so the script falls back to file completion. Risks cluster around `eval` quoting, directive parsing, and cache invalidation. `t-completion.sh` compares `git lfs completion fish` against this fixture byte-for-byte.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/fixtures/completions/git-lfs-completion.fish -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/fixtures/completions/git-lfs-completion.zsh -->
# sources/sync-backup/git-lfs/t/fixtures/completions/git-lfs-completion.zsh

## Purpose
Zsh completion fixture for `git-lfs`, also serving as a golden output for `git lfs completion zsh`. It adapts Cobra's completion protocol to zsh's completion system, including descriptions, active help, file filters, directory filters, no-space behavior, and order preservation.

## Important APIs, Functions, and Control Flow
The file defines `__git-lfs_debug` and `_git-lfs`, then registers `_git-lfs` for `git-lfs` with `compdef`. `_git-lfs` truncates `words` to `CURRENT`, computes a `git-lfs __completeNoDesc ...` request, appends an empty argument when the last parameter is complete, evaluates the request, extracts the trailing directive, and processes each completion line. Completion descriptions are converted from tab-separated Cobra output into zsh `_describe` colon syntax, with colons escaped.

## State, Persistence, and Dependencies
State is local to the completion invocation except optional debug logging through `BASH_COMP_DEBUG_FILE`. The script depends on zsh arrays, `compadd`, `_describe`, `_arguments`, and `_files`. The directive constants mirror Cobra shell completion directive bits.

## Integration Points, Risks, and Test Signals
It integrates with `git-lfs` by invoking `git-${words[1]#*git-}`, supporting invocation through aliases such as `git lfs`. Active help lines prefixed with `_activeHelp_ ` are displayed with zsh explanation groups. Risks include `eval` quoting, shell-specific array slicing, and fallback behavior when `_describe` finds no candidates. `t-completion.sh` validates this fixture by exact comparison with generated zsh completion output.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/fixtures/completions/git-lfs-completion.zsh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/fixtures/migrate.sh -->
# sources/sync-backup/git-lfs/t/fixtures/migrate.sh

## Purpose
Shared fixture library for Git LFS migration tests. It constructs many small repositories with controlled commit graphs, ref layouts, attributes, remotes, tags, symlinks, dirty working trees, special filenames, and corrupted LFS tracking states so migration commands can be tested against known histories.

## Important APIs, Functions, and Control Flow
The file exposes setup helpers such as `setup_local_branch_with_gitattrs`, `setup_local_branch_with_nested_gitattrs`, `setup_single_local_branch_untracked`, `setup_single_local_branch_tracked`, `setup_single_local_branch_tracked_corrupt`, `setup_multiple_local_branches`, `setup_multiple_remote_branches`, tag variants, remotes variants, deep tree variants, symlink and dirty-copy variants, and `setup_local_branch_with_special_character_files`. `assert_ref_unmoved` validates refs after a migration operation. `make_bare`, `remove_and_create_local_repo`, and `remove_and_create_remote_repo` are lower-level constructors.

## State, Persistence, and Dependencies
Each setup function mutates the current test directory by creating a new repository, changing into it, committing generated files, optionally pushing to the test Git server, and configuring Git LFS attributes. It depends on `testlib.sh` helpers, `lfstest-genrandom`, `git lfs track`, `setup_remote_repo`, `clone_repo`, `add_symlink`, and environment flags such as `IS_WINDOWS`.

## Integration Points, Risks, and Test Signals
The fixture's outputs are consumed by migration test scripts, not run as standalone assertions. Its most important integration contract is the named repository topology described in comments and embodied by Git refs. Risks include hidden `cd` side effects, randomized repository suffixes, platform-specific symlink and filename support, and attribute precedence involving `.gitattributes`, `.git/info/attributes`, and global Git attributes. Good test signals are commit graph shape, expected file sizes, ref immobility, and whether corrupt tracked files remain non-LFS objects until migration repair.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/fixtures/migrate.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/git-lfs-test-server-api/main.go -->
# sources/sync-backup/git-lfs/t/git-lfs-test-server-api/main.go

## Purpose
Command-line compliance probe for a Git LFS batch API server. It builds or reads known existing and missing object IDs, pins Git LFS transfer machinery to a supplied endpoint, and runs registered upload/download tests against that endpoint.

## Important APIs, Types, and Control Flow
Key types are `TestObject` (`Oid`, `Size`) and `ServerTest` (`Name`, callback). `RootCmd` exposes `--url`, `--clone`, and `--save`. `testServerApi` validates arguments, creates a temporary test repo through `t.NewRepo`, builds a manifest with `buildManifest`, either reads OID fixtures with `readTestOids` or creates them with `buildTestData`, optionally saves them, and calls `runTests`. `constantEndpoint` overrides endpoint discovery so all operations use the target endpoint. `callBatchApi`, `interleaveTestData`, and `uploadTransfer` are shared by upload/download test files.

## State, Persistence, and Dependencies
The tool creates local Git/LFS objects, uploads 50 existing objects when generating fresh test data, and may persist OID lists as `<prefix>_exists` and `<prefix>_missing`. It depends on Git LFS packages `lfsapi`, `lfshttp`, `tq`, `fs`, `tasklog`, and test utilities under `t/cmd/util`, plus Cobra.

## Integration Points, Risks, and Test Signals
The `init` in this file registers CLI flags; `init` functions in companion files register tests through `addTest`. Risks include ignored parse errors in `readTestOids`, deterministic but global `math/rand` seeding, and fatal process exits inside library-like helpers. Test signals are per-test OK/FAILED lines, final `All tests passed`, correct batch response lengths, and expected transfer links or error codes.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/git-lfs-test-server-api/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/git-lfs-test-server-api/testdownload.go -->
# sources/sync-backup/git-lfs/t/git-lfs-test-server-api/testdownload.go

## Purpose
Download-side compliance tests for the Git LFS batch API probe. It verifies that a server correctly advertises download actions for existing objects and returns object-level 404 errors for missing objects.

## Important APIs, Functions, and Control Flow
`downloadAllExist` calls `callBatchApi` with `tq.Download` for all known-present OIDs, checks that the response count matches input count, and requires each returned transfer to have a `download` relation. `downloadAllMissing` requests only missing OIDs, requires no `download` relation, and requires `o.Error.Code == 404`. `downloadMixed` creates string sets for existing and missing objects, interleaves both classes deterministically, and validates each returned object according to class.

## State, Persistence, and Dependencies
This file does not persist state itself; it reads the `oidsExist` and `oidsMissing` slices provided by `main.go`. It depends on `tq.Transfer.Rel`, `tools.StringSet`, `bytes.Buffer` aggregation, and the shared `callBatchApi` and `interleaveTestData` helpers.

## Integration Points, Risks, and Test Signals
The `init` function registers three tests into the global registry. The main risk is that it validates object class by OID membership rather than order, while still requiring total count. It does not verify response order or actual transfer execution, only batch metadata. Test signals are returned object counts, missing or present download links, and exact 404 object-level error codes.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/git-lfs-test-server-api/testdownload.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/git-lfs-test-server-api/testupload.go -->
# sources/sync-backup/git-lfs/t/git-lfs-test-server-api/testupload.go

## Purpose
Upload-side compliance tests for the Git LFS batch API probe. It verifies whether the server asks clients to upload missing objects, skips objects already present, and rejects invalid upload requests with proper object-level errors.

## Important APIs, Functions, and Control Flow
`uploadAllMissing` requires each missing OID to return an `upload` relation. `uploadAllExists` requires existing OIDs not to include upload links. `uploadMixed` uses OID sets and deterministic interleaving to validate mixed responses. `uploadEdgeCases` submits malformed SHA lengths, invalid SHA characters, negative sizes, and a valid zero-size object; invalid cases must return code 422 with no upload relation, while zero size must receive an upload link.

## State, Persistence, and Dependencies
State comes from `main.go` test object slices. The file depends on shared batch helpers, `tools.StringSet`, `bytes.Buffer`, and `tq.Transfer.Rel`. It accumulates all validation problems into a single returned error string per test.

## Integration Points, Risks, and Test Signals
The `init` function registers four upload tests. The tests assert batch API metadata rather than performing actual object upload for the returned links. Risks include strict expectation of 422 for validation failures and lack of error message matching beyond locally stored reasons used in failure text. Primary signals are response count, presence or absence of upload relations, and error code correctness for invalid OIDs and sizes.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/git-lfs-test-server-api/testupload.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-alternates.sh -->
# sources/sync-backup/git-lfs/t/t-alternates.sh

## Purpose
Integration tests for Git object alternates as they affect Git LFS object discovery. The script ensures LFS fetch and push avoid unnecessary batch requests when required objects are available through alternate Git object directories.

## Important APIs, Functions, and Control Flow
Each `begin_test` creates or clones a repository with one LFS-tracked file, removes local `.git/lfs/objects`, configures alternates either through `.git/objects/info/alternates` or `GIT_ALTERNATE_OBJECT_DIRECTORIES`, and runs `git lfs fetch` or push. Cases cover single alternate, multiple alternates with stale entries, commented alternate entries, quoted alternate paths, and environment variable alternates.

## State, Persistence, and Dependencies
The tests manipulate the local Git object store, LFS object store, alternates file, and environment variables. They depend on `setup_remote_repo_with_file`, `clone_repo`, `native_path`, and `native_path_list_separator` from `testlib.sh`. Windows path handling is explicitly considered for quoted alternates.

## Integration Points, Risks, and Test Signals
The key signal is whether trace output contains `sending batch of size 1`; a count of zero means LFS resolved the object locally through alternates. Commented alternates should be ignored and therefore trigger a batch request. Risks include trace-string fragility, path quoting differences across platforms, and hidden dependency on Git's alternates file parsing semantics.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-alternates.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-askpass.sh -->
# sources/sync-backup/git-lfs/t/t-askpass.sh

## Purpose
Credential integration tests for Git LFS askpass fallback. The script validates precedence and behavior for `GIT_ASKPASS`, `core.askPass`, `SSH_ASKPASS`, bad credentials, 401/403 responses, and credentials embedded in remote URLs.

## Important APIs, Functions, and Control Flow
Each test creates a remote repository, tracks `*.dat`, commits an LFS object, disables credential helpers when needed, sets askpass-related environment variables, and pushes. Success cases assert `main -> main`; failure cases assert absence of successful upload and match authorization messages or authentication-attempt limits. The final test rewrites `remote.origin.url` to include `user:pass` and ensures askpass is not invoked.

## State, Persistence, and Dependencies
The tests depend on `lfs-askpass`, `LFS_ASKPASS_USERNAME`, `LFS_ASKPASS_PASSWORD`, `GIT_TRACE`, and `GIT_CURL_VERBOSE`. They mutate local Git config (`credential.helper`, `core.askPass`, remote URL) and inspect `push.log`.

## Integration Points, Risks, and Test Signals
Integration is with Git credential prompting and the Git LFS HTTP client. Signals include trace lines `filling with GIT_ASKPASS`, request counts for username/password prompts, authorization error text, and `refute_server_object` for failed uploads. Risks include Git version or platform differences in prompt ordering and trace formatting.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-askpass.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-attributes.sh -->
# sources/sync-backup/git-lfs/t/t-attributes.sh

## Purpose
Tests Git LFS handling of Git attribute macros, including macros in repository, subdirectory, and global attribute files. It checks both whether files are actually cleaned into LFS objects and whether `git lfs track` recognizes already-supported patterns.

## Important APIs, Functions, and Control Flow
The four tests cover top-level macros, nested macros, global `$HOME/.config/git/attributes`, split macro definitions across HOME and repo `.gitattributes`, and unspecified macro flags with `!lfs`. They create files, commit them, assert local LFS object presence or absence, then inspect `git lfs track` output.

## State, Persistence, and Dependencies
The script mutates `.gitattributes`, subdirectory `.gitattributes`, and global attributes in `$HOME/.config/git/attributes`. It depends on Git's `check-attr` semantics, `assert_local_object`, `refute_local_object`, and `calc_oid`.

## Integration Points, Risks, and Test Signals
The main integration is between Git's attribute macro resolution and Git LFS's own attribute parser. Comments document known limitations where `git lfs track` reads attribute files depth-first and therefore does not fully match Git's macro resolution in nested cases. Signals are object-store assertions and `"already supported"` messages. Risks are global attribute pollution and platform-dependent HOME handling.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-attributes.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-batch-error-handling.sh -->
# sources/sync-backup/git-lfs/t/t-batch-error-handling.sh

## Purpose
Tests client behavior when the batch API returns a malformed or unexpected HTTP response. The repository name `badbatch` is a test-server trigger for an abnormal 203 response.

## Important APIs, Functions, and Control Flow
The test creates a remote and two clones, tracks `*.dat`, commits `a.dat`, verifies the committed Git object is an LFS pointer, verifies the server initially lacks the object, then attempts `git push origin main`. The expected flow ends in a parse error rather than a successful upload.

## State, Persistence, and Dependencies
State includes a local commit, `.gitattributes`, a missing server-side LFS object, and `push.log`. It depends on `setup_remote_repo`, `clone_repo`, `calc_oid`, `assert_pointer`, and `refute_server_object`.

## Integration Points, Risks, and Test Signals
The integration point is batch API response parsing during push. The key signal is `Unable to parse HTTP response` in `push.log`. Risks are high coupling to test-server behavior keyed by repository name and exact user-facing error text.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-batch-error-handling.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-batch-retries-ratelimit.sh -->
# sources/sync-backup/git-lfs/t/t-batch-retries-ratelimit.sh

## Purpose
Tests retry behavior when the batch API itself returns rate-limit responses. It covers upload, multi-object upload, clone/download, multi-object clone/download, and missing Retry-After header behavior.

## Important APIs, Functions, and Control Flow
Each test creates LFS-tracked files, pushes or clones under `GIT_TRACE=1`, and counts `tq: enqueue retry` log entries. Download tests use `set_server_rate_limit "batch"` to avoid rate limiting the initial push and then force rate limiting on the clone. Missing-header upload expects more than one retry and specific retry ordinals.

## State, Persistence, and Dependencies
The tests mutate remote server rate-limit state, local repositories, LFS objects, and trace logs. They depend on `setup_remote_repo`, `clone_repo`, `set_server_rate_limit`, `assert_server_object`, and `assert_local_object`.

## Integration Points, Risks, and Test Signals
Integration is with transfer queue retry scheduling for batch metadata requests. Signals include retry count, retry ordinal messages, successful server/local object assertions, and zero command failures. Risks are timing and delay behavior in rate-limit tests, plus brittle dependence on trace message wording.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-batch-retries-ratelimit.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-batch-storage-corrupt.sh -->
# sources/sync-backup/git-lfs/t/t-batch-storage-corrupt.sh

## Purpose
Verifies that Git LFS detects corrupted object data during download and does not persist invalid content or advance Git state incorrectly. It covers HTTP, pure SSH transfer, and custom transfer adapter paths.

## Important APIs, Functions, and Control Flow
Each test commits an LFS object, pushes it, removes local object data, causes the remote or test server to serve inverted-case corrupt content, then runs `git lfs pull` and `git pull`. The script asserts failed hash validation, absence of both expected and corrupt objects from local storage, appropriate `git lfs fsck` behavior, and that `HEAD` remains unchanged after smudge errors during `git pull`.

## State, Persistence, and Dependencies
State includes local object caches, remote LFS object files, worktree files, `initial_sha`, and logs. Dependencies include `setup_pure_ssh`, `ssh_remote`, custom adapter `lfstest-customadapter`, `invert_case`, `calc_oid`, `assert_server_object`, `assert_remote_object`, and `git lfs fsck`.

## Integration Points, Risks, and Test Signals
The tests exercise HTTP transfer, pure SSH `git-lfs-transfer`, and custom adapter integrity checks. Signals are expected/got OID messages, `downloaded file failed checks`, `Smudge error`, `Failed to fetch some objects`, and `Git LFS fsck OK` after resetting. Risks include exact log matching and platform-specific remote object path handling.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-batch-storage-corrupt.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-batch-storage-encoding.sh -->
# sources/sync-backup/git-lfs/t/t-batch-storage-encoding.sh

## Purpose
Tests HTTP transfer encoding behavior for LFS object storage. It covers gzip and zstd downloads, zstd concurrency and resume behavior, invalid configured encodings, chunked upload transfer encoding, and normal content-length uploads.

## Important APIs, Functions, and Control Flow
Repository names and object contents trigger special server behavior. Download tests configure `lfs.transfer.httpDownloadEncoding`, remove local object caches, run `git lfs pull` or `fetch` with curl tracing, and count `Accept-Encoding`, `Content-Encoding`, decompression, zstd decoder lifecycle, Range, and Content-Range lines. Upload tests inspect PUT request headers after filtering trace output to the storage request.

## State, Persistence, and Dependencies
The script mutates Git config, local object caches, remote repositories, and trace logs. It depends on curl verbose output, server behavior keyed by content/repository names, and object assertions.

## Integration Points, Risks, and Test Signals
Integration points are the HTTP storage adapter, retry/resume code, zstd decoder pooling, and upload header construction. Signals are exact header counts, successful local/server object assertions, unsupported encoding error text, and resume logs. Risks are trace formatting changes, optional zstd support assumptions, and concurrent decoder count sensitivity.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-batch-storage-encoding.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-batch-storage-retries-ratelimit.sh -->
# sources/sync-backup/git-lfs/t/t-batch-storage-retries-ratelimit.sh

## Purpose
Tests delayed retry behavior for storage-object HTTP requests, distinct from batch API retries. It covers upload, download, clone-time download, and missing Retry-After header behavior.

## Important APIs, Functions, and Control Flow
The tests use repository names that cause the test server to rate-limit storage endpoints. They commit LFS objects, push or pull/clone under `GIT_TRACE=1`, and count both `tq: retrying object` and `tq: enqueue retry`. Download tests avoid smudge during clone with disabled filters, then run explicit `git lfs pull`.

## State, Persistence, and Dependencies
State includes Git config, local repositories, server object store, object caches, and logs. Dependencies include `setup_remote_repo`, `clone_repo`, `assert_server_object`, `assert_local_object`, and the server's rate-limit fixtures.

## Integration Points, Risks, and Test Signals
Integration is with the transfer queue's storage request retry path. Test signals are retry log counts and successful object assertions. Risks are exact retry-count coupling and shared server state if repository names are reused.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-batch-storage-retries-ratelimit.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-batch-storage-retries.sh -->
# sources/sync-backup/git-lfs/t/t-batch-storage-retries.sh

## Purpose
Tests non-rate-limit storage retries and download resume behavior. It covers upload/download server errors, Range resume after interrupted downloads, fallback when a Range request is rejected, and avoiding invalid Range headers for complete or oversized partial files.

## Important APIs, Functions, and Control Flow
Upload/download retry tests set `lfs.transfer.maxretries` and expect exactly two retry messages before success. Range tests remove local objects, create or rely on interrupted partial downloads, run `git lfs fetch`, and inspect `Range`, `206 Partial Content`, `416 Requested Range Not Satisfiable`, accepted/rejected resume logs, and final object integrity. The last test manually creates corrupt `.git/lfs/incomplete/<oid>.part` files to exercise resume validation.

## State, Persistence, and Dependencies
The tests mutate `.git/lfs/objects`, `.git/lfs/incomplete`, local Git config, and trace logs. They depend on object content strings that trigger server behavior, curl verbose headers, and helper assertions for local/server objects.

## Integration Points, Risks, and Test Signals
Integration points are the HTTP storage adapter, transfer queue retry policy, incomplete download resume logic, and hash verification. Signals are retry counts, accepted/rejected Range behavior, OID mismatch errors, and final object store checks. Risks include brittle byte-range calculations and assumptions about temporary file naming.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-batch-storage-retries.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-batch-storage-upload-tus.sh -->
# sources/sync-backup/git-lfs/t/t-batch-storage-upload-tus.sh

## Purpose
Tests TUS protocol upload support through the Git LFS batch API. It validates both fresh uploads and interrupted uploads that resume from a server-reported offset.

## Important APIs, Functions, and Control Flow
Each test uses a repository name that advertises `tus` transfer support, sets `lfs.tusTransfers true`, commits `a.dat` plus `verify.dat`, and pushes with trace/curl verbose output. The normal case expects HEAD and PATCH requests from offset zero and no resume. The interrupted case expects initial 500 responses, repeated HEAD/PATCH requests, resume from one third of each object, and final `204 No Content`.

## State, Persistence, and Dependencies
State includes local Git config, LFS objects, server object storage, and `push.log`. The content string `send-verify-action` triggers verify-action behavior. The tests depend on the test server's TUS implementation and log messages from the TUS adapter.

## Integration Points, Risks, and Test Signals
Integration is with the batch adapter negotiation, TUS upload adapter, verify action, and retry/resume machinery. Signals are `Upload-Offset` counts, `xfer: tus.io` log lines, HTTP status counts, and `assert_server_object`. Risks include exact offset math for tiny objects and tight coupling to trace wording.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-batch-storage-upload-tus.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-batch-transfer-size.sh -->
# sources/sync-backup/git-lfs/t/t-batch-transfer-size.sh

## Purpose
Tests `lfs.transfer.batchSize` for upload and download. It ensures multiple objects are split into one-object batch API requests when batch size is configured to `1`.

## Important APIs, Functions, and Control Flow
The upload test commits three LFS objects, sets local `lfs.transfer.batchSize 1`, pushes, and expects three `tq: sending batch of size 1` trace lines. The download test pushes three objects, sets global batch size to `1`, clones, and expects the same trace count during clone.

## State, Persistence, and Dependencies
State includes local/global Git config, remote object store, and trace logs. The tests depend on `setup_remote_repo`, `clone_repo`, `calc_oid`, `assert_server_object`, and `assert_local_object`.

## Integration Points, Risks, and Test Signals
Integration is with transfer queue batching before batch API calls. Signals are exact batch-size trace counts and object presence checks. Risks include global config leakage and trace string changes.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-batch-transfer-size.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-batch-transfer.sh -->
# sources/sync-backup/git-lfs/t/t-batch-transfer.sh

## Purpose
Broad integration coverage for batch transfers over HTTP and SSH. It verifies basic push/pull, object ordering, hash algorithm handling, legacy SSH authentication, pure SSH transfer sessions, multiplexing, concurrency limits, and multi-branch fetches.

## Important APIs, Functions, and Control Flow
The script begins with `setup_expected_concurrent_transfers`. Tests create repositories, track `*.dat`, commit objects, push, clone/fetch/pull, and assert object presence. `assert_ssh_transfer_session_counts` and `assert_ssh_transfer_sessions` parse trace logs to validate `git-lfs-transfer` control and non-control SSH sessions, including special handling for older Git smudge behavior.

## State, Persistence, and Dependencies
State includes remote repositories, local object caches, Git config (`lfs.url`, `lfs.ssh.autoMultiplex`, `lfs.concurrentTransfers`), and trace logs. Dependencies include `setup_pure_ssh`, `ssh_remote`, `compare_version`, `assert_server_object`, `assert_remote_object`, and `git lfs fsck`.

## Integration Points, Risks, and Test Signals
Integration points are HTTP batch API, `git-lfs-authenticate`, pure SSH `git-lfs-transfer`, transfer queue ordering, and hash algorithm negotiation. Signals include upload progress, batch JSON order, unsupported hash errors, trace counts for SSH sessions, object assertions, and `fsck`. Risks are version-specific Git behavior and brittle trace regexes.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-batch-transfer.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-batch-unknown-oids.sh -->
# sources/sync-backup/git-lfs/t/t-batch-unknown-oids.sh

## Purpose
Tests that the transfer queue rejects a server response containing an unknown OID. The repository name `unknown-oids` triggers the test server to return a response inconsistent with the requested object set.

## Important APIs, Functions, and Control Flow
The test creates a remote repository, tracks `*.dat`, commits an object whose content is `unknown-oid`, attempts to push, captures the exit code, verifies the server did not receive the object, and requires a specific error message in `push.log`.

## State, Persistence, and Dependencies
State includes the local commit, `.gitattributes`, server object store, and `push.log`. It depends on `setup_remote_repo`, `clone_repo`, `calc_oid`, and `refute_server_object`.

## Integration Points, Risks, and Test Signals
The integration point is validation of batch API responses before object upload. Signals are nonzero push status, absent server object, and `[unknown-oid] The server returned an unknown OID.` Risks are dependence on test-server repository-name behavior and exact message text.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-batch-unknown-oids.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-checkout.sh -->
# sources/sync-backup/git-lfs/t/t-checkout.sh

## Purpose
Comprehensive integration tests for `git lfs checkout`. It validates normal checkout, path filtering, subdirectory context, missing local data, filesystem conflicts, symlinks, hardlinks, permissions, merge-conflict extraction, sparse/partial clone behavior, pointer extensions, and bare/worktree edge cases.

## Important APIs, Functions, and Control Flow
The main test creates repeated LFS objects across files and directories, removes worktree files, and exercises `git lfs checkout` with no args, file args, globs, `.` and `..`, and directory filters. Subsequent tests cover file/directory and symlink conflicts, case-insensitive collisions, modified files, hardlink replacement, missing clean filter, outside/bare repositories, read-only files/directories, mtime preservation for empty files, conflict checkout with `--to --base/--ours/--theirs`, `GIT_WORK_TREE`, sparse partial clone, and extension smudge paths.

## State, Persistence, and Dependencies
The script heavily mutates worktrees, indexes, `.git/lfs/objects`, incomplete checkouts, permissions, symlinks, hardlinks, merge state, environment variables, and Git config. Dependencies include many `testlib.sh` helpers, `lfstest-nanomtime`, version gates, `setup_case_inverter_extension`, `has_native_symlinks`, and object assertions.

## Integration Points, Risks, and Test Signals
Integration includes checkout scanner behavior, Git index state, pointer decoding, clean/smudge filters, sparse checkout Git versions, filesystem safety checks, and extension smudge execution. Signals are worktree content comparisons, clean-index/status assertions, progress lines, skip/error logs, `fsck`, and non-advancing HEAD on failure. Risks are platform-specific symlink/permissions/case behavior and version-dependent sparse-index behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-checkout.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-cherry-pick-commits.sh -->
# sources/sync-backup/git-lfs/t/t-cherry-pick-commits.sh

## Purpose
Tests that cherry-picking multiple LFS-containing commits succeeds when the local LFS object cache has been removed. This exercises smudge/download behavior during Git cherry-pick.

## Important APIs, Functions, and Control Flow
The test creates a remote, tracks `*.dat`, makes an initial commit, creates `secondbranch`, commits `a.dat` and `b.dat` on main, records both commit IDs, pushes main, checks out `secondbranch`, deletes `.git/lfs/objects`, and runs `git cherry-pick $commit1 $commit2`.

## State, Persistence, and Dependencies
State includes branch topology, two LFS commits, remote uploaded LFS objects, and an intentionally empty local LFS object cache. It depends on `setup_remote_repo`, `clone_repo`, and normal Git LFS smudge/filter integration.

## Integration Points, Risks, and Test Signals
The integration point is Git invoking LFS filters while applying cherry-picked commits. The test signal is command success under `set -e`; there are no explicit content assertions after cherry-pick. The main risk is low diagnostic specificity if cherry-pick succeeds but content is wrong.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-cherry-pick-commits.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-clean.sh -->
# sources/sync-backup/git-lfs/t/t-clean.sh

## Purpose
Unit-style integration tests for `git lfs clean`, the clean filter that stores file contents in the LFS object store and emits pointer files. It also covers pointer-like inputs, pointer extensions, and stdin handling.

## Important APIs, Functions, and Control Flow
`clean_setup` creates a Git repository. Tests pipe ordinary content, a valid pointer, pseudo-pointers, and a pseudo-pointer with large extra data through `git lfs clean`, then compare exact pointer output. The pointer-extension test configures a case-inverter extension and verifies the extension pointer and local object. The stdin test compares OIDs from `git lfs clean < file` to `calc_oid_file`.

## State, Persistence, and Dependencies
The command writes objects under `.git/lfs/objects`, and the extension test writes `LFSTEST_EXT_LOG`. Dependencies include `pointer`, `calc_oid`, `calc_oid_file`, `setup_case_inverter_extension`, `case_inverter_extension_pointer`, and `assert_local_object`.

## Integration Points, Risks, and Test Signals
Integration is with the clean filter, pointer parser, object storage, and extension clean hook. Signals are exact pointer comparisons, object assertions, and extension log entries. Risks include exact fixture hashes and buffer-sensitive pseudo-pointer behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-clean.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-clone-deprecated.sh -->
# sources/sync-backup/git-lfs/t/t-clone-deprecated.sh

## Purpose
Tests that `git lfs clone` emits a deprecation warning on sufficiently new Git versions where regular `git clone` has comparable LFS support.

## Important APIs, Functions, and Control Flow
The script gates on Git version `>= 2.15.0`, creates an empty remote, enters a directory named after the repository, runs `git lfs clone "$GITSERVER/$reponame"`, and greps the output for two warning lines.

## State, Persistence, and Dependencies
State is limited to a test remote, a local directory, and `clone.log`. Dependencies include `ensure_git_version_isnt`, `setup_remote_repo`, and the deprecation text in the `git lfs clone` command.

## Integration Points, Risks, and Test Signals
Integration is the CLI compatibility layer for the deprecated clone subcommand. Signals are exact warning text. Risks are message churn and Git version gate mismatch.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-clone-deprecated.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-clone.sh -->
# sources/sync-backup/git-lfs/t/t-clone.sh

## Purpose
Large integration suite for `git lfs clone` and regular `git clone` with LFS smudge. It covers HTTP, SSL, client certificates, clone flags, include/exclude filters, `.lfsconfig`, missing clean filters, recursive submodules, current-directory clone, empty repositories, bare clones, and cookie-based authentication.

## Important APIs, Functions, and Control Flow
Tests create remotes, track `*.dat`, generate deterministic file histories with `lfstest-testutils addcommits`, push, then clone through several modes. SSL and client-certificate tests configure certificate paths and credential records. Flag tests exercise `--template`, `--local`, `--no-checkout`, `--branch`, `--origin`, `--separate-git-dir`, `--bare`, and short options. Include/exclude and `.lfsconfig` tests assert selective object download. Submodule tests build nested repositories with LFS content.

## State, Persistence, and Dependencies
The script mutates global SSL and credential config, `CREDSDIR`, HOME certificate copies, remote URLs, cookie files, submodule metadata, hooks, and LFS object stores. Dependencies include credential helper `lfstest`, certificate fixtures, `assert_hooks`, object assertions, and Git version gating.

## Integration Points, Risks, and Test Signals
Integration covers clone wrapper behavior, smudge downloads, hook installation, Git config precedence, TLS client auth, cookies, submodules, and fetch include/exclude logic. Signals are clone logs, downloaded file sizes, object-store counts, clean status, hook assertions, and absence of filter/error lines. Risks include global config leakage, platform-specific certificate paths, and deprecation-sensitive `git lfs clone` behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-clone.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-commit-delete-push.sh -->
# sources/sync-backup/git-lfs/t/t-commit-delete-push.sh

## Purpose
Tests that `git lfs push` includes LFS objects reachable from history even if their files are later deleted before the push. This prevents lost objects for historical commits.

## Important APIs, Functions, and Control Flow
The test commits `deleted.dat`, checks dry-run output and pointer metadata, commits `added.dat`, checks dry-run includes both objects, removes `deleted.dat`, commits the deletion, checks dry-run again, then performs a real push and verifies both server objects exist.

## State, Persistence, and Dependencies
State includes a three-commit history, dry-run logs, server object store, and local pointers. Dependencies include `calc_oid`, `assert_pointer`, `assert_server_object`, and exact dry-run output.

## Integration Points, Risks, and Test Signals
Integration is with LFS object graph traversal for push. Signals are dry-run `push <oid> => <path>` lines, upload progress for two files, and server object assertions. Risks are exact output matching and reliance on historical path names after deletion.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-commit-delete-push.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-completion.sh -->
# sources/sync-backup/git-lfs/t/t-completion.sh

## Purpose
Tests the `git lfs completion` command for supported shells and argument validation. It ties generated completion output to checked-in fixtures.

## Important APIs, Functions, and Control Flow
The script runs `git lfs completion bash`, `fish`, and `zsh`, comparing stdout byte-for-byte against fixtures in `$COMPLETIONSDIR`. It also runs the command with no shell argument and with invalid shell `ksh`, then greps for validation errors.

## State, Persistence, and Dependencies
The tests only create temporary logs and rely on `$COMPLETIONSDIR`. Dependencies are fixture files, `cmp`, and Cobra argument validation messages.

## Integration Points, Risks, and Test Signals
Integration is with CLI completion generation. Signals are exact fixture comparisons plus `accepts 1 arg` and `invalid argument` text. Risks are high fixture churn whenever generated completion templates change.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-completion.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-config.sh -->
# sources/sync-backup/git-lfs/t/t-config.sh

## Purpose
Tests Git LFS configuration discovery, precedence, URL rewriting, extension configuration, safe `.lfsconfig` handling, and include directives under `GIT_CONFIG`.

## Important APIs, Functions, and Control Flow
Tests inspect `git lfs env` and `git lfs ext` output under combinations of remote URL defaults, `.lfsconfig`, local/global Git config, repository-tree `.lfsconfig` via `HEAD` and index, extension config precedence, `url.*.insteadOf` longest-match and ambiguity behavior, unsafe key filtering, and included config files. One test ensures an LFS-tracked file named before `.lfsconfig` lexicographically does not prevent config loading during clone.

## State, Persistence, and Dependencies
State includes `.lfsconfig`, `.git/config`, global config, included config files, remote refs, and LFS object caches. Dependencies include `setup_remote_repo`, `git lfs env`, `git lfs ext`, URL alias logic, and Git config include support.

## Integration Points, Risks, and Test Signals
Integration points are endpoint discovery, auth access mode selection, extension loading, Git URL rewriting, repository config loading from tree/index, and `.lfsconfig` safety filtering. Signals are exact `Endpoint=... (auth=...)`, `Extension: ...`, warning text, and cloned file contents. Risks are exact output wording and global config side effects.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-config.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-content-type.sh -->
# sources/sync-backup/git-lfs/t/t-content-type.sh

## Purpose
Tests Content-Type detection for LFS uploads and the warning emitted when a server rejects unsupported content types.

## Important APIs, Functions, and Control Flow
The first test creates a `.tar.gz` LFS object and expects `Content-Type: application/x-gzip` in curl verbose upload output by default. The second sets `lfs.$GITSERVER.contenttype 0` and expects `application/octet-stream` instead. The third uploads content `status-storage-422`, which triggers server rejection and verifies user guidance to disable content-type detection.

## State, Persistence, and Dependencies
State includes local Git config, tar-generated files, push logs, and server object behavior. Dependencies include `tar`, `GIT_CURL_VERBOSE`, repository-name/content triggers, and `git lfs track`.

## Integration Points, Risks, and Test Signals
Integration is with MIME detection and upload request header construction. Signals are curl verbose header counts and warning text. Risks are platform-dependent MIME detection and exact server-triggered message wording.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-content-type.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-credentials-no-prompt.sh -->
# sources/sync-backup/git-lfs/t/t-credentials-no-prompt.sh

## Purpose
Tests non-interactive credential failure behavior. It ensures Git LFS does not hang for prompts when `GIT_TERMINAL_PROMPT=0` and credential helpers or askpass commands cannot supply usable credentials.

## Important APIs, Functions, and Control Flow
The first test configures `credential.helper lfsnoop` globally and locally, then pushes without credentials and expects an authorization or missing-credentials error. The second disables credential helpers, sets a nonexistent `GIT_ASKPASS`, blocks terminal prompts, and expects both an askpass failure and a credential fill attempt.

## State, Persistence, and Dependencies
State includes global/local credential config, committed LFS files, and `push.log`. The script depends on Git version `>= 2.3.0`, `git-credential-lfsnoop`, and prompt suppression through `GIT_TERMINAL_PROMPT=0`.

## Integration Points, Risks, and Test Signals
Integration is with Git credential lookup and prompt suppression. Signals are explicit authorization/missing-credential messages, `failed to find GIT_ASKPASS command`, and `creds: git credential fill`. Risks are version-specific credential behavior and multiple accepted error strings in the first test.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-credentials-no-prompt.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-credentials-protect.sh -->
# sources/sync-backup/git-lfs/t/t-credentials-protect.sh

## Purpose
Security tests for credential protocol protection against control characters embedded in credential fields, especially URL paths decoded from `%0a`, `%0d`, and `%00`.

## Important APIs, Functions, and Control Flow
`setup_creds` prepares credential records and copies localhost credentials. Each test creates an LFS object, configures `lfs.url` to a localhost URL whose repository path contains an encoded line feed, carriage return, or null byte, creates the matching remote directory, attempts `git lfs push`, and inspects credential rejection. The carriage-return case also disables `credential.protectProtocol` and expects success; newline and null remain rejected.

## State, Persistence, and Dependencies
State includes `CREDSDIR`, local config `lfs.url`, optional `credential.protectProtocol`, server repositories with encoded names, and server object store. Dependencies include `setup_creds`, `setup_remote_repo`, `refute_server_object`, and `assert_server_object`.

## Integration Points, Risks, and Test Signals
Integration is with Git credential protocol serialization and LFS endpoint URL parsing. Signals are `credential value for path contains newline/carriage return/null byte`, missing credential errors, success after disabling protection for carriage return, and object-store assertions. Risks are URL-decoding differences and exact security error text.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-credentials-protect.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-credentials.sh -->
# sources/sync-backup/git-lfs/t/t-credentials.sh

## Purpose
Large credential integration suite for Git LFS. It covers credential helper precedence, `useHttpPath`, 401/403 retry behavior, WWW-Authenticate forwarding, Bearer and multistage auth capabilities, raw `git credential` helper behavior, netrc fallback, credentials in `lfs.url`, and credentials in `remote.origin.url`.

## Important APIs, Functions, and Control Flow
The file sets `CREDSDIR` and `setup_creds`, then creates per-test repositories and credential records. Tests push LFS objects under different helper and config settings, count `git credential fill/approve/reject/cache`, validate path inclusion or omission, and verify object presence or absence. Netrc tests iterate `.netrc` and `_netrc` on Windows. URL credential tests switch between bad unauthenticated URLs and embedded `requirecreds:pass` credentials, checking storage endpoint access-mode behavior.

## State, Persistence, and Dependencies
State includes credential record files, `.netrc`, Git global/local config, credential capability output, `LFS_TEST_CREDS_WWWAUTH`, remote URLs, LFS object caches, and trace/curl logs. Dependencies include `git-credential-lfstest`, `git credential capability`, server auth modes, `setup_remote_repo`, and object assertions.

## Integration Points, Risks, and Test Signals
Integration points are Git credential plumbing, LFS API authentication retries, locking API authentication, WWW-Authenticate metadata, netrc parsing, auth-state capabilities, and endpoint access-mode caching. Signals are upload progress or absence, fill/approve counts, authorization headers, retry-limit messages, credential output exact matches, and object-store assertions. Risks include Git version capability differences, global config pollution, platform netrc naming, and exact trace log matching.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-credentials.sh -->
