<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/docs/themes/ozonedoc/static/swagger-resources/swagger-ui-standalone-preset.js -->
# sources/object-store/apache-ozone/hadoop-hdds/docs/themes/ozonedoc/static/swagger-resources/swagger-ui-standalone-preset.js

## Purpose
This is a vendored, minified Swagger UI standalone preset bundle for the Ozone documentation theme. It exposes `SwaggerUIStandalonePreset` through a UMD wrapper so the same artifact can be consumed by CommonJS, AMD, browser globals, or the local Swagger UI initialization code used by the docs site.

## Important APIs, Types, And Functions
- The top-level UMD wrapper exports `SwaggerUIStandalonePreset`.
- The preset array registers Swagger UI plugins for the standalone view, including `Topbar`, `Logo`, `StandaloneLayout`, `ErrorBoundary`, `Fallback`, and wrapping for `Topbar`, `StandaloneLayout`, and `onlineValidatorBadge`.
- The bundled config state plugin exposes actions equivalent to config update/toggle behavior and selectors such as `getLocalConfig`.
- `getLocalConfig` returns a default YAML configuration containing the Petstore spec URL, `#swagger-ui` DOM target, and the public Swagger validator URL.
- The bundle includes minified third-party runtime code for React components, object helpers, URL/config parsing, YAML parsing, and browser polyfills such as Buffer/base64 helpers.

## Control Flow
The file initializes immediately when loaded. The wrapper detects the module system, invokes the bundled factory, and returns a preset array. Swagger UI later consumes the preset by invoking its plugin factories. Those factories register components, state plugins, selectors, reducers, and wrapper components. Config loading flows through a fetch action that downloads a YAML config, parses it, updates loading status on failure, clears the URL, and logs errors to the browser console.

## State And Persistence
The file does not write durable application state. It contributes runtime Redux-like Swagger UI state through config reducers and selectors once the docs page loads. Browser-visible state includes config values, loading status, wrapped component error state, and rendered Swagger UI component state. Persistence is limited to the static asset itself and any browser cache of the generated documentation site.

## Dependencies And Integration Points
This asset lives beside `swagger-ui-bundle.js`, `swagger-ui.css`, `recon-api.yaml`, and favicon assets under the Ozone Hugo theme static tree. It integrates with the generated documentation pages that mount Swagger UI into `#swagger-ui`. It depends on the compatible Swagger UI bundle/runtime being loaded by the page, browser APIs such as `fetch`, and the static OpenAPI YAML resource. The source map comment references `swagger-ui-standalone-preset.js.map`, but that map is not present in the same directory.

## Risks And Edge Cases
Because the bundle is minified and vendored, local patches are difficult to review and are likely to be overwritten by Swagger UI upgrades. The default Petstore URL and public validator URL can leak through if page initialization does not override them with Ozone-specific config. The missing source map makes browser debugging harder. Security-sensitive behavior, including URL sanitization and YAML parsing, should track upstream Swagger UI versions rather than local edits. Any version mismatch between this preset, `swagger-ui-bundle.js`, and `swagger-ui.css` can break component names or plugin contracts at runtime.

## Test Signals
Useful validation signals include loading the generated documentation Swagger page, confirming the Ozone/OpenAPI spec renders in `#swagger-ui`, checking that the top bar and standalone layout render without console errors, verifying no network request goes to the default Petstore spec during normal Ozone docs usage, and confirming static site packaging includes this file together with compatible Swagger UI assets.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/docs/themes/ozonedoc/static/swagger-resources/swagger-ui-standalone-preset.js -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/docs/themes/ozonedoc/theme.toml -->
# sources/object-store/apache-ozone/hadoop-hdds/docs/themes/ozonedoc/theme.toml

## Purpose
This is the Hugo theme metadata file for the Ozone documentation theme. It identifies the theme as `Ozonedoc` so Hugo can discover and refer to the theme by name.

## Important APIs, Types, And Functions
- The only TOML key is `name = "Ozonedoc"`.
- There are no executable functions or reusable types.

