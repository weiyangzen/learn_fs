# subset-b-007908 grouped research

Work item: `subset-b-007908`

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/web/test_web.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/test/web/test_web.py

## Purpose

This is the main Tahoe-LAFS WebAPI/WebUI integration-style test module. It builds a minimal fake Tahoe client, fake uploader, fake node maker, fake history, fake storage server, and a real `webish.WebishServer`, then exercises HTTP behavior through `treq`/Twisted. The file validates welcome/status/storage pages, security headers, file and directory URL handling, mutable and immutable upload flows, JSON/HTML/text/API formats, operation handles, redirects, ETags, range requests, static serving, incident reporting, and error humanization.

## Important APIs, types, and helpers

- `FakeStatsProvider`, `FakeBucketCounter`, `FakeLeaseChecker`, and `FakeStorageServer` provide enough service/stat state for WebUI pages to render storage and lease status.
- `FakeNodeMaker` subclasses `NodeMaker` and creates `FakeCHKFileNode` / `FakeMutableFileNode` instances backed by a shared `all_contents` dictionary. Its `encoding_params` fix `k=3`, `n=10`, `happy=7`, and a 128 KiB segment size for predictable tests.
- `FakeUploader.upload` reads uploadable data, creates a fake CHK file node, stores data in `all_contents`, and returns an `upload.UploadResults` with fake timings/share metadata and the generated URI.
- `build_one_ds` constructs a `DownloadStatus` with segment, DYHB, read, and block events in complete, error, and unfinished states so status views can render mixed operation progress.
- `FakeHistory` exposes lists of upload/download/mapupdate/publish/retrieve statuses consumed by `/status`.
- `FakeDisplayableServer` supplies display-oriented storage server state, announcements, connection status, version, nickname, available space, and timestamps for welcome JSON/HTML tests.
- `FakeClient` subclasses `_Client` but avoids full client initialization. It wires together fake node maker/uploader/history/storage broker, two known storage servers, node identity, nickname, introducer/helper state, and a `SecretHolder`.
- `WebMixin` is the shared fixture. `setUp` starts `FakeClient` and `webish.WebishServer`, creates public/private roots and a nested directory tree, stores sample CHK/SDMF/MDMF files, special Unicode/HTML-sensitive names, read-only directories, and broken content references. It exposes HTTP helpers `GET`, `HEAD`, `PUT`, `DELETE`, `POST`, `POST2`, multipart `build_form`, failure helpers, node/content assertion helpers, operation polling helpers, redirect helpers, and initial-child builders.
- `MultiFormatResourceTests` defines an inline `MultiFormatResource` subclass and tests format selection, default format behavior, explicit `None` renderer fallback, and unknown-format errors.
- `Web` contains the large behavioral test suite.
- `HumanizeExceptionTests` verifies `humanize_exception` maps `MustBeReadonlyError` to 400 and `FileTooLargeError` to 413.

## Control flow and behavior covered

The fixture creates a real listening Webish service with an in-memory Tahoe graph. Most tests make HTTP requests against `self.webish_url`, parse responses, then assert either HTTP headers/body/status or resulting fake node state.

High-level WebUI coverage includes:

- Root page security headers: `X-Frame-Options: DENY` and `Referrer-Policy: no-referrer`.
- Welcome JSON and HTML server/introducer/helper status, including censoring helper FURLs and not leaking unguessable introducer secrets.
- `/storage` page rendering with nickname display.
- `/status` index and status detail pages for upload, download, mutable servermap update, publish, and retrieve operations; JSON event data for download status; malformed status paths and missing IDs.
- CSS static asset shape and `/static` file serving/missing-directory error handling.
- `/report_incident` response text without an HTML wrapper.

File URL coverage includes:

- `GET`, `HEAD`, `Range`, partial ranges, suffix ranges, invalid ranges, and bad range syntax.
- `/file/<cap>` and `/named/<cap>` name handling, attachment filenames, Unicode filenames, and errors when used with wrong methods or directory caps.
- `/uri/<filecap>` fetch, MDMF extension suffixes, read-only mutable caps, file child errors, immutable offset update errors, and read-only PUT rejection.
- ETag behavior for immutable files and immutable directories, including `If-None-Match` returning 304 and no ETag for info/rename-form responses.
- `t=json`, `t=uri`, `t=readonly-uri`, and `t=info` outputs for CHK, SDMF, and MDMF nodes.

Directory URL coverage includes:

