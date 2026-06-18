# subset-b-007975 Research

Grouped research report for the requested source-tree-aligned files. Each file section is delimited for deterministic reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdVoms/XrdVomsgsi.cc -->
# sources/distributed-fs/xrootd/src/XrdVoms/XrdVomsgsi.cc

## Purpose

This file is the externally loadable GSI VOMS plugin entry point. It bridges the historical XRootD GSI security plugin ABI to the `XrdVomsFun` implementation by exporting C-linkage functions named `XrdSecgsiVOMSFun` and `XrdSecgsiVOMSInit`.

## Important APIs, Types, and Functions

- `XrdSecgsiVOMSInit(const char *cfg)`: creates a process-global `XrdVomsFun` instance with a static `XrdSysLogger` and `XrdSysError` destination, then delegates configuration parsing to `XrdVomsFun::VOMSInit`.
- `XrdSecgsiVOMSFun(XrdSecEntity &ent)`: validates that initialization created `vomsFun`, then delegates credential extraction and entity mutation to `XrdVomsFun::VOMSFun`.
- Anonymous-namespace `XrdVomsFun *vomsFun`: plugin singleton used by both exported functions.

## Control Flow

Initialization is expected before credential processing. `XrdSecgsiVOMSInit` allocates `XrdVomsFun`, keeps it in the static pointer, and returns the result of `VOMSInit`. Later, the GSI layer calls `XrdSecgsiVOMSFun`, which returns `-1` when initialization has not happened and otherwise forwards the `XrdSecEntity` by reference.

## State and Persistence Behavior

State is process-local and static. The logger and error destination live for process lifetime, and every successful init overwrites `vomsFun` with a newly allocated object without deleting any previous object. Persistent configuration and mapfile behavior live in `XrdVomsFun`, not this file.

## Dependencies and Integration Points

The file depends on `XrdSysError`, `XrdSysLogger`, `XrdSecEntity` through the VOMS API, and `XrdVomsFun.hh`. Its exported symbol names are the integration surface for dynamic plugin loading and preserve backward compatibility with older GSI VOMS naming.

## Risks

- Repeated `XrdSecgsiVOMSInit` calls leak the prior `XrdVomsFun` object and replace global behavior.
- `XrdSecgsiVOMSFun` has no locking around `vomsFun`, so concurrent calls during reinitialization would race.
- Failure is compressed to `-1` before initialization; richer diagnostics depend on initialization logs in `XrdVomsFun`.

## Test Signals

Useful checks are dynamic loading symbol tests, invoking `XrdSecgsiVOMSFun` before init and expecting `-1`, init with valid and invalid VOMS config strings, and integration tests confirming `XrdSecEntity` fields are populated by the delegated implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdVoms/XrdVomsgsi.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXml/CMakeLists.txt -->
# sources/distributed-fs/xrootd/src/XrdXml/CMakeLists.txt

## Purpose

This CMake file builds the `XrdXml` shared library and wires in the bundled TinyXML object library plus optional libxml2-backed reader support.

## Important APIs, Types, and Functions

- `add_subdirectory(tinyxml)`: builds `XrdTinyXml` from the bundled TinyXML source.
- `add_library(XrdXml SHARED ...)`: includes metalink conversion, TinyXML reader, and abstract reader sources.
- `find_package(LibXml2)`: conditionally adds `XrdXmlRdrXml2.cc/.hh`, defines `HAVE_XML2`, and links `LibXml2::LibXml2`.
- `target_link_libraries(XrdXml PUBLIC XrdTinyXml PRIVATE XrdUtils ${CMAKE_THREAD_LIBS_INIT})`: exposes the TinyXML object dependency and private XRootD utility/thread dependencies.

## Control Flow

The build always includes the TinyXML adapter and abstract XML reader. If libxml2 is found at configure time, the streaming XML reader is compiled into the same shared library and made selectable at runtime by `XrdXmlReader::GetReader(..., "libxml2")`.

## State and Persistence Behavior

No runtime state is kept here. The file controls shared object version metadata using `${XRootD_VERSION_MAJOR}` and `${XRootD_LIBVERSION}` and installs the resulting library into `${CMAKE_INSTALL_LIBDIR}`.

## Dependencies and Integration Points

`XrdXml` integrates with `XrdTinyXml`, `XrdUtils`, thread libraries, and optional LibXml2. The `HAVE_XML2` compile definition is consumed by `XrdXmlReader.cc` to expose the libxml2 implementation.

## Risks

- Runtime support for `"libxml2"` silently depends on configure-time discovery; code using that implementation must handle `ENOTSUP`.
- `XrdTinyXml` is public, so include path and object-library details can affect downstream targets.
- The bundled TinyXML code is old and receives no external package update through this CMake path.

## Test Signals

Build tests should cover configurations with and without LibXml2, verify that `XrdXml` links and installs with the expected SO version, and check that `XrdXmlReader::Init("libxml2")` behaves according to `LIBXML2_FOUND`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXml/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXml/XrdXmlMetaLink.cc -->
# sources/distributed-fs/xrootd/src/XrdXml/XrdXmlMetaLink.cc

## Purpose

This file implements conversion from Metalink XML v3 or v4 documents into one or more `XrdOucFileInfo` objects. It extracts file names, URLs, hashes, sizes, global logical file names, priorities, and protocols while allowing callers to filter URL protocols and optionally synthesize a global redirect URL.

## Important APIs, Types, and Functions

- `XrdXmlMetaLink::Convert(const char *fname, int blen)`: converts the first applicable file entry from a path or memory buffer.
- `XrdXmlMetaLink::ConvertAll(const char *fname, int &count, int blen)`: converts all file entries and returns an array of `XrdOucFileInfo *`.
- `XrdXmlMetaLink::DeleteAll`: deletes arrays returned by `ConvertAll`.
- Private parsing helpers: `GetFile`, `GetFileInfo`, `GetGLfn`, `GetHash`, `GetSize`, `GetUrl`, `GetName`, `UrlOK`, `GetRdrError`, and `PutFile`.
- RAII helper classes `CleanUp` and `vecMon`: delete the active reader/temp file and free attribute vectors.

