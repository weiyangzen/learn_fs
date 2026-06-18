# subset-b-008119 Research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/src/main/java/org/apache/ozone/recon/schema/SchemaVersionTableDefinition.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/src/main/java/org/apache/ozone/recon/schema/SchemaVersionTableDefinition.java

## Purpose
`SchemaVersionTableDefinition` is the Recon SQL codegen-side schema definition for the `RECON_SCHEMA_VERSION` table. It ensures Recon has a table that records the active schema/software layout version and bootstraps that value on fresh installations.

## Important APIs, Types, And Functions
The class implements `ReconSchemaDefinition`, is Guice `@Singleton`, and exposes `SCHEMA_VERSION_TABLE_NAME`, `initializeSchema()`, and `setLatestSLV(int)`. Private helpers `createSchemaVersionTable(DSLContext)` and `insertInitialSLV(DSLContext,int)` perform jOOQ DDL and initial insert.

## Control Flow
`initializeSchema()` opens a JDBC connection, builds a local `DSLContext`, checks table existence with `SqlDbUtils.TABLE_EXISTS_CHECK`, detects fresh installs by calling `listAllTables(conn)`, creates the table if missing, and inserts `latestSLV` only when no other tables existed.

## State And Persistence
Persistent state is a SQL table with `version_number` and timestamp `applied_on`. Runtime state is the injected `DataSource` and mutable `latestSLV`, which must be set by `ReconSchemaManager` before initialization.

## Dependencies And Integration Points
It depends on `DataSource`, JDBC, jOOQ DSL/data types, and `SqlDbUtils`. `ReconSchemaManager` initializes it before other schema definitions and passes the latest value derived from `ReconLayoutFeature`.

## Risks
If `setLatestSLV` is not called before a fresh install, version `0` can be inserted. Table existence is probed by selecting from the table name, so dialect-specific quoting or permission failures look like absence. Existing installs with other tables but no version row create an empty version table and rely on later migration code.

## Test Signals
Useful tests verify fresh install insert behavior, non-fresh empty-version behavior, table DDL shape, timestamp defaulting, and idempotent second initialization.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/src/main/java/org/apache/ozone/recon/schema/SchemaVersionTableDefinition.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/src/main/java/org/apache/ozone/recon/schema/SqlDbUtils.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/src/main/java/org/apache/ozone/recon/schema/SqlDbUtils.java

## Purpose
`SqlDbUtils` centralizes SQL helper constants and utility functions used by Recon schema bootstrap and code generation. It abstracts Derby creation/log suppression and a shared table-existence probe.

## Important APIs, Types, And Functions
Key constants are `DERBY_DRIVER_CLASS`, `SQLITE_DRIVER_CLASS`, and `DERBY_DISABLE_LOG_METHOD`. `TABLE_EXISTS_CHECK` is a `BiPredicate<Connection,String>` using jOOQ `select(count()).from(tableName)`. Other APIs are `createNewDerbyDatabase`, `disableDerbyLogFile`, and `listAllTables`.

## Control Flow
`createNewDerbyDatabase` sets Derby's error method, loads the embedded driver, then opens a `create=true` connection with the supplied schema name. `TABLE_EXISTS_CHECK` executes a count query and returns false on `DataAccessException`. `listAllTables` iterates JDBC metadata table rows.

## State And Persistence
The class is static and final. Persistent effects are Derby database creation and system property mutation for embedded Derby logging. `listAllTables` only reads metadata.

## Dependencies And Integration Points
It depends on JDBC, jOOQ, Derby/SQLite driver class names, SLF4J, and Java `OutputStream`. Schema definitions call the table check before creating Recon SQL tables; `SchemaVersionTableDefinition` uses `listAllTables` to identify fresh installs.

## Risks
The existence check treats any jOOQ data access failure as "table missing", which can hide permission, syntax, or connection errors. `listAllTables` does not filter system schemas, so its fresh-install semantics depend on the JDBC driver's metadata behavior. Derby logging suppression changes a JVM-wide property.

## Test Signals
Tests should cover Derby URL creation, no-op log stream behavior, table-exists true and false paths, metadata table listing, and failure behavior for invalid connections.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/src/main/java/org/apache/ozone/recon/schema/SqlDbUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/src/main/java/org/apache/ozone/recon/schema/StatsSchemaDefinition.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/src/main/java/org/apache/ozone/recon/schema/StatsSchemaDefinition.java

## Purpose
`StatsSchemaDefinition` creates Recon's `GLOBAL_STATS` SQL table, which stores keyed cluster and OM table count values used by summary APIs.

## Important APIs, Types, And Functions
The class implements `ReconSchemaDefinition`, declares `GLOBAL_STATS_TABLE_NAME`, and exposes `initializeSchema()`. Private `createGlobalStatsTable()` creates columns `key`, `value`, and `last_updated_timestamp` with primary key `pk_key`.

## Control Flow
Initialization gets a connection from the injected `DataSource`, creates a jOOQ `DSLContext`, probes for `GLOBAL_STATS`, and calls the DDL helper only when the table is absent.

## State And Persistence
Persistent state is the `GLOBAL_STATS` table keyed by a varchar stat name. Runtime state includes a mutable `DSLContext` field and the injected `DataSource`; the connection opened in `initializeSchema()` is not closed in this implementation.

## Dependencies And Integration Points
It depends on Guice, JDBC, jOOQ, and `SqlDbUtils.TABLE_EXISTS_CHECK`. Runtime code such as `ReconUtils.upsertGlobalStatsTable`, `ReconGlobalStatsManager`, `OmTableInsightTask`, and `ClusterStateEndpoint` relies on these rows.

## Risks
The unclosed connection is a resource-leak risk during repeated test or bootstrap runs. The table uses a generic `key` column, which can be dialect-sensitive. Failures in table-existence probing can lead to redundant DDL attempts.

## Test Signals
Tests should verify DDL shape, idempotent initialization, primary-key enforcement, insert/update compatibility through generated DAO classes, and connection cleanup under failures.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/src/main/java/org/apache/ozone/recon/schema/StatsSchemaDefinition.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/src/main/java/org/apache/ozone/recon/schema/UtilizationSchemaDefinition.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/src/main/java/org/apache/ozone/recon/schema/UtilizationSchemaDefinition.java