## Control Flow
There is no local control flow. Hugo reads the metadata during site/theme discovery and uses it as descriptive theme configuration.

## State And Persistence
The file persists static theme metadata in source control. It does not maintain runtime state, generated state, or caches.

## Dependencies And Integration Points
The integration point is Hugo's theme loading and the surrounding Ozone documentation tree under `docs/themes/ozonedoc`. The file should remain valid TOML and should stay aligned with any site configuration that names or packages the theme.

## Risks And Edge Cases
The small size means syntax errors are the main operational risk. Renaming the theme can break Hugo configuration, theme packaging, or documentation build scripts that expect `Ozonedoc`. Additional metadata fields should follow Hugo theme conventions if this theme is later published or validated by external tooling.

## Test Signals
Run the Ozone documentation build with the `ozonedoc` theme selected. A successful Hugo build and correct theme resolution are the primary signals.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/docs/themes/ozonedoc/theme.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/dev-support/findbugsExcludeFile.xml -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/dev-support/findbugsExcludeFile.xml

## Purpose
This SpotBugs/FindBugs exclusion file suppresses a known warning in the HDDS erasure-code module. It excludes `MS_EXPOSE_REP` for `org.apache.ozone.erasurecode.rawcoder.util.GF256`, allowing the module's static-analysis run to pass despite that class exposing a representation that is accepted for this implementation.

## Important APIs, Types, And Functions
- Root element: `FindBugsFilter`.
- One `Match` block targets `Class name="org.apache.ozone.erasurecode.rawcoder.util.GF256"`.
- The suppressed bug pattern is `MS_EXPOSE_REP`.

## Control Flow
There is no runtime control flow. During Maven SpotBugs execution, the plugin reads this filter and omits matching findings from the module report. All other findings remain eligible for reporting or build failure according to the parent build configuration.

## State And Persistence
The file persists static-analysis policy for the erasure-code module. It does not affect application runtime state, but it changes the persisted quality gate behavior for every build that uses this module's SpotBugs configuration.

## Dependencies And Integration Points
The module POM wires this file through `spotbugs-maven-plugin` using `${basedir}/dev-support/findbugsExcludeFile.xml`. It depends on SpotBugs filter XML syntax and the exact fully qualified class and bug pattern names. It integrates with the broader HDDS Maven build and CI static-analysis checks.

## Risks And Edge Cases
The suppression is narrow, but it can still hide a real representation exposure if `GF256` changes and the original justification no longer applies. Class renames or package moves can silently make the exclusion ineffective. Expanding this file without review would weaken the static-analysis signal for low-level erasure-code arithmetic.

## Test Signals
Run the erasure-code module SpotBugs goal through Maven and confirm the filter file is loaded and only the intended `GF256` `MS_EXPOSE_REP` warning is suppressed. A build should still fail or report unrelated SpotBugs findings.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/dev-support/findbugsExcludeFile.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/pom.xml -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/pom.xml

## Purpose
This Maven POM defines the `hdds-erasurecode` jar module in Apache Ozone HDDS. It inherits dependency and plugin management from `hdds-hadoop-dependency-client`, declares erasure-code runtime and test dependencies, and applies module-local SpotBugs and compiler configuration.

## Important APIs, Types, And Functions
- Maven coordinates: parent `org.apache.ozone:hdds-hadoop-dependency-client:2.3.0-SNAPSHOT`, artifact `hdds-erasurecode`, packaging `jar`.
- Runtime dependencies include Guava, Hadoop Common, `hdds-common`, and `slf4j-api`.
- Test dependencies include Apache Commons Lang3 and `hdds-config`.
- `spotbugs-maven-plugin` uses `dev-support/findbugsExcludeFile.xml` as the module exclusion filter.
- `maven-compiler-plugin` sets `<proc>none</proc>`, disabling annotation processing for this module build.

## Control Flow
The build starts from the parent POM, resolves dependency versions and plugin defaults from parent management, then builds this module as a jar. SpotBugs applies the module filter file when static analysis runs. Java compilation proceeds without annotation processing, which keeps the erasure-code module independent of annotation processors that may be configured elsewhere in the reactor.

