# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.19.1.xml lines 43513-44195

## Chunk Scope

This chunk is the tail of the Hadoop 0.19.1 JDiff API XML for `org.apache.hadoop.util`. It starts in the middle of `StringUtils`, covers the nested `StringUtils.TraditionalBinaryPrefix` enum, then documents `Tool`, `ToolRunner`, `UTF8ByteArrayUtils`, `VersionInfo`, and `XMLUtils` before closing the package and API document.

Because this source is generated API XML rather than implementation source, control flow, state, and persistence behavior are inferred from public signatures, modifiers, checked exceptions, and embedded Javadoc.

## Purpose

The chunk captures utility APIs used across Hadoop common and MapReduce applications:

- string and byte formatting/parsing helpers in `StringUtils`;
- command-line application integration through `Tool` and `ToolRunner`;
- byte-level search helpers for UTF-8 encoded records;
- build/version metadata access through `VersionInfo`;
- a simple XSLT transform helper in `XMLUtils`.

As a compatibility artifact, this section is useful for tracking public method overloads, nested enum shape, field visibility, static utility contracts, checked exceptions, and documentation wording in the Hadoop 0.19.1 public API.

## Important APIs and Types

### `org.apache.hadoop.util.StringUtils` tail

The visible part of `StringUtils` is a static utility surface for presentation, conversion, escaping, and logging support. The chunk begins after earlier formatting helpers and includes:

- `byteToHexString(byte[], int, int)` and `byteToHexString(byte[])`, converting byte ranges or entire arrays to hexadecimal text.
- `hexStringToByte(String)`, converting a hex string back to a byte array of size `hex.length()/2`.
- `uriToString(URI[])`, `stringToURI(String[])`, and `stringToPath(String[])`, bridging command-line/configuration string arrays with `java.net.URI` and Hadoop `Path` values.
- `formatTimeDiff(long finishTime, long startTime)`, `formatTime(long timeDiff)`, and `getFormattedTimeWithDiff(DateFormat, long finishTime, long startTime)`, formatting elapsed time and optionally appending a finish-start delta.
- `getStrings(String)` and `getStringCollection(String)`, splitting comma-separated values into arrays or `Collection<String>`.
- `split(String)` and `split(String, char escapeChar, char separator)`, splitting strings while respecting escaped separators.
- `findNext(String, char separator, char escapeChar, int start, StringBuilder split)`, the lower-level scanner used to find an unescaped separator and return the extracted segment through a mutable `StringBuilder`.
- `escapeString` overloads for default comma escaping, escaping a single character, or escaping an array of characters.
- `unEscapeString` overloads matching the escaping APIs.
- `getHostname()`, returning a hostname without propagating exceptions.
- `startupShutdownMessage(Class<?>, String[], Log)`, logging startup and shutdown messages for server classes.
- `escapeHTML(String)`, escaping HTML-special characters for display.

Public constants in this slice are `COMMA`, `COMMA_STR`, and `ESCAPE_CHAR`. These constants define the default delimiter and escape syntax for the string splitting/escaping helpers.

### `StringUtils.TraditionalBinaryPrefix`

`TraditionalBinaryPrefix` is a public static final enum nested under `StringUtils`. It represents binary prefixes such as kilo, mega, through exa, with case-insensitive symbols and 64-bit integer values.

Visible APIs include:

- compiler-generated enum methods `values()` and `valueOf(String)`;
- `valueOf(char symbol)`, resolving a prefix by symbol;
- `string2long(String)`, trimming and parsing numeric strings with optional traditional binary suffixes.

The enum exposes public final instance fields `value` (`long`) and `symbol` (`char`). Documentation examples show `-1230k` becoming `-1230 * 1024` and `891g` becoming `891 * 1024^3`.

### `org.apache.hadoop.util.Tool`

`Tool` is a public interface extending `org.apache.hadoop.conf.Configurable`. Its single command API is:

- `run(String[] args) throws Exception`, returning a process-style exit code.

The interface documentation defines the standard Hadoop command-line application pattern: application-specific tools should delegate generic Hadoop option parsing to `ToolRunner`, then process their own remaining arguments using the `Configuration` installed on the tool.

The embedded example shows a `Configured implements Tool` application building a `JobConf`, setting input/output paths and mapper/reducer classes, then invoking `JobClient.runJob(job)`. The XML does not expose `JobConf` methods here, but the docs make this interface a MapReduce application integration point.

### `org.apache.hadoop.util.ToolRunner`

`ToolRunner` is a public utility class with a public constructor and static helpers:

- `run(Configuration conf, Tool tool, String[] args) throws Exception`, parsing generic options with the supplied or newly created `Configuration`, setting the possibly modified configuration on the `Tool`, and delegating to `Tool.run`.
- `run(Tool tool, String[] args) throws Exception`, equivalent to `run(tool.getConf(), tool, args)`.
- `printGenericCommandUsage(PrintStream out)`, printing generic Hadoop command-line arguments and usage information.

