# Research: subset-b-007911

This grouped report covers the exact subset B work item files and is structured for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/webish.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/webish.py

## Purpose
This module owns Tahoe-LAFS web server glue around Twisted Web. It customizes request parsing for uploads, applies site-wide HTTP security headers, privacy-preserving access logging, temporary-file handling for large request bodies, and service setup for both client and introducer web APIs.

## Important APIs, Types, and Functions
`FileUploadFieldStorage` subclasses `cgi.FieldStorage` to force Tahoe upload field bodies to remain bytes even when no MIME filename is supplied. `TahoeLAFSRequest` subclasses Twisted `Request`, overrides `requestReceived`, populates `fields` for POST form bodies, and applies `_tahoeLAFSSecurityPolicy`. `_get_client_ip`, `_logFormatter`, and `censor` provide request logging with capability/query redaction. `anonymous_tempfile_factory` returns a temp-file creator bound to a directory. `TahoeLAFSSite` subclasses `Site`, uses `TahoeLAFSRequest`, and chooses `BytesIO` or a real temporary file by content length. `WebishServer` wires `root.Root`, `OphandleTable`, static resources, storage plugin resources, Twisted strports, node URL persistence, and startup URL discovery. `IntroducerWebishServer` reuses the same server builder with `introweb.IntroducerRoot`.

## Control Flow
When a request completes, `TahoeLAFSRequest.requestReceived` rewinds the body, parses query args, detects POST form content types, builds lowercase CGI headers, synthesizes content length if Twisted did not provide it, and stores parsed `FieldStorage` in `self.fields`. It then sets security headers and calls Twisted's normal `process`. `WebishServer.__init__` builds a root resource tree, then starts child services. `startService` starts Twisted services, discovers the listening port/scheme through endpoint internals or old `TCPServer`/`SSLServer` objects, fills `_url`, and fires `_started`; optional node URL file writing is chained from that deferred.

## State and Persistence
Request state lives on each request object: `args`, `fields`, `path`, `processing_started_timestamp`, and response headers. Server state includes `root`, `site`, `_operations`, `_scheme`, `_portnum`, `_url`, `_listener`, and `_started`. Persistent side effects are limited to optional atomic writing of `nodeurl_path` and temporary request-body files created by the supplied factory.

## Dependencies and Integration Points
The module integrates Twisted application/service/web APIs, Tahoe `allmydata.web.root`, introducer web resources, operation handle tracking, storage plugin resources, `allmydata.util.fileutil.write_atomically`, and `strports.service`. It depends on Python `cgi.FieldStorage`, `urllib.parse`, and temp-file APIs. Static file serving is delegated to `twisted.web.static.File`.

## Risks and Test Signals
The POST parsing path depends on deprecated `cgi` behavior and a filename heuristic workaround; upload tests should verify bytes behavior for `file` fields with separate `name` fields. `censor` assumes ASCII query bytes before UTF-8 value decoding, so malformed query bytes need coverage. Twisted endpoint introspection uses private `_waitingForPort`, creating compatibility risk across Twisted versions. Privacy tests should assert `/uri/`, `/file/`, `/named/`, `uri`, and `private-key` are redacted in logs. Startup tests should cover bare numeric ports, SSL endpoints, and `nodeurl_path` atomic output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/webish.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/windows/__init__.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/windows/__init__.py

## Purpose
This package initializer is intentionally empty. It marks `allmydata.windows` as a Python package so Windows-specific helper modules such as `fixups` and `registry` can be imported through a stable package path.

## Important APIs, Types, and Functions
There are no exported functions, classes, or constants in this file.

## Control Flow
Importing the package has no runtime behavior beyond normal Python package initialization.

## State and Persistence
No state is created and no persistence occurs.

## Dependencies and Integration Points
The file integrates only with Python's import system by defining the package boundary.

## Risks and Test Signals
The practical test signal is importability of `allmydata.windows` and platform-gated imports of its child modules. Because it is empty, behavioral risk is negligible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/windows/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/windows/fixups.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/windows/fixups.py

## Purpose
This Windows-only helper performs one process-level startup fix: suppressing critical-error and open-file error dialogs so Tahoe-LAFS command-line or service usage does not block on GUI prompts when Windows encounters removable media or file-association problems.

## Important APIs, Types, and Functions
`initialize()` is the sole public function. It checks platform and an internal `_done` flag, then calls `win32api.SetErrorMode` with `SEM_FAILCRITICALERRORS | SEM_NOOPENFILEERRORBOX`. The module-level `assert sys.platform == "win32"` exists to help mypy and to make accidental non-Windows import fail early.

## Control Flow
On Windows, import loads `win32api` and `win32con`. `initialize()` is idempotent: if the platform is not `win32` or `_done` is already true, it returns `True`; otherwise it sets `_done` before applying the error mode. Setting `_done` before the Win32 call prevents repeated attempts if callers retry after partial initialization.

## State and Persistence
The `_done` module global tracks whether initialization has run in the current process. `SetErrorMode` mutates process-wide Windows error handling state; it is not file-backed and does not survive process exit.

## Dependencies and Integration Points
Depends on pywin32's `win32api` and `win32con`. Callers must import it only on Windows or tolerate import failure. It is a startup/runtime integration helper rather than business logic.

## Risks and Test Signals
The process-global setting can affect all loaded libraries in the process. Tests should verify idempotence, non-Windows avoidance by callers, and that `SetErrorMode` receives exactly the combined flag value. Because import itself asserts Windows, cross-platform tests should mock or gate imports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/windows/fixups.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/windows/registry.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/windows/registry.py

## Purpose
This module provides Windows registry helpers for Tahoe-LAFS settings under `Software\Allmydata`, especially the configured base directory path.

## Important APIs, Types, and Functions
`get_registry_setting(key, name, _topkey=None)` searches an optional top key, then `HKEY_CURRENT_USER`, then `HKEY_LOCAL_MACHINE`, returning a matching `REG_SZ` value or raising `KeyError`. `set_registry_setting(key, name, data, reg_type=REG_SZ, _topkey=HKEY_LOCAL_MACHINE, create_key_if_missing=True)` opens or creates a key, deletes any existing value, and writes the new value. `get_registry_value(keyname)` scopes lookup to `_AMD_KEY`. `get_base_dir_path()` returns `_BDIR_KEY` or `None`.

## Control Flow
Import is platform-gated: non-Windows defines a local `WindowsError` placeholder and raises `ImportError`. Reads iterate candidate root keys, enumerate all values in the target key, and only return exact name matches with string type. Writes open with `KEY_SET_VALUE`, optionally create missing keys, ignore delete failures, and set the requested value.

