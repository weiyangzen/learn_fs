# Research: subset-b-008401

Grouped research for FoundationDB RapidXML headers and the `contrib/replay` trace replay tool. Each section preserves the source path and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidxml/include/rapidxml/rapidxml.hpp -->
# sources/storage-engines/foundationdb/contrib/rapidxml/include/rapidxml/rapidxml.hpp

## Purpose

`rapidxml.hpp` is the header-only core of RapidXML 1.13 as vendored into FoundationDB, with local extensions for XML namespace tracking/validation and stream-oriented partial parsing. It defines the parser flags, error model, DOM types, memory pool allocator, in-place XML parser, namespace lookup helpers, and static lookup tables used by sibling headers.

The parser is optimized for mutable, zero-terminated XML buffers. By default it writes terminators into the input, expands entity references in place, and stores node and attribute names/values as pointers into the original buffer. This is a high-performance design, but it makes input lifetime, mutability, and parse flags part of the API contract.

## Important APIs, Types, and Functions

- Error configuration:
  - `RAPIDXML_PARSE_ERROR(what, where)` and `RAPIDXML_EOF_ERROR(what, where)` either throw exceptions or call `parse_error_handler()` when `RAPIDXML_NO_EXCEPTIONS` is defined.
  - `parse_error` carries a typed `where<Ch>()` pointer into the source buffer.
  - `validation_error` reports namespace validation failures.
  - `eof_error` is declared as a `parse_error` subtype, but its constructor is private in this file, so direct construction is not externally useful.
- Parser flags:
  - Stock flags include `parse_no_data_nodes`, `parse_no_element_values`, `parse_no_string_terminators`, `parse_no_entity_translation`, `parse_no_utf8`, `parse_declaration_node`, `parse_comment_nodes`, `parse_doctype_node`, `parse_pi_nodes`, `parse_validate_closing_tags`, `parse_trim_whitespace`, and `parse_normalize_whitespace`.
  - Compound flags are `parse_default`, `parse_non_destructive`, `parse_fastest`, and `parse_full`.
  - Local extensions include `parse_open_only`, `parse_parse_one`, and `parse_validate_xmlns` declarations. The first two affect parser control flow; `parse_validate_xmlns` is declared but is not automatically invoked by `parse()` in this file.
- `memory_pool<Ch>`:
  - Allocates `xml_node`, `xml_attribute`, and strings using a static pool first, then dynamically allocated blocks.
  - Exposes `allocate_node()`, `allocate_attribute()`, `allocate_string()`, `clone_node()`, `clear()`, and `set_allocator()`.
  - Adds cached strings for `nullstr()`, `xmlns_xml()`, and `xmlns_xmlns()` for namespace lookup helpers.
- `xml_base<Ch>`:
  - Common name/value/size/parent storage for nodes and attributes.
  - Setters store non-owning pointers; callers are responsible for lifetime unless strings come from the pool.
- `xml_attribute<Ch>`:
  - Represents a linked-list attribute with `previous_attribute()`, `next_attribute()`, `document()`, `xmlns()`, `xmlns_size()`, `local_name()`, and `local_name_size()`.
  - Namespace methods lazily compute/cache the namespace URI and local-name pointer.
- `xml_node<Ch>`:
  - Stores node type, prefix, cached namespace URI, child list, and attribute list.
  - Provides child and attribute lookup (`first_node`, `last_node`, `previous_sibling`, `next_sibling`, `first_attribute`, `last_attribute`) plus mutation (`prepend_node`, `append_node`, `insert_node`, removals, and attribute equivalents).
  - Adds namespace-aware `first_node()` and `last_node()` overload shape: when a name is supplied without an explicit namespace, it assumes the same namespace as the current node.
  - `xmlns_lookup()` walks ancestor attributes looking for `xmlns` or `xmlns:prefix`, with hard-coded handling for `xml` and `xmlns`.
  - `validate()` recursively checks that element and attribute namespace bindings exist and that duplicate attributes are not present either by raw name or by local-name-plus-namespace.
- `xml_document<Ch>`:
  - Inherits from both `xml_node<Ch>` and `memory_pool<Ch>`.
  - `parse<Flags>(Ch *text, xml_document<Ch> *parent = 0)` clears current tree links, parses BOM and top-level nodes, and returns the input pointer at the parse stop point.
  - `parse<Flags>(Ch *text, xml_document<Ch>& parent)` forwards to the pointer overload.
  - `clear()` removes nodes/attributes and clears the pool.
  - `fixup<Flags>(xml_node<Ch>* element, bool recurse)` terminates and decodes a previously parsed subtree, particularly useful with partial/open parsing.
  - `validate()` runs namespace validation over top-level children.

