# Research: subset-b-009800

Grouped research for the s3fs-fuse credential, logging, request, XML, object-list, signal, help, global, and utility files. Each section preserves the source path for reconciliation.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/s3fs_cred.cpp -->
# sources/user-network-fs/s3fs-fuse/src/s3fs_cred.cpp

Purpose: implements `S3fsCred`, the singleton credential manager used by s3fs-fuse to load, validate, refresh, and expose credentials for S3 requests. It supports command-line credentials, passwd files, AWS environment variables, AWS profile files, IAM role metadata, ECS metadata, IBM IAM, and external credential plugins.

Important APIs and functions: the built-in weak-compatible credential functions (`VersionS3fsCredential`, `InitS3fsCredential`, `FreeS3fsCredential`, `UpdateS3fsCredential`) act as defaults and plugin fallbacks. `SetBucket`/`GetBucket` store the static bucket name. `DetectParam` consumes credential-related mount options. `CheckAllParams` validates bucket/auth option combinations and initializes credentials. `CheckIAMCredentialUpdate` refreshes tokens and returns the current access key, secret, and token. `LoadIAMCredentials`, `LoadIAMRoleFromMetaData`, `SetIAMCredentials`, and `ParseIAMCredentialResponse` implement metadata/IAM flows. `ReadS3fsPasswdFile`, `ParseS3fsPasswdFile`, `ReadAwsCredentialFile`, and `InitialS3fsCredentials` implement local credential discovery. `LoadExtCredLib`, `InitExtCredLib`, `UnloadExtCredLib`, and `UpdateExtCredentials` implement the dynamic plugin path.

Control flow: option parsing sets mode flags and source-specific fields. `CheckAllParams` first validates bucket syntax and incompatible credential combinations, then either loads built-in credentials or initializes an external library. Built-in credential initialization short-circuits for public buckets, IAM/ECS/plugin modes, explicit access keys, then searches explicit passwd file, environment variables, `AWS_CREDENTIAL_FILE`, `${HOME}/.aws/credentials`, `${HOME}/.passwd-s3fs`, and `/etc/passwd-s3fs`. Runtime token refresh happens in `CheckIAMCredentialUpdate`: if IAM/ECS/IBM/plugin credentials expire within `IAM_EXPIRE_MERGING`, it refreshes through built-in metadata calls or the plugin.

State and persistence: credential fields (`AWSAccessKeyId`, `AWSSecretAccessKey`, `AWSAccessToken`, expiration, IAM role/token/version) are protected by `token_lock`. Durable sources are external files and metadata services; this file itself does not persist secrets. It stores the selected passwd file path, AWS profile, IAM URL/fields, ECS/IBM/session flags, external library handles and function pointers, and the static bucket name.

Dependencies and integration points: relies on `S3fsCurl` policy state, `s3fs_threadreqs` direct IAM request helpers, passwd/profile parsing helpers from `string_util`, expiration conversion from auth/meta code, bucket globals (`pathrequeststyle`, `s3host`), logging, `dlopen`/`dlsym`, and `show_usage`. It is consumed by request signing and token refresh paths in the curl layer.

Risks: IAM credential parsing is ad hoc string scanning rather than JSON parsing, so malformed values, escaped quotes, or field-name collisions can behave incorrectly. `InitialS3fsCredentials` calls `SetAccessKeyWithSessionToken` and then unconditionally calls `SetAccessKey`, which preserves `is_use_session_token` but overwrites only key/secret; this should be regression-tested to ensure the token remains available. IAM metadata calls are made while holding `token_lock`, and comments warn that curl retry logic must not re-enter `S3fsCred`. External credential libraries execute in-process and return heap strings that must be freed exactly as expected. Passwd-file permission checks are security-sensitive and have special `/etc/passwd-s3fs` behavior.

Test signals: cover each credential precedence branch, invalid mixed options, passwd-file permission modes, per-bucket credential selection, AWS profile session-token requirements, IMDSv2 fallback to v1 on `-ENOENT`, IBM IAM field parsing, ECS missing environment variable, external library missing required/optional symbols, token refresh at the merge window, and bucket-name validation for virtual-hosted/path-style modes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/s3fs_cred.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/s3fs_cred.h -->
# sources/user-network-fs/s3fs-fuse/src/s3fs_cred.h

Purpose: declares the `S3fsCred` singleton and credential-management contract for the rest of s3fs-fuse. It centralizes credential source configuration, mutable access-token state, IAM metadata settings, external credential library function pointers, and public auth entry points.

