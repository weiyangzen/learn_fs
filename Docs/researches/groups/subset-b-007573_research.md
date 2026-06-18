# subset-b-007573 research

Grouped research for the requested Hadoop HDFS test resources and S3A module files. Each section is keyed by the original source path for deterministic reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/testXAttrConf.xml -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/testXAttrConf.xml

Purpose: XML testConf input for HDFS extended attribute CLI behavior. It drives shell-command style tests for `-setfattr` and `-getfattr` against `NAMENODE`, covering namespace validation, value encodings, removal, recursion, raw namespace access through `/.reserved/raw`, and the special `security.hdfs.unreadable.by.superuser` attribute.

Important structure and APIs: the file contains `<configuration><mode>test</mode><tests>...` with repeated `<test>` entries. Each entry has a description, ordered `<test-commands>`, cleanup commands, and comparators. Comparator types include `SubstringComparator` for diagnostic fragments and `ExactComparator` for fully normalized output strings using `#LF#`.

Control flow: the test harness executes commands in declaration order, then cleanup commands, then compares command output with expected comparator output. Tests create `/file1` or `/dir1`, mutate xattrs, invoke read/list commands, and validate positive and negative behavior. Error-path tests intentionally verify permission failures, invalid namespace prefixes, invalid encoding names, missing attributes, undeletable security xattrs, and access denial when a protected file is fetched.

State and persistence behavior: state is entirely HDFS namespace metadata created during each test. Cleanup removes created files or directories and one local `/tmp/file1` artifact. The raw namespace tests depend on the same underlying `/file1` object while addressing it through `/.reserved/raw/file1`.

Dependencies and integration points: consumed by Hadoop's `testConf.xml` XML-driven CLI test framework and HDFS command implementations for `setfattr`/`getfattr`. It relies on HDFS xattr namespace semantics: `user`, `trusted`, `security`, `system`, and `raw`; superuser/security restrictions; encoding handling for text, hex, and base64; recursive `getfattr -R`; and reserved raw-path behavior.

Risks: expectations are brittle around exact CLI error text, output ordering, and newline normalization. Tests touching `/tmp/file1` assume local cleanup is safe and that the process has local filesystem permissions. Namespace permissions can vary if the harness user or cluster security mode changes.

Test signals: successful execution demonstrates xattr round trips, prefix validation, permission rejection for protected namespaces, immutable unreadable-by-superuser behavior, raw namespace isolation, encoding conversion, xattr deletion, missing-attribute diagnostics, and recursive listing output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/testXAttrConf.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/test_ec_policies.xml -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/test_ec_policies.xml

Purpose: user-defined erasure coding policy fixture for HDFS tests. It models the expected XML policy format, including a layout version, schema definitions, and policies that combine schema IDs with cell sizes.

Important structure and APIs: top-level `<configuration>` contains `<layoutversion>1</layoutversion>`, `<schemas>`, and `<policies>`. Schemas define `codec`, data units `k`, parity units `m`, and options. Policies reference schemas by ID and set `cellsize` values in bytes.

Control flow: there is no executable flow; parser tests load this file, validate the layout version, build schema objects, then bind policies to schemas. The included schemas cover `xor`, `rs`, `rs-legacy`, and an uppercase `RS` entry marked as intended for failed-test coverage.

State and persistence behavior: read-only fixture with no persistence. The policy parser materializes transient EC schema/policy instances for tests.

Dependencies and integration points: integrates with HDFS erasure coding policy XML parsing and validation. It depends on available codec names and cell-size validation rules, including positive multiples of 1024 and case-insensitive uniqueness comments.

Risks: comment and fixture intent indicate one schema is for negative testing; if codec normalization or accepted codec sets change, this fixture may change behavior. Cell sizes are literal values, so unit interpretation changes would break tests.

Test signals: parser tests can assert valid policy loading for XOR, RS, and RS-LEGACY schemas, while also exercising failure handling for a deliberately questionable uppercase schema entry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/test_ec_policies.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/topology-broken-script.sh -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/topology-broken-script.sh

Purpose: intentionally failing topology script fixture. It exists to verify that Hadoop topology resolution callers handle external scripts that fail.

Important APIs/functions: no functions are declared. The script exits with status `1` after comments explicitly warning not to fix it.

Control flow: execution immediately reaches `exit 1`, producing no topology output.

State and persistence behavior: no state, no output files, and no side effects.

Dependencies and integration points: used by HDFS/network topology tests that configure an external script-based rack resolver. It depends only on `/usr/bin/env bash`.

Risks: its failure is the contract. Any change that makes it succeed, print a rack, or depend on input would invalidate tests for broken topology handling.

Test signals: callers should observe non-zero exit status and exercise error/fallback paths without crashing or misclassifying nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/topology-broken-script.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/topology-script.sh -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/topology-script.sh

Purpose: simple rack topology script fixture. It maps an input hostname or node name containing hyphen-delimited fields into a rack path.

Important APIs/functions: single pipeline `echo $1 | awk -F'-' '{printf("/rackID-%s",$2)}'`. It reads only the first argument and uses the second hyphen-separated field as the rack suffix.

Control flow: shell expands `$1`, `awk` splits on `-`, and the script prints `/rackID-<field2>` without a trailing newline from `printf`.

State and persistence behavior: no persistent state and no side effects.

Dependencies and integration points: used by topology resolver tests. Depends on Bash and `awk`, and on test node names having a meaningful second hyphen-delimited field.

Risks: unquoted `$1` permits word splitting and glob expansion, which is acceptable for controlled fixtures but unsafe for general input. Inputs without a second field produce `/rackID-`, so tests must use well-formed node names.

Test signals: resolver tests can assert that script-based topology resolution converts node names into deterministic rack strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/topology-script.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/scripts/hdfs-functions_test_helper.bash -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/scripts/hdfs-functions_test_helper.bash

