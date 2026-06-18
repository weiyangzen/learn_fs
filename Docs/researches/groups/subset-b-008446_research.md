# Research Group subset-b-008446

This grouped report covers FoundationDB client utilities, blobstore integration test fixtures, generated binding-option writers, the experimental `fdbctl` gRPC control service, and the Kubernetes monitor API/build support. Each section is delimited for reconciliation into a source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/zipf.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/zipf.h

## Purpose
This header exposes a small C ABI for a YCSB-derived Zipfian integer generator used by FoundationDB client-side tests or benchmarks that need skewed key selection. It defines `ZIPFIAN_CONSTANT` as `0.99`, declares generator initialization overloads, and declares `zipfian_next()` for producing the next sampled item.

## Important APIs, Types, And Functions
The public API is `zipfian_generator3(int min, int max, double zipfianconstant)`, `zipfian_generator(int items)`, and `zipfian_next()`. The declarations are wrapped in `extern "C"` for C++ consumers and protected by both `#ifndef ZIPF_H` and `#pragma once`.

## Control Flow
Callers must initialize process-global generator state with either an item count or an explicit min/max/constant range before calling `zipfian_next()`. The header itself has no logic; it couples callers to the global-state implementation in `zipf.c`.

## State And Persistence Behavior
No persistent state is declared here. The important state implication is that the implementation uses global static state, so this header represents a singleton generator rather than a reusable object.

## Dependencies And Integration Points
The header integrates C and C++ code by providing C linkage. It is included by `zipf.c` and any workload or benchmark code needing YCSB-like distributions.

## Risks And Edge Cases
The API does not expose seeding, reset, thread-safety, or error handling. Calling `zipfian_next()` before initialization, using invalid ranges, or sharing the generator across threads depends entirely on implementation behavior.

## Test Signals
Useful tests initialize with known item counts/ranges, assert samples remain within bounds, compare histogram skew, and check that C++ code can link through the C ABI.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/zipf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/notified_support.swift -->
# sources/storage-engines/foundationdb/fdbclient/notified_support.swift

## Purpose
This Swift file is currently a placeholder for Swift helpers around Flow/FDB notification primitives. It imports `Flow`, `flow_swift`, and `FDBClient`, but the only implementation is commented out.

## Important APIs, Types, And Functions
The commented extension targets `NotifiedVersion` and would add an async `atLeast(_:)` wrapper around `whenAtLeast(limit)`, awaiting a `FutureVoid` through Swift concurrency.

## Control Flow
No executable control flow is compiled. The intended path was: call `whenAtLeast`, receive a Flow future, bridge it to `await f.value()`, and propagate errors.

## State And Persistence Behavior
There is no runtime state or persistence. If enabled, the helper would observe version-notification state owned by `NotifiedVersion` without mutating durable data.

## Dependencies And Integration Points
The imports show integration between generated Swift bindings and Flow futures. The file is a natural bridge point for async/await support in the Swift API.

## Risks And Edge Cases
Because the code is commented, the risk is mostly build churn or stale API expectations: `VersionMetricHandle.ValueType`, `FutureVoid`, or `value()` signatures may no longer match. If uncommented, cancellation/error propagation across Flow and Swift concurrency would need tests.

## Test Signals
Current test signal is simply successful Swift compilation with unused imports accepted. Future tests should verify `atLeast` completes after the notified version crosses the limit and propagates failed/cancelled futures.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/notified_support.swift -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/sha1/SHA1.cpp -->
# sources/storage-engines/foundationdb/fdbclient/sha1/SHA1.cpp

## Purpose
This file implements a public-domain SHA-1 digest class adapted to return the 20-byte binary digest as a `std::string`. It supports incremental updates from strings or streams and a convenience `from_string` one-shot helper.

## Important APIs, Types, And Functions
Public methods implemented here are `SHA1::SHA1()`, `update(const std::string&)`, `update(std::istream&)`, `final()`, and `from_string`. Private helpers are `reset`, `transform`, `buffer_to_block`, and `read`. The SHA-1 compression function is written with macros `SHA1_ROL`, `SHA1_BLK`, and the unrolled round macros `SHA1_R0` through `SHA1_R4`.

## Control Flow
Construction calls `reset()` to seed the five SHA-1 digest words. `update(string)` wraps the input in an `istringstream`; `update(stream)` fills the partial buffer up to 64 bytes, repeatedly converts the buffer into sixteen big-endian words, and calls `transform`. `final()` appends SHA-1 padding, conditionally transforms an extra block if the length field does not fit, appends the 64-bit bit length split across the last two words, transforms the final block, emits digest words in big-endian byte order, resets the instance, and returns the binary digest.

## State And Persistence Behavior
All state is in-memory: `digest[5]`, `buffer`, and `transforms`. `final()` is destructive in the useful sense that it resets the object for reuse after returning the digest. No persistent storage is touched.

## Dependencies And Integration Points
The implementation depends only on `SHA1.h`, `<sstream>`, and standard stream/string types. It can be used anywhere FoundationDB needs a compact local SHA-1 implementation without external crypto-library linkage.

## Risks And Edge Cases
SHA-1 is cryptographically broken for collision resistance and should not be used for security-sensitive signatures or integrity guarantees against malicious input. `read()` allocates a heap buffer for each read and does not use RAII, although it deletes on the normal path. The declaration and implementation use `uint32 block[BLOCK_BYTES]` for parameters where only `BLOCK_INTS` words are accessed; this is harmless for callers here but confusing. The returned digest is binary, not hex, and may contain NUL bytes.

## Test Signals
Known-answer tests for empty string, `"abc"`, multi-block inputs, stream updates split at 63/64/65 bytes, and object reuse after `final()` would cover the important paths. Tests should compare binary digest bytes, not printable strings.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/sha1/SHA1.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/sha1/SHA1.h -->
# sources/storage-engines/foundationdb/fdbclient/sha1/SHA1.h

## Purpose
This header declares the `SHA1` C++ class and its internal constants/state. It is the public interface for the SHA-1 implementation in `SHA1.cpp`.

## Important APIs, Types, And Functions
The public API exposes construction, `update` from `std::string`, `update` from `std::istream`, `final`, and static `from_string`. Internal aliases `uint32` and `uint64` use fixed-width integer types. Constants define five digest words, sixteen 32-bit block words, and sixty-four bytes per block.

## Control Flow
Callers construct an instance, call one or more `update` methods, then call `final()` to retrieve and reset the digest. The private helpers declare the compression and buffer-conversion steps used by the implementation.

## State And Persistence Behavior
`digest`, `buffer`, and `transforms` hold mutable in-memory hashing state. There is no file, network, or database persistence.

## Dependencies And Integration Points
The header depends on `<iostream>`, `<string>`, and `<stdint.h>`. It is designed as a standalone utility class and returns `std::string` for easy integration with FoundationDB code that already uses string-like binary buffers.

## Risks And Edge Cases
The binary return value from `final()` is easy to misinterpret as text. The class is mutable and not thread-safe. SHA-1 should only be used for compatibility or non-adversarial checks.

## Test Signals
Compilation users should include this header without additional crypto dependencies. Behavioral tests should exercise incremental updates, stream updates, empty input, and multiple `final()` calls on one instance.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/sha1/SHA1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/tests/aws_fixture.sh -->
# sources/storage-engines/foundationdb/fdbclient/tests/aws_fixture.sh

## Purpose
This Bash fixture provides helper functions for FoundationDB blobstore tests that run against real AWS S3. It creates scratch space, discovers EC2 metadata-derived region/account information, writes blob credential files, and cleans up temporary files.

## Important APIs, Types, And Functions
Key functions are `shutdown_aws`, `create_aws_dir`, `write_blob_credentials`, and `aws_setup`. `write_blob_credentials` either builds and runs the Go `fdb-aws-s3-credentials-fetcher` from the build tree or falls back to IMDS role credentials plus `jq`. `aws_setup` returns host, bucket, credentials file, and region as newline-separated values.

## Control Flow
Consumers source the fixture, call `create_aws_dir`, call `aws_setup build_dir aws_dir`, read the returned array, run tests, and call `shutdown_aws`. Setup obtains an IMDSv2 token, region, account id through `aws sts`, computes `backup-${account_id}-${region}`, prefixes the host with `@` to force credential-file lookup, and writes credentials before printing results.

## State And Persistence Behavior
The fixture persists only temporary local scratch files and generated JSON credentials. It may also build a helper binary in the build tree. It does not create or delete S3 buckets; higher-level tests remove object prefixes.

