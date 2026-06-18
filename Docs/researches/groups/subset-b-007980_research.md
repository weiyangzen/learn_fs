# subset-b-007980 research

Grouped worker report for subset-b-007980. Each section preserves the source path in its title and is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdZip/XrdZipUtils.hh -->
# sources/distributed-fs/xrootd/src/XrdZip/XrdZipUtils.hh

Purpose: Defines common XrdZip utility types and byte-conversion helpers used by ZIP record classes. The file centralizes little-endian serialization/deserialization, an overflow sentinel template, a ZIP buffer alias, and DOS timestamp construction.

Important APIs/types/functions: `XrdZip::bad_data` is a marker exception for corrupted ZIP input. `ovrflw<UINT>::value` returns the all-ones unsigned sentinel used where ZIP32 fields overflow into ZIP64. `buffer_t` is `std::vector<char>`. `copy_bytes`, `from_buffer`, and `to` move integer values to and from raw buffers, applying `bswap` on `Xrd_Big_Endian`. `dos_timestmp` stores packed DOS `time` and `date` fields and builds them from current time or a supplied `time_t`.

Control flow: Serialization helpers reinterpret integer storage as bytes, reverse on big-endian hosts, and append/read fixed-width fields. Timestamp constructors call `std::localtime`, mask calendar fields, and shift them into ZIP DOS bit positions.

State and persistence behavior: No persistent state is owned. The helpers mutate caller-provided buffers or pointer cursors. `dos_timestmp` stores two 16-bit packed values intended to be persisted inside ZIP metadata.

Dependencies and integration points: Depends on `XrdSysPlatform.hh` for platform endian definitions and `bswap`. ZIP headers such as EOCD, ZIP64 EOCD, and locator structures use these functions to remain endian-correct.

Risks: The deserialization helpers assume the source buffer is large enough and correctly aligned for `memcpy` length; callers must validate sizes. `std::localtime` returns local calendar time and may be thread-hostile on some platforms. Month packing uses `tm_mon` directly, which is zero-based in C but DOS dates are normally one-based, so timestamp consumers should verify expectations.

Test signals: Useful tests are endian round trips for all integer widths, malformed short-buffer handling at callers, and fixed `time_t` conversion cases around month/year boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdZip/XrdZipUtils.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdZip/XrdZipZIP64EOCD.hh -->
# sources/distributed-fs/xrootd/src/XrdZip/XrdZipZIP64EOCD.hh

Purpose: Models the ZIP64 End of Central Directory record. It supports parsing from a raw central-directory trailer and constructing/serializing a new ZIP64 EOCD for archives whose central directory offsets, sizes, or counts exceed ZIP32 limits.

Important APIs/types/functions: `ZIP64_EOCD(const char*)` reads fixed offsets for record size, ZIP versions, disk numbers, entry counts, central-directory size, and central-directory offset. `ZIP64_EOCD(uint64_t cdoff, uint32_t cdcnt, uint32_t cdsize)` builds a single-disk ZIP64 record with version-made-by `(3 << 8) | 63` and minimum version `45`. `Serialize(buffer_t&)` appends the signature and fields in ZIP order. `ToString()` exposes fields for logging. Constants include `zip64EocdSign` and `zip64EocdBaseSize`.

Control flow: Parsing is offset-based and delegates endian conversion to `XrdZipUtils::to`. Construction fills single-disk fields and calculates `zip64EocdSize` as total base size plus extensible data minus the 12 bytes excluded by the ZIP spec. Serialization writes the signature, scalar fields, and optional `extensibleData`.

State and persistence behavior: The struct stores all ZIP64 EOCD fields as public members. Serialized state is persisted into a ZIP trailer; no external resource state is managed.

Dependencies and integration points: Includes ZIP utility functions and related LFH/CDFH headers. It integrates with ZIP writer/reader code that needs a ZIP64 trailer and with `ZIP64_EOCDL`, which points to this record.

Risks: The parsing constructor ignores the actual extensible data length and initializes `extensibleDataLength` to zero even though `zip64EocdSize` could indicate extra bytes. It also does no signature or length validation. `ToString()` writes `std::string extensibleData` directly, which can contain binary data.

Test signals: Tests should cover parsing known ZIP64 trailers, serialization byte-for-byte output, archives with no extensible data, and callers rejecting buffers with wrong signatures or insufficient length.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdZip/XrdZipZIP64EOCD.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdZip/XrdZipZIP64EOCDL.hh -->
# sources/distributed-fs/xrootd/src/XrdZip/XrdZipZIP64EOCDL.hh

Purpose: Models the ZIP64 End of Central Directory Locator, the fixed-size record that tells ZIP readers where the ZIP64 EOCD record is located.

Important APIs/types/functions: `ZIP64_EOCDL(const char*)` parses disk number, ZIP64 EOCD offset, and disk count from a raw buffer. `ZIP64_EOCDL(const EOCD&, const ZIP64_EOCD&)` computes the ZIP64 EOCD record offset from the normal EOCD fields when possible, falling back to ZIP64 central-directory offset and size when the ZIP32 fields contain overflow sentinels. `Serialize(buffer_t&)` emits the locator signature and fields. `ToString()` provides log-friendly formatting. Constants are `zip64EocdlSign` and `zip64EocdlSize`.

Control flow: The construction-from-records path starts with a zero disk number and one total disk, chooses the central directory offset from EOCD or ZIP64 EOCD, then adds central directory size from EOCD or ZIP64 EOCD to land at the ZIP64 EOCD position.

State and persistence behavior: The struct stores only the locator fields and serializes them into the ZIP trailer. There is no dynamic ownership or cache state.

Dependencies and integration points: Depends on `EOCD`, `ZIP64_EOCD`, and `ovrflw<uint32_t>` to recognize ZIP32 overflow. It is written after the ZIP64 EOCD and before the classic EOCD in ZIP64 archives.

Risks: Parsing does not validate signature or buffer length. The computed offset assumes a single-disk archive and specific central-directory layout. Multi-disk ZIP64 archives are represented by fields but not truly supported by the constructor.

Test signals: Important tests include locator serialization size/signature, offset computation when EOCD fields are normal, offset computation when EOCD fields overflow, and rejection of malformed buffers at higher-level callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdZip/XrdZipZIP64EOCDL.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/annotations/pom.xml -->
# sources/object-store/apache-ozone/hadoop-hdds/annotations/pom.xml

Purpose: Defines the `hdds-annotation-processing` Maven module. This module packages Apache Ozone compile-time annotation processors that validate internal annotations before the rest of the project compiles.

Important APIs/types/functions: The artifact is `org.apache.ozone:hdds-annotation-processing:2.3.0-SNAPSHOT`, packaged as a jar under the `hdds` parent. The module name and description identify it as annotation-processing tooling.

Control flow: Maven builds this module as an early dependency. The compiler plugin is configured with `<proc>none</proc>`, preventing the module's own processors from running while compiling the processors themselves.

State and persistence behavior: No runtime state. The persistent artifact is the jar containing processors and `META-INF/services` registrations.

Dependencies and integration points: Inherits dependencies and plugin configuration from the parent `hdds` project. The generated jar is later placed on javac's annotation processor path for other Ozone modules.

Risks: `<maven.test.skip>true</maven.test.skip>` means this module currently lacks direct test execution, so processor regressions can surface only when downstream modules compile. If service metadata is missing, processors silently will not run.

Test signals: Build-level signals are successful compilation of downstream modules with known-valid annotations and intentional invalid fixture annotations that fail compilation with the expected diagnostic messages.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/annotations/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/annotations/src/main/java/org/apache/ozone/annotations/OmRequestFeatureValidatorProcessor.java -->
# sources/object-store/apache-ozone/hadoop-hdds/annotations/src/main/java/org/apache/ozone/annotations/OmRequestFeatureValidatorProcessor.java

Purpose: Implements a javac annotation processor that validates Ozone Manager request feature validator methods annotated with `OMClientVersionValidator` or `OMLayoutVersionValidator`.

