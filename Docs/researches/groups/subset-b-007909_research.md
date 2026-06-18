# subset-b-007909 research

Grouped research for Tahoe-LAFS capability and utility modules under `src/allmydata`. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/uri.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/uri.py

## Purpose

This module defines Tahoe-LAFS capability URI objects and parsers. It covers immutable CHK caps, literal caps, mutable SSK and MDMF read/write/verifier caps, directory wrappers around those file caps, unknown-cap handling, Twisted adapter registration, and URI-extension packing. The classes still use historical `to_string()` naming even though the values are bytes.

## APIs and control flow

Important types are `CHKFileURI`, `CHKFileVerifierURI`, `LiteralFileURI`, `WriteableSSKFileURI`, `ReadonlySSKFileURI`, `SSKVerifierURI`, `WriteableMDMFFileURI`, `ReadonlyMDMFFileURI`, `MDMFVerifierURI`, directory URI variants, directory verifier variants, and `UnknownURI`. Each concrete cap has a `BASE_STRING`, regex parser, `init_from_string()`, `to_string()`, readonly/mutable predicates, and methods for deriving readonly or verifier caps. `wrap_dirnode_cap()` maps a file cap to the corresponding directory cap.

`from_string()` is the dispatcher. It accepts unicode or bytes, strips `ro.` and `imm.` alleged-constraint prefixes, enforces readonly or deep-immutable context rules, and returns either a concrete cap or `UnknownURI` with an attached `MustBeReadonlyError`, `MustBeDeepImmutableError`, or `BadURIError`. The `from_string_*` helpers assert interface conformance and are registered as adapters for bytes.

## State, dependencies, risks, and tests

State is object-local key material, storage indexes, fingerprints, share counts, and sizes. Persistent compatibility is the serialized cap bytes; changing regexes, field order, hash derivations, or prefixes can invalidate existing files. Dependencies include `base32`, `hashutil`, storage index conversion helpers, `allmydata.interfaces`, Twisted adapters, and zope interfaces.

Risks include accepting malformed prefixes as unknown instead of failing loudly, regexes that intentionally allow some trailing MDMF separators, assertion-based validation in adapter helpers, and the security sensitivity of readonly/deep-immutable constraints. URI-extension packing sorts keys, netstring-encodes values, coerces selected values back to ints, and hashes readable output; callers depend on deterministic bytes. Test signals should cover round-trips for every cap class, readonly and immutable constraint failures, unknown/future cap prefixes, adapter registration, literal-cap edge cases, verifier derivation, and `pack_extension`/`unpack_extension` compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/uri.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/__init__.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/util/__init__.py

## Purpose

This package initializer is intentionally empty. Its role is structural: it marks `allmydata.util` as an importable Python package containing Tahoe-LAFS compatibility helpers, filesystem utilities, async helpers, encoding shims, transport providers, statistics, logging adapters, and cryptographic hash wrappers.

## APIs and control flow

The file exports no symbols, performs no imports, and has no runtime control flow. Importers reach utility modules directly, for example `allmydata.util.hashutil`, `allmydata.util.fileutil`, or `from allmydata.util import base32`. Because the initializer does not import submodules, importing `allmydata.util` has no side effects such as starting thread pools, touching platform APIs, installing logging observers, or importing optional Tor/I2P dependencies.

## State, dependencies, risks, and tests

There is no local state or persistence. The absence of eager imports is an integration choice: many sibling modules carry expensive or platform-sensitive side effects, including CPU thread-pool startup in `cputhreadpool.py`, Windows ctypes setup in `fileutil.py`, and optional dependency imports in provider modules.

The main risk is accidental future convenience imports in this file. Adding them could create import cycles, slow startup, or make optional dependencies mandatory. Test signals are mostly indirect: package import should succeed in minimal environments, direct submodule imports should continue to work, and packaging metadata should include this file so `allmydata.util` remains importable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/abbreviate.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/util/abbreviate.py

## Purpose

This module formats durations and byte counts for user-facing status messages and parses compact size strings back into integer byte counts. It is presentation-oriented but participates in configuration and status surfaces where readability matters.

## APIs and control flow

`abbreviate_time()` accepts seconds or `datetime.timedelta`. `None` becomes `"unknown"`, timedeltas get `" ago"` or `" in the future"` suffixes, and thresholds choose seconds, minutes, hours, days, months, or years. `abbreviate_space()` formats bytes using either SI powers of 1000 or IEC powers of 1024 while preserving the historical `kB`/`kiB` style. `abbreviate_space_both()` returns both variants. `parse_abbreviated_size()` accepts integer strings with optional `K/M/G/T/P/E`, optional `I`, and optional `B`, returning `None` for empty input.

## State, dependencies, risks, and tests

There is no persistent state. Dependencies are only `re` and `datetime.timedelta`. The implementation floors quantities with `int()` and treats months as 30 days and years as 365 days, so the output is approximate. `parse_abbreviated_size()` intentionally rejects decimals and silently uppercases suffixes.

Risks are boundary regressions around thresholds such as 119/120 seconds, SI versus IEC suffix confusion, and callers assuming calendar-accurate months. Test signals should cover `None`, timedeltas of both signs, threshold changes, all size suffixes, lowercase parsing, invalid strings, and large values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/abbreviate.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/assertutil.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/util/assertutil.py

## Purpose

This is a compatibility shim that re-exports assertion helpers from `pyutil.assertutil`. Older Tahoe-LAFS code imports `_assert`, `precondition`, and `postcondition` from this local module, so this file keeps those import paths stable.

## APIs and control flow

The public API is exactly `_assert`, `precondition`, and `postcondition`, listed in `__all__`. There is no custom control flow, validation, state, or persistence here. All behavior belongs to the upstream `pyutil.assertutil` implementations.

## State, dependencies, risks, and tests

The only dependency is `pyutil.assertutil`. The risk is compatibility drift: if the pyutil helpers change message formatting, exception behavior, or availability, Tahoe modules that rely on rich assertion diagnostics will observe that behavior through this shim. Removing this file would break many local imports.

Test signals are import-level and behavioral: callers should be able to import the three names, failed preconditions should include useful diagnostic kwargs, and modules such as `uri.py`, `base32.py`, `encodingutil.py`, and `fileutil.py` should continue to use the same assertions without local changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/assertutil.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/attrs_provides.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/util/attrs_provides.py

## Purpose

This module restores the `attrs` validator pattern for requiring that an attribute value provide a zope interface. It exists because native attrs support for zope interfaces was deprecated while Tahoe-LAFS still uses zope interfaces heavily.

## APIs and control flow

`provides(interface)` returns a `_ProvidesValidator` instance. The validator checks `interface.providedBy(value)` during attrs initialization and raises `TypeError` with the attribute, expected interface, and offending value if the contract is not met. `_ProvidesValidator` is itself an attrs class with slots, hash support, and a concise repr for diagnostics.