## State And Persistence
The POM persists module metadata, dependency declarations, and build behavior. Build outputs are Maven target artifacts: compiled classes, test classes, reports, and the `hdds-erasurecode` jar. It does not define runtime persistence for Ozone services.

## Dependencies And Integration Points
This module integrates with the HDDS/Ozone Maven reactor through its parent and sibling dependencies. Hadoop Common provides native erasure-code classes used by bridge code such as `HadoopNativeECAccessorUtil`; `hdds-common` supplies Ozone/HDDS annotations and shared client types; SLF4J backs module logging; Guava is used by tests and implementation code such as `CodecRegistry` annotations. The module's service-provider resources participate in `ServiceLoader` discovery at runtime.

## Risks And Edge Cases
The description contains a typo (`Earsurecode`), which is harmless but visible in generated project metadata. Dependency versions are inherited, so parent changes can alter native Hadoop EC compatibility or static-analysis behavior. Disabling annotation processing is intentional but can surprise future code that expects generated sources. The SpotBugs exclusion path is based on `${basedir}`, so moving the filter file or module layout breaks the configured suppression.

## Test Signals
Run `mvn -pl hadoop-hdds/erasurecode test` or the equivalent reactor path to compile the module and execute tests. Static-analysis validation should include the SpotBugs plugin using the module filter. Integration signals include successful `ServiceLoader` registration tests for erasure-code factories and native/non-native coder fallback tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/HadoopNativeECAccessorUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/HadoopNativeECAccessorUtil.java

## Purpose
This private utility bridges Ozone erasure-code wrappers to protected Hadoop native erasure-code implementation methods. It is placed in the Hadoop rawcoder package so it can access package/protected native encoder and decoder methods until Ozone adapts the native EC code directly.

## Important APIs, Types, And Functions
- `performEncodeImpl(NativeRSRawEncoder, ByteBuffer[], int[], int, ByteBuffer[], int[])` delegates Reed-Solomon native encoding.
- `performDecodeImpl(NativeRSRawDecoder, ByteBuffer[], int[], int, int[], ByteBuffer[], int[])` delegates Reed-Solomon native decoding.
- `performEncodeImpl(NativeXORRawEncoder, ByteBuffer[], int[], int, ByteBuffer[], int[])` delegates XOR native encoding.
- `performDecodeImpl(NativeXORRawDecoder, ByteBuffer[], int[], int, int[], ByteBuffer[], int[])` delegates XOR native decoding.
- The class is `final`, has a private constructor, and is annotated `@InterfaceAudience.Private`.

## Control Flow
Each public static method immediately forwards all buffers, offsets, data length, erased indexes, and output arrays to the corresponding Hadoop native encoder or decoder method. The utility performs no validation, copying, retry, fallback, or transformation. Any `IOException` from Hadoop native code is propagated to the caller.

## State And Persistence
The class is stateless. It mutates only the output `ByteBuffer` contents through the delegated native operations. It does not retain references, cache native handles, or persist metadata.

## Dependencies And Integration Points
The utility depends on Hadoop's `NativeRSRawEncoder`, `NativeRSRawDecoder`, `NativeXORRawEncoder`, and `NativeXORRawDecoder` classes, plus Java NIO `ByteBuffer`. Ozone native wrapper classes (`NativeRSRawEncoder`, `NativeRSRawDecoder`, `NativeXORRawEncoder`, and `NativeXORRawDecoder` in the `org.apache.ozone.erasurecode.rawcoder` package) call this utility from their protected implementation methods. The module POM's Hadoop Common dependency supplies the Hadoop native classes.

## Risks And Edge Cases
This file relies on a package-level access workaround by using the Hadoop package name inside the Ozone module. Hadoop API changes to method signatures, visibility, or package structure can break compilation. Because all validation is delegated, malformed offset arrays, buffer sizing mistakes, direct-vs-heap buffer issues, or native library linkage errors surface from lower layers. The bridge should stay minimal; adding behavior here could diverge from Hadoop native EC semantics.

