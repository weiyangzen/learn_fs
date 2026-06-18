# subset-b-009769 research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/selfupdate/verify.go -->
# sources/user-network-fs/rclone/cmd/selfupdate/verify.go

## Purpose

Build-tagged into normal self-update builds, this file verifies downloaded release archives against a signed `SHA256SUMS` file.

## Important APIs, Types, and Functions

`verifyHashsum` downloads `<site>/<version>/SHA256SUMS` and delegates to `verifyHashsumDownloaded`. `verifyHashsumDownloaded` parses the embedded `ncwPublicKeyPGP`, decodes a clearsigned checksum block, validates the detached signature with ProtonMail OpenPGP, extracts the target archive hash with `findFileHash`, and compares it to the supplied SHA-256 bytes.

## Control Flow

The path is download checksum list, parse keyring, clearsign decode, reject unsigned trailing data, check signature over `block.Bytes`, locate archive row, then reject byte inequality. Error messages distinguish key parse, missing signature, unsigned data, invalid signature, missing archive hash, and hash mismatch.

## State and Persistence Behavior

No mutable state is persisted. The trusted public key is a compiled constant, so key rotation requires source change and rebuild.

## Dependencies and Integration Points

This integrates with the broader self-update downloader and `findFileHash` in the package. It depends on `downloadFile`, `fs.Debugf`, OpenPGP clearsign parsing, and the release server checksum layout.

## Risks and Test Signals

Risks include stale signing key material, accepting a signed checksum file whose parsed archive entry is outside the signed bytes if `findFileHash` reads the wrong buffer, and strict dependency on clearsigned `SHA256SUMS` formatting. Tests in `verify_test.go` cover success, one-bit signature corruption, hash mismatch, and missing archive name.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/selfupdate/verify.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/selfupdate/verify_test.go -->
# sources/user-network-fs/rclone/cmd/selfupdate/verify_test.go

## Purpose

This test file validates self-update checksum verification against checked-in fixture data.

## Important APIs, Types, and Functions

`TestVerify` reads `testdata/verify/SHA256SUMS`, decodes the known archive SHA-256 hex string, and calls `verifyHashsumDownloaded` across four subtests.

## Control Flow

The success case verifies the fixture signature and hash. `BadSig` flips one byte in the signed data and expects an invalid signature error, then restores it. `BadSum` flips one byte in the expected digest and expects an archive hash mismatch. `BadName` asks for a non-existent archive and expects the hash lookup path to fail.

## State and Persistence Behavior

The test mutates local byte slices in memory and restores them between subtests. It reads immutable fixtures only.

## Dependencies and Integration Points

It depends on build tag `!noselfupdate`, the local `testdata/verify` release-like files, `encoding/hex`, and testify assertions.

## Risks and Test Signals

Coverage is focused and valuable for signature and digest regression. It does not exercise the networked `verifyHashsum` downloader, malformed clearsign blocks, unsigned trailing data, keyring parse failure, or multiple archive checksum rows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/selfupdate/verify_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/selfupdate/writable_unix.go -->
# sources/user-network-fs/rclone/cmd/selfupdate/writable_unix.go

## Purpose

This platform implementation decides whether a path is writable on non-Windows, non-Plan9, non-JS self-update builds.

## Important APIs, Types, and Functions

`writable(path string) bool` calls `unix.Access(path, unix.W_OK)` and returns true only when the kernel reports write access.

## Control Flow

There is no branching beyond the syscall result. The caller can use this as a preflight for replacing the current executable or related files.

## State and Persistence Behavior

No state is stored. The result is a point-in-time permissions check and can race with later chmod, ownership, mount, or ACL changes.

## Dependencies and Integration Points

It depends on `golang.org/x/sys/unix` and is selected by `!windows && !plan9 && !js && !noselfupdate`. It integrates with the self-update install path checks.

## Risks and Test Signals

`access(2)` can be misleading under elevated effective IDs or unusual ACL/security module policy, and any check-then-write sequence is inherently racy. No direct tests in this subset exercise platform-specific permission behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/selfupdate/writable_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/selfupdate/writable_unsupported.go -->
# sources/user-network-fs/rclone/cmd/selfupdate/writable_unsupported.go

## Purpose

This fallback makes the self-update writability probe permissive on Plan 9 and JavaScript builds.

## Important APIs, Types, and Functions

`writable(path string) bool` always returns true.

## Control Flow

The function intentionally performs no filesystem query. Any actual failure is deferred to the update write/replace operation.

## State and Persistence Behavior

No state or persistence is involved.

## Dependencies and Integration Points

Build tags are `(plan9 || js) && !noselfupdate`. It keeps the package buildable where the Unix and Windows probes do not apply.

## Risks and Test Signals

The permissive answer can show self-update as possible when the later write will fail. It is probably acceptable as a compatibility fallback, but there are no tests for Plan 9 or JS behavior here.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/selfupdate/writable_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/selfupdate/writable_windows.go -->
# sources/user-network-fs/rclone/cmd/selfupdate/writable_windows.go

## Purpose

This Windows implementation estimates whether a path is writable for self-update.

## Important APIs, Types, and Functions

`writable(path string) bool` calls `os.Stat`, checks the permission bits, and treats bit `128` as `UserWritableBit`.

## Control Flow

If `Stat` succeeds, the function returns true when the user-write bit is set. Any stat error returns false.

## State and Persistence Behavior

No state is persisted. The result is a metadata snapshot and can change before update writes.

## Dependencies and Integration Points

The file is selected by `windows && !noselfupdate` and integrates with self-update install checks.

## Risks and Test Signals

Windows ACLs are richer than Go mode bits, so this can produce false positives or negatives on inherited ACLs, UAC elevation, network shares, or read-only attributes. There are no Windows-specific tests in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/selfupdate/writable_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/selfupdate_disabled.go -->
# sources/user-network-fs/rclone/cmd/selfupdate_disabled.go

## Purpose

This file exposes the command-package feature flag for builds compiled with `noselfupdate`.

## Important APIs, Types, and Functions

`const selfupdateEnabled = false` is defined in package `cmd`.

## Control Flow

There is no runtime flow. Other command code can branch on the constant and the compiler can eliminate dead paths.

## State and Persistence Behavior

No state is stored.

## Dependencies and Integration Points

The build tag is `noselfupdate`. The constant intentionally lives in `cmd`, not `cmd/selfupdate`, to avoid an import cycle.

## Risks and Test Signals

The risk is build-tag drift: all call sites must compile under both enabled and disabled variants. The main signal is successful tagged compilation, not runtime tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/selfupdate_disabled.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/selfupdate_enabled.go -->
# sources/user-network-fs/rclone/cmd/selfupdate_enabled.go

## Purpose

This file exposes the command-package feature flag for normal self-update-capable builds.

## Important APIs, Types, and Functions

`const selfupdateEnabled = true` is defined in package `cmd`.

## Control Flow

There is no runtime flow. It enables command registration/help logic to use a compile-time feature flag without importing the selfupdate subpackage.

## State and Persistence Behavior

No state is stored.

## Dependencies and Integration Points

The build tag is `!noselfupdate`. The comment documents that the constant must remain in `cmd` to prevent dependency loops.

## Risks and Test Signals

Risks are limited to build configuration and accidental relocation. Tagged build tests are the relevant signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/selfupdate_enabled.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/dlna/cds.go -->
# sources/user-network-fs/rclone/cmd/serve/dlna/cds.go

## Purpose

`cds.go` implements the DLNA ContentDirectory service over rclone VFS content, translating files and directories into DIDL-Lite UPnP AV objects.

## Important APIs, Types, and Functions