## Purpose
`UtilizationSchemaDefinition` defines SQL tables used for historical utilization and size-distribution reporting in Recon.

## Important APIs, Types, And Functions
The public table names are `CLUSTER_GROWTH_DAILY`, `FILE_COUNT_BY_SIZE`, and `CONTAINER_COUNT_BY_SIZE`. `initializeSchema()` creates all three when missing. `getDSLContext()` exposes the last initialized jOOQ context for tests or codegen support.

## Control Flow
Initialization opens a connection, assigns `dslContext`, checks each table with `TABLE_EXISTS_CHECK`, and invokes `createFileSizeCountTable`, `createClusterGrowthTable`, or `createContainerSizeCountTable` as needed. The method is annotated `@Transactional`, but the actual transaction boundary depends on the surrounding injector/persistence setup.

## State And Persistence
Persistent tables track daily datanode growth samples, file-size counts per volume/bucket/bin, and container-size bin counts. Runtime state is limited to `DataSource` and the mutable `DSLContext`.

## Dependencies And Integration Points
It uses Guice, Spring transaction annotations, JDBC, jOOQ, and generated DAO consumers such as `ClusterGrowthDailyDao`, `FileCountBySizeDao`, and `ContainerCountBySizeDao`.

## Risks
Connections are not closed directly. Table primary-key names are global strings and may collide in dialects that do not scope constraint names by table. Size-bin writers must match the primary-key dimensions exactly or updates become duplicate inserts.

## Test Signals
Tests should assert table creation, idempotency, primary keys, DAO compatibility, and population/readback from utilization tasks and endpoints.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/src/main/java/org/apache/ozone/recon/schema/UtilizationSchemaDefinition.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/src/main/java/org/apache/ozone/recon/schema/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/src/main/java/org/apache/ozone/recon/schema/package-info.java

## Purpose
`package-info.java` documents the `org.apache.ozone.recon.schema` package as the home for classes that define the Recon SQL database schema.

## Important APIs, Types, And Functions
There are no runtime APIs. The file only contains package-level Javadoc and the package declaration.

## Control Flow
No executable control flow exists.

## State And Persistence
No state is held or persisted.

## Dependencies And Integration Points
The package houses schema definition classes consumed by `ReconSchemaGenerationModule`, `ReconSchemaManager`, jOOQ code generation, and generated DAO bindings.

## Risks
The documentation is intentionally broad. If schema definitions move out of this package, package-level docs may become stale.

## Test Signals
There are no direct tests. Build compilation and generated Javadoc/package scanning are sufficient signals.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/src/main/java/org/apache/ozone/recon/schema/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/dev-support/findbugsExcludeFile.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/dev-support/findbugsExcludeFile.xml

## Purpose
This SpotBugs/FindBugs filter suppresses static-analysis findings for jOOQ-generated Recon schema classes.

## Important APIs, Types, And Functions
The XML root is `FindBugsFilter`. It contains `Match` entries for generated packages under `org.apache.ozone.recon.schema.generated`, including `tables`, `tables.daos`, `tables.pojos`, and `tables.records`.

## Control Flow
The file is declarative. The SpotBugs Maven plugin reads it and excludes matching packages from analysis.

## State And Persistence
No runtime state exists. Build-time state is the set of excluded package names.

## Dependencies And Integration Points
`recon/pom.xml` points `spotbugs-maven-plugin` at this file. The exclusions match code generated from the Recon schema definitions during the Maven lifecycle.

## Risks
Generated-code exclusions can hide real issues if hand-written classes are accidentally placed in generated packages. Package renames or jOOQ output layout changes can make the filter ineffective.

## Test Signals
Build signals are SpotBugs running without reporting generated-code findings, while manually written Recon classes remain analyzed.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/dev-support/findbugsExcludeFile.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/pom.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/pom.xml

## Purpose
The Recon Maven module POM builds the `ozone-recon` service, wires backend dependencies, runs jOOQ code generation, compiles generated sources, builds the Recon web frontend with pnpm, and packages web assets into the service artifact.

## Important APIs, Types, And Functions
Key build plugins are `maven-compiler-plugin` with `ConfigFileGenerator`, `exec-maven-plugin` running `org.apache.ozone.recon.codegen.JooqCodeGenerator`, `build-helper-maven-plugin` adding generated sources, `spotbugs-maven-plugin`, `frontend-maven-plugin`, `maven-clean-plugin`, and `maven-resources-plugin`. Dependencies span Guice/Jersey/HK2, jOOQ, Derby/SQLite, Spring JDBC/TX, SCM/OM modules, RocksDB, commons libraries, metrics/chatbot libraries, and tests.

## Control Flow
During Maven execution, generated config files are handled by annotation processing, Recon schema codegen runs in `generate-resources`, generated Java sources are added in `generate-sources`, frontend dependencies are installed and built, and built webapp files are copied during `process-resources`.

## State And Persistence
Build outputs land in `target`, generated Java sources under `target/generated-sources/java`, web build artifacts under the frontend `build` tree and classpath `webapps/recon`, and node/pnpm tooling under `target` plus a configured pnpm store.

## Dependencies And Integration Points
The POM ties the runtime classes in this subset to generated DAO classes, SQL schema definitions, HTTP/Jersey serving, OM/SCM clients, Recon tasks, and frontend resources. `findbugsExcludeFile.xml` is consumed here.

## Risks
The build has several generated-artifact phases; phase ordering matters for compiling DAO consumers. Frontend builds require pnpm lock consistency and network/cache availability. The `ozone-cli-admin` dependency excludes all transitives, so callers must rely on already declared dependencies.

## Test Signals
Signals include successful `generate-resources`, generated DAO compilation, SpotBugs filtering, frontend build/resource copy success, and module tests resolving both compile and runtime dependencies.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/ConfigurationProvider.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/ConfigurationProvider.java

