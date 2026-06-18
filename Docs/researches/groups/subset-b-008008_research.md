# subset-b-008008 research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/dev-support/checkstyle/checkstyle.xml -->
# sources/object-store/apache-ozone/hadoop-hdds/dev-support/checkstyle/checkstyle.xml

## Purpose
This XML file is the Hadoop HDDS Checkstyle rule set used by Maven/build-time Java linting. It extends the standard Checkstyle `Checker`/`TreeWalker` model with HDDS-specific style, import, Javadoc, and code-quality constraints. It is not application runtime code; it defines static validation policy for Java sources in the Apache Ozone HDDS tree.

## Important modules and APIs
- Root module: `Checker`, using Checkstyle DTD `configuration_1_2.dtd`.
- File-level modules: `Header`, `BeforeExecutionExclusionFileFilter`, `SuppressWarningsFilter`, `JavadocPackage`, `NewlineAtEndOfFile`, `Translation`, `FileTabCharacter`, `LineLength`, and `RegexpMultiline`.
- AST modules under `TreeWalker`: `SuppressWarningsHolder`, suppression comment filters, Javadoc checks, naming checks, import checks, size checks, whitespace checks, modifier/block/coding/design checks, `ArrayTypeStyle`, `Indentation`, `UpperEll`, and `ModifierOrder`.
- HDDS-specific constraints include the license header path `hadoop-hdds/dev-support/checkstyle/license.header`, generated-source exclusion `.*/target/generated.*`, line length `120`, and a regex ban on `Preconditions.checkNotNull` in favor of `Objects.requireNonNull`.
- Import policy forbids `sun.*`, relocated/shaded packages, selected `org.apache.hadoop.test` utilities, and `org.apache.hadoop.fs.CommonConfigurationKeys`.

## Control flow
Checkstyle loads the root `Checker`, applies file-level filters and checks, then runs `TreeWalker` checks over Java ASTs. Generated files under `target/generated*` are filtered before execution. Suppression annotations/comments are enabled through `SuppressWarningsFilter`, `SuppressWarningsHolder`, `SuppressionCommentFilter`, and `SuppressWithNearbyCommentFilter`, so selected violations can be locally waived when Checkstyle is configured to honor them.

## State and persistence
The file has no mutable runtime state. Its persistent effect is policy: build runs and IDE integrations using this config will report or fail on violations. The only external file state it references directly is the required license header file.

## Dependencies and integration points
This integrates with Checkstyle, the HDDS Maven build, Java source files, generated-source directories, and any suppression configuration wired by the build. The DTD is referenced from `https://checkstyle.org/dtds/configuration_1_2.dtd`. The rule set assumes modern Checkstyle support for tokens such as `RECORD_DEF` and `COMPACT_CTOR_DEF`.

## Risks and edge cases
- The `Header` path is relative to the build execution layout; moving the module or changing Maven working directories can break header resolution.
- The `IllegalImport` regex is broad for relocated/shaded packages and can reject intentional internal relocation imports.
- `RegexpMultiline` searches across lines for `Preconditions.checkNotNull`; false positives are possible in comments or non-code text if file extension scoping changes.
- New Java language constructs require Checkstyle/token compatibility; the config already includes record tokens, but future constructs may need updates.
- Javadoc and package checks can produce high churn in generated, test, or legacy packages unless suppressions are kept aligned.

## Test signals
Primary validation is running the Checkstyle goal/profile used by the HDDS Maven build. Useful targeted signals are: a Java file without the license header should fail `Header`; a Java file with tabs should fail `FileTabCharacter`; a long Java code line over 120 characters should fail unless matching the ignore pattern; an import from `sun.*` or `*.shaded.*` should fail; `Preconditions.checkNotNull` should emit the configured replacement message; generated files under `target/generated*` should be excluded.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/dev-support/checkstyle/checkstyle.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/dev-support/checkstyle/suppressions.xml -->
# sources/object-store/apache-ozone/hadoop-hdds/dev-support/checkstyle/suppressions.xml