## Control Flow

For buffer input, `PutFile` writes the buffer to a unique `/tmp/.MetaLink<time>.<pid>.<seq>` path, then cleanup unlinks it on return. `Convert` creates an `XrdXmlReader`, finds the root `metalink` tag, reads its `xmlns`, switches v3 documents into the `files` scope, and rejects unknown namespaces. It then loops over `file` tags, allocating a new `XrdOucFileInfo`, extracting sub-elements, linking successful entries into `fileList`, and optionally adding a global URL constructed from `rdProt`, `rdHost`, and an extracted `glfn`. In single-file mode it returns only the first linked file and treats accumulated errors as fatal.

`GetFileInfo` walks selected child tags in the current scope. `url` tags add matching protocol URLs and set `noUrl=false`; `hash` and `size` are required to contain valid text when encountered; `verification` and `resources` are processed recursively; `glfn` adds an LFN. The final result for a file is accepted only if at least one URL passed the protocol filter.

## State and Persistence Behavior

Each `XrdXmlMetaLink` instance keeps parser state in `reader`, `fileList`, `lastFile`, `currFile`, `fileCnt`, `doAll`, `noUrl`, and last error fields `eCode/eText`. Temporary file naming uses process-wide `tmpPath`, `seqNo`, and `xMutex`, seeded by `GenTmpPath`. Temporary files are persisted only during conversion and unlinked by `CleanUp`.

## Dependencies and Integration Points

The converter depends on `XrdXmlReader` implementations, `XrdOucFileInfo` mutators (`AddUrl`, `AddProtocol`, `AddDigest`, `SetSize`, `AddLfn`, `AddFileName`), XRootD atomics/mutex wrappers, `XrdSysFD_Open`, `XrdSysE2T`, and POSIX `unlink`, `write`, and `close`. It is the consumer-facing bridge from XML metalink documents to XRootD file-location metadata.

## Risks

- `ConvertAll` sets `doAll=true` and never resets it, so reusing the same object for later `Convert` calls can keep all-file behavior.
- The temporary-file implementation uses `/tmp` and a custom name scheme rather than `mkstemp`; `O_EXCL` helps but failure paths and permissions still need scrutiny.
- `UrlOK` records every protocol on the `XrdOucFileInfo` before checking the filter, so rejected protocols can still appear in protocol metadata.
- `strstr(prots, pBuff)` can match protocols as substrings if protocol-list formatting is not strict.
- XML content is accepted leniently; the header comment explicitly says it is not a rigorous RFC validator.
- In `PutFile`, `fd > 0` treats descriptor 0 as failure even though `open` can legally return 0.

## Test Signals

Tests should cover Metalink v3 and v4 root namespace handling, required `xmlns`, unsupported namespace rejection, URL protocol filtering, v3 `files` scoping, nested `verification/resources`, invalid sizes, missing hash attributes, buffer input cleanup, `ConvertAll` array ownership, and global URL synthesis from `glfn`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXml/XrdXmlMetaLink.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXml/XrdXmlMetaLink.hh -->
# sources/distributed-fs/xrootd/src/XrdXml/XrdXmlMetaLink.hh

## Purpose

This header declares the Metalink conversion interface that turns XML specifications into `XrdOucFileInfo` objects. It documents that conversion is intentionally permissive and may accept non-strict Metalink v3/v4 inputs when enough usable information is present.

## Important APIs, Types, and Functions

- `XrdXmlMetaLink::Convert`: returns one `XrdOucFileInfo` for the first usable file entry.
- `XrdXmlMetaLink::ConvertAll`: returns all usable file entries plus a count.
- `XrdXmlMetaLink::DeleteAll`: companion cleanup helper for `ConvertAll`.
- `GetStatus(int &ecode)`: exposes `eText` and `eCode` from the previous conversion.
- Constructor parameters: `protos` URL protocol allow-list, `rdprot` synthetic global-file protocol, `rdhost` synthetic global-file host, and `encode` XML encoding hint.

## Control Flow

The public methods delegate to private parser helpers. The class owns its current `XrdXmlReader`, active and linked `XrdOucFileInfo` instances, protocol strings, temporary filename buffer, and status text. The constructor duplicates `protos` and `encode`, stores redirect parameters by pointer, initializes counters and flags, and clears error/temp buffers.

## State and Persistence Behavior

Per-object state is mutable across conversions. `prots` and `encType` are heap-duplicated and freed in the destructor. `rdProt` and `rdHost` are borrowed pointers, so callers must ensure their lifetime covers the converter use. `tmpFn` and `eText` are fixed-size buffers.

## Dependencies and Integration Points

The header depends on `XrdOucFileInfo.hh` and `XrdXmlReader.hh`. It exposes the expected ownership model: returned file info objects are owned by the caller, and arrays from `ConvertAll` require deleting each element or calling `DeleteAll`.

## Risks

- Borrowed `rdProt` and `rdHost` can dangle if caller-provided storage is transient.
- The destructor does not delete any active `reader` or file list; implementation relies on conversion-time RAII cleanup and caller ownership transfers.
- Fixed-size error buffers truncate long filesystem or parser messages.
- Stateful members make object reuse sensitive to flags such as `doAll` and prior errors.

## Test Signals

Header-level contract tests should verify default constructor behavior (`root:xroot:` filter and `xroot:` redirect protocol), caller ownership of returned objects, `GetStatus` after success and failure, and safe destruction after failed conversions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXml/XrdXmlMetaLink.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXml/XrdXmlRdrTiny.cc -->
# sources/distributed-fs/xrootd/src/XrdXml/XrdXmlRdrTiny.cc

## Purpose