## State, dependencies, risks, and tests

State is just the interface object captured by the validator. Dependencies are `attr._make.attrs` and `attrib`, plus zope-interface semantics supplied by the passed interface. Integration appears in modules such as `eliotutil.py`, where optional Eliot logger attributes are validated.

Risks include relying on private attrs internals (`attr._make`) and only checking runtime interface provision, not structural type hints. Test signals should verify success for implementing objects, `TypeError` content for non-providers, repr readability, and compatibility with attrs validators such as `optional(provides(...))`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/attrs_provides.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/base32.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/util/base32.py

## Purpose

This module implements Tahoe-LAFS base32 encoding and validation using the lowercase RFC3548 alphabet. It supplies regex fragments and trailing-character checks used by capability parsers, storage index displays, and other binary-to-text identifiers.

## APIs and control flow

`b2a()` base32-encodes bytes, strips padding, and lowercases. `a2b()` validates with `could_be_base32_encoded()`, restores padding, uppercases, and decodes via Python `base64`. `b2a_or_none()` preserves `None`. The trailing-character helpers build regex fragments such as `BASE32CHAR_3bits`, `BASE32CHAR_1bits`, and `BASE32STR_anybytes` so callers can validate exact byte lengths without accepting impossible low bits.

## State, dependencies, risks, and tests

Module state consists of translation tables, constants mapping encoded lengths to original byte lengths, and `s8`, a precomputed table for cheap final-character validity. Dependencies are `base64`, typing, and `precondition`.

This is compatibility-sensitive because URI regexes in `uri.py` depend on the exact alphabet and trailing-bit restrictions. Risks include accepting uppercase only after validation, rejecting non-canonical encodings, and assertion/precondition behavior being disabled or changed. Test signals should cover round-trips for all short byte lengths, invalid trailing characters, empty bytes, `None`, URI regex integration, and compatibility with historical Tahoe caps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/base32.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/base62.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/util/base62.py

## Purpose

This module implements Tahoe-LAFS base62 conversion over digits, uppercase letters, and lowercase letters. It supports both byte-aligned round-trips and explicit bit-length encodings for compact non-byte-aligned values.

## APIs and control flow

`b2a()` encodes bytes using `b2a_l()` with `len(os) * 8` and asserts the output length maps back to the input byte length. `b2a_l()` treats input bytes as a big-endian integer, repeatedly divides by 62, and emits translated characters sized for the requested bit length. `a2b()` chooses a byte length from encoded-character count, while `a2b_l()` decodes with the explicit bit length. Length helpers use `log_floor` and `log_ceil`.

## State, dependencies, risks, and tests

State is alphabet and translation tables. Dependencies are `mathutil.log_ceil` and `log_floor`. There is no persistence, but serialized values produced elsewhere depend on the exact alphabet and bit-length agreement.

The docstrings warn that `b2a_l()` and `a2b()` are not safely interchangeable when the data length is not byte-aligned. Risks include silent truncation of least-significant bits in explicit-length mode and no strong validation of illegal input bytes before translation. Test signals should cover byte-aligned round-trips, explicit bit lengths, output length formulas, invalid characters, and compatibility with any caller that persists base62 text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/base62.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/cbor.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/util/cbor.py

## Purpose

This module is a deliberate CBOR entry point that allows encoding through `cbor2` but blocks decoding through the wrong library. Tahoe-LAFS wants CBOR decoding to use `pycddl`, presumably for schema validation and safer decoding behavior.

## APIs and control flow

`dumps` and `dump` are imported directly from `cbor2`. `load()` always raises `RuntimeError("Use pycddl for decoding CBOR")`, and `loads` is an alias to that rejecting function. `__all__` exports all four names so accidental imports still get a loud failure for decoding.

## State, dependencies, risks, and tests

There is no state or persistence here; persistence belongs to callers that serialize CBOR bytes. The only dependency is `cbor2` for encoding. The main integration point is policy: modules should use this file instead of importing `cbor2.loads()`.

Risks are bypassing this module and decoding without pycddl, or assuming `loads` works because it is exported. Test signals should verify `dump`/`dumps` can encode representative values and `load`/`loads` raise consistently with the exact guidance message.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/cbor.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/configutil.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/util/configutil.py

## Purpose

This module reads, writes, copies, and validates Tahoe configuration files using `ConfigParser`. It normalizes UTF-8 with optional BOM, supports non-strict duplicate options, atomically-ish writes configs, and provides a composable `ValidConfiguration` contract for rejecting unknown sections/options.

## APIs and control flow

`get_config()` reads a file with `utf-8-sig` and delegates to `get_config_from_string()`. `set_config()` creates sections as needed. `write_config()` writes to a Twisted `FilePath` temporary sibling, creates parent directories, removes the target first on Windows, then moves the temp into place. `validate_config()` iterates all sections/options and raises `UnknownConfigError` for anything outside a `ValidConfiguration`.

`ValidConfiguration.everything()`, `.nothing()`, `.is_valid_section()`, `.is_valid_item()`, and `.update()` combine static valid sections with dynamic predicates. `copy_config()` clones values while escaping `%` to avoid interpolation effects.

## State, dependencies, risks, and tests

State is the returned `ConfigParser` and validation objects; persistence is `tahoe.cfg` on disk. Dependencies include `ConfigParser`, attrs, Twisted `platform`, and `FilePath` APIs. Integration points include node creation, provider configuration, and config validation.

Risks include Windows non-atomic overwrite behavior, `strict=False` accepting duplicate config entries, interpolation `%` handling, and predicate composition accidentally allowing too much. Test signals should cover BOM input, unknown section/option errors, atomic write paths, Windows target removal behavior, config copying with `%`, and merged validators.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/configutil.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/connection_status.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/util/connection_status.py

## Purpose

This module converts Foolscap reconnection state into Tahoe's `IConnectionStatus` shape for status displays and diagnostics. It summarizes whether a connection is live, connecting, waiting, or unstarted and preserves per-hint non-connected statuses.

## APIs and control flow

`ConnectionStatus` stores `connected`, `summary`, `non_connected_statuses`, `last_connection_time`, and `last_received_time`. `ConnectionStatus.unstarted()` returns a canonical not-yet-attempted object. `from_foolscap_reconnector()` reads `Reconnector.getReconnectionInfo()`, normalizes byte states, handles `unstarted`, `connected`, `connecting`, and `waiting`, then builds a summary and maps losing hints through `_hint_statuses()`.

## State, dependencies, risks, and tests

State is a snapshot object; there is no persistence. Dependencies are Foolscap `Reconnector`, Tahoe `IConnectionStatus`, zope interfaces, and time injection for waiting summaries.

