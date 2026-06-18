# sources/test-tools/lcov/tests/xml2lcov/coverage.xml lines 1-2794

## Scope And Purpose

This chunk covers the first 2,794 lines of the Cobertura XML fixture used by the `xml2lcov` tests. The full file is `sources/test-tools/lcov/tests/xml2lcov/coverage.xml`, but this work item stops in the middle of the `org.jasig.portal.RDBMUserIdentityStore$8$1` class, so the chunk is not a complete XML document on its own.

The fixture starts with a Cobertura `coverage-04.dtd` declaration and a top-level `<coverage>` element reporting aggregate rates from a reduced uPortal coverage export: line rate `0.21974657217686028`, branch rate `0.14609273761902078`, `11411/51928` lines covered, `2593/17749` branches covered, complexity `2.054109364767518`, version `2.0.3`, and timestamp `1403301904999`. Test comments in `xml2lcov.sh` state that this file is a trimmed copy of a larger public Cobertura report and that removed packages were not significant for the testcase.

The fixture exists to exercise `sources/test-tools/lcov/bin/xml2lcov` and its parser/writer helper `xml2lcovutil.py`. It gives the converter realistic Cobertura structure, source path lookup failures, Java method signatures, empty method bodies, generated class names, interfaces with no line data, nested anonymous classes, branch condition coverage strings, and internally inconsistent function data that later `lcov -a` must aggregate with `--ignore inconsistent`.

## XML Structure In This Chunk

The covered range contains:

- `5` package elements.
- `34` class elements.
- `159` method elements.
- `1272` `<line>` elements.
- `163` branch line elements with `branch="true"` and `condition-coverage`.
- `152` XML elements with positive `hits` values.

The `<sources>` section lists four source roots:

- `/Users/apetro/code/github_jasig/uPortal/uportal-war/target/generated-sources/annotations`
- `/Users/apetro/code/github_jasig/uPortal/uportal-war/target/generated-sources/xjc`
- `--source`
- `/Users/apetro/code/github_jasig/uPortal/uportal-war/src/main/java`

These are intentionally not normal paths in this repository. `xml2lcovutil.ProcessFile.process_xml_file()` tries to join each Cobertura class filename to each source path and prints "did not find ..." when the file is absent. That means this fixture tests translation without local source availability, and separately tests failure when a version script needs source metadata.

The package/class coverage covered by this chunk is:

- `org.apache.commons.math3.stat.descriptive.moment`: generated metamodel-style classes `FirstMoment_` and `SecondMoment_`, each with only an uncovered constructor line.
- `org.apache.commons.math3.stat.descriptive.rank`: generated `Max_` and `Min_`, also constructor-only and uncovered.
- `org.apache.commons.math3.stat.descriptive.summary`: generated `SumOfLogs_`, `SumOfSquares_`, and `Sum_`, constructor-only and uncovered.
- `org.hibernate.cache.ehcache`: `SpringBeanEhCacheRegionFactory`, with many empty methods plus uncovered constructor/start/stop lines and branch records.
- `org.jasig.portal`: the main bulk of the chunk, including exception classes, interfaces, entity metadata helpers, portal info resolution, RDBMS utility functions, and most of `RDBMUserIdentityStore` plus nested callback/transaction classes.

## Converter-Relevant APIs And Fields

This file is data, not executable code. The important "APIs" are the XML fields that the converter consumes:

- `<coverage>` attributes provide aggregate Cobertura metrics, but `xml2lcovutil.py` does not use them directly when writing LCOV records.
- `<sources>/<source>` entries are search roots for resolving each class `filename`.
- `<package name="...">` controls whether a class is considered external. A package name starting with `.` and not equal to `.` is treated as external by `xml2lcovutil.py`; all package names in this chunk are internal.
- `<class name="..." filename="..." line-rate="..." branch-rate="..." complexity="...">` supplies the LCOV source file path candidate through `filename`. The converter ignores class-level aggregate rates and complexity for output totals.
- `<methods>/<method name="..." signature="..." line-rate="..." branch-rate="...">` provides function records. The converter uses `name`, first executable line, last executable line, and first line hit count to emit `FNL` and `FNA` records. JVM signatures are present but are not included in the emitted function name.
- `<lines>/<line number="..." hits="..." branch="...">` provides the executable line records that become LCOV `DA` records.
- `condition-coverage="P% (M/N)"` plus nested `<conditions>` provides branch counts. The converter parses only the `M/N` tuple and emits `M` taken `BRDA` records followed by `N-M` untaken records for that source line.