This file implements `XrdXmlReader` using the bundled TinyXML DOM parser. It gives XRootD a small in-process XML reader suitable for small documents such as Metalink files.

## Important APIs, Types, and Functions

- `XrdXmlRdrTiny::XrdXmlRdrTiny(bool &aOK, const char *fname, const char *enc)`: validates the file with `stat`, loads it into a `TiXmlDocument`, initializes traversal pointers, and reports construction success.
- `GetElement(const char **ename, bool reqd)`: searches sibling/child DOM nodes for named elements inside a caller-specified scope.
- `GetAttributes(const char **aname, char **aval)`: duplicates matching attribute values from the current element using `strdup`.
- `GetText(const char *ename, bool reqd)`: duplicates simple text from the current element via `TiXmlElement::GetText`.
- `Init()`: always returns true.

## Control Flow

Construction loads the entire XML document into memory, stores the document as the initial `curNode`, and sets `elmNode` to the current scan point. `GetElement` verifies the requested scope against the current node or last returned element, chooses the next child or sibling scan start, and returns the index of the first requested element. When no matching element remains in the scope, it moves back to the parent and returns 0. `GetAttributes` and `GetText` require a successful prior `GetElement`.

## State and Persistence Behavior

The reader owns a `TiXmlDocument *reader` and deletes it in the destructor. Traversal state is held in `curNode`, `curElem`, and `elmNode`. Error state is stored as `eCode` and `eText`; debug printing to `stderr` is enabled by `XrdXmlDEBUG`.

## Dependencies and Integration Points

The implementation depends on bundled `tinyxml.h`, POSIX `stat`, `XrdSysE2T`, and the abstract `XrdXmlReader` contract. It is the default implementation selected by `XrdXmlReader::GetReader` and is used by `XrdXmlMetaLink` unless another implementation is requested.

## Risks

- The `reqd` error block in `GetElement` is unreachable because the function returns 0 before checking `reqd`; required missing elements may not set the intended error.
- It builds a full DOM tree, so large XML inputs consume memory and parsing time upfront.
- The `enc` constructor argument is ignored, leaving TinyXML to auto-detect or parse under defaults.
- Only simple first-child text is returned by `TiXmlElement::GetText`; mixed-content XML can be truncated.
- Error handling around `LoadFile` appears inverted for `ErrorDesc()` emptiness and may report "Unknown error" in some parser-error cases.

## Test Signals

Tests should cover required and optional element misses, nested scope transitions, repeated sibling scans, attribute duplication/freeing, mixed-content text behavior, invalid XML load errors, `XrdXmlDEBUG` trace output, and large document rejection expectations at a higher layer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXml/XrdXmlRdrTiny.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXml/XrdXmlRdrTiny.hh -->
# sources/distributed-fs/xrootd/src/XrdXml/XrdXmlRdrTiny.hh

## Purpose

This header declares the TinyXML-backed implementation of the abstract `XrdXmlReader` interface.

## Important APIs, Types, and Functions

- Overrides `GetAttributes`, `GetElement`, `GetError`, and `GetText`.
- `static bool Init()`: preinitialization hook, currently trivial.
- Constructor and destructor manage an underlying `TiXmlDocument`.
- Private `Debug` emits traversal diagnostics when enabled.

## Control Flow

The class exposes the same pull-style reader interface as other implementations: callers fetch an element, then fetch attributes or text from the current element. Internally, the `.cc` file uses DOM node pointers to emulate a streaming-ish scoped walk.

## State and Persistence Behavior

Persistent per-reader fields include the TinyXML document pointer, current node/element pointers, last error code/text, and a debug flag. The fixed `eText[251]` buffer stores transient error descriptions.

## Dependencies and Integration Points

The header forward-declares `TiXmlDocument`, `TiXmlElement`, and `TiXmlNode` to avoid exposing TinyXML internals to users. It inherits from `XrdXmlReader` and is instantiated by `XrdXmlReader::GetReader`.

## Risks

- The file comment says "based on libxml2" even though this is the TinyXML reader, which can mislead maintainers.
- Traversal state is mutable and not thread-safe per instance.
- Error buffer size is fixed and may truncate.

## Test Signals

Compile tests should validate no TinyXML header leak through this header. Behavioral tests should instantiate through `XrdXmlReader::GetReader` and verify virtual dispatch through the abstract interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXml/XrdXmlRdrTiny.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXml/XrdXmlRdrXml2.cc -->
# sources/distributed-fs/xrootd/src/XrdXml/XrdXmlRdrXml2.cc

## Purpose

This file implements the optional libxml2-backed `XrdXmlReader`. It provides a streaming XML reader better suited to larger documents and exposes the same element, attribute, text, and error methods as the TinyXML adapter.

## Important APIs, Types, and Functions

- `XrdXmlRdrXml2::XrdXmlRdrXml2(bool &aOK, const char *fname, const char *enc)`: creates an `xmlTextReader` for a file path.
- `GetElement(const char **ename, bool reqd)`: advances the libxml2 reader until one of the requested start tags is found or the current scope end tag is reached.
- `GetAttributes(const char **aname, char **aval)`: iterates attributes on the current start element, duplicates requested values, and returns whether any were found.
- `GetText(const char *ename, bool reqd)`: reads the next node and returns text content if present.
- `Init()`: calls `xmlInitParser`.
- `Free(void *strP)`: wrapper for `xmlFree`, though the public base class does not declare it.

## Control Flow

Construction stores a duplicated encoding string in `encType`, initializes flags, and opens the libxml2 text reader. `GetElement` calls `xmlTextReaderRead` in a loop, skips significant whitespace or nameless nodes, returns the requested element index on a matching start element, and stops when it sees the caller-provided scope end element. Attribute and text methods operate relative to the current libxml2 cursor.

## State and Persistence Behavior

