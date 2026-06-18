# subset-b-000494 Research Report

This grouped report covers the assigned Alluxio FUSE entry points, JNI/JNR filesystem implementations, stream/auth helpers, metadata/options utilities, and focused unit tests. Each section is delimited for deterministic reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/AlluxioFuse.java -->
# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/AlluxioFuse.java

Purpose: command-line entry point and launcher for standalone Alluxio FUSE. It parses mount point, mounted Alluxio path, root UFS, mount options, help, and update-check flags; mutates the runtime `InstancedConfiguration`; creates `FuseOptions`; starts metrics, optional web service, JVM pause monitoring, and optional update-check heartbeat; then mounts either JNI FUSE or legacy JNR FUSE.

Important APIs and flow: `main` parses CLI, applies `setConfigurationFromInput`, creates `FileSystemContext`, optionally loads cluster config from master, and calls `launchFuse`. `launchFuse` validates configuration, loads the requested libfuse version, creates the mount directory when missing, then instantiates `AlluxioJniFuseFileSystem` when `FUSE_JNIFUSE_ENABLED` is true or `AlluxioJnrFuseFileSystem` otherwise. JNI mode installs a `FuseSignalHandler` for `TERM`; JNR mode adapts mount options to `-o...`.

State, dependencies, and integration: this class owns process-level state only through global configuration, metrics sinks, optional `FuseWebServer`, and update-check executor. It depends on Alluxio client `FileSystem`, `FileSystemContext`, FUSE native library loading, heartbeat infrastructure, and `PropertyKey` configuration. Risks include process exit on launch failure, option parsing that splits only on `=`, mutation of global configuration, and cleanup behavior differing between JNI forced unmount and JNR shutdown hooks. Test signals are mostly indirect through filesystem implementation tests and option/path behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/AlluxioFuse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/AlluxioFuseOpenUtils.java -->
# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/AlluxioFuseOpenUtils.java

Purpose: small flag decoder for FUSE `open`/`create` access modes. It maps masked `O_ACCMODE` bits to `OpenAction.READ_ONLY`, `WRITE_ONLY`, `READ_WRITE`, or fallback `NOT_SUPPORTED`, and exposes helpers for `O_TRUNC` and `O_CREAT`.

Important APIs and flow: `getOpenAction(int)` masks the input flag with `O_ACCMODE` and switches on JNR `OpenFlags`; `containsTruncate` and `containsCreate` perform bit tests. The semantics are tuned for Alluxio's write-once model: completed files are read-only, write opens create or truncate, and read-write is deferred to existing-file/no-truncate versus write-mode cases in stream code.

State, dependencies, risks, and tests: no persistent state. It depends only on `jnr.constants.platform.OpenFlags`, even for JNI callers. Risks are platform flag interpretation and missing coverage for `O_CREAT`/`O_TRUNC` helpers. `AlluxioFuseOpenUtilsTest` validates representative Linux-style flags with high-order bits preserved.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/AlluxioFuseOpenUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/AlluxioFuseRestServiceHandler.java -->
# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/AlluxioFuseRestServiceHandler.java

Purpose: Jersey REST resource for operational FUSE service control. The current surface is a single log-level mutation endpoint under `/fuse/logLevel`.

Important APIs and flow: `logLevel(@QueryParam logName, @QueryParam level)` wraps `LogUtils.setLogLevel` with `RestUtils.call`, using global configuration for response handling. Constants define the service prefix and query names.

State, dependencies, risks, and tests: it mutates logging state and has no local persistence. It is integrated by `FuseWebServer`, which scans package `alluxio.fuse` under Alluxio's REST API prefix. Risks include exposing runtime log mutation when the FUSE web server is enabled and relying on caller-provided logger names/levels. No direct assigned unit test covers this handler.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/AlluxioFuseRestServiceHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/AlluxioFuseUtils.java -->
# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/AlluxioFuseUtils.java

Purpose: shared utility hub for JNI/JNR FUSE code. It centralizes name-length checks, Alluxio create/delete/set-attribute wrappers, libfuse selection, cluster config loading, stat filling, UID/GID translation, FUSE install checks, error-code mapping, completion waits, instrumentation, path resolution, and test-only native `FuseFileInfo` allocation.