## Control Flow

Parsing starts in `xml_document::parse<Flags>()`. It clears the current node and attribute links, optionally attaches the document under a parent document's first node, skips a UTF-8 BOM, then repeatedly skips whitespace and expects `<`. Each markup item is dispatched through `parse_node<Flags>()`.

`parse_node()` dispatches by the first character after `<`:

- default: `parse_element()`
- `?`: XML declaration or PI
- `!`: comment, CDATA, DOCTYPE, or unknown declaration-like markup skipped to `>`

`parse_element()` creates a `node_element`, splits an optional `prefix:local` element name, parses attributes, then either parses nested contents for open tags, handles self-closing tags, or reports syntax errors. Name/prefix terminators are written unless `parse_no_string_terminators` is set.

`parse_node_contents()` loops over child markup and text until a closing tag, EOF, or parse flag stops it. Data is routed through `parse_and_append_data()`, which performs entity expansion, optional whitespace normalization/trimming, optional `node_data` creation, optional parent element value assignment, and optional terminator insertion. The function returns the character that stopped text scanning because terminator insertion may have overwritten it.

Attribute parsing in `parse_node_attributes()` reads attribute names, appends each attribute immediately, enforces `=`, handles quote choice, expands entity references in value text, stores value spans, and writes terminators unless disabled. Attribute whitespace normalization is explicitly masked out even when element text normalization is enabled.

Namespace validation is not part of the parse loop. Callers must invoke `validate()` explicitly after parsing if they want namespace binding and duplicate-attribute checks.

## State and Persistence Behavior

The DOM is memory-backed by `memory_pool`. Nodes, attributes, cached namespace strings, and allocated strings are invalidated by `memory_pool::clear()` or document destruction. Parsed names/values generally point into the original input buffer, so the input buffer must outlive the DOM unless callers clone/copy strings into the pool.

The parser mutates source text by default. Mutations include null terminators after names/values and in-place replacement of entity references/numeric character references. `parse_non_destructive` prevents terminators and entity translation but also requires users to respect `*_size()` because strings are not guaranteed to be null-terminated.

Several object fields are intentionally undefined unless related pointers are non-null, for performance. For example, `m_last_node` is meaningful only when `m_first_node` is set, and sibling pointers are meaningful only when a parent is set. Misusing raw internals or calling traversal functions outside their preconditions can assert or produce undefined behavior.

Namespace URI and local-name fields are cached lazily inside mutable members. If attributes or prefixes are modified after first lookup, cached namespace values may become stale because mutation methods do not invalidate `m_xmlns` or `m_local_name`.

## Dependencies and Integration Points

The header depends on the C++ standard library unless `RAPIDXML_NO_STDLIB` is defined. Default builds use `<cstdlib>`, `<cassert>`, `<new>`, and `<stdexcept>`. It is consumed directly by `rapidxml_iterators.hpp`, `rapidxml_print.hpp`, and `rapidxml_utils.hpp`.

Build-time customization is through macros such as `RAPIDXML_NO_EXCEPTIONS`, `RAPIDXML_NO_STDLIB`, `RAPIDXML_STATIC_POOL_SIZE`, `RAPIDXML_DYNAMIC_POOL_SIZE`, and `RAPIDXML_ALIGNMENT`. Users disabling exceptions must provide `rapidxml::parse_error_handler()`.

The likely repository integration is XML parsing for FoundationDB utilities or tests where a lightweight header-only parser is preferred. The namespace extensions suggest local callers need XPath-like namespace-aware lookup or validation.

## Risks and Edge Cases

- Input mutation is easy to overlook. Passing string literals, read-only memory, mmap pages without write permission, or buffers that do not outlive the document will break the parser contract.
- `xml_node::remove_all_nodes()` and `remove_all_attributes()` clear parent pointers but leave some last/sibling fields stale; this is consistent with internal preconditions but unsafe for external stale pointers.
- `clone_node()` shares name and value pointers rather than copying string data, so clones can dangle when the source buffer is released.
- Namespace lookup allocates temporary attribute names with `new[]` on every uncached lookup and does not use the memory pool for that temporary.
- Namespace caches can become stale after DOM mutation.
- `parse_validate_xmlns` is declared but not wired into `parse()`, so setting the flag alone does not appear to validate namespaces.
- `parse_open_only`/`parse_parse_one` partially parse streams and return the stop pointer, but callers must carefully use `fixup()` or subsequent parsing to finish names/values and tree state.
- `parse_and_append_data()` trims by looking at `end - 1`; all-whitespace or empty data with trimming enabled should be tested because this code assumes there is a preceding character to inspect.
- Closing tag validation compares only `node->name()` and not the parsed prefix. For prefixed elements this may validate local name only, depending on how closing names are parsed.

