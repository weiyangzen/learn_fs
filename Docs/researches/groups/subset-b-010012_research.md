# subset-b-010012 research

Grouped research for Samba WINS replication service setup and SMBJ build, CI, integration-test, DFS, security descriptor, ACE, NTSTATUS, and MS-FSCC source files. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/wrepl_server/wrepl_server.c -->
# sources/user-network-fs/samba/source4/wrepl_server/wrepl_server.c

Source read signal: reviewed complete local file (558 lines, 15982 bytes).

## Purpose
`wrepl_server.c` is the Samba4 WINS Replication service bootstrap and shared partner/table management implementation. It opens the local WINS database and WREPL configuration database, loads configured replication partners, builds the owner/version table from existing WINS records, schedules pull and push processing, starts the inbound replication listener, and registers the task as the `wrepl` server service.

## Important APIs, types, and functions
Key local helpers are `wins_config_db_connect()`, `wins_config_db_get_seqnumber()`, `wreplsrv_open_winsdb()`, `wreplsrv_find_attr_as_uint32()`, `wreplsrv_load_partners()`, `wreplsrv_load_table()`, `wreplsrv_setup_partners()`, `wreplsrv_setup_sockets()`, `wreplsrv_task_init()`, and `server_service_wrepl_init()`. Exported service helpers include `wreplsrv_find_partner()`, `wreplsrv_fill_wrepl_table()`, `wreplsrv_find_owner()`, and `wreplsrv_add_table()`. The code fills `struct wreplsrv_service`, `struct wreplsrv_partner`, and `struct wreplsrv_owner` fields declared in the companion header and hands off protocol work to the other WREPL server modules through generated prototypes.

## Control flow
`server_service_wrepl_init()` registers a non-preforking service whose `task_init` is `wreplsrv_task_init()`. Startup rejects hosts that are not configured as WINS servers, allocates `struct wreplsrv_service`, opens `wins.ldb` with a local-owner address selected from `winsdb:local_owner` or the first IPv4 interface, opens `wins_config.ldb`, reads interval defaults from `wreplsrv:*` smb.conf parameters, loads partners, loads the WINS owner table, sets up pull/push timers, listens on WREPL sockets from `dcerpc_endpoint_servers:winsrepl`, starts periodic scavenging/maintenance, and registers the IRPC name `wrepl_server`.

## State and persistence
Persistent state lives in `wins.ldb` and `wins_config.ldb`. The in-memory service caches the configuration database sequence number, partner linked list, owner table, local owner pointer, timers, incoming connections, and scavenging flags. `wreplsrv_load_partners()` uses `@BASEINFO sequenceNumber` to skip reloads when partner configuration has not changed, disables existing partners before reapplying database rows, and forces pull rescheduling when an existing partner is updated. `wreplsrv_add_table()` may advance the local WINS max version in the database when a higher local version is observed.

## Dependencies and integration points
The file depends on Samba task services, talloc, tevent, LDB, the WINS database API, generated `winsrepl` NDR types, `dlinklist`, IRPC messaging, auth/system sessions, loadparm, network interface discovery, and WREPL helper modules for socket, periodic, pull, push, and scavenging behavior. It integrates with `source4/wscript_build` through the `service_wrepl` module and with `wrepl_server/wscript_build` for the private `WREPL_SRV` subsystem.

## Risks
Partner parsing is trust-boundary adjacent: malformed LDB values fall back or fail, and `wreplsrv_find_attr_as_uint32()` accepts decimal and hex forms through signed/unsigned conversions. The configuration reload path marks all partners disabled first, so a partial failure leaves old in-memory partner objects with `type = NONE` until a later successful reload. Local-owner selection depends on interface ordering when `winsdb:local_owner` is absent. `wreplsrv_load_table()` scans all WINS records and updates max-version state; database corruption or unexpected owner/version values can affect replication decisions. Socket setup requires exactly one valid WINSREPL endpoint server.

## Test signals
Useful tests cover startup when WINS is disabled, absent or invalid `wins_config.ldb`, partner sequence-number no-op reloads, add/update/remove partner rows, decimal and hex partner type parsing, `0.0.0.0` owner normalization, local max-version advancement, endpoint configuration errors, and scheduled pull/push/periodic events after startup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/wrepl_server/wrepl_server.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/wrepl_server/wrepl_server.h -->
# sources/user-network-fs/samba/source4/wrepl_server/wrepl_server.h

Source read signal: reviewed complete local file (321 lines, 8056 bytes).

## Purpose
`wrepl_server.h` is the shared private interface for Samba's WINS Replication server. It defines the service-wide state object, incoming/outgoing connection state, partner configuration/runtime state, WINS owner table entries, default timing constants, association-context constants, and includes the generated WREPL server prototypes used across the implementation files.

## Important APIs, types, and functions
Important declarations are `WREPLSRV_VALID_ASSOC_CTX`, `WREPLSRV_INVALID_ASSOC_CTX`, `enum winsrepl_partner_type`, `WINSREPL_DEFAULT_PULL_INTERVAL`, `WINSREPL_DEFAULT_PULL_RETRY_INTERVAL`, and `WINSREPL_DEFAULT_PUSH_CHANGE_COUNT`. Core structs are `wreplsrv_in_call`, `wreplsrv_in_connection`, `wreplsrv_out_connection`, `wreplsrv_partner`, `wreplsrv_owner`, and `wreplsrv_service`. The header pulls in `wrepl_out_helpers.h` and generated `wrepl_server_proto.h`, making it the module boundary for other WREPL server source files.

## Control flow
There is no executable control flow in the header, but it encodes lifecycle relationships. A `wreplsrv_service` belongs to one `task_server` and owns database handles, connection lists, partner lists, owner tables, periodic timers, and scavenging state. Incoming calls attach to an inbound connection and carry parsed request/reply packets plus input/output blobs. Outgoing connections attach to a partner and hold a WREPL socket plus association-context negotiation state. Pull and push substructures inside each partner record hold timers, retry/error counters, current composite requests, and per-cycle IO state.

## State and persistence
All structs are in-memory task state, normally talloc-owned by the service or connection. Persistent database handles are referenced through `wins_db` and `config.ldb`; timers and outstanding requests are transient tevent/composite state. Partner state records the configured address/name/source address, type, pull intervals, retry status, push max-version sent to the partner, and whether push notifications use inform messages. Owner state mirrors WREPL owner/version rows and links owners back to configured partners when possible.

## Dependencies and integration points
The header depends on Samba network types, WINS replication generated packet structs, stream/tstream/tevent/composite abstractions, WINS database handles, and helper headers. It is consumed by the WREPL inbound call/connection, outbound helper/pull/push, periodic, scavenging, and server bootstrap code.

## Risks
Because this is a shared private header, layout changes affect many modules at once. Association context constants must remain synchronized with protocol handling. Pull and push nested state mixes configuration, last error state, timer handles, and active composite requests; ownership or cancellation changes need careful review. The header lacks include guards in this snapshot and relies on normal project include behavior.

## Test signals
Build coverage of all WREPL server modules is the primary signal. Runtime tests should observe that partner timers, push notifications, association contexts, inbound connection shutdown, and owner-table updates still operate after any struct or constant change.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/wrepl_server/wrepl_server.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/wrepl_server/wscript_build -->
# sources/user-network-fs/samba/source4/wrepl_server/wscript_build

Source read signal: reviewed complete local file (11 lines, 417 bytes).

## Purpose
This Waf build fragment defines Samba's private `WREPL_SRV` subsystem for the `source4/wrepl_server` directory. It gathers the WINS replication server implementation files into one internal library-like component.

## Important APIs, types, and functions
The only build API is `bld.SAMBA_SUBSYSTEM('WREPL_SRV', ...)`. The source list includes `wrepl_server.c`, inbound connection/call handling, outbound helper/pull/push code, record application, periodic processing, and scavenging. Public dependency declarations include `LIBCLI_WREPL`, `WINSDB`, `process_model`, `DCERPC_COMMON`, `LIBCLI_RESOLVE`, `LIBCLI_NBT`, `samba-hostconfig`, `ldb`, and `events`.

## Control flow
There is no runtime control flow. During configure/build, Waf uses this fragment to compile the listed C files and link the resulting subsystem into higher-level Samba service modules.

## State and persistence
The file has no runtime state. Its persistent effect is build graph state: the exact object list and dependency set that make WREPL server code available.

## Dependencies and integration points
It integrates with the parent `source4/wscript_build`, which references `WREPL_SRV` from `service_wrepl`. It also declares the protocol, database, process model, resolver, NBT, hostconfig, LDB, and event dependencies the source files need.

## Risks
The source list must stay synchronized with generated prototypes and service module references. Missing a new source file can produce unresolved symbols; keeping a removed source can break builds. Dependency under-declaration can hide until non-unified or minimal builds.

## Test signals
Run the Samba Waf build for the `service_wrepl` module or all of source4. Link errors around WREPL symbols and missing headers are the key signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/wrepl_server/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/wscript_build -->
# sources/user-network-fs/samba/source4/wscript_build

