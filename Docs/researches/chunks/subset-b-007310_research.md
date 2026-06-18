# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.19.2.xml lines 43531-44204

## Scope

This chunk is the final segment of the generated JDiff public API snapshot for Hadoop 0.19.2. It is XML API metadata, not Java implementation code. The range begins inside the `org.apache.hadoop.util.StringUtils.hexStringToByte(String)` method entry, then completes `StringUtils`, `StringUtils.TraditionalBinaryPrefix`, `Tool`, `ToolRunner`, `UTF8ByteArrayUtils`, `VersionInfo`, and `XMLUtils`, followed by the closing `</package>` and `</api>` markers.

The XML records public API compatibility surface: class and interface names, inheritance, implemented interfaces, constructors, methods, parameters, declared exceptions, fields, visibility, static/final/abstract/synchronized/native flags, deprecation state, and embedded Javadoc contracts. Because this chunk is API metadata, control flow and state behavior are inferred from signatures and documentation rather than method bodies.

## Purpose and Major API Surface

`StringUtils` is documented as "General string utils" and this tail of the class exposes conversion, formatting, escaping, hostname, startup/shutdown logging, and HTML escaping helpers. The chunk starts with `hexStringToByte(String hex)`, whose method header begins just before this range; its contract converts a hex string into a byte array with length `hex.length/2`. URI and path conversion helpers include `uriToString(URI[] uris)`, `stringToURI(String[] str)`, and `stringToPath(String[] str)`, bridging string configuration values with Java `URI` and Hadoop `Path` arrays.

Time formatting helpers include `formatTimeDiff(long finishTime, long startTime)`, `formatTime(long timeDiff)`, and `getFormattedTimeWithDiff(DateFormat dateFormat, long finishTime, long startTime)`. `formatTimeDiff` returns an elapsed-time string in hours, minutes, and seconds and explicitly allows negative components when `finishTime` precedes `startTime`. `getFormattedTimeWithDiff` formats a finish timestamp and appends the elapsed difference when a start time is present; if `finishTime` is `0`, the method returns an empty string.

Comma-separated string helpers include `getStrings(String str)`, `getStringCollection(String str)`, two `split` overloads, `findNext(String str, char separator, char escapeChar, int start, StringBuilder split)`, three `escapeString` overloads, and three `unEscapeString` overloads. The default methods use the public constants `COMMA`, `COMMA_STR`, and `ESCAPE_CHAR`, while the overloads allow caller-supplied separator and escape characters or arrays of characters to escape. `findNext` is part of the escaped-splitting contract: it searches for the first unescaped separator starting at an index and returns the extracted segment through a `StringBuilder`.

Host and log/HTML helpers include `getHostname()`, which returns a hostname without throwing; `startupShutdownMessage(Class<?> clazz, String[] args, Log LOG)`, which writes standard startup and shutdown logging for server classes; and `escapeHTML(String string)`, which escapes HTML special characters in a string. These utilities sit at diagnostic and web UI boundaries rather than data-structure boundaries.

`StringUtils.TraditionalBinaryPrefix` is a public static final enum nested under `StringUtils`. It represents traditional binary prefixes from kilo through exa in powers of 1024. Public enum methods include the generated `values()`, `valueOf(String name)`, a Hadoop-specific `valueOf(char symbol)` that maps a prefix symbol case-insensitively, and `string2long(String s)`, which trims and parses strings with optional binary suffixes such as `k` or `g`. The enum exposes public final instance fields `value` (`long`) and `symbol` (`char`).

`Tool` is a public interface extending `org.apache.hadoop.conf.Configurable`. It defines Hadoop's standard command-line application contract through `run(String[] args)`, returning an integer exit code and declaring `Exception`. The Javadoc positions `Tool` as the standard MapReduce application interface: generic Hadoop options should be delegated to `ToolRunner`, while custom application arguments remain the responsibility of the application.

`ToolRunner` is a public utility class for executing `Tool` implementations. It has a public constructor, two static `run` overloads, and `printGenericCommandUsage(PrintStream out)`. `run(Configuration conf, Tool tool, String[] args)` parses generic Hadoop arguments, uses the supplied `Configuration` or creates one when null, installs the possibly modified configuration on the tool, then calls `Tool.run(String[])`. `run(Tool tool, String[] args)` delegates to the first overload using `tool.getConf()`. `printGenericCommandUsage` writes generic Hadoop command-line usage to a supplied `PrintStream`.

`UTF8ByteArrayUtils` is a public byte-array search utility class. It has a public constructor and static helpers for searching UTF-8 encoded byte arrays: `findByte(byte[] utf, int start, int end, byte b)`, `findBytes(byte[] utf, int start, int end, byte[] b)`, and two `findNthByte` overloads. These methods return the matching byte offset or `-1` if absent. The APIs operate on raw bytes even though the documentation describes the array as UTF-8 encoded text, so they are suitable for delimiter scanning without allocating Java `String` objects.