## Purpose
`ConfigurationProvider` exposes the CLI-created `OzoneConfiguration` to Guice/Jersey/CDI-managed Recon components as a singleton provider and registers deprecated key aliases.

## Important APIs, Types, And Functions
It implements `Provider<OzoneConfiguration>`. Static methods `setConfiguration` and `resetConfiguration` are visible for tests. `addDeprecations` maps legacy Recon HTTP and Kerberos configuration keys to current `ReconServerConfigKeys`.

## Control Flow
The static initializer registers deprecations once. `ReconServer.call()` sets the configuration before Guice object creation. `get()` returns the static configuration reference.

## State And Persistence
State is a process-wide static `OzoneConfiguration`. No persistent data is written.

## Dependencies And Integration Points
It integrates Hadoop `Configuration.addDeprecations`, Guice provider binding in `ReconControllerModule`, and `ReconServer` startup. Tests and MiniOzoneCluster can pre-populate the static value.

## Risks
The static configuration is global and only set when currently null, so tests must call `resetConfiguration` for isolation. If startup forgets to set it, Guice consumers receive null.

## Test Signals
Tests should verify deprecation mappings, single-assignment behavior, reset behavior, and successful injection into modules.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/ConfigurationProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/MetricsServiceProviderFactory.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/MetricsServiceProviderFactory.java

## Purpose
`MetricsServiceProviderFactory` selects and constructs Recon metrics-provider implementations for Prometheus and JMX-backed metric collection.

## Important APIs, Types, And Functions
The constructor reads metrics HTTP timeouts and creates a `URLConnectionFactory`. `getMetricsServiceProvider()` returns a `PrometheusServiceProviderImpl` when `OZONE_RECON_PROMETHEUS_HTTP_ENDPOINT` is configured. `getJmxMetricsServiceProvider(String)` always creates a `JmxServiceProviderImpl`.

## Control Flow
On construction it converts timeout configs to milliseconds. Prometheus selection trims a trailing slash from the endpoint, logs the selected provider, and returns null when no endpoint is configured.

## State And Persistence
Runtime state is the injected `OzoneConfiguration`, `ReconUtils`, and connection factory. No metrics are persisted by this class.

## Dependencies And Integration Points
It is a singleton Guice binding used by `DataNodeMetricsService` and metric collection tasks. It depends on HDFS `URLConnectionFactory`, Recon config keys, `ReconUtils`, and provider implementations.

## Risks
Prometheus selection only checks non-empty endpoint string; endpoint reachability and authentication failures surface later. Connection timeout values are cast to int milliseconds and can overflow if configured extremely high.

## Test Signals
Tests should cover absent endpoint returning null, trailing slash normalization, timeout propagation, Prometheus provider creation, and JMX provider creation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/MetricsServiceProviderFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/ReconConstants.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/ReconConstants.java

## Purpose
`ReconConstants` collects stable filenames, query parameter names, default values, stats keys, size-bin bounds, and shared reprocess guards used across Recon.

## Important APIs, Types, And Functions
Important values include snapshot DB names, REST query parameter constants, file/container size bounds and bin counts, stat keys like `TOTAL_KEYS`, and atomic flags `FILE_SIZE_COUNT_TABLE_TRUNCATED` and `CONTAINER_KEY_MAPPER_INITIALIZED`. `resetTableTruncatedFlags()` clears both flags.

## Control Flow
There is no service flow beyond reset. Size-bin counts are calculated statically from power-of-two bounds.

## State And Persistence
Most values are immutable constants. The two `AtomicBoolean` fields are process-local coordination state used during OM task reprocessing to prevent duplicate truncation or initialization.

## Dependencies And Integration Points
The constants are used by REST endpoints, Recon tasks, `ReconUtils`, schema/table writers, and snapshot handling. Query names define the public API contract.

## Risks
Changing constants affects REST compatibility and task persistence semantics. Atomic guards are JVM-local, so they coordinate concurrent tasks only within one Recon process and must be reset per reprocess cycle.

## Test Signals
Tests should validate size-bin count math, reset behavior, and endpoint defaults that depend on these constants.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/ReconConstants.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/ReconContext.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/ReconContext.java

## Purpose
`ReconContext` is a singleton runtime health and identity context shared by Recon modules. It tracks cluster ID, node thread prefix, health status, and user-facing error metadata.

## Important APIs, Types, And Functions
The class exposes `isHealthy`, `updateHealthStatus`, `threadNamePrefix`, error metadata getters, `updateErrors`, cluster ID accessors, and the `ErrorCode` enum. Error codes cover topology, certificates, internal errors, snapshot failures, and upgrade failures.

## Control Flow
Construction derives Recon node details from `ReconUtils`, stores the thread prefix, and initializes maps from each `ErrorCode` to messages and impacted UI areas. Health updates atomically replace the boolean value and log the transition.

## State And Persistence
State is in-memory only: `clusterId`, `AtomicBoolean isHealthy`, synchronized error list, and error metadata maps. Nothing is persisted.

## Dependencies And Integration Points
It is injected into `ReconServer`, upgrade handling, health endpoints, node managers, and OM provider code. It depends on `OzoneConfiguration` and `ReconUtils`.

## Risks
The error list can accumulate duplicates and has no removal API. `updateHealthStatus` accepts an `AtomicBoolean` but copies only the current value, which may be surprising. Maps are mutable and exposed directly.

## Test Signals
Tests should verify initialization of error metadata, thread prefix derivation, health transitions, error recording, and cluster ID storage.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/ReconContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/ReconControllerModule.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/ReconControllerModule.java

## Purpose
`ReconControllerModule` is the main Guice module for the Recon backend. It binds service implementations, persistence modules, Recon tasks, generated DAOs, RPC clients, and SQL datasource configuration.

## Important APIs, Types, And Functions
`configure()` binds core services such as `ReconHttpServer`, `ReconDBProvider`, metadata managers, OM/SCM providers, task controller, SCM facade, metrics factory, and optional chatbot module. Nested modules bind `ReconOmTask` implementations and generated jOOQ DAO constructors. Provider methods create an executor, `OzoneManagerProtocol`, `StorageContainerLocationProtocol`, and `DataSourceConfiguration`.