The class documentation ties `ToolRunner` directly to `GenericOptionsParser`, which handles generic Hadoop options while preserving application-specific arguments for the tool.

### `org.apache.hadoop.util.UTF8ByteArrayUtils`

`UTF8ByteArrayUtils` is a public byte-search utility class with a public constructor and static methods operating on byte arrays that contain UTF-8 encoded strings:

- `findByte(byte[] utf, int start, int end, byte b)`, returning the first occurrence of a byte in a bounded range, or `-1`.
- `findBytes(byte[] utf, int start, int end, byte[] b)`, returning the first occurrence of a byte sequence, or `-1`.
- `findNthByte(byte[] utf, int start, int length, byte b, int n)`, returning the position of the nth occurrence in a bounded region, or `-1`.
- `findNthByte(byte[] utf, byte b, int n)`, a whole-array convenience overload.

These APIs are byte-oriented, so callers are expected to search for delimiter bytes or byte sequences that are meaningful in the encoded representation.

### `org.apache.hadoop.util.VersionInfo`

`VersionInfo` is a public utility class for build metadata. It exposes:

- `getVersion()`, returning the Hadoop version string.
- `getRevision()`, returning the Subversion revision for the root directory.
- `getDate()`, returning the build date.
- `getUser()`, returning the build user.
- `getUrl()`, returning the Subversion URL for the root Hadoop directory.
- `getBuildVersion()`, combining version, revision, user, and date.
- `main(String[] args)`, presumably printing version/build details for command-line use.

The class documentation states that it finds package info and `HadoopVersionAnnotation` information.

### `org.apache.hadoop.util.XMLUtils`

`XMLUtils` is a public class with a simple XSLT wrapper:

- `transform(InputStream styleSheet, InputStream xml, Writer out) throws TransformerConfigurationException, TransformerException`.

The method takes a stylesheet stream, an XML input stream, and a writer for transformed output. It integrates with the standard `javax.xml.transform` exception model.

## Control Flow and Behavioral Contracts

Most behavior is utility-level and stateless:

- `StringUtils` conversion methods flow from input arrays/strings into formatted strings, parsed bytes, `URI[]`, or `Path[]`.
- Escaping flow uses `escapeString` before storage or serialization of comma-separated data, then `split` and `unEscapeString` to recover logical tokens. `findNext` is the lower-level scanning primitive that ignores escaped separators and passes the token back through a `StringBuilder`.
- Time formatting flow computes a finish-start delta through `formatTimeDiff`, formats raw deltas through `formatTime`, and combines date formatting with optional elapsed time through `getFormattedTimeWithDiff`. Documentation says `getFormattedTimeWithDiff` returns an empty string when finish time is zero and omits the delta when start time is zero.
- `TraditionalBinaryPrefix.string2long` trims input, checks for a suffix symbol, resolves that suffix through `valueOf(char)`, parses the numeric portion, and multiplies by the prefix value.
- Hadoop CLI execution flows through `ToolRunner.run`: construct or reuse a `Configuration`, parse generic options with `GenericOptionsParser`, set the resulting configuration on the `Tool`, then invoke `Tool.run` with remaining command-specific arguments.
- `UTF8ByteArrayUtils` methods scan byte arrays linearly for a target byte, byte sequence, or nth occurrence.
- `VersionInfo` reads build/package annotation metadata through static accessors and exposes the same information through `main`.
- `XMLUtils.transform` builds or uses a transformer from the stylesheet and applies it to the XML input, writing transformed text to the supplied `Writer`.

## State and Persistence Behavior

This chunk exposes little mutable object state:

- `StringUtils` is effectively stateless except for public static delimiter constants and temporary parsing/formatting results.
- `TraditionalBinaryPrefix` enum instances carry immutable public final `value` and `symbol` fields.
- `Tool` instances are stateful through the inherited `Configurable` contract: `ToolRunner` mutates the tool by installing the parsed `Configuration` before invoking `run`.
- `UTF8ByteArrayUtils` methods do not persist state; they return offsets into caller-owned byte arrays.
- `VersionInfo` exposes build metadata embedded in the Hadoop artifact/package annotations. That metadata is persisted at build/package time rather than by this runtime API.
- `XMLUtils.transform` does not define persistence itself, but it streams transformed XML into caller-provided output.

Caller-owned mutable objects matter in this API surface: `StringBuilder` in `findNext`, byte arrays in UTF-8 search methods, `Configuration` inside `ToolRunner`, and `Writer` output in `XMLUtils`.

## Dependencies and Integration Points

Visible dependencies include:

- Java core types: `String`, arrays, `StringBuilder`, `Collection`, `DateFormat`, `PrintStream`, `InputStream`, `Writer`, `URI`, and checked exceptions.
- Hadoop core types: `org.apache.hadoop.fs.Path`, `org.apache.hadoop.conf.Configuration`, `org.apache.hadoop.conf.Configurable`, `GenericOptionsParser`, and `ToolRunner`.
- Logging: `org.apache.commons.logging.Log` for `startupShutdownMessage`.
- XML transformation: `javax.xml.transform.TransformerConfigurationException` and `TransformerException`.
- Build metadata: `HadoopVersionAnnotation` and Java package information are referenced by `VersionInfo` documentation.

