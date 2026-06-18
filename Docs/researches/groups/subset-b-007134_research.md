# Research: subset-b-007134

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix.h -->
# sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix.h

Purpose: public/internal header for GlusterFS's POSIX storage xlator. It centralizes POSIX brick constants, platform feature includes, private state structures, inode/fd context helpers, and the FOP function signatures implemented across the POSIX storage source files.

Important APIs, types, and functions: key macros include `VECTOR_SIZE`, xattr buffer sizing, `DHT_LINKTO`, GFID handle path sizing, unlink flags, `DISK_SPACE_CHECK_AND_GOTO`, timestamp abstraction macros, `GFID_NULL_CHECK_AND_GOTO`, and `DIRECT_ALIGNED`. `struct posix_fd` tracks kernel file/dir descriptors, flags, directory EOF, janitor list linkage, owning xlator, and O_DIRECT state. `struct posix_private` is the brick-wide configuration/runtime state: base path, block size, locks, timers, AIO/io_uring fields, fsync batching, janitor/health/disk-space threads, gfid2path settings, statfs export, disk reserve, masks, and feature booleans. `posix_xattr_filler_t` and `posix_inode_ctx_t` support xattr enumeration and per-inode synchronization.

Control flow: this header is included by the POSIX xlator implementation files so they share common state and exported declarations. The macros short-circuit FOPs for full disks and invalid GFID requests before lower-level filesystem operations. The FOP prototypes map Gluster's entry, inode, fd, xattr, locking, directory, checksum, put, and copy-file-range operations to POSIX-backed implementations.

State and persistence: state described here is mostly process memory tied to the xlator instance, inode contexts, and open fd contexts. Persistent effects are indirect: base paths, GFID handles, xattrs, unlink staging paths, and backend filesystem metadata are manipulated by implementation files using these definitions. Thread state for janitor, fsyncer, health checks, disk checks, AIO, and io_uring is process-lifetime state.

Dependencies and integration points: depends on libc/POSIX headers, optional Linux/FreeBSD xattr APIs, Gluster compatibility, call-stub, mem types, AIO, and io_uring support. It integrates POSIX storage with Gluster's translator graph, inode/fd context APIs, dict/xattr system, GFID model, cloudsync state helpers, and generated xlator FOP tables elsewhere.

Risks and test signals: many declarations depend on conditional compile flags, so feature-matrix builds are important. `posix_private` has many thread and lock fields, making lifecycle and shutdown ordering risky. The GFID and disk-space macros assume valid `frame`, `priv`, and dict inputs. Test signals include POSIX xlator build coverage, FOP integration tests that exercise create/lookup/xattr/rename/unlink/statfs, disk-full behavior, GFID validation, O_DIRECT alignment paths, and AIO/io_uring configuration variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/system/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/system/Makefile.am

Purpose: automake directory dispatcher for GlusterFS system translators. It declares `posix-acl` as the only subdirectory in this source snapshot.

Important APIs, types, and functions: the only build directive is `SUBDIRS = posix-acl`, which makes automake descend into the POSIX ACL translator subtree during build, install, clean, and distribution targets.

Control flow: top-level xlator build recursion enters `xlators/system`, reads this file, and delegates all work to `xlators/system/posix-acl`.

State and persistence: no runtime state. Persistent build/install effects are produced by the subdirectory makefiles.

Dependencies and integration points: integrates the `posix-acl` module into GlusterFS's automake build hierarchy. Removing or changing this entry would detach the system ACL translator from normal builds.

Risks and test signals: the file is intentionally minimal, but stale `SUBDIRS` entries would break builds or omit translators. Test signal is a full autotools build where the `posix-acl` subdirectory is visited.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/system/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/system/posix-acl/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/system/posix-acl/Makefile.am

Purpose: automake directory dispatcher for the POSIX ACL system translator. It delegates to the `src` directory where the module is built.

Important APIs, types, and functions: the build directive is `SUBDIRS = src`.

Control flow: automake recursion enters this directory from `xlators/system/Makefile.am`, then immediately enters `src` for compilation and install rules.

State and persistence: no runtime state. Build artifacts are produced by `src/Makefile.am`.

Dependencies and integration points: connects the translator's source directory to the parent GlusterFS system xlator build.

Risks and test signals: low risk except for build omission if the directive is wrong. Test signal is that `xlators/system/posix-acl/src/posix-acl.la` is reached by a normal build.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/system/posix-acl/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/system/posix-acl/src/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/system/posix-acl/src/Makefile.am

Purpose: automake build recipe for the GlusterFS POSIX ACL translator shared module.

Important APIs, types, and functions: declares `xlator_LTLIBRARIES = posix-acl.la`, installs it under `$(libdir)/glusterfs/$(PACKAGE_VERSION)/xlator/system`, builds from `posix-acl.c` and `posix-acl-xattr.c`, links against `libglusterfs.la`, and lists the internal headers. `AM_CPPFLAGS`, `AM_CFLAGS`, and `AM_LDFLAGS` supply Gluster include and linker paths. The `access-control-compat` target creates a compatibility symlink from `xlator/features/access-control.so` to `../system/posix-acl.so`.

Control flow: normal build compiles the two C files into a module. `install-exec-local` runs `access-control-compat`; `uninstall-local` removes the compatibility symlink.

State and persistence: no runtime state, but install/uninstall mutate the target filesystem by creating/removing the legacy feature-path symlink.

Dependencies and integration points: depends on GlusterFS autotools variables, libtool module flags, libglusterfs, generated RPC XDR include paths, and the historical `features/access-control.so` module name expected by older configurations.

Risks and test signals: the compatibility symlink is path-sensitive and uses `rm -rf` on the target symlink path, so install tests should verify it resolves correctly under staged `DESTDIR`. Build tests should confirm module name, exported xlator API, and uninstall cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/system/posix-acl/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/system/posix-acl/src/posix-acl-mem-types.h -->
# sources/distributed-fs/glusterfs/xlators/system/posix-acl/src/posix-acl-mem-types.h

Purpose: memory-accounting type declarations for the POSIX ACL translator.

Important APIs, types, and functions: `gf_posix_acl_mem_types_t` starts after `gf_common_mt_end` and defines accounting IDs for ACL inode contexts, ACL/ACE allocation, temporary character buffers, translator configuration, and the end marker.

Control flow: `posix-acl.c` passes `gf_posix_acl_mt_end` to `xlator_mem_acct_init()` and uses individual enum values in `GF_CALLOC` calls for contexts, ACL entries, strings, and configuration.

State and persistence: no persistent state. The enum labels runtime heap allocations for Gluster's memory accounting subsystem.

Dependencies and integration points: includes `glusterfs/mem-types.h` and must remain synchronized with all allocation sites in the translator.

Risks and test signals: adding allocations without new or appropriate memory types reduces diagnostic accuracy. Test signals are translator startup with memory accounting enabled and leak/accounting reports that categorize POSIX ACL allocations correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/system/posix-acl/src/posix-acl-mem-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/system/posix-acl/src/posix-acl-messages.h -->
# sources/distributed-fs/glusterfs/xlators/system/posix-acl/src/posix-acl-messages.h

Purpose: stable Gluster message-ID declarations for POSIX ACL log events.

Important APIs, types, and functions: uses `GLFS_MSGID(POSIX_ACL, POSIX_ACL_MSG_EACCES)` to allocate the component message ID used when permission checks fail.

Control flow: `posix-acl.c` includes this header and logs denied access through `gf_msg(..., POSIX_ACL_MSG_EACCES, ...)`.

State and persistence: no runtime state. Message IDs are a persistence contract for log analysis and must not be removed or reused.

Dependencies and integration points: depends on `glusterfs/glfs-message-id.h` and the global component registry. Integrates POSIX ACL logs with Gluster's structured logging system.