## Purpose
This file defines Checkstyle suppression rules for known HDDS/Hadoop source areas where the main `checkstyle.xml` rules are intentionally relaxed. It is a build-time lint configuration companion, not runtime code.

## Important modules and entries
- Root element: `suppressions`, using Checkstyle DTD `suppressions_1_1.dtd`.
- Suppresses `JavadocPackage` for any `src/test` path.
- Suppresses `JavadocPackage` for `src/main/java/org/apache/hadoop/io/erasurecode/rawcoder`.
- Suppresses `IllegalImport` and `MissingJavadocType` for `src/test/java/org/apache/hadoop/fs/contract/.*java`.
- Suppresses `IllegalImport` for `src/test/java/org/apache/hadoop/tools/contract/.*java`.
- Suppresses all checks for `src/main/java/org/apache/hadoop/.*_/.*java`, which appears intended for generated or underscore-suffixed compatibility package paths.

## Control flow
When Checkstyle is configured with this suppression file, each violation is matched against the `checks` regex/name and `files` regex. Matching violations are discarded before reporting. The suppression decisions are declarative and order-independent for these entries.

## State and persistence
The file has no mutable state. Its persistent behavior is to hide matching Checkstyle findings across all builds that include this suppressions file.

## Dependencies and integration points
It depends on Checkstyle suppression support and on the build wiring that points Checkstyle at this file. It integrates tightly with `dev-support/checkstyle/checkstyle.xml`, especially the `JavadocPackage`, `IllegalImport`, and `MissingJavadocType` checks.

## Risks and edge cases
- File regexes are path-format sensitive. Some entries use forward slashes only while the first uses `[\\/]`; Windows or alternate path normalization can affect matches.
- `checks=".*"` for underscore package paths suppresses every rule and can mask serious style or correctness issues if the regex catches more code than intended.
- Suppressing test Javadocs reduces noise but also weakens documentation checks for public test utilities.
- If package paths are moved, suppressions may silently stop applying or continue applying to unintended files.

## Test signals
Run the configured Checkstyle task against representative files in the suppressed paths. Violations for `JavadocPackage` under `src/test` should be ignored, `IllegalImport` in the listed contract test paths should be ignored, and the same violations outside those paths should still be reported. A path separator variation test is useful if the build supports multiple operating systems.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/dev-support/checkstyle/suppressions.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/docs/config.yaml -->
# sources/object-store/apache-ozone/hadoop-hdds/docs/config.yaml

## Purpose
This is the Hugo site configuration for the Apache Ozone HDDS documentation module. It sets site language metadata, title, theme, URL behavior, Markdown rendering, and security allowances for selected environment variables.

## Important configuration
- `languageCode: en-us`, `DefaultContentLanguage: en`.
- Two languages are declared: English with weight 1 and Chinese with weight 2.
- Site title is `Ozone`.
- `params.ghrepo` points at `https://github.com/apache/ozone/`.
- Theme is `ozonedoc`.
- `pygmentsCodeFences: true` enables code highlighting for fenced blocks.
- `uglyurls: true` and `relativeURLs: true` control generated URLs for static packaging.
- Taxonomy and taxonomyTerm page kinds are disabled.
- Goldmark `renderer.unsafe: true` allows raw HTML in Markdown.
- Hugo security allows `getenv` for variables matching `^HUGO_` and `^OZONE_VERSION$`.

## Control flow
Hugo reads this file at site generation time. The settings determine content language selection, theme loading, output URL construction, Markdown rendering, and which environment variables templates may access. The `OZONE_VERSION` allowance is paired with the generation script that exports the Maven-derived project version.

## State and persistence
No mutable application state is stored here. The persistent output effect is the generated static documentation tree, especially links and HTML rendering behavior under the build target.

## Dependencies and integration points
This integrates with Hugo, the local `ozonedoc` theme under `docs/themes`, Markdown content, theme templates that may call `getenv`, and `docs/dev-support/bin/generate-site.sh` which exports `OZONE_VERSION`.