Important APIs and types: `iamcredmap_t` maps IAM response fields. `S3fsCred::get()` provides the process-wide singleton. Public APIs include `SetBucket`, `GetBucket`, `IsIBMIAMAuth`, `LoadIAMRoleFromMetaData`, `CheckIAMCredentialUpdate`, `GetCredFuncVersion`, `DetectParam`, and `CheckAllParams`. Private APIs model local credential files, AWS profiles, IAM/ECS/IBM URLs and parsing, token refresh, external library loading, and bucket-parameter validation. Constants define IAM metadata endpoints, IMDSv2 headers, token TTL, field names, and refresh margin.

Control flow: callers configure the singleton through option detection, then call `CheckAllParams` during mount setup. After setup, request signing code calls `CheckIAMCredentialUpdate` to get current credential material and trigger refresh as needed. IAM role auto-detection is separated into `LoadIAMRoleFromMetaData`, allowing curl initialization before metadata access.

State and persistence: the class owns process memory for secrets, tokens, expiration, IAM role, selected profile, passwd-file path, plugin path/options, and plugin handles. Thread-safety annotations mark credential/token fields as guarded by `token_lock`, but some flags and configuration strings are not annotated and are expected to be startup-only.

Dependencies and integration points: includes `s3fs_extcred.h` for plugin ABI typedefs, `types.h`/`common.h` for shared maps and annotations, and is used by curl/auth, option parsing, and mount initialization code.

Risks: the header exposes only coarse public operations, which is good for containment, but the singleton means tests and repeated mounts must carefully reset process state. Returning `const std::string&` from locked accessors can be unsafe if references escape the lock; public `GetIAMRole()` currently returns a reference after releasing its local lock. Plugin ABI function pointers require exact C symbol signatures.

Test signals: compile-time thread-safety annotation checks, singleton lifecycle tests, option-detection table tests, and tests that call public APIs in the same order as mount startup and request signing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/s3fs_cred.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/s3fs_extcred.h -->
# sources/user-network-fs/s3fs-fuse/src/s3fs_extcred.h

Purpose: defines the C ABI that external credential libraries must implement so s3fs can delegate credential initialization, refresh, version reporting, and cleanup.

Important APIs and types: required symbols are `VersionS3fsCredential(bool detail)` and `UpdateS3fsCredential(...)`. Optional symbols are `InitS3fsCredential(const char*, char**)` and `FreeS3fsCredential(char**)`. Typedefs `fp_VersionS3fsCredential`, `fp_InitS3fsCredential`, `fp_FreeS3fsCredential`, and `fp_UpdateS3fsCredential` match the `dlsym` casts in `s3fs_cred.cpp`. `S3FS_FUNCATTR_WEAK` is intentionally overrideable for internal weak symbol builds.

Control flow: s3fs loads a shared library, resolves the required and optional symbols, calls init once after load, calls update whenever token refresh is needed, and calls free before unload/destruction. Error strings and credential strings are allocated by the plugin and freed by the caller.

State and persistence: this header owns no state. It defines ownership transfer rules for strings and the token expiration value, using `long long` to avoid ABI ambiguity around `time_t`.

Dependencies and integration points: consumed by both s3fs core and external credential-library authors. It must remain C-compatible despite being included from C++.

Risks: ABI drift is high impact: changing argument order, allocation contract, or symbol names breaks plugins. The caller expects heap allocations compatible with `free()`. Plugins run inside the s3fs process, so failures or unsafe code affect the filesystem.

Test signals: build a minimal plugin implementing required-only symbols, a plugin implementing all symbols, and failure plugins that return null strings or invalid expiration. Verify `credlib_opts` propagation and caller-side freeing under sanitizers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/s3fs_extcred.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/s3fs_global.cpp -->
# sources/user-network-fs/s3fs-fuse/src/s3fs_global.cpp

Purpose: defines shared process-wide configuration and request counters declared elsewhere, including foreground/logging flags, multipart/path/XML/security flags, endpoint settings, program/instance names, and atomic S3 operation counters.

Important APIs and types: no functions are defined. Exported globals include `foreground`, `nomultipart`, `pathrequeststyle`, `noxmlns`, `insecure_logging`, `program_name`, `service_path`, `s3host`, `region`, `cipher_suites`, `instance_name`, and atomics such as `num_requests_head_object`, `num_requests_put_object`, and multipart counters.

Control flow: these variables are initialized at process start with defaults and then mutated by option parsing and runtime request code. Logging, credentials, XML parsing, and curl behavior read these globals directly.