## State and Persistence
All meaningful state is persisted in the Windows registry. The module has no in-memory cache. `_AMD_KEY` and `_BDIR_KEY` are constants defining the Tahoe registry namespace and base-dir value name.

## Dependencies and Integration Points
Uses Python `winreg` and Windows registry hives. It is likely consumed by Windows startup/config discovery code and installer/runtime integration. Callers must handle `ImportError` on non-Windows and `KeyError` for missing values when using the low-level helpers.

## Risks and Test Signals
Bare `except:` around `DeleteValue` can hide permission or handle errors. Registry handles are not explicitly closed. Search order means user-level settings override machine-level settings. Tests should mock `winreg` to cover top-key precedence, missing key fallback, type filtering to `REG_SZ`, create/no-create write behavior, and `get_base_dir_path()` returning `None` when absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/windows/registry.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/static/tahoe.py -->
# sources/distributed-fs/tahoe-lafs/static/tahoe.py

## Purpose
This script is an executable PyInstaller/static-entry helper for Tahoe-LAFS. It primes dependency discovery and then runs Tahoe's normal script runner.

## Important APIs, Types, and Functions
There are no local functions. The script imports `allmydata`, `Decimal`, `xml.dom.minidom`, `allmydata.web`, and `allmydata.scripts.runner`, then calls `runner.run()`.

## Control Flow
Importing `allmydata` first suppresses deprecation warnings according to the comment. Several otherwise-unused imports are deliberately referenced as bare expressions so pyflakes considers them used and PyInstaller sees them. Finally, control transfers to Tahoe's CLI runner.

## State and Persistence
No local state is persisted. Runtime effects are whatever `runner.run()` performs for the invoked Tahoe command.

## Dependencies and Integration Points
Integrates with PyInstaller packaging, Tahoe's package import side effects, web package dependencies, standard `decimal` and `xml.dom.minidom`, and `allmydata.scripts.runner`.

## Risks and Test Signals
Because this is an entry script, failures are import-time failures. Packaging tests should verify PyInstaller includes the hinted modules and that executing the bundled script reaches `runner.run()`. Unit tests can monkeypatch `runner.run` if this file is imported directly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/static/tahoe.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/towncrier.toml -->
# sources/distributed-fs/tahoe-lafs/towncrier.toml

## Purpose
This configuration defines Tahoe-LAFS release-note generation with Towncrier.

## Important APIs, Types, and Functions
It configures `package_dir = "src"`, `package = "allmydata"`, output `filename = "NEWS.rst"`, fragment `directory = "newsfragments"`, `start_string`, release `title_format`, Trac ticket `issue_format`, and underline styles. It defines fragment categories: `security`, `incompat`, `feature`, `bugfix`, `installation`, `configuration`, `documentation`, `removed`, `other`, and hidden-content `minor`.

## Control Flow
Towncrier reads this TOML file during `towncrier.check`, draft generation, or release rendering. Fragment files in category directories are grouped by the listed type order and inserted into `NEWS.rst` at the configured start marker.

## State and Persistence
The source state is the `newsfragments` directory and package metadata under `src/allmydata`. Generated release state is persisted in `NEWS.rst` when Towncrier is run in release mode.

## Dependencies and Integration Points
Integrated by `tox.ini` environments `codechecks`, `draftnews`, and `news`. The `issue_format` points to Tahoe-LAFS Trac tickets, so fragment names are expected to map to ticket ids and type suffixes.

## Risks and Test Signals
Changing directory names breaks contributor fragment validation. `minor` uses `showcontent = false`, so fragments in that type intentionally affect categorization without rendering body text. Test signals are successful `python -m towncrier.check --config towncrier.toml`, draft generation, and release generation against representative fragments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/towncrier.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/tox.ini -->
# sources/distributed-fs/tahoe-lafs/tox.ini

## Purpose
This file defines Tahoe-LAFS test, type-check, lint, docs, release-note, integration, and packaging tox environments and maps GitHub Actions Python versions to tox jobs.

## Important APIs, Types, and Functions
`[gh-actions]` maps Python 3.9-3.12 and PyPy 3.9 to coverage or PyPy jobs. `[pytest] twisted = 1` enables Twisted pytest integration. `[tox]` sets envlist and `minversion = 4`. The default `[testenv]` installs Tahoe with `testenv` and `test` extras, runs `pip freeze`, `tahoe --version`, stdout encoding inspection, and Twisted Trial with optional coverage. Named environments include `integration`, `codechecks`, `typechecks`, `draftnews`, `news`, `deprecations`, `upcoming-deprecations`, `docs`, `pyinstaller`, and `tarballs`.

## Control Flow
Tox creates isolated environments, installs deps/extras, sets pass-through environment variables, then executes commands. Coverage jobs switch Trial invocation to `coverage run`, combine data, and emit XML. `codechecks` runs ruff, Tahoe coding tools, and Towncrier fragment checks. `typechecks` runs mypy for Python 3.9 and 3.12. Release-note environments drive Towncrier and `news` commits NEWS changes.

## State and Persistence
Tox manages virtualenvs under its work directory. Coverage commands produce coverage files/XML. `news` mutates `NEWS.rst` and creates a git commit when run. `tarballs` builds source and wheel artifacts. Integration tests may create temporary runtime data.

## Dependencies and Integration Points
Integrates with Twisted Trial, coverage, ruff, mypy, Sphinx, Towncrier, PyInstaller, Chutney for Tor integration, Tahoe CLI, setup.py packaging, and GitHub Actions via `tox-gh-actions`.

## Risks and Test Signals
`news` runs `git commit`, which is intentionally side-effectful. `integration` depends on a pinned Git URL and platform selectors. Type checks pin Twisted and mypy versions, so dependency drift can alter results. Test signals are passing tox envs, especially `codechecks`, `typechecks`, `py*-coverage`, and `integration`; packaging confidence comes from `pyinstaller` and `tarballs`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/tox.ini -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/ws_client.py -->
# sources/distributed-fs/tahoe-lafs/ws_client.py

## Purpose
This script is a Twisted/Autobahn WebSocket client for streaming Tahoe-LAFS private log messages from a local testgrid node.

## Important APIs, Types, and Functions
`TahoeLogProtocol` subclasses `WebSocketClientProtocol` and implements `onOpen`, `onMessage`, and `onClose`. `main(reactor)` reads Tahoe config, extracts `api_auth_token` and `node.web.port`, builds a `WebSocketClientFactory` for `/private/logs/v1`, and connects through `HostnameEndpoint`. The script runs with `twisted.internet.task.react`.