## Risks and edge cases
- `unsafe: true` permits raw HTML from docs content; this is common for documentation sites but increases review burden for untrusted content.
- `relativeURLs` and `uglyurls` are important for packaged docs. Changing either can break links in the built jar or static artifact.
- Only `HUGO_*` and `OZONE_VERSION` environment variables are allowed to templates; adding template usage of other environment variables will fail under Hugo security.
- The `DefaultContentLanguage` key uses Hugo's historical capitalization; config parser behavior should be checked when upgrading Hugo.

## Test signals
Run the docs generation path and inspect generated links, language output, syntax-highlighted code blocks, raw HTML rendering, and any template version display using `OZONE_VERSION`. A Hugo config validation/build with the repo's supported Hugo version is the best signal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/docs/config.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/docs/dev-support/bin/generate-site.sh -->
# sources/object-store/apache-ozone/hadoop-hdds/docs/dev-support/bin/generate-site.sh

## Purpose
This Bash script builds the HDDS documentation site with Hugo into the Maven output directory. It is designed to be invoked from the docs build/check flow and to skip cleanly when Hugo is unavailable.

## Important variables and commands
- `set -eu` exits on unset variables and failed commands.
- `DIR` resolves the script directory via `${BASH_SOURCE[0]}`.
- `DOCDIR="$DIR/../.."` points to the docs module root.
- `which hugo` gates execution; if Hugo is missing, it prints a skip message and exits `0`.
- `OZONE_VERSION` is exported from `mvn help:evaluate -Dexpression=ozone.version -q -DforceStdout -Dscan=false`.
- `ENABLE_GIT_INFO` becomes `--enableGitInfo` if `git -C $(pwd) status` succeeds.
- Output directory is `$DOCDIR/target/classes/docs`.
- Main build command is `hugo "${ENABLE_GIT_INFO}" -d "$DESTDIR" "$@"`.

## Control flow
The script resolves paths, checks for Hugo, computes the Ozone version from Maven, conditionally enables Hugo Git metadata, creates the destination directory, changes into the docs directory, invokes Hugo with any caller-provided arguments, and returns to the previous directory with `cd -`.

## State and persistence
The script writes generated static docs into `hadoop-hdds/docs/target/classes/docs`. It also exports `OZONE_VERSION` for the Hugo process. It does not persist any state outside generated output.

## Dependencies and integration points
Dependencies are Bash, `hugo`, `mvn`, `git`, the docs `config.yaml`, and the `ozonedoc` Hugo theme. The Maven docs module and `hadoop-ozone/dev-support/checks/docs.sh` are likely callers through the docs `pom.xml`.

## Risks and edge cases
- Missing Hugo is treated as a successful skip, so CI must separately decide whether skipped docs are acceptable.
- `git -C $(pwd)` leaves `$(pwd)` unquoted; unusual working directories with whitespace would break this check.
- Passing an empty `ENABLE_GIT_INFO` as a quoted argument may produce an empty Hugo argument; most shells pass it as `""`, which Hugo generally tolerates but is less clean than an array.
- Maven version evaluation failure aborts the script because of `set -e`.
- `cd -` prints the previous directory, which can add noise to build logs.

## Test signals
Run with Hugo absent to confirm exit `0` and skip message. Run with Hugo present to confirm `target/classes/docs` is populated, the generated site sees `OZONE_VERSION`, user-provided Hugo args are passed through, and Git info is enabled only inside a Git worktree. Shellcheck would flag the unquoted `$(pwd)` and empty-argument pattern.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/docs/dev-support/bin/generate-site.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/docs/pom.xml -->
# sources/object-store/apache-ozone/hadoop-hdds/docs/pom.xml

## Purpose
This Maven POM defines the `hdds-docs` jar module for Apache Ozone documentation. It packages generated documentation resources rather than compiling application code.