The instance owns `_xmlTextReader *reader` and frees it in the destructor. It also stores `encType`, `eCode/eText`, `doDup`, and a debug flag. Returned strings are duplicated with `strdup` by default so callers can use `free()` consistently, avoiding libxml allocator ownership leakage.

## Dependencies and Integration Points

The implementation depends on `<libxml/xmlreader.h>`, `XrdSysE2T`, and `XrdXmlReader`. It is compiled only when `HAVE_XML2` is defined by CMake and selected by `XrdXmlReader::GetReader(..., "libxml2")`.

## Risks

- `encType` is allocated but not freed in the destructor, producing a small per-reader leak when an encoding is supplied.
- The constructor ignores `encType` when calling `xmlNewTextReaderFilename`, so the encoding hint is effectively unused.
- `GetAttributes` leaves the reader positioned on the last attribute, relying on later libxml2 reads to recover correctly.
- `GetText` only checks the immediate next node for text, so mixed content or CDATA can be missed.
- libxml2 global initialization requirements are documented at the base layer; callers must invoke `Init("libxml2")` early in threaded applications.

## Test Signals

Tests should build with LibXml2 enabled, call `Init("libxml2")`, parse large documents without full-DOM memory spikes, verify scope-end behavior, exercise missing required elements, attribute duplication/freeing, CDATA/text handling, and run under leak checking for encoded reader creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXml/XrdXmlRdrXml2.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXml/XrdXmlRdrXml2.hh -->
# sources/distributed-fs/xrootd/src/XrdXml/XrdXmlRdrXml2.hh

## Purpose

This header declares the optional libxml2 implementation of `XrdXmlReader`.

## Important APIs, Types, and Functions

- Overrides `GetAttributes`, `GetElement`, `GetError`, and `GetText`.
- Adds `Free(void *strP)` for libxml-allocated string cleanup, although current implementation normally duplicates values with `strdup`.
- `static bool Init()` exposes libxml2 preinitialization.
- Private helpers `Debug` and `GetName` wrap diagnostic output and libxml name extraction.

## Control Flow

The class is instantiated by `XrdXmlReader::GetReader` when the implementation string is `"libxml2"` and the build includes `HAVE_XML2`. Users interact only through the base pull-reader interface.

## State and Persistence Behavior

It stores a libxml2 text reader pointer, borrowed/duplicated encoding text, an error buffer, a duplication mode flag, and debug mode. The reader object is mutable and intended for one parsing stream.

## Dependencies and Integration Points

The header forward-declares `_xmlTextReader` to avoid exposing libxml2 headers. It depends on `XrdXmlReader.hh` and is included only when CMake finds LibXml2.

## Risks

- `Free` is not present in the base class, so generic callers cannot rely on it through `XrdXmlReader *`.
- The implementation is not always available; code must handle `ENOTSUP` in non-libxml2 builds.
- Per-instance use is not thread-safe, and libxml2 global state requires preinitialization in threaded programs.

## Test Signals

Compile tests should cover LibXml2-present and LibXml2-absent builds. Interface tests should confirm selecting `"libxml2"` returns this implementation only when compiled in and that all returned strings can be released with `free()` under default duplication mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXml/XrdXmlRdrXml2.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXml/XrdXmlReader.cc -->
# sources/distributed-fs/xrootd/src/XrdXml/XrdXmlReader.cc

## Purpose

This file implements the factory and preinitialization methods for the abstract XML reader interface.

## Important APIs, Types, and Functions

- `XrdXmlReader::GetReader(const char *fname, const char *enc, const char *impl)`: creates either `XrdXmlRdrTiny` or, when compiled in, `XrdXmlRdrXml2`.
- `XrdXmlReader::Init(const char *impl)`: returns true for TinyXML and delegates to `XrdXmlRdrXml2::Init` for libxml2.

## Control Flow

If `impl` is null or `"tinyxml"`, the factory constructs a TinyXML reader and returns it on successful construction. If construction fails, it fetches the reader error code, deletes the reader, sets `errno`, and returns null. If `impl` is `"libxml2"` and `HAVE_XML2` is available, the same pattern is used for `XrdXmlRdrXml2`. Unknown or unavailable implementations set `errno=ENOTSUP`.

## State and Persistence Behavior

The file keeps no persistent state. Ownership of a successful reader transfers to the caller, who must delete it. Failure diagnostics are reported through `errno` after the temporary object is deleted.

## Dependencies and Integration Points

It always includes `XrdXmlRdrTiny.hh` and conditionally includes `XrdXmlRdrXml2.hh`. `HAVE_XML2` is defined by `src/XrdXml/CMakeLists.txt`. `XrdXmlMetaLink` and any other XML consumers use this file as the implementation-selection point.

## Risks

- Implementation selection is stringly typed and silently defaults null to TinyXML.
- Error text from failed constructors is lost after deletion; callers only receive `errno`.
- No plugin or registry mechanism exists; adding readers requires editing this factory.

## Test Signals

Tests should validate null, `"tinyxml"`, `"libxml2"`, and unknown implementation strings; `errno` on nonexistent files; `Init` behavior in both build modes; and ownership cleanup of returned reader objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXml/XrdXmlReader.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXml/XrdXmlReader.hh -->
# sources/distributed-fs/xrootd/src/XrdXml/XrdXmlReader.hh

## Purpose

This header defines the abstract pull-style XML reader API used by XRootD XML consumers. It hides TinyXML and libxml2 behind a small common interface.

## Important APIs, Types, and Functions

- Pure virtual `GetAttributes`, `GetElement`, `GetError`, and `GetText`.
- Static `GetReader` factory, with implementation choices `"tinyxml"` and `"libxml2"`.
- Static `Init`, intended for preinitializing implementations with global/thread-safety requirements.

## Control Flow

Callers obtain a reader for a file, repeatedly call `GetElement` with a scope-plus-candidates array, then call `GetAttributes` and/or `GetText` for the current tag. `GetElement` returns 0 on scope end or not found, and positive indexes corresponding to the candidate array.