Important APIs and flow: `createFile` builds `CreateFilePOptions`, creates the Alluxio file, and invokes `AuthPolicy` to set owner/group. `fillStat` overloads translate either `URIStatus` or in-progress `CreateFileStatus` to JNI `FileStat`. `waitForFileCompleted` polls `getStatus` up to 5 seconds to bridge asynchronous release. `call` wraps every FUSE callback with debug logs, timers, failure counters, slow-call warning, and throwable-to-`EIO` guard. `getPathResolverCache` joins mount-relative FUSE paths to either `FUSE_MOUNT_ALLUXIO_PATH` or root UFS address.

State, dependencies, risks, and tests: local state is limited to static thresholds and constants; external state includes shell user/group databases, Alluxio master config, metrics timers, and path cache contents. Risks include shell-command portability/injection around user/group names, inconsistent nanosecond scaling in tests versus implementation, coarse `EIO` fallback masking details, and 5-second completion timeout changing POSIX-visible behavior. JNI and JNR tests exercise path translation, stat filling, completion waiting, name length, and error surfaces indirectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/AlluxioFuseUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/AlluxioJniFuseFileSystem.java -->
# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/AlluxioJniFuseFileSystem.java

Purpose: primary JNI-backed FUSE filesystem implementation. It implements libfuse callbacks by translating mount-relative paths to Alluxio URIs, managing open file handles, enforcing Alluxio write-once/sequential semantics through `FuseFileStream`, and mapping failures to negative errno values.

Important APIs and flow: `create` forces `O_WRONLY` then delegates to `createOrOpenInternal`; `open` uses the requested flags. Open/create allocate monotonically increasing file ids, store `FuseFileEntry<FuseFileStream>` in an `IndexedSet` by fd and path, and set `fi.fh`. `getattr` fills normal status, handles special FuseShell commands, overlays in-progress `CreateFileStatus`, and waits for incomplete files written by other clients. `read`, `write`, `flush`, and `release` resolve fd entries and delegate to stream objects. Metadata operations create directories, delete files/dirs, rename with JNI rename flag handling, chmod/chown via auth policy, limited truncate support, no-op `utimens`, unsupported symlink, statfs from cached block master info, and bounded unmount waiting for open streams.

State, dependencies, risks, and tests: key mutable state is `mFileEntries`, `mNextOpenFileId`, path resolver cache, stat cache, auth policy, and stream factory. Integration points include Alluxio `FileSystem`, `BlockMasterClient`, `FuseShell`, metrics gauges, `AuthPolicyFactory`, and JNI structs. Risks include path index uniqueness preventing multiple entries for the same path despite comments about streams, best-effort unmount waiting on async release, rename delete-then-rename semantics for overwrite, unsupported incomplete-source rename, `truncate` returning `EEXIST` for missing nonzero truncation, and UFS mode returning zeroed `statfs`. `AlluxioJniFuseFileSystemTest` covers chmod/chown, create, name limits, flush, getattr waiting and in-progress writes, mkdir, open/read/write, rename errors, unlink/rmdir, path translation, and statfs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/AlluxioJniFuseFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/AlluxioJniRenameUtils.java -->
# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/AlluxioJniRenameUtils.java

Purpose: bit helpers for libfuse rename flags used by JNI FUSE. It defines `NO_FLAGS`, `RENAME_NOREPLACE`, and `RENAME_EXCHANGE`.

Important APIs and flow: `exchange(int)` and `noreplace(int)` test the respective bits; `noFlags(int)` requires exact zero. `AlluxioJniFuseFileSystem.renameInternal` uses these helpers to reject exchange, reject noreplace overwrites, delete existing destinations for no-flag overwrites, and reject unknown flags.

State, dependencies, risks, and tests: no state and no external dependencies. Risks are Linux-specific numeric flag assumptions and no validation for combined unsupported bits beyond the caller logic. Rename behavior is covered indirectly by JNI filesystem tests for no-flag success, missing source, existing destination, and length limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/AlluxioJniRenameUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/AlluxioJnrFuseFileSystem.java -->
# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/AlluxioJnrFuseFileSystem.java

Purpose: legacy JNR-FUSE implementation of the Alluxio FUSE callbacks. It predates the newer `FuseFileStream` abstraction and directly manages `FileInStream`/`FileOutStream` pairs in `OpenFileEntry`.