## Control Flow
`main` starts Twisted logging, assumes `tahoe_dir = "testgrid/alice"`, reads private and public node config, normalizes `tcp:` ports, creates deferreds `factory.on_open` and `factory.on_close`, connects to localhost, waits for open, then waits for close. `onOpen` callbacks `on_open`; `onMessage` prints raw payload bytes and flushes stdout; `onClose` errbacks open if the connection closed before opening, then callbacks `on_close`.

## State and Persistence
The script reads existing Tahoe node config and private API token. It persists nothing, but emits log payloads to stdout and Twisted connection diagnostics to stdout.

## Dependencies and Integration Points
Depends on Twisted endpoints/deferreds/reactor, Autobahn WebSocket client classes, and `allmydata.client.read_config`. It integrates with Tahoe's private logs WebSocket endpoint and token-based authorization header format `tahoe-lafs <token>`.

## Risks and Test Signals
The hard-coded `testgrid/alice` path makes this a developer utility rather than generic CLI. `onClose` always callbacks `on_close`; repeated close/error edge cases depend on Deferred state. The disabled JSON pretty-print branch suggests expected Eliot JSON payloads but current behavior prints bytes. Tests should cover port parsing, Authorization header construction, failed connect handling, and protocol deferred sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/ws_client.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/python/src/AsyncResponseHandler.hh -->
# sources/distributed-fs/xrootd/python/src/AsyncResponseHandler.hh

## Purpose
This header implements the generic bridge from asynchronous XrdCl responses to Python callbacks in the XRootD Python extension.

## Important APIs, Types, and Functions
`template<class Type> AsyncResponseHandler` subclasses `XrdCl::ResponseHandler`. It implements `HandleResponseWithHosts`, `HandleResponse`, `ParseResponse`, and `Exit`. `GetHandler<T>(PyObject *callback)` validates and increfs a Python callback through `IsCallable` and returns a new handler instance.

## Control Flow
On callback from XrdCl, the handler first avoids interpreter-finalization deadlock by returning if `Py_IsInitialized()` is false. It acquires the GIL, initializes Python types, converts `XRootDStatus`, converts the typed response from `AnyObject`, optionally converts host lists, constructs callback arguments, determines whether the response is final by checking `suContinue`, invokes the Python callback, releases references, releases the GIL, deletes XrdCl-owned response/status/host objects, and self-deletes on final response. Error paths call `Exit`, which prints Python errors, releases the GIL, and deletes `this`.

## State and Persistence
State is the retained Python callback pointer and GIL state. The handler owns its lifetime after submission to XrdCl and deletes itself after a final response or conversion/callback error. There is no persistence.

## Dependencies and Integration Points
Depends on `PyXRootD.hh`, `Conversions.hh`, `Utils.hh`, and XrdCl response types. It is used by file and filesystem async methods for typed response conversion.

## Risks and Test Signals
The no-interpreter path returns without deleting `status`, `response`, or `hostList`, trading shutdown safety for potential leaks. Callback ownership depends on `IsCallable` incref and final-response decref. Self-deletion is fragile if XrdCl ever reuses the handler after an error. Tests should exercise async callbacks for final and `suContinue` chunked responses, host-list responses, callback exceptions, and interpreter shutdown behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/python/src/AsyncResponseHandler.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/python/src/CMakeLists.txt -->
# sources/distributed-fs/xrootd/python/src/CMakeLists.txt

## Purpose
This CMake file builds the `client` Python extension module for PyXRootD.

## Important APIs, Types, and Functions
It calls `Python_add_library(client MODULE WITH_SOABI ...)` with all binding headers and source files, suppresses compile warnings with `target_compile_options(client PRIVATE -w)`, configures Apple RPATH/install-name properties, and links against XRootD client libraries.

## Control Flow
If CMake target `XrdCl` already exists, it links `client` against `XrdCl` and `XrdUtils`. Otherwise it discovers `XrdCl`, `XrdUtils`, and XRootD include directories via `find_library`/`find_path`, failing fast with `message(FATAL_ERROR)` when missing. For installed XRootD builds it adds both public and private include paths.

## State and Persistence
The build produces a Python extension named `client` with the interpreter ABI suffix. It mutates CMake target properties and include/link settings only during configure/generate.

## Dependencies and Integration Points
Depends on CMake's Python support, XRootD client libraries, `XrdUtils`, and private XRootD headers. It integrates with both in-tree XRootD builds and external/pre-installed XRootD builds.

## Risks and Test Signals
`-w` hides all compiler warnings and can mask Python C API reference issues. Private include dependency may break against installed XRootD layouts. Test signals are successful in-tree and external builds on Linux/macOS, import of the generated `client` module, and runtime smoke tests for `File`, `FileSystem`, `URL`, and `CopyProcess`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/python/src/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/python/src/ChunkIterator.hh -->
# sources/distributed-fs/xrootd/python/src/ChunkIterator.hh

## Purpose
This header defines an internal Python iterator type used by `File.readchunks()` to stream file data as fixed-size byte chunks.

## Important APIs, Types, and Functions
`ChunkIterator` stores a `File *`, `chunksize`, `startOffset`, and `currentOffset`. `ChunkIterator_init` parses file, offset, and chunk size. `ChunkIterator_iter` returns self. `ChunkIterator_iternext` calls `File::ReadChunk`, returns a Python bytes object, or raises `StopIteration`. `ChunkIteratorType` defines the Python type object.

## Control Flow
Construction converts Python numeric parameters through utility functions. Each iteration reads from the current offset, stops on zero-byte reads, otherwise advances by `chunksize` and returns the actual bytes read. There is no read-ahead or buffering beyond one XrdCl buffer per iteration.

## State and Persistence
Iterator state is in-memory offset progression. It references the `File` object pointer passed by the creator but does not visibly incref it in this header, so lifetime is coupled to the caller retaining the file object.

## Dependencies and Integration Points
Depends on `PyXRootDFile.hh` and `File::ReadChunk`. It is initialized on demand by `File::ReadChunks`.

## Risks and Test Signals
The file pointer lifetime is a risk if a `File` is destroyed while an iterator remains. `currentOffset` advances by requested chunk size rather than actual read size, which is fine for sequential fixed reads until EOF but should be tested for short reads. Tests should cover default 2 MB chunks, explicit offsets, zero-byte EOF, closed file behavior through the caller, and iterator/file lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/python/src/ChunkIterator.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/python/src/Conversions.hh -->
# sources/distributed-fs/xrootd/python/src/Conversions.hh

## Purpose
This header centralizes conversion of XrdCl C++ response objects into Python dictionaries, lists, tuples, booleans, and bytes for PyXRootD.