## State and Persistence Behavior

The base class has no state and a virtual destructor. State, memory allocation strategy, and parser cursor behavior are implementation-specific. The API specifies that returned attribute values and text must be freed with `free()`.

## Dependencies and Integration Points

The header is intentionally dependency-light and is consumed by `XrdXmlMetaLink`, `XrdXmlRdrTiny`, `XrdXmlRdrXml2`, and factory callers. It documents that TinyXML builds a full DOM and libxml2 streams.

## Risks

- The API overloads return value 0 for scope end and not-found, so callers must inspect `GetError` when required semantics matter.
- Memory ownership is C-style and relies on callers freeing every returned string.
- The comments contain small typos and say `GetRead()` rather than `GetReader()`, but the API itself is clear.
- Implementation-specific thread-safety is exposed only through documentation, not type constraints.

## Test Signals

Contract tests should run the same XML traversal through both implementations where available, verify string-free ownership, confirm required-tag error behavior, and test threaded preinitialization guidance for libxml2.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXml/XrdXmlReader.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXml/tinyxml/CMakeLists.txt -->
# sources/distributed-fs/xrootd/src/XrdXml/tinyxml/CMakeLists.txt

## Purpose

This CMake file builds the bundled TinyXML source as the `XrdTinyXml` object library used by `XrdXml`.

## Important APIs, Types, and Functions

- `add_library(XrdTinyXml OBJECT ...)`: compiles `tinystr`, `tinyxml`, error text, and parser sources into reusable object files.
- `POSITION_INDEPENDENT_CODE ON`: makes objects safe to include in shared libraries.
- `target_include_directories(... PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>)`: exposes `tinyxml.h` and `tinystr.h` during the build.

## Control Flow

The parent `XrdXml` CMake file adds this subdirectory, then links the object library into the shared `XrdXml` library.

## State and Persistence Behavior

No runtime state exists here. It controls build-time object composition and include paths only.

## Dependencies and Integration Points

The object library is the dependency that lets `XrdXmlRdrTiny.cc` include `tinyxml.h` without a system TinyXML package.

## Risks

- Object library consumers inherit bundled TinyXML implementation details.
- There is no versioned external package boundary; updating TinyXML means editing vendored source.
- Public include exposure can collide if another target also uses a different TinyXML header.

## Test Signals

Build tests should verify position-independent compilation and that `XrdXmlRdrTiny.cc` can include `tinyxml.h` via the target include path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXml/tinyxml/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXml/tinyxml/tinystr.cpp -->
# sources/distributed-fs/xrootd/src/XrdXml/tinyxml/tinystr.cpp

## Purpose

This file implements TinyXML's lightweight `TiXmlString` class when `TIXML_USE_STL` is not defined.

## Important APIs, Types, and Functions

- `TiXmlString::npos`: sentinel for failed finds.
- `TiXmlString::nullrep_`: shared empty representation.
- `reserve`, `assign`, and `append`: manage string capacity and content.
- Non-member `operator+` overloads for `TiXmlString` combinations with other `TiXmlString` or C strings.

## Control Flow

`reserve` grows capacity by allocating a temporary string with requested capacity, copying existing bytes, and swapping representations. `assign` either reallocates when capacity is too small or too large relative to new content, or reuses the buffer with `memmove`. `append` grows capacity using `newsize + capacity()` and appends to the current finish pointer.

## State and Persistence Behavior

Each string owns a `Rep` buffer except empty strings, which point at the static `nullrep_`. The implementation uses an `int[]` allocation cast to `Rep *` for alignment portability. All state is in memory.

## Dependencies and Integration Points

It includes `tinystr.h` and is compiled only in non-STL TinyXML mode. `tinyxml.h` maps `TIXML_STRING` to `TiXmlString` unless `TIXML_USE_STL` is enabled.

## Risks

- Assumes non-null C strings in constructors/operators.
- Capacity growth and shrink heuristics are custom and old; overflow is theoretically possible for extreme sizes.
- Uses raw `new[]`, casts, `memmove`, and no exception handling beyond normal C++ allocation behavior.

## Test Signals