Purpose: shared BATS setup/teardown helper for HDFS shell-function tests. It creates an isolated temporary directory, prepares Hadoop shell environment variables, sources `hadoop-functions.sh`, and provides a string containment helper.

Important APIs/functions: `setup()` creates and exports `TMP`, resolves `TESTBINDIR` and `HADOOP_LIBEXEC_DIR`, enables `HADOOP_SHELL_SCRIPT_DEBUG`, unsets `HADOOP_CONF_DIR`, `HADOOP_HOME`, and `HADOOP_PREFIX`, sets `QATESTMODE=true`, sources the common Hadoop shell functions, and `pushd`s into `TMP`. `teardown()` pops the directory and removes `TMP`. `strstr()` prints `true` or `false` depending on substring presence.

Control flow: BATS invokes `setup` before each test and `teardown` after each test. The source path to `hadoop-functions.sh` is relative to the test directory, so the helper anchors tests in the source tree layout.

State and persistence behavior: creates per-process/random target directories under `../../../target/test-dir/bats.$$.$RANDOM`, exports environment variables, and deletes the temp directory after each test. No persistent test state should survive a successful teardown.

Dependencies and integration points: integrates with BATS, Hadoop shell scripts, and the `hadoop-common` script library. The helper controls compatibility behavior by unsetting legacy Hadoop home variables.

Risks: cleanup depends on `TMP` being set correctly; a failed `pushd`/`popd` or sourced-script failure could leave temporary data. Relative path assumptions are sensitive to test invocation location.

Test signals: tests using this helper should start from a clean temp directory, source Hadoop functions successfully, and be able to assert shell output with `strstr`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/scripts/hdfs-functions_test_helper.bash -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/scripts/run-bats.sh -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/scripts/run-bats.sh

Purpose: BATS test launcher for Hadoop HDFS shell tests. It runs all `*.bats` files in the current directory, captures TAP output, and returns failure if any test file fails.

Important APIs/functions: creates `../../../target/surefire-reports` and `../../../target/tap`; locates `bats` with `which`; emits a TAP skip/failure marker when BATS is missing; loops over `*.bats`; runs `bats -t`; captures output through `tee`; reads the command status from `PIPESTATUS[0]`; accumulates `exitcode`.

Control flow: if no BATS executable exists, the script writes `shelltest.tap`, logs skip guidance, and exits `0` so Maven does not fail purely because BATS is absent. Otherwise it runs each test and exits `1` when any result is non-zero.

State and persistence behavior: persists TAP files under `target/tap` and ensures Surefire report directories exist. It does not remove prior TAP files.

Dependencies and integration points: intended to be invoked from Maven or test scripts inside the HDFS test script directory. Depends on Bash, BATS, and standard shell utilities.

Risks: if no `*.bats` files match, Bash may pass the literal pattern unless shell options differ. Missing BATS is treated as a non-failing skip, which can hide unexecuted shell tests in environments expected to run them.

Test signals: non-zero exit reflects at least one failing BATS file; TAP artifacts provide per-file diagnostics for CI consumption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/scripts/run-bats.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/pom.xml -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/pom.xml

Purpose: Maven aggregator POM for the Hadoop HDFS project. It groups HDFS modules under the parent `hadoop-project` build.

Important structure: packaging is `pom`; artifact is `hadoop-hdfs-project` version `3.6.0-SNAPSHOT`; modules include `hadoop-hdfs`, `hadoop-hdfs-client`, `hadoop-hdfs-native-client`, `hadoop-hdfs-httpfs`, `hadoop-hdfs-nfs`, and `hadoop-hdfs-rbf`.

Control flow: Maven traverses declared modules during reactor builds. The build config skips deployment through `maven-deploy-plugin` and configures Apache RAT without additional local options.

State and persistence behavior: no runtime state. Build outputs are produced by child modules under their respective targets.

Dependencies and integration points: inherits dependency/plugin management from `../hadoop-project`. It is the integration root for HDFS server, client, native client, HTTPFS, NFS, and Router-Based Federation modules.

Risks: module ordering and parent-relative path are critical for reactor resolution. Skipping deploy at this aggregator prevents accidental deployment of the aggregate POM but child deploy behavior depends on child configuration.

Test signals: successful Maven reactor loading confirms all listed child module paths exist and the parent POM is resolvable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/dev-support/findbugs-exclude.xml -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/dev-support/findbugs-exclude.xml

Purpose: SpotBugs/FindBugs exclusion filter for `hadoop-aws`. It documents known static-analysis warnings that are accepted or false positives for S3A and related classes.

Important structure: `<FindBugsFilter>` contains `<Match>` blocks by class, optional method or field, and bug pattern. Suppressed patterns include string equality warnings, redundant null checks, ignored return values, inconsistent synchronization reports, switch fallthrough, volatile increment warnings, and overridable-method read-object warnings.

Control flow: no executable flow. The SpotBugs Maven plugin reads this file and suppresses matched findings during analysis.

State and persistence behavior: read-only build configuration. It affects generated static-analysis reports but does not alter compiled code.

Dependencies and integration points: referenced from `hadoop-tools/hadoop-aws/pom.xml` in the SpotBugs plugin configuration, alongside the global Hadoop exclusion filter.

Risks: overly broad class-level suppressions, especially `IS2_INCONSISTENT_SYNC` on `S3AInputStream`, can mask real concurrency regressions. Exclusions may become stale when classes or methods are renamed.

Test signals: a clean SpotBugs run for `hadoop-aws` depends on these suppressions matching known warnings while allowing new unsuppressed issues to surface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/dev-support/findbugs-exclude.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/pom.xml -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/pom.xml

Purpose: Maven module POM for Hadoop's AWS integration jar. It builds S3A and AWS support code, wires AWS SDK dependencies, and configures unit, integration, scale, and parallel test behavior.