Risks include assumptions about Foolscap's `ReconnectionInfo` field names, missing `winningHint` in connected state, and fragile human-readable timing for waiting state. Test signals should cover all reconnection states, bytes/native string state values, listener-based connections, multiple hints and handlers, and deterministic waiting text with an injected time function.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/connection_status.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/consumer.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/util/consumer.py

## Purpose

This module provides a simple Twisted `IConsumer` that accumulates downloaded bytes in memory. It is used by filenode read paths when a caller wants the whole requested range as one bytes object.

## APIs and control flow

`MemoryConsumer` stores `chunks`, `done`, and the producer. `registerProducer()` starts a streaming producer once or repeatedly calls `resumeProducing()` for non-streaming producers until `unregisterProducer()` marks completion. `write()` appends bytes. `download_to_data(n, offset=0, size=None)` calls `n.read(MemoryConsumer(), offset, size)` and joins collected chunks in a callback.

## State, dependencies, risks, and tests

State is in-memory downloaded data; there is no disk persistence. Dependencies are zope interface implementation and Twisted `IConsumer`. Integration is direct with filenode `read()` implementations and producer/consumer flow control.

Risks include unbounded memory use for large downloads, synchronous loops for non-streaming producers that depend on correct producer behavior, and lack of pause/resume/backpressure beyond the basic interface. Test signals should exercise streaming and non-streaming producers, offset/size reads through a fake filenode, chunk ordering, empty downloads, and Deferred error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/consumer.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/cputhreadpool.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/util/cputhreadpool.py

## Purpose

This module owns a global Twisted thread pool for CPU-intensive work so Tahoe does not consume the reactor's general thread pool used by DNS and other blocking operations. The pool starts at import time and is sized from `os.cpu_count()`.

## APIs and control flow

`defer_to_thread()` is an async wrapper around `deferToThreadPool()` that runs a callable in `_CPU_THREAD_POOL` and awaits its result. If `_DISABLED` is true, it calls the function synchronously. `disable_thread_pool_for_test(test)` flips `_DISABLED` and registers a cleanup on a `unittest.TestCase`. Import-time setup starts the pool and either registers `_CPU_THREAD_POOL.stop` with `threading._register_atexit` or makes worker threads daemon-capable on older Python.

## State, dependencies, risks, and tests

State is the global `_CPU_THREAD_POOL` and `_DISABLED` flag. Dependencies include Twisted threadpool APIs, the global reactor, Python threading internals, typing helpers, and unittest cleanup. Integration is with CPU-bound code paths that must not block the reactor.

Risks include import-time side effects, reliance on private `threading._register_atexit`, too many threads under cgroups/affinity constraints, and synchronous test mode masking race behavior. Test signals should verify threaded execution, exception propagation, synchronous disable/restore, shutdown behavior, and no accidental use of the default reactor pool.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/cputhreadpool.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/dbutil.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/util/dbutil.py

## Purpose

This module centralizes SQLite database open/create/version-upgrade behavior. It is used by Tahoe components such as backup database code that need a schema version table and migration scripts.

## APIs and control flow

`DBError` wraps open, compatibility, and version failures. `get_db()` opens or creates a SQLite file, enables foreign keys, executes the initial schema and inserts the target version for new databases, reads the `version` table, applies sequential updater scripts while `version < target_version`, and verifies the final version. `just_create` returns immediately after creation/version read for tests.

## State, dependencies, risks, and tests

Persistent state is the SQLite file and its `version` table. Dependencies are `sqlite3`, `os.path.exists`, and optional stderr naming. The parent directory must already exist.

Risks include updater scripts needing to update the `version` table consistently with the loop, failure after partial migration commits, no explicit transaction wrapping across multi-version upgrades, and treating incompatible files as `DBError`. Test signals should cover fresh creation, foreign-key enforcement, unusable files, missing updater paths, sequential migrations, `just_create`, and open failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/dbutil.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/deferredutil.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/util/deferredutil.py

## Purpose

This module provides Twisted Deferred utilities for timeouts, DeferredList result normalization, eventual callback chaining, test hooks, polling cleanup, async/coroutine bridging, and racing Deferreds. It is a shared async infrastructure module.

## APIs and control flow

`timeout_call()` races a Deferred result against a reactor timer and raises local `TimeoutError` on expiry. `DeferredListShouldSucceed()` and `gatherResults()` convert DeferredList results into plain lists or first failures. `eventually_callback()`, `eventually_errback()`, and `eventual_chain()` schedule callbacks through Foolscap `eventually` while logging `AlreadyCalledError`.

`HookMixin` lets tests register named one-shot Deferred hooks with ignore counts. `WaitForDelayedCallsMixin` polls the reactor for near-term delayed calls. `until()` repeats a Deferred-returning action until a predicate is true. `async_to_deferred()` wraps async functions into Deferred-returning callables. `race()` returns the first successful Deferred index/value and cancels the rest, or fails with `MultiFailure`.

## State, dependencies, risks, and tests

State is mostly caller-owned Deferreds plus hook dictionaries. Dependencies include Twisted reactor/defer/error, Foolscap eventual scheduling, Eliot inline callbacks, Failure, local logging, and `PollMixin`.

Risks include Deferred cancellation semantics, timer/result races, swallowing AlreadyCalled problems unless logs are checked, `race()` behavior when inputs ignore cancellation, and test hook misuse. Test signals should cover timeout success/failure races, DeferredList failures, hook ignore counts and async mode, delayed-call polling, coroutine conversion, `until()` loops, `race()` first success, all-failure `MultiFailure`, and cancellation propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/deferredutil.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/dictutil.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/util/dictutil.py

## Purpose

This module contains small dictionary helpers used across Tahoe: value filtering, dictionaries of sets, auxiliary cached values, and typed-key dictionaries for bytes or unicode keys.

## APIs and control flow

`filter(pred, orig)` returns key/value pairs whose values match a predicate. `DictOfSets` has `add`, `update`, and `discard` operations that create, merge, and remove empty sets. `AuxValueDict` keeps a parallel `auxilliary` map; normal assignment clears aux state, while `set_with_aux()` sets both main and cached packed values. `_TypedKeyDict` enforces key types in initialization and selected methods; `BytesKeyDict` and `UnicodeKeyDict` specialize it.

## State, dependencies, risks, and tests

State is in-memory dictionaries only. Dependencies are typing primitives. Integration includes directory-node packing/unpacking where `AuxValueDict` can avoid repacking unchanged children, and byte/unicode separation in Python 3 porting surfaces.

Risks include incomplete key-type enforcement for unoverridden dict methods such as bulk updates, the misspelled `auxilliary` field becoming API by accident, and ambiguity between missing aux values and explicit `None`. Test signals should cover set discard cleanup, aux clearing on assignment/delete, aux-preserving set, initialization with bad keys, method-level type errors, and unmodified dict behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/dictutil.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/eliotutil.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/util/eliotutil.py