Important APIs and flow: `create` creates an Alluxio file, records an output stream, and optionally sets owner/group from FUSE context. `open` opens existing files for reading, waiting for incomplete files to complete. `read` seeks and copies into JNR `Pointer`; `write` copies bytes from `Pointer`, ignores duplicate lower-offset writes, and writes sequentially to the output stream. `getattr`, `readdir`, `mkdir`, `chmod`, `chown`, `rename`, `rmInternal`, `statfs`, `flush`, and `release` map JNR callbacks to Alluxio client APIs.

State, dependencies, risks, and tests: mutable state includes `mOpenFiles`, `mNextOpenFileId`, path cache, and user/group translation flag. It depends on JNR FUSE structs, Alluxio client streams, shell UID/GID translation utilities, and block master client creation. Risks include no path-scoped lock manager, `MAX_OPEN_FILES` effectively unbounded, direct `ClientContext.create()` in statfs rather than injected context, unsupported truncate, weaker rename overwrite semantics than JNI, and legacy errno differences. `AlluxioJnrFuseFileSystemTest` covers the main operations, incomplete-file wait, read offsets, path translation, statfs, and chown edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/AlluxioJnrFuseFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/CreateFileEntry.java -->
# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/CreateFileEntry.java

Purpose: legacy closeable container for an output stream opened during file creation. It stores fd id, mutable path, and output stream.

Important APIs and flow: constructor validates non-`-1` id, non-empty path, and non-null output stream. Getters expose id/path/out; `setPath` supports rename updating open-file metadata; `close` closes the output stream.

State, dependencies, risks, and tests: state is the mutable path and stream reference. It depends only on `OutputStream` and Guava preconditions. It is not thread-safe and appears superseded by `OpenFileEntry`/`FuseFileEntry` in current implementations. No assigned direct test covers it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/CreateFileEntry.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/FuseConstants.java -->
# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/FuseConstants.java

Purpose: central list of FUSE operation metric names. JNI code uses these names for call wrapping, metrics timers, and update-check operation signals.

Important APIs and flow: constants cover getattr, readdir, read, write, mkdir, unlink, rmdir, rename, chmod, chown, and truncate. `getFuseMethodNames` returns a new list in a fixed order for `UpdateChecker`.

State, dependencies, risks, and tests: no mutable state. It depends on standard collections only. Risks are missing newer operations such as statfs, flush, release, symlink, and utimens from update-check telemetry. No direct assigned tests; usage is indirect in `UpdateChecker` and JNI callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/FuseConstants.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/FuseSignalHandler.java -->
# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/FuseSignalHandler.java

Purpose: handles JVM `TERM` signal for mounted JNI FUSE processes so unmount runs before exit.

Important APIs and flow: `handle(Signal)` logs the signal, calls `FuseUmountable.umount(false)` only for signal number 15, logs and returns on unmount failure, and otherwise calls `System.exit(0)`.

State, dependencies, risks, and tests: state is the mounted `FuseUmountable` reference. It depends on `sun.misc.Signal`, a non-standard API. Risks include exact numeric signal check, no handling for INT/HUP, returning without exit if unmount fails, and reliance on process-global signal handlers. No direct assigned test covers it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/FuseSignalHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/FuseUmountable.java -->
# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/FuseUmountable.java

Purpose: minimal interface for objects that can unmount a FUSE filesystem. It lets launch/signal code treat JNI and JNR implementations uniformly.

Important APIs and flow: `umount(boolean force)` is the only method. Implementations differ: JNI waits for open stream closure and delegates to native unmount; JNR logs and delegates to `super.umount()`.

State, dependencies, risks, and tests: no state or dependencies. The comment for `force` is confusing because JNI throws on timeout when `force` is false and suppresses timeout when true. Tested indirectly by launch/signal paths only.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/FuseUmountable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/FuseWebServer.java -->
# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/FuseWebServer.java

Purpose: Jetty/Jersey web server wrapper for FUSE REST endpoints.

Important APIs and flow: constructor delegates to `WebServer`, builds a Jersey `ResourceConfig` scanning `alluxio.fuse`, registers protobuf-aware Jackson provider, wraps it in a servlet, and mounts it under `Constants.REST_API_PREFIX/*`.

State, dependencies, risks, and tests: state lives in inherited servlet context. It depends on Alluxio web server infrastructure, Jersey, Jetty, and path utilities. Risks include package-wide resource scanning and enabling operational endpoints based on configuration. No direct assigned test covers it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/FuseWebServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/OpenFileEntry.java -->
# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/OpenFileEntry.java