Important APIs/types/functions: The processor supports two annotation types and Java 8 source. It validates that annotated elements are methods, are static, have the right return type for the annotation processing phase, and have expected parameters. Constants define required fully qualified types for `OMRequest`, `OMResponse`, and `ValidationContext`. `ProcessingPhaseVisitor` extracts enum values for `PRE_PROCESS` and `POST_PROCESS`.

Control flow: `process` filters supported annotations by simple name, then passes matching annotated elements to `processElements`. For each annotation mirror on an element, `validateAnnotatedMethod` reads `processingPhase`, checks method kind and static modifier, validates return type, and validates parameter count/order. Errors are emitted with `processingEnv.getMessager()`.

State and persistence behavior: No persistent state beyond constants. Diagnostics are reported into the compiler round; returning `false` allows other processors to also process these annotations.

Dependencies and integration points: Integrates with Ozone OM request validation annotations and javac's annotation-processing API. It relies on type string equality against generated protobuf nested classes.

Risks: `validateAnnotatedMethod` casts to `ExecutableElement` after emitting a non-method error, so an incorrectly annotated class/field may still cause `ClassCastException` instead of a clean diagnostic. The processor loops over all annotation mirrors on an element, not only the matched annotation, so unrelated annotations lacking `processingPhase` may be treated as post-process by default. Default annotation values absent from `getElementValues()` can make `isPreprocessor` default false.

Test signals: Compile-failure tests should cover non-static validators, wrong parameter counts, wrong return types for pre/post phases, missing or default processing phase behavior, and non-method annotated elements.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/annotations/src/main/java/org/apache/ozone/annotations/OmRequestFeatureValidatorProcessor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/annotations/src/main/java/org/apache/ozone/annotations/RegisterValidatorProcessor.java -->
# sources/object-store/apache-ozone/hadoop-hdds/annotations/src/main/java/org/apache/ozone/annotations/RegisterValidatorProcessor.java

Purpose: Annotation processor for `RegisterValidator` annotations. It checks that annotated annotation types expose the required annotation methods used by Ozone request-validation registration.

Important APIs/types/functions: The required annotation methods are `applyBefore`, `requestType`, and `processingPhase`. `validateMethod` checks a method name, return element kind, and optional assignability to an expected interface. `validateArrayMethod` handles array-returning methods such as `requestType`. Error constants describe missing max-version, request-type, and processing-phase methods.

Control flow: `process` filters annotation types by simple name, retrieves elements annotated with `RegisterValidator`, and inspects only elements of kind `ANNOTATION_TYPE`. For each enclosed executable element, it updates booleans for required methods. Missing requirements produce compiler errors.

State and persistence behavior: No persistent runtime state; all validation is compiler diagnostic output.

Dependencies and integration points: Uses javac `Elements` and `Types` APIs and validates against `org.apache.hadoop.ozone.Version` and `RequestProcessingPhase`. It protects downstream OM validator annotation definitions from shape drift.

Risks: `validateArrayMethod` calls `types.asElement(method.getReturnType())` for the full array type in the assignability check when an expected interface is present; array types do not map like declared enum types. Current use passes `null` expected interface for `requestType`, avoiding that path. Non-annotation annotated elements are silently ignored. As with many processors, missing expected type elements could produce null-driven failures.

Test signals: Compile tests should include a valid registered annotation, annotations missing each required method, wrong enum/interface return types, array versus scalar request types, and non-annotation elements annotated with `RegisterValidator`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/annotations/src/main/java/org/apache/ozone/annotations/RegisterValidatorProcessor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/annotations/src/main/java/org/apache/ozone/annotations/ReplicateAnnotationProcessor.java -->
# sources/object-store/apache-ozone/hadoop-hdds/annotations/src/main/java/org/apache/ozone/annotations/ReplicateAnnotationProcessor.java

Purpose: Validates methods annotated with `org.apache.hadoop.hdds.scm.metadata.Replicate`. The processor enforces that replicated SCM metadata operations declare the expected checked exception contract.

Important APIs/types/functions: `ANNOTATION_NAME` identifies the processed annotation. `REQUIRED_EXCEPTION` is `org.apache.hadoop.hdds.scm.exceptions.SCMException`. `init` resolves the required exception type. `checkMethodSignature` verifies the annotated element is an executable method and that one of its declared thrown types is assignable from the required exception type.

Control flow: During each processing round, `process` finds the matching annotation by qualified name and checks every annotated element. Non-method elements receive an error. Methods without `SCMException` or a parent exception in `throws` receive an error attached to the method.

State and persistence behavior: The processor caches `requiredException` for the processing environment. It has no runtime persistence.

Dependencies and integration points: Depends on javac processing APIs and the SCM exception class being available on the annotation-processing classpath. It supports the metadata replication layer by keeping generated/proxied replicated methods compatible with failure semantics.

Risks: If the required exception type cannot be resolved, `init` can fail before a useful compiler diagnostic. The assignability direction accepts declared parent exceptions, matching the message, but should be checked if subclasses of `SCMException` are intended to be accepted.

Test signals: Compile tests should verify methods throwing `SCMException`, methods throwing `Exception`, methods throwing no exception, methods throwing unrelated exceptions, and accidental annotation on non-method elements.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/annotations/src/main/java/org/apache/ozone/annotations/ReplicateAnnotationProcessor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/annotations/src/main/java/org/apache/ozone/annotations/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/annotations/src/main/java/org/apache/ozone/annotations/package-info.java

Purpose: Provides package-level documentation for `org.apache.ozone.annotations`.

Important APIs/types/functions: No executable APIs are declared. The Javadoc states that the package contains compile-time annotation processors used by Ozone to validate internal annotations and related code.

Control flow: Not applicable; package-info is consumed by Javadoc and compilation metadata.

State and persistence behavior: No state. It persists package documentation in source and generated documentation.

Dependencies and integration points: Documents the same package that contains the Ozone annotation processors registered for javac.

Risks: The wording is broad and says "as needed, if needed"; it does not enumerate processors or contracts, so developers must inspect concrete classes for exact behavior.

Test signals: Compile-only signal that package-info remains syntactically valid.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/annotations/src/main/java/org/apache/ozone/annotations/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/cli-common/dev-support/findbugsExcludeFile.xml -->
# sources/object-store/apache-ozone/hadoop-hdds/cli-common/dev-support/findbugsExcludeFile.xml

Purpose: SpotBugs/FindBugs exclude filter for the `hdds-cli-common` module.

Important APIs/types/functions: Defines a root `<FindBugsFilter>` with no `<Match>` entries, so it currently excludes nothing.

Control flow: The module POM passes this file to the SpotBugs Maven plugin. SpotBugs reads it during static analysis.

State and persistence behavior: It is static build configuration only.

Dependencies and integration points: Integrated by `hadoop-hdds/cli-common/pom.xml` through `excludeFilterFile`.

Risks: Because the filter is empty, any future need for exclusions must be explicitly added. An empty file is low risk but can mislead readers into thinking there are module-specific suppressions.

Test signals: Static-analysis builds should continue to pass without relying on exclusions from this file.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/cli-common/dev-support/findbugsExcludeFile.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/cli-common/pom.xml -->
# sources/object-store/apache-ozone/hadoop-hdds/cli-common/pom.xml

Purpose: Maven module definition for shared Apache Ozone CLI infrastructure.

Important APIs/types/functions: The artifact is `hdds-cli-common`, packaging `jar`. It depends on picocli, Jakarta annotations, Hadoop common, `hdds-common`, Ratis common, and SLF4J. Build plugins configure SpotBugs, javac annotation processors, and an enforcer override.

Control flow: During compile, javac runs `org.kohsuke.metainf_services.AnnotationProcessorImpl` and picocli's GraalVM native image config generator. The default compile execution passes `-Aproject=${project.groupId}/${project.artifactId}`. Enforcer bans `Config` and `ConfigGroup` imports in this module while explaining the selected annotation processors.

State and persistence behavior: Produces the shared CLI jar and generated annotation/native-image metadata. No runtime state in the POM itself.