State and persistence: all state is in process memory. Request counters are atomic for concurrent request updates; configuration strings and bools are not atomic and are expected to settle during initialization.

Dependencies and integration points: includes `common.h`, which likely declares these externs and their types. Integrated broadly with logger, credential checks, XML namespace behavior, curl request construction, metrics, and user-facing launch/version behavior.

Risks: global mutable state makes test isolation and multi-mount-in-one-process scenarios fragile. Non-atomic configuration reads are only safe if mutation is limited to startup. `insecure_logging` affects secret masking throughout the process.

Test signals: startup default tests, option parsing tests that validate global mutation, concurrent request tests for atomic counters, and regression tests ensuring secret masking follows `insecure_logging`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/s3fs_global.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/s3fs_help.cpp -->
# sources/user-network-fs/s3fs-fuse/src/s3fs_help.cpp

Purpose: provides static user-facing usage, full help, version, and short-version output for the `s3fs` command.

Important APIs and functions: `show_usage()` prints the short command form using `program_name`. `show_help()` prints usage and the large `help_string`. `show_version()` prints version, commit hash, crypto backend, license, and warranty text. `short_version()` returns a static compact version string.

Control flow: CLI option parsing calls these functions for `--help`, `--version`, argument errors, and launch logging. The help text documents mount, unmount, utility mode, s3fs options, FUSE/mount options, and misc flags.

State and persistence: no mutable local state; output is generated from static text plus compile-time `VERSION`/`COMMIT_HASH_VAL`, runtime `program_name`, and `s3fs_crypt_lib_name()`.

Dependencies and integration points: depends on `common.h` for `program_name` and version macros, and `s3fs_auth.h` for crypto library naming. It must track behavior implemented across option parsing, credential, cache, curl, and request modules.

Risks: static help can drift from actual option semantics. Because the help text mentions security behavior for TLS and credential logging, stale text can cause operational risk. Very large string literals are easy to edit incorrectly, including missing newline boundaries between adjacent entries.

Test signals: snapshot tests for `--help`, `--version`, and invalid bucket usage; checks that each documented credential option is accepted by parser; checks for security-warning text around insecure TLS/logging options.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/s3fs_help.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/s3fs_help.h -->
# sources/user-network-fs/s3fs-fuse/src/s3fs_help.h

Purpose: declares the small public help/version surface used by CLI parsing and startup logging.

Important APIs: `show_usage()`, `show_help()`, `show_version()`, and `short_version()`.

Control flow: command-line parsing calls the printing functions for help/version/error paths; `print_launch_message` uses `short_version()` for startup logs.

State and persistence: no state is declared. The implementation reads shared globals and compile-time macros.

Dependencies and integration points: included by credential validation for usage output and by utility/startup code for launch messaging.

Risks: low implementation risk, but declarations are part of a broad CLI path; signature changes would ripple through startup and validation code.

Test signals: compile checks for all include sites and CLI smoke tests for help/version output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/s3fs_help.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/s3fs_logger.cpp -->
# sources/user-network-fs/s3fs-fuse/src/s3fs_logger.cpp

Purpose: implements s3fs logging, including singleton lifecycle, syslog integration, file logging, timestamp formatting, debug-level transitions, environment overrides, and printf-style log emission.

Important APIs and functions: `S3fsLog::IsS3fsLogLevel`, `GetCurrentTime`, `SetLogfile`, `ReopenLogfile`, `SetLogLevel`, `BumpupLogLevel`, `SetTimeStamp`, constructor/destructor, `LowLoadEnv`, `LowSetLogfile`, `LowSetLogLevel`, `LowBumpupLogLevel`, `Printf`, `s3fs_low_logprn`, and `s3fs_low_logprn2`.

Control flow: constructing the singleton opens syslog and reads `S3FS_LOGFILE` and `S3FS_MSGTIMESTAMP`. Static methods delegate to the singleton for mutable operations. Log macros in the header call `s3fs_low_logprn*`, which either write atomically to stdout/stderr/logfile or send to syslog depending on foreground/logfile state. `SIGUSR2` bumps log level via `BumpupLogLevel`; `SIGHUP` reopens via `ReopenLogfile`.

State and persistence: static state holds singleton pointer, current debug level, `FILE*` logfile, logfile path, and timestamp mode. File logs persist externally. `Printf` bypasses stdio buffering and writes directly to the file descriptor, retrying on `EINTR`.