Purpose: legacy open-file table entry for JNR FUSE. It stores fd id, mutable path, either input or output stream, and the next write offset.

Important APIs and flow: constructor enforces valid id/path and at least one stream. `getIn`/`getOut` identify read-only versus write-only mode; `getWriteOffset`/`setWriteOffset` support duplicate-write suppression; `setPath` supports rename; `close` closes both non-null streams and resets offset.

State, dependencies, risks, and tests: state is mutable and annotated not thread-safe; JNR synchronizes on entries during read/release but not all metadata operations. Risks include stale path index in `IndexedSet` after `setPath` if the collection does not reindex mutable fields, and no enforcement that only one stream is non-null. JNR filesystem tests indirectly exercise fd lookup, write offset handling, and release/flush.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/OpenFileEntry.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/StackFS.java -->
# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/StackFS.java

Purpose: JNI-FUSE local stack filesystem used as a performance/test harness. It maps paths under a mount point directly to a local root path without Alluxio client/server interaction.

Important APIs and flow: `transformPath` concatenates root and FUSE path. Callbacks implement local `getattr`, `readdir`, `open`, `read`, `create`, `write`, `mkdir`, recursive `rmdir`, synthetic `statfs`, `unlink`, no-op `utimens`, `rename`, `chmod`, `chown`, no-op `flush`/`release`, and fixed fs name. File metadata is read through NIO/POSIX APIs; read/write use local file streams.

State, dependencies, risks, and tests: state is only `mRoot`. It depends on local filesystem POSIX attributes, Alluxio metrics, JNI FUSE structs, and `FileUtils`. Risks include path concatenation without normalization, write opening `FileOutputStream` without append and ignoring offset, recursive `rmdir` behavior unlike POSIX empty-directory removal, a likely wrong `rename` existence error for existing destination, and synthetic statfs. No assigned direct tests cover StackFS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/StackFS.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/StackMain.java -->
# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/StackMain.java

Purpose: standalone launcher for `StackFS`.

Important APIs and flow: `main` expects mount point and source path, loads libfuse based on configuration, strips `-o` prefixes from remaining options, sets process type, starts metric sinks, and mounts `StackFS` in blocking mode. On failure it prints the stack trace, forces unmount, and exits nonzero.

State, dependencies, risks, and tests: process state includes metrics sinks and FUSE mount. It depends on global Alluxio configuration and JNI FUSE library loading. Risks include simplistic option parsing (`substring(2)`), direct stdout/stderr usage, and no validation that source path exists. No assigned direct tests cover it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/StackMain.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/auth/AuthPolicy.java -->
# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/auth/AuthPolicy.java

Purpose: abstraction for mapping FUSE/Alluxio ownership between numeric Unix IDs and Alluxio owner/group names.

Important APIs and flow: implementations initialize via `init`, optionally set owner/group after create or mkdir through `setUserGroupIfNeeded`, set explicit `uid`/`gid` through `setUserGroup`, and report current/default uid/gid. Default `getUid(owner)` and `getGid(group)` ignore their arguments and return policy defaults.

State, dependencies, risks, and tests: interface has no state. Implementations integrate with Alluxio `setAttribute`, FUSE context, and system user/group lookup. Risks are policy-specific performance and correctness differences. Auth tests exercise shared `setUserGroup` behavior and custom policy lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/auth/AuthPolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/auth/AuthPolicyFactory.java -->
# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/auth/AuthPolicyFactory.java

Purpose: configuration-driven factory for `AuthPolicy` implementations.

Important APIs and flow: `create(FileSystem, AlluxioConfiguration, FuseFileSystem)` reads `FUSE_AUTH_POLICY_CLASS`, validates it implements `AuthPolicy`, reflectively calls static `create(FileSystem, AlluxioConfiguration, Optional<FuseFileSystem>)`, invokes `init`, and returns the policy.

State, dependencies, risks, and tests: no persistent state. It depends on configuration class loading and reflection. Risks include runtime-only validation, strict static method signature, reflective exception wrapping, and requiring a present FUSE filesystem for policies such as `SystemUserGroupAuthPolicy`. Covered indirectly by JNI filesystem construction and auth policy tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/auth/AuthPolicyFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/auth/CustomAuthPolicy.java -->
# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/auth/CustomAuthPolicy.java