## Important Maven elements
- Parent: `org.apache.ozone:hdds:2.3.0-SNAPSHOT`.
- Artifact: `hdds-docs`, version `2.3.0-SNAPSHOT`, packaging `jar`.
- Properties: `maven.test.skip` is `true` because there is no testable code, and `skipDocs` defaults to `false`.
- `maven-compiler-plugin` sets `<proc>none</proc>` to disable annotation processing.
- `exec-maven-plugin` binds goal `exec` to the `compile` phase and executes `../../hadoop-ozone/dev-support/checks/docs.sh`, controlled by `<skip>${skipDocs}</skip>`.

## Control flow
During Maven `compile`, the exec plugin invokes the docs check/generation script unless `skipDocs` is true. The resulting generated resources are expected to land under the module target tree and be packaged into the jar. Tests are skipped for this module.

## State and persistence
The POM itself has no runtime state. Build outputs persist under `docs/target`, especially generated docs resources that can be included in the jar artifact.

## Dependencies and integration points
This module depends on the parent HDDS Maven configuration for plugin versions and properties. It integrates with the external script `hadoop-ozone/dev-support/checks/docs.sh`, which in turn is expected to drive Hugo generation through `docs/dev-support/bin/generate-site.sh`.

## Risks and edge cases
- The executable path is relative to this module and crosses into `hadoop-ozone`; repository layout changes can break the build.
- Since tests are skipped, regressions in docs generation are only caught by script exit status and artifact inspection.
- `skipDocs` can disable the main behavior, so release/CI profiles need to ensure it is not accidentally true where documentation artifacts are required.
- Disabling annotation processing is appropriate for a docs module but can hide accidental introduction of Java sources that expect processors.

## Test signals
Run `mvn compile` for the docs module with `skipDocs=false` and confirm `docs.sh` executes and generated docs are packaged. Run with `-DskipDocs=true` to confirm skip behavior. Check effective POM/plugin versions from the parent if plugin behavior changes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/docs/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/docs/themes/ozonedoc/static/js/bootstrap.min.js -->
# sources/object-store/apache-ozone/hadoop-hdds/docs/themes/ozonedoc/static/js/bootstrap.min.js

## Purpose
This is the minified Bootstrap JavaScript bundle for Bootstrap v3.4.1, vendored into the `ozonedoc` Hugo theme. It provides browser-side interactive UI behavior for the generated documentation site.

## Important APIs and plugins
- Requires jQuery and explicitly rejects unsupported versions: at least 1.9.1 and below 4.
- Defines `jQuery.fn` plugins for Bootstrap 3 components including `alert`, `button`, `carousel`, `collapse`, `dropdown`, `modal`, `tooltip`, `popover`, `scrollspy`, `tab`, and `affix`.
- Adds transition support helpers such as `emulateTransitionEnd` and `bsTransitionEnd`.
- Uses Bootstrap event namespaces such as `.bs.modal`, `.bs.dropdown`, `.bs.tab`, and related component lifecycle events.
- Provides `noConflict` hooks for plugins so existing jQuery plugin names can be restored.

## Control flow
On load, the bundle validates the presence and version of jQuery, detects CSS transition end event support, then registers each Bootstrap plugin on `jQuery.fn`. Runtime behavior is event-driven: data attributes and direct plugin calls attach handlers for clicks, keyboard events, transitions, scrolling, modal display, collapses, tabs, tooltips, and popovers.

## State and persistence
State is in browser memory and DOM attributes/classes. Components store plugin instances in jQuery data, add/remove CSS classes such as `open`, `active`, `in`, and `affix`, and manage transient timers/transition callbacks. There is no server persistence or storage API use in this vendored bundle.

## Dependencies and integration points
The bundle depends on `jquery-3.5.1.min.js` being loaded first and on Bootstrap 3 CSS classes in the theme. It integrates with theme markup using Bootstrap data attributes and with the custom `ozonedoc.js` script that adds Bootstrap table classes.

## Risks and edge cases
- Bootstrap 3.4.1 is a legacy major version; compatibility and security review should be handled as a vendored third-party dependency.
- Loading order is critical: if jQuery is missing or version 4+ is used, the script throws and Bootstrap behavior is unavailable.
- Minified vendor code is difficult to patch locally; upgrades should replace the whole artifact from a trusted upstream source.
- Bootstrap plugins mutate DOM classes and may conflict with custom theme JavaScript if selectors overlap.