Dependencies and integration points: This module is consumed by Ozone admin/debug/repair CLI tools and any command package using `GenericCli`, marker interfaces, or picocli helpers.

Risks: The native-image and `MetaInfServices` processors are part of compile behavior; removing them can break dynamic command discovery or native packaging. The enforcer override is intentionally narrow and should be kept aligned with allowed processors.

Test signals: Maven compile, SpotBugs, service metadata generation, and CLI tests using dynamic subcommands are the main build signals.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/cli-common/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/cli-common/src/main/java/org/apache/hadoop/hdds/cli/AbstractMixin.java -->
# sources/object-store/apache-ozone/hadoop-hdds/cli-common/src/main/java/org/apache/hadoop/hdds/cli/AbstractMixin.java

Purpose: Base class for picocli mixins used by Ozone CLI commands. It lets mixins access the command spec, root command, and Ozone configuration.

Important APIs/types/functions: The class is annotated as a picocli command. It injects `CommandSpec` for the mixee through `@CommandLine.Spec(MIXEE)`. `spec()` returns that command spec, `rootCommand()` resolves the `GenericParentCommand`, and `getOzoneConf()` delegates to the root command.

Control flow: Picocli injects the mixee spec when parsing/constructing a command. Mixin methods then use `AbstractSubcommand.findRootCommand` to climb to the root command or a test fallback.

State and persistence behavior: The only state is the injected `CommandSpec`. Configuration state is owned by the root command.

Dependencies and integration points: Integrates with `AbstractSubcommand`, `GenericParentCommand`, `OzoneConfiguration`, and picocli mixin injection.

Risks: Calling `rootCommand()` before picocli injection would dereference a null spec. Mixins used outside picocli should be tested through command parsing rather than direct construction.

Test signals: Unit tests can build commands with mixins and confirm `getOzoneConf()` observes root-level configuration overrides.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/cli-common/src/main/java/org/apache/hadoop/hdds/cli/AbstractMixin.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/cli-common/src/main/java/org/apache/hadoop/hdds/cli/AbstractSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-hdds/cli-common/src/main/java/org/apache/hadoop/hdds/cli/AbstractSubcommand.java

Purpose: Shared base class for Ozone picocli subcommands. It provides access to root command context, output streams, verbose mode, configuration, and a unit-test fallback root.

Important APIs/types/functions: Picocli injects `CommandSpec`. `rootCommand()` memoizes `findRootCommand(spec)` through Ratis `MemoizedSupplier`. `isVerbose()`, `getOzoneConf()`, `out()`, and `err()` delegate to root or command line streams. `NoParentCommand` supplies a default `OzoneConfiguration`, current user lookup, and stack-trace error printing for tests that bypass `GenericCli`.

Control flow: Subcommands are executed by picocli with standard help options and `HddsVersionProvider`. On first root access, the class checks whether the root user object implements `GenericParentCommand`; otherwise it installs the fallback.

State and persistence behavior: Holds injected command spec and a memoized root supplier. The fallback root lazily caches `UserGroupInformation`.

Dependencies and integration points: Used by concrete Ozone CLI commands. Depends on picocli, `GenericParentCommand`, Hadoop security, and Ozone configuration.

Risks: Directly constructed subcommands need a spec before helper methods are safe. The fallback can hide missing root command setup in tests, so integration tests should also run through `GenericCli`.

Test signals: Command execution tests should verify inherited version/help options, stdout/stderr routing, fallback behavior, and root configuration propagation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/cli-common/src/main/java/org/apache/hadoop/hdds/cli/AbstractSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/cli-common/src/main/java/org/apache/hadoop/hdds/cli/AdminSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-hdds/cli-common/src/main/java/org/apache/hadoop/hdds/cli/AdminSubcommand.java

Purpose: Marker interface for subcommands discoverable under `OzoneAdmin`.

Important APIs/types/functions: Declares no methods. Implementing classes use it as their service-loader type.

Control flow: `ExtensibleParentCommand.addSubcommands` can load providers of this interface, inspect their picocli command annotation, sort them by command name, and add them to an admin parent command.

State and persistence behavior: No state. Persistent behavior comes from `META-INF/services` provider files generated or supplied by implementations.

Dependencies and integration points: Integrated with `ExtensibleParentCommand`, `ServiceLoader`, picocli annotations, and admin CLI modules.

Risks: Implementations must be annotated with `@CommandLine.Command` and registered as services; otherwise dynamic loading will fail or throw a null annotation issue.

Test signals: Service-loader tests for admin plugins should verify that implementations appear under the admin command.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/cli-common/src/main/java/org/apache/hadoop/hdds/cli/AdminSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/cli-common/src/main/java/org/apache/hadoop/hdds/cli/DebugSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-hdds/cli-common/src/main/java/org/apache/hadoop/hdds/cli/DebugSubcommand.java

Purpose: Marker interface for subcommands discoverable under `OzoneDebug`.

Important APIs/types/functions: It has no methods and exists only as a service-loader classification type.

Control flow: Parent commands implementing `ExtensibleParentCommand` can return this marker from `subcommandType()`. The common loader then discovers providers, wraps them in picocli command lines, and registers them recursively.

State and persistence behavior: No state or persistence except service metadata provided by implementations.

Dependencies and integration points: Used by debug-oriented CLI modules with picocli and `ServiceLoader`.

Risks: Missing service registration or missing command annotation on an implementation prevents discovery. Because the interface has no type contract, behavior correctness lives entirely in implementing classes.

Test signals: Dynamic debug CLI registration tests and command help output are the relevant signals.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/cli-common/src/main/java/org/apache/hadoop/hdds/cli/DebugSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/cli-common/src/main/java/org/apache/hadoop/hdds/cli/DeprecatedCliOption.java -->
# sources/object-store/apache-ozone/hadoop-hdds/cli-common/src/main/java/org/apache/hadoop/hdds/cli/DeprecatedCliOption.java

Purpose: Emits compatibility warnings when legacy multi-character single-dash CLI options are used.

Important APIs/types/functions: `DEPRECATED_OPTIONS` is a `LinkedHashMap` mapping old names such as `-conf`, `-id`, `-host`, and `-pt` to preferred long options. `warnIfMatched(CommandLine.ParseResult)` scans a root parse result and subcommand parse results. `warn(PrintWriter, String, String)` formats the warning.

Control flow: `GenericCli` installs an execution strategy that calls `warnIfMatched` before `RunLast`. The scanner iterates every `CommandLine` in the parse-result chain and checks `hasMatchedOption` for each deprecated name.

State and persistence behavior: Static immutable-by-convention map; no runtime persistence. Warnings are written to stderr.

Dependencies and integration points: Depends on picocli parse state and is coupled to hidden/deprecated option aliases in Ozone CLI commands.

Risks: The map must stay synchronized with actual aliases; otherwise warnings may be absent or check names not defined on a command. It only warns for options recognized by picocli, so removed aliases will fail parsing before warning.

Test signals: CLI parsing tests should assert warnings for deprecated aliases, no warnings for preferred aliases, and behavior across nested subcommands.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/cli-common/src/main/java/org/apache/hadoop/hdds/cli/DeprecatedCliOption.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/cli-common/src/main/java/org/apache/hadoop/hdds/cli/ExtensibleParentCommand.java -->
# sources/object-store/apache-ozone/hadoop-hdds/cli-common/src/main/java/org/apache/hadoop/hdds/cli/ExtensibleParentCommand.java

Purpose: Defines the dynamic subcommand extension contract for Ozone CLI parent commands.

Important APIs/types/functions: `subcommandType()` returns the marker interface class used for service discovery. Static `addSubcommands(CommandLine)` recursively registers discovered subcommands.

Control flow: For any command object implementing this interface, the loader calls `ServiceLoader.load` with its marker type, creates `CommandLine` wrappers using the parent's factory, sorts providers by their `@CommandLine.Command.name()`, and adds them to the parent. It then recurses into all subcommands.