Purpose: auth policy that forces a configured Alluxio owner and group for newly created FUSE paths while still allowing explicit chown to other valid users/groups through the parent policy.

Important APIs and flow: static `create` reads custom user/group properties, validates they are non-empty, resolves uid/gid, constructs fixed `SetAttributePOptions`, and returns the policy. `setUserGroupIfNeeded` always sets the configured owner/group. `setUserGroup` fast-paths matching uid/gid to the configured options, otherwise delegates to `LaunchUserGroupAuthPolicy`.

State, dependencies, risks, and tests: state includes fixed uid/gid and set-attribute options. It depends on shell-backed uid/gid resolution and Alluxio `setAttribute`. Risks are startup failure when configured principals do not exist locally, and log message argument ordering appears swapped for owner/uid and group/gid. `CustomAuthPolicyTest` mocks ID resolution, verifies configured owner/group assignment, and verifies fixed uid/gid reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/auth/CustomAuthPolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/auth/LaunchUserGroupAuthPolicy.java -->
# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/auth/LaunchUserGroupAuthPolicy.java

Purpose: default auth policy that treats the user launching the FUSE process as the owner/group baseline.

Important APIs and flow: `init` resolves launch uid/gid. `setUserGroupIfNeeded` is a no-op because Alluxio client creation already uses the launch user. `setUserGroup` skips work for launch uid/gid, checks existing `URIStatus`, caches uid-to-name and gid-to-name lookups, builds `SetAttributePOptions` for resolvable IDs, and updates Alluxio attributes only when needed.

State, dependencies, risks, and tests: state includes launch ids and two Guava lookup caches. It depends on Alluxio status/setAttribute and local user/group shell utilities. Risks include stale user/group cache entries, partial updates when only uid or gid resolves, and exceptions if launch identity cannot be resolved. `AbstractAuthPolicyTest` verifies chown behavior and no duplicate `setAttribute` when owner/group already match.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/auth/LaunchUserGroupAuthPolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/auth/SystemUserGroupAuthPolicy.java -->
# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/auth/SystemUserGroupAuthPolicy.java

Purpose: auth policy that maps each FUSE request to the actual caller uid/gid from the FUSE context.

Important APIs and flow: static `create` constructs the policy; constructor requires a present `FuseFileSystem`. `setUserGroupIfNeeded` reads `getContext().uid/gid` and delegates to `setUserGroup`. `getUid`/`getGid` return current context IDs, while owner/group-specific overloads resolve names via `AlluxioFuseUtils`.

State, dependencies, risks, and tests: state is inherited file system references plus reliance on live FUSE context. It depends on JNI FUSE context and shell user/group resolution. Risks include performance overhead on create/mkdir, null or stale context outside callbacks, and local principal mismatch across clients. Covered indirectly through `AbstractAuthPolicyTest` infrastructure and JNI create/getattr paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/auth/SystemUserGroupAuthPolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/file/CreateFileStatus.java -->
# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/file/CreateFileStatus.java

Purpose: in-memory status for an actively created/written FUSE file. It extends `FileStatus` with mode, uid, and gid so `getattr` can expose a plausible stat before Alluxio marks the file complete.

Important APIs and flow: static `create(AuthPolicy, mode, fileLength)` resolves current uid/gid from the policy or uses `-1`, then constructs the status. Getters expose mode and ownership; inherited methods track length.

State, dependencies, risks, and tests: state is mutable length plus fixed mode/uid/gid. It depends on `AuthPolicy` and `AlluxioFuseUtils` constants. Risks include stale uid/gid for policies whose context changes after creation and mode `-1` if no mode was supplied. Tested indirectly by JNI `getattrWhenWriting` and stream create/write tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/file/CreateFileStatus.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/file/FileStatus.java -->
# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/file/FileStatus.java

Purpose: simple mutable length holder for open FUSE streams.

Important APIs and flow: constructor sets initial length, `getFileLength` returns it, and `setFileLength` updates it. It is used by read streams for EOF checks, write streams for visible in-progress length, and mixed streams before a concrete mode is chosen.

State, dependencies, risks, and tests: state is a plain `long` with no synchronization or volatile marker; callers synchronize at stream level where needed. No dependencies. Risks are visibility if accessed outside stream synchronization, but current JNI `getattr` reads through synchronized stream methods for write streams. Tested indirectly by read EOF and write/getattr behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/file/FileStatus.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/file/FuseFileEntry.java -->
# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/file/FuseFileEntry.java