Dependencies and integration points: uses process globals `foreground` and `instance_name`, `CaseInsensitiveStringView`, syslog APIs, `clock_gettime`/`gettimeofday`, and signal handling.

Risks: `GetCurrentTime` appears to invert `clock_gettime` handling: on failure it reads `tsnow`, and on success it calls `gettimeofday`, so timestamp behavior deserves correction/testing. `ReopenLogfile` appears to reject non-empty `logfile`, which conflicts with its purpose and likely breaks SIGHUP log rotation. Static logger state is not mutex-protected, so concurrent logfile changes and logging can race. Formatting code computes `vsnprintf` lengths without checking negative values in `s3fs_low_logprn*`.

Test signals: tests for `S3FS_LOGFILE`, `S3FS_MSGTIMESTAMP`, log-level masks, foreground/syslog branching, SIGHUP reopen, SIGUSR2 level cycling, concurrent logging line integrity, and timestamp sanity under successful `clock_gettime`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/s3fs_logger.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/s3fs_logger.h -->
# sources/user-network-fs/s3fs-fuse/src/s3fs_logger.h

Purpose: declares `S3fsLog`, log levels, logging macros, and FUSE-context logging helpers used throughout s3fs-fuse.

Important APIs and types: `S3fsLog::Level` encodes CRIT/ERR/WARN/INFO/DBG as bit masks. Static helpers map levels to syslog priorities and string prefixes, provide timestamp text, select output/error streams, set/reopen log files, change level, and write atomic formatted output. Macros include `S3FS_PRN_EXIT`, `S3FS_PRN_CRIT`, `S3FS_PRN_ERR`, `S3FS_PRN_WARN`, `S3FS_PRN_INFO*`, `S3FS_PRN_DBG`, `S3FS_PRN_CURL`, `S3FS_PRN_CACHE`, and FUSE-context variants.

Control flow: call sites use macros, which first check the active log level and then pass file/function/line context to implementation functions. Exit/init/launch/cache/curl macros have specialized output behavior. FUSE macros append `pid`, `uid`, and `gid` when `fuse_get_context()` is available.

State and persistence: declares static logger process state but no per-call persistence. Macros may expose sensitive values unless callers mask them or `insecure_logging` intentionally disables masking in helper functions.

Dependencies and integration points: includes syslog, common globals, FUSE context APIs via call sites, and is included by nearly every module for diagnostics.

Risks: macro-heavy logging can evaluate varargs in surprising ways and couples call sites to global `foreground`/`instance_name`. Format strings are compile-checked on implementation functions but macro varargs still need care. Because logging is used in signal handlers, only async-signal-safe paths should be called from handlers, but current handlers call higher-level logging operations.

Test signals: compile with format warnings, exercise every macro at each level, verify FUSE-context suffixes, and verify sensitive values are masked at representative credential and IAM call sites.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/s3fs_logger.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/s3fs_threadreqs.cpp -->
# sources/user-network-fs/s3fs-fuse/src/s3fs_threadreqs.cpp

Purpose: implements the threaded and direct request helpers that adapt high-level filesystem operations to `S3fsCurl` calls. It covers HEAD, multi-HEAD, DELETE, PUT metadata, PUT object, list bucket, bucket check, multipart upload/copy/complete/abort, parallel GET, single GET, and direct IAM metadata requests.

Important APIs and functions: worker functions such as `head_req_threadworker`, `multi_head_req_threadworker`, `multipart_upload_part_req_threadworker`, `multipart_put_head_req_threadworker`, and `parallel_get_object_req_threadworker` execute with a provided `S3fsCurl`. Public wrappers such as `head_request`, `put_request`, `multipart_upload_request`, `mix_multipart_upload_request`, `multipart_put_head_request`, `parallel_get_object_request`, and `get_object_request` package parameters for `ThreadPoolMan`. Direct IAM helpers `get_iamv2api_token_request`, `get_iamrole_request`, and `get_iamcred_request` intentionally bypass the thread pool.

Control flow: simple operations create a stack parameter struct and call `ThreadPoolMan::AwaitInstruct`. Fan-out operations allocate parameter structs with `unique_ptr`, schedule asynchronous workers with a semaphore, release ownership to the worker, wait for all semaphore completions, and then inspect shared result state. Multipart uploads initiate an upload ID, schedule parts, abort on scheduling or worker failure, and complete with collected ETags. Multi-HEAD and parallel GET/copy workers retry on selected curl/HTTP failures, incrementing shared retry counters under locks.