## Important APIs, Types, and Functions
`ConvertType<T>` dispatches through `PyDict<T>::Convert`. Specializations cover `XRootDStatus`, `ProtocolInfo`, `StatInfo`, `StatInfoVFS`, `DirectoryList`, `HostList`, `LocationInfo`, `Buffer`, `ChunkInfo`, `VectorReadInfo`, `PropertyList`, `std::deque<PropertyList>`, `std::vector<std::string>`, `std::vector<XAttrStatus>`, and `std::vector<XAttr>`.

## Control Flow
Each converter allocates Python containers, extracts fields from XrdCl objects, and builds Python values. Buffer/chunk converters return bytes. `ChunkInfo` and `VectorReadInfo` converters delete the backing chunk buffers after building Python bytes, making conversion part of memory cleanup. Host-list conversion ensures `URLType` is ready and wraps host URLs as Python URL objects.

## State and Persistence
No persistent state is stored. Some converters have ownership side effects by freeing XrdCl-allocated buffers. All output state is newly allocated Python objects.

## Dependencies and Integration Points
Depends on Python C API, `PyXRootDURL.hh`, `Utils.hh`, XrdCl response headers, property lists, and extended attribute types. It is used throughout file, filesystem, copy, async, and progress-handler code.

## Risks and Test Signals
Reference ownership is subtle: several converters use `Py_BuildValue` with `N` or `O` and then decref temporary objects. Buffer ownership conventions must match XrdCl expectations, especially for async vector reads. `PyDict<XrdCl::AnyObject>` always returns `None`, so methods using that type expose only status. Tests should validate exact Python shapes for every XrdCl operation, memory safety under vector reads/chunk reads, host-list URL conversion, and property-list copy results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/python/src/Conversions.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/python/src/PyXRootD.hh -->
# sources/distributed-fs/xrootd/python/src/PyXRootD.hh

## Purpose
This common header provides Python C API setup and a convenience macro for releasing the GIL around blocking XrdCl calls.

## Important APIs, Types, and Functions
It defines `PY_SSIZE_T_CLEAN`, includes `Python.h`, `string`, and `structmember.h`, and defines `async(func)` as `Py_BEGIN_ALLOW_THREADS; func; Py_END_ALLOW_THREADS`.

## Control Flow
There is no runtime control flow in the header. The `async` macro wraps synchronous C++ calls so Python threads can run while XrdCl performs I/O.

## State and Persistence
No state or persistence.

## Dependencies and Integration Points
Included by almost every PyXRootD binding source/header. It is the shared Python C API prelude for the extension.

## Risks and Test Signals
The macro name `async` conflicts with modern C++/Python terminology but is a preprocessor symbol in C++. Wrapped code must not touch Python objects while the GIL is released. Tests should include concurrent Python-thread smoke tests and builds across supported C++ standards/compilers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/python/src/PyXRootD.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/python/src/PyXRootDAdler32.cc -->
# sources/distributed-fs/xrootd/python/src/PyXRootDAdler32.cc

## Purpose
This source exposes a simplified Python API to write an Adler-32 checksum extended attribute for a local file using XRootD checksum attribute structures.

## Important APIs, Types, and Functions
`setXAttrAdler32_cpp(path, checksum)` parses two strings, validates an 8-character checksum, opens the file read-only, `fstat`s it, populates `XrdOucXAttr<XrdCksXAttr>`, writes the structured attribute through `xCS.Set("", fd)`, best-effort removes legacy `user.checksum.adler32`, and returns `None` or raises Python exceptions.

## Control Flow
The function performs argument validation first, then local filesystem operations. Every failing syscall preserves `errno` across `close` before raising `OSError`. Attribute setup failures raise `RuntimeError`. Platform-specific legacy removal uses `fremovexattr` on Linux/GNU or `openat`/`unlinkat` on Solaris-like systems.

## State and Persistence
It persists checksum metadata in the file's extended attributes and may remove an older xattr name. It opens and closes a file descriptor each call. It uses the file modification time to set checksum metadata timestamps.

## Dependencies and Integration Points
Depends on POSIX file APIs, optional platform xattr APIs, `XrdCksXAttr`, and `XrdOucXAttr`. Registered as a module method in `PyXRootDModule.cc`.

## Risks and Test Signals
Validation only checks checksum length, while `XrdCksXAttr::Set` appears to validate content later. The code assumes local filesystem xattr support and sufficient permissions. Tests should cover success on an xattr-capable filesystem, invalid length, invalid hex value, nonexistent file, permission errors, and legacy xattr cleanup behavior on supported platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/python/src/PyXRootDAdler32.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/python/src/PyXRootDAdler32.hh -->
# sources/distributed-fs/xrootd/python/src/PyXRootDAdler32.hh

## Purpose
This header declares the Python C API entry point for the Adler-32 xattr helper.

## Important APIs, Types, and Functions
It declares `extern "C" PyObject* setXAttrAdler32_cpp(PyObject* self, PyObject* args)` in namespace `PyXRootD`.

## Control Flow
No runtime flow; it enables `PyXRootDModule.cc` to register the function implemented in `PyXRootDAdler32.cc`.

## State and Persistence
No state or persistence.

## Dependencies and Integration Points
Depends on `Python.h`. Included by the module initializer and the implementation file.

## Risks and Test Signals
Risk is limited to signature mismatch between declaration, implementation, and module method table. Build and import tests cover it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/python/src/PyXRootDAdler32.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/python/src/PyXRootDCopyProcess.cc -->
# sources/distributed-fs/xrootd/python/src/PyXRootDCopyProcess.cc

## Purpose
This source implements the Python binding for XrdCl multi-job copy processing.

## Important APIs, Types, and Functions
`CopyProcess::Parallel` stores the requested parallel job count. `CopyProcess::AddJob` parses source/target and many copy options, fills an `XrdCl::PropertyList`, pushes a matching results list entry, updates copy retry environment settings, and adds the job. `Prepare` appends a configuration job with the parallel count and calls `process->Prepare()`. `Run` optionally wraps a Python progress handler, releases the GIL, runs the copy process, and returns `(status, results)`.

## Control Flow
Callers typically create `CopyProcess`, call `add_job` one or more times, call `parallel` if needed, then `prepare` and `run`. Defaults for chunk sizes and timeouts are pulled from `DefaultEnv`. `sourceLimit > 1` enables extended copy properties. `Run` always constructs a `CopyProgressHandler`, even if the Python handler is null.

## State and Persistence
Object state is an owned `XrdCl::CopyProcess`, a deque of `PropertyList` result records, and an integer parallel count. Persistent side effects are remote/local copy operations and global XrdCl environment updates for retry policy.