## Test Signals

Useful tests should include destructive vs non-destructive parsing, entity translation and numeric character references, UTF-8 vs `parse_no_utf8`, whitespace trimming/normalization, comments/PI/doctype inclusion flags, CDATA with and without data nodes, closing tag validation, partial parsing with `parse_open_only` and `parse_parse_one`, and explicit namespace validation.

Namespace tests should cover default namespaces, prefixed element/attribute lookup, built-in `xml` and `xmlns` prefixes, unbound prefixes, duplicate raw attributes, duplicate local-name-plus-namespace attributes, and cache behavior after mutation.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidxml/include/rapidxml/rapidxml.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidxml/include/rapidxml/rapidxml_iterators.hpp -->
# sources/storage-engines/foundationdb/contrib/rapidxml/include/rapidxml/rapidxml_iterators.hpp

## Purpose

`rapidxml_iterators.hpp` adds lightweight STL-style bidirectional iterators over RapidXML child nodes and attributes. It is a small convenience layer on top of `rapidxml.hpp` linked-list traversal methods.

## Important APIs, Types, and Functions

- `node_iterator<Ch>`:
  - `node_iterator()` constructs an end/null iterator.
  - `node_iterator(xml_node<Ch>* node)` starts at `node->first_node()`.
  - `operator*()` and `operator->()` expose the current `xml_node`.
  - Prefix and postfix increment move to `next_sibling()`.
  - Prefix and postfix decrement move to `previous_sibling()`.
  - Equality compares the underlying node pointer.
- `attribute_iterator<Ch>`:
  - Mirrors `node_iterator`, but starts at `node->first_attribute()` and moves through `next_attribute()` / `previous_attribute()`.

The typedefs advertise `std::bidirectional_iterator_tag`, `std::ptrdiff_t`, pointer/reference, and value type members expected by older STL algorithms. The file relies on `rapidxml.hpp` for `<cassert>` and standard-library typedef availability in normal configurations.

## Control Flow

Both iterators store only one pointer. Construction from a parent node immediately moves to the first child or first attribute. Increment/decrement methods assert that the current pointer is non-null, then ask RapidXML's linked-list APIs for the adjacent item. Comparison is pointer identity.

## State and Persistence Behavior

Iterator validity is tied to the underlying DOM node/attribute lifetime and list stability. Any DOM mutation that removes the current item or clears the document invalidates the iterator. Appending other siblings may leave existing iterators usable as long as the pointed item remains linked, but there is no formal invalidation tracking.

End is represented by a null current pointer. There is no stored parent pointer, so decrementing an end iterator cannot move to the last item. This differs from many container bidirectional iterators and should be treated as a limited traversal helper rather than a full container iterator.

## Dependencies and Integration Points

The only direct include is `rapidxml.hpp`. Callers that want range-like loops over child nodes or attributes can construct a begin iterator from a node and compare against the default iterator as the end sentinel.

## Risks and Edge Cases

- Postfix `operator++(int)` and `operator--(int)` call `++this` instead of `++(*this)` / `--(*this)`. In standard C++, incrementing `this` is invalid because `this` is not an lvalue iterator object. This is a serious compile-time defect if postfix operators are instantiated.
- Postfix decrement also increments rather than decrements, so even after the `this` bug is fixed it must call the decrement operator.
- Decrement asserts that a previous item exists; it cannot be used from end or from the first item.
- Constructors do not accept `const xml_node<Ch>*`, so these iterators do not support const DOM traversal.
- Equality operators are non-const member functions, which can reduce compatibility with STL algorithms expecting comparisons on const iterator objects.

## Test Signals

Compile tests should instantiate prefix and postfix increment/decrement for both iterator types. Runtime traversal tests should cover empty nodes, one child/attribute, multiple siblings, default end comparison, and behavior after removing the current item. Tests should also verify expected compiler diagnostics or fixes around the postfix operator bug.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidxml/include/rapidxml/rapidxml_iterators.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidxml/include/rapidxml/rapidxml_print.hpp -->
# sources/storage-engines/foundationdb/contrib/rapidxml/include/rapidxml/rapidxml_print.hpp

## Purpose

`rapidxml_print.hpp` serializes RapidXML DOM nodes back to XML through output iterators or C++ streams. It implements escaping, indentation, node-type-specific formatting, and `operator<<` integration when streams are enabled.

## Important APIs, Types, and Functions