## Test signals
Generated docs should load without console errors, with jQuery loaded before this file. Manual/browser tests should cover navbar dropdowns, tabs, collapsible panels, modals/tooltips if used, scrollspy/affix behavior if used, and table styling from `ozonedoc.js`. Static dependency checks should verify the vendored version and license header.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/docs/themes/ozonedoc/static/js/bootstrap.min.js -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/docs/themes/ozonedoc/static/js/jquery-3.5.1.min.js -->
# sources/object-store/apache-ozone/hadoop-hdds/docs/themes/ozonedoc/static/js/jquery-3.5.1.min.js

## Purpose
This is the minified jQuery v3.5.1 library vendored into the `ozonedoc` Hugo theme. It supplies DOM traversal, event handling, AJAX, Deferreds, animation, CSS manipulation, and plugin infrastructure used by Bootstrap and the theme's custom JavaScript.

## Important APIs and functions
- Exposes global `jQuery` and `$` unless loaded in a CommonJS environment.
- Core constructor is `jQuery(...)` / `$()`, backed by `jQuery.fn.init`.
- Provides event APIs including `on`, `one`, `off`, `trigger`, and shorthand methods for common browser events.
- Provides DOM/CSS APIs including selection, traversal, attributes, classes, `css`, dimensions, and effects/animation.
- Provides `ajax`, `Deferred`, `Callbacks`, `parseHTML`, `parseJSON`, `proxy`, `holdReady`, `noConflict`, `type`, `isFunction`, and `isWindow`.

## Control flow
The library initializes through a UMD-style wrapper. In browsers it attaches itself to `window`; in CommonJS it exports a factory or initialized instance depending on whether a document exists. It then defines utility functions, selector/DOM logic, event dispatch, data management, queues, AJAX transports, effects, and finally global assignment plus `noConflict` restoration.

## State and persistence
jQuery stores transient state in memory: event handlers, data caches, queues, Deferred state, and references to previous global `$`/`jQuery` values for `noConflict`. It does not persist to localStorage/sessionStorage or server state by itself.

## Dependencies and integration points
This file is a foundational browser dependency for `bootstrap.min.js` and `ozonedoc.js`. It depends on a browser `window.document` for normal operation. Theme pages must load it before Bootstrap and before scripts that use `$`.

## Risks and edge cases
- jQuery 3.5.1 is older and should be tracked as a third-party dependency for known CVEs and browser compatibility.
- Duplicate jQuery loads can overwrite plugin registrations or break `noConflict` expectations.
- Minified vendored code should not be locally edited except for full-version replacement from upstream.
- Bootstrap 3 requires jQuery below version 4, so jQuery upgrades must also account for Bootstrap compatibility.

## Test signals
Browser smoke tests should verify no console errors, `$`/`jQuery` availability before Bootstrap loads, document-ready callbacks firing, event binding working, and Bootstrap plugins registering on `jQuery.fn`. Dependency scans should record jQuery version 3.5.1 and its license.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/docs/themes/ozonedoc/static/js/jquery-3.5.1.min.js -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/docs/themes/ozonedoc/static/js/ozonedoc.js -->
# sources/object-store/apache-ozone/hadoop-hdds/docs/themes/ozonedoc/static/js/ozonedoc.js

## Purpose
This small custom theme script applies Bootstrap table styling to all tables in generated Ozone documentation pages.

## Important functions and APIs
- Uses jQuery's document-ready shorthand: `$(function(){ ... })`.
- Selects all `table` elements.
- Calls `.addClass("table table-condensed table-bordered table-striped")`.

## Control flow
When the DOM is ready, the callback runs once, finds every table in the document, and adds Bootstrap 3 classes. This makes Markdown-generated tables adopt Bootstrap's table styling without requiring authors to add classes manually.