`contentDirectoryService` embeds the server and UPnP eventing. Key functions are `cdsObjectToUpnpavObject`, `readContainer`, `mediaWithResources`, `objectFromID`, `countChildren`, and `Handle`. `object` converts between cleaned absolute VFS paths, ObjectIDs, parent IDs, and local display paths.

## Control Flow

Browse requests are unmarshaled from SOAP XML, empty or `0` ObjectIDs resolve to root, and `BrowseDirectChildren` lists a VFS directory, folds in `Subs` children, sorts directories before files, associates subtitle resources, marshals UPnP AV objects, adjusts XML entities, and wraps the result in ordered SOAP args. `BrowseMetadata` stats one object and returns a single DIDL item or container. Unsupported actions become UPnP invalid action/value errors.

## State and Persistence Behavior

The service stores no durable state. `updateIDString` uses the process ID, so update IDs are process-lifetime signals rather than real content version counters.

## Dependencies and Integration Points

It depends on rclone VFS, MIME helpers, anacrolix UPnP/DLNA types, `upnpav` structs, HTTP request host names for resource URLs, and service descriptions in `ContentDirectory.xml`.

## Risks and Test Signals

Risks include expensive full-directory reads, ObjectID/path escaping corner cases, subtitle matching across mixed directories, MIME misclassification, Samsung/XML compatibility regressions, and a TODO that BrowseMetadata omits external subtitles. `cds_test.go` exercises subtitle association, title trimming, SOAP escaping, and resource inclusion; `dlna_test.go` exercises live SOAP browse calls.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/dlna/cds.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/dlna/cds_test.go -->
# sources/user-network-fs/rclone/cmd/serve/dlna/cds_test.go

## Purpose

This file unit-tests ContentDirectory helper behavior that is difficult to verify only through full DLNA server requests.

## Important APIs, Types, and Functions

`TestMediaWithResources` builds a local backend VFS and calls `mediaWithResources`. `TestSOAPResponseQuoteEscaping`, `TestTitleExtensionRemoval`, and `TestAdjustXMLApostrophes` validate output formatting expectations.

## Control Flow

The tests list fixture directories, append `Subs` entries where needed, and assert that media nodes retain matching `.srt`, language-suffixed `.srt`, and `.idx`/`.sub` resources. Formatting tests simulate marshaled SOAP/DIDL payloads and verify named XML entities and extension-trimmed titles.

## State and Persistence Behavior

Tests use local fixture files and in-memory VFS nodes. They do not mutate persistent source fixtures.

## Dependencies and Integration Points

They depend on the local backend, VFS, anacrolix SOAP args, testify, and `cmd/serve/dlna/testdata/files`.

## Risks and Test Signals

The tests are strong signals for DLNA client compatibility fixes, especially Samsung behavior. They do not cover malformed ObjectIDs, huge directories, MIME fallback failures, browse pagination edge cases beyond the implementation path, or actual XML schema validation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/dlna/cds_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/dlna/cms.go -->
# sources/user-network-fs/rclone/cmd/serve/dlna/cms.go

## Purpose

`cms.go` implements the DLNA ConnectionManager service.

## Important APIs, Types, and Functions

`defaultProtocolInfo` is the advertised source protocol string for many common video, audio, and image MIME types. `connectionManagerService.Handle` supports only `GetProtocolInfo`.

## Control Flow

When the SOAP action is `GetProtocolInfo`, the handler returns ordered args `Source` and `Sink`; all other actions return `upnp.InvalidActionError`.

## State and Persistence Behavior

The service has no mutable state beyond embedded eventing support inherited from anacrolix.

## Dependencies and Integration Points

It is registered from `dlna.go` under the `ConnectionManager` service key and must remain consistent with `ConnectionManager.xml` action and argument definitions.

## Risks and Test Signals

The advertised protocol string is static and may overstate support because rclone does not transcode. There are indirect tests through root descriptor discovery, but no dedicated action-level tests for unsupported ConnectionManager actions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/dlna/cms.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/dlna/data/assets_generate.go -->
# sources/user-network-fs/rclone/cmd/serve/dlna/data/assets_generate.go

## Purpose

This ignored generator embeds DLNA static assets into Go source.

## Important APIs, Types, and Functions

`main` uses `vfsgen.Generate` over `http.Dir("./static")`, package name `data`, build tag `!dev`, and variable name `Assets`.

## Control Flow

`go generate` runs this program from the data directory. It scans `static`, generates `assets_vfsdata.go`, and exits fatally on generator errors.

## State and Persistence Behavior

It writes generated Go source during developer generation, not at runtime.

## Dependencies and Integration Points

It depends on `github.com/shurcooL/vfsgen`, the `static` asset directory, and `data.go` which opens `Assets`.

## Risks and Test Signals

Risks are stale generated assets when XML/templates/images change, and mismatch between `dev` and non-`dev` builds. There is no direct generator test; compile-time use of `data.Assets` and root descriptor tests provide indirect coverage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/dlna/data/assets_generate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/dlna/data/assets_vfsdata.go -->
# sources/user-network-fs/rclone/cmd/serve/dlna/data/assets_vfsdata.go

## Purpose

This generated file embeds DLNA service XML, the root descriptor template, and rclone icon PNGs as an `http.FileSystem`.

## Important APIs, Types, and Functions

`Assets` is a generated `http.FileSystem`. Generated types include `vfsgen...FS`, `CompressedFileInfo`, `CompressedFile`, `FileInfo`, `File`, `DirInfo`, and `Dir`. Methods implement `Open`, `Read`, `Seek`, `Close`, `Stat`, `Readdir`, and metadata accessors.

## Control Flow

`Open` cleans the path, finds an embedded entry, and returns a gzip-backed reader for compressed XML/template assets, a bytes reader for PNGs, or a directory wrapper. Compressed reads reset and fast-forward when seeking backward or forward.

## State and Persistence Behavior

All asset bytes are compiled into the binary. Opened file objects keep per-handle reader position only; no durable or shared mutable state is written.

## Dependencies and Integration Points

`dlna.go` serves `/static/` from `data.Assets`; `data.go` reads `rootDesc.xml.tmpl` from it. The embedded SCPD XML must match service handlers.

## Risks and Test Signals

This generated code should not be manually edited. Risks are stale asset generation, unusual generated identifier characters, seek behavior over gzip, and mismatch between embedded XML and handlers. Tests that fetch `rootDesc.xml` and static service links indirectly validate availability.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/dlna/data/assets_vfsdata.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/dlna/data/data.go -->
# sources/user-network-fs/rclone/cmd/serve/dlna/data/data.go

## Purpose

`data.go` provides runtime access to the embedded DLNA root device descriptor template.

## Important APIs, Types, and Functions

`GetTemplate` opens `rootDesc.xml.tmpl` from `Assets`, reads it fully, parses it as a `text/template`, and returns the parsed template.

## Control Flow

The function reports wrapped errors for open, read, and parse failures. It uses `fs.CheckClose` to close the embedded file while preserving an existing error.

## State and Persistence Behavior

No persistent state is written. Each call parses a fresh template rather than caching it.

## Dependencies and Integration Points

`server.rootDescHandler` calls `GetTemplate` per request to render root device XML using server fields and service descriptors.

## Risks and Test Signals

Repeated parsing is simple but adds per-request work. Template errors would break discovery. `dlna_test.go` checks that root SCPD output includes expected services and URLs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/dlna/data/data.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/dlna/data/static/ConnectionManager.xml -->
# sources/user-network-fs/rclone/cmd/serve/dlna/data/static/ConnectionManager.xml

## Purpose

This SCPD document declares the UPnP ConnectionManager service contract exposed by the DLNA server.

## Important APIs, Types, and Functions

The XML declares actions `GetProtocolInfo`, `PrepareForConnection`, `ConnectionComplete`, `GetCurrentConnectionIDs`, and `GetCurrentConnectionInfo`, plus state variables for source/sink protocol info, connection IDs, direction, status, and related argument types.