## Dependencies and Integration Points
Depends on `PyXRootDCopyProcess.hh`, `PyXRootDCopyProgressHandler.hh`, `Conversions.hh`, XrdCl copy constants, copy process, default environment, and property lists. `FileSystem::Copy` uses this binding internally for one-shot copy.

## Risks and Test Signals
`parallel` must be applied via a configuration job at prepare time; ordering comments mention segfault risk if done earlier. `AddJob` mutates global default environment for retry settings, which can affect other copies. Copy option parsing is dense and needs compatibility tests. Test signals include one-shot copy through `FileSystem.copy`, multi-job copy, parallel copy, checksum modes, third-party copy, progress callbacks, cancellation, and result property conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/python/src/PyXRootDCopyProcess.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/python/src/PyXRootDCopyProcess.hh -->
# sources/distributed-fs/xrootd/python/src/PyXRootDCopyProcess.hh

## Purpose
This header defines the Python object type wrapping `XrdCl::CopyProcess`.

## Important APIs, Types, and Functions
`CopyProcess` exposes static methods `Parallel`, `AddJob`, `Prepare`, and `Run`. Its Python object stores `process`, `results`, and `parallel`. `CopyProcess_init` allocates the XrdCl process and result deque. `CopyProcess_dealloc` releases them. `CopyProcessMethods` and `CopyProcessType` define the Python-visible type.

## Control Flow
The initializer sets default parallelism to 1. Method dispatch is through Python C API method tables. Deallocation frees C++ resources when Python GC destroys the object.

## State and Persistence
In-memory state is the owned copy process, accumulated per-job results, and parallel setting. No direct persistence occurs in the header; copy operations are implemented in the source file.

## Dependencies and Integration Points
Depends on Python C API and XrdCl copy/property response headers. Included by module initialization and filesystem/copy implementation files.

## Risks and Test Signals
Because the type object is static in the header, include/ODR usage must remain controlled. Tests should verify construction/destruction does not leak, methods exist on the Python type, and repeated module import initializes the type safely.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/python/src/PyXRootDCopyProcess.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/python/src/PyXRootDCopyProgressHandler.cc -->
# sources/distributed-fs/xrootd/python/src/PyXRootDCopyProgressHandler.cc

## Purpose
This source adapts XrdCl copy progress notifications into Python handler method calls.

## Important APIs, Types, and Functions
`BeginJob` calls Python `handler.begin(jobNum, jobTotal, source_url, target_url)`. `EndJob` converts the result `PropertyList` and calls `handler.end(jobNum, result)`. `JobProgress` calls `handler.update(jobNum, bytesProcessed, bytesTotal)`. `ShouldCancel` calls `handler.should_cancel(jobNum)` and returns true only if the result is `True`.

## Control Flow
Each callback acquires the GIL with `PyGILState_Ensure`, checks whether a handler was supplied, performs the Python method call, decrefs the return value, and releases the GIL. `EndJob` additionally converts and decrefs the result object.

## State and Persistence
The handler stores only a borrowed-looking `PyObject *handler` pointer from construction. It persists nothing. The underlying copy operation side effects are outside this file.

## Dependencies and Integration Points
Depends on `PyXRootDCopyProgressHandler.hh`, `Conversions.hh`, and XrdCl property/response types. Used by `CopyProcess::Run`.

## Risks and Test Signals
The constructor does not incref the Python handler, so lifetime depends on `CopyProcess::Run` keeping the argument alive while XrdCl calls back. Python exceptions from handler methods are not printed or propagated here. Tests should cover each callback method, handler absence, cancellation return values, Python exceptions in callbacks, and reference lifetime under long-running copies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/python/src/PyXRootDCopyProgressHandler.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/python/src/PyXRootDCopyProgressHandler.hh -->
# sources/distributed-fs/xrootd/python/src/PyXRootDCopyProgressHandler.hh

## Purpose
This header declares the C++ progress-handler adapter used by copy operations.

## Important APIs, Types, and Functions
`CopyProgressHandler` subclasses `XrdCl::CopyProgressHandler` and declares overrides for `BeginJob`, `EndJob`, `JobProgress`, and `ShouldCancel`. It stores `PyObject *handler`.

## Control Flow
The header only defines construction and method declarations; implementation lives in the `.cc` file. XrdCl invokes the virtual methods during copy execution.

## State and Persistence
State is the Python handler pointer. No persistence.

## Dependencies and Integration Points
Depends on Python C API, `XrdClCopyProcess`, `XrdClPropertyList`, and `XrdClURL`. Instantiated by `CopyProcess::Run`.

## Risks and Test Signals
No ownership policy is documented in the type itself. Build tests catch virtual signature mismatches; runtime tests should verify Python handler lifetime and callback method names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/python/src/PyXRootDCopyProgressHandler.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/python/src/PyXRootDEnv.hh -->
# sources/distributed-fs/xrootd/python/src/PyXRootDEnv.hh

## Purpose
This header implements module-level Python functions for interacting with the global XrdCl default environment and logging controls.

## Important APIs, Types, and Functions
`EnvPutString_cpp`, `EnvGetString_cpp`, `EnvPutInt_cpp`, `EnvGetInt_cpp`, `EnvGetDefault_cpp`, `XrdVersion_cpp`, `SetLogLevel_cpp`, and `SetLogMask_cpp` are Python C API functions registered by `PyXRootDModule.cc`.

## Control Flow
Each function parses Python arguments, reads or writes `XrdCl::DefaultEnv::GetEnv()`, and returns Python booleans, strings, ints, or `None`. `XrdVersion_cpp` strips a leading `v` from `XrdVERSION` once into a static string. Log functions call `DefaultEnv::SetLogLevel` or `SetLogMask` if parsing succeeds and always return `None`.

## State and Persistence
The functions mutate XrdCl's process-global default environment and logging configuration. Settings are in-memory and can affect all subsequent XrdCl operations in the process.

## Dependencies and Integration Points
Depends on `XrdClDefaultEnv` and `XrdVersion.hh`. Exposed as module-level helpers in the `client` extension.

## Risks and Test Signals
The log setters ignore parse failure by returning `None` instead of propagating an argument error. Environment writes may be rejected if shell-imported settings already exist, indicated by false return. Tests should verify put/get behavior, default lookup for string and integer defaults, version formatting, log setter argument validation, and cross-operation impact of environment changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/python/src/PyXRootDEnv.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/python/src/PyXRootDFile.cc -->
# sources/distributed-fs/xrootd/python/src/PyXRootDFile.cc

## Purpose
This source implements the Python `File` object wrapping `XrdCl::File`, exposing open/close/stat/read/write/sync/truncate/vector-read/control/xattr/template-open/clone operations plus context manager and line/chunk iteration behavior.