Source read signal: reviewed complete local file (18 lines, 596 bytes).

## Purpose
This parent Samba4 Waf fragment wires top-level source4 server modules and subsystem directories into the build. For this research item its relevant role is including the WREPL server subdirectory and declaring the `service_wrepl` server module.

## Important APIs, types, and functions
It calls `bld.RECURSE()` for many source4 subdirectories including `wrepl_server`, and defines `bld.SAMBA_MODULE('service_wrepl', ...)` with `subsystem='service'`, `source='wrepl_server/service_wrepl.c'`, `deps='WREPL_SRV process_model'`, and `internal_module=False`. This exposes WREPL through Samba's service subsystem.

## Control flow
There is no runtime flow. Build-time flow recurses into component directories, then creates service modules such as LDAP, CLDAP, web, KDC, DNS, winbind, NBT, WREPL, KCC, DNS update, DNS query, RODC, and DREPL.

## State and persistence
The build graph is the only state. The `service_wrepl` declaration persists the relationship between the service loader and the private `WREPL_SRV` subsystem.

## Dependencies and integration points
The file is consumed by Samba's Waf build and service module registration. WREPL depends on the recursively built `wrepl_server` subsystem plus `process_model`.

## Risks
Removing the `wrepl_server` recursion or changing the `service_wrepl` dependency breaks WINS replication service availability even if the C files compile in isolation. Service module naming must match runtime registration expectations.

## Test signals
Build source4 and verify the `service_wrepl` module links. Runtime startup of Samba configured as a WINS server should reach `server_service_wrepl_init()`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/.bettercodehub.yml -->
# sources/user-network-fs/smbj/.bettercodehub.yml

Source read signal: reviewed complete local file (6 lines, 71 bytes).

## Purpose
`.bettercodehub.yml` covers Better Code Hub configuration. sets component-depth to 1 and excludes `src/test`, `src/it`, `src/main/java/com/hierynomus/protocol/transport`, `src/main/java/com/hierynomus/security`, and `.github` from analysis.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
There is no runtime flow; the external scanner reads this YAML to scope quality metrics.

## State and persistence
State is limited to repository quality-policy metadata.

## Dependencies and integration points
It integrates only with Better Code Hub.

## Risks
Broad exclusions can hide complexity in security and transport packages, while a shallow component depth can make package-level architecture signals coarse.

## Test signals
Run the Better Code Hub scan and compare included/excluded paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/.bettercodehub.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/.github/workflows/codeql-analysis.yml -->
# sources/user-network-fs/smbj/.github/workflows/codeql-analysis.yml

Source read signal: reviewed complete local file (70 lines, 2398 bytes).

## Purpose
`codeql-analysis.yml` covers GitHub CodeQL workflow. runs Java CodeQL analysis on pushes and pull requests to `master` plus a weekly Wednesday cron, using checkout v3, CodeQL init v2, autobuild, and analyze.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
GitHub Actions checks out full history, initializes the Java language database, lets CodeQL autobuild the Gradle project, then uploads analysis.

## State and persistence
No application state; results persist in GitHub code scanning alerts.

## Dependencies and integration points
Integrates with GitHub Actions, CodeQL, and the Java/Gradle build.

## Risks
Autobuild may miss custom integration-test or release build paths; action versions are pinned to older major versions; only Java is scanned.

## Test signals
Signals are successful workflow runs and populated CodeQL alerts on changed Java code.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/.github/workflows/codeql-analysis.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/.github/workflows/gradle.yml -->
# sources/user-network-fs/smbj/.github/workflows/gradle.yml

Source read signal: reviewed complete local file (51 lines, 1353 bytes).

## Purpose
`gradle.yml` covers SMBJ CI workflow. runs `./gradlew check` on Java 11 and then `./gradlew integrationTest` on Ubuntu for pushes and PRs targeting `master`.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
The integration job depends on the Java 11 build job, reuses Gradle cache, and relies on Docker/Testcontainers availability on `ubuntu-latest`.

## State and persistence
No runtime state except Gradle caches and CI artifacts/logs.

## Dependencies and integration points
Integrates GitHub Actions, setup-java Zulu 11, Gradle wrapper, Docker/Testcontainers, and the Gradle `check`/`integrationTest` tasks.

## Risks
Cache keys use only Gradle files, so wrapper or dependency-lock changes outside that pattern may be missed. The workflow does not chmod `gradlew`, assuming executable mode is preserved.

## Test signals
Passing Java 11 unit checks and container-backed integration tests are the main test signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/.github/workflows/gradle.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/.github/workflows/release.yml -->
# sources/user-network-fs/smbj/.github/workflows/release.yml

Source read signal: reviewed complete local file (51 lines, 1365 bytes).

## Purpose
`release.yml` covers SMBJ release workflow. publishes artifacts to Sonatype when a `v*` tag is pushed, after a Java 12 `./gradlew check` gate.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
A build job checks out full history, sets up Zulu 12, chmods `gradlew`, and runs checks. The release job repeats checkout/setup and runs `clean publishToSonatype closeAndReleaseSonatypeStagingRepository` with signing and OSSRH secrets.

## State and persistence
Persistent state is external: Maven Central/Sonatype staging repositories, GitHub release permissions, and signed artifacts.

## Dependencies and integration points
Integrates GitHub Actions, Gradle publishing/signing, axion release version tags, Nexus Publish, and Sonatype credentials.

## Risks
Java 12 is dated and can diverge from CI's Java 11 coverage. A tag push can publish if secrets are present; failed staging close may need manual cleanup.

## Test signals
Signals are a passing tagged workflow, signed source/javadoc/binary jars, and a released Sonatype staging repository.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/.github/workflows/release.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/build.gradle -->
# sources/user-network-fs/smbj/build.gradle

Source read signal: reviewed complete local file (238 lines, 6085 bytes).

## Purpose
`build.gradle` covers SMBJ Gradle build. defines a Java/Groovy library with Jacoco, license checks, Maven publishing/signing, axion-release versioning, GitHub metadata, Nexus publishing, and a `jvm-test-suite` integration-test suite under `src/it`.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Default task is `build`; `check` depends on Jacoco; `release` depends on integration tests and build. Unit and integration suites use JUnit Jupiter with common dependencies, and integration tests add Testcontainers, logback, and commons-compress.

## State and persistence
Build state includes generated version from SCM tags, Gradle caches, Jacoco reports, signed Maven publications, and Sonatype staging operations.

## Dependencies and integration points
Integrates SLF4J, Bouncy Castle, MBassador, ASN.1 helpers, Mockito, AssertJ, Spock, Testcontainers, Logback, license plugin, Maven Publish, Signing, Nexus Publish, and GitHub info plugins.

## Risks
Transitive implementation dependencies are disabled globally, so missing explicit dependencies can appear at runtime. The jar manifest has a misspelled `Implenentation-Title`. Release behavior depends on tag-derived versioning and secrets.

## Test signals
Run `./gradlew check`, `./gradlew integrationTest`, `./gradlew publishToMavenLocal`, and inspect Jacoco/license output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/build.gradle -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/gradlew -->
# sources/user-network-fs/smbj/gradlew

Source read signal: reviewed complete local file (160 lines, 4971 bytes).

## Purpose
`gradlew` covers Gradle wrapper launcher. is the POSIX shell wrapper that locates Java, resolves `gradle-wrapper.jar`, normalizes paths under Cygwin/MSYS/Darwin/NonStop, sets JVM options, and invokes `org.gradle.wrapper.GradleWrapperMain`.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
The script parses app-relative paths, validates `java`, builds an argument array, escapes paths for Windows-like shells, then execs Java with wrapper classpath and user arguments.

## State and persistence
No project runtime state; it uses environment variables such as `JAVA_HOME`, `DEFAULT_JVM_OPTS`, `GRADLE_OPTS`, and `JAVA_OPTS`.

## Dependencies and integration points
Integrates with the checked-in Gradle wrapper jar/properties and shell environments used by CI and developers.

## Risks
Wrapper correctness depends on executable bits, matching wrapper jar, and shell portability. Environment options can change memory/daemon behavior.

## Test signals
Signals are `./gradlew --version`, CI `./gradlew check`, and successful use on Linux/macOS/Windows compatibility shells.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/gradlew -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/settings.gradle -->
# sources/user-network-fs/smbj/settings.gradle

Source read signal: reviewed complete local file (1 lines, 26 bytes).

## Purpose
`settings.gradle` covers Gradle settings. sets the root project name to `smbj`.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Gradle reads it before project evaluation to name publications, tasks, and build scans.

## State and persistence
No runtime state.

## Dependencies and integration points
Integrates with Gradle project identity and build.gradle's publication metadata.

## Risks
Changing the name affects artifact/module naming and automatic module name composition.

## Test signals
Run `./gradlew projects` or inspect publication coordinates.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/settings.gradle -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/it/docker-image/Dockerfile -->
# sources/user-network-fs/smbj/src/it/docker-image/Dockerfile

Source read signal: reviewed complete local file (23 lines, 711 bytes).