Purpose: thread-safe container used by JNI FUSE to bind a FUSE file handle id and mount-relative path to a `FuseFileStream`.

Important APIs and flow: constructor validates non-negative id, non-empty path, and non-null stream. Getters expose id/path/stream; `close` delegates to the stream. `AlluxioJniFuseFileSystem` stores entries in an `IndexedSet` by id and path.

State, dependencies, risks, and tests: state is immutable except the underlying stream. It depends on `FuseFileStream` and Guava preconditions. Risks include path immutability, so open entries are not updated by rename in JNI mode, and path index uniqueness may conflict with multiple opens of the same path. Tested indirectly through JNI open/read/write/release paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/file/FuseFileEntry.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/file/FuseFileInOrOutStream.java -->
# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/file/FuseFileInOrOutStream.java

Purpose: lazy stream for `O_RDWR`-style opens where Alluxio cannot actually support simultaneous read/write. It chooses read-only or write-only behavior based on flags and first operation.

Important APIs and flow: `create` immediately creates a write stream when `O_TRUNC` or `O_CREAT` is present; otherwise it defers. `read` fails if write mode was chosen, lazily creates `FuseFileInStream`, and delegates. `write` and `truncate` fail if read mode was chosen, lazily create `FuseFileOutStream`, and delegate. `getFileStatus`, `flush`, and `close` delegate to the active stream or return current path length when no stream has been chosen.

State, dependencies, risks, and tests: state is synchronized optional in/out stream references plus URI/mode and dependencies. It integrates with `FileSystem`, `AuthPolicy`, `FuseReadWriteLockManager`, and open flag helpers. Risks include surprising first-operation semantics for applications expecting true read-write handles, unsupported read-after-write/write-after-read, and delayed file creation for existing-file write without truncate. Tested indirectly by JNI create/open/write/read/truncate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/file/FuseFileInOrOutStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/file/FuseFileInStream.java -->
# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/file/FuseFileInStream.java

Purpose: read-only implementation of `FuseFileStream` for completed Alluxio files.

Important APIs and flow: static `create` acquires a per-path read lock, waits for incomplete files to complete, fails missing/incomplete paths, opens a `FileInStream`, and records length. `read` validates buffer bounds, handles zero/EOF, seeks to the requested offset, reads into the JNI `ByteBuffer`, and returns bytes read. `write` and `truncate` throw; `flush` is no-op; `close` closes the stream and releases the lock once.

State, dependencies, risks, and tests: state includes the Alluxio input stream, immutable status length, URI, lock resource, and closed flag. It depends on Alluxio `FileSystem`, `FileInStream`, completion wait helper, and lock manager. Risks include synchronized read limiting parallelism per handle, fixed length not reflecting external updates, and error conversion through runtime exceptions. JNI/JNR tests cover read paths and incomplete-file open behavior indirectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/file/FuseFileInStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/file/FuseFileOutStream.java -->
# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/file/FuseFileOutStream.java

Purpose: write-only `FuseFileStream` enforcing Alluxio's write-once and sequential-write constraints while supporting selected POSIX truncate workflows.

Important APIs and flow: static `create` acquires a write lock, waits for incomplete external writes, inherits mode when omitted, records current length, deletes and recreates existing files for truncate or empty-file overwrite, or returns a stream without an output stream to allow later `truncate(0)`. `write` requires an active output stream, validates bounds, rejects non-sequential forward writes, skips duplicate lower-offset writes, and writes bytes. `truncate(0)` closes/deletes/recreates; larger truncate on an active new stream records desired length and close fills zero bytes up to that length. `close` closes streams and releases the lock.

State, dependencies, risks, and tests: state includes auth/file system, path lock, URI, `CreateFileStatus`, closed flag, and optional `FileOutStream`. It depends on `AlluxioFuseUtils`, `AlluxioFuseOpenUtils`, `AuthPolicy`, and Alluxio output streams. Risks include delete-before-create data loss on truncate, unsupported append/overwrite, zero-fill loop subtracting `DEFAULT_BUFFER_SIZE` even for smaller final write, delayed already-exists error when opening existing file without truncate, and reliance on output stream byte counters. JNI tests exercise create, flush, write duplicate suppression, getattr during writing, and truncate-related behavior indirectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/file/FuseFileOutStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/file/FuseFileStream.java -->
# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/file/FuseFileStream.java