## Important APIs, Types, and Functions
The file defines `File_init`, `File_dealloc`, `File_iter`, `File_iternext`, `File_enter`, `File_exit`, `FileType`, and method implementations for `Open`, `Close`, `Stat`, `Read`, `ReadLine`, `ReadLines`, `ReadChunk`, `ReadChunks`, `Write`, `Sync`, `Truncate`, `VectorRead`, `Fcntl`, `Visa`, `IsOpen`, `GetProperty`, `SetProperty`, `SetXAttr`, `GetXAttr`, `DelXAttr`, `ListXAttr`, `OpenUsingTemplate`, and `Clone`.

## Control Flow
Most I/O methods parse Python args, reject closed-file use with `ValueError`, optionally create an async response handler when a callback is supplied, release the GIL around the XrdCl call, convert the resulting status and response, and return either status alone for async submission or `(status, response)` for synchronous calls. `Read` stats the file to determine size when size is zero. `ReadLine` repeatedly calls `ReadChunk` until newline, requested size, or EOF and advances `currentOffset` for default sequential reads. `ReadChunks` constructs `ChunkIterator`. `VectorRead` builds a chunk list with allocated buffers and uses a guard so buffers are freed by conversion or on early failure. `Clone` validates a list of dictionaries referencing source `File` objects and offsets.

## State and Persistence
`File` owns an `XrdCl::File` pointer and a `currentOffset` for line iteration. Remote state changes include open sessions, writes, syncs, truncation, xattr mutation, clone writes, and property settings. In-memory callback handlers own async response completion.

## Dependencies and Integration Points
Depends on `AsyncResponseHandler`, `ChunkIterator`, `Utils`, XrdCl file/filesystem types, and `Conversions`. It is registered in the module initializer and used by user-facing Python APIs around remote XRootD files.

## Risks and Test Signals
Reference returns for `GetProperty`/`SetProperty` use `Py_None`/`Py_True`/`Py_False` without explicit incref, which is risky in Python C API terms. `ReadLines` parses with `|kII` into local C variables while later conversion variables remain null, suggesting offsets/options may not work as intended. `Read` allocates `new char[size]` and for async relies on response conversion to free chunk buffers. `ReadLine` returns Unicode from raw bytes, which can fail or corrupt binary data. Tests should cover sync/async variants for every method, closed-file errors, large reads, line iteration offsets, vector-read cleanup on invalid chunks, xattr list validation, template open, clone dictionary validation, and reference-count leak/crash checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/python/src/PyXRootDFile.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/python/src/PyXRootDFile.hh -->
# sources/distributed-fs/xrootd/python/src/PyXRootDFile.hh

## Purpose
This header declares the Python `File` binding type and its method surface.

## Important APIs, Types, and Functions
`class File` declares all static method implementations and stores `PyObject_HEAD`, `XrdCl::File *file`, and `uint64_t currentOffset`. It declares external `PyTypeObject FileType`.

## Control Flow
No method implementations are in the header; it defines the public C++ interface consumed by `ChunkIterator`, `PyXRootDFile.cc`, and module initialization.

## State and Persistence
The type's state is the owned XrdCl file handle and sequential-read offset. Persistence occurs only through operations implemented in the source file.

## Dependencies and Integration Points
Depends on Python C API, `Utils.hh`, XrdCl file types, and `deque`. It is the cross-file declaration needed by iterators, clone/template APIs, and module registration.

## Risks and Test Signals
The raw pointer ownership model requires correct deallocation and no use-after-free from iterators or clone references. Build tests catch signature drift; runtime tests should exercise object lifecycle and iterator interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/python/src/PyXRootDFile.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/python/src/PyXRootDFileSystem.cc -->
# sources/distributed-fs/xrootd/python/src/PyXRootDFileSystem.cc

## Purpose
This source implements the Python `FileSystem` object wrapping `XrdCl::FileSystem`, exposing namespace, metadata, query, copy, preparation, remote cat, and xattr operations.

## Important APIs, Types, and Functions
Implemented methods include `Copy`, `Locate`, `DeepLocate`, `Mv`, `Query`, `Truncate`, `Rm`, `MkDir`, `RmDir`, `ChMod`, `Ping`, `Stat`, `StatVFS`, `Protocol`, `DirList`, `SendInfo`, `Prepare`, `GetProperty`, `SetProperty`, `Cat`, `SetXAttr`, `GetXAttr`, `DelXAttr`, and `ListXAttr`.

## Control Flow
Most methods follow the same pattern: parse Python args, create an async handler for callbacks or call XrdCl synchronously with the GIL released, convert `XRootDStatus`, convert response objects when present, and return status alone or `(status, response)`. `Copy` constructs a `CopyProcess`, delegates `AddJob`, `Prepare`, and `Run`, and returns `(status, None)` on prepare failure. `Prepare` validates a list of strings before calling XrdCl prepare. `Cat` builds an XrdCl copy process to `stdio://-` and returns only status.

## State and Persistence
The object owns a parsed `URL` and `XrdCl::FileSystem`. Remote persistent side effects include copies, moves, truncates, removals, directory creation/removal, chmod, prepare requests, and xattr mutations. `Cat` writes remote content to stdout via XrdCl.

## Dependencies and Integration Points
Depends on `PyXRootDFileSystem.hh`, `PyXRootDCopyProcess.hh`, `AsyncResponseHandler.hh`, `Utils.hh`, XrdCl filesystem/copy process, and conversion helpers. It is module-registered as `FileSystem`.

## Risks and Test Signals
`GetProperty` and `SetProperty` have the same borrowed singleton return risk as `File`. Several xattr parse format strings are labelled `set_xattr` even in get/delete/list functions, which affects error messages. `Copy` creates temporary tuples/dicts without obvious decrefs on all paths. Tests should cover sync/async methods, argument validation, returned Python shapes for each response type, copy failure paths, xattr list validation, remote cat behavior, and reference-count checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/python/src/PyXRootDFileSystem.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/python/src/PyXRootDFileSystem.hh -->
# sources/distributed-fs/xrootd/python/src/PyXRootDFileSystem.hh

## Purpose
This header defines the Python `FileSystem` binding type and its method table.

## Important APIs, Types, and Functions
`class FileSystem` declares static filesystem methods and stores `URL *url` plus `XrdCl::FileSystem *filesystem`. The header defines `FileSystemMethods`, `FileSystem_init`, `FileSystem_dealloc`, `FileSystemMembers`, and static `FileSystemType`.