- `print_no_indenting` suppresses tab indentation and newline insertion.
- `internal::copy_chars()` copies raw character ranges.
- `internal::copy_and_expand_chars()` writes text while escaping `<`, `>`, `'`, `"`, and `&`, with a `noexpand` character that can be copied verbatim for quote selection.
- `internal::fill_chars()` emits repeated indentation characters.
- `internal::find_char<Ch, ch>()` scans a range for a character.
- `internal::print_node()` dispatches by `node_type`.
- Node-specific printers include:
  - `print_children()`
  - `print_attributes()`
  - `print_data_node()`
  - `print_cdata_node()`
  - `print_element_node()`
  - `print_declaration_node()`
  - `print_comment_node()`
  - `print_doctype_node()`
  - `print_pi_node()`
- Public APIs:
  - `template <class OutIt, class Ch> OutIt print(OutIt out, const xml_node<Ch>& node, int flags = 0)`
  - Stream overload `std::basic_ostream<Ch>& print(...)` unless `RAPIDXML_NO_STREAMS` is defined.
  - `operator<<` for stream output unless streams are disabled.

## Control Flow

Public `print()` starts at `internal::print_node(out, &node, flags, 0)`. `print_node()` switches on `node->type()` and delegates to the matching printer. After each node, it appends a newline unless `print_no_indenting` is set.

Element printing emits an opening tag, attributes, and either:

- a self-closing tag when the node has no value and no children,
- inline text when the node has no children but has a value,
- inline text when the only child is `node_data`,
- or a multiline child subtree followed by the closing tag.

Attributes are printed with a quote choice heuristic: if the value contains `"`, single quotes are used and double quotes are not expanded; otherwise double quotes are used and single quotes are not expanded. Other XML-sensitive characters are escaped.

CDATA, comments, doctype, declaration, and PI nodes are emitted using fixed XML delimiters and raw node name/value slices as appropriate. Document nodes print their children.

## State and Persistence Behavior

The printer does not mutate the DOM. It reads `name()`, `name_size()`, `value()`, `value_size()`, child lists, and attribute lists. It supports non-null-terminated names and values because all output uses pointer-plus-size ranges.

Output state is owned by the caller-provided iterator or stream. The code assumes writes through the output iterator cannot fail except through the iterator/stream implementation.

## Dependencies and Integration Points

The header includes `rapidxml.hpp`. When `RAPIDXML_NO_STREAMS` is not defined it also includes `<ostream>` and `<iterator>`. It is the companion serializer for DOMs produced by `rapidxml.hpp` and manually constructed DOMs from the memory pool.

## Risks and Edge Cases

- The printer does not validate XML before serialization. Invalid names, illegal comment content (`--`), illegal CDATA content (`]]>`), and invalid PI payloads can produce malformed XML.
- Namespace prefixes are not reconstructed from `xml_node::prefix()`. Element printing copies only `node->name()`, which in this local RapidXML stores the local name when a prefixed element was parsed. Without manual name reconstruction or preserved attributes, round-tripping prefixed XML may lose prefixes in output.
- `print_attributes()` uses the stored attribute name exactly; attribute prefix handling depends on how the parser stored the name.
- Pretty printing uses tabs and appends a newline after every node, including top-level documents, which may not be byte-for-byte stable for tests expecting exact input preservation.
- `node_data` values are escaped, while `node_cdata`, comments, doctype, and PI values are copied raw. Caller-provided raw values can break XML syntax.
- Very large DOMs are serialized recursively through node traversal and may stress call stack or output iterator performance.

## Test Signals

Tests should cover all `node_type` cases, escaped text and attributes, quote-choice behavior, pretty vs `print_no_indenting`, non-null-terminated ranges, empty elements, element value vs sole data child precedence, stream overload behavior, and namespace/prefix round-trip expectations for this local RapidXML variant.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidxml/include/rapidxml/rapidxml_print.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidxml/include/rapidxml/rapidxml_utils.hpp -->
# sources/storage-engines/foundationdb/contrib/rapidxml/include/rapidxml/rapidxml_utils.hpp

## Purpose

`rapidxml_utils.hpp` provides small high-level utilities for simple RapidXML use cases: loading a full file or stream into a zero-terminated buffer and counting child nodes or attributes.

## Important APIs, Types, and Functions

- `file<Ch>`:
  - `file(const char* filename)` opens a binary input file, measures it with seek/tell, reads it into `std::vector<Ch>`, and appends a zero terminator.
  - `file(std::basic_istream<Ch>& stream)` reads an existing stream through `istreambuf_iterator`, checks stream failure, and appends a zero terminator.
  - `data()` returns mutable or const pointer to the vector buffer.
  - `size()` returns `m_data.size()`, including the terminating zero.