## Control Flow

Clients discover this file from the root descriptor, then invoke SOAP actions at the server control URL. The Go implementation currently handles only `GetProtocolInfo`.

## State and Persistence Behavior

This is static metadata with no runtime persistence.

## Dependencies and Integration Points

It is embedded into `data.Assets` and served under `/static/`. Handler response argument names and order must match the XML.

## Risks and Test Signals

The XML advertises more actions than the Go service implements, so clients calling the optional actions receive invalid action errors. Root descriptor tests confirm the service is linked, but there are no schema or full action coverage tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/dlna/data/static/ConnectionManager.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/dlna/data/static/ContentDirectory.xml -->
# sources/user-network-fs/rclone/cmd/serve/dlna/data/static/ContentDirectory.xml

## Purpose

This SCPD document declares the UPnP ContentDirectory service contract for browse/search/media metadata discovery.

## Important APIs, Types, and Functions

The document lists actions including `GetSearchCapabilities`, `GetSortCapabilities`, `GetSystemUpdateID`, `Browse`, many optional transfer/mutation actions, and Samsung extension actions `X_GetFeatureList` and `X_SetBookmark`. It defines state variables for object IDs, browse flags, filters, counts, update IDs, feature lists, transfer status, URI arguments, and bookmark fields.

## Control Flow

DLNA clients read this XML to determine legal SOAP action names, argument names, argument directions, and expected output order. `cds.go` implements the read-oriented subset, especially `Browse`.

## State and Persistence Behavior

The file is static and embedded. It does not track actual content updates.

## Dependencies and Integration Points

It must stay consistent with `contentDirectoryService.Handle`, `soapArgs` ordering, and DIDL-Lite output. `dlna_test.go` explicitly protects Browse response argument order matching this XML.

## Risks and Test Signals

The XML advertises actions the implementation does not support, which may confuse aggressive clients. The highest-risk contract is Browse output order and XML entity compatibility; tests directly cover both.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/dlna/data/static/ContentDirectory.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/dlna/data/static/X_MS_MediaReceiverRegistrar.xml -->
# sources/user-network-fs/rclone/cmd/serve/dlna/data/static/X_MS_MediaReceiverRegistrar.xml

## Purpose

This SCPD document declares Microsoft's MediaReceiverRegistrar compatibility service.

## Important APIs, Types, and Functions

It declares `IsAuthorized`, `RegisterDevice`, and `IsValidated`, with argument/state variables for device IDs, result integers, registration request/response blobs, and authorization/validation update IDs.

## Control Flow

Clients discover the service from the root descriptor and call SOAP actions at the shared control URL. `mrrs.go` fakes positive authorization/validation and returns the server UUID for registration.

## State and Persistence Behavior

The XML is static; no authorization registry is persisted.

## Dependencies and Integration Points

It is embedded through `data.Assets` and must match `mediaReceiverRegistrarService.Handle` response argument names.

## Risks and Test Signals

The implementation is deliberately permissive and not a security control. `TestMediaReceiverRegistrarService` verifies `RegisterDevice` is reachable and returns `RegistrationRespMsg`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/dlna/data/static/X_MS_MediaReceiverRegistrar.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/dlna/dlna.go -->
# sources/user-network-fs/rclone/cmd/serve/dlna/dlna.go

## Purpose

`dlna.go` wires rclone's `serve dlna` command, RC entrypoint, HTTP routes, SOAP dispatch, media resource serving, and SSDP discovery.

## Important APIs, Types, and Functions

Public configuration is `OptionsInfo`, `Options`, global `Opt`, and Cobra `Command`. Core server APIs are `newServer`, `Serve`, `Shutdown`, `Addr`, `rootDescHandler`, `serviceControlHandler`, `soapActionResponse`, `resourceHandler`, `startSSDP`, `ssdpInterface`, and `serveHTTP`. `UPnPService` abstracts individual SOAP services.

## Control Flow

Command/RC code builds VFS and options, `newServer` resolves friendly name and network interfaces, registers ContentDirectory, ConnectionManager, and MediaReceiverRegistrar, builds HTTP routes, binds a listener, and returns a server. `Serve` starts SSDP and HTTP in goroutines, then waits for shutdown. SOAP requests parse the `SOAPACTION` header and envelope body, dispatch to the service map, and return either ordered response XML or a UPnP fault.

## State and Persistence Behavior

Server state is in memory: listener, VFS, selected interfaces, UUID derived from friendly name, wait channel, route handler, and service map. There is no content index persistence; media listing is live VFS access.

## Dependencies and Integration Points

It integrates Cobra, `serve.Command`, RC, rclone VFS, systemd notification, anacrolix UPnP/SOAP/SSDP, embedded data assets, and HTTP clients/players.

## Risks and Test Signals

Risks include SSDP interface filtering, IPv4/IPv6 advertise mismatches, type assertion of resource nodes to `*vfs.File`, goroutine shutdown races if `Shutdown` is called multiple times, and SOAP/XML compatibility. Tests cover root descriptor, media serving, browse requests, receiver registration, RC creation, and content resource URLs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/dlna/dlna.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/dlna/dlna_test.go -->
# sources/user-network-fs/rclone/cmd/serve/dlna/dlna_test.go

## Purpose

This file performs integration-style DLNA server tests against local fixture media.

## Important APIs, Types, and Functions

`startServer` creates a `server` on `localhost:0`. Tests cover initialization, root descriptor serving, content download, ContentDirectory `BrowseMetadata`, Browse response argument ordering, MediaReceiverRegistrar, direct child browsing, and RC startup.

## Control Flow

The tests start one package-level server, issue HTTP GET or SOAP POST requests, set `SOAPACTION` headers, read response bodies, and assert status codes and important XML/resource fragments. Direct-child tests browse root and subdirectories to verify subtitle URLs from same directory and `Subs`.

## State and Persistence Behavior

Tests use local fixture files and a package-global `dlnaServer`/`baseURL`. The server remains shared across tests after `TestInit`, so ordering assumptions are present.

## Dependencies and Integration Points

Dependencies include local backend registration, configfile setup, VFS, HTTP client, anacrolix SOAP, `servetest.TestRc`, and fixture media under `testdata/files`.

## Risks and Test Signals

Coverage is strong for HTTP/SOAP interoperability and Samsung-specific Browse ordering. Residual risks include test order coupling, no SSDP multicast verification, no concurrent browse/shutdown tests, and no negative SOAP malformed-request tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/dlna/dlna_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/dlna/dlna_util.go -->
# sources/user-network-fs/rclone/cmd/serve/dlna/dlna_util.go

## Purpose

This utility file provides naming, UUID generation, interface filtering, DIDL/SOAP XML helpers, request logging, trace logging, response headers, error handling, and extension splitting for the DLNA server.

## Important APIs, Types, and Functions

Important functions include `makeDefaultFriendlyName`, `makeDeviceUUID`, `listInterfaces`, `isAppropriatelyConfigured`, `didlLite`, `adjustXML`, `mustMarshalXML`, `soapArgs`, `marshalSOAPResponse`, `logging`, `traceLogging`, `withHeader`, `serveError`, and `splitExt`. `soapArg` preserves SOAP argument order.

## Control Flow

HTTP middleware wraps handlers with panic/error logging and optional full request/response dumping. SOAP output marshals args in explicit slice order, then replaces numeric XML entities for compatibility before wrapping them in an action response. Interface helpers filter usable SSDP interfaces.

## State and Persistence Behavior

No durable state is stored. `loggingResponseWriter` tracks per-request commit state, and trace logging buffers the response through `httptest.ResponseRecorder`.

## Dependencies and Integration Points

Utilities are used across `dlna.go` and `cds.go`, and depend on rclone logging, anacrolix SOAP/UPnP, net interfaces, HTTP test utilities, and XML encoding.