## Control Flow
Construction creates a Python `URL` from the provided args and then constructs an XrdCl filesystem from that URL. Deallocation deletes the XrdCl filesystem and decrefs the URL. Python method dispatch is described by the method table.

## State and Persistence
In-memory object state is the server URL and filesystem client instance. Persistence is through implementation methods in the source file.

## Dependencies and Integration Points
Depends on `PyXRootDURL.hh`, `Conversions.hh`, and `XrdClFileSystem`. Included by module initialization and filesystem implementation.

## Risks and Test Signals
If URL construction fails, initialization returns failure before creating the filesystem. Static type definition in a header requires controlled inclusion. Tests should verify constructor argument validation, `url` member exposure, deallocation, and method availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/python/src/PyXRootDFileSystem.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/python/src/PyXRootDFinalize.hh -->
# sources/distributed-fs/xrootd/python/src/PyXRootDFinalize.hh

## Purpose
This header implements a module-level finalization hook for stopping XrdCl background threads from Python `atexit` handlers.

## Important APIs, Types, and Functions
`__XrdCl_Stop_Threads(PyObject *self, PyObject*)` releases the GIL, calls `XrdCl::DefaultEnv::GetPostMaster()->Stop()`, reacquires the GIL, and returns `None`.

## Control Flow
The function is called explicitly from Python shutdown logic. It blocks outside the GIL while XrdCl's postmaster stops job manager, task manager, and poller threads.

## State and Persistence
It mutates process-global XrdCl thread/runtime state. No persistence.

## Dependencies and Integration Points
Depends on Python C API, `XrdClDefaultEnv`, and `XrdClPostMaster`. Registered as `__XrdCl_Stop_Threads` in the extension module.

## Risks and Test Signals
Shutdown ordering is sensitive; async response handlers also guard against interpreter finalization. Tests should verify the hook can be called repeatedly or at least safely during teardown, does not deadlock, and leaves no XrdCl worker threads after interpreter exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/python/src/PyXRootDFinalize.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/python/src/PyXRootDModule.cc -->
# sources/distributed-fs/xrootd/python/src/PyXRootDModule.cc

## Purpose
This source defines the `client` Python extension module for PyXRootD and registers all exposed types and module-level helper functions.

## Important APIs, Types, and Functions
It declares global `ClientModule`, `module_methods`, `moduledef`, and `PyInit_client`. Registered functions include finalization, environment getters/setters, version/log controls, and `setXAttrAdler32_cpp`. Registered types are `FileSystem`, `File`, `URL`, and `CopyProcess`.

## Control Flow
`PyInit_client` readies each type by setting `tp_new`, calling `PyType_Ready`, and increfing the type. It creates the module and adds type objects with `PyModule_AddObject`, then returns the module.

## State and Persistence
Module state size is `-1`, meaning global state rather than per-interpreter module state. It stores the module pointer globally. No persistence beyond process/module lifetime.

## Dependencies and Integration Points
Includes all binding headers, environment/finalization helpers, and Adler-32 helper. It is the entry point compiled by the Python extension target.

## Risks and Test Signals
`PyModule_AddObject` steals references; the prior increfs align with that, but failure paths after partial module creation are not extensively cleaned up. `m_size = -1` is not subinterpreter-friendly. Test signals are successful import, attribute presence, repeated import, type construction, and module finalization behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/python/src/PyXRootDModule.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/python/src/PyXRootDURL.cc -->
# sources/distributed-fs/xrootd/python/src/PyXRootDURL.cc

## Purpose
This source implements property accessors and methods for the Python `URL` object wrapping `XrdCl::URL`.

## Important APIs, Types, and Functions
Methods include `IsValid` and `Clear`. Getters/setters cover `hostid`, `protocol`, `username`, `password`, `hostname`, `port`, `path`, and read-only `path_with_params`.

## Control Flow
Getters pull string or integer fields from the underlying XrdCl URL and return Python values. Setters validate Python type (`str` or `int`), convert to C++ strings or long, update the XrdCl URL, and return 0 or -1 with a Python exception. `Clear` resets the URL object and returns `None`.

## State and Persistence
All state is the mutable in-memory `XrdCl::URL` owned by the Python object. No persistent side effects.

## Dependencies and Integration Points
Depends on `PyXRootDURL.hh` and XrdCl URL semantics. Used directly by Python users and by host-list conversion and filesystem construction.

## Risks and Test Signals
Setters do not check `PyUnicode_AsUTF8` or `PyLong_AsLong` error conditions beyond initial type checks. URLs with invalid port ranges depend on XrdCl handling. Tests should cover construction, stringification, validation, every getter/setter, invalid setter types, clearing, and filesystem use of a URL-derived host.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/python/src/PyXRootDURL.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/python/src/PyXRootDURL.hh -->
# sources/distributed-fs/xrootd/python/src/PyXRootDURL.hh

## Purpose
This header defines the Python `URL` binding type.

## Important APIs, Types, and Functions
`class URL` declares accessors/mutators and stores `XrdCl::URL *url`. `URL_init` parses a URL string and allocates `XrdCl::URL`. `URL_dealloc` deletes it. `URL_str` returns the full URL string. `URLGetSet`, `URLMethods`, and `URLType` expose Python properties/methods.

## Control Flow
Object construction requires one string argument. Python property access dispatches to implementations in `PyXRootDURL.cc`. Deallocation frees the C++ URL.

## State and Persistence
The object contains a mutable parsed URL. No persistence.

## Dependencies and Integration Points
Depends on Python C API and `XrdClURL`. Included by conversions, filesystem, module initialization, and URL implementation.

## Risks and Test Signals
Type object is static in a header and must not be duplicated across independent translation units in problematic ways. Tests should verify constructor failures, `str(url)`, property table behavior, and lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/python/src/PyXRootDURL.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/python/src/Utils.cc -->
# sources/distributed-fs/xrootd/python/src/Utils.cc

## Purpose
This source implements shared PyXRootD utility functions for callback validation, type initialization, and checked integer conversion from Python objects to unsigned C/C++ numeric types.

## Important APIs, Types, and Functions
`IsCallable` checks `PyCallable_Check`, sets `TypeError` on failure, and increfs valid callbacks. `InitTypes` prepares `URLType`. Numeric helpers are `PyIntToUlong`, `PyObjToUlong`, `PyObjToUint`, `PyObjToUshrt`, and `PyObjToUllong`.

## Control Flow
Integer helpers validate type/range, translate Python conversion errors into more specific messages, reject negative values, and write through output pointers. `PyObjToUint` and `PyObjToUshrt` layer range narrowing on top of unsigned long conversion. `PyObjToUllong` currently routes `PyLong_Check` inputs through unsigned-long conversion first.