The fixture includes XML-escaped Java constructor names as `&lt;init&gt;` and class initializer names as `&lt;clinit&gt;`. After XML parsing these become `<init>` and `<clinit>`, so downstream LCOV function names can contain angle brackets unless later filtering or report code handles them.

## Main Control Flow Exercised

`xml2lcov.sh` runs `xml2lcov` against this fixture several times:

- A normal conversion to `test.info` with verbose flags, expecting success even though source files are not found.
- A second verbose conversion to exercise logging paths.
- A conversion with `--version-script`, expecting failure because the fixture's source roots do not resolve in the test checkout.
- Usage and argument-error paths around missing input, missing files, unsupported parameters, and malformed version-script arguments.
- An `lcov -a test.info --ignore inconsistent` aggregation pass used as a syntax and compatibility check.

For this XML, `ProcessFile.process_xml_file()` parses the root with `ElementTree`, verifies that child `0` is `sources` and child `1` is `packages`, records source paths, iterates packages/classes, applies optional class filename exclusion patterns, attempts to resolve the class filename against each source path, writes `SF:<name>`, optionally writes `VER:<version>`, delegates the class body to `process_file()`, and then writes `end_of_record`.

Inside `process_file()`, method records are first converted into an in-memory function list. For each method with line data, the first method line becomes the function start, the last method line becomes the function end, and the first method line's hit count becomes the function hit count. Empty methods, which appear often in `SpringBeanEhCacheRegionFactory` and synthetic accessors, are elided with verbose logging rather than written as LCOV functions.

The class-level `<lines>` element is then translated into `DA` records and summary totals. Branch lines with `condition-coverage` are expanded into synthetic LCOV branch slots because Cobertura does not identify which branch expression was hit. This fixture deliberately contains many `0% (0/2)`, `50% (1/2)`, and one multi-condition `0% (0/6)` style record, which exercises that lower-bound branch translation.

## Covered Classes And Behavioral Signals

The initial Commons Math generated classes are low-noise coverage records. They verify that generated filenames under `org/apache/commons/math3/...` are translated and that simple uncovered constructors become line and function records.

`SpringBeanEhCacheRegionFactory` is a compact branch and empty-method case. Its empty Hibernate cache-region builder methods have no `<line>` children and should not produce LCOV function records. Its `start` method has uncovered branch lines at Java lines 47 and 52, while `stop`, `isMinimalPutsEnabledByDefault`, and the constructor provide plain uncovered line records.

`AuthorizationException`, `Constants`, and `PortalException` provide overloaded constructor coverage. `PortalException` mixes covered and uncovered constructors, so it checks function hit derivation from the first line of each method rather than from class-level line rates.

`EntityIdentifier` and `EntityTypes` exercise simple methods and branch misses. `EntityIdentifier.<init>` is hit 71 times, while equality branches are uncovered. `EntityTypes` has static initialization, setters, singleton access, DAO/counter integration methods, and `addEntityTypeIfNecessary` branch records. `EntityTypes$1` adds duplicate `mapRow` methods with different return types/signatures but the same XML method name, which is a known inconsistency noted by `xml2lcov.sh`.

Interfaces such as `IBasicEntity`, `IOIDGenerator`, `IPortalInfoProvider`, `ISequenceGenerator`, `IUserIdentityStore`, `IUserPreferencesManager`, and `IUserProfile` have empty `<methods>` and `<lines>` blocks with `line-rate="1.0"`. They check that interface-only Cobertura classes can pass through without DA/FN data.

`PortalInfoProviderImpl` provides a dense branch-miss cluster around server name and network-interface resolution. Methods such as `doInReadLock`, `getDefaultNetworkInterfaceName`, `getNetworkInterfaceName`, `getNetworkInterfaceNames`, and `resolveServerName` include multiple uncovered branch lines, while getters/setters are also uncovered. This stresses branch parsing independent of positive line hits.

`RDBMServices` covers static JDBC utility methods such as `closeResultSet`, `closeStatement`, `commit`, `dbFlag`, `getConnection`, `getDataSource`, `releaseConnection`, `rollback`, `setAutoCommit`, and `sqlEscape`. In this chunk they are largely uncovered and branch-heavy, exercising conversion of exception-handling/control-flow utility code into many synthetic `BRDA` records.

`RDBMUserIdentityStore` is the largest class in the chunk. It includes positive-hit records for static initialization, construction, lock access, portal UID lookup, template-name/default-user checks, DAO setter methods, and the `RDBMUserIdentityStore$1` cache entry factory. It also includes many uncovered database, group-membership, transaction, add/update/remove-user, rollback/commit, and saved-layout paths.