## Control Flow
Guice installs persistence, task, DAO, and optional chatbot bindings. DAO classes are bound reflectively to constructors accepting jOOQ `Configuration`. The datasource provider resolves `${ozone.recon.db.dir}`-style Derby URLs by computing the configured Recon DB directory.

## State And Persistence
The module itself holds the `ReconServer` instance. It configures persistent SQL access but does not write directly. The provided executor is a fixed five-thread pool.

## Dependencies And Integration Points
It integrates Guice, jOOQ, generated schema DAOs, OM/SCM RPC clients, Recon metadata managers, tasks, heatmap service, and chatbot feature bindings.

## Risks
Provider methods return null on OM protocol construction failure, which can defer errors into consumers. Reflective DAO binding logs missing constructors but continues. The fixed executor and hard-coded task multibindings can become bottlenecks or require updates when tasks are added.

## Test Signals
Injector creation tests should assert expected bindings, DAO constructor binding, datasource URL resolution, optional chatbot binding behavior, and provider behavior on bad RPC configuration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/ReconControllerModule.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/ReconGuiceServletContextListener.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/ReconGuiceServletContextListener.java

## Purpose
`ReconGuiceServletContextListener` exposes the Recon Guice injector to the servlet container and to internal code that runs outside Jersey request handling.

## Important APIs, Types, And Functions
It extends `GuiceServletContextListener`, overrides `getInjector()`, and provides package-visible `setInjector(Injector)` plus public static `getGlobalInjector()`.

## Control Flow
`ReconServer` creates the injector and calls `setInjector` before starting the HTTP server. Jetty/Guice servlet startup then retrieves the same injector through `getInjector`.

## State And Persistence
State is a static `Injector` reference. No persistence is involved.

## Dependencies And Integration Points
It bridges server startup, Guice servlet integration, and upgrade actions that need injector access outside Jersey. `ReconRestServletModule` separately bridges Guice into Jersey/HK2.

## Risks
Static injector state can leak across tests or restarts in the same JVM. `getInjector()` can return null if servlet startup happens before `ReconServer` sets it.

## Test Signals
Tests should verify setter/getter behavior, servlet listener access, and reset/isolation patterns in embedded server tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/ReconGuiceServletContextListener.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/ReconHttpServer.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/ReconHttpServer.java

## Purpose
`ReconHttpServer` specializes `BaseHttpServer` with Recon-specific configuration keys, defaults, authentication settings, and bind ports.

## Important APIs, Types, And Functions
The constructor calls `super(conf, "recon")`. Overridden methods return HTTP/HTTPS address keys, bind-host keys/defaults, port defaults, Kerberos keytab/principal keys, enabled key, auth type, and auth config prefix.

## Control Flow
`ReconServer` obtains this singleton from Guice and calls `start()` and `stop()` through the base class. All address/security behavior is delegated to `BaseHttpServer` using the provided keys.

## State And Persistence
Server runtime state is held in the superclass. No Recon-specific persistence exists here.

## Dependencies And Integration Points
It depends on `OzoneConfiguration`, `BaseHttpServer`, `ReconConfigKeys`, and `ReconServerConfigKeys`. It serves the Jersey/Guice servlet bindings configured by `ReconRestServletModule`.

## Risks
Misconfigured key names or defaults break endpoint reachability. HTTP auth and SPNEGO depend on the keytab/principal values returned here matching the deprecation mappings and docs.

## Test Signals
Tests should verify address/default resolution, enabled/disabled behavior, HTTP security integration, and server lifecycle under Recon configuration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/ReconHttpServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/ReconResponseUtils.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/ReconResponseUtils.java

## Purpose
`ReconResponseUtils` provides small helpers for building common JSON error or empty-result HTTP responses.

## Important APIs, Types, And Functions
Static APIs are `noMatchedKeysResponse(String)`, `createBadRequestResponse(String)`, and `createInternalServerErrorResponse(String)`. Each returns a JAX-RS `Response` with JSON media type.

## Control Flow
Each helper formats a JSON string with a message, sets the HTTP status (`204`, `400`, or `500`), applies `MediaType.APPLICATION_JSON`, and builds the response.

## State And Persistence
The class is stateless and has a private constructor.

## Dependencies And Integration Points
Endpoints can use these helpers for consistent response bodies. It depends only on JAX-RS `Response` and `MediaType`.

## Risks
Messages are inserted via `String.format` without JSON escaping, so quotes or control characters in user-provided input can produce invalid JSON. A `204 NO_CONTENT` response with an entity is unusual and may be stripped by clients or servers.

## Test Signals
Tests should assert status codes, media type, body content for simple messages, and escaping behavior or lack thereof for special characters.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/ReconResponseUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/ReconRestServletModule.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/ReconRestServletModule.java

## Purpose
`ReconRestServletModule` configures Jersey REST serving for Recon APIs, scans resource packages, and installs authentication and admin filters for secured deployments.

## Important APIs, Types, And Functions
Constants define `/api/v1`, the Recon API package, and chatbot API package. `configureServlets()` chooses packages based on chatbot enablement. `configureApi` registers `ServletContainer`, provider package params, and admin endpoint discovery. `addFilters` applies `ReconAuthFilter` and `ReconAdminFilter`. Nested `GuiceResourceConfig` bridges Guice into Jersey HK2.

## Control Flow
At injector setup, the module scans packages with Reflections, detects classes annotated `@AdminOnly`, serves `/api/v1/*`, and conditionally wires filters based on HTTP security and authorization settings. Jersey startup initializes the HK2 bridge using the servlet-context Guice injector.

## State And Persistence
No persistent state exists. Runtime state is servlet/filter configuration and discovered endpoint path sets.

## Dependencies And Integration Points
It integrates Guice Servlet, Jersey, HK2 bridge, Ozone HTTP security utilities, `AdminOnly`, `ReconAuthFilter`, `ReconAdminFilter`, and optional chatbot endpoints.