## Purpose
`Dockerfile` covers integration-test Samba image. builds an Alpine-based image with tini, Samba, supervisor, bash, a configured `smbj` user, public/user/readonly/dfs directories, copied Samba config, and exposed SMB/NetBIOS ports.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Build flow installs packages, copies configs, adds seed public data, creates directories with permissive modes, creates the Samba user/passdb entry, marks the entrypoint executable, then starts supervisord through tini.

## State and persistence
Container filesystem state includes `/opt/samba/share`, `/opt/samba/user`, `/opt/samba/readonly`, `/opt/samba/dfs`, `/etc/samba/smb.conf`, and the Samba passdb.

## Dependencies and integration points
Used by integration tests and mirrored programmatically by `SambaContainer.Builder`, though the builder uses a newer Alpine base.

## Risks
The static Dockerfile and Java builder can drift. Alpine/Samba package changes affect DFS and auth behavior. Permissive modes are intentional for tests but unsuitable for production.

## Test signals
Signals are successful image build, smbd/nmbd startup, and passing Testcontainers integration tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/it/docker-image/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/it/docker-image/entrypoint.sh -->
# sources/user-network-fs/smbj/src/it/docker-image/entrypoint.sh

Source read signal: reviewed complete local file (26 lines, 690 bytes).

## Purpose
`entrypoint.sh` covers Samba integration entrypoint. sets default SMB credentials and creates DFS symlinks under `/opt/samba/dfs` before execing the container command.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
It currently hard-codes `ip_address=127.0.0.1`, creates links for `public`, `user`, and `firstfail-public`, then `exec`s supervisord or the passed command.

## State and persistence
Persistent container state is the created msdfs symlinks; credentials are environment defaults consumed earlier by image creation.

## Dependencies and integration points
Integrates with Samba's `msdfs root` share and DFS integration tests that expect working and fallback links.

## Risks
The hard-coded loopback address assumes Samba resolves links from inside the test topology. Re-running can fail if symlinks already exist unless the filesystem is fresh.

## Test signals
Signals are DFS share listings containing `public`, `user`, and fallback behavior for `firstfail-public`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/it/docker-image/entrypoint.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/it/docker-image/smb.conf -->
# sources/user-network-fs/smbj/src/it/docker-image/smb.conf

Source read signal: reviewed complete local file (62 lines, 1189 bytes).

## Purpose
`smb.conf` covers Samba test configuration. defines a standalone user-security Samba server with guest mapping, Japanese DOS charset CP932, high auth logging, MSDFS host support, and `public`, `readonly`, `user`, and `dfs` shares.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Samba reads global options at daemon start and serves shares from `/opt/samba/*`; the `dfs` share is read-only, public, guest-ok, and marked `msdfs root = yes`.

## State and persistence
State lives in Samba TDB passdb, share directories, logs under `/var/log/samba.log`, and DFS symlink targets.

## Dependencies and integration points
Consumed by smbd/nmbd in the Docker image and by all smbj integration tests.

## Risks
The `interfaces = 192.168.2.0/24 eth0` plus `bind interfaces only = yes` is topology-sensitive. Guest-only public access and permissive create modes are test-specific.

## Test signals
Signals are authenticated access to `user`, anonymous access to `public`, denied writes to `readonly`, and working DFS referrals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/it/docker-image/smb.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/it/docker-image/supervisord.conf -->
# sources/user-network-fs/smbj/src/it/docker-image/supervisord.conf

Source read signal: reviewed complete local file (14 lines, 397 bytes).

## Purpose
`supervisord.conf` covers test container process supervisor config. runs `smbd --daemon --foreground --configfile=/etc/samba/smb.conf` and `nmbd --daemon --foreground` with supervisord in the foreground.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Supervisord starts both Samba daemons and keeps the container alive; tini is PID 1 in the Dockerfile/builder.

## State and persistence
No application state, only supervisor process and logs.

## Dependencies and integration points
Integrates with the container entrypoint and Testcontainers wait-for-port behavior.

## Risks
If smbd forks unexpectedly or exits after binding, the listening-port wait can be insufficient to prove share readiness. nmbd failures may be less visible.

## Test signals
Signals are container logs, port 445 listening, and successful SMB session establishment.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/it/docker-image/supervisord.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/it/java/com/hierynomus/smbj/AnonymousIntegrationTest.java -->
# sources/user-network-fs/smbj/src/it/java/com/hierynomus/smbj/AnonymousIntegrationTest.java

Source read signal: reviewed complete local file (104 lines, 5279 bytes).

## Purpose
`AnonymousIntegrationTest.java` covers anonymous/guest SMB integration tests. parameterized tests authenticate with `AuthenticationContext.anonymous()`, verify signing-required failure, and connect to the guest `public` share.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Each test uses `SambaContainer.INSTANCE`, `withConnectedClient()`, or manual `SMBClient` connection, then asserts session IDs, guest signing exceptions, and `DiskShare` tree state.

## State and persistence
State is limited to live SMB sessions/tree connects against the container.

## Dependencies and integration points
Depends on Testcontainers, JUnit Jupiter parameter sources from `TestingUtils`, SMB dialect/sign/encrypt config variants, and `SambaContainer`.

## Risks
Guest auth behavior is sensitive to Samba `map to guest`, signing policy, and dialect negotiation.

## Test signals
Passing tests signal anonymous login, expected signing enforcement, and guest share connectivity.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/it/java/com/hierynomus/smbj/AnonymousIntegrationTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/it/java/com/hierynomus/smbj/ChangeNotifyIntegrationTest.java -->
# sources/user-network-fs/smbj/src/it/java/com/hierynomus/smbj/ChangeNotifyIntegrationTest.java

Source read signal: reviewed complete local file (105 lines, 5523 bytes).

## Purpose
`ChangeNotifyIntegrationTest.java` covers SMB2 change notify integration tests. verifies directory watch notifications for file creation and cancellation of an outstanding notify request.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
The watch test opens a directory, issues recursive `watch()`, creates a file, waits for the future, and asserts `FILE_ACTION_ADDED` plus file name. The cancel test sends a watch with `send()`, cancels it, and expects an empty notify list.

## State and persistence
Uses transient files/directories in the `user` share and asynchronous futures.

## Dependencies and integration points
Depends on `DiskShare`, `Directory.watch`, SMB2 completion/cancel behavior, `FileNotifyAction`, and the Samba container.

## Risks
Timing can be flaky if creation races with watch registration or cancellation. Samba behavior for canceled notify responses is part of the contract.

## Test signals
Signals are prompt future completion with one notify item and successful cancel returning an empty response.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/it/java/com/hierynomus/smbj/ChangeNotifyIntegrationTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/it/java/com/hierynomus/smbj/DfsIntegrationTest.java -->
# sources/user-network-fs/smbj/src/it/java/com/hierynomus/smbj/DfsIntegrationTest.java

Source read signal: reviewed complete local file (99 lines, 4769 bytes).

## Purpose
`DfsIntegrationTest.java` covers DFS share integration tests. validates smbj DFS resolution against the container's `dfs` share, including virtual directory listing, broken-first-target fallback, and filename preservation for normal shares when DFS is enabled.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Tests use `TestingUtils#dfsConfig`, connect to `dfs`, list links, open DFS directories through helper `withDir()`, and assert regular share directory path/name/UNC fields.

## State and persistence
State comes from DFS symlinks created by the entrypoint and temporary directory handles.

## Dependencies and integration points
Depends on the MSDFS-enabled Samba config, `SambaContainer`, `Directory`, `DiskShare`, DFS client path rewriting, and file information listings.

## Risks
DFS target hostnames/loopback choices are environment-sensitive. Fallback behavior relies on a reserved unreachable address followed by a good target.

## Test signals
Signals are listed DFS links, successful fallback listing, and unchanged regular-share `getFileName()`/UNC behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/it/java/com/hierynomus/smbj/DfsIntegrationTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/it/java/com/hierynomus/smbj/IntegrationTest.java -->
# sources/user-network-fs/smbj/src/it/java/com/hierynomus/smbj/IntegrationTest.java

Source read signal: reviewed complete local file (112 lines, 5289 bytes).

## Purpose
`IntegrationTest.java` covers basic SMB integration tests. covers connection, authentication, share connection, listing empty shares with empty or null paths, disabled signing configuration, and idempotent connection close.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Parameterized tests open clients through `SambaContainer`, authenticate with default credentials, connect to `user`, and assert tree IDs, connected flags, and `.`/`..` directory entries.

## State and persistence
Runtime state is live connection/session/tree state and the empty `user` share.

## Dependencies and integration points
Depends on `SMBClient`, `Connection`, `Session`, `DiskShare`, `SmbConfig`, and container auth setup.

## Risks
Assertions about exact empty-share size depend on Samba listing `.` and `..` and no leftover files from other tests.

## Test signals
Signals are successful session establishment and clean list/close behavior across default config variants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/it/java/com/hierynomus/smbj/IntegrationTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/it/java/com/hierynomus/smbj/SMB2DirectoryIntegrationTest.java -->
# sources/user-network-fs/smbj/src/it/java/com/hierynomus/smbj/SMB2DirectoryIntegrationTest.java