## State and persistence
The only state change is DOM mutation in the current page: class names are added to table elements. There is no persistent storage and no network activity.

## Dependencies and integration points
This depends on jQuery and Bootstrap CSS. It complements `jquery-3.5.1.min.js` and `bootstrap.min.js` in the `ozonedoc` theme. It integrates with Hugo-rendered Markdown content because Markdown tables become plain HTML `table` elements.

## Risks and edge cases
- It styles every table globally, including any table-like layout or third-party widget that may not be intended to use Bootstrap table classes.
- If jQuery fails to load, this script fails because `$` is undefined.
- It does not handle tables inserted after DOM ready; dynamically added content would need another call or delegated handling.
- The script assumes Bootstrap 3 class names; Bootstrap major-version upgrades may require different class choices.

## Test signals
Build a docs page with a Markdown table and confirm the generated table has `table`, `table-condensed`, `table-bordered`, and `table-striped` classes after page load. Also verify no console error occurs when scripts load in theme order.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/docs/themes/ozonedoc/static/js/ozonedoc.js -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/docs/themes/ozonedoc/static/swagger-resources/recon-api.yaml -->
# sources/object-store/apache-ozone/hadoop-hdds/docs/themes/ozonedoc/static/swagger-resources/recon-api.yaml

## Purpose
This OpenAPI 3.0 document describes the Apache Ozone Recon REST API exposed under `/api/v1/`. It is a static documentation/specification artifact used by the docs theme, Swagger tooling, client readers, and possibly contract validation. It covers administrative metadata APIs for containers, keys, blocks, namespace state, datanodes, pipelines, Recon tasks, utilization, Prometheus metrics proxying, storage distribution, pending deletion, heatmap features, and manual DB sync utilities.

## Important API surface
- Metadata root: `openapi: 3.0.0`, `info.title: Ozone Recon REST API`, `version: v1`, server URL `/api/v1/`.
- 48 operations are defined across 19 tags.
- Container APIs include listing containers, deleted containers, missing/unhealthy/quasi-closed containers, replica history, mismatch reports, deleted-in-SCM mismatch reports, and keys by container.
- Async unhealthy-container export lifecycle includes listing jobs, starting jobs, checking status, cancelling jobs, and downloading completed TAR archives.
- Volume, bucket, key, and block APIs expose paginated listings and summaries for open keys, multipart open keys, pending-deletion keys/directories, committed key listing under a prefix, and pending block deletion.
- Namespace APIs expose summary, disk usage, quota, and file-size distribution by path.
- Cluster APIs expose cluster state, datanodes, decommissioning information, datanode removal, pipelines, Recon task status, file/container utilization, and Prometheus metrics proxy responses.
- Feature and admin APIs include heatmap read access and health check, disabled feature introspection, OM DB sync trigger, SCM DB snapshot sync trigger/status/cancel, storage distribution, pending deletion by component, and CSV download of datanode storage distribution.
- 60 schemas are defined, including `ContainerMetadata`, `UnhealthyContainerMetadata`, `ListKeysResponse`, `NamespaceMetadataResponse`, `ClusterState`, `DatanodeDetails`, `ExportJob`, `StorageCapacityDistributionResponse`, `DataNodeMetricsServiceResponse`, `EntityReadAccessHeatMap`, and SCM snapshot sync response/status enums.

## Control flow and API behavior
Most endpoints are synchronous GET reads over Recon-maintained metadata, with pagination using cursors such as `prevKey`, `lastKey`, `minContainerId`, and `limit`. Several operations are stateful asynchronous workflows:
- `POST /containers/unhealthy/export` queues an export job for a required unhealthy container state, returning an `ExportJob`; later calls poll `/containers/unhealthy/export/{jobId}`, cancel via DELETE, or download from `/download` after completion. Responses include rate limiting, not-found, conflict, and download-limit cases.
- `GET /pendingDeletion?component=dn` and `GET /storageDistribution/download` may trigger or poll background datanode metrics collection, returning `202` until collection is complete and `200` with JSON or CSV when finished.
- `POST /triggerdbsync/scm/snapshot` starts a one-shot SCM DB snapshot sync with `202` on accepted and `409` if one is already running; status and cancel endpoints expose sync phase, cancellation eligibility, timestamps, and errors.
- Heatmap read access is feature-gated: if disabled, `/heatmap/readaccess` returns `404`, and `/features/disabledFeatures` exposes disabled feature names.