State and persistence behavior: No internal state. Persistent discovery depends on service provider metadata in jars.

Dependencies and integration points: Works with `AdminSubcommand`, `DebugSubcommand`, `RepairSubcommand`, picocli, `ServiceLoader`, and `MetaInfServices` generated metadata.

Risks: It assumes every provider class has a `@CommandLine.Command` annotation; if absent, dereferencing `commandAnnotation.name()` fails. Duplicate names overwrite in the sorted map before registration. Service loading happens at CLI construction, so classpath problems affect startup.

Test signals: Tests should include deterministic ordering, recursive registration, duplicate-name handling expectations, and provider classes missing annotations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/cli-common/src/main/java/org/apache/hadoop/hdds/cli/ExtensibleParentCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/cli-common/src/main/java/org/apache/hadoop/hdds/cli/GenericCli.java -->
# sources/object-store/apache-ozone/hadoop-hdds/cli-common/src/main/java/org/apache/hadoop/hdds/cli/GenericCli.java

Purpose: Generic root implementation for Ozone command-line tools. It owns shared configuration loading, current-user lookup, execution strategy, dynamic subcommand registration, and concise error reporting.

Important APIs/types/functions: `execute` delegates to picocli, while `run` terminates nonzero exits through Ratis `ExitUtils`. Options include inherited `--verbose`, `-D/--set` configuration overrides, preferred `--conf`, and hidden deprecated `-conf`. `printError` chooses stack trace, ACL formatting, filesystem-specific messages, or the first error line. `getOzoneConf()` lazily adds the configured resource once. `getUser()` caches `UserGroupInformation`.

Control flow: Construction creates `CommandLine`, installs an execution exception handler, installs a strategy that warns for deprecated options then runs the last command, and dynamically adds service-loaded subcommands. During configuration lookup, `--conf` takes precedence over deprecated `-conf`.

State and persistence behavior: Holds one `OzoneConfiguration`, one picocli command, optional user, configuration path fields, and an "added" flag to avoid duplicate resource loading.

Dependencies and integration points: Core integration point for all Ozone CLIs built on picocli. Uses Hadoop `Path`, `HddsUtils`, `OzoneConfiguration`, UGI, `DeprecatedCliOption`, and `ExtensibleParentCommand`.

Risks: `printError` calls `ExitUtils.terminate` inside ACL handling, which can surprise tests unless exit trapping is configured. Configuration resources are added lazily, so code accessing `config` directly before `getOzoneConf()` would miss `--conf`. Error output truncates multiline messages unless verbose.

Test signals: Existing `TestGenericCliConfiguration` covers `--conf` versus `-conf` precedence. Additional signals include `-D` overrides, filesystem exception formatting, verbose stack traces, deprecated option warnings, and dynamic subcommand loading.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/cli-common/src/main/java/org/apache/hadoop/hdds/cli/GenericCli.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/cli-common/src/main/java/org/apache/hadoop/hdds/cli/GenericParentCommand.java -->
# sources/object-store/apache-ozone/hadoop-hdds/cli-common/src/main/java/org/apache/hadoop/hdds/cli/GenericParentCommand.java

Purpose: Shared interface exposed by CLI root commands to subcommands and mixins.

Important APIs/types/functions: Declares `isVerbose()`, `getOzoneConf()`, `getUser()`, and `printError(Throwable)`. The contract specifies cached configuration and cached `UserGroupInformation`.

Control flow: `AbstractSubcommand` and `AbstractMixin` resolve their root as this interface and delegate common behavior to it.

State and persistence behavior: Interface has no state, but implementations such as `GenericCli` own the configuration and user cache.

Dependencies and integration points: Bridges CLI command classes to `OzoneConfiguration` and Hadoop security without requiring a concrete `GenericCli` dependency.

Risks: Implementations need consistent caching and error semantics. A test fallback implementation exists in `AbstractSubcommand`, so behavior can differ from production root command behavior.

Test signals: Subcommand unit tests should verify calls through this interface observe the intended root implementation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/cli-common/src/main/java/org/apache/hadoop/hdds/cli/GenericParentCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/cli-common/src/main/java/org/apache/hadoop/hdds/cli/HddsVersionProvider.java -->
# sources/object-store/apache-ozone/hadoop-hdds/cli-common/src/main/java/org/apache/hadoop/hdds/cli/HddsVersionProvider.java

Purpose: Picocli version provider for HDDS/Ozone CLI commands.

Important APIs/types/functions: Implements `CommandLine.IVersionProvider`. `getVersion()` returns a one-element string array containing `HddsVersionInfo.HDDS_VERSION_INFO.getBuildVersion()`.

Control flow: Picocli invokes the provider when a command using it receives a version option.

State and persistence behavior: No state. It reads static build/version metadata from `HddsVersionInfo`.

Dependencies and integration points: Referenced by `AbstractSubcommand`'s `versionProvider`. Integrates CLI version output with HDDS build metadata.

Risks: If build metadata is missing or malformed, version output quality depends on `HddsVersionInfo`. The method declares `Exception` per picocli interface but does not handle failures.

Test signals: CLI `--version` output should include the expected HDDS build version.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/cli-common/src/main/java/org/apache/hadoop/hdds/cli/HddsVersionProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/cli-common/src/main/java/org/apache/hadoop/hdds/cli/ItemsFromStdin.java -->
# sources/object-store/apache-ozone/hadoop-hdds/cli-common/src/main/java/org/apache/hadoop/hdds/cli/ItemsFromStdin.java

Purpose: Abstract helper for CLI parameters that accept a list of items either from command-line arguments or from standard input when the first argument is `-`.

Important APIs/types/functions: `FORMAT_DESCRIPTION` provides reusable option help suffix text. `setItems(List<String>)` is the main mutator. `isReadFromStdin()`, `getItems()`, `iterator()`, and `size()` expose the loaded items. `readItemsFromStdin()` reads UTF-8 lines with `Scanner` and trims each line.

Control flow: Subclasses call `setItems` from picocli setter methods. If the argument list starts with `-`, all items are replaced by lines read from stdin; otherwise the supplied list or an empty list is stored.

State and persistence behavior: Holds an in-memory item list and a boolean indicating stdin mode. `getItems()` returns an unmodifiable view.

Dependencies and integration points: Used by CLI commands needing repeated item arguments. Depends on Jakarta `@Nonnull`, standard input, and Java collection iteration.

Risks: Reading stdin is blocking until EOF, so commands must document usage. Only the first argument controls stdin mode; later arguments are ignored in stdin mode. Trimming lines may remove significant whitespace.

Test signals: Tests should cover null/empty arguments, normal lists, `-` stdin mode with multiple lines, iterator behavior, and unmodifiable output.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/cli-common/src/main/java/org/apache/hadoop/hdds/cli/ItemsFromStdin.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/cli-common/src/main/java/org/apache/hadoop/hdds/cli/RepairSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-hdds/cli-common/src/main/java/org/apache/hadoop/hdds/cli/RepairSubcommand.java

Purpose: Marker interface for subcommands discoverable under `OzoneRepair`.

Important APIs/types/functions: Declares no methods; it is a `ServiceLoader` marker.

Control flow: A repair parent command can return this marker from `subcommandType()`, letting `ExtensibleParentCommand.addSubcommands` discover, sort, and register repair subcommands.

State and persistence behavior: No state; provider metadata controls persistence of discovery.

Dependencies and integration points: Used with picocli and service-loader based CLI extension.

Risks: Same marker-interface risks as admin/debug markers: missing provider registration or missing command annotation prevents loading.

Test signals: Repair CLI help and service discovery tests should confirm registered repair commands appear.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/cli-common/src/main/java/org/apache/hadoop/hdds/cli/RepairSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/cli-common/src/main/java/org/apache/hadoop/hdds/cli/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/cli-common/src/main/java/org/apache/hadoop/hdds/cli/package-info.java

Purpose: Package-level documentation for shared HDDS/Ozone CLI helpers.

Important APIs/types/functions: No executable declarations. The package doc says the package contains generic helper classes to instantiate picocli-based CLI tools.