Purpose: common stream contract for JNI FUSE read, write, mixed, flush, truncate, status, and close operations.

Important APIs and flow: implementers provide `read(ByteBuffer,size,offset)`, `write`, `getFileStatus`, `flush`, `truncate`, and `close`. Nested `Factory` owns one `FuseReadWriteLockManager` and selects `FuseFileInStream` for `O_RDONLY`, `FuseFileOutStream` for `O_WRONLY`, and `FuseFileInOrOutStream` for other access modes.

State, dependencies, risks, and tests: factory state is shared lock manager plus file system/auth policy. It depends on JNR open flag constants even when used by JNI FUSE. Risks include platform flag mismatch, treating every non-read/non-write access mode as mixed, and one factory-level lock manager per filesystem rather than externally visible lock lifecycle. Tested indirectly by JNI filesystem open/create/read/write/truncate tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/file/FuseFileStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/lock/FuseReadWriteLockManager.java -->
# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/lock/FuseReadWriteLockManager.java

Purpose: per-path read/write lock manager for JNI FUSE streams.

Important APIs and flow: `tryLock(path, mode)` hashes the path with MD5, obtains a weakly cached `ClientRWLock`, chooses read or write lock, waits up to 20 seconds, and returns a `CloseableResource<Lock>` that unlocks on close. Interrupted waits restore the interrupt flag and throw cancellation.

State, dependencies, risks, and tests: state is a Guava `LoadingCache<String, ClientRWLock>` with weak values and max reader concurrency 64 per path. It depends on Alluxio concurrency primitives and runtime exceptions. Risks include MD5 collision theoretical aliasing, weak-value lock eviction subtleties, timeout surfacing as stream creation failure, and no direct rename coordination. Tested indirectly by stream open/create behavior and unmount waiting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/lock/FuseReadWriteLockManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/meta/UpdateChecker.java -->
# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/meta/UpdateChecker.java

Purpose: heartbeat executor that periodically sends anonymized FUSE environment/operation signals to Alluxio's update-check service.

Important APIs and flow: `create(FuseOptions)` builds immutable info for local Alluxio data cache, metadata cache, kernel data cache, and underlying filesystem type, and initializes counters for selected FUSE operation timers. `heartbeat` calls `UpdateCheck.getLatestVersion` with a per-process UUID and logs if latest differs. `getFuseCheckInfo` adds operation names whose timer count increased since the previous heartbeat and updates internal counters.

State, dependencies, risks, and tests: state includes instance UUID, last-seen operation counts, and immutable FUSE info. It depends on metrics timers, URI parsing, and remote update-check service. Risks include network calls from a FUSE process, unordered map iteration, operation list omissions, and update-check defaults differing for Alluxio versus root-UFS mounts. No assigned direct unit test covers it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/meta/UpdateChecker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/options/FuseOptions.java -->
# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/options/FuseOptions.java

Purpose: immutable-ish holder for Alluxio file system options, normalized FUSE mount options, and update-check enablement.

Important APIs and flow: `create` overloads derive `FileSystemOptions`, collect non-empty `FUSE_MOUNT_OPTIONS` into a set, validate JNR is not used with libfuse3, add `big_writes` for libfuse2, add `direct_io` for JNR/libfuse2, remove unsupported `direct_io` for libfuse3, and add default `max_idle_threads=64` for libfuse3. Getters expose file system options, mutable option set reference, and update-check flag.

State, dependencies, risks, and tests: state is file system options, option set, and boolean. It depends on `AlluxioFuseUtils.getLibfuseVersion`, `FileSystemOptions`, and configuration. Risks include using a set that drops order/duplicates, returning mutable options, silently removing `direct_io` for libfuse3 after logging error, and option normalization changing user intent. Tested indirectly by launcher and filesystem construction paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/options/FuseOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/AlluxioFuseOpenUtilsTest.java -->
# sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/AlluxioFuseOpenUtilsTest.java

Purpose: unit test for access-mode decoding in `AlluxioFuseOpenUtils`.

Important APIs and flow: three tests feed representative flags with high-order bits set and assert `READ_ONLY`, `WRITE_ONLY`, or `READ_WRITE` based on the low access-mode bits.