- HTML directory listings, favicon checks, upload/mkdir form controls, read-only markers, encoded file links for unsafe names, literal immutable directory rendering, and return links.
- Directory JSON contents with child metadata, Tahoe link creation/modification times, formats for SDMF/MDMF children, and correct read/write/read-only URI visibility.
- `t=uri`, `t=readonly-uri`, invalid `t`, missing children, deletion, and replace policies.
- Manifest, deep-size, deep-stats, stream-manifest, deep-check, check, and repair/check-and-repair operations using operation handles and output variants.

Mutation and upload coverage includes:

- PUT new file, replace file, mkdirs along a path, blocking file conflicts, empty component rejection, content-range rejection, immutable vs mutable creation, and explicit `format=sdmf|mdmf|chk`.
- POST upload linked and unlinked files, Unicode names, explicit form `name`, `when_done`, upload-result redirects with substituted URI, mutable overwrite preserving URI, large mutable uploads, and predetermined RSA private key upload via `private-key`.
- POST mkdir, mkdir-with-children, mkdir-immutable, format selection, parentless `/uri?t=mkdir*` operations, initial-child JSON with known and unknown caps, immutable child validation, and ignored/invalid body cases.
- Linking by URI, unknown cap policy, set-children, delete/unlink, rename, relink, cross-directory relink, replace/no-replace/only-files policies, slash validation, and bad destination URI handling.
- PUT `t=uri` to link caps, replace/no-replace, unknown cap policy, parentless `/uri` PUT upload, `/uri?t=mkdir`, and mutable offset update/append.

Operation-handle coverage includes bad handles, cancel, `retain-for`, `release-after-complete`, uncollected expiration after four days, collected expiration after one day, and a redirect regression for `/uri/?uri=<cap>&t=json`.

## State and persistence behavior

All filesystem-like state lives in fake in-memory nodes backed by `FakeClient.all_contents`. Directory mutations update fake `DirectoryNode`/mutable node structures; immutable file contents are keyed by cap in `all_contents`; mutable content is stored by fake mutable nodes. The Webish server also has a temporary directory from `anonymous_tempfile_factory` for request bodies and a `staticdir` for static file tests. Operation-handle state is held by the Webish `operations` service and time-dependent expiration is controlled with a Twisted `Clock` plus `fakeTime` for deterministic rendering.

Persistent external effects are deliberately limited to temp files created by Trial/Twisted for the server, static file fixture content, and request temp bodies. No real Tahoe grid, introducer, storage server, or network storage persistence is used.

## Dependencies and integration points

The tests integrate with:

- Twisted services, Deferreds, Trial, `Clock`, HTTP errors, and `twisted.web`.
- `treq` for real HTTP requests against the local Webish listener.
- BeautifulSoup/html5lib for WebUI HTML assertions.
- Tahoe modules: `webish`, `web.common.MultiFormatResource`, `client._Client`, `SecretHolder`, `StorageFarmBroker`, `StubServer`, `DirectoryNode`, `NodeMaker`, immutable upload/download status, mutable servermap/publish/retrieve status, fake test nodes, URI parsing, mutable key derivation, JSON bytes helpers, base32/hash utilities, connection status, and web test helpers.
- Test helper modules `allmydata.test.common`, `common_util`, `common_web`, and `test.web.common`.

The module is a broad contract for `allmydata.webish`, `allmydata.web.root`, file/directory web resources, operation-monitor resources, upload/mkdir command parsing, and common exception-to-HTTP mapping.

## Risks and edge cases

- The fixture is intentionally fake, so tests validate WebAPI control flow and representation but not real erasure coding, storage allocation, network introducer behavior, or durable storage.
- Many tests depend on exact HTML strings, CSS snippets, or form structure. This catches regressions but can make UI refactors expensive.
- Several helper calls assume fake node operations are synchronous and ignore Deferreds from `set_uri`; this is correct for the fake nodes but would be unsafe against real implementations.
- `FakeClient` bypasses `_Client.__init__`, so changes to client attributes required by Webish may silently require fixture updates.
- URI/capability security is central: tests intentionally cover secret censoring, unknown rw-cap rejection, readonly/immutable prefix handling, and read-only mutation errors.
- Operation-handle expiry uses a fake clock; changes to scheduler/time integration must keep deterministic advancement working.

## Test signals

This file is itself a dense test signal for the WebAPI. Strongly covered areas are HTTP method routing, response formats, mutable/immutable format selection, path handling, redirects, operation handles, range/ETag semantics, JSON metadata, unknown-cap policy, and WebUI rendering. Weaker signals are real storage interaction, concurrency/race behavior, browser-level rendering, and production filesystem persistence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/web/test_web.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/web/test_webish.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/test/web/test_webish.py

## Purpose