## Dependencies And Integration Points
It depends on Bash 4+, `curl`, `openssl`, `jq`, optionally Go, optionally `aws`, EC2 IMDS at `169.254.169.254`, and the FoundationDB Docker credential-fetcher source. It integrates with `tests_common.sh` through shared `err` logging and with `s3client_test.sh`/`bulkload_test.sh` through the returned configuration.

## Risks And Edge Cases
The fixture assumes it is running in an AWS environment with metadata access and suitable IAM permissions. Missing `aws` CLI is not checked explicitly before `aws_setup`. Several failures call `exit 1` from a sourced file, which terminates the parent test script. Generated credential files contain sensitive temporary credentials and must remain in scratch storage.

## Test Signals
Signals include successful dependency checks, a non-empty credentials JSON file, correct `@s3.<region>.amazonaws.com` host, expected bucket naming, and successful downstream `s3client`/bulkload operations against S3.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/tests/aws_fixture.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/tests/bulkload_test.sh -->
# sources/storage-engines/foundationdb/fdbclient/tests/bulkload_test.sh

## Purpose
This integration test validates FoundationDB bulkdump and bulkload using either real S3/GCS or MockS3Server. It starts a loopback cluster, writes data, dumps the full key range to blobstore, clears the database, restores from the dump, verifies data, and checks logs for severity 40 errors.

## Important APIs, Types, And Functions
Main functions are `cleanup`, `resolve_to_absolute_path`, `bulkdump`, `bulkload`, and `test_basic_bulkdump_and_bulkload`. The script uses shared helpers from `tests_common.sh` (`load_data`, `clear_data`, `verify_data`, `grep_for_severity40`, `setup_s3_environment`), `fdb_cluster_fixture.sh` (`start_fdb_cluster`, `shutdown_fdb_cluster`), and cloud/mock fixtures.

## Control Flow
The script installs exit/signal traps, resolves its own directory, sources common helpers, derives `USE_S3`, sets TLS and encryption knobs, validates command-line source/build/scratch arguments, sets up the blobstore environment, sources the FDB cluster fixture, starts a loopback cluster with nine storage servers, and runs `test_basic_bulkdump_and_bulkload`. The test loads generated key/value data, optionally removes the target S3 prefix, enables bulkdump mode, starts a dump, polls until no dump is running, clears data, enables bulkload mode, adds the lock owner, starts load by job id, polls until completion, verifies values, and scans logs.

## State And Persistence Behavior
It creates scratch directories containing cluster files, logs, MockS3 persistence, credentials, and temporary outputs. Database state is deliberately mutated through load, clear, and restore phases. Cleanup normally tears down FDB, MockS3, AWS scratch state, and can preserve artifacts when `PRESERVE_TEST_DATA=1`.

## Dependencies And Integration Points
The test depends on built `fdbcli`, `s3client`, the loopback cluster script, blobstore fixture selection, and bulkdump/bulkload CLI commands. It passes blobstore URLs of the form `blobstore://host/path?bucket=...&region=...&secure_connection=...`.

## Risks And Edge Cases
`bulkdump` declares `local_url` but invokes `bulkdump dump ... "${url}"`, which relies on a global `url` rather than the parameter and is fragile. Poll loops have no explicit timeout, so stuck jobs can hang until the outer test timeout. Real S3 mode uses KMS encryption knobs and may fail on IAM/KMS policy drift. The script uses `set -euo pipefail` plus sourced fixtures that can `exit`.

## Test Signals
Strong signals are a captured dump job id, successful `bulkload status` convergence to no running job, exact restored values from `verify_data`, and absence of `Severity="40"` traces outside excluded directories.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/tests/bulkload_test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/tests/fdb_cluster_fixture.sh -->
# sources/storage-engines/foundationdb/fdbclient/tests/fdb_cluster_fixture.sh

## Purpose
This Bash fixture starts and stops local loopback FoundationDB clusters for integration tests. It also provides a helper to start `backup_agent` against the generated cluster file.

## Important APIs, Types, And Functions
The exported surface is the global `FDB_PIDS` array plus `shutdown_fdb_cluster`, `start_fdb_cluster`, and `start_backup_agent`. `start_fdb_cluster` invokes `tests/loopback_cluster/run_custom_cluster.sh` with selected role counts, storage count, storage engine, knobs, and PID dumping.

## Control Flow
Startup builds a knob string with `--knob_shard_encode_location_metadata=true` and optional extra knobs, then retries port prefixes starting at 1600 in increments of 100. It temporarily disables `errexit` and `noclobber` around cluster startup, extracts `PIDS=` from output with retries, checks `fdbcli status`, retries only on "Local address in use", and otherwise prints stderr and fails. Shutdown sends SIGTERM to tracked PIDs, waits briefly, sends SIGKILL to survivors, and reports any remaining processes within a 15-second budget.

## State And Persistence Behavior
The fixture creates a `loopback_cluster` under the supplied scratch directory, writes output and stderr capture files, and stores tracked process IDs in memory. It does not delete scratch directories directly; caller cleanup owns file removal.

## Dependencies And Integration Points
It depends on the FoundationDB source tree, built `fdbcli`, `backup_agent`, loopback cluster scripts, POSIX process tools, and shared `err`/`log` functions when sourced by tests.

## Risks And Edge Cases
PID extraction depends on textual `PIDS=` output and may produce malformed entries if output contains unexpected binary/text data. Shutdown is intentionally aggressive and can kill only tracked processes, leaving untracked children if PID extraction failed. Knobs are passed as a single string, so quoting-sensitive values require care.

## Test Signals
Startup success is `fdbcli status` against `${scratch}/loopback_cluster/fdb.cluster`. Cleanup signal is no remaining tracked process and logs showing SIGTERM/SIGKILL completion within the shutdown budget.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/tests/fdb_cluster_fixture.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/tests/gcp_fixture.sh -->
# sources/storage-engines/foundationdb/fdbclient/tests/gcp_fixture.sh

## Purpose
This fixture configures blobstore tests to run against Google Cloud Storage. It creates scratch space, writes a GCS bearer-token credential file, returns host/bucket/credential configuration, and removes scratch data on shutdown.

## Important APIs, Types, And Functions
The public functions are `shutdown_gcp`, `create_gcp_dir`, `write_gcp_blob_credentials`, and `gcp_setup`. `gcp_setup` requires `GCS_APPLICATION_TOKEN` and `GCS_FDB_BUCKET`.

## Control Flow
Callers source the fixture, create a scratch directory, and call `gcp_setup build_dir scratch`. Setup validates required environment variables, chooses `storage.googleapis.com`, writes `{"accounts":{"@storage.googleapis.com":{"token":...}}}`, and prints `@host`, bucket, and credential-file path.

## State And Persistence Behavior
The fixture persists only a local credentials JSON file under the test scratch directory. It does not manipulate GCS buckets or objects directly.

## Dependencies And Integration Points
It integrates with `tests_common.sh` blobstore-provider selection and downstream blobstore URL construction using query parameter `p=gcs`. It depends on environment-provided credentials rather than cloud metadata APIs.

## Risks And Edge Cases
The credential JSON is constructed by string interpolation without escaping, so tokens containing JSON-significant characters could break the file. `gcp_setup` exits the parent script on missing environment variables. The `build_dir` parameter is accepted but unused.

## Test Signals
Expected signals are correct credentials-file creation, host returned with `@` prefix, selected bucket from `GCS_FDB_BUCKET`, and successful downstream `s3client` or bulkload operations in GCS provider mode.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/tests/gcp_fixture.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/tests/mocks3_fixture.sh -->
# sources/storage-engines/foundationdb/fdbclient/tests/mocks3_fixture.sh

## Purpose
This fixture starts a local MockS3Server by running the built `fdbserver` with role `mocks3server`. It provides a fast local blobstore backend for CTests when real S3/GCS is unavailable or undesired.

## Important APIs, Types, And Functions
Important globals are `MOCKS3_HOST`, `MOCKS3_PORT`, `MOCKS3_PID`, and `MOCKS3_LOG_FILE`. Functions are `start_mocks3`, `shutdown_mocks3`, and `get_mocks3_url`, exported for scripts that source the fixture.

## Control Flow
`start_mocks3` accepts optional build and persistence directories, discovers a build directory if omitted, validates `bin/fdbserver`, and tries up to ten ports. Each attempt starts `fdbserver --role mocks3server --public-address host:port --listen-address host:port`, optionally with persistence and log directories, waits a few seconds, treats process death plus bind-related log patterns as a retryable port conflict, and otherwise returns ready. Shutdown sends SIGTERM, waits up to about a second, sends SIGKILL if needed, logs unkillable process info, and removes the temporary stderr log.