## State and persistence behavior
The spec itself is static YAML, but it documents APIs backed by persistent Recon state: OM/SCM metadata snapshots, Recon DB tables, datanode memory/nodes table, task status, Prometheus metrics, export job files, background metrics collection status, and SCM snapshot sync state. Export jobs persist identifiers, status, timestamps, progress counters, filenames, download counters, and download limits. Snapshot sync status persists current/last status, phase, timestamps, duration, cancellation permission, and last error.

## Dependencies and integration points
The file integrates with Swagger/OpenAPI renderers in the documentation site, Recon server route implementations, Ozone OM/SCM metadata, Prometheus for metrics proxying, HeatMapProvider service for heatmap data, datanodes for storage/pending-deletion metrics, and admin tooling that triggers sync operations. It also depends on OpenAPI clients correctly handling `oneOf`, binary `application/x-tar` and `text/csv` responses, deprecated endpoints, and status codes like `202`, `204`, `400`, `404`, `409`, `429`, `500`, and `503`.

## Schema highlights
- `OpenKeys`, `DeletePendingKeys`, `DeletePendingDirs`, and `ListKeysResponse` carry status and byte-size aggregates alongside lists of OM key information.
- `NamespaceMetadataResponse`, `MetadataDiskUsage`, `MetadataQuota`, and `MetadataSpaceDist` encode namespace statuses such as OK/not found/not applicable through response fields rather than only HTTP status.
- `ClusterState` aggregates container/key/bucket/volume counts, service IDs, datanode health, pipeline count, and storage report details.
- `DataNodeStorageReport`, `ClusterStorageReport`, and `StorageCapacityDistributionResponse` distinguish filesystem capacity, reserved space, Ozone capacity, used/free/committed space, namespace usage, and per-datanode reports.
- `ExportJob` captures queue and download policy with statuses `QUEUED`, `RUNNING`, `COMPLETED`, and `FAILED`.
- `ScmDbSnapshotSyncStatus` is one of `IDLE`, `IN_PROGRESS`, `SUCCESS`, `FAILED`, `CANCELLED`; `ScmDbSnapshotSyncPhase` refines cancellation and progress phases.

## Risks and edge cases
- Many admin-only endpoints expose sensitive metadata or actions; the spec labels them but does not define security schemes, so access control must be enforced by server configuration and implementation.
- Some endpoints return semantic status in JSON bodies while still returning HTTP `200`, which clients must not treat as unconditional success.
- Pagination parameters vary by endpoint (`prevKey`, `lastKey`, `firstKey`, `minContainerId`) and types differ between string and integer; client generators need endpoint-specific handling.
- `/containers/missing` is deprecated in favor of `/containers/unhealthy/MISSING`; clients should migrate.
- Binary responses (`application/x-tar`, `text/csv`) require separate client handling from JSON endpoints.
- Background task endpoints can return `202` and nullable result arrays; clients must poll and tolerate incomplete data.
- OpenAPI schema coverage includes broad object maps and loosely typed fields, so generated clients may not fully enforce server contracts.

## Test signals
Validate the YAML with an OpenAPI 3 parser and render it through the docs Swagger UI. Contract tests should compare documented paths, operation IDs, parameters, response codes, and schema fields with Recon server route implementations. Client behavior tests should cover pagination, deprecated missing-container replacement, invalid parameters (`400`/`406`), export job lifecycle including `429` and `409`, heatmap disabled `404`, pending-deletion `202` polling, SCM snapshot sync `202`/`409`/cancel behavior, binary download content types, and `503` while Recon is bootstrapping OM DB.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/docs/themes/ozonedoc/static/swagger-resources/recon-api.yaml -->