Important structure and APIs: artifact `hadoop-aws`, packaging `jar`, parent `hadoop-project`. Properties define S3A scale-test toggles, huge-file sizes, integration timeout, stream type (`classic`, `prefetch`, `analytics`), job ID, and root-test toggle. Profiles enable/disable integration tests based on `auth-keys.xml`, split parallel and sequential integration tests, and switch scale/prefetch/analytics modes.

Control flow: Maven profiles select surefire/failsafe execution. `parallel-tests` creates per-fork directories and excludes root, encryption, huge, terasort, marker, aggregate statistics, and cache-sensitive tests from the parallel phase, then runs those sequentially. `sequential-tests` is active when `parallel-tests` is absent. The build config also runs SpotBugs with local/global filters, copies dependencies for optional/builtin tool lists and native libs, and enforces banned imports outside allowed committer/encryption classes.

State and persistence behavior: produces target dependency lists under `target/hadoop-tools-deps`, native test libraries under `target/native-libs`, packaged libs under `target/lib`, and test directories parameterized by fork number/job ID. Integration tests may touch real S3 buckets when credentials are present.

Dependencies and integration points: depends on Hadoop common, AWS SDK v2 bundle, AWS SDK v1 core for adapter classes, S3 encryption client, analytics accelerator, WildFly OpenSSL, Hadoop MR/YARN/HDFS/DistCp test artifacts, Bouncy Castle, JUnit 5, AssertJ, and Mockito. It integrates with AWS credentials in `src/test/resources/auth-keys.xml`.

Risks: real-cloud integration tests are costly and stateful; root tests must be isolated. The property name `fs.s3a.scale.test.huge.huge.partitionsize` appears intentionally propagated but is easy to confuse with `huge.partitionsize`. Enforcer import restrictions can break new code unless exclusions are maintained.

Test signals: profile activation without auth keys should skip ITs; with auth keys, failsafe runs S3A integration tests. Parallel profile success demonstrates fork isolation, bucket-path uniqueness, and correct sequencing of unsafe tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/AWSApiCallTimeoutException.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/AWSApiCallTimeoutException.java

Purpose: IOException mapping for AWS SDK API call timeout failures. It subclasses Hadoop `ConnectTimeoutException` so existing timeout handlers can catch it.

Important APIs/types: constructor `AWSApiCallTimeoutException(String operation, Exception cause)` stores the operation as the exception message and initializes the cause.

Control flow: no retry logic here; construction occurs during exception translation elsewhere, then callers handle it as an `IOException`/connect timeout.

State and persistence behavior: immutable exception state after construction, except standard Throwable cause initialization.

Dependencies and integration points: depends on `org.apache.hadoop.net.ConnectTimeoutException` and integrates with S3A exception translation and retry policy code.

Risks: only the operation string is used as the top-level message, so detailed cause text is available through the cause rather than the message.

Test signals: translation tests should assert timeout exceptions retain the SDK cause and are catchable as `ConnectTimeoutException`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/AWSApiCallTimeoutException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/AWSBadRequestException.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/AWSBadRequestException.java

Purpose: typed S3A IOException for HTTP 400 Bad Request service responses.

Important APIs/types: extends `AWSServiceIOException`; exposes `STATUS_CODE` equal to `SC_400_BAD_REQUEST`; constructor accepts operation and `AwsServiceException`.

Control flow: no custom behavior beyond superclass wrapping. Retryability is inherited from the underlying SDK exception unless policy code treats the type specially.

State and persistence behavior: stores operation and AWS service exception through the superclass.

Dependencies and integration points: used by S3A exception translation for malformed requests, bad headers, and incompatible parameters.

Risks: third-party object stores may use 400 for multiple misconfiguration classes; callers should not assume all 400s have identical remedies.

Test signals: exception translation should map 400 responses to this type and preserve request IDs, status code, and AWS error details through `AWSServiceIOException`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/AWSBadRequestException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/AWSClientIOException.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/AWSClientIOException.java

Purpose: base IOException wrapper for AWS SDK `SdkException` instances.

Important APIs/types: constructor validates non-null operation and cause; `getCause()` narrows the type to `SdkException`; `getMessage()` returns `<operation>: <cause message>`; `retryable()` delegates to the SDK exception; `getOperation()` exposes the operation.

Control flow: constructed by S3A exception translation, then inspected by retry policy and callers. It does not retry by itself.

State and persistence behavior: immutable operation string and Throwable cause.

Dependencies and integration points: depends on AWS SDK v2 `SdkException`, Hadoop `Preconditions`, and Java `IOException`. It is the superclass for service-specific wrappers.

Risks: message formatting depends on non-null cause message; retry decisions reflect SDK metadata unless subclasses override.

Test signals: unit tests should verify null argument rejection, message formatting, cause narrowing, and retryable delegation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/AWSClientIOException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/AWSCredentialProviderList.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/AWSCredentialProviderList.java

Purpose: S3A credential-provider chain with Hadoop-specific diagnostics, dynamic provider composition, anonymous-provider handling, and reference-counted close behavior.

Important APIs/types: implements `AwsCredentialsProvider` and `AutoCloseable`. Constructors accept empty, collection, or named varargs provider sets. Public methods include `setName`, `add`, `addAll`, deprecated no-op `refresh`, `resolveCredentials`, `getProviders`, `checkNotEmpty`, `listProviderNames`, `share`, `getRefCount`, `isClosed`, `close`, `size`, and static `maybeTranslateCredentialException`.

Control flow: `resolveCredentials()` rejects closed or empty lists, optionally reuses `lastProvider`, then iterates providers. It accepts credentials with access and secret keys, or credentials from anonymous providers. `NoAwsCredentialsException` is logged without stack and only captured as last exception when no stronger exception exists; other `SdkException` instances replace the last exception; non-SDK exceptions are wrapped as `SdkException` when they have messages. If no provider succeeds, `CredentialInitializationException` is rethrown, otherwise a `NoAuthWithAWSException` is raised with provider diagnostics.