Risks and test signals: changing IDs or component names can break log parsers and documented diagnostics. Test signals are build-time message ID generation and runtime EACCES logs that include the expected POSIX ACL message identifier.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/system/posix-acl/src/posix-acl-messages.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/system/posix-acl/src/posix-acl-xattr.c -->
# sources/distributed-fs/glusterfs/xlators/system/posix-acl/src/posix-acl-xattr.c

Purpose: binary xattr codec for Gluster's in-memory POSIX ACL representation. It parses Linux-style ACL xattr blobs into `struct posix_acl` and serializes ACLs back to xattr buffers.

Important APIs, types, and functions: `posix_ace_cmp()` orders ACEs by tag then ID. `posix_acl_normalize()` sorts ACL entries. `posix_acl_from_xattr()` validates header size, entry alignment, little-endian version, tag set, and IDs, then builds an ACL with `posix_acl_new()`. `posix_acl_to_xattr()` writes `posix_acl_xattr_header` and `posix_acl_xattr_entry` data, returning required size when the caller's buffer is too small. `posix_acl_matches_xattr()` decodes another ACL and compares entries.

Control flow: lookup/readdirp/setxattr paths in `posix-acl.c` call `from_xattr` when child translators return ACL blobs; inheritance paths call `to_xattr` to attach ACL xattrs to create requests; update paths use `matches_xattr` to avoid replacing cached ACLs when the xattr has not changed.

State and persistence: no global state. Persistent representation is the little-endian xattr blob stored by the lower POSIX xlator. In-memory ACL objects are ref-counted by `posix-acl.c`.

Dependencies and integration points: depends on endian conversion APIs, Gluster xlator types, `posix-acl.h`, and `glusterfs-acl.h` constants such as `POSIX_ACL_XATTR_VERSION`, ACL tags, and undefined ID.

Risks and test signals: `posix_acl_normalize()` calls `qsort()` with `sizeof(struct posix_ace *)` instead of `sizeof(struct posix_ace)`, which is suspicious because the array stores structs, not pointers. Invalid tags or malformed sizes fail parsing. Test signals should cover round-trip serialization, invalid version/size/tag rejection, deterministic ordering, and matching behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/system/posix-acl/src/posix-acl-xattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/system/posix-acl/src/posix-acl-xattr.h -->
# sources/distributed-fs/glusterfs/xlators/system/posix-acl/src/posix-acl-xattr.h

Purpose: public internal header for POSIX ACL xattr conversion helpers.

Important APIs, types, and functions: declares `posix_acl_from_xattr()`, `posix_acl_to_xattr()`, and `posix_acl_matches_xattr()`.

Control flow: included by `posix-acl.c` so translator FOP wrappers can decode lower xattrs, encode inherited ACLs, and compare cached ACLs with newly returned xattr data.

State and persistence: no state. The functions declared here bridge transient in-memory ACL objects and persistent xattr bytes.

Dependencies and integration points: includes `posix-acl.h` for ACL allocation/refcount API and `glusterfs/glusterfs-acl.h` for ACL binary format constants.

Risks and test signals: API users must pass trusted buffer lengths and unref returned ACLs. Test signals mirror `posix-acl-xattr.c`: parse/serialize/match coverage and malformed xattr handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/system/posix-acl/src/posix-acl-xattr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/system/posix-acl/src/posix-acl.c -->
# sources/distributed-fs/glusterfs/xlators/system/posix-acl/src/posix-acl.c

Purpose: GlusterFS system translator implementing POSIX ACL authorization in front of a child storage translator. It enforces ACL checks for lookups, opens, creates, mutation FOPs, directory reads, xattrs, and setattr operations, while caching ACL state in inode contexts.

Important APIs, types, and functions: initialization APIs are `mem_acct_init()`, `init()`, `reconfigure()`, and `fini()`. Identity helpers include `r00t()`, `frame_is_user()`, `frame_is_super_user()`, and `frame_in_group()`. ACL state APIs include `posix_acl_ctx_new/get()`, `posix_acl_new/ref/dup/unref/destroy()`, `posix_acl_get/set/set_specific()`, and `posix_acl_ctx_update()`. Permission helpers include `acl_permits()`, `sticky_permits()`, `setattr_scrutiny()`, and `setxattr_scrutiny()`. FOP wrappers are registered in `struct xlator_fops fops`, and `xlator_api` exposes the translator as identifier `access-control`.

Control flow: lookup first checks execute permission on the parent, requests access/default ACL xattrs from the child, then `posix_acl_lookup_cbk()` creates/updates the inode context from iatt and xattr data. `acl_permits()` handles superuser bypass, owner/user/group/mask/other ACE selection, minimal ACL fallback, and denial logging. Create-like operations check write+execute on the parent, inherit default ACLs through `posix_acl_inherit_*()`, encode xattrs into the request dict, then update the new inode context in callbacks. Read/write/ftruncate/fsetattr/fsetxattr/fgetxattr are conditionally registered under `FD_MODE_CHECK_IS_IMPLEMENTED`; non-FUSE fd operations recheck permissions. Rename/unlink/rmdir/link combine parent ACL checks with sticky-bit checks. Setattr enforces owner/superuser and group rules before winding. Xattr setting/removal restricts ACL xattr changes to owners or superuser and updates cached ACLs when ACL xattrs change.

State and persistence: translator-private state is `struct posix_acl_conf`, holding `acl_lock`, `super_uid`, and a minimal three-entry ACL. Per-inode `struct posix_acl_ctx` stores uid, gid, mode permissions, last FOP, and ref-counted access/default ACL pointers. ACL refcounts are guarded by `acl_lock`; inode context creation is guarded by the inode lock. Persistent ACL data lives in POSIX ACL xattrs on the child translator; this translator caches and rewrites those xattrs but does not own disk storage directly.

Dependencies and integration points: depends on Gluster defaults, dicts, xlator stack winding/unwinding, inode contexts, iatt mode helpers, ACL xattr codecs, memory accounting, structured message IDs, and child translator FOPs. It integrates with FUSE/NFS identity via `frame->root`, supports `super-uid`, and consumes `POSIX_ACL_*` and `GF_POSIX_ACL_*` xattr names.

Risks and test signals: ACL cache coherency depends on lookup/readdirp/xattr callbacks updating contexts before later FOP checks. `posix_acl_ctx_get()` logs missing contexts and many paths convert that into EIO/EACCES, so missing lookup priming can become authorization failure. `posix_acl_link()` calls `sticky_permits(frame, new->parent, new->inode)` even though hard-link destinations may not have `new->inode`, which is a null-risk path if callers do not guarantee it. Denial logs include ACL details and group membership, useful but potentially sensitive. Test signals should include owner/group/mask/other permissions, named users/groups, default ACL inheritance for files vs directories, sticky directory unlink/rename/rmdir, setxattr ACL ownership rules, setattr chmod/chown/chgrp rules, FUSE vs non-FUSE `access`, lookup/readdirp cache refresh, and `super-uid` reconfiguration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/system/posix-acl/src/posix-acl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/system/posix-acl/src/posix-acl.h -->
# sources/distributed-fs/glusterfs/xlators/system/posix-acl/src/posix-acl.h

Purpose: internal POSIX ACL translator header exposing ACL allocation, reference counting, context access, and cache get/set operations to companion source files.

Important APIs, types, and functions: declares `posix_acl_new()`, `posix_acl_ref()`, `posix_acl_unref()`, `posix_acl_destroy()`, `posix_acl_ctx_get()`, `posix_acl_get()`, and `posix_acl_set()`.

Control flow: `posix-acl-xattr.c` uses the allocation/destruction functions while translating xattrs; `posix-acl.c` implements all declarations and uses get/set/ref APIs throughout FOP callbacks.