Control flow: Not applicable.

State and persistence behavior: No state; persists documentation.

Dependencies and integration points: Describes the package containing `GenericCli`, subcommand bases, marker interfaces, and related helpers.

Risks: Documentation is brief and grammatically rough, so it does not communicate dynamic service-loader behavior or root-command contracts.

Test signals: Compile/Javadoc generation is the only direct signal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/cli-common/src/main/java/org/apache/hadoop/hdds/cli/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/cli-common/src/test/java/org/apache/hadoop/hdds/cli/TestGenericCliConfiguration.java -->
# sources/object-store/apache-ozone/hadoop-hdds/cli-common/src/test/java/org/apache/hadoop/hdds/cli/TestGenericCliConfiguration.java

Purpose: Unit tests for `GenericCli` configuration-file option precedence, especially preferred `--conf` versus deprecated hidden `-conf`.

Important APIs/types/functions: `TestGenericCli` is an empty concrete subclass of `GenericCli`. Three JUnit 5 tests parse arguments and inspect `cli.getOzoneConf().get("test.key")`. `writeConf` creates temporary Hadoop XML configuration files with different values.

Control flow: Each test writes one or two temporary configs, parses arguments through picocli without executing a command, then lazily triggers config resource loading through `getOzoneConf()`. Assertions use AssertJ.

State and persistence behavior: Temporary files are created with `Files.createTempFile`, written as UTF-8 XML, and marked `deleteOnExit`. Each `GenericCli` has its own configuration state.

Dependencies and integration points: Tests the `GenericCli` path-selection logic and Hadoop `Configuration.addResource` parsing.

Risks: Tests rely on `deleteOnExit`, which can accumulate temp files in long-lived JVMs. They only cover configuration precedence, not warning emission for `-conf`.

Test signals: Confirms `--conf` wins when both options are present in either order, and deprecated `-conf` still works when preferred `--conf` is absent.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/cli-common/src/test/java/org/apache/hadoop/hdds/cli/TestGenericCliConfiguration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/dev-support/findbugsExcludeFile.xml -->
# sources/object-store/apache-ozone/hadoop-hdds/client/dev-support/findbugsExcludeFile.xml

Purpose: SpotBugs filter for the `hdds-client` module.

Important APIs/types/functions: Contains one `<Match>` suppressing `EI_EXPOSE_REP2` for `org.apache.hadoop.hdds.scm.storage.ByteArrayReader`, with a comment that deep-copying `byte[]` would hurt performance.

Control flow: The client module POM passes this filter to SpotBugs during static analysis.

State and persistence behavior: Static build-time configuration only.

Dependencies and integration points: Integrated through the `spotbugs-maven-plugin` configuration in `client/pom.xml`.

Risks: Suppression applies only to a specific class not otherwise included in this work item. If the class moves or behavior changes, the stale filter may hide or fail to hide the intended warning.

Test signals: SpotBugs output should show this one intentional suppression and no broad class of hidden warnings.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/dev-support/findbugsExcludeFile.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/pom.xml -->
# sources/object-store/apache-ozone/hadoop-hdds/client/pom.xml

Purpose: Maven module definition for the HDDS client library used by Apache Ozone clients to talk to storage containers and datanodes.

Important APIs/types/functions: The artifact is `hdds-client`. Dependencies include Guava, Jakarta annotations, commons-lang3, Hadoop common, HDDS common/config/erasurecode/interface-client, Ratis client/common/grpc/proto/thirdparty misc, SLF4J, and test utilities. Build plugins configure SpotBugs, the HDDS config annotation processor, and an enforcer rule banning `org.kohsuke.MetaInfServices`.

Control flow: During compilation, `ConfigFileGenerator` processes `@Config` classes such as `OzoneClientConfig` and `XceiverClientManager.ScmClientConfig`. SpotBugs uses the module filter. The enforcer override narrows allowed annotations/processors for this module.

State and persistence behavior: Produces the HDDS client jar and generated configuration metadata. No runtime state is in the POM.

Dependencies and integration points: This module is central to Ozone object-store clients, container protocol calls, Ratis/gRPC communication, and erasure-coded IO.

Risks: The dependency graph includes both Hadoop retry APIs and Ratis APIs; version drift can affect exception handling and wire behavior. The config annotation processor is required for documented config generation.

Test signals: Maven compile, config generation, SpotBugs, and client integration tests exercising Ratis/gRPC paths are key signals.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/ContainerClientMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/ContainerClientMetrics.java

Purpose: Hadoop metrics source for container client write distribution and latency measurements.

Important APIs/types/functions: Static `acquire`, `acquireHandle`, and `release` manage a singleton metrics source with reference counting. `Handle` is `AutoCloseable`. Counters track total write-chunk calls/bytes, per-pipeline calls/bytes, and leader call counts. Mutable rates track hsync phases. Quantile arrays cover list/get/read/get-small-file/hsync latencies for 60/300/900 second intervals.

Control flow: First acquire registers an instance with `DefaultMetricsSystem` under a unique source name. Each acquire increments `referenceCount`. Release decrements and unregisters/stops quantiles when the count reaches zero. `recordWriteChunk` lazily creates per-pipeline/per-leader counters and increments totals. Latency methods add samples to every configured quantile.

State and persistence behavior: Static singleton, reference count, instance count, metrics registry, concurrent maps, and mutable metric objects. Metrics are process-local and exported through Hadoop metrics, not persisted by this class.

Dependencies and integration points: Used by write paths to report container IO. Depends on Hadoop metrics2, `Pipeline`, `PipelineID`, `DatanodeID`, and `MetricUtil`.

Risks: Manual reference counting can leak metrics if clients do not release, or throw if release is called too often. Dynamic metric names include IDs and can grow with many pipelines. Singleton synchronization protects acquire/release but per-metric maps rely on concurrent structures.

Test signals: Tests should cover acquire/release lifecycle, handle idempotent close, per-pipeline counter creation, quantile stopping, and reference-count edge cases.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/ContainerClientMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/ECXceiverClientGrpc.java -->
# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/ECXceiverClientGrpc.java

Purpose: Erasure-coding-specific gRPC xceiver client. It customizes standalone gRPC behavior for EC write semantics and optional gRPC retry policy.

Important APIs/types/functions: Constructor reads EC retry enable/max settings and sets EC write timeout. `shouldBlockAndWaitAsyncReply` always returns false, allowing async EC write requests to proceed without the base class's write synchronization wait. `createChannel` extends the base Netty channel builder with service-config retry policy when enabled. `createRetryServiceConfig` builds the gRPC retry configuration for `DEADLINE_EXCEEDED`.

Control flow: On channel creation, if retries are enabled, it configures max attempts, backoff settings, retryable status codes, target service name, and enables gRPC retry. Async sends rely on external EC synchronization rather than blocking in the client.

State and persistence behavior: Stores one `enableRetries` boolean and inherited channel/cache state. No persistence.

Dependencies and integration points: Extends `XceiverClientGrpc`, uses Ozone EC gRPC config keys, datanode details, Netty gRPC, and container protobuf requests.

Risks: Disabling async blocking assumes EC write layers correctly order and synchronize requests. Retry service config applies to the whole service and currently retries only deadline exceeded, which may or may not match every EC failure mode. `maxAttempts` is read as int but stored in a `double` map value for gRPC config.

Test signals: Tests should verify nonblocking async behavior, EC timeout selection, retry config shape, and retry disabled/enabled channel builder behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/ECXceiverClientGrpc.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/ErrorInjector.java -->
# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/ErrorInjector.java

Purpose: Functional test hook for injecting server-like errors into client-side Ratis request handling.

Important APIs/types/functions: Single method `getResponse(ContainerCommandRequestProto request, ClientId id, Pipeline pipeline)` returns a `RaftClientReply` to substitute for a real Ratis response, or presumably null to allow normal execution.

Control flow: `XceiverClientCreator.enableErrorInjection` stores an injector, and `XceiverClientRatis.sendRequestAsync` consults it before sending a request to Ratis. A non-null reply short-circuits normal network IO with a completed future.