State and persistence behavior: mutable in-memory provider list, optional cached `lastProvider`, `reuseLastProvider`, `name`, atomic `refCount`, and atomic `closed`. `share()` increments references; `close()` decrements and only closes nested `Closeable`/`AutoCloseable` providers when the count reaches zero. No persistent storage is written, but nested providers may manage background refresh threads.

Dependencies and integration points: integrates with S3A credential provider configuration, Hadoop auth exceptions, AWS SDK v2 providers, anonymous credentials, `S3AUtils.closeAutocloseables`, and exception translation to `AccessDeniedException`.

Risks: provider list mutation is not generally synchronized except around share/close; concurrent add/resolve patterns would be unsafe. Reusing `lastProvider` can keep using a provider whose credentials later fail until that provider itself throws. Closing while shared incorrectly can leak background resources or close providers still in use.

Test signals: tests should cover empty-list failure, anonymous credentials acceptance, exception prioritization, cached-provider reuse, reference-counted close, closed-list failure, and translation of credential initialization errors to access denied.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/AWSCredentialProviderList.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/AWSNoResponseException.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/AWSNoResponseException.java

Purpose: service IOException wrapper for no-response failures, treated as retryable.

Important APIs/types: extends `AWSServiceIOException`; constructor accepts operation and `AwsServiceException`; overrides `retryable()` to return `true`.

Control flow: generated by exception translation for a no-response service condition and then consumed by retry policy as idempotent/retryable.

State and persistence behavior: stores superclass operation and AWS cause only.

Dependencies and integration points: part of S3A retry and exception translation around HTTP/service failures.

Risks: unconditional retryability must still be combined with operation idempotency; retrying non-idempotent operations can be unsafe if the service actually processed the request.

Test signals: retry-policy tests should confirm this wrapper reports retryable and preserves service metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/AWSNoResponseException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/AWSRedirectException.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/AWSRedirectException.java

Purpose: typed service IOException for redirect responses that reach S3A callers.

Important APIs/types: extends `AWSServiceIOException` and only defines an operation/cause constructor.

Control flow: exception translation constructs this when redirect handling was not resolved by the SDK/client configuration. No local recovery logic exists.

State and persistence behavior: standard wrapped exception state only.

Dependencies and integration points: connects endpoint/region misconfiguration handling with callers that need a Hadoop `IOException`.

Risks: redirects surfacing to users are generally configuration problems; retrying without endpoint/region changes may loop or fail repeatedly.

Test signals: endpoint-region tests should assert redirect responses translate to this type with AWS request details preserved.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/AWSRedirectException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/AWSS3IOException.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/AWSS3IOException.java

Purpose: public evolving wrapper for S3-specific `S3Exception` instances as Hadoop IOExceptions.

Important APIs/types: extends `AWSServiceIOException`; `getCause()` narrows to `S3Exception`; annotated public/evolving.

Control flow: created during S3A exception translation for S3 service failures not mapped to a more specific subclass.

State and persistence behavior: retains operation and original S3 exception.

Dependencies and integration points: exposes AWS SDK v2 S3 exception details while fitting Hadoop `IOException` contracts.

Risks: public API stability is evolving; callers should avoid depending on implementation-specific message text.

Test signals: translation tests should verify cause narrowing and inherited access to request ID, status code, extended request ID, and error details.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/AWSS3IOException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/AWSServiceIOException.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/AWSServiceIOException.java

Purpose: base IOException wrapper for AWS `AwsServiceException` with direct accessors for service metadata.

Important APIs/types: extends `AWSClientIOException`; narrows `getCause()` to `AwsServiceException`; exposes `requestId()`, `awsErrorDetails()`, `statusCode()`, and `extendedRequestId()`.

Control flow: constructed by S3A translation for service-side responses; subclasses specialize status classes such as throttling, bad request, redirects, and unsupported features.

State and persistence behavior: immutable operation and wrapped service exception.

Dependencies and integration points: bridges AWS SDK v2 service exceptions to Hadoop public IO exception behavior. Consumers can log or branch on HTTP status and AWS request IDs without unpacking the cause.

Risks: methods delegate directly to the cause; malformed or third-party SDK exceptions with missing details can return null details.

Test signals: wrapper tests should verify metadata delegation and compatibility with the `AWSClientIOException` message and retryable behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/AWSServiceIOException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/AWSServiceThrottledException.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/AWSServiceThrottledException.java

Purpose: typed IOException for AWS service throttling.

Important APIs/types: extends `AWSServiceIOException`; declares `STATUS_CODE = 503`; overrides `retryable()` to `true`.

Control flow: exception translation maps throttle responses to this class. Retry policy and metrics can distinguish throttling from generic service failures.

State and persistence behavior: no mutable state beyond wrapped AWS cause.

Dependencies and integration points: used by S3A retry policy, statistics, and throttling diagnostics.

Risks: not every 503 is semantically throttling on third-party stores; treating all mapped instances as retryable may hide persistent misconfiguration.

Test signals: retry tests should assert retryable behavior and metrics tests should count translated throttle failures accurately.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/AWSServiceThrottledException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/AWSStatus500Exception.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/AWSStatus500Exception.java

Purpose: typed service IOException for HTTP 5xx server-side failures.

Important APIs/types: extends `AWSServiceIOException` with only an operation/cause constructor. Class comments document that 500s are considered retryable by the AWS SDK and conditionally retried in S3A based on `fs.s3a.retry.http.5xx.errors`.

Control flow: created during exception translation after SDK retries are exhausted. Actual retry decisions are external in S3A retry policy.

State and persistence behavior: standard wrapped exception state only.

Dependencies and integration points: integrates with S3A retry configuration and server-error handling for AWS and third-party object stores.

Risks: third-party stores may use 5xx for permanent configuration failures; repeated retries can increase load and latency.