This module tests lower-level `allmydata.webish` request and site behavior that sits below the larger WebAPI tests: multipart form parsing, request body storage policy, and access-log capability censoring.

## Important APIs, types, and functions

- `TahoeLAFSRequestTests._fields_test` builds a `TahoeLAFSRequest` over a Twisted `DummyChannel`, injects headers/body bytes, calls `requestReceived`, and matches the resulting `request.fields`.
- `test_no_form_fields` asserts GET requests do not populate `fields`.
- `test_form_fields_if_filename_set` and `test_form_fields_if_name_is_file` verify multipart POST parsing and bytes-vs-text behavior for file-like fields.
- `test_form_fields_require_correct_mime_type` ensures non-`multipart/form-data` POST bodies are not parsed as form fields, a regression check for ticket 3854.
- `TahoeLAFSSiteTests._test_censoring` creates a `TahoeLAFSSite`, sends a dummy request, and verifies the access log contains a censored path rather than raw capabilities or private key material.
- Censoring tests cover `private-key`, `/uri/<CAP>`, `/file/<CAP>`, `/named/<CAP>`, and `/uri?uri=<CAP>`.
- `_create_request` builds a request attached to a site whose temporary-file factory creates named files in a test directory, making body-storage decisions observable.
- `test_small_content`, `test_unknown_request_size`, and `test_large_request` validate the 1 MiB threshold for memory vs temporary file request content.
- `param`, `body`, `_field`, `_multipart_formdata`, and `multipart_formdata` generate simple multipart form-data payloads for the tests.

## Control flow

Request parsing tests manually drive Twisted request lifecycle methods: `gotLength`, `handleContentChunk`, and `requestReceived`. They do not start a network listener. Access-log tests instantiate `TahoeLAFSSite`, attach it to a dummy channel/factory, receive a request path, then inspect the log file. Body-size tests call `gotLength` and inspect whether the request uses `BytesIO` or creates a temporary file.

## State and persistence behavior

The only durable state is temporary: access logs at `mktemp()` paths and named temporary files in a test directory. Small request bodies stay in memory (`BytesIO`). Unknown-size and >=1 MiB bodies are written through the site's configured temporary-file factory.

## Dependencies and integration points

The module uses Hypothesis for size property tests, testtools matchers for structural assertions, Twisted `DummyChannel`/`Resource`/`FilePath`, and `SyncTestCase`. It directly imports `TahoeLAFSRequest`, `TahoeLAFSSite`, and `anonymous_tempfile_factory`, so it is a focused contract for `webish` internals used by the full WebAPI server.

## Risks and edge cases

- Censoring must keep pace with every URL shape that can carry capabilities or private keys; this file covers common forms but not every future query parameter.
- Multipart tests use a minimal hand-built serializer, which is useful for clarity but does not cover all multipart syntax variants.
- The memory/file body threshold is tested around the 1 MiB boundary; changes to Twisted request internals or site factory wiring could break assumptions.

## Test signals

Strong signals: request form parsing, non-form POST safety, sensitive data censoring in logs, and large-body spillover behavior. Remaining gaps: full HTTP server integration, malformed multipart bodies, and access-log formats beyond the tested paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/web/test_webish.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/testing/__init__.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/testing/__init__.py

## Purpose

This file is an empty package marker for `allmydata.testing`. It makes the directory importable as a Python package and carries no runtime logic, exports, or side effects.

## Important APIs, types, and functions

There are no functions, classes, constants, or explicit `__all__` entries in this file.

## Control flow

Importing `allmydata.testing` executes no code beyond normal package initialization.

## State and persistence behavior

No state is created, mutated, or persisted.

## Dependencies and integration points

The file allows sibling modules such as `allmydata.testing.web` to be imported via package-qualified paths. It also provides a namespace for future testing helpers.

## Risks and edge cases

The only practical risk is accidental removal in environments that still rely on explicit package marker files. Because it is empty, any expected package-level exports must be added deliberately elsewhere.

## Test signals

No direct tests are implied by this file. Import success for modules under `allmydata.testing` is the meaningful signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/testing/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/testing/web.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/testing/web.py

## Purpose

This module provides in-memory testing helpers for code that talks to Tahoe-LAFS through the WebUI using `treq`. It exposes a fake Tahoe root resource and a `treq.client.HTTPClient` wired through `RequestTraversalAgent`, avoiding a real network listener or real Tahoe grid while preserving an HTTP-client-style interface.

## Important APIs, types, and functions