State and persistence: no standalone state. The declared functions manipulate in-memory ref-counted ACLs and per-inode contexts that mirror persistent ACL xattrs.

Dependencies and integration points: assumes Gluster core types such as `xlator_t` and `inode_t` are available from including translation units. It is the local contract between ACL core logic and xattr codec.

Risks and test signals: because this header does not include the type definitions itself, include order matters. Callers must obey refcount ownership: returned ACLs from `posix_acl_get()` need unref, and ACLs passed into `posix_acl_set()` are retained by the context. Test signals include leak/refcount checks during lookup, setxattr, forget, and translator fini.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/system/posix-acl/src/posix-acl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-annotations/pom.xml -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-annotations/pom.xml

Purpose: Maven module descriptor for the Hadoop annotations jar containing audience/stability annotations and doclet filtering helpers.

Important APIs, types, and functions: declares parent `hadoop-project`, artifact `hadoop-annotations`, packaging `jar`, provided dependency on `io.github.zhtttylz:jdiff`, and a compiler-plugin override that uses `source`/`target` plus `--add-modules jdk.javadoc` and `--add-exports jdk.javadoc/jdk.javadoc.internal.tool=ALL-UNNAMED`.

Control flow: Maven compiles this module as a jar. The compiler override is necessary because the doclet bridge imports JDK internal javadoc classes and cannot use the parent `release` configuration.

State and persistence: no runtime state. Build output is the annotations jar consumed by other Hadoop modules.

Dependencies and integration points: integrates with the Hadoop parent build, JDiff doclet APIs, and JDK 17 javadoc internals used by `HadoopDocEnvImpl`.

Risks and test signals: JDK internal exports are brittle across JDK upgrades. Provided JDiff means runtime users of JDiff doclets need it available from the doc generation classpath. Test signals include `mvn -pl hadoop-common-project/hadoop-annotations compile` on the supported JDK and doclet execution under the docs profile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-annotations/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-annotations/src/main/java/org/apache/hadoop/classification/InterfaceAudience.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-annotations/src/main/java/org/apache/hadoop/classification/InterfaceAudience.java

Purpose: defines Hadoop API audience annotations that document whether program elements are public, limited-private to named projects, or private to Hadoop internals.

Important APIs, types, and functions: container class `InterfaceAudience` is annotated `@Public` and `@Evolving`. Nested runtime-retained documented annotations are `Public`, `LimitedPrivate` with `String[] value()`, and `Private`. The private constructor prevents instantiation.

Control flow: no executable flow beyond annotation metadata. Consumers attach nested annotations to packages, classes, methods, and fields; doclet filters inspect annotation mirrors by canonical name.

State and persistence: annotations are retained at runtime, so classification metadata persists in compiled class files and can be inspected reflectively or by javadoc/doclet tooling.

Dependencies and integration points: uses Java annotation APIs and integrates with Hadoop's public API policy, doclet filters, and downstream modules that mark API audience.

Risks and test signals: unannotated public classes are documented as private by policy, but enforcement relies on tooling. Test signals include annotation retention in compiled classes and doclet filtering behavior for Public, LimitedPrivate, Private, and unannotated classes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-annotations/src/main/java/org/apache/hadoop/classification/InterfaceAudience.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-annotations/src/main/java/org/apache/hadoop/classification/InterfaceStability.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-annotations/src/main/java/org/apache/hadoop/classification/InterfaceStability.java

Purpose: defines Hadoop API stability annotations that describe compatibility expectations across releases.

Important APIs, types, and functions: container class `InterfaceStability` is `@Public` and `@Evolving`. Nested runtime-retained documented annotations are `Stable`, `Evolving`, and `Unstable`.

Control flow: no runtime logic. Annotations are attached to program elements and consumed by documentation tooling, especially `HadoopDocEnvImpl` and `StabilityOptions`.

State and persistence: stability metadata persists in class files due to runtime retention.

Dependencies and integration points: imports `InterfaceAudience` annotations for its own documentation and classification. Integrates with doclet filters that exclude unstable/evolving APIs depending on `-stable`, `-evolving`, or `-unstable` options.

Risks and test signals: compatibility promises are only as accurate as annotations. Filtering correctness should be tested for each stability level and for private elements with explicit stability annotations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-annotations/src/main/java/org/apache/hadoop/classification/InterfaceStability.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-annotations/src/main/java/org/apache/hadoop/classification/VisibleForTesting.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-annotations/src/main/java/org/apache/hadoop/classification/VisibleForTesting.java

Purpose: marker annotation for program elements that are present or more visible specifically for Hadoop internal tests.

Important APIs, types, and functions: `@VisibleForTesting` targets types, methods, fields, and constructors; it is documented and retained in class files with `RetentionPolicy.CLASS`.

Control flow: no executable control flow. The annotation is informational and can be consumed by static analysis, review, or generated docs.

State and persistence: metadata is stored in compiled class files but not guaranteed to be available via runtime reflection because retention is `CLASS`.

Dependencies and integration points: depends only on Java annotation APIs. Used in modules such as Hadoop auth to expose test hooks like `KerberosAuthenticator.wrapExceptionWithMessage()` and `JWTRedirectAuthenticationHandler.constructLoginURL()`.

Risks and test signals: external consumers may be tempted to depend on testing-only APIs despite the documented private/unstable semantics. Test signal is compile-time availability to tests without broadening intended API stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-annotations/src/main/java/org/apache/hadoop/classification/VisibleForTesting.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-annotations/src/main/java/org/apache/hadoop/classification/tools/ExcludePrivateAnnotationsJDiffDoclet.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-annotations/src/main/java/org/apache/hadoop/classification/tools/ExcludePrivateAnnotationsJDiffDoclet.java

Purpose: legacy static-entry JDiff doclet wrapper that excludes Hadoop private and limited-private annotated elements before generating JDiff output.

Important APIs, types, and functions: `languageVersion()` returns `SourceVersion.RELEASE_17`; `start(DocletEnvironment)` delegates to `JDiff.start(RootDocProcessor.process(root))`; `optionLength()` recognizes stability options before forwarding to `JDiff.optionLength()`; `validOptions()` applies stability options, filters them out, then delegates validation to JDiff.

Control flow: javadoc/JDiff calls static doclet entry points. Stability options update `RootDocProcessor`; `RootDocProcessor.process()` wraps the environment with `HadoopDocEnvImpl`; JDiff sees the filtered environment.

State and persistence: static stability state lives in `StabilityOptions`/`RootDocProcessor` for the JVM invocation. No disk state is written by this wrapper itself.

Dependencies and integration points: depends on JDK doclet APIs and the `jdiff.JDiff` dependency. Integrates Hadoop annotation filtering into API-diff generation.

Risks and test signals: static mutable filtering state can leak across multiple doclet invocations in the same JVM. JDiff option compatibility depends on `filterOptions()` removing only Hadoop-specific flags. Test signals are JDiff generation with `-stable`, `-evolving`, and `-unstable`, plus exclusion of Private/LimitedPrivate classes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-annotations/src/main/java/org/apache/hadoop/classification/tools/ExcludePrivateAnnotationsJDiffDoclet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-annotations/src/main/java/org/apache/hadoop/classification/tools/ExcludePrivateAnnotationsStandardDoclet.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-annotations/src/main/java/org/apache/hadoop/classification/tools/ExcludePrivateAnnotationsStandardDoclet.java

Purpose: JDK 17 `Doclet` implementation that wraps `StandardDoclet` and excludes Hadoop Private/LimitedPrivate APIs, with stability option support.