## State And Persistence Behavior
It stores object data in the optional persistence directory, writes trace logs near that directory, and keeps PID/log-path state in shell globals. Failed bind attempts remove temporary logs and matching trace files to avoid false `Severity=40` test failures.

## Dependencies And Integration Points
The fixture depends on a built FoundationDB binary that supports `--role mocks3server`, POSIX process control, `mktemp`, and optional persistence directories. It integrates with `tests_common.sh`, `s3client_test.sh`, and `bulkload_test.sh` through URL/host/port variables.

## Risks And Edge Cases
Readiness is time-based after several seconds rather than an HTTP health check, so a slow or partially initialized server may still be reported ready. `set -e` in a sourced fixture can affect parent script behavior. Global `MOCKS3_PORT` is mutated on conflict and reused by URL builders.

## Test Signals
Signals are "MockS3Server ready" logs, a live tracked PID, successful `blobstore://mocks3:mocksecret@host:port` operations, and clean shutdown without lingering processes or severity-40 traces from failed bind attempts.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/tests/mocks3_fixture.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/tests/s3client_test.sh -->
# sources/storage-engines/foundationdb/fdbclient/tests/s3client_test.sh

## Purpose
This integration test exercises the FoundationDB `s3client` binary against real S3, MockS3Server, or mock-GCS mode. It validates file copy, directory copy, listing behavior, missing resources, and optional object-integrity checks.

## Important APIs, Types, And Functions
Major functions are `cleanup`, `filter_http_debug`, `run_s3client`, `resolve_to_absolute_path`, `upload_download`, `test_file_upload_and_download`, `test_file_upload_and_download_no_integrity_check`, `test_dir_upload_and_download`, `test_nonexistent_bucket`, `test_nonexistent_resource`, `test_empty_bucket`, `wait_for_files_in_listing`, `test_list_with_files`, and `test_ls_handling`.

## Control Flow
The script installs traps, sources `tests_common.sh`, determines `USE_S3`, parses optional explicit S3 settings, validates the build/scratch arguments, selects real S3, mock GCS, or MockS3Server, builds blobstore URL query strings, and runs the test cases. `run_s3client` centralizes common flags including HTTP verbosity, optional KMS encryption for real S3, integrity-check knob, TLS CA file, blob credentials, and log directory. Upload/download tests copy local files/directories up to blobstore, copy them back, remove the remote prefix, and `diff` local results. Listing tests account for S3 vs MockS3/Seaweed differences and include retry loops for eventual listing visibility.

## State And Persistence Behavior
The script creates scratch files, logs, credentials JSON, and optional MockS3 persisted objects. Remote state is created and removed under per-test path prefixes. Cleanup shuts down MockS3/AWS scratch unless preservation is requested.

## Dependencies And Integration Points
It depends on built `bin/s3client`, cloud/mock fixtures, shared helper matching functions, `diff`, `grep`, `awk`, and blobstore URL parsing by FoundationDB. It can use explicit `--host`, `--bucket`, `--region`, and `--blob-credentials-file` in real S3 mode.

## Risks And Edge Cases
The script’s behavior branches heavily by provider, so an assertion meaningful for S3 may be too loose for MockS3 or vice versa. HTTP debug filtering is text-pattern based and can mask output changes. Some checks only inspect command output rather than object metadata. The final `fi`/test block indentation is unusual but syntactically part of provider setup completion.

## Test Signals
Strong signals are successful round-trip `diff`, successful recursive and non-recursive listings with expected paths, correct empty/missing resource behavior for each provider, and clean remote-prefix removal after each test.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/tests/s3client_test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/tests/tests_common.sh -->
# sources/storage-engines/foundationdb/fdbclient/tests/tests_common.sh

## Purpose
This file centralizes Bash helper functions used by FoundationDB blobstore and bulkload CTests. It covers logging, cleanup watchdogs, preserve-data behavior, FDB data loading/verification, severity log scans, encryption key generation, provider detection, blobstore environment setup, and TLS CA discovery.

## Important APIs, Types, And Functions
Important helpers include `start_cleanup_watchdog`, `cancel_cleanup_watchdog`, `log`, `err`, `output_contains`, `output_matches`, `should_preserve_test_data`, `cleanup_with_preserve_check`, `make_key`, `has_data`, `has_nodata`, `load_data`, `clear_data`, `verify_data`, `is_fdb_source_dir`, `log_test_result`, `grep_for_severity40`, `test_fdbcli_status_json_for_bkup`, `create_encryption_key_file`, `get_use_s3_default`, `detect_blobstore_provider`, `setup_s3_environment`, and `setup_tls_ca_file`.

## Control Flow
Data helpers build deterministic key names from `FDB_KEY_PREFIX`, write timestamped values through `fdbcli`, clear the whole keyspace with `clearrange "" \xff`, and verify each stored value. Environment setup chooses GCS if GCS credentials are present, real S3 if `USE_S3=true`, otherwise MockS3Server, then sources the right fixture, creates scratch space, starts mock services as needed, builds `host`, `bucket`, `region`, `blob_credentials_file`, and `query_str`, and exports credentials/TLS variables for FoundationDB processes.

## State And Persistence Behavior
Global state includes `FDB_DATA`, `FDB_DATA_KEYCOUNT`, `FDB_KEY_PREFIX`, `TESTS_COMMON_DIR`, `CLEANUP_WATCHDOG_PID`, and provider variables made readonly by setup. It mutates the test database during load/clear operations and writes credential/key files in scratch directories. The watchdog can forcibly terminate process groups if cleanup exceeds its budget.

## Dependencies And Integration Points
The file integrates all S3/GCS/MockS3 fixtures and FDB cluster tests. It depends on `fdbcli`, `jq`, shell process tools, CA bundle paths, and Ginkgo-style CTest invocation around the scripts.

## Risks And Edge Cases
The cleanup watchdog has a broad `pkill -f` fallback based on script name, which is useful for hung CTests but dangerous if names collide. `verify_data` parses `fdbcli get` output with `sed`, making it sensitive to output format and punctuation. `setup_s3_environment` marks globals readonly, so callers cannot reconfigure after setup in the same shell.

## Test Signals
Signals are accurate pass/fail logs, successful FDB data round trips, provider-specific environment variables exported, preserved scratch paths printed when requested, and `grep_for_severity40` returning failure on high-severity traces.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/tests/tests_common.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/versions.h.cmake -->
# sources/storage-engines/foundationdb/fdbclient/versions.h.cmake

## Purpose
This CMake template generates a tiny C/C++ header containing FoundationDB version and package-name macros.

## Important APIs, Types, And Functions
It emits `FDB_VT_VERSION` from `${FDB_VERSION}` and `FDB_VT_PACKAGE_NAME` from `${FDB_PACKAGE_NAME}` behind `#pragma once`.

## Control Flow
CMake configures the file by substituting variables during the build. Runtime code includes the generated header and reads compile-time string macros.

## State And Persistence Behavior
There is no runtime state. The generated header persists build metadata in the build output.

## Dependencies And Integration Points
It depends on the build system defining `FDB_VERSION` and `FDB_PACKAGE_NAME`. Consumers can use it to stamp binaries or generated versioned artifacts.

## Risks And Edge Cases
Missing or malformed CMake variables would produce empty or invalid macro strings. Because this is a template, source review must distinguish template placeholders from final generated values.

## Test Signals
Build tests should verify the configured header exists and contains the expected version/package values for a given build configuration.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/versions.h.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/vexillographer/c.cs -->
# sources/storage-engines/foundationdb/fdbclient/vexillographer/c.cs

## Purpose
This C# binding writer generates the C options header for FoundationDB from parsed option metadata. It emits C enums grouped by option scope.

## Important APIs, Types, And Functions
Class `c` implements `BindingWriter`. `getCLine` formats an individual enum entry and optional parameter comment. `writeCEnum` emits one `typedef enum` for a `Scope`. `writeFiles` writes the full generated header with include guards, license text, and all scope enums.

## Control Flow
`writeFiles` opens the target file, writes a fixed header, iterates every `Scope`, filters options for that scope, and calls `writeCEnum`. Empty scopes receive a `DUMMY_DO_NOT_USE` placeholder for C compatibility.

## State And Persistence Behavior
The writer persists one generated header file and does not retain state beyond local formatting variables. It can overwrite existing generated output with `FileMode.Create`.

## Dependencies And Integration Points
It depends on `Option`, `Scope`, `ParamType`, and `BindingWriter` from `vexillographer.cs`. It integrates with build generation for `fdb_c_options.g.h`-style artifacts consumed by C API users.

## Risks And Edge Cases
Option comments and parameter descriptions are interpolated directly into comments and enum metadata; malformed XML text can produce awkward generated comments. Hidden options are still emitted, with an advisory comment. Empty-scope placeholders must not collide with real option names.