State, dependencies, risks, and signals: no state beyond local arrays. It depends on JUnit assertions. It signals that only the `O_ACCMODE` low bits should drive access action. Coverage does not include `containsTruncate`, `containsCreate`, invalid access modes, or platform-specific flag variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/AlluxioFuseOpenUtilsTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/AlluxioJniFuseFileSystemTest.java -->
# sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/AlluxioJniFuseFileSystemTest.java

Purpose: isolated unit tests for the primary JNI FUSE filesystem using mocked Alluxio clients and native JNI structs.

Important APIs and flow: setup configures path cache size, mount root, and mount point, loads libfuse, creates mocked `FileSystemContext`/`FileSystem`, and allocates native `FuseFileInfo`. Tests cover chmod/chown variants, create and name limits, flush, getattr stat fields and incomplete-file waiting, getattr while current FUSE is writing, mkdir, open/read/incomplete-open, rename success/errors/name limit, rmdir/write/unlink, path resolver cache, and statfs from mocked block master info.

State, dependencies, risks, and signals: tests use Mockito/PowerMock, direct buffers, environment user/group lookup, and may skip when libfuse is unavailable. They provide strong behavioral signals for path translation, errno mapping, and async-release waiting. Risks are environment-sensitive uid/gid assertions, native library availability assumptions, limited coverage of truncate/symlink/utimens/readdir/release failure paths, and some mock setups using overloads that differ from production call sites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/AlluxioJniFuseFileSystemTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/AlluxioJnrFuseFileSystemTest.java -->
# sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/AlluxioJnrFuseFileSystemTest.java

Purpose: isolated unit tests for the legacy JNR FUSE filesystem.

Important APIs and flow: setup creates mocked `FileSystem`, enables user/group translation, builds `AlluxioJnrFuseFileSystem`, and allocates JNR `FuseFileInfo`. Tests mirror many JNI cases: chmod/chown variants, create/name limit, flush, getattr, incomplete-file getattr/open waits, mkdir, open/read/read offsets, rename success/errors/name limit, rmdir/write duplicate suppression/unlink, path translation, and statfs via mocked block master client.

State, dependencies, risks, and signals: tests use JNR runtime memory, Mockito/PowerMock, and local user/group lookup. They document legacy differences such as incomplete-open returning `EFAULT`, 4 KiB statfs block size, and true JNR pointer read behavior. Coverage gaps include truncate unsupported path, release close failures, readdir, and write offset edge cases beyond duplicate lower-offset write.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/AlluxioJnrFuseFileSystemTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/auth/AbstractAuthPolicyTest.java -->
# sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/auth/AbstractAuthPolicyTest.java

Purpose: abstract test base and shared behavior test for FUSE auth policies.

Important APIs and flow: `setUserGroup` test spies `AlluxioFuseUtils` to resolve uid/gid to names, invokes the concrete `mAuthPolicy`, verifies owner/group in an in-memory file system, then calls again to verify no redundant `setAttribute` when status already matches. Nested `CustomContextFuseFileSystem` supplies a controllable FUSE context; nested `UserGroupFileSystem` implements enough `FileSystem` to store and return `URIStatus` from `setAttribute`/`getStatus` while throwing for unrelated APIs.

State, dependencies, risks, and signals: state is the in-memory URI-to-status map and selected auth policy from subclasses. It depends on PowerMock static spying and many `FileSystem` interface stubs. It signals idempotent chown behavior and partial fake status behavior. Risks include the fake file system not modeling create, permissions, or missing-owner defaults, and broad unsupported methods that can hide integration drift until compile time.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/auth/AbstractAuthPolicyTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/auth/CustomAuthPolicyTest.java -->
# sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/auth/CustomAuthPolicyTest.java

Purpose: concrete tests for fixed owner/group custom auth policy.

Important APIs and flow: setup writes custom auth class/user/group config, mocks `AlluxioFuseUtils.getUid` and `getGidFromGroupName`, creates and initializes `CustomAuthPolicy`, and reuses `AbstractAuthPolicyTest` behavior. `setUserGroupIfNeed` verifies a created URI receives configured owner/group; `getUidGid` verifies owner/group arguments are ignored and configured IDs are returned.

State, dependencies, risks, and signals: state is inherited fake file system plus fixed mocked IDs. It depends on PowerMock static mocking and global modifiable configuration. It signals startup validation and configured identity behavior, but does not test invalid custom user/group, parent fallback in `setUserGroup`, or interaction with a real system user database.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/auth/CustomAuthPolicyTest.java -->