State and persistence: state is mostly per-request and passed through parameter structs. Shared fan-out state includes semaphores, `std::mutex` locks, retry counters, first-error result integers, not-found lists, `etaglist_t`, and `filepart` metadata. Persistent side effects occur through S3 object changes, local file descriptor reads/writes, stat-cache updates, and cache/SSE helper state.

Dependencies and integration points: central integration layer for `S3fsCurl`, `ThreadPoolMan`, `Semaphore`, `StatCache`, `SyncFiller`, metadata/stat conversion, SSE lookup, XML ETag parsing, URL resource construction, fdcache page lists, and logging. Credential code calls direct IAM helpers.

Risks: fan-out code depends on every scheduled worker releasing its semaphore and owning/finalizing heap parameters. `multipart_put_head_request` declares `int result;` without obvious initialization before the scheduling loop, making post-drain checks potentially undefined if no scheduling failure occurred before assignment. Shared retry counters are global per fan-out operation, so one part's retries can affect siblings. Multipart paths must abort uploads on all partial failures to avoid leaked incomplete uploads. Direct IAM helpers avoid thread-pool deadlock, but still perform network I/O while callers may hold credential locks.

Test signals: unit or integration tests for each wrapper's `AwaitInstruct` failure path, multipart success and abort-on-part-failure, scheduling failure after some parts queued, retry exhaustion on 400/500/timeout/partial file, parallel GET range writes, multi-HEAD not-found behavior and stat-cache fills, direct IAM helper errors, and sanitizers for uninitialized `result`/lifetime issues.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/s3fs_threadreqs.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/s3fs_threadreqs.h -->
# sources/user-network-fs/s3fs-fuse/src/s3fs_threadreqs.h

Purpose: declares request parameter structs, worker entry points, high-level request wrappers, multipart helpers, and direct IAM request helpers for s3fs-fuse's threaded request layer.

Important APIs and types: structs such as `head_req_thparam`, `multi_head_req_thparam`, `multipart_upload_part_req_thparam`, `multipart_put_head_req_thparam`, and `parallel_get_object_req_thparam` define the data shared between caller and worker. Public functions include synchronous wrappers for HEAD/DELETE/PUT/list/check/get, asynchronous multi-head and multipart/parallel operations, and direct IAM token/role/credential calls. `retrycnt_t` maps paths to retry counts.

Control flow: headers expose a two-level API: worker functions compatible with `ThreadPoolMan`, and utility wrappers that callers should use. Some wrappers are await-style and stack-safe; others require heap-allocated params because workers outlive the scheduling call.

State and persistence: structs hold pointers to caller-owned state (`headers_t`, locks, semaphores, result ints, ETag records, response strings). Correct lifetime is part of the API contract. No global state is declared here.

Dependencies and integration points: includes metadata headers, curl, fdcache page data, object lists, sync filler, and semaphores. Used by filesystem operation code and by credential metadata refresh code.

Risks: many raw pointers are nullable in structs and validated only at runtime. Callers must keep pointed-to locks/results/ETags/semaphores alive until workers finish. Function signatures expose low-level file descriptors and offsets, so invalid descriptors/ranges propagate to network/file I/O paths.

Test signals: compile-time coverage for all declarations, lifecycle tests around async wrappers, null-parameter worker tests, and integration tests using fake `ThreadPoolMan`/`S3fsCurl` to verify parameter propagation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/s3fs_threadreqs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/s3fs_util.cpp -->
# sources/user-network-fs/s3fs-fuse/src/s3fs_util.cpp

Purpose: implements miscellaneous utilities for path prefixing, sysconf-derived buffer sizing, UID/GID lookups, safe basename/dirname wrappers, recursive directory creation/deletion, directory permission checks, launch logging, `fclose` wrapping, and sensitive-string masking.

Important APIs and functions: `get_realpath`, `init_sysconf_vars`, `get_username`, `is_uid_include_group`, `mydirname`, `mybasename`, `mkdirp`, `get_exist_directory_path`, `check_exist_dir_permission`, `delete_files_in_dir`, `print_launch_message`, `s3fs_fclose`, and `mask_sensitive_string`.

Control flow: startup should call `init_sysconf_vars` before UID/GID helpers. Path helpers are used by request code to combine `mount_prefix` and object paths and to safely call libc `dirname`/`basename` under a mutex. Permission helpers use `stat`, `get[e]uid`, and group membership to decide cache/directory usability. Launch logging builds a masked command line unless insecure logging is enabled, then logs TLS-warning messages based on curl settings.