## Test Signals
Generation tests should compare enum prefixes such as `FDB_NET_OPTION_`, values, hidden-parameter comments, dummy placeholder behavior, newline style, and successful C compilation of the generated header.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/vexillographer/c.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/vexillographer/cpp.cs -->
# sources/storage-engines/foundationdb/fdbclient/vexillographer/cpp.cs

## Purpose
This C# binding writer generates C++ option enum and metadata files from FoundationDB option definitions. It writes a header containing scoped option structs and a source file initializing `FDBOptionInfoMap` instances.

## Important APIs, Types, And Functions
Class `cpp` implements `BindingWriter`. `writeCppEnum` emits `struct FDB<Scope>s` with nested `enum Option`. `getCInfoLine` formats `ADD_OPTION_INFO` calls. `writeCppInfo` emits static map definitions and `init` methods. `writeFiles` writes `<fileName>.h` and `<fileName>.cpp`.

## Control Flow
Generation opens the header, emits guards and `fdbclient/FDBOptions.h`, iterates scopes for enum structs, then opens the `.cpp`, includes the generated header, and iterates scopes again for metadata initialization.

## State And Persistence Behavior
It creates or overwrites two generated files. The generated runtime state is the static `FDBOptionInfoMap` per scope, populated by generated `init()` methods.

## Dependencies And Integration Points
It reuses `c.getCLine` for enum formatting and relies on C++ macros/types from `FDBOptions.h`. It integrates generated option metadata with C++ client configuration and introspection.

## Risks And Edge Cases
String fields are inserted into C++ string literals without visible escaping in this writer, so XML descriptions containing quotes or backslashes could break generated code. Empty scopes produce empty enums here rather than the C dummy placeholder behavior. Metadata must stay synchronized with enum values.

## Test Signals
Signals include compiling generated `.h/.cpp`, validating `ADD_OPTION_INFO` fields for hidden/persistent/sensitive/default flags, and comparing C and C++ enum numeric values for the same XML input.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/vexillographer/cpp.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/vexillographer/java.cs -->
# sources/storage-engines/foundationdb/fdbclient/vexillographer/java.cs

## Purpose
This C# binding writer generates Java option classes, enums, and `FDBException` predicate helpers from the shared FoundationDB option XML.

## Important APIs, Types, And Functions
Key helpers are `formatComment`, `replaceTicks`, `getEnum`, `toCamelCase`, `toSetFuncName`, `toPredicateFuncName`, `getJavaTypeName`, `writeOptionsClass`, `writePredicateClass`, `writeEnumClass`, and `writeFiles`. `scopeDocOptions` controls public visibility and whether a scope becomes a settable options class or enum.

## Control Flow
For each `Scope`, `writeFiles` chooses an output Java file: settable option scopes get `<Scope>s.java`, `ErrorPredicate` gets `FDBException.java`, and non-settable scopes get enum files. Hidden options are skipped. Comments are converted to Javadoc, double-backtick spans become `{@code ...}`, deprecated comments add `@Deprecated`, and parameterized options get typed setter methods.

## State And Persistence Behavior
The writer creates multiple Java files in an existing output directory. Runtime state in generated classes is minimal: option code constants and methods that call `setOption` or `FDB.evalErrorPredicate`.

## Dependencies And Integration Points
Generated output targets package `com.apple.foundationdb` and integrates with Java binding classes such as `OptionsSet`, `OptionConsumer`, `Transaction`, `Database`, and `FDBException`. It depends on option metadata parsed by `vexillographer.cs`.

## Risks And Edge Cases
`replaceTicks` throws on unmatched double ticks, so documentation formatting can fail generation. Output newline is set to `"\r"`, which is unusual and may affect diff/test expectations. Java string/comment escaping is limited; problematic XML descriptions can break Javadoc or source.

## Test Signals
Tests should compile generated Java, verify hidden options are absent, deprecated options are annotated, error predicates call the right native codes, and malformed double-tick comments fail generation predictably.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/vexillographer/java.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/vexillographer/python.cs -->
# sources/storage-engines/foundationdb/fdbclient/vexillographer/python.cs

## Purpose
This C# binding writer generates a Python module containing dictionaries of FoundationDB options grouped by scope.

## Important APIs, Types, And Functions
Class `python` implements `BindingWriter`. `typeMap` maps `ParamType` to Python type objects (`type(None)`, `type(0)`, `type('')`, `type(b'')`). `getPythonLine` formats a dictionary entry, `writePythonDict` emits one scope dictionary, and `writeFiles` writes the full module.

## Control Flow
The writer emits a fixed Python API license/import header, iterates all scopes, filters out hidden options, and writes dictionaries keyed by option name. Each value tuple contains numeric code, comment, expected Python parameter type, and optional parameter description.

## State And Persistence Behavior
It creates or overwrites one generated Python file. The generated module has static dictionary state only.

## Dependencies And Integration Points
Generated dictionaries are consumed by the Python binding option layer to validate option names/types and map them to C API codes. The source depends on shared `Option`/`Scope`/`ParamType` metadata.

## Risks And Edge Cases
Descriptions and parameter descriptions are interpolated into quoted Python strings without robust escaping. Hidden options are omitted, so consumers needing hidden/testing options cannot use this generated map. The embedded copyright range in this older C# writer differs from newer 2026 files.

## Test Signals
Importing the generated Python module, checking dictionary contents/types, and passing comments with quotes or bytes parameters through generation are useful test signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/vexillographer/python.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/vexillographer/ruby.cs -->
# sources/storage-engines/foundationdb/fdbclient/vexillographer/ruby.cs

## Purpose
This C# binding writer generates Ruby option metadata hashes under module `FDB`.

## Important APIs, Types, And Functions
Class `ruby` implements `BindingWriter`. `typeMap` maps option parameter types to representative Ruby values (`nil`, `0`, `''`). `getRubyLine` formats each option entry. `writeRubyHash` emits one class variable hash per scope, and `writeFiles` writes the Ruby module.

## Control Flow
The writer emits a fixed Ruby API license/header, iterates scopes except `ErrorPredicate`, filters out hidden options, writes `@@<Scope>` hashes with uppercase option names, and closes the `FDB` module.

## State And Persistence Behavior
It creates or overwrites one generated Ruby file. Generated state consists of module class-variable hashes used by the Ruby binding.

## Dependencies And Integration Points
It depends on the common option model in `vexillographer.cs` and integrates with the Ruby binding’s option validation/dispatch code.

## Risks And Edge Cases
String escaping is minimal for comments and parameter descriptions, so XML text containing quotes can break Ruby output. Error predicates are intentionally skipped, which must match Ruby binding expectations. Bytes and string parameters both map to `''`, losing type distinction at this metadata level.

## Test Signals
Tests should load the generated Ruby file, validate expected class-variable hashes and numeric codes, confirm hidden/error-predicate exclusions, and exercise option descriptions with special characters.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/vexillographer/ruby.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/vexillographer/vexillographer.cs -->
# sources/storage-engines/foundationdb/fdbclient/vexillographer/vexillographer.cs

## Purpose
This is the original C# option-code generator driver. It parses FoundationDB option XML and dispatches to a language-specific `BindingWriter` implementation for C, C++, Java, Ruby, or Python.

## Important APIs, Types, And Functions
It defines `Scope`, `ParamType`, `Option`, `BindingWriter`, and static class `vexillographer`. Important methods are `Main`, `usage`, `parseOptions`, `Scope.getDescription`, `AttributeOrNull`, and `AttributeNonNull`. `Option` exposes `isDeprecated()` and `getParameterComment()`.

## Control Flow
`Main` validates at least three arguments, parses options from XML using the requested binding name, loads `vexillographer.<binding>` by reflection, constructs it, and invokes `writeFiles`. `parseOptions` walks `<Options>/<Scope>/<Option>`, parses enum values and flags, honors comma-separated `disableOn` entries for the selected binding, and returns a list of `Option` objects.

## State And Persistence Behavior
The driver stores parsed option definitions in memory and delegates all file persistence to the selected writer. It has no durable state of its own.

## Dependencies And Integration Points
It depends on LINQ-to-XML and the sibling language writer classes. The generated artifacts are part of FoundationDB binding build pipelines and must stay consistent across languages.

## Risks And Edge Cases
Most parse exceptions are swallowed into return code `1`, reducing diagnostic detail. Reflection failures print stack traces and return `31`. XML attributes are assumed present for scope names, option names, and codes; missing required data aborts generation. Binding names must match class names exactly.