## Risks
Reflections scanning must find annotation metadata correctly; path construction from resource classes controls admin filtering. If authorization is disabled, admin-only resources still skip `ReconAdminFilter`. Missing packages only log warnings, so requests fail later.

## Test Signals
Tests should verify servlet mapping, provider package list, chatbot conditional registration, admin filter path generation, auth filter enablement, and Guice-to-HK2 injection of endpoint resources.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/ReconRestServletModule.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/ReconSchemaManager.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/ReconSchemaManager.java

## Purpose
`ReconSchemaManager` orchestrates creation of all Recon SQL schema definitions during server startup.

## Important APIs, Types, And Functions
The constructor receives a Guice set of `ReconSchemaDefinition`. `createReconSchema()` initializes the schema version table first, then all other definitions. `calculateLatestSLV()` delegates to `ReconLayoutFeature.determineSLV()`.

## Control Flow
Startup calls `createReconSchema()`. It computes the latest software layout version, finds `SchemaVersionTableDefinition`, sets its latest SLV, initializes it, then iterates non-version definitions and calls `initializeSchema()` on each while logging `SQLException`s.

## State And Persistence
The manager stores a set of schema definitions. Persistent effects are whatever DDL each definition performs against the SQL datasource.

## Dependencies And Integration Points
It depends on generated schema definitions from `ReconSchemaGenerationModule`, `SchemaVersionTableDefinition`, `ReconLayoutFeature`, and SLF4J. `ReconServer` invokes it before service startup and layout upgrade finalization.

## Risks
Initialization errors are logged but not rethrown, so the server may continue with incomplete schema and fail later. HashSet iteration gives no ordering among non-version tables. Missing version definition silently skips version-table creation.

## Test Signals
Tests should verify version table first, latest SLV injection, all definitions invoked, exception handling, and behavior with absent or failing definitions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/ReconSchemaManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/ReconSchemaVersionTableManager.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/ReconSchemaVersionTableManager.java

## Purpose
`ReconSchemaVersionTableManager` reads and updates the single-row `RECON_SCHEMA_VERSION` table used by Recon layout upgrade finalization.

## Important APIs, Types, And Functions
The constructor injects a `DataSource` and initializes a jOOQ `DSLContext`. `getCurrentSchemaVersion()` fetches `version_number`, returning `-1` when no row exists. `updateSchemaVersion(int, Connection)` updates an existing row or inserts a new row. `getDataSource()` exposes the datasource.

## Control Flow
Upgrade code reads the current version through `getCurrentSchemaVersion()`. After a feature finalizes, it passes the migration connection to `updateSchemaVersion`, which switches the DSL context to that connection, checks for any row, and writes the version and current timestamp.

## State And Persistence
Persistent state is the version row and `applied_on` timestamp. Runtime state is a mutable `DSLContext` plus the injected datasource; the constructor obtains a connection without closing it.

## Dependencies And Integration Points
It depends on JDBC, jOOQ, and `ReconLayoutVersionManager`, which drives finalization after `ReconServer` starts services.

## Risks
The constructor connection may leak. The table is assumed to contain at most one row, but no primary key or uniqueness is enforced by this manager. `getCurrentSchemaVersion()` Javadoc says 0 for empty/missing table but implementation returns `-1` for empty and throws for missing/inaccessible table.

## Test Signals
Tests should cover empty table, missing table, update-vs-insert, timestamp changes, multi-row behavior, and exception wrapping.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/ReconSchemaVersionTableManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/ReconServer.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/ReconServer.java

## Purpose
`ReconServer` is the CLI entry point and lifecycle owner for the Recon service. It constructs the injector, initializes storage/security/schema, starts HTTP and metadata services, runs layout finalization, and coordinates shutdown.

## Important APIs, Types, And Functions
It extends `GenericCli` and implements `Callable<Void>`. Key methods are `call`, `start`, `stop`, `join`, `initializeCertificateClient`, `saveNewCertId`, `terminateRecon`, `loginReconUserIfSecurityEnabled`, `createReconAdmins`, `isAdmin`, and visible-for-testing accessors.

## Control Flow
`call()` loads configuration, registers it in `ConfigurationProvider`, computes Recon admins, creates Guice modules, sets the servlet injector, initializes storage and certificates when secure, creates schema, enables safe mode, obtains services, starts services, finalizes layout features, registers task metrics, and installs a shutdown hook. On initialization errors it logs and updates health based on missing components.

## State And Persistence
Runtime fields hold injector, HTTP server, metadata managers, service providers, storage config, certificate client, metrics, admins, and `isStarted`. Persistent side effects include Recon VERSION/storage initialization, certificate serial persistence, SQL schema DDL, layout version updates, and DB/provider state.

## Dependencies And Integration Points
It integrates CLI, Guice, Jetty, OM/SCM providers, Recon DB, schema manager, safe mode, metrics, security login, certificate recovery, feature flags, and shutdown hooks.

## Risks
Some initialization exceptions are caught and logged without terminating, so partial startup is possible. `start()` sets `isStarted` before all services start. `updateAndLogReconHealthStatus()` assumes `injector` is available. Security login failures are logged in helper code and may allow later failures rather than immediate abort.

## Test Signals
Tests should exercise normal lifecycle, stop idempotency, secure and insecure startup, admin resolution, health updates after component failures, schema-before-upgrade ordering, metrics register/unregister, and shutdown cleanup.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/ReconServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/ReconServerConfigKeys.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/ReconServerConfigKeys.java

## Purpose
`ReconServerConfigKeys` defines Recon-specific configuration keys and defaults for HTTP service, DB paths, OM/SCM sync, task execution, metrics collection, container reconciliation, and exports.

## Important APIs, Types, And Functions
The class is a public unstable constants holder. Key groups include HTTP/SPNEGO settings, Recon DB and snapshot directories, OM snapshot intervals and timeouts, task thread/buffer counts, SCM sync intervals, DataNode metrics collection settings, container ID/deleted-container batch sizes, unhealthy-container fetch size, and export queue/download/directory settings.