Important APIs, types, and functions: static legacy methods mirror old doclet entry points: `languageVersion()`, `start()`, `optionLength()`, and `validOptions()`. Instance methods implement `Doclet`: `init()`, `getName()`, `getSupportedOptions()`, `getSupportedSourceVersion()`, and `run()`. `getSupportedOptions()` adds `-unstable` and `-evolving` options to the delegate's options.

Control flow: javadoc constructs the doclet, calls `init()`, reads supported options, processes stability flags, then `run()` applies `StabilityOptions` and should run the delegate on a filtered environment. The static `start()` path prints the doclet name and runs `StandardDoclet` directly when elements are present.

State and persistence: instance state holds delegate, reporter, and locale; global stability state lives in `StabilityOptions` and `RootDocProcessor`.

Dependencies and integration points: integrates with JDK `StandardDoclet`, Hadoop annotation filtering, and the compiler POM's `jdk.javadoc` export because filtering uses `HadoopDocEnvImpl`.

Risks and test signals: `run()` calls `RootDocProcessor.process(environment)` but ignores the returned filtered environment and passes the original `environment` to `delegate.run()`, which appears to bypass filtering in the instance doclet path. The custom options omit `-stable` despite `StabilityOptions` supporting it. Test signals should verify generated docs actually exclude Private/LimitedPrivate elements for both legacy static and JDK 17 instance entry points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-annotations/src/main/java/org/apache/hadoop/classification/tools/ExcludePrivateAnnotationsStandardDoclet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-annotations/src/main/java/org/apache/hadoop/classification/tools/HadoopDocEnvImpl.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-annotations/src/main/java/org/apache/hadoop/classification/tools/HadoopDocEnvImpl.java

Purpose: filtered `DocletEnvironment` implementation for Hadoop doclets. It subclasses JDK internal `DocEnvImpl` to remain compatible with doclets that expect that implementation while filtering elements by Hadoop audience and stability annotations.

Important APIs, types, and functions: constructor accepts the original environment, selected stability flag, and whether unannotated classes should be private. `extractToolEnvironment()` retrieves `DocEnvImpl.toolEnv` from the original environment. `exclude(Element)` evaluates `InterfaceAudience.Private`, `InterfaceAudience.LimitedPrivate`, `InterfaceAudience.Public`, `InterfaceStability.Unstable`, and `InterfaceStability.Evolving`. Overrides filter `getSpecifiedElements()`, `getIncludedElements()`, and `isIncluded()`, while delegating doc trees, element/type utils, file manager, source version, module mode, and file kind.

Control flow: doclet wrappers call `RootDocProcessor.process()`, which constructs this wrapper. Standard or JDiff doclets then ask for specified/included elements and receive filtered `LinkedHashSet` results preserving base order.

State and persistence: instance state is read-only after construction. No persistent data is written; filtering decisions are recomputed from annotation mirrors.

Dependencies and integration points: depends on `jdk.javadoc.internal.tool.DocEnvImpl` and `ToolEnvironment`, requiring explicit module exports. It integrates directly with Hadoop's annotation classes and JDK doclet APIs.

Risks and test signals: JDK internal inheritance is fragile across Java releases. Filtering only checks annotations present directly on each element, so inherited/package-level classification may not affect all elements unless javadoc includes those annotations on the element. Test signals are doc generation on the supported JDK, filtering by audience and each stability level, and failure behavior when the original environment is not `DocEnvImpl`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-annotations/src/main/java/org/apache/hadoop/classification/tools/HadoopDocEnvImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-annotations/src/main/java/org/apache/hadoop/classification/tools/IncludePublicAnnotationsJDiffDoclet.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-annotations/src/main/java/org/apache/hadoop/classification/tools/IncludePublicAnnotationsJDiffDoclet.java

Purpose: JDiff doclet wrapper that includes only public Hadoop API elements and excludes private, limited-private, and unannotated class-level elements.

Important APIs, types, and functions: implements `Doclet` with a `JDiff` delegate and supports custom `-unstable` and `-evolving` options. `run()` and static `start()` set `RootDocProcessor.setTreatUnannotatedClassesAsPrivate(true)` before delegating to JDiff on a processed environment. Static compatibility methods provide `languageVersion()`, `optionLength()`, and `validOptions()`.

Control flow: custom options update `StabilityOptions`; `run()` applies stability to `RootDocProcessor`, enables unannotated-class exclusion, wraps the environment, and runs JDiff. The static path follows the same public-only filtering intent.

State and persistence: delegate, reporter, and locale are per instance; filtering mode and stability are static global state in helper classes for the doclet invocation.

Dependencies and integration points: depends on JDiff, JDK doclet APIs, `RootDocProcessor`, and `HadoopDocEnvImpl`. Used for API diff documentation that should reflect public Hadoop APIs only.

Risks and test signals: supports `-unstable` and `-evolving` in the instance option set but not `-stable`, despite static optionLength recognizing it. Static mutable state can affect sequential doclet runs. Test signals include JDiff output containing `@Public` APIs, excluding unannotated classes, and stability filtering with each flag.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-annotations/src/main/java/org/apache/hadoop/classification/tools/IncludePublicAnnotationsJDiffDoclet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-annotations/src/main/java/org/apache/hadoop/classification/tools/IncludePublicAnnotationsStandardDoclet.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-annotations/src/main/java/org/apache/hadoop/classification/tools/IncludePublicAnnotationsStandardDoclet.java

Purpose: Standard Javadoc doclet wrapper that should document only Hadoop `@InterfaceAudience.Public` API elements, excluding private, limited-private, and unannotated class-level elements.

Important APIs, types, and functions: implements `Doclet` around a `StandardDoclet` delegate. `getSupportedOptions()` adds `-unstable` and `-evolving`; `run()` enables unannotated-class exclusion, applies stability, processes the environment, and delegates to the standard doclet with the filtered environment. Static `start()`, `optionLength()`, and `validOptions()` support legacy-style entry points.

Control flow: javadoc calls `init()`, option processing updates `StabilityOptions`, then `run()` wraps the environment through `RootDocProcessor.process(env)` and invokes `delegate.run(filtered)`.

State and persistence: per-instance state is the delegate. Global filtering state is stored in `RootDocProcessor` and `StabilityOptions`.

Dependencies and integration points: depends on JDK `StandardDoclet`, Hadoop annotation filtering, and JDK 17 doclet APIs.

Risks and test signals: the `-evolving` option handler sets `StabilityOptions.Level.UNSTABLE` instead of `EVOLVING`, which likely makes `-evolving` too permissive. Like other wrappers, the instance option set omits `-stable`. Test signals should assert option behavior and generated docs under `-unstable`, `-evolving`, and `-stable`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-annotations/src/main/java/org/apache/hadoop/classification/tools/IncludePublicAnnotationsStandardDoclet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-annotations/src/main/java/org/apache/hadoop/classification/tools/RootDocProcessor.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-annotations/src/main/java/org/apache/hadoop/classification/tools/RootDocProcessor.java

Purpose: shared static coordinator for Hadoop doclet filtering. It stores selected stability and whether unannotated classes should be treated as private, then wraps a `DocletEnvironment`.

Important APIs, types, and functions: static setters/getters are `setStability()`, `getStability()`, `setTreatUnannotatedClassesAsPrivate()`, and `isTreatUnannotatedClassesAsPrivate()`. `process(DocletEnvironment)` returns a new `HadoopDocEnvImpl`.

Control flow: doclet wrappers set stability and public-only mode, then call `process()` before delegating to StandardDoclet or JDiff.

State and persistence: all configuration is static process state, initialized to `-unstable` and `false` for unannotated private handling. No disk persistence.

Dependencies and integration points: depends on JDK doclet environment and `HadoopDocEnvImpl`. It is the bridge between option parsing in `StabilityOptions` and actual environment filtering.