State and persistence behavior: Interface has no state. The global static reference in `XceiverClientCreator` is the stateful integration point.

Dependencies and integration points: Depends on container command protobufs, Ratis client IDs/replies, and SCM pipelines. Used by tests or fault-injection scenarios.

Risks: Global static injection can leak between tests if not reset. Injected replies must be coherent with request and pipeline or downstream code can fail in surprising ways.

Test signals: Fault-injection tests should assert injected failures propagate and normal path resumes when injector returns null or is cleared.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/ErrorInjector.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/OzoneClientConfig.java -->
# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/OzoneClientConfig.java

Purpose: Configuration bean for Ozone client behavior, generated/documented by HDDS config annotations.

Important APIs/types/functions: Annotated with `@ConfigGroup(prefix = "ozone.client")`. It defines stream buffer sizes, datastream packet/window/sync settings, retry counts/intervals, checksum type and bytes per checksum, EC retry/queue/reconstruction pool settings, default bucket layout, HBase enhancement gates, streaming read settings, and checksum combine mode. `validate()` enforces consistency and mutates invalid settings to defaults where appropriate. Nested `ChecksumCombineMode`, `Keys`, and `Defaults` expose enum and stable test constants.

Control flow: Config injection sets fields from configuration. `@PostConstruct validate` checks positive buffer sizes, divisibility between max/flush/chunk sizes, minimum checksum size, HBase enhancement gate behavior, and streaming read sanity. Getters and setters expose fields to client components.

State and persistence behavior: Holds in-memory client configuration. It does not persist values itself, but annotations feed generated config documentation/metadata.

Dependencies and integration points: Used by stream output/input classes, checksum logic, EC code, bucket creation defaults, and HBase-related client features. Depends on `OzoneConfigKeys`, Guava preconditions, and HDDS config annotations.

Risks: Validation both rejects some invalid values and silently resets others with warnings; callers must ensure `validate()` has run when constructing manually. `getChecksumCombineMode()` returns null for invalid strings rather than defaulting. HBase enhancement settings are forcibly disabled unless allowed, which can surprise deployments if only subfeature flags are set.

Test signals: Config tests should cover divisibility failures, checksum minimum reset, HBase gate overrides, invalid stream read values, checksum combine parsing, and EC/HBase feature defaults.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/OzoneClientConfig.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/StreamBufferArgs.java -->
# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/StreamBufferArgs.java

Purpose: Immutable-by-convention argument bundle for Ozone client stream buffer sizing.

Important APIs/types/functions: Holds buffer size, flush size, max size, and flush-delay flag. Builder exposes setters and `build()`. `getDefaultStreamBufferArgs(ReplicationConfig, OzoneClientConfig)` chooses values based on replication type.

Control flow: For EC replication, buffer, flush, and max sizes all become the EC chunk size from `ECReplicationConfig`. For non-EC replication, values come from `OzoneClientConfig`. Flush-delay always comes from client config.

State and persistence behavior: Stores buffer parameters in memory. Setters are protected except flush-delay setter is public, so the object is not strictly immutable.

Dependencies and integration points: Used by stream writing code to derive buffer pool behavior. Depends on replication configs and `HddsProtos.ReplicationType`.

Risks: The EC branch casts `ReplicationConfig` to `ECReplicationConfig` after checking type; custom configs must obey that contract. No validation is performed in the builder, so invalid sizes must be caught elsewhere.

Test signals: Tests should cover EC and non-EC defaults, flush-delay propagation, and builder setter behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/StreamBufferArgs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/XceiverClientCreator.java -->
# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/XceiverClientCreator.java

Purpose: Non-caching factory for connected `XceiverClientSpi` instances.

Important APIs/types/functions: Constructors capture configuration, optional `ClientTrustManager`, security flag, and topology-aware-read flag. `enableErrorInjection` stores a static `ErrorInjector`. `newClient(Pipeline)` chooses `XceiverClientRatis`, `XceiverClientGrpc`, or `ECXceiverClientGrpc` by pipeline replication type and connects it. `acquireClient`/`releaseClient` implement `XceiverClientFactory` without caching.

Control flow: Construction requires a trust manager when security is enabled. New clients are created per acquire and immediately connected; connection failures are wrapped as IOExceptions. Release closes the client quietly, with topology-aware read release respecting configured topology mode.

State and persistence behavior: Stores factory config and static global error injector. No client cache; users own acquired clients until release.

Dependencies and integration points: Base class for `XceiverClientManager`. Integrates pipeline types with Ratis/gRPC implementations, Ozone security, trust management, and topology-aware read behavior.

Risks: The static error injector is global and can affect all factories. For security-enabled clusters, null trust manager is rejected at construction. Unsupported `CHAINED` or unknown pipeline types throw.

Test signals: Tests should verify client type selection, security trust-manager requirement, connection failure wrapping, quiet release, and error-injection isolation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/XceiverClientCreator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/XceiverClientFactory.java -->
# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/XceiverClientFactory.java

Purpose: Interface for obtaining and releasing `XceiverClientSpi` connections to container pipelines.

Important APIs/types/functions: Defines general acquire/release, read-specific acquire/release, topology-aware acquire, and topology-aware release methods. Extends `AutoCloseable`.

Control flow: Implementations decide whether to cache, connect, close, or topology-select clients. Callers acquire with a `Pipeline`, use the client, then release with an invalidation hint.

State and persistence behavior: Interface has no state. Implementations such as `XceiverClientCreator` and `XceiverClientManager` own state.

Dependencies and integration points: Used by block input/output paths and higher-level Ozone clients to abstract Ratis/gRPC client creation and pooling.

Risks: Correctness depends on callers always releasing clients, especially when an implementation caches references. The invalidation and topology flags must be consistently interpreted across implementations.

Test signals: Contract tests should exercise acquire/release pairs, invalidation behavior, read-specific topology use, and close cleanup.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/XceiverClientFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/XceiverClientGrpc.java -->
# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/XceiverClientGrpc.java

Purpose: Standalone gRPC implementation of `XceiverClientSpi` for datanode container protocol operations, especially reads and non-Ratis standalone writes.

Important APIs/types/functions: Manages per-datanode `ManagedChannel` and async stubs in `ChannelInfo`. `connect`, `connectToDatanode`, and `createChannel` establish gRPC transport with optional TLS. `sendCommand`, `sendCommandAsync`, and `sendCommandOnAllNodes` send container protobuf requests. `sortDatanodes` chooses read retry order with leader/cache/topology/operational-state handling. Streaming read uses `initStreamRead`, `streamRead`, and `completeStreamRead`.

Control flow: Initial connect targets closest or first node. Each send injects trace ID and current client version if absent, then sends through a per-call gRPC bidirectional stream. A semaphore bounds outstanding requests, and metrics are incremented/decremented around each call. Synchronous sends retry datanodes in sorted order. `GetBlock` caches the successful datanode so `ReadChunk` can favor the same DN. EC requests are reconstructed with datanode UUID and replica index where needed.

State and persistence behavior: Holds pipeline, config, security config, metrics, timeout, semaphore, per-DN channel map, block-to-DN cache, trust manager, and closed flag. State is process-local and cleared on close.

Dependencies and integration points: Integrates with `XceiverClientManager` metrics, datanode protobuf service stubs, tracing, security/TLS, topology-aware reads, `HddsClientUtils`, and Ozone client versioning.

Risks: `pipeline.getNodes()` may return mutable lists; `sortDatanodes` swaps/shuffles returned lists, so pipeline list semantics matter. Semaphore release correctness depends on gRPC callbacks; streaming reads require explicit `completeStreamRead`. Close waits up to five seconds and logs unclosed channels. Authentication errors are translated to `SCMSecurityException`.

Test signals: Tests should cover datanode sort order, GetBlock/ReadChunk cache, EC request reconstruction, semaphore release on success/error, TLS/plaintext channel creation, close idempotence, and streaming read fallback.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/XceiverClientGrpc.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/XceiverClientManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/XceiverClientManager.java