## Control Flow
There is no executable flow. Runtime code reads these constants through `OzoneConfiguration`, `ReconHttpServer`, `ReconControllerModule`, task controllers, metrics services, SCM sync code, and export managers.

## State And Persistence
No mutable state exists. The constants define persistence locations and operational defaults used elsewhere.

## Dependencies And Integration Points
It is referenced by server startup, HTTP server, SQL config URL resolution, OM/SCM providers, `DataNodeMetricsService`, and container export/listing paths.

## Risks
Changing defaults can have large operational impact on memory, SCM lock pressure, network payloads, task concurrency, and export storage. Deprecated legacy keys still exist for compatibility in nearby configuration providers.

## Test Signals
Tests should verify defaults are consumed correctly, deprecated aliases map correctly, batch caps in consuming code honor comments, and exported config docs include these annotated keys where appropriate.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/ReconServerConfigKeys.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/ReconSqlDbConfig.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/ReconSqlDbConfig.java

## Purpose
`ReconSqlDbConfig` is the annotated configuration bean for Recon's SQL database connection and jOOQ dialect.

## Important APIs, Types, And Functions
It is annotated `@ConfigGroup(prefix = "ozone.recon.sql.db")`. Configured fields include driver class, JDBC URL, username, password, autocommit, connection timeout, max active connections, max/idle ages, idle test period/query, and SQL dialect. The class provides standard getters and setters.

## Control Flow
`OzoneConfiguration.getObject(ReconSqlDbConfig.class)` populates the bean. `ReconControllerModule.getDataSourceConfiguration` reads it and adapts it to Recon's `DataSourceConfiguration` interface.

## State And Persistence
The object stores configuration values in memory. It influences persistent SQL DB location and connection-pool behavior but does not write itself.

## Dependencies And Integration Points
It depends on HDDS config annotations and is consumed by the jOOQ persistence module, codegen/runtime DAO stack, and Derby default URL resolution.

## Risks
The `@ConfigGroup` prefix and full `@Config` keys both include the same prefix style; changes must stay aligned with the config framework. Defaults are Derby-specific, so alternate dialects must set driver, URL, and dialect consistently.

## Test Signals
Tests should verify default object values, XML/config override parsing, datasource adaptation, time-unit conversion, and compatibility with Derby and SQLite settings.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/ReconSqlDbConfig.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/ReconUtils.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/ReconUtils.java

## Purpose
`ReconUtils` is a broad utility class for Recon filesystem paths, snapshot archive handling, FSO path reconstruction, metadata table pagination, global stats writes, metrics extraction, CSV streaming, and utilization size-bin math.

## Important APIs, Types, And Functions
Key APIs include `getReconDbDir`, `createTarFile`, `untarCheckpointFile`, `constructFullPath`, `constructFullPathPrefix`, `convertToObjectPathForOpenKeySearch`, `makeHttpCall`, `getLastKnownDB`, `upsertGlobalStatsTable`, permission conversion helpers, size-bin helpers, `isInitializationComplete`, `convertToEpochMillis`, `validateStartPrefix`, `extractKeysFromTable`, `gatherSubPaths`, `validateNames`, `constructObjectPathWithPrefix`, `getMetricsData`, `extractLongMetricValue`, and `downloadCsv`.

## Control Flow
Path construction walks `NSSummary` parents bottom-up until parent ID zero, returning empty when the summary tree is missing/rebuilding. Object-path conversion parses volume/bucket/path names, resolves IDs from OM tables, then checks directory and open-file tables. Table extraction seeks by `prevKey` or prefix and iterates until limit or prefix mismatch. Snapshot selection picks the newest timestamped file and deletes older/unknown entries.

## State And Persistence
The class is mostly stateless aside from a replaceable static logger. It creates/deletes tar/snapshot files, deletes stale DB snapshot directories, writes global stats via DAO upsert, and streams CSV responses.

## Dependencies And Integration Points
It touches HDDS/SCM utilities, OM metadata tables, Recon namespace summary, Recon SCM facade, jOOQ/global stats DAO, Hadoop URL connections, CSV printer, and JAX-RS responses.

## Risks
The class mixes unrelated responsibilities. `getLastKnownDB` deletes files while scanning. Path conversion returns original prefixes on runtime failures, which can mask data issues. Name validation is bucket/volume-specific but used in path conversion. CSV and JSON callers must handle unescaped or large output carefully.

## Test Signals
Strong tests cover FSO path reconstruction, rebuild/missing summary behavior, object path conversion at root/volume/bucket/dir/key levels, table pagination, size-bin boundaries, date parse fallback, metrics parsing, global stats upsert, snapshot cleanup, and CSV headers/body.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/ReconUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/TarExtractor.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/TarExtractor.java

## Purpose
`TarExtractor` extracts tar archive contents into a staging directory with parallel file writes, then replaces the target output directory.

## Important APIs, Types, And Functions
The constructor accepts thread-pool size and thread-name prefix. Public lifecycle methods are `start`, `extractTar(InputStream,Path)`, and `stop`. Private helpers `readEntryData` and `writeFile` buffer tar entry bytes and write them to disk.

## Control Flow
`start()` creates a fixed executor once. `extractTar()` creates a `.staging_<uuid>` sibling directory, sequentially reads tar entries, buffers each file entry into memory, submits write tasks, waits for all futures, deletes an existing output directory, then attempts an atomic move from staging to output. `stop()` shuts down the executor and awaits termination.

## State And Persistence
Runtime state is an executor guarded by `AtomicBoolean`. Persistent effects are staging directory creation, extracted files, deletion of existing output, and final directory replacement.

## Dependencies And Integration Points
It depends on Guava thread factories, Apache Commons Compress tar streams, Commons IO `FileUtils`, and `ReconConstants.STAGING`. It is suited for OM/SCM snapshot extraction flows.

## Risks
Calling `extractTar` before `start` causes a null executor. Each file is fully buffered in memory and casts entry size to int, which is unsafe for very large entries. If atomic move fails, it only logs a warning and leaves staging/output state ambiguous. Tar entry names are written directly, so path traversal protection is not explicit.