`VersionInfo` exposes Hadoop build metadata. Static methods include `getVersion()`, `getRevision()`, `getDate()`, `getUser()`, `getUrl()`, `getBuildVersion()`, and `main(String[] args)`. The Javadoc says this class finds package info and `HadoopVersionAnnotation` information; the returned build version combines version, revision, user, and date.

`XMLUtils` is a public general XML utility class. Its static `transform(InputStream styleSheet, InputStream xml, Writer out)` applies an XSLT stylesheet to input XML and writes the result to the supplied writer. It declares `TransformerConfigurationException` and `TransformerException`, exposing failures from the Java XML transform stack.

## Control Flow and Behavioral Contracts

The `StringUtils` escaping flow is a round-trip contract across persisted or CLI-provided delimited values. Callers escape separator characters before joining or storing values, split on unescaped separators with `split`/`findNext`, and unescape values after parsing. Correct behavior depends on all default helpers agreeing on `COMMA` and `ESCAPE_CHAR`, and on overloads treating caller-provided escape and separator characters consistently.

The time-formatting flow separates raw duration formatting from timestamp display. `formatTimeDiff` computes `finishTime - startTime` and delegates the user-facing duration shape to the same style as `formatTime`. `getFormattedTimeWithDiff` adds conditional presentation behavior around missing timestamps: no finish time produces no text, while no start time suppresses the elapsed suffix.

The binary-prefix parsing flow in `TraditionalBinaryPrefix.string2long` trims the input, detects an optional final prefix symbol, maps that symbol through `valueOf(char)`, and multiplies the numeric portion by the prefix value. The documentation examples make sign handling part of the contract: negative numeric strings retain the sign before multiplication.

The `Tool`/`ToolRunner` flow is the central command-line integration path. A Hadoop application implements `Tool`, usually via a `Configured` base class. `ToolRunner.run` parses generic Hadoop options first, mutates the tool's configuration via the `Configurable` contract, and forwards only application-specific arguments to `Tool.run`. The returned integer is the process-level exit code expected by caller `main` methods.

The UTF-8 byte search flow scans caller-owned byte arrays by offset. `findByte` searches a bounded `[start, end)`-style interval for one byte; `findBytes` searches for a byte sequence in the same bounded interval; `findNthByte` searches for the nth occurrence either within an explicit `start`/`length` range or across the whole array. The API returns `-1` for misses rather than throwing for normal absence.

`VersionInfo` lookup is a read-only build metadata flow. Static getters retrieve version, source-control revision, build date, build user, repository URL, and a combined display string. `main` is available for command-line inspection of the same metadata.

`XMLUtils.transform` is a one-shot transform flow: consume stylesheet and XML input streams, configure a transformer, apply the transform, and stream the output to the caller-provided `Writer`. Transform configuration failures and runtime transform failures remain visible through the declared checked exceptions.

## State, Persistence, and Side Effects

The JDiff XML itself is persistent API compatibility data. It does not store implementation bodies or runtime values, but it captures source/binary compatibility decisions for Hadoop 0.19.2 public APIs.

Most APIs in this chunk are stateless static helpers. Persistent data dependencies arise indirectly: `StringUtils` URI/path/comma escaping helpers are commonly used to serialize and deserialize configuration values, command-line lists, and log/web display strings. Changes to escaping, splitting, hex conversion, or URI/path conversion can affect data already stored in configuration files or job metadata.

`ToolRunner.run` has an explicit state side effect: it sets the tool's `Configuration` after generic option parsing. That mutation is intentional and central to the `Tool` contract; tools that read `getConf()` inside `run` depend on receiving the processed configuration, not the original raw object.

`startupShutdownMessage` writes through an Apache Commons Logging `Log` and installs shutdown logging behavior according to its documentation. `escapeHTML` is a pure string transform but is used to protect generated HTML output boundaries.

`TraditionalBinaryPrefix` enum instances carry immutable public fields `value` and `symbol`. Although the fields are public, they are final and represent fixed enum constants. `string2long` returns primitive values and does not persist state.

`UTF8ByteArrayUtils` methods inspect caller-owned byte arrays and return offsets without documented mutation. `VersionInfo` getters read package or annotation metadata embedded at build time. `XMLUtils.transform` consumes input streams and writes transformed content to the supplied `Writer`; it may leave partial output if a `TransformerException` occurs after writing begins.

## Dependencies and Integration Points

This chunk integrates `StringUtils` with Java core types (`String`, `String[]`, `StringBuilder`, `DateFormat`, `URI`) and Hadoop filesystem paths (`org.apache.hadoop.fs.Path`). The startup/shutdown logging method depends on `org.apache.commons.logging.Log`.

`Tool` depends on `org.apache.hadoop.conf.Configurable`; `ToolRunner` depends on `org.apache.hadoop.conf.Configuration`, `Tool`, `PrintStream`, and the related `GenericOptionsParser` API documented in Javadoc links. The example Javadoc also references the older MapReduce API surface (`JobConf`, `JobClient`, mapper/reducer configuration, `Path`) as the expected application context.