- `count_children(xml_node<Ch>* node)` iterates `first_node()` / `next_sibling()`.
- `count_attributes(xml_node<Ch>* node)` iterates `first_attribute()` / `next_attribute()`.

## Control Flow

The filename constructor opens with `ios::binary`, disables `skipws`, seeks to end to determine size, seeks back, resizes the vector to `size + 1`, reads exactly `size` characters, and stores `0` at the end. The stream constructor disables `skipws`, assigns all characters from the stream buffer to the vector, checks `fail()`/`bad()`, and pushes a terminator.

Counting helpers are straightforward linear linked-list scans over the DOM.

## State and Persistence Behavior

`file<Ch>` owns its buffer in `m_data`; the pointer returned by `data()` remains valid until the `file` object is destroyed or its vector is otherwise reallocated internally. This fits RapidXML's requirement that the mutable parse buffer outlive the document.

The reported `size()` includes the trailing terminator, which callers must remember if they need original byte/character count.

## Dependencies and Integration Points

The file includes `rapidxml.hpp`, `<vector>`, `<string>`, `<fstream>`, and `<stdexcept>`. It is intended for simple callers that do not already have their XML payload loaded into mutable memory.

## Risks and Edge Cases

- `tellg()` is cast to `size_t` without checking for failure or negative position; unusual streams or very large files can misbehave.
- The filename constructor does not verify that `read()` consumed the expected number of characters after resizing.
- `size()` including the null terminator can lead to off-by-one mistakes.
- Loading the entire file into memory is unsuitable for very large XML traces or untrusted input sizes.
- Constructors throw `std::runtime_error` on open/read failures, independent of RapidXML's `RAPIDXML_NO_EXCEPTIONS` parse-error mode.
- `data()` returns `&m_data.front()`; because constructors always append/allocate at least one terminator, it is valid for constructed objects, but this pattern would be unsafe if future code allowed empty vectors.

## Test Signals

Tests should load a real file, an empty file, a stream with embedded whitespace, a stream failure case, and verify that the buffer is mutable and zero-terminated. Count helpers should be tested with zero, one, and multiple children/attributes and after DOM mutations.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidxml/include/rapidxml/rapidxml_utils.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/replay/CMakeLists.txt -->
# sources/storage-engines/foundationdb/contrib/replay/CMakeLists.txt

## Purpose

This CMake file integrates the Go-based `replay` TUI into the FoundationDB build. It detects Go, configures the output binary under the build tree's `bin` directory, and creates an `ALL` target that runs `go build` for the replay package.

## Important APIs, Targets, and Variables

- Requires CMake 3.13.
- `find_program(GO_EXECUTABLE go)` locates the Go toolchain.
- If Go is missing, it emits a warning and returns from the subdirectory, so the target is not available.
- `execute_process(COMMAND ${GO_EXECUTABLE} version ...)` records/logs the installed Go version but does not enforce the warned Go 1.21+ minimum.
- `REPLAY_OUTPUT_DIR` is `${CMAKE_BINARY_DIR}/bin`.
- `REPLAY_BINARY` is `${REPLAY_OUTPUT_DIR}/replay`.
- `file(GLOB REPLAY_GO_SOURCES "*.go")` tracks all Go files in the current source directory.
- `REPLAY_GO_MOD` and `REPLAY_GO_SUM` point at package module files.
- `add_custom_command(OUTPUT ${REPLAY_BINARY} COMMAND ${GO_EXECUTABLE} build -o ${REPLAY_BINARY} . WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR} DEPENDS ...)` builds the binary.
- `add_custom_target(replay ALL DEPENDS ${REPLAY_BINARY} SOURCES ${REPLAY_GO_SOURCES})` makes replay build by default when Go exists.

## Control Flow

CMake configuration first tries to find `go`. Missing Go is non-fatal for the broader build. When found, it logs the Go version, creates the binary output directory, gathers source dependencies, registers a custom command to build the Go module, and exposes an `ALL` target named `replay`.

At build time, the custom command runs `go build` from the replay source directory and emits the binary into the CMake build `bin` directory. Rebuilds are dependency-driven by the listed Go source files and module files.

## State and Persistence Behavior

The build artifact is persistent at `${CMAKE_BINARY_DIR}/bin/replay`. Go module downloads and build caches are managed by the Go toolchain outside this CMake file unless overridden by environment variables. The CMake source glob is evaluated at configure time, so adding new `.go` files may require reconfiguration depending on generator behavior.