## Test Signals
Tests should cover lifecycle ordering, directory and file extraction, existing output replacement, large file behavior, failed write propagation through futures, interrupted shutdown, atomic move fallback, and malicious entry names.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/TarExtractor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/AccessHeatMapEndpoint.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/AccessHeatMapEndpoint.java

## Purpose
`AccessHeatMapEndpoint` exposes Recon heatmap APIs for read-access metadata and provider health checks.

## Important APIs, Types, And Functions
The resource is `@Path("/heatmap")`, JSON-producing, `@AdminOnly`, and `@InternalOnly`. It injects `HeatMapServiceImpl`. `getReadAccessMetaData(path, entityType, startDate)` handles `/readaccess`; the overloaded no-arg `getReadAccessMetaData()` handles `/healthCheck`.

## Control Flow
The read-access method checks whether the heatmap feature is disabled through `FeatureProvider.getAllDisabledFeatures()`, then delegates to `heatMapService.retrieveData`. Failures become `WebApplicationException` with HTTP 500. The health-check endpoint directly returns `heatMapService.doHeatMapHealthCheck()`.

## State And Persistence
The endpoint holds only the injected service. Persistence is owned by the heatmap provider/service behind `HeatMapServiceImpl`.

## Dependencies And Integration Points
It integrates REST query constants, `FeatureProvider`, admin filtering via `AdminOnly`, internal feature gating, and heatmap service implementation.

## Risks
The feature-name comparison uses `"HeatMap"` while the annotation uses `"Heatmap"`, so naming consistency matters. Disabled feature returns 404, not a structured feature-disabled body. All service exceptions are collapsed to 500.

## Test Signals
Tests should verify query defaults, disabled-feature 404, successful tree response, service exception mapping, admin filter discovery, and health-check delegation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/AccessHeatMapEndpoint.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/AdminOnly.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/AdminOnly.java

## Purpose
`AdminOnly` marks JAX-RS resource classes whose endpoints should be restricted to Ozone or Recon administrators when HTTP authorization is enabled.

## Important APIs, Types, And Functions
It is a runtime-retained type annotation targeting classes. It has no members.

## Control Flow
`ReconRestServletModule` scans API packages for `@AdminOnly`, builds resource paths from annotated classes, and applies `ReconAdminFilter` to those paths when security and authorization are enabled.

## State And Persistence
No state or persistence exists.

## Dependencies And Integration Points
It depends on Java annotations and JAX-RS `@Path` by convention. It is used by endpoints such as heatmap, blocks, buckets, and containers.

## Risks
The annotation has effect only if package scanning discovers it and authorization is enabled. Method-level restrictions are not supported. A class missing `@Path` or with unusual path composition can produce incorrect filter paths.

## Test Signals
Tests should assert annotated resources are discovered, admin filters are added for their paths, and unannotated resources remain accessible according to the auth policy.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/AdminOnly.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/BlocksEndPoint.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/BlocksEndPoint.java

## Purpose
`BlocksEndPoint` exposes block deletion backlog information grouped by container lifecycle state.

## Important APIs, Types, And Functions
The resource is `@Path("/blocks")`, JSON-producing, and `@AdminOnly`. The main API is `GET /deletePending` through `getBlocksPendingDeletion(limit, prevKey)`. It uses `ContainerBlocksInfoWrapper` and SCM `DELETED_BLOCKS` table entries.

## Control Flow
The endpoint rejects negative limit or previous transaction ID with `406`. It iterates the SCM deleted-blocks table, optionally seeks to `prevKey` and skips it, converts each `DeletedBlocksTransaction` into wrapper metadata, looks up the container state from `ReconContainerManager`, groups by state, and stops when the current state's list reaches the limit.

## State And Persistence
It reads persistent SCM RocksDB state through `DBStore` and the in-memory/container-manager view of container state. It does not mutate data.

## Dependencies And Integration Points
It depends on `ReconStorageContainerManagerFacade`, `ReconContainerManager`, SCMDB `DELETED_BLOCKS`, container IDs, and JAX-RS exceptions.

## Risks
The limit is applied to the size of the currently appended state list, not total records, so responses can exceed the limit across multiple states. Container lookup failures turn into 500. Invalid seek keys can return empty results.

## Test Signals
Tests should cover negative inputs, prevKey seeking/skipping, state grouping, per-state limit behavior, missing container errors, and empty deleted-block tables.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/BlocksEndPoint.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/BucketEndpoint.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/BucketEndpoint.java

## Purpose
`BucketEndpoint` lists buckets known to Recon's OM metadata snapshot, optionally under a specific volume.

## Important APIs, Types, And Functions
The resource is `@Path("/buckets")`, JSON-producing, and `@AdminOnly`. `getBuckets(volume, limit, prevKey)` returns `BucketsResponse` containing `BucketObjectDBInfo` wrappers.

## Control Flow
The endpoint delegates to `ReconOMMetadataManager.listBucketsUnderVolume(volume, prevKey, limit)`, maps each `OmBucketInfo` into API metadata, counts the returned buckets, and returns a JSON response.

## State And Persistence
It reads the OM metadata snapshot through `ReconOMMetadataManager`. It has no local mutable state beyond the injected manager reference.

## Dependencies And Integration Points
It integrates REST query constants, OM metadata manager bucket listing, `OmBucketInfo`, and bucket response DTOs.

## Risks
No explicit validation is performed for negative limits or malformed volume names here; behavior depends on the metadata manager. The field is both `@Inject` annotated and constructor-injected, which is redundant.

## Test Signals
Tests should cover unscoped and volume-scoped listing, pagination via `prevKey`, limit handling, empty results, and IOException propagation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/BucketEndpoint.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/ClusterStateEndpoint.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/ClusterStateEndpoint.java

## Purpose
`ClusterStateEndpoint` returns a high-level summary of Recon's view of the Ozone cluster: containers, datanodes, pipelines, capacity, volume/bucket/key counts, pending deletion, and service IDs.

## Important APIs, Types, And Functions
The resource is `@Path("/clusterState")`. `getClusterState()` builds `ClusterStateResponse`, `ClusterStorageReport`, and `ContainerStateCounts`. It uses a `MISSING_CONTAINER_COUNT_LIMIT` sentinel of 1001.