Risks and test signals: static state can leak between doclet invocations in the same JVM. Test signals should reset or isolate invocations and verify default unstable behavior plus public-only toggling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-annotations/src/main/java/org/apache/hadoop/classification/tools/RootDocProcessor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-annotations/src/main/java/org/apache/hadoop/classification/tools/StabilityOptions.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-annotations/src/main/java/org/apache/hadoop/classification/tools/StabilityOptions.java

Purpose: option parsing and normalization helper for Hadoop doclets' API stability filters.

Important APIs, types, and functions: constants are `-stable`, `-evolving`, and `-unstable`. `Level` orders `STABLE`, `EVOLVING`, and `UNSTABLE`; `level` is a volatile static defaulting to `UNSTABLE`. `optionLength()` identifies supported options. `setFromOptionName()` promotes the current level to the least restrictive requested level. `applyToRootProcessor()` maps the selected level to `RootDocProcessor.setStability()`. `validOptions()` scans doclet option arrays, and `filterOptions()` removes Hadoop stability flags before passing options to delegate doclets.

Control flow: doclet wrappers call `validOptions()` or custom `Option.process()` during option parsing, then call `applyToRootProcessor()` before processing the doclet environment.

State and persistence: global JVM state is `level`; there is no persistence. The volatile field provides visibility but not full reset semantics between independent doclet runs.

Dependencies and integration points: depends on `Reporter` and Java collections. Integrates with `RootDocProcessor`, JDiff wrappers, and StandardDoclet wrappers.

Risks and test signals: because `setFromOptionName()` only updates when `next.ordinal() > level.ordinal()` and the default is already `UNSTABLE`, command-line `-stable` or `-evolving` cannot make the filter stricter through that path unless `level` was reset lower first. This is a likely semantic bug. Test signals should cover all option combinations and sequential invocations in one JVM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-annotations/src/main/java/org/apache/hadoop/classification/tools/StabilityOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-annotations/src/main/java/org/apache/hadoop/classification/tools/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-annotations/src/main/java/org/apache/hadoop/classification/tools/package-info.java

Purpose: package-level audience annotation for Hadoop classification doclet tools.

Important APIs, types, and functions: annotates `org.apache.hadoop.classification.tools` with `@InterfaceAudience.LimitedPrivate` for Hadoop-related projects including Common, Avro, Chukwa, HBase, HDFS, Hive, MapReduce, Pig, and ZooKeeper.

Control flow: no runtime control flow. The package annotation supplies metadata to documentation and API policy tooling.

State and persistence: package annotation metadata persists in compiled package metadata according to annotation retention.

Dependencies and integration points: imports `InterfaceAudience`; integrates the tools package with Hadoop's API audience classification.

Risks and test signals: package-level classification may not be considered by element-level filtering code that only inspects direct annotation mirrors. Test signals include generated documentation for the package and downstream use by allowed Hadoop-related projects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-annotations/src/main/java/org/apache/hadoop/classification/tools/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth-examples/pom.xml -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth-examples/pom.xml

Purpose: Maven WAR module for Hadoop Auth example web application and client.

Important APIs, types, and functions: artifact `hadoop-auth-examples` packages as `war`; dependencies include servlet API provided by the container, `hadoop-auth`, SLF4J, reload4j, and slf4j-reload4j. Build plugins set the WAR name, skip deploy, and configure `exec-maven-plugin` to run `WhoClient` with `${url}`.

Control flow: Maven builds a WAR containing `WhoServlet`, `RequestLoggerFilter`, and `web.xml`; the exec plugin can run the example client against a supplied URL.

State and persistence: no application state in the POM. Build output is `hadoop-auth-examples.war`.

Dependencies and integration points: integrates with the parent Hadoop build, servlet container deployment, Hadoop auth filter library, and logging runtime.

Risks and test signals: examples use older web.xml/servlet configuration while the dependency is marked Jakarta in Maven but imports in sources are `javax.servlet`, so dependency alignment should be verified through compilation. Test signals include WAR packaging and running the exec goal against the deployed sample endpoints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth-examples/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth-examples/src/main/java/org/apache/hadoop/security/authentication/examples/RequestLoggerFilter.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth-examples/src/main/java/org/apache/hadoop/security/authentication/examples/RequestLoggerFilter.java

Purpose: servlet filter for the Hadoop Auth examples that logs HTTP request and response status/headers when debug logging is enabled.

Important APIs, types, and functions: implements `Filter` with no-op `init()`/`destroy()` and debug-aware `doFilter()`. `XHttpServletRequest.getResquestInfo()` formats method, URL, query string, and request headers. `XHttpServletResponse` wraps response mutation methods to track status, message, cookies, and headers, then `getResponseInfo()` formats them after the chain returns.

Control flow: when debug is disabled, the filter delegates directly. When enabled, it wraps request/response, logs request data, invokes the chain, and logs response data in a `finally` block.

State and persistence: per-request wrapper state stores captured headers/status in memory. No persistent state.

Dependencies and integration points: depends on servlet APIs and SLF4J. Registered first in the example `web.xml` so it observes traffic before auth filters and servlet handling.

Risks and test signals: debug logs may expose authentication headers or cookies. Header capture is incomplete for response APIs not overridden. `getResquestInfo` has a misspelled method name but is internal. Test signals are example deployment with debug logging, response header/status capture for success and error paths, and no wrapping overhead when debug is off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth-examples/src/main/java/org/apache/hadoop/security/authentication/examples/RequestLoggerFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth-examples/src/main/java/org/apache/hadoop/security/authentication/examples/WhoClient.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth-examples/src/main/java/org/apache/hadoop/security/authentication/examples/WhoClient.java

Purpose: command-line example client that uses `AuthenticatedURL` to call a Hadoop Auth-protected endpoint and print the token, status, and body.

Important APIs, types, and functions: `main(String[] args)` validates one URL argument, creates `AuthenticatedURL.Token`, opens an authenticated connection through `new AuthenticatedURL().openConnection(url, token)`, prints token and HTTP status, and streams response lines on HTTP 200.

Control flow: execution is linear; authentication happens inside `AuthenticatedURL`, then the code reads only successful responses. Exceptions print an error and exit nonzero.

State and persistence: token state lives in memory for this single process invocation. No token is persisted.

Dependencies and integration points: depends on Hadoop auth client classes, `HttpURLConnection`, URL parsing, and UTF-8 input reading. Configured as the exec plugin main class in the examples POM.

Risks and test signals: prints the auth token to stdout, which is acceptable for an example but not safe for real clients. It does not URL-encode or retry itself. Test signal is running it against `/anonymous/who`, `/simple/who`, and `/kerberos/who` endpoints in the example WAR.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth-examples/src/main/java/org/apache/hadoop/security/authentication/examples/WhoClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth-examples/src/main/java/org/apache/hadoop/security/authentication/examples/WhoServlet.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth-examples/src/main/java/org/apache/hadoop/security/authentication/examples/WhoServlet.java

Purpose: sample servlet that reports the authenticated remote user and principal placed on the request by Hadoop Auth.

Important APIs, types, and functions: `doGet()` sets `text/plain`, status 200, reads `req.getRemoteUser()` and `req.getUserPrincipal().getName()`, and writes a formatted line. `doPost()` delegates to `doGet()`.

Control flow: servlet endpoints are reached after the configured auth filter chain. The response reflects authentication state from the request wrapper installed by `AuthenticationFilter`.

State and persistence: stateless servlet; no persistent data.

Dependencies and integration points: depends on servlet APIs and is mapped to anonymous, simple, and kerberos example URL prefixes in `web.xml`.