Source read signal: reviewed complete local file (143 lines, 7238 bytes).

## Purpose
`SMB2DirectoryIntegrationTest.java` covers SMB2 directory integration tests. checks opening directories, folder-exists semantics, directory listing, delete-pending handling for rmdir/folderExists, and creating/listing a new directory.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Tests connect to `public` or `user`, use `openDirectory`, `folderExists`, `rmdir`, `deleteOnClose`, `mkdir`, and `list` assertions.

## State and persistence
State is temporary directories and files in the `user` share plus seeded public folder data.

## Dependencies and integration points
Depends on SMB2 create dispositions, access masks, share access, directory information parsing, and Samba delete-pending responses.

## Risks
Delete-pending behavior is server-specific. Cleanup must remove created directories or later empty-share tests can fail.

## Test signals
Signals are correct `Directory` instances, folder/file distinction, stable listing, and no exceptions for delete-pending cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/it/java/com/hierynomus/smbj/SMB2DirectoryIntegrationTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/it/java/com/hierynomus/smbj/SMB2FileIntegrationTest.java -->
# sources/user-network-fs/smbj/src/it/java/com/hierynomus/smbj/SMB2FileIntegrationTest.java

Source read signal: reviewed complete local file (463 lines, 24680 bytes).

## Purpose
`SMB2FileIntegrationTest.java` covers SMB2 file integration tests. exercises opening, creating, checking existence, nested reads, share-mode locking, large transfer, byte-range locks, file ID lookup, append, server-side remote copy, delete-pending handling, async writes, and stream-based gzip/unzip transfer.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Tests use `DiskShare.openFile`, `File.write`, input/output streams, `ArrayByteChunkProvider`, `InputStreamByteChunkProvider`, `requestLock()`, remote copy, `deleteOnClose`, futures, and `endOfFile()` comparisons.

## State and persistence
State includes temporary files in `user`, seeded files in `public`, large random byte arrays, temp local gzip files, locks, and pending asynchronous write operations.

## Dependencies and integration points
Depends on access masks, share access, create dispositions, SMB status mapping, directory/file information classes, Apache Commons IO, Java streams, and the Samba container.

## Risks
Large transfer and async tests are timing/resource sensitive. Sharing-violation expectations depend on server lock/share-mode implementation. Temp-file cleanup occurs in `finally` for gzip tests.

## Test signals
Signals are byte-for-byte reads, matching file IDs, expected `STATUS_SHARING_VIOLATION`, successful locks/unlocks, completed async writes, and matching unzipped data.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/it/java/com/hierynomus/smbj/SMB2FileIntegrationTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/it/java/com/hierynomus/smbj/testcontainers/ExecutionFailedException.java -->
# sources/user-network-fs/smbj/src/it/java/com/hierynomus/smbj/testcontainers/ExecutionFailedException.java

Source read signal: reviewed complete local file (24 lines, 873 bytes).

## Purpose
`ExecutionFailedException.java` covers Testcontainers exec failure exception. wraps a failed container exec exit code in a runtime exception used by `SambaContainer.ensureOk()`.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Constructed when helper commands such as `mkdir`, `chmod`, or `rm` return non-zero.

## State and persistence
No persistent state beyond the exit code in the message/field.

## Dependencies and integration points
Integrates with Testcontainers `execInContainer` helper methods.

## Risks
Only exit code is captured, so stderr/stdout context can be lost.

## Test signals
Signals are helper tests or integration setup failures surfacing a clear non-zero exit.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/it/java/com/hierynomus/smbj/testcontainers/ExecutionFailedException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/it/java/com/hierynomus/smbj/testcontainers/SambaContainer.java -->
# sources/user-network-fs/smbj/src/it/java/com/hierynomus/smbj/testcontainers/SambaContainer.java

Source read signal: reviewed complete local file (180 lines, 7084 bytes).

## Purpose
`SambaContainer.java` covers Testcontainers Samba fixture. builds and runs the Samba image, exposes port 445, provides authenticated/connected SMB client helpers, URI helpers, container file operations, and debug logging setup.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
The singleton builds an image from `src/it/docker-image`, starts smbd/nmbd, waits for the port, then tests call wrappers that open `SMBClient`, `Connection`, and `Session` objects around callbacks.

## State and persistence
State includes one shared container, fixed host port 445 mapping, generated Docker image, share files, logs, and temporary files manipulated by tests.

## Dependencies and integration points
Depends on Testcontainers, Dockerfile builder, Logback, SMBJ client/session APIs, and `TestingUtils` credentials.

## Risks
Fixed exposed port 445 can conflict on developer/CI hosts. The Java builder's Alpine version can drift from the Dockerfile. Helper failures drop command output.

## Test signals
Signals are successful image build/start, SMB connection/auth helper success, and container file helper correctness.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/it/java/com/hierynomus/smbj/testcontainers/SambaContainer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/it/java/com/hierynomus/smbj/testing/LoggingProgressListener.java -->
# sources/user-network-fs/smbj/src/it/java/com/hierynomus/smbj/testing/LoggingProgressListener.java

Source read signal: reviewed complete local file (31 lines, 1081 bytes).

## Purpose
`LoggingProgressListener.java` covers test progress logger. implements an SMBJ progress listener that logs transfer progress during integration tests.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Callback methods receive byte counts or progress events and emit them through SLF4J.

## State and persistence
No persistent state beyond logger use.

## Dependencies and integration points
Integrates with SMBJ IO transfer APIs and test logging.

## Risks
High-frequency progress logging can make large-transfer tests noisy.

## Test signals
Signals are readable progress logs when transfer tests fail or time out.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/it/java/com/hierynomus/smbj/testing/LoggingProgressListener.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/it/java/com/hierynomus/smbj/testing/TestingUtils.java -->
# sources/user-network-fs/smbj/src/it/java/com/hierynomus/smbj/testing/TestingUtils.java

Source read signal: reviewed complete local file (94 lines, 3660 bytes).

## Purpose
`TestingUtils.java` covers shared integration-test utilities. defines credentials, authentication contexts, random helpers, config parameter streams for default and DFS tests, EOF comparison helper, and checked callback interfaces.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
JUnit `@MethodSource` providers build `SmbConfig` variants for dialect/sign/encrypt/DFS combinations; tests use static credentials and helper methods to reduce setup duplication.

## State and persistence
State includes a shared `Random` and constants for username/password/domain.

## Dependencies and integration points
Integrates JUnit parameterized tests, SMBJ auth/config APIs, file IO helpers, and the Samba container.

## Risks
Shared random state is non-deterministic. Expanding config matrices increases test runtime and can expose server feature mismatches.

## Test signals
Signals are broad reuse across integration tests and parameterized coverage of config variants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/it/java/com/hierynomus/smbj/testing/TestingUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/it/java/integration/smbfs/DirectoryCreationIntegrationTest.java -->
# sources/user-network-fs/smbj/src/it/java/integration/smbfs/DirectoryCreationIntegrationTest.java

Source read signal: reviewed complete local file (52 lines, 1674 bytes).

## Purpose
`DirectoryCreationIntegrationTest.java` covers directory creation through the NIO provider. It validates the smbj `smbfs` Java NIO provider against the Samba Testcontainers fixture.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
opens a `SmbFileSystem` from `samba.userUri()`, calls `provider().createDirectory()` on path `a`, and relies on cleanup by container state isolation.

## State and persistence
temporary directory `a` in the user share

## Dependencies and integration points
SmbFileSystemProvider, SmbPath, and Testcontainers

## Risks
cleanup omissions can affect later tests if the share is reused

## Test signals
directory visible in the container/user share after creation
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/it/java/integration/smbfs/DirectoryCreationIntegrationTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/it/java/integration/smbfs/DirectoryListingIntegrationTest.java -->
# sources/user-network-fs/smbj/src/it/java/integration/smbfs/DirectoryListingIntegrationTest.java

Source read signal: reviewed complete local file (85 lines, 2867 bytes).

## Purpose
`DirectoryListingIntegrationTest.java` covers root and nested directory listing through `SmbFiles`. It validates the smbj `smbfs` Java NIO provider against the Samba Testcontainers fixture.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
lists root directories and a seeded public folder, collecting path names and comparing ordered expected values.

## State and persistence
read-only traversal of seeded public data

## Dependencies and integration points
SmbFiles, SmbFileSystem, Java streams

## Risks
ordering assumptions can vary if the provider or server changes listing sort behavior