## Risks and Test Signals

Risks include response buffering memory cost under trace logging, panic recovery after partial response commit, `maps.Copy` header behavior for multi-value headers, and fragile XML string substitutions. Tests cover XML entity adjustment, SOAP quote escaping, and ordered Browse response output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/dlna/dlna_util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/dlna/dlna_util_test.go -->
# sources/user-network-fs/rclone/cmd/serve/dlna/dlna_util_test.go

## Purpose

This test file protects DLNA XML compatibility normalization.

## Important APIs, Types, and Functions

`TestAdjustXML` calls `adjustXML` with simple, quoted, mixed, already-normalized, and nested XML strings.

## Control Flow

Each subtest compares the returned string to an expected value, ensuring numeric quote entities become `&quot;` while already named entities are preserved.

## State and Persistence Behavior

No persistent state is touched.

## Dependencies and Integration Points

It depends only on `testing`, testify assertions, and the helper under test.

## Risks and Test Signals

It is a precise regression signal for Samsung-compatible entity output. It does not test apostrophes and all "Big 5" entities because those cases live in `cds_test.go`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/dlna/dlna_util_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/dlna/mrrs.go -->
# sources/user-network-fs/rclone/cmd/serve/dlna/mrrs.go

## Purpose

`mrrs.go` implements a minimal Microsoft MediaReceiverRegistrar service for DLNA client compatibility.

## Important APIs, Types, and Functions

`mediaReceiverRegistrarService.Handle` supports `IsAuthorized`, `IsValidated`, and `RegisterDevice`.

## Control Flow

Authorization and validation actions return `Result=1`. `RegisterDevice` returns `RegistrationRespMsg` containing the server root device UUID. Any other action returns `upnp.InvalidActionError`.

## State and Persistence Behavior

No device registry, authorization table, or validation state is stored. Responses are stateless and permissive.

## Dependencies and Integration Points

The service is registered in `newServer`, described by `X_MS_MediaReceiverRegistrar.xml`, and tested through the shared SOAP control endpoint.

## Risks and Test Signals

This should not be interpreted as authentication; it is compatibility scaffolding. Tests verify `RegisterDevice` response presence, but not the two boolean actions or invalid-action behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/dlna/mrrs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/dlna/upnpav/upnpav.go -->
# sources/user-network-fs/rclone/cmd/serve/dlna/upnpav/upnpav.go

## Purpose

This file defines the XML model used to marshal rclone VFS nodes into UPnP AV DIDL-Lite objects.

## Important APIs, Types, and Functions

Types are `Resource`, `Container`, `Item`, `Object`, and `Timestamp`. `NoSuchObjectErrorCode` maps ContentDirectory missing-object errors to UPnP code 701. `Timestamp.MarshalXML` formats non-zero dates as `YYYY-MM-DD`.

## Control Flow

`encoding/xml` uses struct tags to emit `res`, `container`, `item`, `dc:title`, `upnp:class`, resources, attributes, and inner XML. Zero timestamps omit date elements.

## State and Persistence Behavior

These are pure value types with no persistence.

## Dependencies and Integration Points

`cds.go` constructs these values before wrapping XML in DIDL-Lite. The XML namespace prefixes are supplied by `didlLite`.

## Risks and Test Signals

The struct tags are a wire contract with DLNA clients. Risks include missing optional metadata, wrong class strings, zero date omission differences, and XML namespace assumptions. Integration tests inspect resulting DIDL fragments but do not validate against a DIDL schema.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/dlna/upnpav/upnpav.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/docker/api.go -->
# sources/user-network-fs/rclone/cmd/serve/docker/api.go

## Purpose

`api.go` exposes the Docker volume plugin HTTP API and adapts JSON requests to the driver methods.

## Important APIs, Types, and Functions

It defines request/response structs for create, remove, mount, unmount, path, get, list, capabilities, and errors. `newRouter` registers chi POST routes for Docker plugin endpoints. `decodeRequest` decodes JSON; `encodeResponse` writes Docker plugin content type, success bodies, or `ErrorResponse`.

## Control Flow

Each route decodes the JSON body into a typed request, calls the corresponding `Driver` method, and encodes either the response or an HTTP 500 error JSON understood by Docker. `/Plugin.Activate` returns `Implements: ["VolumeDriver"]`; capabilities returns the configured scope.

## State and Persistence Behavior

The router itself is stateless; all volume state lives in `Driver`.

## Dependencies and Integration Points

It depends on Docker's plugin HTTP contract, chi routing, rclone logging, and the driver/volume types in this package.

## Risks and Test Signals

Risks include returning HTTP 500 for all driver errors, no method/content negotiation beyond route matching, and limited decode error format. `docker_test.go` exercises activation and create/mount/unmount/remove/list API flows over TCP and Unix sockets when enabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/docker/api.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/docker/docker.go -->
# sources/user-network-fs/rclone/cmd/serve/docker/docker.go

## Purpose

This file registers the `rclone serve docker` command and global plugin options.

## Important APIs, Types, and Functions

Global settings include `pluginName`, `pluginScope`, `baseDir`, socket/spec paths, `stateFile`, `socketAddr`, `socketGid`, `canPersist`, `forgetState`, and `noSpec`. `Command` is the Cobra command; `help` trims embedded `docker.md`.

## Control Flow

Command initialization adds Docker-specific, mount, and VFS flags. Runtime creates a `Driver`, wraps it in a `Server`, then serves on the default plugin Unix socket, an explicit Unix socket path, or a TCP address with optional spec-file writing.

## State and Persistence Behavior

Persistent state is handled by `Driver` in the rclone cache dir. Command globals configure where sockets, specs, and volume mountpoints live.

## Dependencies and Integration Points

It integrates Cobra, `serve.Command`, mountlib, VFS flags, embedded docs, and platform socket helpers.

## Risks and Test Signals

Global variables mean tests and repeated command setup must avoid cross-test contamination. Persisted remote creation is disabled by `canPersist=false`. API and option tests cover most driver behavior, but command-line flag combinations are not exhaustively tested.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/docker/docker.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/docker/docker_test.go -->
# sources/user-network-fs/rclone/cmd/serve/docker/docker_test.go

## Purpose

This test file validates Docker plugin driver logic and, when possible, end-to-end Docker plugin API serving.

## Important APIs, Types, and Functions

Helpers include `initialise`, `assertErrorContains`, `assertVolumeInfo`, `APIClient`, `newAPIClient`, `APIClient.request`, and `testMountAPI`. Tests include `TestDockerPluginLogic`, `TestDockerPluginMountTCP`, and `TestDockerPluginMountUnix`.

## Control Flow

`TestDockerPluginLogic` uses a dummy driver to create volumes, validate bad options, list/get, mount with multiple IDs, restore saved state, and remove after unmount. API tests start a real server, call Docker endpoints, write through the mounted path, then unmount and remove.

## State and Persistence Behavior

Tests redirect rclone cache dir to a temp directory so `docker-plugin.state` is isolated. Dummy tests exercise persistence without real mounts.

## Dependencies and Integration Points

They depend on local and memory backends, mount/cmount packages, mountlib availability, Docker API JSON, TCP/Unix sockets, and filesystem cleanup helpers.

## Risks and Test Signals

The file has `!race` and skips or marks real mount tests unreliable on some platforms, so concurrency and real mount coverage may be absent in CI. The tests still provide strong signals for state restoration, request reference counting, and API error formatting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/docker/docker_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/docker/driver.go -->
# sources/user-network-fs/rclone/cmd/serve/docker/driver.go

## Purpose

`driver.go` implements the stateful Docker volume driver: volume registry, state persistence, mount monitoring, cache clearing, and lifecycle cleanup.

## Important APIs, Types, and Functions