## Test Signals
Driver tests should cover successful generation for each binding, `disableOn` filtering, missing required attributes, unknown binding names, deprecated comments, hidden/persistent/sensitive flags, and scope-description mappings.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/vexillographer/vexillographer.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/vexillographer/vexillographer.py -->
# sources/storage-engines/foundationdb/fdbclient/vexillographer/vexillographer.py

## Purpose
This Python script is a newer option-code generator for FoundationDB bindings. It parses the same option XML model and can generate C, C++, Python, Ruby, and a consolidated Java artifact.

## Important APIs, Types, And Functions
It defines `Scope`, `ParamType`, `Option`, `parse_options`, and writer functions `write_c`, `write_cpp`, `write_python`, `write_ruby`, and `write_java`. `WRITERS` maps CLI language names to writer functions, and `main` uses `argparse` to select the writer.

## Control Flow
`main` parses `input`, `lang`, and `output`, loads XML with `ElementTree`, filters options whose `disableOn` contains the selected binding, then calls the chosen writer. The C writer emits scope enums with dummy placeholders for empty scopes. The C++ writer emits `.h` and `.cpp` files. Python and Ruby writers emit static metadata dictionaries/hashes. The Java writer emits one `FDBOptions` class containing enums and option-info arrays.

## State And Persistence Behavior
The script has no persistent state beyond generated files. Writers open output files with newline control and overwrite existing generated artifacts.

## Dependencies And Integration Points
It depends only on Python standard library modules. It is a build-time replacement/parallel implementation for the older C# vexillographer and integrates with binding code generation.

## Risks And Edge Cases
The Java output shape is not identical to the C# writer: it creates a consolidated `FDBOptions` class rather than many package classes plus `FDBException`. Several writers interpolate comments into source strings without full language-specific escaping. `parse_options` calls enum constructors directly, so unknown scope/param values raise exceptions with Python stack traces.

## Test Signals
Signals include byte-for-byte or semantic comparison with expected generated artifacts, `argparse` choice validation, `disableOn` filtering, empty-scope dummy behavior for C, generated C++ compilation, Python/Ruby import/load, and Java compilation against the target binding shape.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/vexillographer/vexillographer.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/zipf.c -->
# sources/storage-engines/foundationdb/fdbclient/zipf.c

## Purpose
This C file implements the YCSB-derived Zipfian integer generator declared in `zipf.h`. It produces skewed integer samples over a configured inclusive range.

## Important APIs, Types, And Functions
Public functions are `zipfian_generator3`, `zipfian_generator`, and `zipfian_next`; internal helpers include `zipfian_generator4`, `zipfian_generator2`, `next_int`, `rand_double`, `zetastatic2`, `zeta2`, `zetastatic`, and `zeta`. Global static variables hold item count, base, theta/alpha/zeta values, and count tracking.

## Control Flow
Initialization computes `items`, `base`, `theta`, `zeta2theta`, `alpha`, `zetan`, `countforzeta`, and `eta`, then calls `zipfian_next()` once to warm the generator. `zipfian_next` delegates to `next_int(items)`. `next_int` updates zeta if item count changed, draws `u = rand()/RAND_MAX`, handles the first two high-probability items specially, and otherwise computes the selected item with the Zipfian power formula.

## State And Persistence Behavior
All generator state is process-global and mutable. There is no persistence, no per-instance object state, and no locking. Randomness comes from the C library `rand()` global state; this file does not seed it.

## Dependencies And Integration Points
It depends on `<math.h>`, `<stdlib.h>`, and `fdbclient/zipf.h`. It is suitable for benchmark/test code that can tolerate global generator state.

## Risks And Edge Cases
The implementation is not thread-safe or reentrant. Invalid ranges, zero item counts, or `zipfianconstant` values near 1 can produce division/power edge cases. `allowitemcountdecrease` is always zero, so decreasing item counts do not recompute zeta through that branch. The disabled test block calls `next_value()`, which is not defined, indicating stale sample code.

## Test Signals
Tests should assert generated values stay within `[min,max]`, repeated initialization resets bounds, distribution is skewed toward low ranks, deterministic behavior follows `srand`, and concurrent use is either avoided or explicitly documented as unsafe.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/zipf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbctl/CMakeLists.txt -->
# sources/storage-engines/foundationdb/fdbctl/CMakeLists.txt

## Purpose
This build file defines the `fdbctl` static library target and optional gRPC/protobuf generation for the FoundationDB control service.

## Important APIs, Types, And Functions
It uses `fdb_find_sources(FDBCTL_SRCS)`, `add_flow_target(STATIC_LIBRARY NAME fdbctl SRCS ...)`, `target_include_directories`, `target_link_libraries`, conditional `generate_grpc_protobuf`, and a UBSAN link option.

## Control Flow
CMake discovers sources, creates the static library, exposes the `include` directory, links privately to `fdbclient`, and, when `WITH_GRPC` is enabled, generates protobuf/gRPC code from `protos/control_service.proto` and links it publicly. Under `USE_UBSAN`, it adds `-rdynamic`.

## State And Persistence Behavior
The file controls build artifacts only: a static library and generated protobuf sources/targets. It has no runtime state.

## Dependencies And Integration Points
The target integrates with the Flow build macros, FoundationDB client library, and optional gRPC/protobuf toolchain. Consumers need `WITH_GRPC` for the control service sources guarded by `FLOW_GRPC_ENABLED`.

## Risks And Edge Cases
When Go/grpc/protobuf generation settings change, generated target names must remain aligned with includes such as `fdbctl/control_service/control_service.pb.h`. If `WITH_GRPC` is off, much of the fdbctl C++ service code is compiled out.

## Test Signals
Build signals are successful `fdbctl` target creation with and without `WITH_GRPC`, generated proto headers available in include paths, and UBSAN builds linking with symbols.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbctl/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbctl/ControlCommands.cpp -->
# sources/storage-engines/foundationdb/fdbctl/ControlCommands.cpp

## Purpose
This file implements several gRPC-backed administrative commands for `fdbctl` when Flow gRPC is enabled. It covers coordinators, status, workers, include, kill, and shared utility reads from management/system special keys.

## Important APIs, Types, And Functions
Top-level handlers include `getCoordinators`, `changeCoordinators`, `getStatus`, `getWorkers`, `include`, and `kill`. Helpers include `getTransaction`, `localityDataToProto`, `addInterfacesFromKVs`, `getWorkerInterfaces`, `utils::getSpecialKeysFailureErrorMessage`, `utils::getStorageServerInterfaces`, and `utils::getWorkersProcessData`.

## Control Flow
Handlers create transactions, set required special/system key options, run reads/writes through `ThreadFuture` bridged by `safeThreadFutureToFuture`, and retry through `tr->onError`. Coordinator change writes special keys and expects commit to fail with `commit_unknown_result`; special-key failure messages are inspected to distinguish not-enough-machines and same-address results. Worker listing reads process classes and worker list keys, merges class data, filters tester processes, and writes `Worker` protos. `kill` resolves worker interfaces and calls `db->rebootWorker` for all or selected addresses.

## State And Persistence Behavior
Read-only operations fetch special/system key state. Mutating operations write special keys for coordinator changes and inclusion, or send reboot requests to workers. No local persistence is used.

## Dependencies And Integration Points
It depends on FoundationDB management APIs, special key ranges, worker/process metadata encoders, Flow actors/futures, gRPC statuses, Boost string splitting/joining, JSON schema validation, and generated `control_service` protos.

## Risks And Edge Cases
This code is compiled only with `FLOW_GRPC_ENABLED`. Some requests are partially implemented: `kill` ignores `duration_seconds`, and `include` parses only `addresses` while declaring but never populating `localities`. Several failure paths use `ASSERT`, which is unsuitable for graceful API errors if cluster state is malformed. `changeCoordinators` has a TODO to reject disjoint coordinator sets.

## Test Signals
Useful tests issue gRPC requests against a test cluster for coordinator get/change, status JSON retrieval, worker listing, include all/specific, invalid address parsing, unknown kill targets, and special-key failure translation.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbctl/ControlCommands.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbctl/ControlService.cpp -->
# sources/storage-engines/foundationdb/fdbctl/ControlService.cpp

## Purpose
This file provides the minimal implementation for `ControlServiceImpl` construction when Flow gRPC is enabled. The actual RPC method definitions live mostly in the header through a macro.

## Important APIs, Types, And Functions
The only implemented function is `ControlServiceImpl::ControlServiceImpl(Reference<IDatabase> db)`, which initializes the generated gRPC service base and stores the database reference in `db_`.

## Control Flow
Construction is direct and has no branching. RPC handling flow is defined in `ControlService.h`, where each gRPC method calls `handleRequestOnMainThread`.