State and persistence: global `mount_prefix` and static max buffer sizes are process state. Filesystem side effects include directory creation and recursive deletion. Launch messages persist only through logging.

Dependencies and integration points: depends on libc/POSIX filesystem and passwd/group APIs, `s3fs_logger`, `string_util`, `s3fs_help`, and `S3fsCurl` TLS settings. `scope_guard` from the header is used for `closedir`.

Risks: `mkdirp` builds relative components by appending `component + "/"`, so absolute path handling and empty components need coverage. Recursive deletion is powerful and should only be called with trusted cache directories. `get_username` depends on prior `init_sysconf_vars`; missing initialization may produce zero-size/undefined behavior. `check_exist_dir_permission` requires full `rwx`, which may be stricter than some use cases.

Test signals: absolute/relative/trailing-slash tests for path helpers and `mkdirp`, passwd/group lookup tests including missing users/groups, permission matrix tests for owner/group/other directories, recursive deletion tests with files/subdirs and failure injection, and launch-message masking/TLS-warning tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/s3fs_util.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/s3fs_util.h -->
# sources/user-network-fs/s3fs-fuse/src/s3fs_util.h

Purpose: declares the utility functions implemented by `s3fs_util.cpp` and defines a small RAII `scope_guard` helper for cleanup callbacks.

Important APIs and types: function declarations cover real path construction, sysconf initialization, user/group lookup, basename/dirname wrappers, directory creation/discovery/permission/deletion, launch logging, sensitive masking, and `s3fs_fclose`. `scope_guard` stores a `std::function<void()>`, calls it on destruction, and can be dismissed.

Control flow: call sites construct `scope_guard` around resources that need cleanup unless the operation is dismissed. Utility functions are used by startup, cache handling, request construction, and logging.

State and persistence: no state is declared in the header, but the implementation uses process globals and filesystem state.

Dependencies and integration points: includes `<functional>` and `<string>`, supplies clock fallback macros for portability, and is included by request, XML, and support modules.

Risks: `scope_guard` uses `std::function` and compares it to `nullptr`; this is convenient but heavier than a templated guard and only supports non-movable usage. Header-level clock macro fallbacks may mask platform differences.

Test signals: compile coverage for C++ standard versions supported by the project, RAII cleanup/dismiss behavior, and include-order portability tests around clock macros.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/s3fs_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/s3fs_xml.cpp -->
# sources/user-network-fs/s3fs-fuse/src/s3fs_xml.cpp

Purpose: implements XML parsing helpers for S3 ListBucket/ListObjects responses, continuation markers, incomplete multipart upload listings, object extraction into `S3ObjList`, and simple single-key XML extraction.

Important APIs and functions: `GetXmlNsUrl` caches namespace discovery. `get_base_exp`, `get_prefix`, `get_next_continuation_token`, `get_next_marker`, and `is_truncated` extract common response fields. `get_object_name` reduces full S3 keys relative to a listed path. `get_incomp_mpu_list` builds incomplete multipart upload records. `append_objects_from_xml_ex` and `append_objects_from_xml` populate `S3ObjList` from `Contents` and `CommonPrefixes`. `simple_parse_xml` parses a small document and returns the text for a named child element.

Control flow: callers pass a parsed libxml document. Namespace-aware XPath expressions are assembled dynamically unless `noxmlns` is set. Object appending discovers the response prefix, creates XPath contexts, appends contents and common prefixes separately, extracts optional ETag/Size/LastModified, decodes encoded CR characters, and inserts normalized names into `S3ObjList`.

State and persistence: static namespace cache stores one namespace string for up to 60 seconds under `xml_parser_mutex`; this is process-wide, not document-specific. Parsed results are stored in caller-owned `S3ObjList` or incomplete MPU lists. No disk persistence.

Dependencies and integration points: uses libxml2 XPath/parser APIs, global `noxmlns`, logging, path helpers from `s3fs_util`, string conversions from `string_util`, MPU types, and `S3ObjList`.

Risks: namespace caching is global and time-based, so mixed S3-compatible endpoints with different namespaces in the same process can be parsed with stale namespace data. XPath construction is repetitive and string-based. `get_object_name` path-relative logic is subtle for root, trailing slash, and nested prefix cases. `simple_parse_xml` only checks direct children and is not a general XML query helper. Global `xmlSetGenericErrorFunc` in `s3fsXmlBufferParserError` affects libxml process state.