- `__all__` exports `create_fake_tahoe_root` and `create_tahoe_treq_client`.
- `_FakeTahoeRoot` is a Twisted `Resource` with a `/uri` child. `add_data(kind, data)` delegates to the URI handler and returns the generated cap.
- `KNOWN_CAPABILITIES` is derived from `allmydata.uri` classes that expose `BASE_STRING`; it defines accepted capability kind prefixes.
- `capability_generator(kind)` validates a byte capability kind and yields deterministic fake capability strings. It updates SHA-256 hashers with zero bytes on each iteration, base32-encodes key and UEB hash material, and formats caps as `kind + key + ":" + ueb_hash + ":1:1:<size>"`.
- `_FakeTahoeUriHandler` is an `attr.s` Twisted leaf `Resource` with `data: BytesKeyDict` and per-kind `capability_generators`.
- `_FakeTahoeUriHandler.add_data(kind, data)` type-checks byte inputs, deduplicates by data bytes, generates a cap for new content, stores `cap -> data`, and returns `(fresh, cap)`.
- `_FakeTahoeUriHandler.render_PUT` reads the request body, stores it as `URI:CHK:`, returns the cap, and sets 201 for fresh data or 200 for duplicate data.
- `_FakeTahoeUriHandler.render_POST` supports `t=mkdir-immutable`, stores request bytes as `URI:DIR2-CHK:`, and returns the cap.
- `_FakeTahoeUriHandler.render_GET` accepts either `/uri?uri=<cap>` or `/uri/<cap>`, validates that a cap was supplied and exists in `data`, returns 400 for missing cap, 410 for unknown cap, or the stored bytes.
- `create_fake_tahoe_root()` builds `_FakeTahoeRoot(uri=_FakeTahoeUriHandler())`.
- `_SynchronousProducer` implements `IBodyProducer` for immediate in-memory request bodies. It accepts bytes or unwraps `FileBodyProducer` by reading its input file, sets `length`, writes all body bytes in `startProducing`, and returns a succeeded Deferred.
- `create_tahoe_treq_client(root=None)` creates a `treq.HTTPClient` with `RequestTraversalAgent(root)` and `_SynchronousProducer`.

## Control flow

Test code can call `create_fake_tahoe_root()`, optionally prepopulate it with `root.add_data(kind, data)`, then pass it to `create_tahoe_treq_client`. Requests issued through the returned `HTTPClient` traverse the Twisted resource tree in memory. PUT and POST bodies are synchronously produced, read by the fake URI handler, stored in `BytesKeyDict`, and returned as capability bytes. GET decodes the Twisted request URI with `hyperlink.DecodedURL`, extracts a query cap or path cap, and looks up stored bytes.

## State and persistence behavior

State is entirely in memory. `_FakeTahoeUriHandler.data` maps capabilities to bytes and deduplicates identical bytes by returning the existing cap. `capability_generators` stores one deterministic generator per capability kind so subsequent additions have stable but distinct sizes/caps. There is no disk persistence, real shares, mutable state model, leases, or network transport.

## Dependencies and integration points

The helper integrates Twisted resources and body producers, `treq.client.HTTPClient`, `treq.testing.RequestTraversalAgent`, `hyperlink.DecodedURL`, `attrs`, `zope.interface`, Tahoe URI constants/classes, Tahoe base32 utilities, and `BytesKeyDict`. It is intended for tests of Tahoe WebUI clients that need a lightweight subset of `/uri`.

## Risks and edge cases

- The fake implements only part of `/uri`: PUT immutable upload, POST mkdir-immutable, and GET by cap. It does not emulate mutable updates, directory listing, metadata, status pages, authorization, range requests, or real Tahoe capability semantics.
- Capability strings are syntactically plausible and deterministic but not cryptographically tied to content or erasure coding parameters.
- `render_POST` assumes `request.args[u"t"][0]` exists and is in `type_to_kind`; missing or unsupported values will raise rather than returning a polished WebAPI error.
- `_SynchronousProducer` accesses `FileBodyProducer._inputFile`, a private attribute, for testing convenience.
- GET path extraction only uses `request.postpath[0]`, so nested path behavior is intentionally absent.

## Test signals

Useful signals are client code that can PUT bytes, receive a stable cap, GET bytes back by query or path cap, observe 201/200 duplicate behavior, and create immutable-directory-like caps. Tests should avoid treating this fake as a complete WebAPI implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/testing/web.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/unknown.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/unknown.py

## Purpose

This module represents filesystem nodes whose capability type is not understood by the current Tahoe-LAFS code. It preserves security constraints around read/write authority and immutable-directory membership while allowing unknown read-only or alleged-immutable caps to be stored and copied when safe.