Purpose: Caching lifecycle manager for `XceiverClientSpi` instances. It reuses connected clients per pipeline/cache-key and tracks cache metrics.

Important APIs/types/functions: Extends `XceiverClientCreator`. A Guava `Cache<String, XceiverClientSpi>` expires clients after idle threshold and caps cache size. `acquireClient` validates pipeline nodes, fetches/creates a cached client, and increments its reference count. `releaseClient` decrements references and optionally invalidates the cache entry. `getPipelineCacheKey` composes pipeline id/type, optional closest host/standalone port, and current user for security. Static `getXceiverClientMetrics` lazily creates shared client metrics. Nested `ScmClientConfig` and builder define cache sizing and stale threshold.

Control flow: Cache removal marks clients evicted. Acquire/release synchronize on the cache to coordinate reference counts and invalidation. Close invalidates all entries, unregisters cache metrics, and unregisters xceiver metrics.

State and persistence behavior: Owns client cache, cache metrics, and static process-wide xceiver metrics. Client references and eviction flags are in memory.

Dependencies and integration points: Used by Ozone client IO paths for connection pooling. Depends on Guava cache, HDDS config annotations, UGI, `CacheMetrics`, and `XceiverClientCreator`.

Risks: Removal listener only calls `setEvicted`; actual close may depend on `XceiverClientSpi` reference/eviction behavior outside this file. Cache key construction catches closest-node/current-user exceptions and continues with degraded keys, risking collisions. Static metrics lifecycle spans managers.

Test signals: Tests should cover cache reuse, invalidation, max-size eviction, idle expiration, topology-aware/EC key suffixes, security user suffix, and close unregistering metrics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/XceiverClientManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/XceiverClientMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/XceiverClientMetrics.java

Purpose: Metrics source for storage container client operations and EC reconstruction counters.

Important APIs/types/functions: Tracks global `pendingOps`, `totalOps`, `ecReconstructionTotal`, and `ecReconstructionFailsTotal`, plus per-`ContainerProtos.Type` pending/op counters and latency `PerformanceMetrics`. `create` registers with `DefaultMetricsSystem`. `incrPendingContainerOpsMetrics`, `decrPendingContainerOpsMetrics`, and `addContainerOpsLatency` are called around requests. `getMetrics` snapshots all counters and latencies.

Control flow: `init` reads percentile intervals from an `OzoneConfiguration`, creates a registry, and initializes maps for every container command type. Request paths increment pending/total before async send, decrement and record latency on completion. `unRegister` closes latency metrics and unregisters the source.

State and persistence behavior: Holds mutable counters, maps, and registry in process memory. Export is through Hadoop metrics.

Dependencies and integration points: Created by `XceiverClientManager` and used by gRPC, Ratis, and datastream write paths. Depends on Hadoop metrics2 and Ozone `PerformanceMetrics`.

Risks: `reset()` calls `init()` without unregistering previous registry-derived metrics, so tests must isolate carefully. `decrPendingContainerOpsMetrics` uses `incr(-1)`, relying on Hadoop metrics allowing negative increments. Creating a new `OzoneConfiguration` inside metrics ignores caller-specific percentile config unless globally loaded.

Test signals: Tests should validate per-command counters, pending decrement, latency snapshot presence, EC reconstruction counters, reset behavior, and unregister cleanup.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/XceiverClientMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/XceiverClientRatis.java -->
# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/XceiverClientRatis.java

Purpose: Ratis-backed `XceiverClientSpi` implementation for replicated container writes and read-only Ratis operations.

Important APIs/types/functions: Static factories create clients from pipeline, config, trust manager, and optional error injector. Constructor sets RPC type, retry policy, TLS config, watch replication level, majority size, and commit-info map. `connect` builds a Ratis `RaftClient`. `sendCommandAsync` sends container requests via Ratis async API and converts `RaftClientReply` messages into container responses. `watchForCommit` waits for configured replication level with fallback from all-committed to majority-committed. `updateCommitInfosMap` tracks per-server commit indexes.

Control flow: `sendRequestAsync` first allows error injection. Read-only requests use `async().sendReadOnly`; others use `async().send`. Completion updates metrics, validates success, parses protobuf response, updates commit info on successful container result, records log index and replier datanode. `watchForCommit` returns immediately if local replicated minimum already satisfies the index; otherwise it calls Ratis watch and handles `NotReplicatedException` by extracting commit info or issuing majority watch fallback.

State and persistence behavior: Stores pipeline, atomic Raft client, retry/TLS/config, commit-index map, metrics, watch type, majority count, and error injector. State is process-local and cleared by close.

Dependencies and integration points: Integrates with Apache Ratis, HDDS Ratis helper/message wrappers, tracing, security TLS, xceiver metrics, datastream API, and block stream commit watchers.

Risks: Watch type supports only `ALL_COMMITTED` or `MAJORITY_COMMITTED`; misconfigurations throw at construction. Commit-info map update semantics remove failed nodes after all-commit failure, affecting later minimum calculations. Close wraps IOExceptions as unchecked `IllegalStateException`. Error injection can bypass real Ratis behavior.

Test signals: Tests should cover send success/failure parsing, read-only routing, commit-info updates for all and majority, watch fallback on `NotReplicatedException`, group mismatch propagation, data stream API exposure, and close/connect idempotence.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/XceiverClientRatis.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/client/HddsClientUtils.java -->
# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/client/HddsClientUtils.java

Purpose: Shared utility methods for Ozone/HDDS clients, covering resource-name validation, retry-policy creation, config accessors, and exception unwrapping.

Important APIs/types/functions: `verifyResourceName` enforces S3-like bucket/volume/resource naming with optional non-strict underscore support. `verifyKeyName` validates key names with Ozone regex. `checkNotNull` validates varargs references. `getListCacheSize`, `getDefaultS3VolumeName`, and `getMaxOutstandingRequests` read client settings. `checkForException` unwraps nested exceptions against an expected list. `containsException` searches causal chains. `createRetryPolicy` and `getRetryPolicyByException` build Hadoop retry policies.

Control flow: Resource validation scans characters, detects all-numeric/IP-like names, checks unsupported characters and invalid dot/dash adjacency, then checks length and edge characters. Retry policy mapping uses zero-delay retries for timeout and Ratis retry failures and configured delay for other known exceptions.

State and persistence behavior: Static utility only. The exception list and log-name length constant are immutable static data.

Dependencies and integration points: Used by xceiver clients, stream output/input retry logic, and higher-level Ozone clients. Depends on Ozone constants, Ratis exceptions, Hadoop retry APIs, and HDDS configuration.

Risks: `verifyResourceName` loops over `resName.length()` before null checking, so null input causes `NullPointerException` rather than the intended `IllegalArgumentException`. `checkForException` returns the last cause if no expected class is found, which can affect retry-map lookups. Non-strict S3 behavior allows underscore only.

Test signals: Tests should cover invalid/valid resource names, null handling, long-name truncation in messages, IPv4/all-numeric rejection, key regex failures, retry policy mappings, and exception-chain search.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/client/HddsClientUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/client/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/client/package-info.java

Purpose: Package documentation for client-facing container operation classes.

Important APIs/types/functions: No executable API. The comment identifies the package as containing client-facing classes for container operations.

Control flow: Not applicable.

State and persistence behavior: No state; persists Javadoc metadata.

Dependencies and integration points: Documents `org.apache.hadoop.hdds.scm.client`, including `HddsClientUtils`.

Risks: Documentation is minimal and does not enumerate public utility contracts or retry behavior.

Test signals: Compile/Javadoc generation only.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/client/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/package-info.java

Purpose: Package-level architecture documentation for HDDS SCM client implementations.

Important APIs/types/functions: No executable code. The doc explains that the package contains container service clients, distinguishes Ratis and Standalone clients, says Ratis is used for writing data and Standalone/gRPC for reading, and points to `XceiverClientManager` and `XceiverClientSpi`.