Tests should cover empty-string sharing, assign shorter/longer values, append after reserve, concatenation operators, self-overlap safety through `memmove`, and builds with and without `TIXML_USE_STL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXml/tinyxml/tinystr.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXml/tinyxml/tinystr.h -->
# sources/distributed-fs/xrootd/src/XrdXml/tinyxml/tinystr.h

## Purpose

This header defines TinyXML's minimal string and output-stream substitutes for builds without dependable STL support.

## Important APIs, Types, and Functions

- `TiXmlString`: small subset of `std::string` with constructors, assignment, append, `c_str`, `data`, `length`, `capacity`, `find`, `clear`, `reserve`, and comparison operators.
- `TiXmlOutStream`: `TiXmlString` subclass with `operator<<` for TinyXML output accumulation.
- `TIXML_EXPLICIT`: portability macro for older compilers.

## Control Flow

The class wraps a mutable `Rep` structure with size, capacity, and inline storage. Empty strings share `nullrep_`; non-empty strings allocate a buffer. Mutating operations call `assign`, `append`, `reserve`, or `clear`, with comparisons delegated to `strcmp`.

## State and Persistence Behavior

String contents are heap-resident unless empty. Copy construction and assignment make independent buffers. `operator[]` returns a non-const reference even from a const method, reflecting the older TinyXML API style.

## Dependencies and Integration Points

The header is active only when `TIXML_USE_STL` is not defined. `tinyxml.h` uses it as `TIXML_STRING`, and all TinyXML parser/DOM code is built against that typedef.

## Risks

- Not a complete or standards-compatible `std::string`; callers must not assume STL semantics.
- Indexing relies on `assert` and has no runtime bounds checks in release builds.
- C-string operations require null-terminated input.
- The unusual allocation layout can be fragile with sanitizers or exotic allocators.

## Test Signals

Compile TinyXML in non-STL mode, run parser load/save tests, and directly test `TiXmlString` copy, clear, reserve, find, comparisons, and `TiXmlOutStream` append behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXml/tinyxml/tinystr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXml/tinyxml/tinyxml.cpp -->
# sources/distributed-fs/xrootd/src/XrdXml/tinyxml/tinyxml.cpp

## Purpose

This file implements most TinyXML DOM operations, printing, file loading/saving, attribute handling, cloning, visitor traversal, and in-memory XML string generation.

## Important APIs, Types, and Functions

- `TiXmlBase::EncodeString`: escapes XML special characters and control bytes.
- `TiXmlNode` operations: construction/destruction, child insertion/replacement/removal, sibling/child traversal, `GetDocument`.
- `TiXmlElement`: attribute getters/setters/query methods, `Print`, `CopyTo`, `Accept`, `Clone`, and `GetText`.
- `TiXmlDocument`: `LoadFile`, `SaveFile`, `Parse` entry support, error state copying, `Print`, `Accept`, and cloning.
- `TiXmlAttribute`, `TiXmlAttributeSet`: query/print/set numeric values and manage circular attribute lists.
- `TiXmlHandle`: null-safe child traversal wrapper.
- `TiXmlPrinter`: visitor that prints XML to a buffer with configurable indentation and line breaks.

## Control Flow

DOM nodes own linked lists of children; insert operations clone or link nodes and wire `parent`, `prev`, and `next` pointers. Destructors recursively delete children, and element cleanup deletes attributes. `LoadFile` reads the whole file in binary mode, normalizes CR/LF sequences in memory, calls `Parse`, and returns whether the document has an error. Printing walks the DOM recursively or via the visitor and emits compact or formatted XML depending on node shape.

## State and Persistence Behavior

Documents persist an in-memory DOM, error flags, row/column location, tab size, and UTF-8 BOM state. Nodes persist value strings, user data pointers, source locations, parent/child/sibling pointers, and type tags. File load/save persists XML to disk only when callers invoke document file methods. Static state includes whitespace condensation in `TiXmlBase::condenseWhiteSpace`.

## Dependencies and Integration Points

It depends on `tinyxml.h`, C `FILE *` I/O, and optional STL stream support. In this repository it is bundled into `XrdTinyXml` and consumed by `XrdXmlRdrTiny` for DOM parsing.

## Risks

- Loading reads entire files into memory and uses `long` file lengths from `ftell`, which is unsuitable for very large files.
- The DOM owns linked raw pointers; misuse of `LinkEndChild` ownership can cause leaks or double deletes outside expected patterns.
- Printing uses `fprintf` and buffers, so malformed values are escaped only through paths that call `EncodeString`.
- `TiXmlPrinter` uses a single `simpleTextPrint` bool, which can be fragile for nested visitor state.
- Error reporting stores only the first error and uses English static strings.

## Test Signals

Tests should cover parse/load/save round trips, CR/LF normalization, element/attribute mutation, cloning, child replacement/removal, visitor printing, CDATA/text/comment/declaration/unknown nodes, duplicate document-child rejection, and memory-sanitizer runs for ownership operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXml/tinyxml/tinyxml.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXml/tinyxml/tinyxml.h -->
# sources/distributed-fs/xrootd/src/XrdXml/tinyxml/tinyxml.h

## Purpose

This header declares the TinyXML 2.6.2 DOM, parser, visitor, handle, printer, encoding, and error APIs vendored into XRootD.

## Important APIs, Types, and Functions

- Version constants `TIXML_MAJOR_VERSION`, `TIXML_MINOR_VERSION`, `TIXML_PATCH_VERSION`.
- `TiXmlBase`: common parse helpers, error IDs, entity helpers, encoding helpers, whitespace policy, row/column/user data.
- `TiXmlNode`: parent/child/sibling DOM base with virtual `Parse`, `Clone`, `Print`, `Accept`, and cast helpers.
- `TiXmlElement`, `TiXmlAttribute`, `TiXmlAttributeSet`: elements and attributes, including typed query helpers.
- `TiXmlText`, `TiXmlComment`, `TiXmlDeclaration`, `TiXmlUnknown`, and `TiXmlDocument`: concrete XML node types.
- `TiXmlVisitor`, `TiXmlHandle`, and `TiXmlPrinter`: visitor traversal, null-safe navigation, and string printing.

## Control Flow

The header defines a classic object-oriented DOM. Parsing starts at `TiXmlDocument::Parse` or `LoadFile`, which creates concrete node objects through virtual parse methods. Navigation uses child/sibling linked lists. Output uses recursive `Print` or visitor-based `Accept` through `TiXmlPrinter`.

## State and Persistence Behavior

Every node stores value, parent/child/sibling pointers, type, user data, and parse location. Documents add error state, tab size, and BOM flag. Attribute sets use a circular sentinel list. Static parser state includes entity tables, UTF-8 byte table, error strings, and whitespace condensation.

## Dependencies and Integration Points

The header can use STL strings/streams when `TIXML_USE_STL` is set; otherwise it depends on `tinystr.h`. XRootD's TinyXML reader includes this header directly and uses `TiXmlDocument`, `TiXmlNode`, and `TiXmlElement`.

## Risks

- The API predates modern C++ ownership conventions and uses raw pointers extensively.
- Non-STL mode supplies only a partial string implementation.
- XML namespace, DTD, schema, streaming, and full encoding support are limited.
- Many methods return null on error without rich diagnostics unless the containing document has error state.

## Test Signals

Header/API tests should compile both STL and non-STL modes, exercise public DOM navigation and mutation APIs, verify error IDs and row/column reporting, and ensure XRootD's `XrdXmlRdrTiny` only relies on stable public APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXml/tinyxml/tinyxml.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXml/tinyxml/tinyxmlerror.cpp -->
# sources/distributed-fs/xrootd/src/XrdXml/tinyxml/tinyxmlerror.cpp

## Purpose

This file defines TinyXML's static English error-message table.

## Important APIs, Types, and Functions

- `TiXmlBase::errorString[TIXML_ERROR_STRING_COUNT]`: maps TinyXML error IDs to user-facing text.

## Control Flow

There is no executable control flow beyond static initialization. Parser and document code call `TiXmlDocument::SetError`, which indexes this array through the `TiXmlBase` error enum.

## State and Persistence Behavior

The table is process-static read-only text. It does not persist state between parses beyond being globally available.

## Dependencies and Integration Points

It includes `tinyxml.h` for enum definitions. The split file is intended to make future localization easier and keep messages out of parser implementation files.

## Risks

- Messages are English-only.
- The array must stay in exact enum order; adding/removing error IDs without updating this file will misreport errors or fail compilation.
- Some messages are generic, so higher-level callers may need filename/context from other state.

## Test Signals

Tests should trigger each parse error ID and verify `ErrorDesc()` returns the expected non-null text. Compile-time checks should catch mismatch with `TIXML_ERROR_STRING_COUNT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXml/tinyxml/tinyxmlerror.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXml/tinyxml/tinyxmlparser.cpp -->
# sources/distributed-fs/xrootd/src/XrdXml/tinyxml/tinyxmlparser.cpp