Risks and test signals: exposes identity information for demonstration only. Test signals are endpoint responses showing null or authenticated user/principal values depending on the configured auth filter and token state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth-examples/src/main/java/org/apache/hadoop/security/authentication/examples/WhoServlet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth-examples/src/main/webapp/WEB-INF/web.xml -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth-examples/src/main/webapp/WEB-INF/web.xml

Purpose: deployment descriptor for the Hadoop Auth example web application.

Important APIs, types, and functions: declares `WhoServlet` and maps it to `/anonymous/who`, `/simple/who`, and `/kerberos/who`. Declares `RequestLoggerFilter` plus three `AuthenticationFilter` instances: anonymous simple auth, non-anonymous simple auth, and Kerberos auth. Init params configure auth type, anonymous allowance, token validity, Kerberos principal, and keytab.

Control flow: all requests pass through `requestLoggerFilter`; `/anonymous/*`, `/simple/*`, and `/kerberos/*` then pass through their respective auth filters before reaching the servlet.

State and persistence: no persistent application state. Auth filters issue signed cookies according to their configured token validity.

Dependencies and integration points: integrates servlet container deployment with Hadoop auth server filter and the example servlet/filter classes.

Risks and test signals: Kerberos principal/keytab are hard-coded sample values and must be changed for real deployment. Token validity is short at 30 seconds for examples. Test signals are successful deployment and distinct behavior across anonymous, simple, and Kerberos paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth-examples/src/main/webapp/WEB-INF/web.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/dev-support/findbugsExcludeFile.xml -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/dev-support/findbugsExcludeFile.xml

Purpose: SpotBugs/FindBugs exclusion file for intentional representation-exposure warnings in Hadoop Auth secret provider classes.

Important APIs, types, and functions: excludes `EI_EXPOSE_REP` for `getAllSecrets()` and `getCurrentSecret()` on `RolloverSignerSecretProvider`, `StringSignerSecretProvider`, and `FileSignerSecretProvider`.

Control flow: the SpotBugs Maven plugin reads this filter and suppresses matching findings during analysis.

State and persistence: no runtime state. Static-analysis configuration persists in the build tree.

Dependencies and integration points: referenced by `hadoop-auth/pom.xml` in `spotbugs-maven-plugin` alongside the global Hadoop exclude file.

Risks and test signals: suppressing exposed-representation findings assumes callers will not mutate returned byte arrays/secrets; that is a security-sensitive contract. Test signals include SpotBugs runs that suppress only these known patterns while continuing to report other findings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/dev-support/findbugsExcludeFile.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/pom.xml -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/pom.xml

Purpose: Maven module descriptor for Hadoop Auth, the HTTP authentication library providing client authenticators, server filters, handlers, signed cookies, JWT redirect support, and tests.

Important APIs, types, and functions: artifact `hadoop-auth` packages as a jar. Dependencies include Hadoop annotations, servlet API, SLF4J/logging, commons-codec, HttpClient, Nimbus JOSE JWT, ZooKeeper/Curator, Kerby, shaded Guava, Snappy provided, and extensive test dependencies including Jetty, MiniKDC, ApacheDS, Mockito, AssertJ, and JUnit 5. Build plugins attach source/test jars and configure SpotBugs excludes. A `docs` profile runs javadoc.

Control flow: Maven compiles the library, packages jar/source/test-jar during `prepare-package`, applies SpotBugs filters, and optionally generates docs.

State and persistence: no runtime state in the POM. Build outputs include the main jar, source jar, and test jar.

Dependencies and integration points: central module used by Hadoop services and the example WAR. It integrates with Kerberos, LDAP tests, JWT libraries, ZooKeeper-backed signer secrets, servlet containers, and Hadoop annotations.

Risks and test signals: broad security dependencies require compatibility and CVE management. Provided servlet and snappy scopes mean runtime containers must supply compatible APIs. Test signals are module test suite execution, MiniKDC/SPNEGO tests, JWT validation tests, SpotBugs with local/global excludes, and docs profile generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/client/AuthenticatedURL.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/client/AuthenticatedURL.java

Purpose: client-side helper for using `HttpURLConnection` with servers protected by Hadoop `AuthenticationFilter`. It manages the `hadoop.auth` cookie token and delegates initial authentication to an `Authenticator`.

Important APIs, types, and functions: constant `AUTH_COOKIE` is `hadoop.auth`. Nested `AuthCookieHandler` stores and emits the authentication cookie, parses `Set-Cookie`, shortens max-age to 90%, quotes v0 cookie values, and removes expired/empty cookies. Nested `Token` wraps the cookie handler, provides `isSet()`, package-private `set()`, `openConnection()`, and `toString()`. Static default authenticator is `KerberosAuthenticator`. Public APIs include constructors, `setDefaultAuthenticator()`, `getDefaultAuthenticator()`, `openConnection(URL, Token)`, `injectToken()`, and `extractToken()`.

Control flow: `openConnection()` validates HTTP(S) URL and token, calls `authenticator.authenticate(url, token)`, then opens the actual connection through the token's cookie handler. `Token.openConnection()` temporarily installs a global `CookieHandler` under a class lock to let `URL.openConnection()` attach cookies, then restores the previous handler. `extractToken()` treats 200/201/202 as success, 404 as `FileNotFoundException`, and other statuses as authentication failures while clearing the token.

State and persistence: token/cookie state is in memory inside `Token`; no disk persistence. `DEFAULT_AUTHENTICATOR` is static global mutable process state. The temporary global `CookieHandler` swap is synchronized but still a sensitive integration point.

Dependencies and integration points: depends on Hadoop auth server constants, `Authenticator` implementations, `HttpURLConnection`, Java `CookieHandler`/`HttpCookie`, and optional `ConnectionConfigurator` for TLS/timeouts/proxies. Tested by `TestAuthenticatedURL`.

Risks and test signals: instances are documented non-thread-safe. Global default authenticator changes affect all future default instances. Cookie parsing ignores malformed headers and token string printing can reveal credentials. Test signals include cookie extraction/injection, expiry behavior, 404/error handling, configurator invocation, and Kerberos/Pseudo authenticator integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/client/AuthenticatedURL.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/client/AuthenticationException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/client/AuthenticationException.java

Purpose: checked exception representing authentication failures in Hadoop Auth client and server authentication flows.

Important APIs, types, and functions: extends `Exception`, declares `serialVersionUID = 0`, and provides constructors for cause, message, and message plus cause.

Control flow: thrown by authenticators, server handlers, token parsing, and filter logic; callers handle it separately from transport `IOException`.

State and persistence: exception state is the normal Java message/cause chain. No persistent state.

Dependencies and integration points: used throughout client and server packages as the common authentication error type.

Risks and test signals: messages may be propagated to HTTP error reasons by `AuthenticationFilter`, so sensitive details should be avoided. Test signals are exception wrapping paths in Kerberos/Pseudo/filter tests and cause preservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/client/AuthenticationException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/client/Authenticator.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/client/Authenticator.java

Purpose: client-side authentication mechanism contract for `AuthenticatedURL`.

Important APIs, types, and functions: declares `setConnectionConfigurator(ConnectionConfigurator)` and `authenticate(URL, AuthenticatedURL.Token)`.

Control flow: `AuthenticatedURL.openConnection()` calls `authenticate()` before opening the caller's connection. Implementations may no-op when the token is already set, perform SPNEGO, pseudo auth, or custom flows, and update the token on success.

State and persistence: interface has no state. Implementations are documented as use-once and need not be thread-safe.

Dependencies and integration points: implemented by `KerberosAuthenticator` and `PseudoAuthenticator`, and extensible for custom client auth. It integrates with URL connections and the token cookie abstraction.

Risks and test signals: implementations must consistently use the supplied `ConnectionConfigurator`; otherwise TLS/proxy settings may be lost. Test signals are custom authenticator injection and configured connection behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/client/Authenticator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/client/ConnectionConfigurator.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/client/ConnectionConfigurator.java