## State And Persistence Behavior
The service stores an in-memory `Reference<IDatabase>`. It does not persist anything itself; command handlers mutate cluster state through the database reference.

## Dependencies And Integration Points
It depends on `ControlService.h`, `fmt`, `<chrono>`, and `FLOW_GRPC_ENABLED`. It integrates the generated gRPC service with FoundationDB’s database handle.

## Risks And Edge Cases
This source file is intentionally sparse, so constructor changes must be coordinated with header-defined RPC behavior. Unused includes may drift. No lifecycle/shutdown logic exists here.

## Test Signals
Construction tests should verify the service can be instantiated with a database reference in gRPC builds and that linked RPC methods resolve from the header-generated overrides.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbctl/ControlService.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbctl/ExcludeCommand.cpp -->
# sources/storage-engines/foundationdb/fdbctl/ExcludeCommand.cpp

## Purpose
This file implements gRPC exclusion management for `fdbctl`: excluding addresses/localities, checking in-progress exclusions, and reporting excluded/failed status.

## Important APIs, Types, And Functions
Utility readers include `utils::getExcludedServers`, `getFailedServers`, `getExcludedLocalities`, `getFailedLocalities`, and `getInProgressExclusion`. Mutating/control functions include `excludeServersAndLocalities`, `checkForExcludingServers`, `exclude`, and `excludeStatus`.

## Control Flow
Status helpers read management special-key ranges and strip range prefixes. `exclude` concurrently fetches worker process data and storage server interfaces, builds exclusion sets from requested localities and processes, validates non-empty input, writes exclusions/failed exclusions with optional force flags, then waits or checks in-progress exclusions according to `no_wait`. It populates response fields for excluded addresses, data movement completion, and absent addresses. `excludeStatus` aggregates excluded, failed, locality, and in-progress data into the reply.

## State And Persistence Behavior
Exclusion state is persisted in FoundationDB management special keys under excluded/failed address and locality ranges. Force options are written as special option keys in the same transaction. Local state consists of temporary sets/maps of worker and storage addresses.

## Dependencies And Integration Points
It depends on `ControlCommands.h`, FoundationDB management/special-key APIs, storage server interfaces, worker locality helpers such as `getAddressesByLocality`, Flow actors, Boost joining, and gRPC status types.

## Risks And Edge Cases
`ExcludeRequest.hosts` and `all` are defined in the proto but are not handled here; only `localities` and `processes` are considered. Invalid process addresses return `INVALID_ARGUMENT` with an empty message. The internal error format `fmt::format("error: ", e.name())` omits the error name because the format string lacks a placeholder. Waiting uses polling with jitter rather than watches. A stray `I` appears in the license comment.

## Test Signals
Tests should cover process exclusion, locality exclusion, failed exclusion, force flags, `no_wait`, absent-address reporting, in-progress migration reporting, include/exclude round trips, unsupported `hosts`/`all` fields, and special-key API failure propagation.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbctl/ExcludeCommand.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbctl/include/fdbctl/ControlCommands.h -->
# sources/storage-engines/foundationdb/fdbctl/include/fdbctl/ControlCommands.h

## Purpose
This header declares the gRPC command-handler API and shared special-key constants for `fdbctl` when Flow gRPC support is enabled.

## Important APIs, Types, And Functions
It declares handlers for coordinators, configure, status, workers, include, exclude, exclude status, and kill. The `utils` namespace declares special-key error decoding and worker/storage/exclusion readers. The `special_keys` namespace defines coordinator, excluded/failed server, excluded/failed locality, force-option, in-progress-exclusion, and worker-interface verification keys/ranges.

## Control Flow
The header has no executable control flow. It defines the contract used by `ControlService.h` and implemented across `ControlCommands.cpp` and `ExcludeCommand.cpp`.

## State And Persistence Behavior
The constants identify FoundationDB special-key state that command handlers read and mutate. No local state is declared except function signatures.

## Dependencies And Integration Points
It includes FoundationDB client/storage interfaces, Flow gRPC support, and generated control-service protobuf/gRPC headers. It is the coupling point between generated RPC messages and Flow actor command implementations.

## Risks And Edge Cases
`configure` is declared but not implemented in the visible files and its handler is commented out in the service. Constants are duplicated with a TODO to point fdbcli code here, so drift with other management paths is possible.

## Test Signals
Compile/link tests with `FLOW_GRPC_ENABLED` should catch missing handler implementations. Behavioral tests should verify all special-key constants match the management API paths expected by FoundationDB.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbctl/include/fdbctl/ControlCommands.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbctl/include/fdbctl/ControlService.h -->
# sources/storage-engines/foundationdb/fdbctl/include/fdbctl/ControlService.h

## Purpose
This header adapts generated gRPC service methods to FoundationDB Flow actor handlers and ensures requests run on the main Flow thread with deadline handling.

## Important APIs, Types, And Functions
The `DEFINE_GRPC_HANDLER` macro defines synchronous gRPC overrides. Template `grpcHandlerWrapper` applies deadline-derived timeout handling and maps Flow errors to gRPC statuses. Class `ControlServiceImpl` derives from generated `fdbctl::ControlService::Service` and defines handlers for `GetCoordinators`, `ChangeCoordinators`, `GetStatus`, `GetWorkers`, `Include`, `Exclude`, `ExcludeStatus`, and `Kill`.

## Control Flow
Each gRPC method calls `handleRequestOnMainThread`, which schedules `grpcHandlerWrapper` through `onMainThread(...).getBlocking()`. The wrapper reads the gRPC deadline, uses `CLIENT_KNOBS->GRPC_CTL_SERVICE_DEFAULT_TIMEOUT` when no deadline is set, rejects expired deadlines, awaits the Flow handler under `timeoutError`, maps `timed_out` to `DEADLINE_EXCEEDED`, and maps other Flow errors to `INTERNAL`.

## State And Persistence Behavior
`ControlServiceImpl` stores a database reference. The wrapper itself is stateless; persistence occurs only in delegated command handlers.

## Dependencies And Integration Points
It depends on generated gRPC/protobuf code, `ControlCommands.h`, Flow thread helpers, generic actors, client knobs, and gRPC server contexts.

## Risks And Edge Cases
Deadline conversion truncates to whole seconds; sub-second deadlines can become zero and be rejected. Blocking on `getBlocking()` ties gRPC worker threads to Flow main-thread execution. Proto-declared RPCs `ConfigureAutoSuggest`, `Configure`, and `Maintenance` are not wired here, with `Configure` explicitly commented.

## Test Signals
Tests should cover deadline exceeded before execution, operation timeout, successful main-thread dispatch, internal error mapping, and reflection/registration showing only implemented RPCs are callable.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbctl/include/fdbctl/ControlService.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbctl/protos/control_service.proto -->
# sources/storage-engines/foundationdb/fdbctl/protos/control_service.proto

## Purpose
This proto defines the public gRPC API for `fdbctl` cluster control operations, including coordinator changes, configuration, status, worker listing, include/exclude, kill, and maintenance.

## Important APIs, Types, And Functions
The `ControlService` service declares RPCs `GetCoordinators`, `ChangeCoordinators`, `ConfigureAutoSuggest`, `Configure`, `GetStatus`, `GetWorkers`, `Include`, `Exclude`, `ExcludeStatus`, `Kill`, and `Maintenance`. Message types include `Worker`, coordinator request/reply types, `ConfigureRequest/Reply`, `GetStatusReply`, `IncludeRequest/Reply`, `ExcludeRequest/Reply`, `ExcludeStatusReply`, `KillRequest/Reply`, and `MaintenanceRequest/Reply`.

## Control Flow
The proto has no executable flow, but it defines request/response contracts used by generated C++ and other language bindings. Enums encode configuration choices such as redundancy mode, storage engine, storage migration type, configure result, and maintenance operation/result.

## State And Persistence Behavior
Messages model cluster state and desired mutations. Actual persistence is in FoundationDB special keys and management APIs implemented by server handlers.

## Dependencies And Integration Points
It sets Go and Java package options and is consumed by CMake `generate_grpc_protobuf`. The generated C++ headers are included by fdbctl service/command code.

## Risks And Edge Cases
The proto surface is ahead of current C++ service wiring: configure autosuggest, configure, maintenance, exclude `hosts`, exclude `all`, include `localities`, include reply counts, and kill duration are not fully implemented in the observed handlers. Proto3 `optional` fields require generated-code support compatible with the toolchain.

## Test Signals
Signals include generated-code compilation, gRPC reflection/contract tests, request compatibility across Go/Java/C++, and end-to-end tests proving every declared field either works or is explicitly rejected.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbctl/protos/control_service.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbkubernetesmonitor/.golangci.yml -->
# sources/storage-engines/foundationdb/fdbkubernetesmonitor/.golangci.yml