Test signals: retry-policy tests should cover behavior with HTTP 5xx retry enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/AWSStatus500Exception.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/AWSUnsupportedFeatureException.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/AWSUnsupportedFeatureException.java

Purpose: typed service IOException for object stores that reject a requested S3 feature.

Important APIs/types: extends `AWSServiceIOException`; overrides `retryable()` to `false`.

Control flow: exception translation creates this when a feature such as change detection or another S3 capability is unsupported. Callers should disable the feature rather than retry.

State and persistence behavior: wraps original service exception only.

Dependencies and integration points: integrates with S3A feature negotiation and compatibility paths for third-party S3-compatible stores.

Risks: accurate mapping matters; misclassifying a transient service problem as unsupported prevents useful retries.

Test signals: compatibility tests should verify unsupported-feature responses fail fast and surface actionable diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/AWSUnsupportedFeatureException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/AnonymousAWSCredentialsProvider.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/AnonymousAWSCredentialsProvider.java

Purpose: Hadoop-configurable AWS SDK v2 credentials provider for unsigned anonymous S3 access.

Important APIs/types: implements `AwsCredentialsProvider`; public `NAME` constant preserves the configuration class name; `resolveCredentials()` delegates to `AnonymousCredentialsProvider.create().resolveCredentials()`; `toString()` returns the simple class name.

Control flow: S3A instantiates this provider from `fs.s3a.aws.credentials.provider`; when selected, AWS requests are unsigned.

State and persistence behavior: stateless; creates/delegates to an SDK anonymous provider on each resolution.

Dependencies and integration points: used by `AWSCredentialProviderList`, which explicitly treats this class as valid even without access/secret keys. Intended for public datasets.

Risks: unsafe for private buckets; accidental configuration can silently remove request signing and produce access-denied behavior or expose reliance on public access.

Test signals: credential-chain tests should verify anonymous credentials are accepted and class-name based configuration remains compatible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/AnonymousAWSCredentialsProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/ArnResource.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/ArnResource.java

Purpose: immutable representation of an S3 ARN-backed resource, currently access points and outposts access points, with endpoint derivation.

Important APIs/types: private fields hold name, owner account ID, region, full ARN, partition, and `accessPointRegionKey`. Getters expose name, account, region, full ARN, and endpoint. Static `accessPointFromArn(String)` parses via AWS SDK `Arn.fromString` and validates region, account ID, and resource string. `getEndpoint()` chooses `s3-accesspoint.%s.amazonaws.com` or `s3-outposts.%s.amazonaws.com` based on `fullArn.contains("s3-outposts")`.

Control flow: parse ARN, validate required fields, extract resource name from `parsed.resource().resource()`, and construct `ArnResource`. Endpoint generation is lazy through getter.

State and persistence behavior: immutable in-memory value object; no persistence.

Dependencies and integration points: depends on AWS SDK ARN parser and S3A access point configuration. It helps S3A convert access point ARN inputs into resource metadata and endpoints.

Risks: endpoint formats ignore partition-specific DNS suffixes even though partition is stored; comments imply AWS SDK endpoint handling elsewhere may use `accessPointRegionKey`, but that field has no getter in this file. `contains("s3-outposts")` is a coarse classifier.

Test signals: tests should cover malformed ARNs, missing region/account/resource, normal access point endpoints, outposts endpoints, and partition variants such as `aws-cn`/`aws-us-gov`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/ArnResource.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/Constants.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/Constants.java

Purpose: public/evolving constant catalog for S3A configuration keys, defaults, capability names, storage classes, retry knobs, encryption options, input stream modes, and compatibility settings. It is the main source-level contract between user configuration, `core-default.xml`, S3A implementation code, and downstream applications.

Important APIs/types: final class with a private constructor and many `public static final` fields. Major groups include credentials (`ACCESS_KEY`, `SECRET_KEY`, provider keys, assumed-role settings), connection and HTTP tuning (`MAXIMUM_CONNECTIONS`, timeouts, proxy keys, SSL channel mode, requester pays), endpoints and regions (`ENDPOINT`, `CENTRAL_ENDPOINT`, `AWS_REGION`, cross-region access, FIPS), upload/delete/listing settings (`MULTIPART_SIZE`, thresholds, paging, bulk delete, fast upload buffers), encryption (`S3_ENCRYPTION_*` plus deprecated legacy SSE keys), custom signers and headers, S3A filesystem identity/prefixes, S3Guard deprecated keys, retry and throttle settings, change detection, directory marker capabilities, create performance/conditional create, vectored reads, input stream selection, prefetch controls, S3 Express, HTTP signer, checksum controls, classloader isolation, S3 Access Grants, IO rate limiting, analytics accelerator prefix, and `IF_NONE_MATCH_STAR`.

Control flow: no executable control flow beyond class loading. Values are consumed throughout S3A to read Hadoop `Configuration`, set defaults, advertise path capabilities, construct clients, and maintain backward compatibility.

State and persistence behavior: immutable constants only. The values influence persisted configuration files and user jobs, but this class itself stores no runtime state.

Dependencies and integration points: imports Hadoop classification annotations, `Options`, checksum and stream integration helpers, SSL socket factory modes, `Duration`, `Locale`, `TimeUnit`, and size constants. It is referenced by S3A client construction, retry policy, filesystem operations, credential initialization, input stream factories, committers, tests, and documentation.

Risks: this is a high-blast-radius compatibility surface. Renaming or changing default values can break deployed configurations. Deprecated S3Guard and legacy encryption constants must often remain even when ignored or rejected. Timeout defaults exist in both `Duration` and legacy numeric forms, so keeping them synchronized matters. Some defaults intentionally balance compatibility over ideal behavior, such as empty default endpoint, cross-region access enabled, and checksum validation disabled.