`Driver` stores root path, volumes map, state path, mount/VFS defaults, synchronization, and monitor channels. Public methods are `NewDriver`, `Exit`, `Create`, `Remove`, `List`, `Get`, `Path`, `Mount`, and `Unmount`; internal helpers include `monitor`, `clearCache`, `getVolume`, `listVolumes`, `saveState`, and `restoreState`.

## Control Flow

Construction creates cache directories, copies defaults, optionally restores JSON state, starts a monitor goroutine, registers atexit unmounting, and notifies systemd. Driver API methods lock the mutex, mutate `volumes` and per-volume mount IDs, and save state after persistent changes. The monitor selects on control signals and mount error channels, clearing caches or cleaning up externally unmounted volumes.

## State and Persistence Behavior

State persists as JSON `docker-plugin.state` under rclone's cache dir. `Exit` unmounts all volumes and persists definitions without active mount IDs. In-memory state is guarded by `mu`.

## Dependencies and Integration Points

It depends on mountlib, VFS options, rclone config/cache directories, systemd daemon notifications, atexit hooks, and `Volume` setup/mount methods.

## Risks and Test Signals

The `monitor` function appears to build both `monChan` and `hupChan` select cases from `drv.monChan`, so SIGHUP cache clearing via `hupChan` may be unreachable. Other risks include state-file corruption handling, blocking sends to `monChan`, and holding `mu` during potentially slow mount operations. Tests cover driver CRUD, persistence, and mount reference counts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/docker/driver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/docker/options.go -->
# sources/user-network-fs/rclone/cmd/serve/docker/options.go

## Purpose

`options.go` maps Docker volume creation options into rclone backend, mountlib, and VFS configuration.

## Important APIs, Types, and Functions

`Volume.applyOptions` handles special keys `remote`/`fs`, `type`, `path`, `mount-type`, and `persist`, stores remaining options, identifies backend type, parses backend configuration, and applies mount/VFS options. `normalOptName` normalizes option spelling.

## Control Flow

The function copies driver defaults, parses the remote or backend type, resolves explicit path override, finds backend metadata, classifies each remaining option as special, mount, VFS, or backend option, parses typed mount/VFS maps with `configstruct.Set`, builds `vol.fsString`, and validates the volume.

## State and Persistence Behavior

It mutates the `Volume` fields that are saved into JSON state: `Fs`, `Type`, `Path`, `Options`, plus runtime-only `fsString`, `persist`, and `mountType`.

## Dependencies and Integration Points

It integrates Docker's flat option map with rclone `fspath.Parse`, backend registry, `fs.ConfigMap`, `rc.Params`, mountlib `OptionsInfo`, VFS `OptionsInfo`, and configstruct parsing.

## Risks and Test Signals

Risks include option-name collisions, backend prefix stripping surprises, unsupported backend option rejection, and sensitive option persistence in driver state. `options_test.go` covers normalization, mount/VFS/backend classification, and parse errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/docker/options.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/docker/options_test.go -->
# sources/user-network-fs/rclone/cmd/serve/docker/options_test.go

## Purpose

This file tests Docker volume option classification and parsing.

## Important APIs, Types, and Functions

`TestApplyOptions` constructs a minimal `Volume` with mount point, driver, mount point object, and request map, then calls `applyOptions`.

## Control Flow

The happy path mixes remote, persist, mount-type, backend, mount, and VFS options with dashes, underscores, and leading `--`, then asserts the generated fs string and parsed option fields. Error cases verify invalid mount option values, invalid VFS option values, and unsupported backend option rejection.

## State and Persistence Behavior

The test mutates only an in-memory `Volume`.

## Dependencies and Integration Points

It depends on local backend registration, mountlib option metadata, VFS option metadata, rclone duration parsing, and testify.

## Risks and Test Signals

It gives good coverage for normalization and routing of flat options. It does not test `type` without `remote`, `path` override, configured named remotes, prefixed non-local backend options, or persistence restrictions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/docker/options_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/docker/serve.go -->
# sources/user-network-fs/rclone/cmd/serve/docker/serve.go

## Purpose

`serve.go` provides the HTTP server wrapper for Docker plugin communication over Unix sockets, systemd-activated sockets, or TCP.

## Important APIs, Types, and Functions

`type Server http.Server`, `NewServer`, `Shutdown`, `serve`, `ServeUnix`, `ServeTCP`, and `writeSpecFile` are the main APIs.

## Control Flow

`ServeUnix` obtains a Unix listener, logs whether it is self-created or systemd-provided, and serves. `ServeTCP` binds TCP, optionally wraps TLS, writes a Docker spec file unless disabled, and serves. `serve` registers cleanup for temp files and delegates to `http.Server.Serve`.

## State and Persistence Behavior

The server writes a Docker spec file for TCP mode and registers atexit removal for spec files or self-created sockets. It does not persist volume state directly.

## Dependencies and Integration Points

It depends on platform `newUnixListener`, Docker plugin spec-file discovery, TLS, rclone file helpers, and atexit cleanup.

## Risks and Test Signals

Risks include stale spec/socket cleanup only on normal atexit, TLS protocol assumptions, Docker discovery path permissions, and use of temp dir for Windows default spec dir. API tests exercise server startup/shutdown in TCP and Unix modes where enabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/docker/serve.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/docker/systemd.go -->
# sources/user-network-fs/rclone/cmd/serve/docker/systemd.go

## Purpose

This Linux implementation exposes systemd socket activation files to the Docker plugin Unix listener code.

## Important APIs, Types, and Functions

`systemdActivationFiles` returns `activation.Files(false)` only when `util.IsRunningSystemd()` is true.

## Control Flow

The function checks for systemd at runtime and returns either activated file descriptors or nil.

## State and Persistence Behavior

No state is persisted.

## Dependencies and Integration Points

Build tags are `linux && !android`. It integrates with `newUnixListener`, allowing systemd to pre-create the plugin socket.

## Risks and Test Signals

Risks are incorrect environment detection and multiple activated sockets. `unix.go` handles the multiple-socket error path. No direct tests cover systemd activation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/docker/systemd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/docker/systemd_unsupported.go -->
# sources/user-network-fs/rclone/cmd/serve/docker/systemd_unsupported.go

## Purpose

This fallback keeps Docker plugin code buildable where systemd activation is not supported.

## Important APIs, Types, and Functions

`systemdActivationFiles` returns nil.

## Control Flow

There is no branching or runtime action.

## State and Persistence Behavior

No state is persisted.

## Dependencies and Integration Points

Build tags are `!linux || android`. `newUnixListener` sees nil and creates its own socket.

## Risks and Test Signals

The behavior is intentionally minimal. Platform build coverage is the main signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/docker/systemd_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/docker/unix.go -->
# sources/user-network-fs/rclone/cmd/serve/docker/unix.go

## Purpose

This Unix-socket implementation creates or adopts the Docker plugin socket on Linux and FreeBSD.

## Important APIs, Types, and Functions

`newUnixListener(path string, gid int)` checks systemd activation, normalizes socket paths, creates parent directories, removes stale sockets, listens on Unix domain sockets, chmods to `0660`, and chowns to root plus the requested group when running as root.

## Control Flow

If systemd provides exactly one socket, it returns a `net.FileListener` and no cleanup path. If more than one socket is provided, it errors. Otherwise it creates a socket under `/run/docker/plugins` for relative names and returns the created path for later cleanup.

## State and Persistence Behavior

It creates a socket filesystem entry and may delete a stale one. Cleanup is registered by `serve.go`.

## Dependencies and Integration Points

It depends on `systemdActivationFiles`, `file.MkdirAll`, platform Unix sockets, and Docker's plugin socket discovery convention.

## Risks and Test Signals