Nested `RDBMUserIdentityStore` classes `$2` through `$8$1` exercise anonymous transaction and JDBC callback shapes. `$4` has mostly covered portal-user lookup data with partial branch coverage, while `$5`, `$6`, `$7`, `$7$1`, `$8`, and `$8$1` are mostly uncovered. The requested chunk ends while listing branch conditions for `$8$1.doInConnection`, so the merge lane must combine this with later chunks for the complete XML/file picture.

## State And Persistence Behavior

The XML fixture itself is static test input and has no runtime state. Its persistence behavior is the Cobertura XML schema: nested package/class/method/line elements persist source filenames, source search roots, hit counts, branch flags, and condition coverage strings.

When consumed by `xml2lcov`, the persistent output is LCOV `.info` text. Each class becomes one `SF` record using either a resolved source path or the original Cobertura `filename`. Each class-level line becomes a `DA` record, method line ranges become indexed `FNL`/`FNA` records, Cobertura branch summaries become `BRDA` records, and each class ends with `end_of_record`. Optional `--checksum` would add line hashes, but the xml2lcov test path for this fixture mainly exercises no-source behavior.

The fixture intentionally causes source-path state to remain unresolved in the test environment. `ProcessFile` tracks a usage count for each `<source>` entry and prints a warning for unused source paths after parsing, which is expected here because the absolute uPortal paths are not present.

## Dependencies And Integration Points

This fixture integrates with:

- `sources/test-tools/lcov/tests/xml2lcov/xml2lcov.sh`, the direct test driver.
- `sources/test-tools/lcov/bin/xml2lcov`, the CLI wrapper that handles arguments and instantiates `ProcessFile`.
- `sources/test-tools/lcov/bin/xml2lcovutil.py`, the Cobertura-to-LCOV translator.
- `xml.etree.ElementTree`, which parses XML entities and tree structure.
- LCOV's later `.info` parser and merger, because `xml2lcov.sh` aggregates the generated `test.info` with `lcov -a`.
- Version callback scripts in `tests/common.tst` and related test support, because `--version-script` is expected to fail for this fixture without real source files.

The source filenames point at Java files from uPortal, Commons Math generated annotation-model classes, Hibernate cache integration, and Spring/JDBC transaction callbacks. Those Java files are not dependencies of the test checkout; they are names embedded in coverage data to test conversion fidelity.

## Risks And Edge Cases

The biggest fixture-specific risk is that the XML is large and partly inconsistent by design. `xml2lcov.sh` explicitly notes inconsistent data for `org/jasig/portal/EntityTypes.java`, where function `mapRow` appears at different locations and overlaps a previous declaration. Tests must preserve that inconsistency because it checks LCOV's `--ignore inconsistent` path.

Cobertura branch data is lossy. This fixture includes many branch summaries, but the converter cannot know which exact Java condition was taken. It assumes the first `M` synthetic branch slots were taken and the remaining slots were not. Merged output is therefore a lower bound, not an exact branch identity model.

Empty methods and empty classes are significant. Removing them from the fixture could weaken coverage of the converter's "elided empty function" behavior, while accidentally treating them as real functions would inflate FNF/FNH totals.

The `<source>--source</source>` entry is unusual. Because the converter blindly joins source roots to filenames, option-looking source text must remain data, not command-line syntax. Current code uses `os.path.join` and does not shell out for path resolution, so this is safe in the conversion path.

The chunk boundary is mid-record. Research or validation that assumes this chunk is a standalone XML file would fail. It should be treated as a source-file segment whose complete XML balancing is handled by adjacent chunks and final reconciliation.

## Test Signals

Strong tests around this fixture should verify:

- `xml2lcov -o test.info coverage.xml -v -v` succeeds without local source files.
- `xml2lcov --version-script ... coverage.xml` fails when source versions cannot be computed, unless keep-going semantics are explicitly being tested.
- Generated `.info` contains `SF` records for unresolved Cobertura filenames rather than fabricated local paths.
- Constructor and overloaded-method entries become stable `FNL`/`FNA` records based on first/last method line and first-line hits.
- Empty methods in `SpringBeanEhCacheRegionFactory`, interfaces, and synthetic accessor methods are elided from function output.
- Branch lines with `condition-coverage` produce the expected number of `BRDA` records and correct hit/total summaries, including `0/2`, `1/2`, and multi-condition cases.
- Positive-hit Java lines in `EntityIdentifier`, `PortalException`, `RDBMUserIdentityStore`, and `$4` nested callback classes survive conversion into `DA` and function-hit totals.
- `lcov -a test.info --ignore inconsistent` accepts the generated output, while the same data without the ignore option may report the intended inconsistency.
- Verbose mode reports source-path checks and unused source path warnings without changing generated coverage data.