Integration is centered on cross-cutting utilities:

- `StringUtils` supports configuration parsing, command-line display, web UI escaping, logging output, and byte/string conversions used by many Hadoop components.
- `Tool` and `ToolRunner` provide the public CLI contract used by MapReduce jobs and administrative commands.
- `UTF8ByteArrayUtils` is suitable for text input parsing and delimiter detection without materializing Java `String` objects.
- `VersionInfo` is used by command-line tools, logs, diagnostics, and compatibility reporting.
- `XMLUtils` supports documentation, reports, or configuration-style XML transformations.

## Risks and Edge Cases

- This XML does not contain method bodies, so exact validation behavior, exception paths, null handling, synchronization, and performance characteristics must be confirmed from implementation source if needed.
- The chunk starts mid-`StringUtils`; final synthesis needs the preceding chunk to include earlier methods such as human-readable integer and percent formatting.
- `hexStringToByte(String)` implies output size `hex.length()/2`; odd-length strings or invalid hex characters are edge cases not specified here.
- Comma splitting and escaping are easy to misuse if callers mix escaped and unescaped values or pass a different separator/escape character across encode and decode paths.
- `findNext` mutates a caller-provided `StringBuilder`, so stale content or reuse without clearing could be an implementation concern depending on method behavior.
- `getFormattedTimeWithDiff` has special sentinel handling for zero finish/start times; tests should distinguish zero from valid epoch timestamps if those can appear.
- `TraditionalBinaryPrefix.string2long` can overflow `long` when large numeric values are combined with large suffixes; behavior is not specified in the XML.
- `TraditionalBinaryPrefix` symbols are documented as case-insensitive, so callers should not rely on preserving suffix case.
- `ToolRunner.run(Tool, String[])` depends on `tool.getConf()`; tools with null configurations rely on the three-argument overload's null-handling contract.
- `Tool.run` throws generic `Exception`, so command launchers must preserve exit-code semantics while handling broad failures.
- `UTF8ByteArrayUtils` searches bytes, not Unicode code points; it is appropriate for ASCII delimiters in UTF-8 but not for arbitrary character-level searching.
- `VersionInfo` references Subversion metadata, which reflects Hadoop's historical build system and may be absent or differently represented in later builds.
- `XMLUtils.transform` leaves stream and writer ownership unclear in the signature docs; callers should manage close/flush behavior explicitly.

## Test Signals

Useful tests inferred from this API slice include:

- `StringUtils.byteToHexString` and `hexStringToByte` round trips for empty arrays, full arrays, subranges, uppercase/lowercase input, odd-length input, and invalid characters.
- `uriToString`, `stringToURI`, and `stringToPath` tests for empty arrays, null-like entries if supported by implementation, relative paths, schemes, authorities, and malformed URI strings.
- `formatTime`, `formatTimeDiff`, and `getFormattedTimeWithDiff` tests for positive, zero, and negative deltas; zero finish time; zero start time; and DateFormat output.
- `getStrings`, `getStringCollection`, `split`, `escapeString`, `unEscapeString`, and `findNext` tests for commas, escaped commas, escape characters themselves, multiple separators, leading/trailing empty tokens, and custom separator/escape characters.
- `escapeHTML` tests for HTML special characters such as `<`, `>`, `&`, quotes, and already-escaped input.
- `getHostname` tests or diagnostics confirming it returns a stable non-throwing value under normal and hostname-resolution failure conditions.
- `startupShutdownMessage` tests with a test `Log` implementation to confirm startup arguments, hostname/build info if included by implementation, and shutdown-hook behavior.
- `TraditionalBinaryPrefix.valueOf(char)` and `string2long` tests for all supported suffixes, case insensitivity, no suffix, whitespace trimming, negative values, invalid suffixes, and overflow boundaries.
- `ToolRunner.run` tests with a dummy `Tool` verifying generic option parsing, configuration injection, remaining application arguments, null configuration handling, returned exit code propagation, and exception propagation.
- `printGenericCommandUsage` tests that usage text is emitted to the supplied `PrintStream`.
- `UTF8ByteArrayUtils` tests for first/nth byte searches, byte sequence searches, start/end boundaries, missing values, overlapping byte sequences, zero-length target arrays if implementation accepts them, and multibyte UTF-8 content with ASCII delimiters.
- `VersionInfo` tests or smoke checks that version, revision, date, user, URL, build version, and `main` produce non-null diagnostic output in packaged builds.
- `XMLUtils.transform` tests using a small stylesheet/XML pair, invalid stylesheet handling, invalid XML handling, and writer flush/content assertions.

## Chunk Boundary Notes

The previous chunk is needed to complete the `StringUtils` class summary because this range begins at `byteToHexString(byte[])` after earlier formatting methods. This chunk closes `org.apache.hadoop.util` and the whole `hadoop_0.19.1.xml` API document, so no following chunk is needed for these specific classes.