Risks include removing a stale path that belongs to another process, permissions/group mismatch preventing Docker access, and systemd listener type assumptions. Unix API tests exercise explicit socket creation on Linux when not skipped.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/docker/unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/docker/unix_unsupported.go -->
# sources/user-network-fs/rclone/cmd/serve/docker/unix_unsupported.go

## Purpose

This fallback reports that Docker plugin Unix sockets are unavailable on unsupported operating systems.

## Important APIs, Types, and Functions

`newUnixListener` returns nil listener, empty path, and the error `unix sockets require Linux or FreeBSD`.

## Control Flow

There is no filesystem or network action.

## State and Persistence Behavior

No state is persisted.

## Dependencies and Integration Points

Build tags are `!linux && !freebsd`. TCP mode can still be used by `ServeTCP`.

## Risks and Test Signals

The behavior is explicit and low-risk. Cross-platform build tests are the relevant signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/docker/unix_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/docker/volume.go -->
# sources/user-network-fs/rclone/cmd/serve/docker/volume.go

## Purpose

`volume.go` defines Docker volume state and implements setup, validation, mount reference counting, unmounting, removal, and VFS cache clearing.

## Important APIs, Types, and Functions

Types include `Volume`, `VolOpts`, and `VolInfo`. Functions/methods include `newVolume`, `getInfo`, `prepareState`, `restoreState`, `validate`, `checkMountpoint`, `setup`, `remove`, `clearCache`, `mount`, `unmount`, and `unmountAll`. Errors include `ErrVolumeNotFound`, `ErrVolumeExists`, and `ErrMountpointExists`.

## Control Flow

New volumes choose a mountpoint under the driver root, apply options, verify/create an empty mountpoint, resolve a mount method, optionally create a persistent remote, and create an rclone Fs. Mount requests reject duplicate IDs, mount once for the first active ID, then record additional IDs as references. Unmount removes one ID and only performs real unmount on the last reference.

## State and Persistence Behavior

Public fields are serialized into driver JSON state. `Mounts` is regenerated from `mountReqs` before saving. Active mount internals, VFS handles, and driver pointers are runtime-only.

## Dependencies and Integration Points

It integrates rclone mountlib, VFS cache, backend creation, config remote creation/deletion, Docker mountpoint conventions, and platform mountpoint checks.

## Risks and Test Signals

Risks include mountpoint race/non-empty checks, persisted sensitive options, incomplete cleanup after partial setup, deleting persistent remotes, and Windows parent-dir behavior. Tests cover validation, mount references, state restore, and API remove-in-use behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/docker/volume.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/ftp/ftp.go -->
# sources/user-network-fs/rclone/cmd/serve/ftp/ftp.go

## Purpose

`ftp.go` implements `rclone serve ftp`, adapting rclone VFS operations to the `goftp.io/server/v2` driver and authentication interfaces.

## Important APIs, Types, and Functions

Configuration lives in `OptionsInfo`, `Options`, `Opt`, `AddFlags`, and Cobra `Command`. The `driver` type implements server lifecycle, authentication, VFS lookup, FTP filesystem operations, and logging. Key methods include `newServer`, `Serve`, `Shutdown`, `Addr`, `CheckPasswd`, `getVFS`, `Stat`, `ChangeDir`, `ListDir`, `DeleteDir`, `DeleteFile`, `Rename`, `MakeDir`, `GetFile`, and `PutFile`. `FileInfo` supplies owner/group/mode/modtime.

## Control Flow

Command or RC setup creates either a global VFS or an auth-proxy-backed per-user VFS. The FTP server parses listen address and passive port range, configures TLS if a key is set, and delegates operations to VFS. Reads open VFS files and seek offsets; writes either replace/create or append/overwrite from an offset.

## State and Persistence Behavior

State is in memory: global VFS, proxy object, cached obscured passwords by user, TLS flag, and server instance. FTP writes mutate the served remote through VFS.

## Dependencies and Integration Points

It integrates Cobra, RC, VFS flags, proxy auth, goftp server interfaces, rclone accounting/logging, obscure password storage, and filesystem user/group lookup.

## Risks and Test Signals

Risks include plain FTP exposure, passive-port misconfiguration, offset upload semantics, password cache lifetime, TLS requiring both cert/key, `Addr` synthesis not reflecting a dynamic `:0` listener, and global `proxy.Opt` use. Tests run generic FTP backend serve tests and RC creation on supported platforms.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/ftp/ftp.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/ftp/ftp_test.go -->
# sources/user-network-fs/rclone/cmd/serve/ftp/ftp_test.go

## Purpose

This file runs rclone's generic serve tests against the FTP server.

## Important APIs, Types, and Functions

`TestFTP` defines a `start` callback for `servetest.Run`. `TestRc` verifies RC startup for FTP.

## Control Flow

The start callback configures listen host/port, passive port range, user, and password, creates a server, runs it in a goroutine, and returns a backend config for the FTP remote plus a shutdown function.

## State and Persistence Behavior

The test uses local backend fixtures managed by `servetest` and a live FTP listener on a fixed localhost port. It mutates whatever test remote `servetest` prepares.

## Dependencies and Integration Points

Build tags exclude Windows, Darwin, and Plan 9. It depends on local backend, proxy defaults, obscure password config, race-detector detection, and the generic serve test harness.

## Risks and Test Signals

The fixed port can conflict locally. Race detector skips RC due to upstream library races. Coverage is broad through generic backend tests but does not directly test TLS, auth proxy, invalid passive port parsing, or upload offsets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/ftp/ftp_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/ftp/ftp_unsupported.go -->
# sources/user-network-fs/rclone/cmd/serve/ftp/ftp_unsupported.go

## Purpose

This Plan 9 fallback prevents package build errors where FTP serving is unsupported.

## Important APIs, Types, and Functions

It defines `var Command *cobra.Command` as nil.

## Control Flow

No command is registered from this file. The nil command marks the feature unavailable on Plan 9.

## State and Persistence Behavior

No state is stored.

## Dependencies and Integration Points

The build tag is `plan9`. It imports Cobra only for the command type.

## Risks and Test Signals

The main risk is callers assuming `ftp.Command` is non-nil on all platforms. Platform compile coverage is the test signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/ftp/ftp_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/http/http.go -->
# sources/user-network-fs/rclone/cmd/serve/http/http.go

## Purpose

`http.go` implements `rclone serve http`, serving a VFS-backed remote as directory listings, files, ranged downloads, favicon responses, and optional zip archives.

## Important APIs, Types, and Functions

Options are composed from `lib/http` config, auth config, template config, and `DisableZip`. Main APIs are `Command`, `newServer`, `Serve`, `Addr`, `Shutdown`, `getVFS`, `auth`, `serveFavicon`, `handler`, `serveDir`, and `serveFile`.

## Control Flow

Command/RC setup builds either a global VFS or auth-proxy custom auth. `newServer` creates a shared libhttp server, installs compression and headers, and routes favicon, GET, and HEAD requests. Directory requests can stream zip output or render a templated listing. File requests stat a VFS node, set content length/type/Last-Modified, handle HEAD, open the file, account transfer, and use `http.ServeContent` for known-size objects.

## State and Persistence Behavior

The HTTP server stores VFS/proxy/server/options in memory. Served remote content may be read or zipped; this command does not modify content.

## Dependencies and Integration Points

It integrates Cobra, RC, lib/http server/auth/templates, chi middleware, VFS, proxy auth, accounting, embedded favicon data, systemd notification, and generic directory rendering helpers.

## Risks and Test Signals

Risks include auth proxy context value type errors, directory zip resource use, unknown-size range rejection, filter interactions, MIME fallback behavior, and global `vfscommon.Opt.NoModTime` in directory rendering. Tests cover GET/HEAD/POST behavior, hidden filters, ranges, zip golden files, favicon fallback/override, gzip compression, auth proxy, and RC.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/http/http.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/http/http_test.go -->
# sources/user-network-fs/rclone/cmd/serve/http/http_test.go