Purpose: callback interface for configuring `HttpURLConnection` objects created by Hadoop Auth clients.

Important APIs, types, and functions: single method `configure(HttpURLConnection conn)` returns the configured connection and may throw `IOException`.

Control flow: `AuthenticatedURL.Token.openConnection()` opens a connection, then invokes the configurator if present. Authenticators pass the same configurator to their internal authentication requests.

State and persistence: no state in the interface. Implementations may carry timeout, SSL, proxy, or header configuration.

Dependencies and integration points: integrates `AuthenticatedURL`, `KerberosAuthenticator`, and `PseudoAuthenticator` with caller-specific HTTP setup.

Risks and test signals: configurators must be idempotent and safe for both authentication OPTIONS requests and final application requests. Test signals include timeout/SSL configurator invocation in client tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/client/ConnectionConfigurator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/client/KerberosAuthenticator.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/client/KerberosAuthenticator.java

Purpose: client-side Kerberos SPNEGO authenticator for Hadoop Auth. It uses the current subject or OS ticket cache and falls back to pseudo authentication when the endpoint does not start a SPNEGO negotiation.

Important APIs, types, and functions: constants mirror HTTP auth headers and `Negotiate`; auth probe method is `OPTIONS`. Nested `KerberosConfiguration` builds JAAS entries for OS login and Kerberos ticket cache, with IBM Java and `KRB5CCNAME` handling. Public methods include `setConnectionConfigurator()` and `authenticate()`. Helpers include `wrapExceptionWithMessage()`, `getFallBackAuthenticator()`, `isTokenKerberos()`, `isNegotiate()`, `doSpnegoSequence()`, `sendToken()`, and `readToken()`.

Control flow: if the token is unset, `authenticate()` opens an OPTIONS request. A 200 response with a Kerberos token is accepted; a 401 with `WWW-Authenticate: Negotiate` triggers manual GSSAPI token exchange in `doSpnegoSequence()`; otherwise it instantiates and runs `PseudoAuthenticator`. The SPNEGO sequence obtains or logs into a subject, creates a GSS context for `HTTP/<host>`, loops sending and reading base64 negotiation tokens until established, then the cookie handler captures the server token.

State and persistence: instance state stores current URL, Base64 codec, and configurator for a single authentication flow. Kerberos credentials come from the current subject or ticket cache; no credentials are persisted by this class. Token state is stored in `AuthenticatedURL.Token`.

Dependencies and integration points: depends on GSSAPI, JAAS, Hadoop `KerberosUtil`/`SubjectUtil`, `AuthToken`, commons-codec Base64, HTTP constants, and fallback pseudo auth. Covered by `TestKerberosAuthenticator`.

Risks and test signals: fallback to pseudo auth may be insecure if a service was expected to require Kerberos. `readToken()` assumes `Negotiate ` with a token after the prefix and can fail on bare `Negotiate`. Exception wrapping uses reflection and may fail for exception classes without a string constructor. Test signals include MiniKDC SPNEGO success, fallback behavior, existing token no-op, configurator propagation, and invalid negotiation headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/client/KerberosAuthenticator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/client/PseudoAuthenticator.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/client/PseudoAuthenticator.java

Purpose: client-side Hadoop simple/pseudo authenticator that sends the local Java `user.name` as a query parameter.

Important APIs, types, and functions: constant `USER_NAME` is `user.name`. `setConnectionConfigurator()` stores optional connection setup. `authenticate()` appends `user.name=<getUserName()>` to the URL, sends an OPTIONS request, and calls `AuthenticatedURL.extractToken()`. `getUserName()` returns `System.getProperty("user.name")` and can be overridden.

Control flow: every call constructs a URL with the username parameter, opens a configured connection through the token, connects, and extracts the issued auth cookie.

State and persistence: only stores the optional configurator. Token state remains in `AuthenticatedURL.Token`.

Dependencies and integration points: integrates with server-side `PseudoAuthenticationHandler`, `AuthenticatedURL`, and `ConnectionConfigurator`. Covered by `TestPseudoAuthenticator`.

Risks and test signals: username is appended without URL encoding, so unusual usernames can break the query string. It trusts a local system property and is not strong authentication. Test signals include URLs with and without existing query strings, overridden usernames, configurator propagation, and error response handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/client/PseudoAuthenticator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/server/AltKerberosAuthenticationHandler.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/server/AltKerberosAuthenticationHandler.java

Purpose: abstract server-side handler that uses Kerberos for non-browser clients and delegates browser authentication to a subclass-defined alternate mechanism.

Important APIs, types, and functions: type constant is `alt-kerberos`. Config property `alt-kerberos.non-browser.user-agents` defaults to `java,curl,wget,perl`. Overrides `getType()`, `init()`, and `authenticate()`. Provides `isBrowser(String userAgent)` and abstract `alternateAuthenticate()`.

Control flow: initialization loads the comma-separated non-browser user-agent fragments. On authenticate, requests with browser-like user agents are sent to `alternateAuthenticate()`; non-browser clients use `KerberosAuthenticationHandler.authenticate()`.

State and persistence: stores lower-cased non-browser user-agent patterns in memory. Kerberos state is managed by the superclass.

Dependencies and integration points: extends `KerberosAuthenticationHandler` and is the base for `JWTRedirectAuthenticationHandler`. Covered by `TestAltKerberosAuthenticationHandler`.

Risks and test signals: user-agent classification is heuristic and spoofable. Null user-agent is treated as non-browser and gets Kerberos. Test signals include default and custom non-browser lists, browser alternate flow, and Kerberos fallback for CLI agents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/server/AltKerberosAuthenticationHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/server/AuthenticationFilter.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/server/AuthenticationFilter.java

Purpose: servlet filter that protects web resources using a pluggable `AuthenticationHandler` and signed `hadoop.auth` cookies.

Important APIs, types, and functions: configuration constants include `config.prefix`, `type`, `signature.secret`, `signature.secret.file`, `token.max-inactive-interval`, `token.validity`, `cookie.domain`, `cookie.path`, `cookie.persistent`, `signer.secret.provider`, and `signer.secret.provider.object`. Lifecycle methods are `init()` and `destroy()`. Extension hooks include `initializeAuthHandler()`, `initializeSecretProvider()`, `constructSecretProvider()`, `getConfiguration()`, `getAuthenticationHandler()`, `doFilter(FilterChain, ...)`, and `createAuthCookie()`. Auth logic is in `getToken()`, `verifyTokenType()`, and servlet `doFilter()`.

Control flow: `init()` extracts prefixed config, resolves handler class via `AuthenticationHandlerUtil`, sets token validity/inactivity, constructs a signer secret provider, initializes the auth handler, and stores cookie settings. `doFilter()` tries to parse and verify an incoming signed cookie; if absent or invalid, it lets the handler run management operations and authenticate. Successful tokens wrap the request to expose auth type, remote user, and principal, then optionally issue or refresh a signed cookie before delegating. Unauthorized paths clear the auth cookie and return 401 or 403 depending on whether a WWW-Authenticate challenge was produced.

State and persistence: per-filter state includes config, signer, secret provider, auth handler, validity settings, cookie settings, and whether to destroy the provider. Persistent security state is the signed auth cookie in clients. Secret provider state may be file-, random-, ZooKeeper-, servlet-context-, or custom-provider-backed.

Dependencies and integration points: depends on servlet API, Hadoop Auth client constants, Kerberos header constants, `Signer`, `SignerSecretProvider` implementations, and pluggable server handlers. Covered by `TestAuthenticationFilter` and also used by the Hadoop auth examples.