## Important APIs, types, and functions

- `strip_prefix_for_ro(ro_uri, deep_immutable)` removes `ALLEGED_READONLY_PREFIX` or, in deep-immutable contexts, `ALLEGED_IMMUTABLE_PREFIX` from a URI before storage in an `ro_uri` slot. It deliberately keeps an alleged-immutable prefix when storing into a mutable directory because the immutable assertion is not implied by that context.
- `UnknownNode` implements `IFilesystemNode`.
- `UnknownNode.__init__(given_rw_uri, given_ro_uri, deep_immutable=False, name=u"<unknown name>")` validates byte inputs, normalizes falsey caps to `None`, records errors instead of raising immediately, and decides whether to store an rw cap, ro cap, or an opaque error node.
- `get_cap()` and `get_readcap()` return `uri.UnknownURI` wrappers for the best cap or read cap.
- `is_readonly()` and `is_mutable()` raise `AssertionError` because unknown nodes cannot safely answer those questions.
- `is_unknown()` returns `True`.
- `is_allowed_in_immutable_directory()` returns true only for non-error nodes without an rw URI.
- `is_alleged_immutable()` returns true for non-error, read-only-only nodes whose ro URI is absent or alleged immutable.
- `raise_error()` raises the stored validation error if present.
- `get_uri`, `get_write_uri`, `get_readonly_uri`, `get_storage_index`, `get_verify_cap`, `get_repair_cap`, `get_size`, `get_current_size`, `check`, and `check_and_repair` satisfy filesystem-node API expectations with available caps or neutral `None`/succeeded-Deferred results.
- Equality compares `rw_uri` and `ro_uri` for other `UnknownNode` instances.

## Control flow

Construction is the critical control flow. If an rw URI is provided in a deep-immutable context, the constructor only accepts it when it is actually an alleged immutable cap and no ro URI was provided; otherwise it records `MustNotBeUnknownRWError` or `MustBeDeepImmutableError` and returns an opaque node. Outside deep-immutable mode, a single unprefixed cap in the rw slot is rejected because it might carry write authority that cannot be diminished. A single cap already prefixed as readonly or immutable is moved to the ro slot. A pair of rw and alleged-immutable ro caps is rejected as inconsistent.

If a ro URI remains, the constructor asks `uri.from_string(..., deep_immutable=deep_immutable, name=name)` to validate constraints. If parsing yields an `UnknownURI` with an error, the node stays opaque and stores that error. Otherwise the constructor strengthens stored caps: in deep-immutable mode it ensures the ro URI has `ALLEGED_IMMUTABLE_PREFIX`; in mutable-directory mode it stores the rw URI if any and ensures the ro URI has at least an alleged readonly/immutable prefix.

## State and persistence behavior

An `UnknownNode` stores only three pieces of local state: `error`, `rw_uri`, and `ro_uri`. It has no storage index, verify cap, repair cap, size, repair/check behavior, or persistence layer. Check operations return succeeded Deferreds with `None`, reflecting that unknown nodes cannot be checked by this implementation.

## Dependencies and integration points

The module depends on `zope.interface.implementer`, Twisted Deferred helpers, `IFilesystemNode`, `MustNotBeUnknownRWError`, `MustBeDeepImmutableError`, URI parsing/`UnknownURI`, and alleged readonly/immutable URI prefixes from `allmydata.uri`. It integrates with directory/node creation paths that may encounter future or unsupported capability types while preserving WebAPI/directory security rules. Tests in the web suite exercise unknown cap linking and immutable-directory child validation.

## Risks and edge cases

- The constructor intentionally delays errors by storing them, so callers must remember to call `raise_error()` or inspect permission methods when attaching nodes.
- Calling `is_readonly()` or `is_mutable()` is a bug and raises by design; generic filesystem-node consumers must special-case `is_unknown()`.
- Prefix handling is security-sensitive: adding a readonly or immutable prefix is only allowed after enough context establishes that the cap should not be treated as write authority.
- Single unprefixed unknown caps are rejected to avoid accidental write-authority leakage.
- Deep-immutable mode treats alleged immutable prefixes as constraints, not proof of real immutability, so downstream code must retain the distinction.

## Test signals

Relevant signals include unknown rw cap rejection in write slots, unknown readonly and alleged immutable caps linking successfully, immutable directory creation rejecting mutable/unknown rw children, and round-tripping of unknown ro/immutable caps through directory JSON or child assertions. Direct unit coverage should focus on constructor matrix cases, prefix stripping/strengthening, delayed errors, and `is_allowed_in_immutable_directory`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/unknown.py -->