## Dependencies and Integration Points

The file depends on a Go toolchain and the replay package's `go.mod` / `go.sum`. It plugs into the FoundationDB CMake tree as an optional contribution target. The `ALL` setting means replay becomes part of the default build only on systems where Go is present.

## Risks and Edge Cases

- The warning says Go 1.21+ is needed, but the script does not parse or enforce the version.
- `file(GLOB ...)` is not configured with `CONFIGURE_DEPENDS`, so newly added `.go` files may not trigger CMake reconfiguration.
- `go build` may download modules, which can make builds network-dependent unless dependencies are already cached or vendored.
- The binary name has no Windows executable suffix handling.
- Because the target is `ALL`, an available but misconfigured Go toolchain can fail default builds that might otherwise not need replay.

## Test Signals

Configuration tests should cover with-Go and without-Go environments. Build tests should verify `${CMAKE_BINARY_DIR}/bin/replay` appears, source changes trigger rebuilds, `go.mod`/`go.sum` changes trigger rebuilds, and invalid/old Go versions produce actionable failures if version enforcement is later added.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/replay/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/replay/cluster.go -->
# sources/storage-engines/foundationdb/contrib/replay/cluster.go

## Purpose

`cluster.go` reconstructs a simplified FoundationDB simulation cluster topology from parsed trace events. It tracks workers, roles, data-center IDs, machine type classification, and role epochs so the replay TUI can display cluster state at a selected point in the trace.

## Important APIs, Types, and Functions

- `RoleInfo` stores role `Name`, role `ID`, and an optional `Epoch`/generation string.
- `Worker` stores `Machine`, assigned `Roles`, `MachineType` (`main`, `tester`, or `unknown`), and `DCID`.
- `ClusterState` is a map from machine address to `*Worker`.
- `NewClusterState()` initializes an empty state.
- `parseAddress(address string)` classifies FDB simulation-style addresses:
  - IPv6-ish `[abcd::X:Y:...]` where `X=2` is main and `X=3` is tester, while `Y` is DC ID.
  - IPv4-ish `X.Y...` with the same type/DC interpretation.
- `BuildClusterState(events []TraceEvent)` replays trace events into current worker-role state.
- `GetWorkersByDC()` groups main workers by DC and sorts each group by machine address.
- `GetTesters()` returns tester workers sorted by machine address.
- `Worker.HasRoles()` tests whether any role is present.
- `Worker.HasNonWorkerRoles()` excludes the generic `Worker` role.
- `Worker.RolesString()` joins role names with `, `.

## Control Flow

`BuildClusterState()` performs one pass over the supplied events while maintaining an `epochByID` map. It first updates epoch hints from `TLogStart`, `LogRouterStart`, `BackupWorkerStart`, `TLogMetrics`, and `LogRouterMetrics`. Then it processes `Role` events with a non-placeholder machine address.

For each qualifying `Role` event, it extracts transition, role name, and role ID. Missing role names are skipped. A worker is created on first sight of a machine, with address classification from `parseAddress()`. `Transition == "Begin"` appends a role if the same name/ID is not already present, using any epoch currently known for that role ID. `Transition == "End"` removes matching roles. `Refresh` and other transitions do not change state.

After the pass, the function walks all remaining roles and fills any missing epoch from `epochByID`, covering metrics or start events that appeared after the role began.

Grouping and sorting functions iterate the map, filter by `MachineType`, and perform simple in-place O(n^2) address sorting for deterministic UI order.

## State and Persistence Behavior

`BuildClusterState()` returns a fresh state for the given event slice and does not persist across calls. It assumes the input event list represents the desired prefix of trace history. Callers in `ui.go` use it both for full traces and for time-window/prefix display updates.

Worker role slices are mutable and are updated in place while building. Role epoch values are strings copied from trace attributes, so no external storage lifetime issues exist beyond the `TraceEvent` slice itself.

## Dependencies and Integration Points

This file depends on `TraceEvent` from `trace.go`, plus `regexp` and `strings`. It is integrated into the TUI by calls such as `BuildClusterState(m.traceData.Events)` and `BuildClusterState(events)` in `ui.go`, and its grouping helpers support cluster layout/status rendering.

## Risks and Edge Cases

- Regular expressions are compiled on every `parseAddress()` call. For large traces with many machines, package-level precompiled regexes would reduce overhead.
- Sorting is O(n^2); acceptable for small simulation clusters but inefficient if machine counts grow.
- `BuildClusterState()` assumes the event slice is already in chronological order. Passing unsorted events can produce incorrect role lifetimes.
- Role identity is name plus ID. If traces reuse IDs across incompatible role lifetimes or omit IDs, de-duplication/removal may be wrong.
- Unknown transition values are silently ignored.
- Placeholder machine `"0.0.0.0:0"` is skipped, but other invalid placeholders become unknown workers.
- Epoch capture is best-effort and stringly typed; missing or malformed epoch attributes do not produce errors.