## Test Signals
Native erasure-code encode/decode tests should exercise both RS and XOR wrappers, including fallback behavior when native code is unavailable. Compilation against the selected Hadoop Common version is itself an important compatibility signal. ByteBuffer round-trip tests with erased indexes verify that offsets and data length are passed through correctly.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/HadoopNativeECAccessorUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/CodecRegistry.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/CodecRegistry.java

## Purpose
`CodecRegistry` is the private singleton registry that maps erasure-code codec names to available raw erasure coder factories. It discovers factories with `ServiceLoader`, orders native implementations before Java implementations, prevents duplicate coder names for the same codec, and exposes lookup methods used by coder creation utilities.

## Important APIs, Types, And Functions
- `getInstance()` returns the eagerly initialized singleton.
- `updateCoders(Iterable<RawErasureCoderFactory>)` registers discovered or test-provided factories and rebuilds the codec-to-coder-name cache.
- `getCoderNames(String codecName)` returns the registered coder-name array for a codec, or `null` if absent.
- `getCoders(String codecName)` returns the registered factory list for a codec, or `null` if absent.
- `getCodecNames()` returns the set of registered codec names.
- `getCoderByName(String codecName, String coderName)` scans a codec's factories for a matching coder name.
- `getCodecFactory(String codecName)` returns the first factory for a codec, effectively the preferred factory, or throws `IllegalArgumentException` if none is registered.

## Control Flow
Class initialization eagerly constructs the singleton, creates empty `HashMap` instances, loads `RawErasureCoderFactory` providers through `ServiceLoader`, and calls `updateCoders`. Registration iterates each factory, groups it by `getCodecName()`, checks for duplicate `getCoderName()` values within that codec, logs conflicts, and skips conflicting entries. Native RS and native XOR factories are inserted at index 0 to make them preferred; other factories append after existing factories. After registration, `coderNameMap` is cleared and rebuilt from `coderMap` so name arrays reflect the current ordering. Lookup methods then read these maps directly.

## State And Persistence
The singleton maintains in-memory mutable maps for the life of the JVM: `coderMap` maps codec names to ordered factory lists, and `coderNameMap` maps codec names to ordered coder-name arrays. There is no durable persistence. `updateCoders` mutates global registry state, which is useful for tests but affects all subsequent lookups in the same JVM.

## Dependencies And Integration Points
The registry depends on Java `ServiceLoader`, SLF4J logging, Guava's `@VisibleForTesting`, HDDS `@InterfaceAudience.Private`, and the `RawErasureCoderFactory` SPI. The service file `META-INF/services/org.apache.ozone.erasurecode.rawcoder.RawErasureCoderFactory` lists RS, XOR, native RS, and native XOR factories. `CodecUtil` uses `getCoderNames` and `getCoderByName` to create encoders/decoders with fallback. Tests in `TestCodecRegistry` verify codec discovery, native-first ordering, duplicate suppression, wrong-codec behavior, and named lookups.

## Risks And Edge Cases
Several lookup methods expose mutable internal data: callers can mutate returned lists or the codec name set, and returned arrays are not defensive copies. `getCoderByName` iterates `getCoders(codecName)` without a null check, so an unknown codec can throw `NullPointerException` instead of returning `null`; current tests only cover wrong coder names for known codecs. `getCodecFactory` also assumes `getCoders(codecName)` is non-null before throwing its own exception, so an unknown codec may not get the intended error path. The singleton maps are plain `HashMap`/`ArrayList` and `updateCoders` is unsynchronized, so concurrent test or plugin registration could race with lookups. The variable `hasConflit` is misspelled, which is cosmetic but lowers readability.

## Test Signals
`TestCodecRegistry` is the main unit-test signal. It checks registered codec names, expected native-first coder order for RS and XOR, `null` for `getCoders("WRONG_CODEC")`, duplicate coder-name suppression via `updateCoders`, and named lookup for all built-in factories. Additional useful tests would cover `getCoderByName` with an unknown codec, `getCodecFactory` with an unknown codec, immutability expectations for returned collections, and repeated `updateCoders` calls in the same JVM.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/CodecRegistry.java -->