## Control Flow
The endpoint reads pipeline count, missing-container records, open/deleted container counts, healthy datanode counts, SCM node aggregate stats, per-datanode filesystem usage, and global stats for OM table counts. It sums legacy keys and FSO files, counts deleted keys and deleted dirs, subtracts deleted containers from total, then returns the response.

## State And Persistence
It reads in-memory SCM manager state, container health SQL records, and global stats values populated from OM metadata tasks. It does not mutate state.

## Dependencies And Integration Points
It integrates `ReconNodeManager`, `ReconPipelineManager`, `ReconContainerManager`, `ContainerHealthSchemaManager`, `ReconGlobalStatsManager`, OM table definitions, and Ozone service ID config keys.

## Risks
Filesystem usage may be incomplete when datanodes have not reported. Missing-container count is capped/sentinel-based. Global stats IO failures set some defaults but may leave other counters at zero. Container total subtracts deleted containers from current manager size, so stale deleted state affects totals.

## Test Signals
Tests should assert healthy node counting, storage report fields, missing sentinel behavior, global stats aggregation, deleted-container subtraction, service ID propagation, and behavior when no datanodes or stats exist.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/ClusterStateEndpoint.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/ContainerEndpoint.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/ContainerEndpoint.java

## Purpose
`ContainerEndpoint` is the main Recon REST resource for container listing, key lookup by container, replica history, unhealthy/missing/quasi-closed container reporting, OM/SCM mismatch insights, deleted-container listing, and async unhealthy-container exports.

## Important APIs, Types, And Functions
The resource is `@Path("/containers")` and `@AdminOnly`. APIs include `GET /`, `/{id}/keys`, `/{id}/replicaHistory`, `/missing`, `/unhealthy`, `/unhealthy/{state}`, export job list/start/status/download/cancel paths, `/deleted`, `/mismatch`, `/mismatch/deleted`, and `/quasiClosed`. Helpers include `DataFilter`, `getUnhealthyContainersFromSchema`, `toUnhealthyMetadata`, `getBlocks`, and `toQuasiClosedMetadata`.

## Control Flow
Container listing pages from `ReconContainerManager`. Key lookup reads container-key prefixes, resolves `OmKeyInfo` from legacy or FSO tables, filters key-location versions, builds block metadata for the target container, and constructs full paths via namespace summaries. Unhealthy endpoints read SQL health rows, convert them to metadata with container info and replica history, and add summary counts. Mismatch endpoints merge sorted SCM container state and OM container metadata iterators to find containers missing in either side or deleted in SCM but present in OM. Export endpoints delegate queueing, progress, download limiting, streaming, and cancellation to `ExportJobManager`.

## State And Persistence
The endpoint reads SCM manager state, OM snapshot tables, Recon container-key metadata, namespace summary state, SQL unhealthy-container records, and export job files. It mutates export job state through submit/cancel/download reservation but does not modify container metadata.

## Dependencies And Integration Points
It integrates `ReconStorageContainerManagerFacade`, `ReconContainerManager`, `PipelineManager`, `ReconContainerMetadataManager`, `ReconOMMetadataManager`, `ReconNamespaceSummaryManager`, `ContainerHealthSchemaManager`, `ExportJobManager`, and numerous API DTOs.

## Risks
Some validation returns `406`, some `400`, and some methods coerce limits differently. `constructFullPath` can return empty during namespace rebuild. Export downloads reserve before streaming, so failed transfers still consume attempts. In-memory sorting/iteration over all SCM containers can be expensive for mismatch endpoints. The deprecated `/missing` path duplicates newer unhealthy-state behavior.

## Test Signals
Tests should cover pagination, negative input handling, key version/block mapping, missing namespace summaries, unhealthy state validation and summary counts, export queue and download limits, mismatch merge correctness for both filters, deleted-container filtering, quasi-closed pagination, and error mapping.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/ContainerEndpoint.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/DataNodeMetricsService.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/DataNodeMetricsService.java

## Purpose
`DataNodeMetricsService` asynchronously collects pending-deletion metrics from all datanodes, aggregates totals, tracks failures, and serves the latest collection status/results to API callers.

## Important APIs, Types, And Functions
It is a singleton service injected with Recon SCM, configuration, and `MetricsServiceProviderFactory`. Public methods are `startTask()`, `getCollectedMetrics(Integer)`, and `shutdown()`. Internal flow uses `CollectionContext`, `MetricCollectionStatus`, `submitMetricsCollectionTasks`, `processCollectionFutures`, `checkAndHandleTimeout`, `handleCompletedFuture`, and `updateFinalState`.

## Control Flow
`getCollectedMetrics` calls `startTask`. `startTask` prevents concurrent runs with `isRunning`, enforces a minimum delay since last completion, handles empty datanode lists, sets status in progress, and schedules `collectMetrics`. Collection submits one `DataNodeMetricsCollectionTask` per node, polls futures every 200 ms, cancels tasks after the configured timeout, accumulates successful pending-byte counts, records failures with `-1`, sorts results descending, and publishes final state.

## State And Persistence
State is in-memory: current status, result list, totals, failure counts, last collection time, and executor. No metrics are persisted by this class.

## Dependencies And Integration Points
It depends on `ReconNodeManager`, `DatanodeInfo`, HTTP policy, DN metrics config keys, `MetricsServiceProviderFactory`, `DataNodeMetricsCollectionTask`, and `DataNodeMetricsServiceResponse`.

## Risks
State fields are not all volatile and reads are not synchronized in `getCollectedMetrics`, so callers may observe stale values. The same executor runs the async orchestrator and per-node tasks, so a pool of size one can deadlock/starve. Timeout is measured from batch submission time, not per-task start. Failed placeholder results sort with negative values last.

## Test Signals
Tests should cover concurrency guard, rate limiting, empty-node handling, success aggregation, failed task counting, timeout cancellation, limit slicing, status transitions, executor shutdown, and low thread-count behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/DataNodeMetricsService.java -->