## Test Signals

Tests should cover IPv6 and IPv4 address parsing, unknown address formats, role begin/end/refresh sequences, duplicate begin suppression, end without begin, epoch updates from start and metrics events, epoch fill after role creation, grouping by DC, tester extraction, sorted output, and behavior with unsorted input.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/replay/cluster.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/replay/main.go -->
# sources/storage-engines/foundationdb/contrib/replay/main.go

## Purpose

`main.go` is the CLI entrypoint for the Go `replay` TUI. It selects a trace XML file, parses it into `TraceData`, reports load summary details, and launches the interactive UI.

## Important APIs and Functions

- `main()` calls `run()`, writes errors to stderr, and exits with code 1 on failure.
- `run()` handles arguments, trace discovery, parsing, summary logging, and `runUI(traceData)`.
- `printHelp()` writes usage, examples, and interaction hint text to stderr.
- `findLatestTraceFile()` finds the most recently modified `trace*.xml` file in the current working directory.

## Control Flow

`run()` accepts exactly three modes:

- One argument `-h` or `--help`: print help and return success.
- One non-help argument: treat it as the explicit trace file path.
- No arguments: call `findLatestTraceFile()` and use the newest matching file in the current directory.

Any other argument count returns a usage error. Once a trace path is chosen, `run()` calls `parseTraceFile()`. Parse errors are wrapped with context. On success it logs event count, min/max time, configuration count, and recovery state count, then calls `runUI(traceData)`.

`findLatestTraceFile()` uses `filepath.Glob("trace*.xml")`, stats each match, skips stat failures, and returns the path with the latest modification time.

## State and Persistence Behavior

The CLI keeps no persistent state. It reads from the current directory when auto-detecting traces and relies on `parseTraceFile()` to load trace contents into memory. Process exit code communicates failure to shell users.

## Dependencies and Integration Points

This file depends on standard packages `fmt`, `os`, `path/filepath`, and `time`. It integrates with `trace.go` via `parseTraceFile()` and with `ui.go` via `runUI()`. The CMake file builds this package into the `replay` binary.

## Risks and Edge Cases

- Auto-discovery only searches the current working directory and only the `trace*.xml` pattern.
- `printHelp()` writes to stderr even on successful help, which may surprise scripts expecting help on stdout.
- A single argument that begins with `-` but is not help is treated as a file path, not an unknown option.
- `findLatestTraceFile()` breaks ties by first encountered glob order because it only updates on strictly newer modification time.
- File existence for an explicit trace path is not checked until `parseTraceFile()`.

## Test Signals

Tests should cover help mode, explicit path mode, no-argument latest-file discovery, no matches, inaccessible matches, too many arguments, parse failure propagation, and successful handoff to a replaceable/testable UI entrypoint if refactoring makes `runUI` injectable.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/replay/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/replay/trace.go -->
# sources/storage-engines/foundationdb/contrib/replay/trace.go

## Purpose

`trace.go` parses FoundationDB XML trace files into indexed in-memory data for the replay TUI. It stores every trace event, extracts database configuration snapshots, recovery states, epoch/version relationships, and provides binary-search helpers for time and event-index navigation.

## Important APIs, Types, and Functions

- `TraceEvent` stores common XML event attributes (`Severity`, `Time`, `DateTime`, `Type`, `Machine`, `ID`), parsed `TimeValue`, and all other attributes in `Attrs`.
- `DBConfig` captures selected fields from the HTML-encoded JSON `Conf` attribute on `MasterRecoveryState` events, plus `RawJSON`.
- `RecoveryState` records time, status code, status text, and the event index of a `MasterRecoveryState`.
- `EpochVersionInfo` correlates recovery epoch data with known committed/recovery versions from `GetDurableResult` and `UpdateRegistration`.
- `TraceData` stores sorted slices of events, configs, recovery states, epoch version info, min/max time, and a default scrub `TimeStep`.
- `parseTraceFile(filepath string)` streams XML, builds slices, sorts them, builds indices, and returns `TraceData`.
- `parseDBConfig(confStr string, time float64)` decodes HTML entities, parses JSON, and extracts common config fields.
- Query helpers:
  - `GetEventsUpToTime(targetTime float64)`
  - `GetLatestConfigAtTime(targetTime float64)`
  - `GetLatestRecoveryStateAtIndex(eventIndex int)`
  - `GetLatestEpochVersionAtIndex(eventIndex int)`
  - `FindPreviousRecovery(eventIndex int)`
  - `FindNextRecovery(eventIndex int)`
  - `FindPreviousRecoveryWithStatusCode(eventIndex int, statusCode string)`
  - `FindNextRecoveryWithStatusCode(eventIndex int, statusCode string)`
  - `GetEventIndexAtTime(targetTime float64)`