## Purpose

This file implements TinyXML's tokenizer and parser: entity decoding, UTF-8 handling, whitespace skipping, document parsing, node identification, element/attribute/text/comment/declaration parsing, and optional STL stream ingestion.

## Important APIs, Types, and Functions

- Static parser data: `TiXmlBase::entity`, UTF-8 BOM constants, and `TiXmlBase::utf8ByteTable`.
- Encoding helpers: `ConvertUTF32ToUTF8`, `IsAlpha`, `IsAlphaNum`, `SkipWhiteSpace`, `ReadName`, `GetEntity`, `StringEqual`, `ReadText`.
- `TiXmlParsingData::Stamp`: maintains source row/column location.
- Parse methods: `TiXmlDocument::Parse`, `TiXmlElement::Parse`, `TiXmlElement::ReadValue`, `TiXmlUnknown::Parse`, `TiXmlComment::Parse`, `TiXmlAttribute::Parse`, `TiXmlText::Parse`, and `TiXmlDeclaration::Parse`.
- `TiXmlNode::Identify`: selects concrete node type from the next XML prefix.

## Control Flow

Parsing starts at `TiXmlDocument::Parse`, which initializes encoding and location state, skips whitespace, identifies nodes, parses them, links them into the document, and updates encoding after an XML declaration. Elements parse a start tag, attributes, empty-tag endings, nested content through `ReadValue`, and matching end tags. Text parsing reads until `<`, CDATA reads until `]]>`, comments read until `-->`, and attributes parse quoted or lenient unquoted values with entity expansion.

## State and Persistence Behavior

The parser mutates DOM node values, child lists, attributes, document error state, parse locations, and document encoding/BOM state. It does not persist outside memory except through later save/print calls.

## Dependencies and Integration Points

It depends on `tinyxml.h`, C string utilities, and optional STL stream support. In XRootD, it is exercised indirectly by `XrdXmlRdrTiny::LoadFile` and therefore by Metalink conversion.

## Risks

- The parser is intentionally lenient in places, including unquoted attributes, and does not provide full XML validation.
- Non-ASCII name handling is approximate: bytes above ASCII are treated generously as letters.
- Entity parsing accepts only built-ins plus numeric references; unknown entities are passed through imperfectly.
- Recursive DOM parsing can consume significant memory and stack for deeply nested inputs.
- Encoding support is limited to UTF-8 versus legacy heuristics.

## Test Signals

Tests should cover UTF-8 BOM handling, numeric and built-in entities, invalid entities, whitespace condensation toggles, duplicate attributes, unclosed elements, mismatched end tags, CDATA, comments containing entity-like text, declarations with encoding, row/column errors, and deeply nested or malformed XML.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXml/tinyxml/tinyxmlparser.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/CMakeLists.txt -->
# sources/distributed-fs/xrootd/src/XrdXrootd/CMakeLists.txt

## Purpose

This CMake file defines the core XRootD protocol implementation sources compiled into `XrdServer` and builds the loadable `XrdXrootd-${PLUGIN_VERSION}` module.

## Important APIs, Types, and Functions

- `target_sources(XrdServer PRIVATE ...)`: registers protocol implementation files including admin, async I/O, bridge, config, file handling, monitoring, paging, prepare, protocol, redirect, response, stats, transit, and execution code.
- `set(XrdXrootd XrdXrootd-${PLUGIN_VERSION})`: names the protocol plugin module.
- `add_library(${XrdXrootd} MODULE XrdXrootdPlugin.cc)`: builds the loadable plugin.
- `target_link_libraries(${XrdXrootd} PRIVATE XrdServer XrdUtils ${EXTRA_LIBS})`: links the plugin against the server implementation and utilities.

## Control Flow

At configure/generate time, the listed sources become part of `XrdServer`. The plugin module is then built from `XrdXrootdPlugin.cc` and linked to the already-populated `XrdServer` target.

## State and Persistence Behavior

No runtime state exists here. Build state includes plugin naming, source membership, link libraries, and install destination.

## Dependencies and Integration Points

This is the central source registration point for XRootD protocol code. The admin files researched in this subset are compiled here into `XrdServer`, while the final module exposes the protocol plugin to the server runtime.

## Risks

- The large flat source list is easy to desynchronize when files are renamed or conditionally unavailable.
- The plugin link relies on `EXTRA_LIBS` supplied elsewhere, so missing platform dependencies can surface late.
- Admin and protocol internals are built into the same server target, which increases recompilation and integration coupling.

## Test Signals