## State and Persistence
No persistent state. `IsCallable` mutates callback reference counts. `InitTypes` mutates Python type initialization state.

## Dependencies and Integration Points
Depends on `Utils.hh` and `PyXRootDURL.hh`. Used by async handlers, file methods, chunk iterator, and other argument-parsing paths.

## Risks and Test Signals
Some branches are unreachable because Python 3 integers are always `PyLong_Check`; `PyObjToUllong` may unintentionally limit to unsigned long rather than full unsigned long long on platforms where sizes differ. Callback incref must be paired by async final-response decref. Tests should cover negative, non-integer, overflow boundary values for each helper and callback reference counting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/python/src/Utils.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/python/src/Utils.hh -->
# sources/distributed-fs/xrootd/python/src/Utils.hh

## Purpose
This header declares utility helpers shared by the PyXRootD extension.

## Important APIs, Types, and Functions
It declares `IsCallable`, `InitTypes`, and numeric conversion helpers for unsigned long, unsigned int, unsigned short, and unsigned long long values.

## Control Flow
No implementations are present; it provides prototypes for source files that need argument validation and callback handling.

## State and Persistence
No state or persistence in the header.

## Dependencies and Integration Points
Depends on `PyXRootD.hh` and XrdCl response headers. Included by file, async, conversions, and other binding components.

## Risks and Test Signals
Header risk is declaration/implementation drift. Build tests cover signatures; runtime tests cover behavior in `Utils.cc`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/python/src/Utils.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/python/src/__init__.py -->
# sources/distributed-fs/xrootd/python/src/__init__.py

## Purpose
This empty file marks the Python source directory as a package or package-adjacent import root for the binding sources.

## Important APIs, Types, and Functions
It exports no Python APIs.

## Control Flow
Importing it has no runtime behavior.

## State and Persistence
No state and no persistence.

## Dependencies and Integration Points
It integrates only with Python packaging/import machinery. The compiled `client` extension provides the actual behavior in this directory.

## Risks and Test Signals
Behavioral risk is negligible. Packaging tests should verify the package/import layout includes the compiled extension and does not rely on this file for runtime initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/python/src/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/CMakeLists.txt -->
# sources/distributed-fs/xrootd/src/CMakeLists.txt

## Purpose
This top-level source CMake file orchestrates XRootD library targets and subdirectories, including shared utility and server libraries.

## Important APIs, Types, and Functions
It configures PyPI build RPATHs, maps `XRDCL_LIB_ONLY` to `XRDCL_ONLY`, includes `XrdHeaders`, creates shared libraries `XrdUtils` and conditionally `XrdServer`, sets SOVERSION/VERSION properties, links platform/system dependencies, installs libraries, and adds many source subdirectories.

## Control Flow
Configuration first handles install RPATH. It always builds and installs `XrdUtils`, then adds common/client-related subdirectories including `XProtocol`, `XrdCl`, HTTP/S3 client pieces, and erasure coding. If `NOT XRDCL_ONLY`, it also builds `XrdServer` and adds server/plugin subdirectories such as auth, cms, ofs, oss, http, macaroons, voms, ceph, and scitokens.

## State and Persistence
Build state is CMake targets, link interfaces, RPATHs, and installed shared libraries. No runtime persistence.

## Dependencies and Integration Points
Depends on OpenSSL, threads, dl/socket/sendfile/systemd/atomic/extra platform libraries, and many internal XRootD subdirectories. It is the central integration point for client-only versus full server builds.

## Risks and Test Signals
RPATH handling differs for PyPI/macOS/non-macOS builds. `XRDCL_ONLY` gates large server functionality, so build matrix coverage is important. Test signals are successful client-only and full builds, installed library discovery, RPATH correctness for Python/plugin packaging, and link correctness with optional systemd/platform libraries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XProtocol/CMakeLists.txt -->
# sources/distributed-fs/xrootd/src/XProtocol/CMakeLists.txt

## Purpose
This CMake file attaches XRootD protocol source files to the `XrdUtils` library target.

## Important APIs, Types, and Functions
It calls `target_sources(XrdUtils PRIVATE XProtocol.hh XProtocol.cc)`.

## Control Flow
When the `XProtocol` subdirectory is processed, the protocol header and implementation are added to the already-defined `XrdUtils` shared library.

## State and Persistence
It mutates the build graph by adding sources to `XrdUtils`. No runtime persistence.

## Dependencies and Integration Points
Depends on the parent CMake file having created `XrdUtils`. It integrates protocol helper functions into the shared utility library used by broader XRootD components.

## Risks and Test Signals
If `XrdUtils` is renamed or not defined before this subdirectory is added, configuration fails. Build tests for `XrdUtils` cover this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XProtocol/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XProtocol/XProtocol.cc -->
# sources/distributed-fs/xrootd/src/XProtocol/XProtocol.cc

## Purpose
This source implements helper routines for XRootD protocol names and file-attribute vector encoding/decoding.

## Important APIs, Types, and Functions
Static tables map XRootD error codes to messages (`errNames`) and request codes to names (`reqNames`). `XProtocol::errName` and `XProtocol::reqName` normalize possible network-byte-order values and return stable strings. `ClientFattrRequest::NVecInsert`, `VVecInsert`, `NVecRead`, and `VVecRead` write/read name-vector and value-vector records for file attribute protocol payloads.

## Control Flow
Error/request name lookups first byte-swap values on little-endian hosts when values are outside the expected host-order range, validate bounds against protocol fences, and return fallback strings for unknown values. Vector insert functions append encoded fields into caller-provided buffers. Vector read functions extract status/name/value fields from buffers, allocating copied strings for names/values where needed.

## State and Persistence
The file has immutable lookup tables and a static endianness probe. It does not persist data; it serializes/deserializes protocol payload fragments in memory. `NVecRead` uses `strdup` and `VVecRead` uses `malloc`, transferring allocation cleanup responsibility to callers.

## Dependencies and Integration Points
Depends on `XProtocol/XProtocol.hh`, C/POSIX headers, byte-order functions, and protocol constants such as `kXR_ArgInvalid`, `kXR_ERRFENCE`, `kXR_auth`, and `kXR_REQFENCE`. Built into `XrdUtils`.

## Risks and Test Signals
Comments say "byte orderdoesn't" and code uses `htons`/`htonl` while reading where `ntohs`/`ntohl` would be clearer; round-trip tests are important. Insert functions assume caller buffers are sufficiently large. Read functions allocate memory that callers must free. Tests should cover host-order and network-order code lookups, unknown/fence values, nvec/vvec round trips, empty strings, long values, and allocation cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XProtocol/XProtocol.cc -->