## Purpose

This module bridges Tahoe-LAFS with Eliot structured logging. It supplies validators, CLI option handlers for destinations, a Twisted service that installs Eliot destinations, relays Twisted and stdlib logging into Eliot, and a decorator for Deferred-returning logged calls.

## APIs and control flow

`validateInstanceOf()` and `validateSetMembership()` create Eliot validators. `eliot_logging_service()` parses destination factories and returns `_EliotLogging`, a `MultiService` that wraps destinations in `ThreadedWriter`, installs stdlib and Twisted observers on start, and removes them on stop. `opt_eliot_destination()` parses `file:<path>` destination strings and appends factories to Twisted Options; `opt_help_eliot_destinations()` prints help.

`_TwistedLoggerToEliotObserver` flattens Twisted events with `eventAsJSON`, removes nonserializable fields, and writes Eliot messages. `_StdlibLoggingToEliotHandler` writes stdlib records and tracebacks. `_DestinationParser` supports stdout via `-` or rotating `LogFile`s. `log_call_deferred()` wraps a Deferred-returning function in an Eliot action and finishes when the Deferred fires.

## State, dependencies, risks, and tests

State is installed observers, logging handlers, and destination writer services. Dependencies include Eliot, Twisted logging/service/options, attrs validators, `jsonbytes.AnyBytesJSONEncoder`, and local `provides`.

Risks include duplicate observer installation, JSON serialization changes in Twisted events, file destination parsing with reserved characters, background writer lifecycle leaks, and logging recursion. Test signals should cover destination parsing, rotate args, stdout destination, service start/stop cleanup, Twisted/stdlib relay output, bytes JSON encoding, UsageError mapping, and Deferred action completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/eliotutil.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/encodingutil.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/util/encodingutil.py

## Purpose

This module normalizes Tahoe-LAFS command-line, filesystem, URL, and display encoding behavior across platforms after the Python 3 port. It favors UTF-8 for I/O, preserves Unicode filesystem APIs, and provides robust quoting for human-visible output.

## APIs and control flow

`canonical_encoding()`, `check_encoding()`, `_reload()`, `get_filesystem_encoding()`, and `get_io_encoding()` establish encodings. `argv_to_unicode()`, `argv_to_abspath()`, and deprecated `unicode_to_argv()` handle CLI values. `to_bytes()`, `from_utf8_or_none()`, and `unicode_to_url()` handle UTF-8 conversion. `quote_output()` and helpers quote bytes/unicode using single quotes where safe or backslash escapes for control/nonprintable bytes. Path helpers quote, extend, and convert Twisted `FilePath`s, list directories, and normalize Unicode to NFC.

## State, dependencies, risks, and tests

State is module globals `io_encoding` and `filesystem_encoding`. Dependencies include `six`, `sys`, `os`, `re`, `unicodedata`, Twisted `usage` and `FilePath`, local logging, assertions, and `fileutil.abspath_expanduser_unicode`.

Risks include locale mismatch, deprecated helpers still used by callers, quoting changing user-visible CLI output, Windows long-path handling interaction through `FilePath`, and `argv_to_abspath()` rejecting paths beginning with `-`. Test signals should cover invalid argv bytes, dash-prefixed paths, quote behavior for printable, newlines, invalid UTF-8 bytes, surrogate pairs, `FilePath` round-trips, NFC normalization, and platform-specific Windows path forms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/encodingutil.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/fileutil.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/util/fileutil.py

## Purpose

This module provides Tahoe-LAFS filesystem primitives: retrying Windows file removal/rename, temporary files, encrypted temporary storage, recursive directory operations, atomic-ish writes, path normalization, Windows long path support, disk-space stats, no-overwrite replacement, and path metadata snapshots.

## APIs and control flow

`rename()` and `remove()` retry with exponential sleeps for transient Windows sharing failures. `ReopenableNamedTemporaryFile` creates a named placeholder and deletes it on shutdown. `EncryptedTemporaryFile` encrypts file contents at rest with AES counter-like offset handling. Directory helpers include `make_dirs_with_absolute_mode()`, `make_dirs()`, `rm_dir()`, `du()`, and `remove_if_possible()`. File helpers include `move_into_place()`, `write_atomically()`, `write()`, `read()`, and `put_file()`.