Risks and test signals: random-secret fallback means tokens are invalidated on restart and may hide missing secret-file configuration unless fallback is disallowed in direct provider construction. Cookie construction is manual and must maintain quoting, `HttpOnly`, secure-on-HTTPS, domain/path, and expiry behavior. Error messages may expose authentication exception text. Test signals include signed cookie validation, expired/max-inactive tokens, token type mismatch including composite handlers, management operations, secret provider selection/fallback, cookie clearing, secure flag behavior, and request wrapper identity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/server/AuthenticationFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/server/AuthenticationHandler.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/server/AuthenticationHandler.java

Purpose: server-side authentication mechanism contract used by `AuthenticationFilter`.

Important APIs, types, and functions: constant `WWW_AUTHENTICATE` aliases the HTTP challenge header. Methods are `getType()`, `init(Properties)`, `destroy()`, `managementOperation(AuthenticationToken, HttpServletRequest, HttpServletResponse)`, and `authenticate(HttpServletRequest, HttpServletResponse)`.

Control flow: `AuthenticationFilter` initializes one handler instance, calls `managementOperation()` for each request, and when needed calls `authenticate()` to obtain an `AuthenticationToken` or let the handler take over the response.

State and persistence: interface has no state, but implementations must be thread-safe because one instance services all requests.

Dependencies and integration points: implemented by pseudo, Kerberos, LDAP, multi-scheme, and JWT/alternate handlers. Integrates servlet requests/responses with Hadoop's token/cookie model.

Risks and test signals: implementations returning tokens before a multi-step auth sequence is complete would create invalid trust. Test signals are handler lifecycle, thread-safety, management operation short-circuiting, and null-token challenge flows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/server/AuthenticationHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/server/AuthenticationHandlerUtil.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/server/AuthenticationHandlerUtil.java

Purpose: static helper for resolving authentication handler names and validating/matching HTTP authentication schemes.

Important APIs, types, and functions: `getAuthenticationHandlerClassName()` maps short names for pseudo, kerberos, LDAP, and multi-scheme handlers to class names, otherwise returns the input. `checkAuthScheme()` canonicalizes Basic, Negotiate, and Digest or throws. `matchAuthScheme()` case-insensitively checks whether an auth header begins with a scheme.

Control flow: `AuthenticationFilter` uses class-name resolution during init. Multi-scheme or handler code can use scheme validation and matching for Authorization headers.

State and persistence: no state; constructor is private.

Dependencies and integration points: depends on `HttpConstants` and handler type constants. Supports pluggability by letting fully qualified class names pass through.

Risks and test signals: `matchAuthScheme()` only checks prefix length, so a header like `BasicXYZ` can match `Basic` even without a delimiter. Null inputs throw `NullPointerException`. Test signals include short-name resolution, custom class pass-through, valid/invalid schemes, and delimiter-sensitive auth matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/server/AuthenticationHandlerUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/server/AuthenticationToken.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/server/AuthenticationToken.java

Purpose: server-side authenticated principal token used by `AuthenticationFilter` and exposed as the servlet request principal.

Important APIs, types, and functions: extends `AuthToken`, defines singleton `ANONYMOUS`, constructors from user/principal/type and from parsed `AuthToken`, overrides `setMaxInactives()` and `setExpires()` to ignore changes to `ANONYMOUS`, exposes `isExpired()`, and static `parse(String)`.

Control flow: authentication handlers create tokens; the filter sets expiry/inactivity, signs serialized token strings into cookies, parses tokens from cookies, and wraps requests so `getUserPrincipal()` returns the token.

State and persistence: token fields are inherited from `AuthToken` and serialized into signed cookies. `ANONYMOUS` is static and intentionally immutable for expiry updates.

Dependencies and integration points: depends on `AuthToken`, `AuthenticationException`, and servlet principal expectations. Covered by `TestAuthenticationToken`.

Risks and test signals: token trust depends on outer signature verification, not the serialized string alone. Anonymous token must not accidentally become persistent or mutable. Test signals include parse/serialize round trips, expiry/max-inactive behavior, and anonymous immutability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/server/AuthenticationToken.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/server/CompositeAuthenticationHandler.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/server/CompositeAuthenticationHandler.java

Purpose: extension interface for authentication handlers that can issue or accept more than one token type.

Important APIs, types, and functions: extends `AuthenticationHandler` and adds `Collection<String> getTokenTypes()`.

Control flow: `AuthenticationFilter.verifyTokenType()` checks this interface and accepts cookies whose token type matches any returned type instead of only `handler.getType()`.

State and persistence: interface has no state. Implementations define supported token type collections.

Dependencies and integration points: used by multi-scheme handlers and the filter's token validation logic.

Risks and test signals: returned collections must include every token type an implementation may issue, or valid cookies will be rejected. Test signals include filter token verification for composite vs single-type handlers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/server/CompositeAuthenticationHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/server/HttpConstants.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/server/HttpConstants.java

Purpose: central constants for HTTP authentication header names and scheme strings used across Hadoop Auth client and server code.

Important APIs, types, and functions: defines `WWW_AUTHENTICATE_HEADER`, `AUTHORIZATION_HEADER`, `NEGOTIATE`, `BASIC`, and `DIGEST`; private constructor prevents instantiation.

Control flow: no runtime logic. Constants are referenced by Kerberos client/server handlers and scheme utility methods.

State and persistence: no state.

Dependencies and integration points: integrates SPNEGO, Basic, and Digest handling across client authenticators and server handlers.

Risks and test signals: typos would break protocol interoperability. Test signals are SPNEGO client/server tests and scheme utility tests that use these constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/server/HttpConstants.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/server/JWTRedirectAuthenticationHandler.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/server/JWTRedirectAuthenticationHandler.java

Purpose: browser-oriented alternate Kerberos handler that redirects unauthenticated UI users to a WebSSO provider, validates an RS256 JWT returned in a cookie, and issues a Hadoop `AuthenticationToken`.

Important APIs, types, and functions: config properties are `authentication.provider.url`, `public.key.pem`, `expected.jwt.audiences`, and `jwt.cookie.name`. State includes auth provider URL, RSA public key, accepted audiences, and cookie name. Public/test APIs include `setPublicKey()`, `init()`, `alternateAuthenticate()`, `getJWTFromCookie()`, and `constructLoginURL()`. Validation helpers are `validateToken()`, `validateSignature()`, `validateAudiences()`, and `validateExpiration()`.

Control flow: initialization requires an auth provider URL and RSA public key, parses optional audience and cookie settings, and delegates base Kerberos setup to `AltKerberosAuthenticationHandler`. Browser requests without a JWT cookie are redirected to the provider with `originalUrl=<current URL plus query>`. Requests with a JWT parse it, validate signature/audience/expiration, extract subject as username, and return an `AuthenticationToken`; invalid tokens trigger a new redirect.

State and persistence: handler stores validation configuration in memory. JWTs persist client-side in the configured cookie. Hadoop auth tokens are then signed and persisted by `AuthenticationFilter` in the normal `hadoop.auth` cookie.

Dependencies and integration points: extends `AltKerberosAuthenticationHandler`; depends on Nimbus JOSE JWT, RSA public keys from `CertificateUtil`, servlet redirects/cookies, and Hadoop auth tokens. Covered by `TestJWTRedirectAuthenticationHandler`.

Risks and test signals: `constructLoginURL()` concatenates the original URL and query without URL encoding, which can break redirects or allow parameter confusion. If expected audiences are unset, any audience is accepted. Expiration treats missing expiration as valid. Logs include usernames and serialized invalid JWTs. Test signals include redirect construction, cookie extraction, signature failure/success, audience matching, expiration handling, custom cookie names, and non-browser Kerberos fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/server/JWTRedirectAuthenticationHandler.java -->