## Purpose
This configuration defines lint policy for the `fdb-kubernetes-monitor` Go module.

## Important APIs, Types, And Functions
It disables all linters by default and enables a curated set including `asciicheck`, `bodyclose`, `errcheck`, `errorlint`, `gofmt`, `govet`, `staticcheck`, `stylecheck`, `unused`, and others. It configures exclusions for generated files, package comments, test dot-imports, deprecation warnings, shadow warnings, and depguard allowlists.

## Control Flow
`golangci-lint` reads this file, applies file/rule exclusions, runs enabled linters with a 10-minute timeout, and allows parallel runners.

## State And Persistence Behavior
No runtime state is affected. It influences developer/CI lint results.

## Dependencies And Integration Points
It integrates with the Go module’s CI/developer workflow and restricts dependencies to standard library, FoundationDB, Kubernetes/controller-runtime, Ginkgo/Gomega, Prometheus, logr, pflag, and fsnotify families.

## Risks And Edge Cases
Several potentially useful linters are commented out, and broad exclusions for deprecation, package comments, and shadowing reduce strictness. `exportloopref` is obsolete in newer Go versions, so lint tool version drift may matter.

## Test Signals
The signal is a clean `golangci-lint run` over the module, with generated files ignored and dependency imports accepted by depguard.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbkubernetesmonitor/.golangci.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbkubernetesmonitor/CMakeLists.txt -->
# sources/storage-engines/foundationdb/fdbkubernetesmonitor/CMakeLists.txt

## Purpose
This CMake file integrates the Go-based `fdb-kubernetes-monitor` binary and its Go tests into the FoundationDB build.

## Important APIs, Types, And Functions
It locates `go` and `gofmt`, collects Go sources, declares `${CMAKE_BINARY_DIR}/bin/fdb-kubernetes-monitor`, adds a custom command running `go build -o ... .`, creates an `ALL` custom target, and registers `go test -race ./...` plus a gofmt diff test.

## Control Flow
If Go is missing or the platform is Windows, it returns early. Otherwise CMake tracks `.go`, `go.mod`, and `go.sum` as dependencies, builds from the module directory, and adds CTest entries for race-enabled tests and formatting.

## State And Persistence Behavior
The build persists the monitor binary in the build `bin` directory. Tests may create Go test artifacts but no runtime state is encoded here.

## Dependencies And Integration Points
It depends on a local Go toolchain and module files. It integrates a Go subproject into the broader CMake/CTest workflow.

## Risks And Edge Cases
`file(GLOB_RECURSE ...)` can require CMake regeneration to detect new files depending on generator behavior. Race tests are slower and may require cgo/toolchain support. Windows builds silently skip the target.

## Test Signals
Build signals are a present `bin/fdb-kubernetes-monitor`, successful `fdb-kubernetes-monitor-go-tests`, and empty `gofmt -d` output.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbkubernetesmonitor/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbkubernetesmonitor/api/.testdata/default_config.json -->
# sources/storage-engines/foundationdb/fdbkubernetesmonitor/api/.testdata/default_config.json

## Purpose
This JSON fixture defines a sample `ProcessConfiguration` for API tests of the Kubernetes monitor.

## Important APIs, Types, And Functions
The fixture sets version `6.3.15` and an `arguments` array combining literal values, environment lookups, process-number arithmetic, and concatenation. It covers `--cluster-file`, public/listen addresses, datadir, class, and locality flags.

## Control Flow
Tests decode the JSON into `ProcessConfiguration`, then `GenerateArguments(1, env)` expands environment values and process-number expressions. The port expression uses process number `1`, multiplier `2`, and offset `4499` to produce `4501`.

## State And Persistence Behavior
This is static test data. It references `.testdata/fdb.cluster` and `.testdata/data/<process>` paths but does not create them by itself.

## Dependencies And Integration Points
It integrates with `config_test.go` and the JSON unmarshalling behavior of `Version`, `ProcessConfiguration`, and `Argument`.

## Risks And Edge Cases
Because this fixture is a representative default config, changes to argument ordering or defaults can break exact-element tests. It does not exercise IP-list selection or `runServers`.

## Test Signals
The key signal is exact generated argument order and values for the provided environment map, plus version decoding to major/minor/patch fields.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbkubernetesmonitor/api/.testdata/default_config.json -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbkubernetesmonitor/api/.testdata/test_env.sh -->
# sources/storage-engines/foundationdb/fdbkubernetesmonitor/api/.testdata/test_env.sh

## Purpose
This shell fixture exports local environment variables for Kubernetes monitor API/manual tests.

## Important APIs, Types, And Functions
It sets `FDB_PUBLIC_IP`, `FDB_POD_IP`, `FDB_ZONE_ID`, `FDB_MACHINE_ID`, `FDB_INSTANCE_ID`, `KUBERNETES_SERVICE_HOST`, and `KUBERNETES_SERVICE_PORT`.

## Control Flow
There is no branching. Sourcing the file populates the shell environment for configs that use environment-backed arguments.

## State And Persistence Behavior
It mutates only the current shell environment and persists no files.

## Dependencies And Integration Points
It pairs with `.testdata/default_config.json` and any monitor code that reads Kubernetes/FDB environment variables.

## Risks And Edge Cases
Values are localhost/docker-desktop oriented and not representative of real pod networking. Tests that rely on the host system environment may behave differently from tests that pass an explicit env map.

## Test Signals
A simple signal is that sourcing this file allows default configuration argument generation without missing-environment errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbkubernetesmonitor/api/.testdata/test_env.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbkubernetesmonitor/api/annotations.go -->
# sources/storage-engines/foundationdb/fdbkubernetesmonitor/api/annotations.go

## Purpose
This Go file centralizes Kubernetes annotation keys used by the FoundationDB Kubernetes monitor and launcher ecosystem.

## Important APIs, Types, And Functions
Constants include `CurrentConfigurationAnnotation`, `EnvironmentAnnotation`, `OutdatedConfigMapAnnotation`, `DelayShutdownAnnotation`, `ClusterFileChangeDetectedAnnotation`, and `IsolateProcessGroupAnnotation`.

## Control Flow
There is no executable control flow. Other packages import these constants to read/write annotations consistently.

## State And Persistence Behavior
The constants name persistent Kubernetes Pod or ConfigMap annotations. The file itself does not access the Kubernetes API.

## Dependencies And Integration Points
It integrates with monitor logic that stores current launcher configuration/environment, detects outdated config maps, delays shutdown, flags cluster-file changes, and isolates process groups for debugging.

## Risks And Edge Cases
Annotation key drift breaks interoperability with the operator/launcher. Values such as durations or booleans must be validated by consuming code, not here.

## Test Signals
Tests should assert exact annotation string values where other components rely on them, especially upgrade/backward-compatibility tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbkubernetesmonitor/api/annotations.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbkubernetesmonitor/api/config.go -->
# sources/storage-engines/foundationdb/fdbkubernetesmonitor/api/config.go

## Purpose
This Go file models monitor process configuration and expands declarative argument specifications into concrete command-line arguments for FDB processes.

## Important APIs, Types, And Functions
Types are `ProcessConfiguration`, `Argument`, and `ArgumentType`. Constants define `Literal`, `Concatenate`, `Environment`, `ProcessNumber`, and `IPList` argument types. Methods include `Argument.GenerateArgument`, `Argument.LookupEnv`, `ProcessConfiguration.GenerateArguments`, and `ProcessConfiguration.ShouldRunServers`.

## Control Flow
`GenerateArguments` optionally prepends `BinaryPath`, then expands each `Argument`. Literal arguments return `Value`; concatenation recursively expands child values; process-number arguments apply optional multiplier then offset; environment and IP-list arguments call `LookupEnv`. `LookupEnv` checks an explicit map first, then `os.LookupEnv`; IP-list mode splits comma-separated values, parses IPs, and returns the first matching IPv4 or IPv6 address.

## State And Persistence Behavior
Configuration is plain JSON-serializable in-memory state. Environment lookup reads process environment but does not mutate it. `ShouldRunServers` defaults nil `RunServers` to true but returns false for a nil configuration receiver.

## Dependencies And Integration Points
It depends on `net`, `os`, string/strconv helpers, and `k8s.io/utils/pointer`. It integrates with launcher/monitor JSON configuration and process startup code.

## Risks And Edge Cases
IP-list matching skips unparsable entries silently and returns the first matching family, which may surprise callers with multiple addresses. Unsupported argument types and IP families return errors. Recursive concatenate can propagate missing env errors but has no cycle concept because JSON is tree-shaped.