## Purpose

This file regression-tests the HTTP server against golden directory listings, file bodies, ranges, zip downloads, favicon behavior, compression, auth proxy, and RC setup.

## Important APIs, Types, and Functions

Helpers include `start`, `setAllModTimes`, `checkGolden`, and `testGET`. Tests include `TestGET`, `TestAuthProxy`, `TestFavicon`, `TestCompressedDirectoryListing`, `TestCompressedTextFile`, and `TestRc`.

## Control Flow

The main GET test configures filters, starts a local server with basic auth or proxy auth, sends requests with expected methods/ranges, validates status and Last-Modified headers, and compares bodies to golden files. Favicon tests verify embedded fallback and remote override. Compression tests request gzip and decompress the response.

## State and Persistence Behavior

Tests mutate fixture file mtimes and optionally update golden files when `-updategolden` is set. Servers and temp proxy processes are scoped to tests.

## Dependencies and Integration Points

They depend on local backend, filter config, lib/http defaults, proxy test code, VFS defaults, golden files, and `servetest.TestRc`.

## Risks and Test Signals

Golden files give strong regression coverage but can be brittle across template changes. Coverage includes many user-visible paths; residual gaps include unknown-size objects, zip errors during streaming, custom template parsing failures, and concurrent shutdown.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/http/http_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/nfs/cache.go -->
# sources/user-network-fs/rclone/cmd/serve/nfs/cache.go

## Purpose

`cache.go` implements NFS file-handle cache selection, path rewriting for subpath mounts, disk-backed handle storage, metadata handle suffixing, and stale-handle handling.

## Important APIs, Types, and Functions

`Cache` defines `ToHandle`, `FromHandle`, `InvalidateHandle`, and `HandleLimit`. `Handler.getCache` selects memory, disk, or symlink cache. `pathRewriter` normalizes subpath mount handles to root-VFS absolute paths. `diskHandler` stores hash-to-path mappings and handles metadata suffixes. Helpers include `newDiskHandler`, `hashPath`, `handleToPath`, `isMetadataFile`, `isMetadataHandle`, and disk read/write/remove/suffix methods.

## Control Flow

Disk handles are MD5 hashes of cleaned full paths, stored under a sharded cache directory. Metadata files use the underlying file handle plus a four-byte suffix. `FromHandle` removes and validates suffixes, reads the mapped path, appends metadata extension if needed, and returns the root billy filesystem plus split path. Invalid or missing mappings become NFS stale handle errors.

## State and Persistence Behavior

Memory cache state is process-only. Disk and symlink caches persist mappings under the configured cache dir. Mutexes protect disk cache operations.

## Dependencies and Integration Points

It integrates go-nfs handle APIs, rclone VFS metadata extension, rclone cache dir/config string, OS path encoding, and Linux symlink cache extension.

## Risks and Test Signals

Risks include MD5 path collisions, stale cache entries after rename/delete failures, metadata suffix length constraints required by Linux NFS clients, cache-dir permissions, and subpath handle consistency. `cache_test.go` covers CRUD, stale handles, concurrency for disk/symlink caches, metadata handles, and subpath handle stability.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/nfs/cache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/nfs/cache_test.go -->
# sources/user-network-fs/rclone/cmd/serve/nfs/cache_test.go

## Purpose

This file tests NFS handle cache backends and the subpath path-rewriter behavior.

## Important APIs, Types, and Functions

Helpers are `testCacheCRUD`, `testCacheThrashDifferent`, and `testCacheThrashSame`. Tests are `TestCache` and `TestPathRewriterHandleStability`.

## Control Flow

For each cache type, tests create a handler with memory-object VFS and temp cache dir, skip symlink cache when unsupported or permission-limited, then verify missing handles, handle creation/readback, invalidation, repeated invalidation, stale-handle behavior, parallel operations, and metadata suffix behavior. Path-rewriter tests compare handles minted from root and subpath FS views.

## State and Persistence Behavior

Disk/symlink tests write into temp cache directories. The test quiets log level temporarily to avoid expected stale-handle noise.

## Dependencies and Integration Points

It depends on object memory Fs, VFS metadata extension, cache selection, and optional Linux `CAP_DAC_READ_SEARCH` for symlink cache.

## Risks and Test Signals

The tests are strong for cache correctness and recent subpath stability. Memory cache is explicitly not concurrency-tested because the upstream caching handler is not thread-safe. Real NFS client behavior is tested elsewhere.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/nfs/cache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/nfs/filesystem.go -->
# sources/user-network-fs/rclone/cmd/serve/nfs/filesystem.go

## Purpose

`filesystem.go` adapts rclone VFS to the `go-billy` filesystem interfaces consumed by go-nfs.

## Important APIs, Types, and Functions

`FS` stores a VFS pointer and optional rooted subpath. It implements `ReadDir`, `Create`, `Open`, `OpenFile`, `Stat`, `Rename`, `Remove`, `Join`, `TempFile`, `MkdirAll`, `Lstat`, `Symlink`, `Readlink`, `Chmod`, `Lchown`, `Chown`, `Chtimes`, `Chroot`, `Root`, and `Capabilities`. `setSys` attaches go-nfs `file.FileInfo` ownership and inode metadata to VFS nodes.

## Control Flow

Each method rewrites relative names through `fullPath`, traces the operation, then delegates to VFS. Directory and stat paths call `setSys` so NFS sees UID, GID, nlink, and file IDs. `MkdirAll` manually creates missing path prefixes to preserve permissions.

## State and Persistence Behavior

FS state is a view over a shared VFS and optional root. Write methods mutate the served remote through VFS. `setSys` mutates per-node Sys metadata.

## Dependencies and Integration Points

It integrates go-billy, go-nfs file metadata, rclone VFS, VFS cache mode, and subpath mount handling from `handler.go`.

## Risks and Test Signals

Risks include path.Join behavior for absolute/empty paths, partial `MkdirAll` behavior, masking `Chmod` ENOSYS, file close logging format, capability reporting based on cache mode, and subpath escape assumptions. Handler tests exercise subpath reads/writes and root visibility.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/nfs/filesystem.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/nfs/handler.go -->
# sources/user-network-fs/rclone/cmd/serve/nfs/handler.go

## Purpose

`handler.go` builds the go-nfs handler around rclone VFS, mount-path validation, handle-cache delegation, filesystem stats, and log bridging.

## Important APIs, Types, and Functions

`Handler` stores VFS, options, root `FS`, and `Cache`. `NewHandler`, `Mount`, `Change`, `FSStat`, `ToHandle`, `FromHandle`, `HandleLimit`, `InvalidateHandle`, and `Options.Limit` are core APIs. Logger methods implement go-nfs logging with rclone log levels. `OnUnmountFunc` and `onUnmount` provide external unmount signaling.

## Control Flow

`NewHandler` initializes cache and maps rclone log level to go-nfs level. `Mount` cleans requested dirpath under `/`, returns root FS for `/`, otherwise stats the target and only accepts plain directories, returning a sub-rooted FS. Handle methods delegate to cache with tracing. Logger `Tracef` detects `mount.Umnt` text to call unmount hooks.

## State and Persistence Behavior

Handler state is in memory; cache backend may persist separately. Subpath mounts share one root VFS and cache so handles stay stable.

## Dependencies and Integration Points

It integrates go-nfs mount/handler interfaces, go-billy, VFS statfs, rclone config logging, and cache implementations.

## Risks and Test Signals