Path helpers enforce absolute unicode paths, expand `~`, construct Windows `\\?\` long paths, read Windows environment variables through ctypes, and collect disk stats using `GetDiskFreeSpaceExW` or `statvfs`. Replacement helpers differ by platform: Windows uses `ReplaceFileW`, POSIX uses hard-link no-overwrite or rename replacement. `get_pathinfo()` returns a `PathInfo` tuple from `lstat`.

## State, dependencies, risks, and tests

State is filesystem state and temporary AES keys. Dependencies include platform APIs, Twisted logging, Tahoe AES, `six.reraise`, and local assertions. Integration spans config writes, storage accounting, upload/download tempfiles, pid cleanup, and node path handling.

Risks are high: atomicity differs on Windows, recursive deletion is manually implemented, encrypted tempfiles require seek between read/write direction changes, long-path normalization is subtle, disk stats can fail or return quota-sensitive values, and assertion-based absolute-path preconditions protect destructive operations. Test signals should cover Windows and POSIX replacement semantics, temp cleanup, encrypted read/write/seek/truncate, recursive removal races, disk-space reserved values, unicode/long paths, symlink pathinfo, and write atomicity under existing targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/fileutil.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/gcutil.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/util/gcutil.py

## Purpose

This module helps account for resources that the Python garbage collector cannot directly see, especially bare file descriptors. It triggers full garbage collection after enough unbalanced allocations so descriptor finalizers have a chance to run.

## APIs and control flow

`_ResourceTracker` tracks `_counter` and `_threshold`. `allocate()` increments the counter and calls `gc.collect()` once the threshold is exceeded, then resets the counter. `release()` decrements the counter without allowing it to go below zero. The public singleton is `fileDescriptorResource`, exported through `__all__`.

## State, dependencies, risks, and tests

State is only the tracker counter and threshold. Dependencies are `gc` and attrs. Integration appears in `iputil.CleanupEndpoint`, which allocates duplicated file descriptors and releases them if the endpoint is garbage-collected without being listened on.

Risks include threshold tuning, over-collection cost, missed releases making GC more frequent, and under-accounting if callers allocate descriptors without using the tracker. Test signals should cover counter increment/decrement, threshold-triggered `gc.collect`, reset behavior, no negative counter, and integration with endpoint descriptor cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/gcutil.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/happinessutil.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/util/happinessutil.py

## Purpose

This module computes and explains Tahoe's "servers of happiness" placement metric: how many distinct servers can be matched to distinct shares such that any needed subset can recover the file. It supports upload/repair placement diagnostics.

## APIs and control flow

`failure_message()` chooses a user-facing explanation based on peer count, needed shares `k`, requested happiness, and effective happiness. `shares_by_server()` inverts a share-to-peers map. `merge_servers()` deep-copies a sharemap and folds in upload tracker buckets. `servers_of_happiness()` converts the sharemap into a bipartite flow network, then runs Edmonds-Karp using `residual_network()` and `augmenting_path_for()` from immutable upload code to compute maximum matching size. `_flow_network_for()` and `_reindex()` build dense integer-indexed graph vertices.

## State, dependencies, risks, and tests

State is in-memory share/server maps. Dependencies are `deepcopy` and `allmydata.immutable.happiness_upload` flow helpers. Integration is direct with erasure-coded upload placement, repair assessment, and user diagnostics when placement cannot satisfy policy.

Risks include divergence from the similar happiness_upload implementation, graph indexing differences, empty maps, duplicate/missing share numbers, and expensive flow computation for large maps. Test signals should cover empty, perfectly distributed, clustered, and tracker-merged sharemaps; failure-message branch selection; non-contiguous share IDs; and parity with upload placement calculations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/happinessutil.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/hashutil.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/util/hashutil.py

## Purpose

This module defines Tahoe-LAFS cryptographic hash domain separation, key derivation, lease secret derivation, storage index derivation, convergence hashing, mutable-cap derivations, and timing-safe comparison. The header warns that almost any change can invalidate existing URIs and stored data.

## APIs and control flow

`_SHA256d_Hasher` implements double SHA-256 with optional truncation and cached final digest. `tagged_hasher()`, `tagged_hash()`, and `tagged_pair_hash()` netstring tags/inputs for domain separation. Named helpers derive immutable storage indexes, block hashes, URI-extension hashes, plaintext/ciphertext segment hashes, convergence keys, random keys, renewal/cancel secrets, bucket secrets, mutable read/write/enabler keys, dirnode child cap keys/salts, backup DB hashes, and server permutation hashes.

`_convergence_hasher_tag()` validates `k`, `n`, zfec limits, and convergence-secret type before building the tag. `hmac()` implements a local SHA-256 construction over tag/data. `timing_safe_compare()` hashes both inputs under a random tag and compares digests.

## State, dependencies, risks, and tests

State is constants and hasher objects. Persistent compatibility is extremely high: tags, truncation lengths, netstring framing, and hash algorithms are part of stored capability and share semantics. Dependencies are `hashlib`, `os.urandom`, and local `netstring`.

Risks include changing any tag string, accepting invalid erasure parameters, relying on assertions for peer id lengths, nonstandard HMAC construction, and SHA-1 in server permutation for historical behavior. Test signals should include golden vectors for every derivation, convergence parameter validation, URI compatibility, lease secret derivation, mutable cap round-trips, timing compare equality/inequality, and old-data fixtures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/hashutil.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/humanreadable.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/util/humanreadable.py

## Purpose

This module provides a richer `reprlib.Repr` implementation for logs and diagnostics. It gives better representations for functions, bound methods, exceptions, lists, and dictionaries, especially when objects are large or mutating concurrently.

## APIs and control flow

`BetterRepr` configures larger maxima than the stdlib defaults. `repr_function()` and `repr_instance_method()` include function names, basenames, and first line numbers. `repr_instance()` expands exception arguments with temporarily larger string/list limits and handles dict/list instances directly. `repr_list()` copies a slice to tolerate concurrent mutation; `repr_dict()` snapshots and sorts items. The module-level `brepr` instance backs `hr(x)`.

## State, dependencies, risks, and tests

State is the mutable global `brepr`, intentionally overridable by other code. Dependencies are `os.path.basename` and `reprlib.Repr`. Integration is logging/debug output throughout Tahoe.

Risks include sorting dict keys that are not mutually comparable, exposing file/line details in logs, and global mutable formatter settings affecting unrelated callers. Test signals should cover functions, builtins, bound methods, exceptions with one/many args, large lists/dicts/strings, concurrent-ish mutation snapshots, and overriding `brepr`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/humanreadable.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/i2p_provider.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/util/i2p_provider.py

## Purpose

This module implements Tahoe's I2P address-family provider. It detects optional dependencies, creates node-listener configuration for I2P destinations, validates `[i2p]` config, and supplies Foolscap client/listener endpoints that hide the node's public IP.

## APIs and control flow

`create()` builds `_Provider`, imports `foolscap.connections.i2p` and `txi2p`, and validates destination config. `is_available()` and `can_hide_ip()` report capability. `_try_to_connect()` probes a SAM endpoint with `txi2p.testAPI()`, trapping expected connection/auth failures. `_connect_to_i2p()` tries default or user-specified SAM ports. `create_config()` connects to I2P, generates a destination/private key, and returns `ListenerConfig` with `listen:i2p`, `i2p:<host>:<port>` location, and tahoe.cfg entries.

`_Provider.get_listener()` constructs an I2P server endpoint string from config. `get_client_endpoint()` chooses SAM, launch, configdir, or default client endpoint behavior. `check_dest_config()` enforces required keys and rejects unsupported launch combinations.

## State, dependencies, risks, and tests

Persistent state is the generated `private/i2p_dest.privkey` and tahoe.cfg `[i2p]` entries. Dependencies are Twisted endpoints/defer/service, txi2p, Foolscap I2P, Tahoe `ListenerConfig`, `_Config`, and `IAddressFamily`.

Risks include optional dependency absence, unsupported launch mode, endpoint-string escaping, fixed external port 3457, private-key file handling, and connection probes that may hang against non-SAM services. Test signals should cover unavailable dependencies, config validation errors, SAM endpoint probing, generated config entries, listener string escaping, disabled client endpoint, and all endpoint-selection branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/i2p_provider.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/idlib.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/util/idlib.py

## Purpose

This module formats Foolscap node identifiers for display. It centralizes the base32 alphabet used for node IDs so status pages and logs present stable IDs.

## APIs and control flow

`nodeid_b2a(nodeid)` calls `foolscap.base32.encode()` and `six.ensure_text()` to return a Unicode string. `shortnodeid_b2a(nodeid)` returns the first eight characters of that display form. There is no branching beyond that conversion.

## State, dependencies, risks, and tests

There is no state or persistence. Dependencies are Foolscap's base32 implementation and `six.ensure_text`. Integration points are status displays, logs, peer identity summaries, and any UI that abbreviates server IDs.

Risks include changing the alphabet by switching away from Foolscap, short-ID collision assumptions in user interfaces, and input type mismatches. Test signals should include binary node ID formatting, Unicode return type, eight-character abbreviation, and consistency with Foolscap expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/idlib.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/iputil.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/util/iputil.py

## Purpose

This module provides network utility helpers for local IPv4 discovery, TCP port allocation/listening, file descriptor limit increases, and safe endpoint adoption. It helps Tahoe/Foolscap bind listening ports while reducing port reuse races on POSIX.

## APIs and control flow

`increase_rlimits()` tries to raise `RLIMIT_NOFILE` where useful. `get_local_addresses_sync()` enumerates `netifaces` interfaces and IPv4 addresses. `_foolscapEndpointForPortNumber()` returns either a Foolscap endpoint string for a requested port or, for automatic POSIX allocation under an `IReactorSocket` reactor, binds/listens a socket, duplicates the fd, marks it nonblocking/close-on-exec, and returns a `CleanupEndpoint` wrapping `AdoptedStreamServerEndpoint`. `listenOnUnused()` calls `tub.listenOn()` and sets a localhost location.

`CleanupEndpoint` delegates `listen()` and closes the adopted fd on garbage collection if it was never listened on, coordinating with `gcutil.fileDescriptorResource`.

## State, dependencies, risks, and tests

State is OS sockets/file descriptors and resource limits. Dependencies include `netifaces`, Foolscap `allocate_tcp_port`, Twisted endpoint/reactor interfaces, POSIX `fcntl`, `resource`, local GC tracking, and attrs.

Risks include fd leaks if adoption/listen cleanup changes, race-prone fallback allocation on Windows or reactors without `IReactorSocket`, platform-specific rlimit behavior, and only IPv4 address enumeration. Test signals should cover local address enumeration, explicit and automatic ports, POSIX adopted fd cleanup, fallback allocation, tub integration, rlimit no-op/error paths, and close-on-exec/nonblocking flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/iputil.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/jsonbytes.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/util/jsonbytes.py

## Purpose

This module makes JSON encoding tolerate bytes in values and keys. It is used by logging and diagnostics where Tahoe often has byte-oriented protocol data but JSON serializers require text.

## APIs and control flow

`bytes_to_unicode(any_bytes, obj)` recursively converts bytes to Unicode. With `any_bytes=False`, bytes must be valid UTF-8; with `True`, decoding uses `backslashreplace` for arbitrary bytes. Dict keys and values are converted, and lists/sets/tuples become lists. `UTF8BytesJSONEncoder` and `AnyBytesJSONEncoder` apply that conversion in `default`, `encode`, and `iterencode`. `dumps()` selects the encoder with an `any_bytes` keyword; `dumps_bytes()` UTF-8 encodes the JSON string. `loads` and `load` are stdlib aliases.

## State, dependencies, risks, and tests

There is no state. Dependency is stdlib `json`. Integration includes Foolscap logging wrappers and Eliot file destinations.

Risks include sets/tuples losing type identity as JSON arrays, key collisions after byte-to-text conversion, strict UTF-8 mode raising late during logging, and `__all__` omitting `dumps_bytes` even though it is useful. Test signals should cover bytes keys/values, nested structures, arbitrary bytes, strict failures, sets/tuples, JSON loads compatibility, and logging serialization paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/jsonbytes.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/log.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/util/log.py

## Purpose

This module wraps Foolscap logging for Tahoe, preserving log level constants, converting bytes in keyword fields to JSON-safe Unicode, and providing mixins that maintain parent message IDs and optional instance prefixes.

## APIs and control flow

`msg()` delegates to `foolscap.logging.log.msg()` after converting kwargs with `jsonbytes.bytes_to_unicode(any_bytes=True)`. `err()` also reports to Twisted's legacy log so unit tests fail on unexpected errors, sets a default `UNUSUAL` level, then delegates to Foolscap. `LogMixin` stores facility and parent/grandparent message IDs; `log()` chooses the parent, coerces kwarg names to native strings, records the first message id as parent, and returns the new id. `PrefixingLogMixin` combines `nummedobj.NummedObj` identity with `LogMixin` and prepends an instance prefix.

## State, dependencies, risks, and tests

State is per-instance parent message id and prefix. Dependencies are Foolscap logging, Twisted logging, pyutil `nummedobj`, `six.ensure_str`, and `jsonbytes`.

Risks include bytes conversion changing structured log values, `err()` making tests fail for handled errors if callers choose the wrong API, and parent message id state causing surprising log hierarchy after the first call. Test signals should cover bytes kwargs, default/error levels, Twisted error forwarding, parent/grandparent behavior, prefix construction from bytes, and first-message parent retention.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/log.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/mathutil.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/util/mathutil.py

## Purpose

This module is a backwards-compatibility import surface for common math helpers from `pyutil.mathutil`, plus Tahoe's local `round_sigfigs()`. Many older modules import these helpers from `allmydata.util.mathutil`.

## APIs and control flow

It re-exports `div_ceil`, `next_multiple`, `pad_size`, `is_power_of_k`, `next_power_of_k`, `ave`, `log_ceil`, and `log_floor`. `round_sigfigs(f, n)` formats `f` in scientific notation with `n-1` fractional digits and converts back to float. `__all__` documents the public names.

## State, dependencies, risks, and tests

There is no state or persistence. Dependencies are only `pyutil.mathutil` and Python float formatting. Integration includes base62 length math and statistics output.

Risks include behavior drift in pyutil imports, floating-point rounding surprises in `round_sigfigs()`, and divide/log helper edge cases inherited from pyutil. Test signals should cover import compatibility, ceiling/floor logarithms used by base62, significant-figure formatting for small/large/negative values, and `__all__` correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/mathutil.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/namespace.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/util/namespace.py

## Purpose

This module defines a minimal `Namespace` class for ad hoc attribute containers. It is a Python object equivalent of a blank record.

## APIs and control flow

`Namespace` has no methods or attributes. Instances can receive arbitrary attributes through normal Python object behavior. The file has no imports, side effects, state, or persistence beyond caller-assigned attributes.

## State, dependencies, risks, and tests

State exists only on instances created by callers. There are no dependencies. Integration is likely with tests or simple configuration/state aggregation where a full attrs/dataclass type would be excessive.

Risks include lack of validation, no readable repr, no slots, and accidental misspelled attributes. Test signals are minimal: construction should work, arbitrary attributes can be assigned/read, and import path compatibility remains stable. Future callers that need a stable schema should prefer attrs/dataclasses instead of expanding this blank container.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/namespace.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/netstring.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/util/netstring.py

## Purpose

This module implements byte netstring encoding and splitting. Tahoe uses netstrings for unambiguous framing in hashes and URI extensions, where length prefixes prevent concatenation ambiguity.

## APIs and control flow

`netstring(s)` asserts `s` is bytes and returns `<len>:<s>,`. `split_netstring(data, numstrings, position=0, required_trailer=None)` walks from `position`, parses decimal length prefixes up to `numstrings`, validates commas and lengths, and returns `(elements, new_position)`. If `required_trailer` is supplied, all remaining data must match it and is consumed.

## State, dependencies, risks, and tests

There is no state or external dependency. Integration is important: `hashutil` uses `netstring()` for domain-separated tags and input pairs, and `uri.py` packs URI extensions with netstrings.

Risks include assertion-based validation for malformed data, `data.index(b":")` raising raw `ValueError`, potential acceptance of leading-zero length strings depending on callers, and compatibility sensitivity for hash inputs. Test signals should cover normal framing, multiple strings with positions, required trailer success/failure, truncated strings, bad comma, zero-length strings, and golden hash/extension fixtures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/netstring.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/observer.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/util/observer.py

## Purpose

This module implements observer helpers for Twisted-style asynchronous code: one-shot Deferred notifications, lazy result production, immediate multi-subscriber notifications, and buffered event streams for a single subscriber.

## APIs and control flow

`OneShotObserverList.when_fired()` returns an already-succeeded Deferred after firing or stores a watcher before firing. `fire()` records the result and callbacks all watchers exactly once. `LazyOneShotObserverList` stores a result producer instead of retaining the result and only calls it when needed. `ObserverList` maintains callbacks and logs exceptions without stopping notification. `EventStreamObserver` buffers keyword-only events until a subscriber is set, schedules notifications with Foolscap `eventually`, and can call a weakref-based canceler on cancellation.

## State, dependencies, risks, and tests

State is watcher lists, fired/result flags, buffered event kwargs, and weak canceler references. Dependencies are Twisted Deferreds/logger, Foolscap eventual scheduling, and `weakref`.

Risks include one-shot double-fire assertions, retained results causing memory retention unless lazy form is used, event buffering growing unbounded before subscription, weak canceler disappearing, and asynchronous ordering through `eventually`. Test signals should cover pre/post-fire `when_fired`, lazy producer call counts, observer exception logging, unsubscribe, buffered event delivery order, watcher kwargs merge, and canceler invocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/observer.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/pid.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/util/pid.py

## Purpose

This module manages Tahoe pidfiles with file locking and process checks. It prevents multiple instances from using the same pidfile and cleans stale pidfiles when their process no longer exists.

## APIs and control flow

`_pidfile_to_lockpath()` maps `node.pid` to a sibling lock path. `parse_pidfile()` reads `pid starttime` and raises `InvalidPidFile` on malformed content. `check_pid_process()` locks the pidfile, checks an existing pid with psutil, raises `ProcessInTheWay` if any process currently owns that PID, removes stale pidfiles for missing processes, then writes the current process PID and creation time. Lock timeout also maps to `ProcessInTheWay`. `cleanup_pidfile()` locks and removes the file, wrapping failures in `CannotRemovePidFile`.

## State, dependencies, risks, and tests

Persistent state is the pidfile and lock file. Dependencies are `psutil`, `filelock`, and Twisted `FilePath`-like methods (`sibling`, `basename`, `open`, `exists`, `remove`, `path`).

Risks include only checking PID existence during `check_pid_process()` rather than comparing saved start time, stale lock files, removal failure, and process creation time precision differences across platforms. Test signals should cover malformed files, stale PID cleanup, live PID conflict, lock timeout, pidfile write format, cleanup success/failure, and PID reuse scenarios for automated callers that inspect start time.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/pid.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/pollmixin.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/util/pollmixin.py

## Purpose

This module provides a Deferred-returning polling mixin mostly for tests. It repeatedly calls a predicate until it succeeds, times out, or observes unexpected logged errors.

## APIs and control flow

`PollMixin.poll(check_f, pollinterval=0.01, timeout=1000)` starts a Twisted `LoopingCall` around `_poll()`. `_poll()` raises local `TimeoutError` after the cutoff, raises `PollComplete` when `check_f()` returns true, and, in Trial-style tests, inspects `self._observer.getErrors()` to fail early on unexpected logged errors. `poll()` converts `PollComplete` into a successful `None` result.

## State, dependencies, risks, and tests

State is the running LoopingCall and optional `_poll_should_ignore_these_errors` on the test object. Dependencies are Twisted `task.LoopingCall` and wall-clock `time.time`.

Risks include wall-clock sensitivity, predicate exceptions errbacking directly, ignored error type lists being too broad or too narrow, and long default timeouts hiding hangs. Test signals should cover immediate success, delayed success, timeout, predicate exception propagation, observed-error early failure, ignored errors, and `timeout=None` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/pollmixin.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/rrefutil.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/util/rrefutil.py

## Purpose

This module adds version metadata to Foolscap remote references. It probes the remote side for `get_version()` and falls back to a caller-provided default for older peers.

## APIs and control flow

`add_version_to_remote_reference(rref, default)` calls `rref.callRemote("get_version")`. On success it sets `rref.version` to the returned version and returns the reference. On `Violation` or `RemoteException`, interpreted as no usable remote method, it sets `rref.version` to `default` and returns the reference. The function returns the Deferred from the remote call with callbacks attached.

## State, dependencies, risks, and tests

State is mutation of the remote reference object by assigning `.version`. Dependencies are Foolscap `Violation` and `RemoteException`. Integration is with peer negotiation and compatibility paths that need a version field even for old servers.

Risks include treating all `RemoteException` values as absence of `get_version()`, masking remote implementation failures, and callers expecting `.version` before the Deferred fires. Test signals should cover success, missing method via `Violation`, remote exception fallback, unexpected failures not trapped if any, and version field assignment timing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/rrefutil.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/spans.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/util/spans.py

## Purpose

This module represents sparse byte ranges and sparse byte data. `Spans` is a compressed integer-set optimized for range operations, while `DataSpans` stores non-overlapping byte chunks with offsets. Downloaders use these structures to track requested, received, and missing share bytes.

## APIs and control flow

`Spans` stores sorted `(start, length)` intervals. `add()` merges overlapping or adjacent ranges; `remove()` trims, deletes, or splits ranges; arithmetic operators implement union, subtraction, in-place updates, and intersection; `__contains__` checks full containment of a range. `overlap()` and `adjacent()` are shared helpers.

`DataSpans` stores sorted `(start, data)` chunks. `add()` overlays new data across existing spans, replacing overlaps and merging adjacent chunks. `get()` returns exact data only if the requested range is fully contained in one merged chunk. `remove()` deletes or splits data chunks, and `pop()` combines get/remove.

## State, dependencies, risks, and tests

State is in-memory interval lists and byte chunks. There are no external dependencies. Integration is downloader scheduling and remote-share data assembly.

Risks include O(n) operations on many small ranges, assertions for invalid ranges, subtle off-by-one errors when trimming/splitting, and `DataSpans.get()` requiring a single containing span. Test signals should cover adjacent merges, overlapping additions, left/right/middle removals, intersection, containment, empty spans, data overlay cases A-E described in comments, pop behavior, and invariant checks after every mutation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/spans.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/statistics.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/util/statistics.py

## Purpose

This module computes probability mass functions and repair cost estimates for erasure-coded file survival. It assumes independent share/server survival probabilities and helps reason about `k-of-N` reliability and repair economics.

## APIs and control flow

`pr_file_loss()` sums survival PMF entries below `k`. `survival_pmf()` validates probabilities and uses convolution over `[1-p, p]` terms; `survival_pmf_via_bd()` is an internal/test alternative grouped by equal probabilities. `pr_backup_file_loss()` factors in source survival. `find_k()` and `find_k_from_pmf()` choose the highest recoverability threshold meeting a target loss probability. `repair_count_pmf()`, `bandwidth_cost_function()`, `mean_repair_cost()`, and `eternal_repair_cost()` estimate repair distributions and long-term costs. Validation and math helpers include `valid_pmf`, `valid_probability_list`, `convolve`, `binomial_distribution_pmf`, and `binomial_coeff`.

## State, dependencies, risks, and tests

There is no persistent state. Dependencies are `math`, `functools.reduce`, `sys.stdout`, and `mathutil.round_sigfigs`. Integration is analytical/planning code rather than live storage mutation.

Risks include the independence assumption being invalid for co-located shares, floating-point rounding in `valid_pmf`, binomial path limitations, and ambiguous `find_k` wording versus loop behavior. Test signals should compare convolution/binomial PMFs for small cases, validate edge probabilities 0/1, loss probability boundaries, repair PMF validity, cost formulas, printed PMFs, and invalid probability inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/statistics.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/time_format.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/util/time_format.py

## Purpose

This module formats and parses UTC timestamps, dates, durations, and elapsed deltas for Tahoe CLI/status output. It provides a small accepted duration grammar backed by an enum of unit spellings.

## APIs and control flow

`format_time()` uses `strftime`. `iso_utc_date()` and `iso_utc()` use an optional timestamp or injected clock and return UTC ISO strings with configurable separator. `iso_utc_time_to_seconds()` parses `YYYY-MM-DD[T_ ]HH:MM:SS[.subsec]` and converts with `calendar.timegm`. `parse_duration()` builds a regex from `ParseDurationUnitFormat`, accepts integer counts plus units, and maps seconds, days, 31-day months, and 365-day years to seconds. `parse_date()` parses UTC midnight. `format_delta()` renders elapsed time or `N/A`/`-`.

## State, dependencies, risks, and tests

There is no state. Dependencies are `calendar`, `datetime`, `re`, `time`, `Enum`, and typing. Integration includes config/CLI duration parsing and status timestamps.

Risks include fixed 31-day months, no fractional durations, regex values depending on enum order, local ambiguity in `format_time()` because it formats a passed time tuple, and strict timestamp parsing. Test signals should cover timestamp separators, subseconds, invalid timestamps, each duration unit and case-insensitivity, invalid units, future/None deltas, and date parsing at UTC midnight.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/time_format.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/tor_provider.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/util/tor_provider.py

## Purpose

This module implements Tahoe's Tor address-family provider. It detects optional Tor dependencies, creates onion-service listener configuration, launches or connects to Tor control ports, creates Foolscap Tor client endpoints, and starts/stops configured onion services.

## APIs and control flow

`is_available()` checks Foolscap Tor and txtorcon. `create()` injects optional import hooks and validates onion config. `_try_to_connect()`, `_connect_to_tor()`, and `_launch_tor()` probe or launch Tor control connections. `create_config()` either launches Tor or connects to an existing control port, creates an ephemeral hidden service, captures hostname/private key, removes the temporary service, writes `private/tor_onion.privkey`, and returns `ListenerConfig` with localhost server endpoint, Tor location, and `[tor]` config entries.

`_Provider.get_listener()` binds local onion backend TCP. `get_client_endpoint()` chooses launched-control, SOCKS, explicit control, or default SOCKS behavior. `_get_launched_tor()` memoizes launch with `OneShotObserverList`. `_start_onion()` reads the stored private key and adds the hidden service. `stopService()` removes it.

## State, dependencies, risks, and tests

Persistent state is the onion private key and tahoe.cfg `[tor]` entries. Runtime state includes launched Tor, active hidden service, and control protocol references. Dependencies are Twisted endpoints/service/defer, txtorcon, Foolscap Tor, local observer and port allocation, and `ListenerConfig`.

Risks include optional dependencies, fixed external port 3457, private-key file permissions, launched Tor lifecycle not fully stopped, control-port auth failures, endpoint selection conflicts, and onion removal on shutdown failures. Test signals should cover dependency absence, launch/connect branches, generated config and key file, provider validation, client endpoint selection, memoized launch, start/stop onion service, and connection failure trapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/tor_provider.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/yamlutil.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/util/yamlutil.py

## Purpose

This module provides a tiny safe YAML import surface. It keeps Tahoe callers on `yaml.safe_load` and `yaml.safe_dump` instead of the unsafe default loader/dumper APIs.

## APIs and control flow

`safe_load(f)` delegates to `yaml.safe_load(f)`. `safe_dump(obj)` delegates to `yaml.safe_dump(obj)`. There is no additional validation, state, or branching. The wrapper centralizes import paths and makes intent explicit.

## State, dependencies, risks, and tests

There is no local state or persistence; YAML documents are caller-owned. The only dependency is PyYAML. Integration is any Tahoe code that reads or writes YAML configuration or metadata.

Risks include assuming this wrapper enforces schema validation; it only uses PyYAML's safe constructors. `safe_load()` may return `None` for empty input, and `safe_dump()` formatting is PyYAML-version dependent. Test signals should cover simple maps/lists/scalars, rejection of unsafe constructors, empty documents, round-trip expectations where order/format does not matter, and caller handling of `None`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/util/yamlutil.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/web/__init__.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/web/__init__.py

## Purpose

This package initializer is intentionally empty. It marks `allmydata.web` as an importable package for Tahoe-LAFS web/status/API modules without importing any web resources at package import time.

## APIs and control flow

The file exports no names and executes no code. Importers reach concrete web modules directly, while `import allmydata.web` remains cheap and side-effect free. This matters because web modules commonly depend on Twisted Web, Nevow-style resources or templates, node state, and other runtime services that should not be initialized by package import alone.

## State, dependencies, risks, and tests

There is no state, persistence, or dependency in this file. Its integration role is packaging and import namespace stability.

Risks are mostly future edits: adding eager imports could create circular imports, force optional web dependencies into non-web code paths, or perform service setup too early. Test signals are import-level: the package should import successfully in minimal contexts, concrete submodules should still be discoverable by package-relative imports, and packaging should include the initializer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/web/__init__.py -->