Control flow: Not applicable.

State and persistence behavior: Documentation-only source.

Dependencies and integration points: Provides context for the classes in `org.apache.hadoop.hdds.scm`, including `XceiverClientRatis`, `XceiverClientGrpc`, `XceiverClientManager`, and metrics/config classes.

Risks: The text is somewhat dated because EC and datastream paths add nuance beyond simple Ratis-write/Standalone-read framing.

Test signals: Compile/Javadoc generation only.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/AbstractCommitWatcher.java -->
# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/AbstractCommitWatcher.java

Purpose: Shared commit-watch helper for write streams. It watches Ratis commit indexes and releases associated buffers once data has replicated sufficiently.

Important APIs/types/functions: `updateCommitInfoMap` associates commit indexes with buffers. `watchOnFirstIndex` and `watchOnLastIndex` watch the lowest or highest pending index. `watchForCommitAsync` deduplicates in-flight watch requests per index. `adjustBuffers` releases buffers for indexes up to the committed index. Subclasses implement `releaseBuffers(long)`. `totalAckDataLength` tracks acknowledged data length.

Control flow: When a watch is requested, a memoized future is inserted in `replies` only if absent. The client's `watchForCommit` future completes the shared future, removes it from the reply cache, and adjusts buffers based on returned log index. Synchronous `watchForCommit` wraps interruptions/execution failures as IOExceptions and releases buffers up to the client's replicated minimum.

State and persistence behavior: Holds a concurrent sorted commit-index-to-buffer map, a concurrent reply-future cache, the xceiver client, and ack length counter. State is in-memory and cleared by `cleanup`.

Dependencies and integration points: Used by stream output implementations such as `BlockDataStreamOutput` through concrete watchers. Depends on `XceiverClientSpi.watchForCommit`.

Risks: `adjustBuffers` streams over `commitIndexMap.keySet()` while `releaseBuffers` likely removes entries; concurrent map semantics make this possible, but subclass side effects need care. Failed watches may release only up to replicated minimum, leaving buffers for retry paths. Duplicate watch future handling relies on strict removal identity.

Test signals: Tests should cover duplicate watch coalescing, first/last index behavior, buffer release ordering, exception release behavior, and cleanup.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/AbstractCommitWatcher.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/AbstractDataStreamOutput.java -->
# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/AbstractDataStreamOutput.java

Purpose: Base class for datastream output implementations that need common retry/error handling.

Important APIs/types/functions: Extends `ByteBufferOutputStream`. Stores retry policy map, retry count, and exception flag. `checkForRetryFailure` identifies Ratis retry/closed failures. `checkIfContainerToExclude` identifies `StorageContainerException`. `handleRetry` selects a retry policy using `HddsClientUtils.checkForException` and enforces sleep/fail behavior. `setExceptionAndThrow` marks the stream exceptional and throws.

Control flow: On retryable IOExceptions, subclasses call `handleRetry`; it asks the selected Hadoop `RetryPolicy` whether to retry or fail. Failures are wrapped as IOExceptions and mark the stream as exceptional. Retry decisions with delay sleep the current thread, handling interruption by re-interrupting and throwing `InterruptedIOException`.

State and persistence behavior: Per-stream in-memory retry count and exception flag. No persistence.

Dependencies and integration points: Used by concrete Ozone datastream outputs. Integrates with Hadoop retry APIs, Ratis exceptions, and storage container exceptions.

Risks: Retry count is shared for all exception types unless subclasses reset it. If `HddsClientUtils.checkForException(exception)` returns a cause class not present in the map, it falls back to generic `Exception`. Thread interruption converts to permanent exception state.

Test signals: Tests should cover retry success with and without delay, fail decisions, interruption, exception classification, and retry-count reset.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/AbstractDataStreamOutput.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/BlockDataStreamOutput.java -->
# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/BlockDataStreamOutput.java

Purpose: ByteBuffer stream output for writing an Ozone block through Ratis datastream, tracking chunks, checksums, putBlock metadata, commit watches, and client cleanup.

Important APIs/types/functions: Constructor acquires a topology-aware `XceiverClientRatis`, initializes a datastream via `StreamInit`, sets up checksum and response executor, and creates `StreamCommitWatcher`. `write` fills `StreamBuffer`s, writes full buffers as datastream chunks, and triggers flush/putBlock by configured boundaries. `executePutBlock` sends metadata through both datastream close compatibility path and `putBlockAsync`. `watchForCommit`, `flush`, `hflush`, `hsync`, `close`, `cleanup`, and retry/write helpers manage lifecycle. Static `executePutBlockClose` and `getProtoLength` write close metadata over datastream.

Control flow: Writes allocate packet-sized buffers, copy incoming ByteBuffer ranges, compute chunk checksum/metadata, and call `DataStreamOutput.writeAsync`, optionally with `SYNC`. When flush boundary is reached, it updates flushed length and queues an async putBlock; when window is full, it waits for the oldest putBlock and watches the first commit index to release buffers. Close flushes remaining data, forces an EOF putBlock if needed, waits for datastream close reply, and releases the xceiver client.

State and persistence behavior: Maintains block ID, block data builder/chunk list, acquired client/factory, chunk index/offset, buffer lists, pending futures, failed servers, checksum, token string, datastream output, sync position, and exception reference. Persistent effects are datanode chunk writes and committed block metadata.

Dependencies and integration points: Integrates Ratis datastream, container protocol calls, `XceiverClientManager`, `OzoneClientConfig`, checksum code, tokens, pipelines, metrics, and commit watcher behavior.

Risks: `hsync` swallows all exceptions, which may hide failed durability operations. `dataStreamCloseReply.get()` in `close` assumes `executePutBlock(true, ...)` initialized the future. Single-thread response executor serializes completions; shutdown is not awaited. Error state is first-writer-wins, so later root causes may be suppressed. Compatibility double putBlock during close must remain aligned with datanode behavior.

Test signals: Tests should cover chunk metadata/checksum generation, flush boundaries, stream window backpressure, putBlock failure propagation, close compatibility path, sync-size `SYNC` writes, retry write path, client invalidation cleanup, and hsync error handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/BlockDataStreamOutput.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/BlockExtendedInputStream.java -->
# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/BlockExtendedInputStream.java

Purpose: Abstract base for block input streams in Ozone. It provides common remaining-length, pipeline normalization, read retry, block-location refresh, and connectivity-check helpers.

Important APIs/types/functions: Abstract methods include `getBlockID`, `getLength`, and `getPos`. `getRemaining` computes unread bytes. `setPipeline` validates EC replica index consistency and converts non-standalone/non-EC pipelines to read copies. `shouldRetryRead` applies a Hadoop retry policy and sleeps for configured delays. `getReadRetryPolicy` derives retry policy from `OzoneClientConfig`. `refreshBlockInfo` re-fetches pipeline and token using a supplied function. `isConnectivityIssue` detects gRPC `UNAVAILABLE`.

Control flow: Read implementations call these helpers when opening or retrying reads. On refresh, the method logs the old pipeline, invokes the refresh function, updates pipeline and token references when a new location is returned, and logs token expiry by decoding `OzoneBlockTokenIdentifier`.

State and persistence behavior: The abstract class owns no fields. It mutates caller-supplied `AtomicReference<Pipeline>` and `AtomicReference<Token<...>>`.

Dependencies and integration points: Used by concrete block input streams. Integrates block location refresh, Ozone block tokens, gRPC status mapping, and client read retry config.

Risks: `refreshBlockInfo` logs `pipelineRef.get().getId()` before checking for null, so null pipeline references can fail. `setPipeline` rejects pipelines with mixed replica indexes, important for EC correctness. `isConnectivityIssue` relies on `Status.fromThrowable(IOException)`, which may not unwrap all causes.

Test signals: Tests should cover remaining calculation, pipeline conversion, mixed replica-index rejection, retry sleep/fail behavior, refresh success/null/no-function cases, token expiry logging, and connectivity exception detection.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/BlockExtendedInputStream.java -->