## Test Signals
Existing tests cover default config expansion, `BinaryPath`, environment present/missing, IPv4/IPv6 selection, invalid IP family, JSON marshalling, and default run-server behavior should be added if absent.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbkubernetesmonitor/api/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbkubernetesmonitor/api/config_test.go -->
# sources/storage-engines/foundationdb/fdbkubernetesmonitor/api/config_test.go

## Purpose
This Ginkgo/Gomega test file validates JSON configuration loading and command-argument generation for the Kubernetes monitor API.

## Important APIs, Types, And Functions
Helper `loadConfigFromFile` decodes JSON into `ProcessConfiguration`. Test scenarios exercise `GenerateArguments`, `Argument.GenerateArgument`, IP-list handling, and JSON marshalling of `ProcessConfiguration` with `Version`.

## Control Flow
Tests load `.testdata/default_config.json`, inject environment maps, and assert exact generated argument arrays. Environment tests vary whether `FDB_ZONE_ID` is present. IP-list tests vary family, address order, malformed entries, and unsupported family. The marshalling test serializes a config with version `7.1.57` and expects compact JSON.

## State And Persistence Behavior
Tests read fixture files and do not persist state. Environment behavior is mostly isolated by passing explicit maps rather than mutating `os.Environ`.

## Dependencies And Integration Points
It depends on Ginkgo v2, Gomega, Go JSON decoding, and the `.testdata` fixtures. It is run by `go test -race ./...` from CMake.

## Risks And Edge Cases
Exact argument ordering makes intentional reorderings test-breaking. Tests do not cover nil `ProcessConfiguration`, `RunServers`, unknown argument types, nested concatenate failures, or fallback to actual OS environment.

## Test Signals
The suite provides strong regression signals for default argument generation, binary path prepending, missing env errors, IP family selection, invalid family errors, and version JSON formatting.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbkubernetesmonitor/api/config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbkubernetesmonitor/api/suite_test.go -->
# sources/storage-engines/foundationdb/fdbkubernetesmonitor/api/suite_test.go

## Purpose
This file initializes the Ginkgo test suite for the Kubernetes monitor API package.

## Important APIs, Types, And Functions
`TestAPIs(t *testing.T)` registers the Gomega fail handler, sets the default eventual timeout to ten seconds, and runs specs named `FDB Kubernetes Monitor API`.

## Control Flow
Go’s test runner invokes `TestAPIs`; Ginkgo then discovers and runs specs in the package.

## State And Persistence Behavior
The only state change is Ginkgo’s package-level default eventual timeout. No files or external systems are mutated.

## Dependencies And Integration Points
It depends on `testing`, `time`, Ginkgo v2, and Gomega. It is required for the BDD-style tests in `config_test.go` and `version_test.go` to execute.

## Risks And Edge Cases
Package-wide timeout changes can affect future specs in the package. Dot-imports are intentionally allowed by lint exclusions.

## Test Signals
The signal is that `go test` discovers and runs the Ginkgo suite rather than reporting no tests or unregistered specs.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbkubernetesmonitor/api/suite_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbkubernetesmonitor/api/version.go -->
# sources/storage-engines/foundationdb/fdbkubernetesmonitor/api/version.go

## Purpose
This Go file defines a FoundationDB `Version` type with parsing, JSON serialization, comparison, compatibility, and next-version helpers for the Kubernetes monitor.

## Important APIs, Types, And Functions
`Version` stores major, minor, patch, and release-candidate numbers. Functions/methods include `MarshalJSON`, `UnmarshalJSON`, `ParseFdbVersion`, `String`, `Compact`, `IsAtLeast`, `GetBinaryVersion`, `IsProtocolCompatible`, `NextMajorVersion`, `NextMinorVersion`, `NextPatchVersion`, and `Equal`.

## Control Flow
`ParseFdbVersion` applies regex `(\d+)\.(\d+)\.(\d+)(-rc(\d+))?`, converts captures to integers, and treats missing/invalid rc as zero. JSON unmarshal trims quotes and delegates to parse. Comparisons proceed major, minor, patch, then RC rules where stable releases outrank release candidates of the same major/minor/patch.

## State And Persistence Behavior
The type is pure in-memory value state. JSON methods persist versions as strings in configuration documents.

## Dependencies And Integration Points
It depends on `regexp`, `strconv`, `strings`, and `fmt`. It integrates with monitor configs and binary/library copy logic that needs compact major.minor or full rc-aware versions.

## Risks And Edge Cases
The regex is not anchored, so strings like `prerelease-6.2.11` parse successfully; this is covered by tests but may be surprising. Invalid rc conversion falls back to zero, though the regex only captures digits. Protocol compatibility treats different release candidates as incompatible.

## Test Signals
Existing tests cover parse variants, JSON round trips, formatting, compatibility, next-version helpers, equality, and RC-aware `IsAtLeast` ordering.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbkubernetesmonitor/api/version.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbkubernetesmonitor/api/version_test.go -->
# sources/storage-engines/foundationdb/fdbkubernetesmonitor/api/version_test.go

## Purpose
This Ginkgo/Gomega suite validates `Version` parsing, JSON serialization, formatting, compatibility, equality, and ordering behavior.

## Important APIs, Types, And Functions
Tests exercise `json.Marshal`, `json.Unmarshal`, `ParseFdbVersion`, `Version.String`, `IsProtocolCompatible`, `NextMajorVersion`, `NextMinorVersion`, `NextPatchVersion`, `Equal`, and `IsAtLeast`.

## Control Flow
The suite runs grouped scenarios for JSON round trips, invalid strings, protocol compatibility across patch/minor/major/RC differences, accepted version-string patterns with prefixes/suffixes, formatting with and without RCs, next-version construction, equality, and RC/stable ordering.

## State And Persistence Behavior
The tests are pure and mutate no external state.

## Dependencies And Integration Points
They depend on Go JSON, Ginkgo, and Gomega. They protect behavior used by JSON process config and monitor upgrade logic.

## Risks And Edge Cases
Tests intentionally lock in unanchored parse behavior for prefixed/suffixed strings. They do not cover negative numbers, very large numeric components, malformed JSON types, or compact `GetBinaryVersion`.

## Test Signals
Failures indicate changed version compatibility semantics, JSON representation drift, or parser changes that could affect monitor upgrade and binary selection behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbkubernetesmonitor/api/version_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbkubernetesmonitor/copy.go -->
# sources/storage-engines/foundationdb/fdbkubernetesmonitor/copy.go

## Purpose
This Go file implements file-copy planning and atomic copy helpers for the Kubernetes monitor binary. It supports copying arbitrary files, FDB binaries, multiversion client libraries, and primary library aliases into shared output directories.

## Important APIs, Types, And Functions
Constants define test override env vars `TEST_LIBRARY_DIRECTORY` and `TEST_BINARY_DIRECTORY`. Functions are `copyFile`, `copyFiles`, `getCompactVersion`, `getBinaryDirectory`, `getLibraryPath`, and `getCopyDetails`. It also defines a compact-version regex `^(\d+)\.(\d+)`.

## Control Flow
`getCopyDetails` starts with user `copyFiles`, computes a default binary output directory based on execution mode and current container version, adds requested binaries from the binary directory, adds requested `libfdb_c_<version>.so` libraries from the library path, optionally maps the primary library to `libfdb_c.so`, and validates that every required copy file is also in `--copy-file`. `copyFiles` creates parent directories and calls `copyFile` for each mapping. `copyFile` opens the input, checks required non-empty files, writes to a temp file in the destination directory, preserves mode, and renames into place.

## State And Persistence Behavior
This code persists copied files into the output directory using temp-file-plus-rename for atomic replacement. It reads environment overrides for test binary/library directories and copies source file permissions to destination files.

## Dependencies And Integration Points
It depends on `os`, `path`, `regexp`, `fmt`, and `github.com/go-logr/logr`. It integrates with command-line execution modes elsewhere in the monitor and with the operator’s expected shared-binary layout.

## Risks And Edge Cases
`copyFile` defers closing the temp file but renames before close, which is usually fine on Unix but can be problematic on some platforms. If `os.Rename` fails, the temp file is not explicitly removed. Map iteration order in `copyFiles` is nondeterministic, so logs and partial-copy order vary. `getCompactVersion` accepts only leading major.minor and ignores patch/rc details for non-sidecar binary directories.

## Test Signals
Tests should verify atomic copy output, mode preservation, required empty-file rejection, required-file validation, env override directories, sidecar vs non-sidecar binary output paths, primary library aliasing, and compact-version parse errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbkubernetesmonitor/copy.go -->