Test signals: configuration tests should assert default values match `core-default.xml`, deprecated names still parse as intended, capability probes use the documented strings, endpoint/region and FIPS settings align with `DefaultS3ClientFactory`, retry constants align with `S3ARetryPolicy`, and stream/checksum/encryption settings are honored by their respective subsystems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/Constants.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/CredentialInitializationException.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/CredentialInitializationException.java

Purpose: non-retryable AWS SDK client exception for credential setup failures.

Important APIs/types: extends `SdkClientException`; constructors accept message with optional cause using SDK builders; overrides `retryable()` to `false`.

Control flow: credential providers throw this when configuration is invalid or initialization cannot succeed. `AWSCredentialProviderList` and S3A exception translation treat it specially and map it to access denied.

State and persistence behavior: standard exception message/cause only.

Dependencies and integration points: public/stable Hadoop API for S3A credential providers. Integrates with AWS SDK retry metadata and Hadoop `AccessDeniedException` translation.

Risks: using this for transient credential-service outages would suppress retries. It should be reserved for deterministic setup failures.

Test signals: credential-provider tests should verify fail-fast retryability and translation to access denied.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/CredentialInitializationException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/DefaultS3ClientFactory.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/DefaultS3ClientFactory.java

Purpose: default S3A factory for AWS SDK v2 synchronous clients, asynchronous clients, and transfer managers. It centralizes HTTP client setup, endpoint/region configuration, request checksum policy, credentials, S3 Express session behavior, plugins, metrics, retry policy, custom headers, requester-pays, user agent suffix, access grants, and optional HTTP signer configuration.

Important APIs/types: extends `Configured` and implements `S3ClientFactory`. Public methods are `createS3Client(URI, S3ClientCreationParameters)`, `createS3AsyncClient(URI, S3ClientCreationParameters)`, and `createS3TransferManager(S3AsyncClient)`. Internal helpers include generic `configureClientBuilder`, protected `createClientOverrideConfiguration`, `configureEndpointAndRegion`, static `getS3Endpoint`, static `getS3RegionFromEndpoint`, and `maybeApplyS3AccessGrantsConfigurations`.

Control flow: sync client creation builds an Apache HTTP client with proxy config, then applies shared builder settings. Async client creation builds a Netty client, configures multipart thresholds, and enables multipart only when client-side encryption and analytics accelerator are disabled. Shared configuration sets endpoint/region, optional MD5 plugin, checksum calculation/validation modes, S3 Access Grants, path-style access, override config, credential provider, S3 Express session auth, metrics, and optional custom HTTP signer.

State and persistence behavior: factory is mostly stateless beyond inherited Hadoop `Configuration` and exactly-once loggers. Created clients hold configured connection pools, credentials, metrics publishers, plugins, and region/endpoint state.

Dependencies and integration points: depends heavily on AWS SDK v2 S3, HTTP, retry, metrics, and plugin APIs; Hadoop `AWSClientConfig`; S3A constants; signer factory; request factory parameters; and S3A instrumentation. It is the integration point where user config becomes actual AWS SDK client behavior.

Risks: endpoint/region decisions are subtle. FIPS mode rejects non-central endpoints; central endpoint avoids explicit override to prevent AWS SDK issue behavior; empty configured region intentionally falls back to SDK region chain; absent region uses `us-east-2` for cross-region access. Multipart async behavior is disabled with CSE or analytics accelerator. Checksum and MD5 defaults can affect third-party S3 stores.

Test signals: tests should cover endpoint URI normalization, secure vs insecure protocol, VPC endpoint region parsing, central endpoint fallback, FIPS rejection, cross-region flag, requester-pays header, custom headers, user-agent suffix, metrics publisher, access grants plugin and fallback, HTTP signer activation, async multipart gating, and checksum/MD5 policies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/DefaultS3ClientFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/FailureInjectionPolicy.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/FailureInjectionPolicy.java

Purpose: compact holder for S3A test failure-injection settings.

Important APIs/types: `DEFAULT_DELAY_KEY_SUBSTRING`, `throttleProbability`, `failureLimit`, constructor reading `FAIL_INJECT_THROTTLE_PROBABILITY`, getters/setters, `trueWithProbability(float)`, `toString()`, and private probability validation.

Control flow: construction reads config and validates probability in range `[0.0, 1.0]`. Callers can mutate failure limit and throttle probability. `trueWithProbability` uses `Math.random()` to decide whether to inject a failure.

State and persistence behavior: in-memory mutable policy values only; no persistence.

Dependencies and integration points: consumes S3A constants and Hadoop `Configuration`; intended for tests and failure-injecting client factories.

Risks: `Math.random()` makes behavior nondeterministic unless probability is 0 or 1. Validation throws on out-of-range config, which is useful for tests but can fail client setup.

Test signals: tests should assert probability bounds, configured throttle probability, failure limit mutation, and deterministic behavior at probabilities 0 and 1.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/FailureInjectionPolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/HttpChannelEOFException.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/HttpChannelEOFException.java

Purpose: normalized EOFException for HTTP channel termination conditions such as no response and OpenSSL errors.

Important APIs/types: extends `EOFException`; constructor accepts path, error, and cause, uses `error` as message, and initializes cause.

Control flow: exception translation or HTTP error handling wraps low-level channel failures into this type so retry policies can match EOF semantics.

State and persistence behavior: standard exception message/cause only. The `path` parameter is not stored in this class.

Dependencies and integration points: used by S3A retry policies and HTTP client exception translation across shaded/unshaded client libraries.

Risks: dropping the path from the message can reduce diagnostics unless callers include path in the error string.

Test signals: retry tests should verify low-level no-response/channel EOF failures are represented as `EOFException` subclasses with original causes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/HttpChannelEOFException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/Invoker.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/Invoker.java

Purpose: central lambda-based invocation wrapper for S3A operations, providing one-shot exception translation, retry loops, future awaiting, quiet/ignored execution, duration tracking, and retry callbacks.