Build tests should ensure all listed sources exist, the `XrdServer` target compiles, the plugin module links and installs to `${CMAKE_INSTALL_LIBDIR}`, and runtime plugin loading succeeds for `XrdXrootd-${PLUGIN_VERSION}`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdAdmin.cc -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdAdmin.cc

## Purpose

This file implements the XRootD admin control channel. It accepts admin socket connections, performs a text login handshake, processes admin commands, lists client/job state, cancels jobs, and sends asynchronous messages to matching client links.

## Important APIs, Types, and Functions

- External thread entry points `XrdXrootdInitAdmin` and `XrdXrootdLoginAdmin`.
- Static setup: `XrdXrootdAdmin::Init` starts the accept loop, and `addJob` registers cancel/list capable job types.
- Connection handling: `Start` accepts sockets forever, `Login` attaches a socket to `XrdOucStream`, validates `<reqid> login <name>`, and enters `Xeq`.
- Command handlers: `do_Cj`, `do_Lsc`, `do_Lsd`, `do_Lsj`, `do_Lsj_Xeq`, and `do_Msg`.
- Helpers: `getMsg`, `getreqID`, `getTarget`, `sendErr`, `sendOK`, and `sendResp` overloads.

## Control Flow

`Init` stores the shared error logger and starts an admin accept thread. `Start` loops on `AdminSock->Accept()` and starts a per-connection login thread. `Login` attaches the accepted descriptor to `Stream`, requires an initial login command, records `TraceID`, logs success, and invokes `Xeq`. `Xeq` reads request lines formatted as `<msgid> <cmd> <args>`, dispatches known commands, and exits on stream EOF or handler failure.

`do_Cj` and `do_Lsj` select a registered `XrdXrootdJob` by name or `*`, then cancel or list jobs. `do_Lsc` lists matching client names via `XrdLink::getName`. `do_Lsd` finds matching `XrdLink` objects, dynamic-casts their protocol to `XrdXrootdProtocol`, and emits XML-like connection, monitoring, auth, and I/O stats. `do_Msg` targets links and sends a `kXR_asyncms` response with or without payload.

## State and Persistence Behavior

Process-global state includes static `eDest` and `JobList`. Each admin connection owns an `XrdOucStream`, `XrdLinkMatch` target matcher, reusable `usResp` response header, `TraceID`, and `reqID`. State is in memory only; admin commands observe live server links and jobs rather than persisted data.

## Dependencies and Integration Points

The file depends on `XrdNetSocket`, `XrdSysThread`, `XrdOucStream`, `XrdLink`, `XrdLinkMatch`, `XrdXrootdJob`, `XrdXrootdProtocol`, XRootD protocol constants from `XProtocol`, and tracing through `XrdXrootdTrace`. It is initialized from XRootD configuration code when an admin socket is configured.

## Risks

- `Start` passes `&InSock` to a newly spawned thread; the stack variable can change before `XrdXrootdLoginAdmin` dereferences it, causing wrong or duplicate descriptors under rapid accepts.
- `JobList` is a global linked list with no locking; concurrent `addJob`, cancel, and list operations can race if registration is not strictly startup-only.
- XML-like responses interpolate client/admin-controlled strings without escaping, so names, hosts, roles, or messages containing markup can break response syntax.
- The accept loop is infinite with no shutdown path in this file.
- `do_Lsd` reference management depends on `XrdLink::Find` semantics; it calls `setRef(-1)` only on one error branch.
- Authentication/authorization of admin socket users is not visible here and must be enforced by socket exposure or upstream config.

## Test Signals

Integration tests should exercise login success/failure, each command (`cj`, `lsc`, `lsd`, `lsj`, `msg`), wildcard job handling, invalid job types, malformed request IDs, target parsing, client data containing XML special characters, rapid concurrent admin connects to expose the socket-FD race, and admin disconnect logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdAdmin.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdAdmin.hh -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdAdmin.hh

## Purpose

This header declares the `XrdXrootdAdmin` class that owns admin connection handling, command dispatch, job registry integration, target matching, and async response sending for the XRootD protocol server.

## Important APIs, Types, and Functions

- Public static `addJob` and `Init` are the setup API used by other protocol/configuration code.
- Public `Login` and `Start` are thread entry helpers used by the external C-style thread wrappers in the `.cc` file.
- Private command handlers cover job cancel/list, connection list/detail, and message dispatch.
- `JobTable` links admin-visible job names to `XrdXrootdJob *`.
- `usr` encodes the unsolicited response header with `kXR_attn`, action code, and payload length.

## Control Flow

`Init` starts `Start`, which accepts admin sockets and creates per-connection objects. Each connection runs `Login`, then the private command dispatch loop. The header keeps command details private so external users only register jobs and bootstrap the listener.

## State and Persistence Behavior

Static `JobList` and `eDest` are process-global. Per-connection objects hold `Stream`, `Target`, `usResp`, `TraceID`, and `reqID`. The nested `usr` constructor initializes attention framing in network byte order; action and length are filled before sends.

## Dependencies and Integration Points

The header includes `XrdLinkMatch`, `XrdOucStream`, and `XProtocol` protocol types. It forward-declares `XrdNetSocket` and `XrdXrootdJob`. `XrdXrootdProtocol.hh` declares this class as a friend, allowing admin detail reporting to inspect protocol internals.

## Risks

- Global mutable `JobList` lacks ownership and synchronization declarations.
- The public constructor/destructor are trivial, so lifecycle management of attached streams and sockets depends on method behavior.
- Fixed-size `TraceID[24]` and `reqID[16]` truncate/limit admin identities and request IDs; `.cc` rejects long request IDs but truncates login names via `strlcpy`.
- Friend access to protocol internals couples admin reporting tightly to protocol implementation layout.

## Test Signals

Compile/link tests should ensure friend access and forward declarations remain valid. Runtime tests should verify job registration before init, request ID bounds, login-name truncation behavior, response header byte order, and per-connection object cleanup after disconnect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdAdmin.hh -->