Test signals: XML fixtures with and without namespaces, ListObjects v1/v2 truncation tokens, root and nested prefixes, common prefixes, CR-encoded keys, ETag/size/last-modified extraction, incomplete MPU lists, malformed XML error buffering, `noxmlns` mode, and mixed namespace documents.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/s3fs_xml.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/s3fs_xml.h -->
# sources/user-network-fs/s3fs-fuse/src/s3fs_xml.h

Purpose: declares XML helper functions and libxml smart-pointer aliases, plus the parser-error buffer utility used when reading XML from memory.

Important APIs and types: `S3FS_XML_PARSE_FLAGS` disables external entity/network behavior where possible. `unique_ptr_xmlChar`, `unique_ptr_xmlXPathObject`, `unique_ptr_xmlXPathContext`, and `unique_ptr_xmlDoc` encode libxml cleanup ownership. `s3fsXmlBufferParserError` installs a generic error handler into a fixed buffer. Public functions include truncation/token extraction, object appending, incomplete MPU parsing, and `simple_parse_xml`.

Control flow: callers parse XML with libxml and use these functions to query known S3 response shapes. The parser-error helper is set immediately before `xmlReadMemory` and inspected after parse failure.

State and persistence: aliases own libxml allocations through custom deleters. The error helper owns a 1024-byte stack/member buffer, but the libxml generic error hook it installs is global.

Dependencies and integration points: includes libxml parser/xpath headers, `mpu_util.h`, and forward-declares `S3ObjList`. Used by request and utility-mode code.

Risks: `xmlSetGenericErrorFunc` is global and can race with concurrent XML parsing. The fixed error buffer truncates long parser diagnostics. Header includes `<cstring>` and writes parser handler inline, so changes can affect many translation units.

Test signals: parser flag verification for XXE-blocking behavior, malformed XML diagnostic capture, smart-pointer cleanup under sanitizers, and concurrent parse tests if XML parsing happens from multiple request threads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/s3fs_xml.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/s3objlist.cpp -->
# sources/user-network-fs/s3fs-fuse/src/s3objlist.cpp

Purpose: implements `S3ObjList`, the in-memory normalized list of S3 objects returned by listing operations, including directory-object normalization, metadata lookup, list/map extraction, removal, dumping, and hierarchy synthesis.

Important APIs and functions: `insert` normalizes names, directory markers, ETag, size, and last-modified data. `insert_normalized` records alias entries. Lookup helpers include `GetOrgName`, `GetNormalizedName`, `GetETag`, `GetSize`, `GetLastModified`, `IsDir`, `GetLastName`, `GetNameList`, `GetNameMap`, `HasName`, and `Remove`. `Dump` serializes debug state. `MakeHierarchizedList` adds missing parent directory entries to a flat list.

Control flow: XML parsing inserts objects or common prefixes. `insert` detects `_$folder$`, trailing slash, and explicit directory flags, removes conflicting file-vs-directory variants, stores canonical entries, then records original-to-normalized mappings when needed. Name extraction optionally filters alias entries and trims trailing slashes. Hierarchy synthesis builds a map of existing and inferred parent directories before appending missing parents.

State and persistence: object state is stored in `objects`, a map keyed by original/canonical names, with `s3obj_entry` values for normalized name, original name, ETag, size, last-modified, and type. `common_prefixes` preserves prefix entries separately. No disk persistence.

Dependencies and integration points: depends on `objtype_t` helpers/macros from `types.h`, and is populated primarily by `s3fs_xml.cpp`. Consumers include directory listing, stat cache filling, and sync filler paths.

Risks: `HasName` and `Remove` appear to compute the no-slash form incorrectly for names ending in `/` by using `substr(strName.size() - 1)`, yielding just `/` rather than removing the trailing slash. Empty `strName` passed to those functions calls `back()` and is undefined. Normalization aliases can make map contents non-obvious, so list/map extraction must consistently filter aliases. Directory-vs-file conflict removal is semantic-critical for S3-compatible directory behavior.

Test signals: insertion tests for files, `dir/`, `dir`, `dir_$folder$`, duplicate updates, alias lookup, ETag/size/last-modified preservation, `HasName`/`Remove` with trailing and non-trailing slash, empty-name defensive behavior, `GetLastName`, and hierarchy synthesis with and without slash suffixes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/s3objlist.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/s3objlist.h -->
# sources/user-network-fs/s3fs-fuse/src/s3objlist.h

Purpose: declares object-list structures and the `S3ObjList` class used to represent S3 listing results in filesystem-friendly form.