Important APIs/types: constructor takes Hadoop `RetryPolicy` and default `Retried` callback. Static methods include `once`, `onceTrackingDuration`, `onceInTheFuture`, `ignoreIOExceptions`, `quietly`, and `quietlyEval`. Instance methods include `retry`, `maybeRetry`, and `retryUntranslated` variants. Nested `Retried` functional interface reports retry events; `NO_OP` and `LOG_EVENT` are default callbacks. Methods are annotated with source-retained `Retries` annotations documenting translation/retry contracts.

Control flow: one-shot methods execute operations and translate `SdkException` through `S3AUtils.translateException`. Retry methods wrap one-shot execution or raw operations, then call `retryPolicy.shouldRetry` with translated IOExceptions, idempotency, and retry count. On retry, callback is invoked before sleeping. Interrupted sleeps become `InterruptedIOException` and re-interrupt the thread. If the retry policy itself fails, the original caught exception is rethrown.

State and persistence behavior: immutable retry policy and callback references. No persistent state. Per-call retry count and caught exception are local.

Dependencies and integration points: integrates S3A operations with Hadoop retry policy, AWS SDK exceptions, S3A exception translation, IO statistics duration tracking, `FutureIO`, and logging. It is used broadly around object-store calls.

Risks: idempotency flag correctness is critical; marking a non-idempotent operation idempotent can duplicate side effects. `retryUntranslated` translates SDK exceptions only for policy decisions and may rethrow the raw SDK exception after retries. Sleep delays block the invoking thread.

Test signals: tests should cover one-shot translation, future exception translation, retry count/delay/callback behavior, idempotent vs non-idempotent policy decisions, interrupt handling, quiet optional behavior, and no nested retry misuse for methods already annotated as retried.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/Invoker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/Listing.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/Listing.java

Purpose: S3A listing helper that turns S3 object-list responses into Hadoop `RemoteIterator` streams of `S3AFileStatus` and `S3ALocatedFileStatus`, with filtering, pagination, asynchronous prefetch of next list batches, audit-span retention, and IO statistics aggregation.

Important APIs/types: class extends `AbstractStoreOperation`. Public/package methods create provided status iterators, file-status listing iterators, located-status iterators, single-status iterators, recursive/non-recursive directory listings, non-empty-directory listings, and list-object requests. Nested types include `FileStatusAcceptor`, `FileStatusListingIterator`, `ObjectListingIterator`, `AcceptFilesOnly`, `AcceptAllButS3nDirs`, `AcceptAllObjects`, `AcceptAllButSelfAndS3nDirs`, and `AcceptAllButSelf`.

Control flow: high-level listing methods build an S3 request using key prefixes and delimiters, then construct `ObjectListingIterator`. That iterator launches the initial async list call at construction. Its first `next()` awaits the initial future and, if truncated, schedules the next async batch. Later `next()` calls await the previously scheduled continuation and schedule another when needed. `FileStatusListingIterator` consumes each `S3ListResult`, filters S3 objects and common prefixes through a path filter and acceptor, converts objects to `S3AFileStatus`, and loops through empty filtered batches until data or remote exhaustion.

State and persistence behavior: iterators keep transient pagination state: current request, latest and previous results, future for the in-flight batch, first-listing flag, listing count, batch iterators, IO statistics, and retained audit span. `close()` aggregates iterator IO statistics into the current IO statistics context. No filesystem state is mutated by listing.

Dependencies and integration points: depends on AWS SDK S3 object/prefix models, S3A request/list result wrappers, `ListingOperationCallbacks`, `StoreContext`, audit spans, `S3AUtils` conversion helpers, role-model key conversion, Hadoop `RemoteIterator`, path filters, located statuses, and IO statistics.

Risks: `hasNext()` can trigger remote work indirectly through `FileStatusListingIterator` because filtering may need more batches before it can answer. Iterators are explicitly not thread-safe. Correct acceptor selection is important to suppress self entries, old S3N `_$folder$` markers, and directory marker objects. The async prefetch path must preserve audit context and handle future failures through `onceInTheFuture`.

Test signals: tests should cover provided-status filtering, recursive delimiter behavior, self and S3N marker suppression, file-only acceptor behavior, common-prefix directory status creation, pagination continuation, empty filtered pages, IO statistics aggregation on close, and async future exception translation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/Listing.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/MultipartUtils.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/MultipartUtils.java

Purpose: utility for listing outstanding S3 multipart uploads as Hadoop `RemoteIterator<MultipartUpload>` instances.

Important APIs/types: final utility class with package-private `listMultipartUploads(StoreContext, S3Client, String, int)`. Nested `ListingIterator` pages `ListMultipartUploadsResponse`; nested public `UploadIterator` flattens each response into individual `MultipartUpload` values.

Control flow: `ListingIterator` captures request factory, invoker, audit span, prefix, max keys, and immediately requests the first batch. `hasNext()` is true for the first listing or while the last response is truncated. `next()` returns the first batch or sends continuation markers for later batches. `UploadIterator` initializes a lister and current batch, then `hasNext()` returns local batch items or requests more batches until exhausted.

State and persistence behavior: transient pagination state includes current listing response, first-listing flag, list count, key/upload ID markers, and batch iterator. No uploads are modified; this only lists state stored in S3.

Dependencies and integration points: depends on AWS SDK `S3Client` multipart upload models, S3A `StoreContext`, `RequestFactory`, `Invoker`, audit spans, operation-duration statistics, and `OBJECT_MULTIPART_UPLOAD_LIST` metric.

Risks: constructor performs remote I/O, so creating the iterator can fail. Listing uses the audit span active at iterator construction for all later calls. Max-key selection affects API load and latency.

Test signals: tests should cover empty listings, truncated listings with key/upload continuation markers, prefix filtering, audit span activation, retry translation, and flattening from responses to individual upload entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/MultipartUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/NoVersionAttributeException.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/NoVersionAttributeException.java