## Test signals
expected root `\` and seeded directory names are returned
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/it/java/integration/smbfs/DirectoryListingIntegrationTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/it/java/integration/smbfs/FileAccessIntegrationTest.java -->
# sources/user-network-fs/smbj/src/it/java/integration/smbfs/FileAccessIntegrationTest.java

Source read signal: reviewed complete local file (86 lines, 2709 bytes).

## Purpose
`FileAccessIntegrationTest.java` covers NIO `checkAccess` behavior. It validates the smbj `smbfs` Java NIO provider against the Samba Testcontainers fixture.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
parameterized existing paths should pass while a missing path throws `IOException`.

## State and persistence
read-only access to public seeded files

## Dependencies and integration points
SmbPath and provider access checks

## Risks
server-specific errors must map to Java IO failures consistently

## Test signals
existing file/folder paths pass and missing path fails
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/it/java/integration/smbfs/FileAccessIntegrationTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/it/java/integration/smbfs/FileAttributesIntegrationTest.java -->
# sources/user-network-fs/smbj/src/it/java/integration/smbfs/FileAttributesIntegrationTest.java

Source read signal: reviewed complete local file (77 lines, 2748 bytes).

## Purpose
`FileAttributesIntegrationTest.java` covers NIO basic file attribute reads. It validates the smbj `smbfs` Java NIO provider against the Samba Testcontainers fixture.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
reads `BasicFileAttributes` for a public file and directory and asserts regular/directory flags, size, symlink false, and null file key.

## State and persistence
read-only metadata from public data

## Dependencies and integration points
NIO attributes and SMB file info mapping

## Risks
directory size is asserted as zero, which can be server-dependent

## Test signals
attributes match the seeded `test.txt` and `folder` fixtures
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/it/java/integration/smbfs/FileAttributesIntegrationTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/it/java/integration/smbfs/FileCopyIntegrationTest.java -->
# sources/user-network-fs/smbj/src/it/java/integration/smbfs/FileCopyIntegrationTest.java

Source read signal: reviewed complete local file (87 lines, 3169 bytes).

## Purpose
`FileCopyIntegrationTest.java` covers NIO copy within and across SMB shares. It validates the smbj `smbfs` Java NIO provider against the Samba Testcontainers fixture.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
copies a generated source file on the same share and from public to user, then verifies target contents from inside the container.

## State and persistence
temporary source/target files under `/opt/samba/user` and `/opt/samba/share`

## Dependencies and integration points
SmbFileSystemProvider.copy, Testcontainers file copy helpers

## Risks
cross-share copy may fall back to client-side streaming and must preserve bytes

## Test signals
container target file content equals original random data
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/it/java/integration/smbfs/FileCopyIntegrationTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/it/java/integration/smbfs/FileDeleteIntegrationTest.java -->
# sources/user-network-fs/smbj/src/it/java/integration/smbfs/FileDeleteIntegrationTest.java

Source read signal: reviewed complete local file (72 lines, 2420 bytes).

## Purpose
`FileDeleteIntegrationTest.java` covers NIO delete of files with nested parameter cases. It validates the smbj `smbfs` Java NIO provider against the Samba Testcontainers fixture.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
copies files into user share, deletes through provider paths, and asserts the container path no longer exists.

## State and persistence
temporary files under `/opt/samba/user` including nested `a/b.txt`

## Dependencies and integration points
provider.delete and SambaContainer file probes

## Risks
directory setup/teardown must match parameterized nested paths

## Test signals
container `test -f` returns false after delete
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/it/java/integration/smbfs/FileDeleteIntegrationTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/it/java/integration/smbfs/FileMoveIntegrationTest.java -->
# sources/user-network-fs/smbj/src/it/java/integration/smbfs/FileMoveIntegrationTest.java

Source read signal: reviewed complete local file (125 lines, 4860 bytes).

## Purpose
`FileMoveIntegrationTest.java` covers NIO move/rename behavior. It validates the smbj `smbfs` Java NIO provider against the Samba Testcontainers fixture.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
moves files within one share, verifies overwrite failure, and moves from public to user while removing the source.

## State and persistence
temporary source/target files and helper directories in public/user shares

## Dependencies and integration points
provider.move, SMB status-to-exception mapping, container probes

## Risks
overwrite semantics and cross-share source deletion are important correctness boundaries

## Test signals
target content preserved, source absent for cross-share move, overwrite throws
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/it/java/integration/smbfs/FileMoveIntegrationTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/it/java/integration/smbfs/FileReadingIntegrationTest.java -->
# sources/user-network-fs/smbj/src/it/java/integration/smbfs/FileReadingIntegrationTest.java

Source read signal: reviewed complete local file (60 lines, 1909 bytes).

## Purpose
`FileReadingIntegrationTest.java` covers NIO file read. It validates the smbj `smbfs` Java NIO provider against the Samba Testcontainers fixture.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
opens `test.txt` from public with `newInputStream`, reads all bytes, and checks UTF-8 contents.

## State and persistence
read-only seeded public file

## Dependencies and integration points
SmbPath, provider.newInputStream, Java IO

## Risks
assumes fixture content and charset remain stable

## Test signals
read content equals `Hi there!\n`
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/it/java/integration/smbfs/FileReadingIntegrationTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/it/java/integration/smbfs/FileSystemIntegrationTest.java -->
# sources/user-network-fs/smbj/src/it/java/integration/smbfs/FileSystemIntegrationTest.java

Source read signal: reviewed complete local file (45 lines, 1554 bytes).

## Purpose
`FileSystemIntegrationTest.java` covers SmbFileSystem creation/close. It validates the smbj `smbfs` Java NIO provider against the Samba Testcontainers fixture.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
creates a filesystem for the user URI and asserts it is a `SmbFileSystem` instance.

## State and persistence
only live filesystem/session state

## Dependencies and integration points
SmbFiles.newFileSystem and provider lifecycle

## Risks
resource leaks would show up as hanging container sessions or close failures

## Test signals
non-null filesystem of expected type
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/it/java/integration/smbfs/FileSystemIntegrationTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/it/java/integration/smbfs/FileWritingIntegrationTest.java -->
# sources/user-network-fs/smbj/src/it/java/integration/smbfs/FileWritingIntegrationTest.java

Source read signal: reviewed complete local file (112 lines, 3735 bytes).

## Purpose
`FileWritingIntegrationTest.java` covers NIO writing and appending. It validates the smbj `smbfs` Java NIO provider against the Samba Testcontainers fixture.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
writes a new file, appends to an empty file, and appends to an existing file, then verifies contents from the container.

## State and persistence
temporary `written.txt` and `test.txt` under user share

## Dependencies and integration points
provider.newOutputStream, `StandardOpenOption.APPEND`, Testcontainers file reads

## Risks
append mode must not truncate and file permissions from copied fixture must allow writes

## Test signals
container file content matches expected concatenation
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/it/java/integration/smbfs/FileWritingIntegrationTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/it/java/integration/smbfs/JavaNioIntegrationTest.java -->
# sources/user-network-fs/smbj/src/it/java/integration/smbfs/JavaNioIntegrationTest.java

Source read signal: reviewed complete local file (90 lines, 3147 bytes).

## Purpose
`JavaNioIntegrationTest.java` covers higher-level Java NIO workflow. It validates the smbj `smbfs` Java NIO provider against the Samba Testcontainers fixture.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
creates local-like nested SMB paths, writes a work file, archives a dated copy, atomically moves the work file into place, and reads both files back.

## State and persistence
nested work/archive/import paths under user share

## Dependencies and integration points
Java `Files` facade over SmbFileSystemProvider

## Risks
parent directory creation and move semantics must work together for application-style workflows

## Test signals
both final and archive files contain the same data
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/it/java/integration/smbfs/JavaNioIntegrationTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/it/java/integration/smbfs/RandomData.java -->
# sources/user-network-fs/smbj/src/it/java/integration/smbfs/RandomData.java

Source read signal: reviewed complete local file (30 lines, 980 bytes).

## Purpose
`RandomData.java` covers test random data helper. It validates the smbj `smbfs` Java NIO provider against the Samba Testcontainers fixture.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
provides small reusable random byte/string generation helpers for SMBFS integration tests.

## State and persistence
holds only static helper behavior and likely a shared random source

## Dependencies and integration points
Java random/strings and test data setup

## Risks
non-deterministic data can complicate reproducing failures unless logged

## Test signals
used tests verify byte preservation rather than fixed values
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/it/java/integration/smbfs/RandomData.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/it/resources/logback-test.xml -->
# sources/user-network-fs/smbj/src/it/resources/logback-test.xml

Source read signal: reviewed complete local file (32 lines, 1008 bytes).

## Purpose
`logback-test.xml` covers integration-test logging config. sets Logback appenders and logger levels for tests, including SMBJ and Testcontainers output.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Logback loads it from test resources during integration-test runtime.

## State and persistence
No application state; it controls emitted logs.

## Dependencies and integration points
Integrates with SLF4J/Logback and Testcontainers logging.

## Risks
Overly verbose levels can slow large transfers or hide relevant logs in CI noise; overly quiet levels reduce diagnosability.

## Test signals
Signals are useful test logs without excessive output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/it/resources/logback-test.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/AndroidManifest.xml -->
# sources/user-network-fs/smbj/src/main/AndroidManifest.xml

Source read signal: reviewed complete local file (8 lines, 322 bytes).

## Purpose
`AndroidManifest.xml` covers minimal Android manifest. declares the package for Android consumers/build tooling compatibility.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
There is no executable control flow.

## State and persistence
No runtime state.

## Dependencies and integration points
Integrates with Android packaging/lint if the library is consumed in Android contexts.

## Risks
A stale package name can break Android metadata expectations.

## Test signals
Signals are Android-compatible builds or consumers resolving the manifest.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/AndroidManifest.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdfsc/DFSException.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdfsc/DFSException.java

Source read signal: reviewed complete local file (33 lines, 1015 bytes).

## Purpose
`DFSException.java` covers DFS exception type. specializes smbj exception handling for DFS resolution/referral errors.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Constructors pass message/cause/status context to the parent exception type.

## State and persistence
No state beyond exception fields.

## Dependencies and integration points
Used by DFS client code around referral lookup and path replacement failures.

## Risks
Too-generic messages make multi-target DFS fallback hard to diagnose.

## Test signals
Signals are DFS tests surfacing meaningful failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdfsc/DFSException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdfsc/DFSPath.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdfsc/DFSPath.java

Source read signal: reviewed complete local file (114 lines, 3548 bytes).

## Purpose
`DFSPath.java` covers DFS path model. parses UNC/DFS paths into components, converts `SmbPath` to DFS form, replaces prefixes with referral targets, identifies SYSVOL/NETLOGON and IPC paths, and renders back to backslash paths.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Constructors split leading double-backslash or single-backslash paths; `replacePrefix()` swaps a prefix for target components and appends the remaining suffix; `from()` builds components from host/share/path.

## State and persistence
Holds immutable reference to a component list, though caller-supplied lists are not defensively copied.

## Dependencies and integration points
Integrates with DFS referral cache, domain cache interlink detection, and SMB path resolution.

## Risks
Empty or one-character path strings can fail due to direct `charAt`; case checks for SYSVOL/NETLOGON/IPC are exact uppercase only.

## Test signals
Signals are DFS integration tests and unit tests for prefix replacement and path rendering.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdfsc/DFSPath.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdfsc/DomainCache.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdfsc/DomainCache.java

Source read signal: reviewed complete local file (99 lines, 4982 bytes).

## Purpose
`DomainCache.java` covers DFS domain referral cache. stores trusted domain referral data keyed by domain name, with DC hint and DC list parsed from DFS referral responses.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
A `DomainCacheEntry` validates one referral, requires `NameListReferral`, reads `specialName` as domain and expanded names as DCs, then `put()` stores it in a concurrent map.

## State and persistence
State is an in-memory `ConcurrentHashMap` with no TTL handling in this class.

## Dependencies and integration points
Integrates with DFS referral parsing and `ReferralCache` interlink detection.

## Risks
Lookup is case-sensitive and there is no expiration/refresh. Empty expanded-name lists would fail when selecting the first DC.

## Test signals
Signals are DFS referral parsing tests and interlink detection tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdfsc/DomainCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdfsc/ReferralCache.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdfsc/ReferralCache.java

Source read signal: reviewed complete local file (262 lines, 11320 bytes).

## Purpose
`ReferralCache.java` covers DFS referral cache tree. stores DFS root/link/sysvol referral responses in a concurrent prefix tree with TTL, target hinting, interlink detection, and clear operations.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
`put()` splits the DFS path prefix into nodes; `lookup()` walks as far as possible and returns the nearest entry; `clear()` removes expired non-root entries under a path; entries are built from `SMB2GetDFSReferralResponse` and `DomainCache`.

## State and persistence
State is an in-memory tree of `ReferralCacheNode` objects with volatile atomic entry updates, target hint index, immutable target list, and computed expiry time.

## Dependencies and integration points
Integrates DFS referral response classes, `DFSPath`, domain cache, and SMB path resolution/fallback.

## Risks
Concurrent node insertion uses get/put rather than `computeIfAbsent`, so duplicate temporary nodes can be created. `clear()` on an expired entry clears child nodes too. TTL uses wall-clock milliseconds.

## Test signals
Signals are DFS cache unit tests, target fallback behavior, and DFS integration tests using broken-first links.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdfsc/ReferralCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdfsc/messages/DFSReferral.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdfsc/messages/DFSReferral.java

Source read signal: reviewed complete local file (184 lines, 5376 bytes).

## Purpose
`DFSReferral.java` covers abstract DFS referral entry. parses/writes the common referral header, dispatches versions 1, 2, 3, and 4, holds path/DFS path/alternate/special/expanded-name fields, and exposes server type and entry flags.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Factory peeks at `VersionNumber`, constructs the matching subclass, `read()` consumes common fields then version-specific body and advances to entry size; `writeTo()` writes common fields and delegates offsets/data to subclasses.

## State and persistence
State is one parsed referral entry object with TTL, server type, flags, and optional strings/lists.

## Dependencies and integration points
Integrates with `SMB2GetDFSReferralResponse`, referral caches, and `SMBBuffer` UTF-16 offset parsing.

## Risks
Unknown versions throw `IllegalArgumentException`. Offset handling depends on subclass size math and buffer positions.

## Test signals
Signals are referral parse/write roundtrips and DFS integration tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdfsc/messages/DFSReferral.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdfsc/messages/DFSReferralV1.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdfsc/messages/DFSReferralV1.java

Source read signal: reviewed complete local file (54 lines, 1696 bytes).

## Purpose
`DFSReferralV1.java` covers DFS referral version 1. implements legacy V1 referral parsing/writing, mainly reading a UTF-16 network address path after TTL.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Reads V1-specific fields from `SMBBuffer`, decodes null-terminated strings, and reports its computed size.

## State and persistence
State is inherited referral fields such as path and TTL.

## Dependencies and integration points
Integrates through `DFSReferral.factory()`.

## Risks
V1 has fewer offsets than later versions, so common cache code must handle missing DFS path fields.

## Test signals
Signals are V1 referral binary fixtures and fallback to original path when needed.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdfsc/messages/DFSReferralV1.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdfsc/messages/DFSReferralV2.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdfsc/messages/DFSReferralV2.java

Source read signal: reviewed complete local file (76 lines, 3102 bytes).

## Purpose
`DFSReferralV2.java` covers DFS referral version 2. parses V2 referral entries with fixed header size, TTL, path offsets, DFS path, alternate path, and network address path.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Reads offset fields relative to referral start and decodes UTF-16 strings after preserving/restoring buffer position; size is the fixed V2 structure plus string data on write.

## State and persistence
State is inherited path/DFS path/alternate path/TTL fields.

## Dependencies and integration points
Integrates with response parsing and referral cache target construction.

## Risks
Incorrect offset or size calculation corrupts subsequent referral entries. Null or illegal paths are rejected later by cache construction.

## Test signals
Signals are V2 referral parse/write tests and DFS link resolution.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdfsc/messages/DFSReferralV2.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdfsc/messages/DFSReferralV34.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdfsc/messages/DFSReferralV34.java

Source read signal: reviewed complete local file (119 lines, 5244 bytes).

## Purpose
`DFSReferralV34.java` covers DFS referral versions 3 and 4. handles modern referrals including path offsets, special names, expanded-name lists, TTL, and V4 target-set boundary flags.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Reads the fixed V3/V4 body, decodes DFS/network/special strings, reads expanded names when `NameListReferral` is set, and writes offsetted string data after entry headers.

## State and persistence
State includes inherited referral fields plus expanded names and target-set-boundary flag exposure through entry flags.

## Dependencies and integration points
Integrates with domain cache, referral cache, DFS response writing, and `EnumWithValue` flag checks.

## Risks
Expanded-name parsing depends on count and null termination. V3/V4 share code but V4-only semantics such as target-set boundary can be easy to lose.

## Test signals
Signals are DC referral tests, V3/V4 binary fixture roundtrips, and DFS domain/interlink tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdfsc/messages/DFSReferralV34.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdfsc/messages/SMB2GetDFSReferralExRequest.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdfsc/messages/SMB2GetDFSReferralExRequest.java

Source read signal: reviewed complete local file (73 lines, 2197 bytes).

## Purpose
`SMB2GetDFSReferralExRequest.java` covers DFS referral EX request encoder. builds an extended DFS referral request with max referral level, request flags, request filename, and optional site name.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Constructors initialize path/site fields; `writeTo()` emits request metadata and UTF-16 strings into `SMBBuffer`.

## State and persistence
State is a request DTO until encoded.

## Dependencies and integration points
Integrates with SMB2 IOCTL FSCTL_DFS_GET_REFERRALS_EX call sites.

## Risks
String length/offset accounting is the main interoperability risk; request flags are internal enum values.

## Test signals
Signals are wire-format tests against Windows/Samba referrals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdfsc/messages/SMB2GetDFSReferralExRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdfsc/messages/SMB2GetDFSReferralRequest.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdfsc/messages/SMB2GetDFSReferralRequest.java

Source read signal: reviewed complete local file (36 lines, 1171 bytes).

## Purpose
`SMB2GetDFSReferralRequest.java` covers DFS referral request encoder. builds the standard DFS referral request with max referral level and requested UNC path.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Constructor stores the path; `writeTo()` writes max referral level and UTF-16 request file name.

## State and persistence
State is a simple request DTO.

## Dependencies and integration points
Integrates with SMB2 DFS referral IOCTL code.

## Risks
Path encoding and null termination must match MS-DFSC expectations.

## Test signals
Signals are successful referral responses from Samba/Windows DFS roots.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdfsc/messages/SMB2GetDFSReferralRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdfsc/messages/SMB2GetDFSReferralResponse.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdfsc/messages/SMB2GetDFSReferralResponse.java

Source read signal: reviewed complete local file (117 lines, 4085 bytes).

## Purpose
`SMB2GetDFSReferralResponse.java` covers DFS referral response parser/writer. reads response header flags, referral count, consumed path length, and a list of referral entries; writes the same structure with entry data packed after headers.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Read loops over `numberOfReferrals`, dispatches `DFSReferral.factory()`, and fills missing `dfsPath` from the original path. Write computes the end of all entry headers, writes entries with data offsets, then writes offsetted data.

## State and persistence
State is original path, path consumed, header flags, and mutable referral entry list.

## Dependencies and integration points
Integrates with referral cache construction, domain cache construction, and DFS client path resolution.

## Risks
No explicit validation of count vs buffer length beyond buffer exceptions. Mixed-version referral lists depend on first-entry version for callers.

## Test signals
Signals are response parse/write roundtrips and DFS integration tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdfsc/messages/SMB2GetDFSReferralResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/ACL.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/ACL.java

Source read signal: reviewed complete local file (93 lines, 2765 bytes).

## Purpose
`ACL.java` covers MS-DTYP ACL serializer. represents an ACL revision and ACE list, and reads/writes SMB self-relative ACL wire format.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Write reserves ACL size, emits ACE count and ACE bodies, then backfills size. Read consumes revision, size, count, reserved fields, and reads each `ACE`.

## State and persistence
State is revision plus ACE list, with null lists normalized to empty.

## Dependencies and integration points
Integrates with `SecurityDescriptor`, `ACE`, and `SMBBuffer`.

## Risks
Read ignores ACL size for bounds beyond buffer position, so malformed ACE counts can drive buffer errors. Returned ACE list is mutable if caller supplied one.

## Test signals
Signals are security descriptor roundtrips and ACL/ACE fixture parsing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/ACL.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/AccessMask.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/AccessMask.java

Source read signal: reviewed complete local file (82 lines, 2365 bytes).

## Purpose
`AccessMask.java` covers SMB/MS-DTYP access-mask enum. enumerates standard, generic, directory, file, and pipe/printer access bits using `EnumWithValue`.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
No flow beyond enum construction and `getValue()`.

## State and persistence
No mutable state.

## Dependencies and integration points
Used throughout create/open calls, ACE factories, and security descriptors.

## Risks
Missing or wrong bit values cause authorization, create, and ACE serialization bugs.

## Test signals
Signals are open/share integration tests and ACE serialization tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/AccessMask.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/FileTime.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/FileTime.java

Source read signal: reviewed complete local file (93 lines, 2801 bytes).

## Purpose
`FileTime.java` covers Windows FILETIME value object. converts between Windows 100ns timestamps, Unix epoch milliseconds, `Instant`, and `Date`.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Factory methods convert input units to Windows epoch offset; getters convert back with `TimeUnit`; equality/hash are timestamp-based.

## State and persistence
Immutable `windowsTimeStamp` field.

## Dependencies and integration points
Used by SMB file information classes and MS-DTYP helpers.

## Risks
Precision loss occurs when converting through milliseconds; overflow is possible for extreme dates.

## Test signals
Signals are timestamp conversion unit tests around epoch, now, and roundtrips.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/FileTime.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/MsDataTypes.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/MsDataTypes.java

Source read signal: reviewed complete local file (99 lines, 4110 bytes).

## Purpose
`MsDataTypes.java` covers MS-DTYP primitive helpers. reads/writes GUIDs in Microsoft mixed-endian layout and FILETIME values from generic buffers.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
GUID write splits UUID bits into little-endian first fields and big-endian tail; read reverses that; filetime helpers wrap `FileTime`.

## State and persistence
Stateless utility class.

## Dependencies and integration points
Used by ACE object GUIDs, security structures, and other protocol messages.

## Risks
GUID byte order is easy to regress because it differs from network-order UUID text.

## Test signals
Signals are GUID/filetime binary fixture roundtrips.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/MsDataTypes.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/SID.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/SID.java

Source read signal: reviewed complete local file (203 lines, 7114 bytes).

## Purpose
`SID.java` covers Security Identifier model. parses SID literals, reads/writes binary SIDs, formats numeric SID strings, exposes SID type enum, and defines `EVERYONE`.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
`fromString()` validates with regex, encodes identifier authority into 6 bytes, parses subauthorities; `write()` emits revision/count/authority/subauthorities; `read()` reverses it.

## State and persistence
State is revision, identifier authority byte array, and subauthority array.

## Dependencies and integration points
Used by ACEs, security descriptors, and access-control APIs.

## Risks
Arrays are exposed directly by getters and not defensively copied. `write()` checks too-long authority but not too-short authority.

## Test signals
Signals are SID string/binary roundtrips and security descriptor tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/SID.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/SecurityDescriptor.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/SecurityDescriptor.java

Source read signal: reviewed complete local file (252 lines, 6495 bytes).

## Purpose
`SecurityDescriptor.java` covers self-relative security descriptor serializer. represents owner/group SIDs, SACL, DACL, and control flags; writes SMB-required self-relative descriptors and reads offset-based descriptors.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Write emits header, reserves four offsets, serializes present owner/group/SACL/DACL, then backfills offsets and `SR`/present bits. Read saves start position, reads offsets, seeks to each present component, and constructs a descriptor.

## State and persistence
State is descriptor fields and control set; write mutates a local copy of controls, not the object.

## Dependencies and integration points
Integrates with ACL, SID, ACE, and SMB security-info operations.

## Risks
`EnumSet.copyOf(control)` fails for null or empty non-EnumSet inputs. Read does not restore buffer position to descriptor end after seeking through components.

## Test signals
Signals are descriptor roundtrip tests and SMB set/get security integration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/SecurityDescriptor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/SecurityInformation.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/SecurityInformation.java

Source read signal: reviewed complete local file (46 lines, 1566 bytes).

## Purpose
`SecurityInformation.java` covers security information selector enum. enumerates owner/group/DACL/SACL/label/attribute/scope bits requested in SMB security operations.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
No flow beyond `getValue()`.

## State and persistence
No mutable state.

## Dependencies and integration points
Used by security descriptor query/set request builders.

## Risks
Incorrect bit values request or update the wrong security sections.

## Test signals
Signals are get/set security request tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/SecurityInformation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/ace/ACE.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/ace/ACE.java

Source read signal: reviewed complete local file (116 lines, 3941 bytes).

## Purpose
`ACE.java` covers abstract ACE base. handles common ACE header/body read-write dispatch for all supported ACE families.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Write reserves four header bytes, writes subclass body, backfills header size; read parses `AceHeader`, dispatches by `AceType`, and advances to `start + aceSize`.

## State and persistence
State is the `AceHeader` plus subclass fields.

## Dependencies and integration points
Integrates with `ACL`, SID, GUID helpers, and access mask enums.

## Risks
Wrong dispatch mapping corrupts security descriptors. Unknown ACE types throw instead of preserving opaque ACEs.

## Test signals
Signals are ACE binary roundtrips for every supported type.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/ace/ACE.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/ace/AceFlags.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/ace/AceFlags.java

Source read signal: reviewed complete local file (38 lines, 1133 bytes).

## Purpose
`AceFlags.java` covers ACE inheritance/audit flag enum. defines ACE flag bit values for object/container inheritance, no-propagate, inherit-only, inherited, and audit success/failure.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
No flow beyond enum values.

## State and persistence
No mutable state.

## Dependencies and integration points
Used by `AceHeader` and `AceTypes` factory methods.

## Risks
Bit drift changes inheritance/audit semantics in serialized ACLs.

## Test signals
Signals are ACE header flag parse/write tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/ace/AceFlags.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/ace/AceHeader.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/ace/AceHeader.java

Source read signal: reviewed complete local file (83 lines, 2401 bytes).

## Purpose
`AceHeader.java` covers ACE header parser/writer. stores ACE type, flags, and size and reads/writes the four-byte ACE header.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Write emits type value, combined flags, and size. Read maps byte values to `AceType` and `AceFlags` set.

## State and persistence
State is type, flag set, and size for one ACE.

## Dependencies and integration points
Used by `ACE.read()` and `ACE.write()`.

## Risks
Unknown ACE type maps to null, later causing dispatch failure. Size must include header and body.

## Test signals
Signals are header roundtrip tests and malformed ACE handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/ace/AceHeader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/ace/AceObjectFlags.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/ace/AceObjectFlags.java

Source read signal: reviewed complete local file (35 lines, 1038 bytes).

## Purpose
`AceObjectFlags.java` covers object ACE flag enum. defines object-type and inherited-object-type GUID presence bits.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
No flow beyond enum values.

## State and persistence
No mutable state.

## Dependencies and integration points
Used by object ACE subclasses.

## Risks
Incorrect flags make GUID fields misread or omitted.

## Test signals
Signals are object ACE roundtrips with zero, one, and both GUIDs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/ace/AceObjectFlags.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/ace/AceType.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/ace/AceType.java

Source read signal: reviewed complete local file (51 lines, 1764 bytes).

## Purpose
`AceType.java` covers ACE type enum. enumerates supported access allowed/denied, object, callback, audit, mandatory label, resource attribute, and scoped policy ACE types.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
No flow beyond values.

## State and persistence
No mutable state.

## Dependencies and integration points
Used by dispatch in `ACE` and factories in `AceTypes`.

## Risks
Unsupported future ACE types currently fail parsing.

## Test signals
Signals are parse dispatch coverage for every enum value.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/ace/AceType.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/ace/AceType1.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/ace/AceType1.java

Source read signal: reviewed complete local file (67 lines, 1937 bytes).

## Purpose
`AceType1.java` covers simple SID/access-mask ACE implementation. represents ACEs whose body is access mask plus SID, including allowed/denied/audit/mandatory-label/scoped-policy forms.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Write emits access mask and SID; read consumes both from the buffer.

## State and persistence
State is access mask and SID.

## Dependencies and integration points
Used by `ACE.read()` and `AceTypes` simple factory methods.

## Risks
Semantic differences between ACE types are carried only by header type, so callers must set the right header.

## Test signals
Signals are roundtrips for allowed, denied, audit, mandatory label, and scoped policy ACEs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/ace/AceType1.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/ace/AceType2.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/ace/AceType2.java

Source read signal: reviewed complete local file (142 lines, 4211 bytes).

## Purpose
`AceType2.java` covers object ACE implementation. represents object ACEs with access mask, object/inherited-object GUID flags, optional GUIDs, and SID.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Read parses flags, optional GUIDs using `MsDataTypes`, then SID; write emits only GUIDs selected by flags.

## State and persistence
State is access mask, object flags, optional UUIDs, and SID.

## Dependencies and integration points
Used for access allowed/denied object ACEs and as the base for callback object ACEs.

## Risks
Size/position handling is sensitive because optional GUIDs change body length.

## Test signals
Signals are object ACE roundtrips with each flag combination.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/ace/AceType2.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/ace/AceType3.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/ace/AceType3.java

Source read signal: reviewed complete local file (79 lines, 2434 bytes).

## Purpose
`AceType3.java` covers callback ACE implementation. represents callback/resource ACEs with access mask, SID, and trailing application data.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Read consumes access mask and SID, then uses ACE size to read remaining application data; write emits all three.

## State and persistence
State is access mask, SID, and byte array application data.

## Dependencies and integration points
Used for callback and resource attribute ACE types.

## Risks
Trailing data length depends on correct `aceStartPos` and header size. Application data is exposed directly.

## Test signals
Signals are callback ACE roundtrips with empty and non-empty data.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/ace/AceType3.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/ace/AceType4.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/ace/AceType4.java

Source read signal: reviewed complete local file (77 lines, 2615 bytes).

## Purpose
`AceType4.java` covers callback object ACE implementation. extends object ACE handling with trailing application data.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Read delegates object fields then reads remaining bytes as application data according to ACE size.

## State and persistence
State is object ACE fields plus application data.

## Dependencies and integration points
Used for callback object and some audit object ACE dispatch paths.

## Risks
The dispatch maps `SYSTEM_AUDIT_OBJECT_ACE_TYPE` to `AceType4`, which should be checked against spec expectations because non-callback audit object ACEs may not contain application data.

## Test signals
Signals are callback object ACE fixtures and audit object ACE parse tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/ace/AceType4.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/ace/AceTypes.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/ace/AceTypes.java

Source read signal: reviewed complete local file (151 lines, 6762 bytes).

## Purpose
`AceTypes.java` covers ACE factory helpers. provides static constructors for common ACE variants from flag sets, access-mask sets, SIDs, UUIDs, and application data.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Each helper creates the appropriate header type and subclass body, converting enum sets to numeric masks where needed.

## State and persistence
Stateless factory utility.

## Dependencies and integration points
Used by callers constructing ACL/security descriptors programmatically.

## Risks
Factory coverage is incomplete for every possible ACE type and must set header/body combinations accurately.

## Test signals
Signals are factory-created ACE write/read roundtrips and descriptor construction tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/ace/AceTypes.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mserref/NtStatus.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mserref/NtStatus.java

Source read signal: reviewed complete local file (170 lines, 5342 bytes).

## Purpose
`NtStatus.java` covers NTSTATUS enum/helper. maps many SMB/Windows NTSTATUS codes to enum constants and classifies success, informational, warning, and error ranges.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
`valueOf(long)` returns a matching constant or `STATUS_OTHER`; classification methods inspect high bits/status ranges.

## State and persistence
No mutable state beyond enum values.

## Dependencies and integration points
Used by SMB exception mapping and integration tests expecting statuses such as sharing violation.

## Risks
Incomplete enum coverage falls back to `STATUS_OTHER`, which can hide specific server behavior.

## Test signals
Signals are status mapping tests and integration assertions on expected status codes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mserref/NtStatus.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/FileAttributes.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/FileAttributes.java

Source read signal: reviewed complete local file (107 lines, 4711 bytes).

## Purpose
`FileAttributes.java` covers MS-FSCC file attribute enum. defines file attribute bit flags such as readonly, hidden, system, directory, archive, temporary, sparse, reparse point, compressed, encrypted, and integrity flags.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
No flow beyond `getValue()`.

## State and persistence
No mutable state.

## Dependencies and integration points
Used by file information parsing, create options, and attribute integration tests.

## Risks
Wrong bit values misclassify files/directories or corrupt create/set-info requests.

## Test signals
Signals are file attribute parse tests and NIO basic attribute integration tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/FileAttributes.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/FileInformationClass.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/FileInformationClass.java

Source read signal: reviewed complete local file (101 lines, 3509 bytes).

## Purpose
`FileInformationClass.java` covers file information class enum. enumerates SMB query/set file information classes with numeric protocol values.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
No flow beyond enum values.

## State and persistence
No mutable state.

## Dependencies and integration points
Used to select parsers and request classes for file metadata operations.

## Risks
Missing values limit protocol coverage; wrong numeric values query the wrong structure.

## Test signals
Signals are directory listing, file ID, internal information, and metadata query tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/FileInformationClass.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/FileNotifyAction.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/FileNotifyAction.java

Source read signal: reviewed complete local file (45 lines, 1474 bytes).

## Purpose
`FileNotifyAction.java` covers file notify action enum. maps change-notify action codes such as added, removed, modified, renamed old/new name, stream changes, and security changes.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
No flow beyond `getValue()`.

## State and persistence
No mutable state.

## Dependencies and integration points
Used by `FileNotifyInformation` and change notify responses.

## Risks
Unknown action codes map to null in current parser callers if not handled.

## Test signals
Signals are change notify integration tests expecting `FILE_ACTION_ADDED`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/FileNotifyAction.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/FileSystemInformationClass.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/FileSystemInformationClass.java

Source read signal: reviewed complete local file (46 lines, 1422 bytes).

## Purpose
`FileSystemInformationClass.java` covers filesystem information class enum. enumerates SMB filesystem information query/set classes.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
No flow beyond enum values.

## State and persistence
No mutable state.

## Dependencies and integration points
Used by filesystem metadata request builders/parsers.

## Risks
Wrong values query incompatible response structures.

## Test signals
Signals are filesystem information query tests when present.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/FileSystemInformationClass.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/directory/FileNotifyInformation.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/directory/FileNotifyInformation.java

Source read signal: reviewed complete local file (58 lines, 1922 bytes).

## Purpose
`FileNotifyInformation.java` covers change notify information parser. reads one file-notify record containing next-entry offset, action, file-name length, and UTF-16 file name.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
`read()` consumes fields from a generic buffer and maps the action with `EnumWithValue`.

## State and persistence
State is parsed offset, action, and filename.

## Dependencies and integration points
Used by SMB2 change notify response parsing and integration tests.

## Risks
It parses a single record; callers must handle chaining via `nextEntryOffset`. Unknown actions become null.

## Test signals
Signals are change-notify tests and multi-record notify parser tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/directory/FileNotifyInformation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileAccessInformation.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileAccessInformation.java

Source read signal: reviewed complete local file (29 lines, 920 bytes).

## Purpose
`FileAccessInformation.java` covers file access information DTO. holds access flags returned by a file information query.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
The class exposes `getAccessFlags()` and is populated by the file information parser infrastructure.

## State and persistence
State is one integer access mask.

## Dependencies and integration points
Integrates with MS-FSCC file information query machinery.

## Risks
Very small DTO; correctness depends on external parser setting the field with little-endian data.

## Test signals
Signals are file information query tests for access masks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileAccessInformation.java -->