Important APIs and types: `s3obj_entry` stores normalized/original names, ETag, size, last-modified, and object type. `s3obj_t`, `s3obj_list_t`, and `s3obj_type_map_t` define map/list contracts. `S3ObjList` exposes insertion, metadata lookup, common prefix access, name list/map extraction, existence/removal, debug dumping, and `MakeHierarchizedList`.

Control flow: callers construct a list, insert objects as XML pages are parsed, then query names and metadata to fill directory entries or stat caches. Private helpers keep canonicalization details inside the class.

State and persistence: all state is in memory in `objects` and `common_prefixes`. The class does not provide locking, so callers must avoid concurrent mutation or guard externally.

Dependencies and integration points: relies on `types.h` for `objtype_t`; used by XML parsing, multi-head/stat fill code, and directory listing code.

Risks: because the class mixes canonical entries and normalization aliases in one map, callers must understand `OnlyNormalized` behavior. Lack of locking is fine for per-request objects but unsafe if shared. Metadata defaults (`size = -1`, empty last-modified) must be handled by consumers.

Test signals: class-level tests for every public method, especially alias filtering, common prefix retention, and directory type classification.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/s3objlist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/sighandlers.cpp -->
# sources/user-network-fs/s3fs-fuse/src/sighandlers.cpp

Purpose: implements process signal handling for runtime cache checks, log-level bumping, and logfile reopening.

Important APIs and functions: `S3fsSignals::SetUsr1Handler` enables SIGUSR1 cache checking and configures output. `HandlerUSR1` wakes a worker thread. `CheckCacheWorker` drains queued signals and calls `FdManager::CheckAllCache`. `HandlerUSR2` bumps logging level. `InitUsr2Handler` and `InitHupHandler` register handlers. `HandlerHUP` reopens the log file. Constructor/destructor initialize and tear down handlers, and `WakeupUsr1Thread` releases the semaphore.

Control flow: setup optionally enables SIGUSR1 only if the platform supports `SEEK_DATA`/`SEEK_HOLE` and cache output can be configured. The singleton constructor installs SIGUSR2 and SIGHUP unconditionally and starts the SIGUSR1 worker if enabled. SIGUSR1 itself only releases a semaphore; the worker performs cache scanning outside the handler context. Destruction disables the worker, releases it, joins, and resets resources.

State and persistence: static `enableUsr1` gates the worker and handler behavior. Instance state owns the worker thread and semaphore. Side effects include signal-handler registration, cache-check output, log-level changes, and logfile reopening.

Dependencies and integration points: depends on `Semaphore`, `S3fsLog`, and `FdManager`. Initialization is exposed through `S3fsSignals::Initialize()` in the header and should occur during process startup.

Risks: SIGUSR2 and SIGHUP handlers call non-async-signal-safe C++/logging code directly. `enableUsr1` is a plain bool shared between signal handlers, main thread, and worker thread. Handler registration does not preserve previous handlers. Destructor joins only when SIGUSR1 was enabled.

Test signals: signal-integration tests for SIGUSR1 cache checks, coalescing queued semaphore releases, SIGUSR2 log-level cycling, SIGHUP logfile reopen, unsupported SEEK_DATA/SEEK_HOLE behavior, and thread teardown under repeated initialize/destroy cycles.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/sighandlers.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/sighandlers.h -->
# sources/user-network-fs/s3fs-fuse/src/sighandlers.h

Purpose: declares the `S3fsSignals` singleton responsible for installing and coordinating s3fs runtime signal behavior.

Important APIs and types: public `Initialize()` forces singleton creation, and `SetUsr1Handler(const char* path)` enables cache-check handling before initialization. Private/protected handlers and helpers cover SIGUSR1, SIGUSR2, SIGHUP, cache worker management, semaphore wakeups, and teardown.

Control flow: callers configure SIGUSR1 output first, then call `Initialize`. Signal handlers are static because they are registered with `sigaction`; instance state holds the worker resources.

State and persistence: static `enableUsr1` plus owned `std::thread` and `Semaphore`. No persistent storage beyond logs/cache-check output.

Dependencies and integration points: includes `psemaphore.h`; implementation integrates with `FdManager` and `S3fsLog`.

Risks: singleton construction order matters because `SetUsr1Handler` only toggles state and output; if called after `Initialize`, the SIGUSR1 thread will not be started by the constructor. Plain static bool is used across threads/signals.

Test signals: startup-order tests for setting SIGUSR1 before/after initialization, handler registration failures, and clean destruction of the worker thread.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/sighandlers.h -->