Risks include text-based unmount detection, unauthenticated mount access, subpath mounts not isolating siblings/parents, and returning root FS even on mount rejection because go-nfs still needs a non-nil FS. Handler tests cover root/subpath/rejection/write/handle stability.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/nfs/handler.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/nfs/handler_test.go -->
# sources/user-network-fs/rclone/cmd/serve/nfs/handler_test.go

## Purpose

This file tests NFS mount-path handling and subpath filesystem behavior.

## Important APIs, Types, and Functions

`newTestHandler` builds a local VFS with `/sub`, `/sub/nested`, and `/sub/hello.txt`. Tests include root mount, subpath mount, rejected mounts, subpath writes, and handle stability.

## Control Flow

Tests call `Handler.Mount` with raw dirpaths, inspect returned `*FS` roots, list subpath contents, write through a subpath FS, verify the write lands under the absolute VFS path, and compare root/subpath NFS handles.

## State and Persistence Behavior

Each test uses a temp local filesystem with VFS cache mode full and shuts down VFS at cleanup.

## Dependencies and Integration Points

It depends on local backend, VFS, go-nfs mount request/status types, and the cache path-rewriter.

## Risks and Test Signals

These tests directly protect traversal normalization, non-directory rejection, non-nil rejected FS behavior, and subpath handle identity. They do not run a full network NFS client.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/nfs/handler_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/nfs/nfs.go -->
# sources/user-network-fs/rclone/cmd/serve/nfs/nfs.go

## Purpose

`nfs.go` registers `rclone serve nfs`, its RC entrypoint, options, cache enum, help text, and command runner for Unix builds.

## Important APIs, Types, and Functions

`OptionsInfo`, `handleCache`, `handleCacheChoices`, `Options`, global `Opt`, `AddFlags`, `Run`, and Cobra `Command` define the public command surface. Cache choices are memory, disk, and symlink.

## Control Flow

Initialization registers global options, adds VFS/NFS flags, registers the command, and installs RC serving. `Run` builds an Fs and VFS, creates an NFS server, and serves. Help text documents default localhost random-port behavior, no authentication, write-cache requirements, cache types, subpath mounts, and metadata handles.

## State and Persistence Behavior

Command state is in global options. Runtime server/cache state is handled by `server.go`, `handler.go`, and `cache.go`; disk/symlink cache options can persist handle mappings.

## Dependencies and Integration Points

It integrates Cobra, RC, rclone VFS, configstruct option parsing, and the Unix-only NFS server implementation.

## Risks and Test Signals

The command intentionally has no authentication and must default to localhost. Documentation says metadata suffix applies to `disk` and `cache`, likely intending `disk` and `symlink`. RC creation is tested in `nfs_test.go`; mount behavior is tested in handler/cache tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/nfs/nfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/nfs/nfs_test.go -->
# sources/user-network-fs/rclone/cmd/serve/nfs/nfs_test.go

## Purpose

This small Unix-only test verifies that NFS can be started through rclone's generic RC serve mechanism.

## Important APIs, Types, and Functions

`TestRc` calls `servetest.TestRc` with `type: nfs` and `vfs_cache_mode: off`.

## Control Flow

The serve test harness creates the service through RC parameters and validates the standard serve handle behavior.

## State and Persistence Behavior

The test relies on harness-managed temporary state and does not persist NFS cache state directly.

## Dependencies and Integration Points

It depends on the local backend, `servetest`, RC params, and Unix build tag.

## Risks and Test Signals

It is a smoke test only. Actual NFS protocol behavior is covered by cache/handler tests here and more complete serving tests referenced in `cmd/nfsmount`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/nfs/nfs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/nfs/nfs_unsupported.go -->
# sources/user-network-fs/rclone/cmd/serve/nfs/nfs_unsupported.go

## Purpose

This fallback keeps the NFS package buildable on non-Unix platforms.

## Important APIs, Types, and Functions

It defines `var Command *cobra.Command` as nil.

## Control Flow

No NFS command is registered from this file.

## State and Persistence Behavior

No state is stored.

## Dependencies and Integration Points

The build tag is `!unix`. Callers must tolerate the command being unavailable.

## Risks and Test Signals

The risk is platform-specific command registration assumptions. Cross-platform build coverage is the main signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/nfs/nfs_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/nfs/server.go -->
# sources/user-network-fs/rclone/cmd/serve/nfs/server.go

## Purpose

`server.go` owns the listening NFS server wrapper around go-nfs.

## Important APIs, Types, and Functions

`Server` stores options, handler, context, listener, and an `UnmountedExternally` flag. `NewServer`, `Addr`, `Shutdown`, and `Serve` are the public methods.

## Control Flow

`NewServer` warns when VFS cache mode is off, defaults an empty listen address to `localhost:`, creates a handler, binds a TCP listener, and returns the server. `Serve` logs the address and calls `nfs.Serve`; `Shutdown` closes the listener.

## State and Persistence Behavior

Server state is in memory. No persistent state is written here; handle cache persistence belongs to cache backends.

## Dependencies and Integration Points

It integrates rclone VFS, VFS cache mode, `NewHandler`, TCP networking, and the go-nfs serving loop.

## Risks and Test Signals

Risks include no authentication, listener-close shutdown semantics, writes being read-only without VFS cache, and go-nfs Serve error propagation. RC and handler tests cover construction paths but not a full client mount in this package.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/nfs/server.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/nfs/symlink_cache_linux.go -->
# sources/user-network-fs/rclone/cmd/serve/nfs/symlink_cache_linux.go

## Purpose

This Linux-only file upgrades the disk NFS handle cache to a symlink-backed cache using kernel file handles for faster lookup.

## Important APIs, Types, and Functions

`makeSymlinkCache` self-tests symlink write/read and installs symlink methods. Helpers include `addLengthPrefix`, `removeLengthPrefix`, `symlinkCacheWrite`, `symlinkCacheRead`, `symlinkCacheRemove`, and `symlinkCacheSuffix`. Constants `emptyPath` and `emptyPathBytes` represent empty symlink targets.

## Control Flow

Writing creates a symlink at the cache path pointing to the full VFS path, obtains the symlink's kernel file handle with `NameToHandleAt`, prefixes its length, and returns that as the NFS handle. Reading removes the prefix, opens by handle with `OpenByHandleAt`, reads the symlink target with `Readlinkat`, and restores empty-path substitution. Removal reads the target, rehashes it, and deletes the real cache symlink.

## State and Persistence Behavior

Cache entries are symlinks on disk. Handles depend on filesystem-native file handles, so backup/restore can break mappings. `handleType` is stored in the `diskHandler`.

## Dependencies and Integration Points

It depends on Linux `name_to_handle_at`, `open_by_handle_at`, `CAP_DAC_READ_SEARCH`, symlink semantics, and the disk handler hooks.

## Risks and Test Signals

Risks include permission failures, handle invalidation after filesystem restore, symlink target truncation at 1024 bytes, file-handle length validation, and close-error handling in the deferred close block. Cache tests exercise this backend when capabilities are available and skip with explicit errors otherwise.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/nfs/symlink_cache_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/nfs/symlink_cache_other.go -->
# sources/user-network-fs/rclone/cmd/serve/nfs/symlink_cache_other.go

## Purpose

This Unix non-Linux fallback reports that the symlink NFS handle cache is unsupported.

## Important APIs, Types, and Functions

`makeSymlinkCache` returns `ErrorSymlinkCacheNotSupported`.

## Control Flow

The disk handler remains unmodified, and cache selection fails for `--nfs-cache-type symlink` on non-Linux Unix systems.

## State and Persistence Behavior

No state is written.

## Dependencies and Integration Points

Build tags are `unix && !linux`. `Handler.getCache` surfaces this error, and tests skip symlink-cache cases when it appears.

## Risks and Test Signals

The fallback is clear and intentional. Cross-platform build and skip behavior in `cache_test.go` are the relevant signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/nfs/symlink_cache_other.go -->