`UTF8ByteArrayUtils` has only byte-array and primitive dependencies, which makes it suitable for low-allocation parsing paths such as text input processing. Its behavior is still tied to callers that understand byte offsets in UTF-8 encoded data.

`VersionInfo` depends on build-time package metadata and `HadoopVersionAnnotation`, as described by the class Javadoc. Its output is consumed by command-line tools, diagnostics, logs, and version checks.

`XMLUtils` depends on Java IO streams/writers and `javax.xml.transform` exceptions. It is an integration point between Hadoop utilities and standard JAXP/XSLT processing.

The XML package boundary closes `org.apache.hadoop.util` and then the whole API document. Downstream merge/reconciliation tools should treat this chunk as the final chunk for `hadoop_0.19.2.xml`.

## Risks and Compatibility Notes

The chunk begins at line 43531 inside the `hexStringToByte` method entry. Its method name, return type, and static/visibility flags are visible in immediately preceding lines, while this chunk contains the parameter and Javadoc. Reconciliation should merge this with the previous chunk when producing a final per-file report.

`StringUtils` helpers are compatibility-sensitive because they affect persisted textual encodings. Escaping rules, separator defaults, hex parsing, URI/path conversion, hostname formatting, and elapsed-time display are all user-visible or configuration-visible. Even a small change to edge cases such as odd-length hex strings, empty comma-separated entries, trailing escape characters, or null arrays could break older jobs or configuration round trips.

`findNext` exposes a low-level parsing helper with output via a mutable `StringBuilder`. Callers depend on the returned index and the side-channel segment content staying synchronized. Off-by-one behavior around escaped separators, adjacent separators, or end-of-string conditions is a likely regression surface.

`TraditionalBinaryPrefix.string2long` can overflow `long` when large numeric values are multiplied by high prefixes. The API returns primitive `long` and the XML does not document overflow behavior. Case-insensitive prefix lookup is documented, so rejecting upper-case symbols would be incompatible.

`ToolRunner` mutates the passed `Tool`'s configuration and declares broad `Exception`. Wrappers must preserve generic option parsing order, argument forwarding semantics, configuration installation, and exit-code propagation. Changing when the configuration is set can break tools that inspect it during `run`.

`UTF8ByteArrayUtils` works at byte offsets, not character indexes. Callers scanning multibyte UTF-8 content must only search for byte delimiters where byte-level matching is valid. Boundary handling for `start`, `end`, `length`, and `n` is a key risk because the Javadoc does not specify validation or exception behavior for invalid ranges.

`VersionInfo` is a diagnostic compatibility point. Missing package annotations or changed formatting of `getBuildVersion()` can affect logs, support tooling, and tests that assert version output.

`XMLUtils.transform` delegates to the platform XML transformer implementation. External entity handling, stylesheet behavior, stream lifecycle, character encoding, and partial writes are not described in the XML. Callers should treat transformer exceptions as expected failure modes and should own closing the streams/writer unless implementation documentation says otherwise.

## Test Signals

JDiff-level validation should confirm the XML remains well formed through the final `</api>`, preserves the closing `org.apache.hadoop.util` package boundary, and keeps all method signatures, parameters, declared exceptions, field constants, visibility, static/final flags, abstract/interface metadata, deprecation states, and Javadoc blocks stable.

`StringUtils` tests should cover hex round trips, invalid or odd-length hex input, URI array to string conversion, string arrays to URI and `Path` arrays, duration formatting for positive, zero, and negative differences, `getFormattedTimeWithDiff` with zero finish/start timestamps, comma-separated parsing, empty and whitespace inputs, escaping/unescaping default commas, custom escape/separator characters, arrays of escaped characters, `findNext` boundary cases, hostname fallback behavior, startup/shutdown log emission, and HTML escaping for special characters.

`TraditionalBinaryPrefix` tests should cover `values()`, Java enum `valueOf(String)`, Hadoop `valueOf(char)` with upper- and lower-case symbols, unknown symbols, `string2long` with no suffix, positive and negative suffixes, surrounding whitespace, high prefixes, zero, and overflow-adjacent values.

`Tool` and `ToolRunner` tests should use a small `Tool` implementation to assert generic option parsing, configuration installation, use of a null or existing `Configuration`, the overload that calls `tool.getConf()`, preservation of application-specific arguments, return-code propagation, exception propagation, and generic usage text printed to a `PrintStream`.

`UTF8ByteArrayUtils` tests should scan ASCII and multibyte UTF-8 byte arrays for single bytes, byte sequences, nth occurrences, missing bytes, start/end subranges, explicit start/length ranges, whole-array overload behavior, and invalid or edge inputs such as empty arrays, `n <= 0`, and ranges at array boundaries.

`VersionInfo` tests should assert non-null version, revision, date, user, URL, combined build-version formatting, and `main` output consistency with the getter values when build metadata is available.

`XMLUtils` tests should transform a simple XML document with a simple stylesheet, assert writer output, and cover malformed stylesheets, malformed XML, transformer runtime errors, and behavior when output has been partially written before a `TransformerException`.