## Control Flow

`parseTraceFile()` opens the file, estimates event capacity from file size, creates an `xml.Decoder`, and loops through XML tokens. For each `<Event>` start element, it builds a `TraceEvent`, mapping known attributes to top-level fields and storing all other attributes in `Attrs`. `Time` is parsed as float and updates `maxTime`. Every event is appended.

While streaming, `MasterRecoveryState` events with a `Conf` attribute are passed to `parseDBConfig()` and appended to `configs` if JSON parsing succeeds.

After EOF, the function sorts events and configs by time. It then builds:

- `RecoveryStates` by scanning sorted events for `MasterRecoveryState` events with both `StatusCode` and `Status`, storing the sorted event index.
- `EpochVersions` with two passes: first collect KCV by recovery/end version from `GetDurableResult`, then scan `UpdateRegistration` events for epoch, recovery transaction version, and last epoch end. Valid entries are optionally enriched with KCV when the last epoch end matches a collected durable result.
- `TimeStep` by sampling up to the first 10,000 sorted events and selecting the smallest positive interval, with `0.1` fallback.

The query helpers rely on sorted slices and `sort.Search`. Time-based helpers search on `TimeValue` or config `Time`; recovery/epoch helpers search on `EventIndex`.

## State and Persistence Behavior

All parsed data is held in memory. `TraceEvent.Attrs` maps own string copies produced by the XML decoder. There is no on-disk cache or incremental persistence. `GetEventsUpToTime()` returns a slice view of `td.Events`, not a copy; callers should treat it as read-only.

`MinTime` is initialized to `0.0` and never updated during parsing. For traces whose first event time is not zero or whose events all have positive times, `MinTime` will still be zero. `MaxTime` is updated while streaming before sorting.

The parser prints progress and status to stdout, while `main.go` prints its summary to stderr. This mixed output is acceptable for an interactive tool but relevant for scripts/tests.

## Dependencies and Integration Points

This file uses standard packages `encoding/xml`, `encoding/json`, `fmt`, `html`, `io`, `os`, `sort`, and `strconv`. It is consumed by `main.go` for initial load, by `cluster.go` through `TraceEvent`, and by `ui.go` for navigation, configuration display, recovery status display, and epoch/version panels.

## Risks and Edge Cases

- The entire trace is stored in memory. Very large XML traces can consume substantial RAM despite streaming token decoding.
- `MinTime` is not computed, so UI ranges or summaries using it may be misleading.
- XML decoder errors abort the whole load; malformed late events lose all earlier parsed data.
- `file.Stat()` ignores its error before calling `fileInfo.Size()`, though stat on an open file normally succeeds. If it failed, this would panic.
- Config JSON parsing silently drops malformed configs by returning nil.
- Numeric config fields are decoded as `float64` and converted to `int`; large values or non-integer JSON numbers could truncate.
- `strconv.ParseInt` errors for version fields are ignored, turning malformed values into zero and potentially filtering or mis-correlating epoch data.
- `kcvByRV` stores one KCV per end version; duplicate `GetDurableResult` events for the same end version overwrite prior entries.
- `GetEventIndexAtTime()` returns `len(td.Events)-1` when target is after the last event, but if `td.Events` is empty this returns `-1`. Callers must handle empty traces.
- Query helpers return pointers into slices. Those remain stable while slices are not reallocated, but callers should not append to the stored slices concurrently.
- Sorting solely by `TimeValue` is not stable. Same-time event ordering may change, which can matter for role transitions or recovery state indexing.

## Test Signals

Tests should parse minimal and multi-event trace XML, malformed XML, events with extra attributes, missing/invalid time values, `MasterRecoveryState` configs with HTML-encoded JSON, malformed config JSON, recovery states with and without status fields, durable/update epoch matching, duplicate same-time events, empty traces, and query boundaries before first event, exactly on an event, between events, and after the last event.

Performance tests should exercise large traces to observe memory growth, progress logging, sort time, and query latency. Integration tests should validate `BuildClusterState()` and `ui.go` consumers against sorted event slices with event-index semantics.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/replay/trace.go -->