Purpose: public unstable path exception indicating that an S3 object lacks the version attribute required by the configured change-detection policy.

Important APIs/types: extends `PathIOException`; constructor accepts path and detail message.

Control flow: thrown by change-detection logic when version IDs are required but absent.

State and persistence behavior: stores path, operation/message fields through `PathIOException`; no persistence.

Dependencies and integration points: integrates S3A change detection with Hadoop path-based IO exception reporting.

Risks: only applies when version-based detection is required; using it when versioning is optional would over-fail reads.

Test signals: change-detection tests should assert this exception when version ID is missing under require-version mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/NoVersionAttributeException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/ProgressableProgressListener.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/ProgressableProgressListener.java

Purpose: AWS SDK transfer listener that bridges S3 transfer progress into Hadoop `Progressable` callbacks and S3A write statistics.

Important APIs/types: implements `TransferListener`. Constructor captures `S3AStore`, object key, optional `Progressable`, and initializes `lastBytesTransferred`. Overrides `transferInitiated`, `transferComplete`, and `bytesTransferred`; adds `uploadCompleted(ObjectTransfer)` for final delta reconciliation.

Control flow: transfer initiation and completion each increment write operations. Every bytes-transferred event invokes optional progress callback, computes delta from cumulative transferred bytes, updates put-progress statistics, and stores the new cumulative value. `uploadCompleted` checks final transfer snapshot for bytes not reported through listener events and records a positive delta.

State and persistence behavior: mutable in-memory `lastBytesTransferred`; persistent effects are metrics/statistics updates in `S3AStore`, not file data changes.

Dependencies and integration points: integrates AWS SDK v2 transfer manager progress events with Hadoop MapReduce progress reporting and S3A instrumentation.

Risks: assumes progress snapshots are monotonically increasing; negative deltas would decrement statistics if callbacks arrive out of order. Race handling is explicitly delegated to `uploadCompleted`.

Test signals: tests should cover progress callback invocation, delta calculation across multiple events, operation counters, final positive delta handling, and no failure when progress callback is null.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/ProgressableProgressListener.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/RangeNotSatisfiableEOFException.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/RangeNotSatisfiableEOFException.java

Purpose: EOFException subclass representing HTTP 416 Range Not Satisfiable.

Important APIs/types: constructor accepts operation and cause, uses operation as message, and initializes cause.

Control flow: exception translation maps range failures to this type so readers expecting EOF semantics continue to work.

State and persistence behavior: standard exception message/cause only.

Dependencies and integration points: used by S3A input stream/range read logic and retry/error handling.

Risks: callers must distinguish legitimate EOF from stale metadata or file-change cases where remote object length changed.

Test signals: range-read tests should assert 416 responses are catchable as `EOFException` and preserve the underlying cause.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/RangeNotSatisfiableEOFException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/RemoteFileChangedException.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/RemoteFileChangedException.java

Purpose: path exception for detecting that an S3 object changed or disappeared relative to an expected version during operations such as reads or rename.

Important APIs/types: extends `PathIOException`; constants `PRECONDITIONS_FAILED` and `FILE_NOT_FOUND_SINGLE_ATTEMPT`; constructors accept path, operation, message, and optional cause, then call `setOperation(operation)`.

Control flow: thrown by change-detection or rename code when object metadata no longer matches expectations, such as open stream revalidation failure or file disappearance between list and copy.

State and persistence behavior: exception holds path, operation, message, and optional cause only.

Dependencies and integration points: integrates S3A change detection, conditional requests, input streams, and rename operations with Hadoop path-aware errors.

Risks: object stores are eventually/concurrently mutable; this exception marks consistency or race failures that callers may or may not retry safely depending on operation semantics.

Test signals: tests should cover version/ETag mismatch, precondition failure mapping, disappeared rename source, operation field preservation, and cause preservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/RemoteFileChangedException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/RenameFailedException.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/RenameFailedException.java

Purpose: path exception representing a failed S3A rename with a boolean result compatible with `FileSystem.rename()`.

Important APIs/types: extends `PathIOException`; constructors accept string source/destination with cause or error, or `Path` source and optional destination. `getExitCode()` returns the boolean rename result; `withExitCode(boolean)` mutates and returns the exception.

Control flow: constructors set operation to `rename` and target path to destination when available. Callers can throw the exception or inspect/propagate its exit code.

State and persistence behavior: mutable `exitCode` defaults false; path/target/operation stored through `PathIOException`.

Dependencies and integration points: used by S3A rename implementation, which must bridge exception-rich failures and Hadoop's boolean rename contract.

Risks: mutable exit code can be overlooked; default false is conservative. Destination may be null in one constructor.

Test signals: rename tests should assert source, target path, operation, cause/message, default false, and `withExitCode(true)` chaining behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/RenameFailedException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/Retries.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/Retries.java

Purpose: package-private documentation annotations describing whether S3A methods perform retrying and/or exception translation internally.

Important APIs/types: final-ish utility class with nested source-retention annotations: `OnceTranslated`, `OnceRaw`, `OnceMixed`, `RetryTranslated`, `RetryRaw`, `RetryMixed`, `RetryExceptionsSwallowed`, and `OnceExceptionsSwallowed`.

Control flow: no runtime behavior. Annotations are retained only in source and used to guide maintainers/callers.

State and persistence behavior: none.

Dependencies and integration points: complements Hadoop retry annotations like `Idempotent` but is not an RPC marker. Used throughout S3A methods such as `Invoker` and listing utilities to avoid nested retries or double translation.

Risks: because retention is source-only, tooling and runtime checks cannot enforce the contract. Documentation can drift from implementation.

Test signals: no direct runtime tests; code review and static source checks can verify retry-sensitive APIs are annotated consistently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/Retries.java -->
