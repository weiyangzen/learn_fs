# subset-b-009145 research

Grouped research report for Kopia notification senders and repository blob storage files. Each section preserves the exact source path and is wrapped for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/notification/sender/email/email_sender.go -->
# sources/sync-backup/kopia/notification/sender/email/email_sender.go

Purpose: implements the registered `email` notification provider. It turns a `sender.Message` into an SMTP message, optionally authenticates with `smtp.PlainAuth`, adds HTML MIME headers when the configured format is `html`, copies message headers, and sends through `smtp.SendMail`.

Important APIs/types/functions: `ProviderType`, `defaultSMTPPort`, `emailProvider`, `Send`, `Summary`, `Format`, and the package `init` registration with `sender.Register`. `Send` depends on `sender.Message`, `net/smtp`, CRLF header/body joining, and comma-splitting the configured recipient list.

Control flow: construction is indirect through the sender registry. `init` validates `Options`, stores a copy in `emailProvider`, and returns it. A send call builds auth only when `SMTPUsername` is present, assembles mandatory headers, adds MIME headers for HTML bodies, appends message headers, joins with `\r\n`, and calls `smtp.SendMail` with `server:port`, from address, parsed recipients, and payload.

State and persistence behavior: the provider is stateless after construction except for copied options. No message history is retained and no durable state is written. SMTP side effects are external delivery attempts.

Dependencies/integration points: integrates with the notification sender registry, `sender.FormatHTML`, and SMTP servers. Risks include unsorted custom header order, no escaping/sanitization of header values, unused `CC` in delivery, and reliance on `smtp.SendMail` without context cancellation. Test signals come from the email sender tests covering HTML/plain payloads, summary text, auth failure, invalid options, and option merging.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/notification/sender/email/email_sender.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/notification/sender/email/email_sender_options.go -->
# sources/sync-backup/kopia/notification/sender/email/email_sender_options.go

Purpose: defines configuration and merge/default behavior for the email notification provider.

Important APIs/types/functions: `Options` contains SMTP server, port, identity, username/password, sender/recipient fields, CC, and format. `MergeOptions` overlays source values onto a destination, `ApplyDefaultsAndValidate` fills default port/format and enforces required fields, and `copyOrMerge` implements create-vs-update semantics for comparable fields.

Control flow: `MergeOptions` copies every field when creating a configuration, but during update only non-zero source values replace destination values. It then validates the merged result. Validation defaults port to `587`, requires SMTP server, from address, and to address, then calls `sender.ValidateMessageFormatAndSetDefault` with default `html`.

State and persistence behavior: this file only mutates the passed `Options` value. Password is marked sensitive for Kopia serialization. The struct is the persistent JSON shape used by method configuration and must remain backward compatible.

Dependencies/integration points: used by `email_sender.go`, CLI/profile merge paths, and sender registry JSON unmarshalling. Risks include inability to clear a field during update because zero values are ignored, the misleading comment that format can be `md` while validation accepts `txt`/`html`, and `CC` being merged/validated but not used by the sender. Tests cover required-field failures, defaults, and update merge behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/notification/sender/email/email_sender_options.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/notification/sender/email/email_sender_test.go -->
# sources/sync-backup/kopia/notification/sender/email/email_sender_test.go

Purpose: unit tests for the email provider's SMTP payload construction, option validation, authentication path, and merge semantics.

Important APIs/types/functions: `TestEmailProvider`, `TestEmailProvider_Text`, `TestEmailProvider_AUTH`, `TestEmailProvider_Invalid`, and `TestMergeOptions`. The tests use `go-smtp-mock`, `sender.GetSender`, `email.Options`, `testlogging.Context`, and `require`.

Control flow: the HTML and plain-text tests start a mock SMTP server, create a sender through the registry, send a multiline message with an extra header, wait until the mock receives one message, and compare the exact SMTP request text. The auth test configures username/password against a mock server without AUTH support and asserts the SMTP error. Invalid tests try incomplete option sets and assert wrapped validation messages. Merge tests exercise create and update modes.

State and persistence behavior: state is limited to mock server messages and a mutable destination options struct. No real email is sent.

Dependencies/integration points: validates the sender registry, SMTP formatting, HTML MIME header insertion, default format/port application, and option merge behavior. Risks/test gaps include no test for multiple comma-separated recipients, `CC`, header ordering with more than one map entry, context cancellation, or successful AUTH against an AUTH-capable server. The exact-payload comparisons are strong regression signals for CRLF and header layout.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/notification/sender/email/email_sender_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/notification/sender/jsonsender/jsonsender.go -->
# sources/sync-backup/kopia/notification/sender/jsonsender/jsonsender.go

Purpose: provides a lightweight notification sender that serializes accepted messages as JSON lines to an `io.Writer`, optionally prefixed for log scanning.

Important APIs/types/functions: `jsonSender`, `Send`, `Summary`, `Format`, `ProfileName`, and `NewJSONSender`. The provider implements `sender.Sender` directly rather than registering as a profile method. It filters by `minSeverity` and encodes `sender.Message` with `encoding/json`.

Control flow: `NewJSONSender` captures prefix, writer, and minimum severity. `Send` returns immediately when `msg.Severity` is below the threshold. Otherwise it writes the prefix to a buffer, JSON-encodes the message with a newline, then writes the whole buffer to the configured writer. `Format` reports plain text because the sender is typically used for machine-readable notification output, not rendered HTML.

State and persistence behavior: no internal durable state is maintained. Persistence depends on the supplied writer; writes are not synchronized, so concurrent callers need an externally safe writer.

Dependencies/integration points: used by notification/reporting code that wants structured output instead of HTTP/SMTP delivery. Risks include partial writer errors being returned without retry, no locking around writes, and the fixed profile name `jsonsender`. The test verifies severity filtering and exact line output.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/notification/sender/jsonsender/jsonsender.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/notification/sender/jsonsender/jsonsender_test.go -->
# sources/sync-backup/kopia/notification/sender/jsonsender/jsonsender_test.go

Purpose: verifies JSON sender severity filtering and output format.

Important APIs/types/functions: `TestJSONSender`, `jsonsender.NewJSONSender`, `notification.SeverityWarning`, `sender.Message`, and a `bytes.Buffer` output sink.

Control flow: the test creates a JSON sender with prefix `NOTIFICATION:` and warning threshold, sends verbose, warning, and error messages, trims/splits the buffer by newline, and asserts only warning/error messages were encoded as prefixed JSON.

State and persistence behavior: all state is in the local buffer. The ignored low-severity message confirms no output side effect for filtered messages.

Dependencies/integration points: exercises the JSON serialization shape of `sender.Message` and the severity constants from the higher-level notification package. Risks/test gaps include no writer-error coverage, no concurrent send coverage, and no message headers in the encoded samples. The exact expected JSON strings are useful signals for field names and omitted empty fields.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/notification/sender/jsonsender/jsonsender_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/notification/sender/notification_message.go -->
# sources/sync-backup/kopia/notification/sender/notification_message.go

Purpose: defines the common notification message model and parsing/format validation helpers shared by all senders.

Important APIs/types/functions: `Severity`, `Message`, `ParseMessage`, `Message.ToString`, `FormatPlainText`, `FormatHTML`, and `ValidateMessageFormatAndSetDefault`. `Message` carries subject, optional headers, severity, and body.

Control flow: `ParseMessage` scans header lines until a blank line, special-cases `Subject:`, parses other `key: value` headers, warns and skips malformed header lines, then joins the remaining lines as the body. It errors if no body lines are found and wraps scanner errors. `ToString` writes the subject, sorts header keys for deterministic output, emits a blank line, and appends the body. Format validation accepts `txt` or `html`, fills a provided default when empty, and rejects any other value.

State and persistence behavior: all operations are in-memory. The string representation can be used as a stable serialized template form, but it is not JSON persistence.

Dependencies/integration points: consumed by SMTP, webhook, pushover, JSON, and test senders. Risks include simple colon parsing, no folded/multiline header support, malformed header lines only logging warnings, and format comments elsewhere mentioning markdown even though validation accepts text/html. Tests cover parsing, no-body errors, deterministic string round trip, and format defaults/errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/notification/sender/notification_message.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/notification/sender/notification_message_test.go -->
# sources/sync-backup/kopia/notification/sender/notification_message_test.go

Purpose: tests the common message parser, serializer, and format validator.

Important APIs/types/functions: `TestParseMessage`, `TestParseMessageNoBody`, `TestToString`, and `TestValidateMessageFormatAndSetDefault`.

Control flow: parse tests feed a subject, valid headers, one invalid header line, a blank separator, and body text; they assert subject/body/header extraction and then round-trip through `ToString` and `ParseMessage`. The no-body test confirms a header-only template is rejected. `TestToString` asserts sorted header order in the rendered form. The format test checks default assignment, `txt`, `html`, and an invalid value.

State and persistence behavior: only in-memory strings/readers are used. Deterministic header ordering is the key persistence-like signal because templates can round-trip consistently.

Dependencies/integration points: validates behavior relied on by all notification senders and template pipelines. Risks/test gaps include duplicated test case name/content, no scanner error simulation, no severity JSON behavior, and no tests for headers containing additional colons beyond the first split. The tests strongly pin accepted formats and the no-body invariant.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/notification/sender/notification_message_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/notification/sender/pushover/pushover_sender.go -->
# sources/sync-backup/kopia/notification/sender/pushover/pushover_sender.go

Purpose: implements the registered `pushover` notification provider by POSTing JSON payloads to the Pushover API or a test override endpoint.

Important APIs/types/functions: `ProviderType`, `defaultPushoverURL`, `pushoverProvider`, `Send`, `Summary`, `Format`, and registry `init`. `Send` combines subject and body into Pushover's `message` field and adds `"html": "1"` for HTML format.

Control flow: construction validates options through `ApplyDefaultsAndValidate`. A send call builds a `map[string]string` with token, user, and message, selects either the default API URL or configured endpoint, marshals JSON, creates a context-aware POST request, sets `Content-Type: application/json`, sends via `http.DefaultClient`, and requires HTTP 200.

State and persistence behavior: no state is mutated after construction. Side effects are external HTTP requests; no retry or message persistence is performed.

Dependencies/integration points: plugs into `sender.GetSender`, depends on Pushover's HTTP API contract, and shares message format constants. Risks include using the default HTTP client without custom timeouts, accepting only status 200, not reading error body details, and no support for Pushover priorities/devices. Tests cover plain and HTML JSON payloads, endpoint override, HTTP status failure, connection failure, required options, and merge behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/notification/sender/pushover/pushover_sender.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/notification/sender/pushover/pushover_sender_options.go -->
# sources/sync-backup/kopia/notification/sender/pushover/pushover_sender_options.go

Purpose: defines Pushover provider configuration and update semantics.

Important APIs/types/functions: `Options` contains app token, user key, body format, and an optional endpoint override. `ApplyDefaultsAndValidate` enforces credentials and defaults the format to plain text. `MergeOptions` overlays app token and user key only; `copyOrMerge` implements create/update behavior.

Control flow: validation fails when `AppToken` or `UserKey` is empty, then delegates format validation to `sender.ValidateMessageFormatAndSetDefault` with default `txt`. Merge copies non-zero values during update and all values during create, then validates the destination.

State and persistence behavior: this is the JSON-persisted sender configuration. Tokens are not marked `kopia:"sensitive"` in this file, which is notable compared with other credential structs.

Dependencies/integration points: consumed by `pushover_sender.go` registration and profile update commands. Risks include `MergeOptions` not merging `Format` or `Endpoint`, so updates cannot change those via this helper, and comments again mention markdown while validation allows only text/html. Tests cover credentials/defaults indirectly, but do not expose the missing `Format`/`Endpoint` merge behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/notification/sender/pushover/pushover_sender_options.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/notification/sender/pushover/pushover_sender_test.go -->
# sources/sync-backup/kopia/notification/sender/pushover/pushover_sender_test.go

Purpose: tests Pushover HTTP payloads, error handling, validation, and merge behavior.

Important APIs/types/functions: `TestPushover`, `TestPushover_Invalid`, and `TestMergeOptions`, using `httptest.Server`, `sender.GetSender`, and `pushover.Options`.

Control flow: the main test records requests and bodies from a local server, creates plain and HTML senders, sends two messages, decodes JSON bodies, and asserts token/user/message/html fields. It then exercises non-OK HTTP status and connection failure paths. The invalid test asserts missing token and user key validation. Merge tests verify create and update replacement for app token/user key.

State and persistence behavior: request capture buffers act as test state; no external Pushover service is contacted.

Dependencies/integration points: validates registry construction, endpoint override, JSON body construction, and HTTP response handling. Risks/test gaps include no coverage of real default endpoint, context cancellation, non-JSON marshal failures, custom format update, endpoint merge behavior, or Pushover-specific response bodies. The tests provide strong signals for the current minimal API contract.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/notification/sender/pushover/pushover_sender_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/notification/sender/sender.go -->
# sources/sync-backup/kopia/notification/sender/sender.go

Purpose: defines the notification sender/provider abstraction and generic registry used by concrete senders.

Important APIs/types/functions: `Provider`, `Sender`, `Factory`, global `allSenders` and `defaultOptions`, `senderWrapper`, `GetSender`, and generic `Register`. A provider sends messages, reports body format support, and summarizes configuration; a sender also exposes a profile name.

Control flow: provider packages call `Register` in `init`, passing typed options and factory functions. `Register` stores a default zero-value options instance and wraps the typed factory in JSON marshal/unmarshal conversion from arbitrary config. `GetSender` looks up the method, invokes the factory, wraps errors, and returns a `senderWrapper` that adds the requested profile name.

State and persistence behavior: registry maps are process-global and mutated during package initialization. No locking is used, so registration is assumed to happen before concurrent use. Persistent config is handled through JSON round-tripping into registered option types.

Dependencies/integration points: central integration point for email, webhook, pushover, testsender, and method config unmarshalling. Risks include runtime panics if registration races, loss of type fidelity through JSON conversion, and unknown-sender errors when provider packages are not imported. Tests are indirect through provider-specific `GetSender` calls and config tests elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/notification/sender/sender.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/notification/sender/sender_config.go -->
# sources/sync-backup/kopia/notification/sender/sender_config.go

Purpose: provides JSON serialization/deserialization for configured notification methods.

Important APIs/types/functions: `Method`, `MethodConfig`, `UnmarshalJSON`, `Options`, and `MarshalJSON`. The JSON shape is `{type, config}` and `config` is decoded according to the registered sender type.

Control flow: `UnmarshalJSON` first decodes raw type and raw config, verifies a sender factory exists in `allSenders`, seeds `Config` from `defaultOptions[type]`, then unmarshals the raw config into that typed value. `Options` re-marshals the stored config into a caller-provided result type. `MarshalJSON` emits the type and config as-is.

State and persistence behavior: this is a persistent profile configuration boundary. Compatibility depends on stable method names and option struct JSON tags. It does not itself validate provider options beyond requiring registration and JSON decodability.

Dependencies/integration points: tightly coupled to `sender.Register` and global default options. Risks include pointer/value subtleties because `defaultOptions` stores a zero value, not a pointer, and unknown sender types fail during unmarshal. Test signals are mostly indirect via provider tests; the file has no dedicated test in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/notification/sender/sender_config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/notification/sender/testsender/test_sender.go -->
# sources/sync-backup/kopia/notification/sender/testsender/test_sender.go

Purpose: provides a registered in-memory notification provider for tests and internal capture flows.

Important APIs/types/functions: `ProviderType`, context key types, `CaptureMessages`, `CaptureMessagesWithHandler`, `MessagesInContext`, `testSenderProvider`, `Send`, `Summary`, `Format`, and registry `init`.

Control flow: capture helpers attach a `capturedMessages` object to context. The default handler appends message pointers; the custom handler delegates to caller code. `Send` locks the provider mutex, extracts capture state from the context, errors when missing, and calls the handler. Construction validates `Options` and stores them.

State and persistence behavior: captured messages live in the context value and are not durable. The provider has a mutex, but the `capturedMessages.messages` slice itself is protected only when accessed through provider `Send`; external reads via `MessagesInContext` are unsynchronized.

Dependencies/integration points: used by notification tests and code that wants to observe sends without network side effects. Risks include context-key coupling, ignored errors in tests if callers do not assert `Send`, and returning message pointers rather than copies. Tests cover capture and missing-context behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/notification/sender/testsender/test_sender.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/notification/sender/testsender/test_sender_options.go -->
# sources/sync-backup/kopia/notification/sender/testsender/test_sender_options.go

Purpose: defines options for the in-memory test notification sender.

Important APIs/types/functions: `Options` has `Format` and an `Invalid` flag used to force construction failure. `MergeOptions`, `ApplyDefaultsAndValidate`, and `copyOrMerge` mirror other sender option files.

Control flow: merge updates the destination format according to create/update semantics and validates. Validation defaults format to `html`, checks it with `sender.ValidateMessageFormatAndSetDefault`, and then returns an explicit `invalid options` error when `Invalid` is true.

State and persistence behavior: options are JSON-serializable, but this provider is test-only. The `Invalid` flag exists as a controlled failure hook rather than real persisted behavior.

Dependencies/integration points: consumed by `test_sender.go` registration and any tests that need sender creation failure. Risks include the comment saying email provider options and markdown support, both copy/paste artifacts; merge does not copy `Invalid`, so update/create through `MergeOptions` cannot set that failure flag. Tests in this subset cover default creation behavior but not `Invalid` or merge directly.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/notification/sender/testsender/test_sender_options.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/notification/sender/testsender/test_sender_test.go -->
# sources/sync-backup/kopia/notification/sender/testsender/test_sender_test.go

Purpose: validates the test sender's context capture behavior.

Important APIs/types/functions: `TestProvider`, `TestProvider_NotConfigured`, `testsender.CaptureMessages`, `testsender.MessagesInContext`, `sender.GetSender`, and `testsender.Options`.

Control flow: `TestProvider` adds capture state to the test context, constructs a `testsender`, sends three message pointers, then asserts the context contains those messages. `TestProvider_NotConfigured` intentionally skips capture setup, sends one message, and asserts no messages are visible in context.

State and persistence behavior: captured state is context-local and in-memory. No durable files or network calls are made.

Dependencies/integration points: exercises registry construction and context-based capture. Risks/test gaps include `TestProvider_NotConfigured` does not assert the `Send` error, so it only verifies absence of captured state, not the explicit `test sender not configured` contract. There is no coverage for custom handlers, handler errors, `Invalid` options, or concurrent sends.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/notification/sender/testsender/test_sender_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/notification/sender/webhook/webhook_sender.go -->
# sources/sync-backup/kopia/notification/sender/webhook/webhook_sender.go

Purpose: implements the registered generic HTTP webhook notification provider.

Important APIs/types/functions: `ProviderType`, `webhookProvider`, `Send`, `Summary`, `Format`, and registry `init`. It sends the message body as the request body, subject as a header, option headers from newline-separated `key: value` lines, and message headers as overrides/additions.

Control flow: construction validates endpoint/method/format. `Send` creates a context-aware request using configured method and endpoint, sets `Subject`, parses configured headers line by line, copies message headers, sends with `http.DefaultClient`, closes the response body, and treats any status other than 200 as an error.

State and persistence behavior: stateless after option capture. Side effects are external HTTP requests only; there is no retry, queueing, or durable delivery state.

Dependencies/integration points: integrates with the sender registry and generic HTTP receivers. Risks include no custom timeout/client, no content type default except what the caller supplies, accepting invalid HTTP methods until send time, ignoring malformed configured header lines, and requiring exactly 200 rather than all 2xx. Tests cover headers, methods, formats, status/connection failures, invalid URL/scheme, invalid method at send time, summary, and merge behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/notification/sender/webhook/webhook_sender.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/notification/sender/webhook/webhook_sender_options.go -->
# sources/sync-backup/kopia/notification/sender/webhook/webhook_sender_options.go

Purpose: defines webhook configuration validation and merge behavior.

Important APIs/types/functions: `Options` contains endpoint, HTTP method, format, and newline-separated headers. `ApplyDefaultsAndValidate` defaults method and format, validates endpoint URL and scheme, and `MergeOptions` overlays fields using create/update semantics.

Control flow: validation sets `POST` when method is empty, calls shared format validation with default `txt`, parses endpoint with `url.ParseRequestURI`, rejects non-HTTP(S) schemes, then redundantly checks for empty format. Merge copies endpoint, method, headers, and format, then validates the result.

State and persistence behavior: this struct is the persistent JSON profile shape for webhook sender configuration. Headers are stored as a raw text blob rather than structured key/value JSON.

Dependencies/integration points: consumed by sender registration and profile update code. Risks include method syntax not being validated until `http.NewRequestWithContext`, inability to clear a field in update mode with zero values, and unstructured headers allowing malformed lines to be silently ignored by the sender. Tests cover defaults through construction, URL/scheme validation, invalid method at send time, and merge updates.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/notification/sender/webhook/webhook_sender_options.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/notification/sender/webhook/webhook_sender_test.go -->
# sources/sync-backup/kopia/notification/sender/webhook/webhook_sender_test.go

Purpose: tests webhook request construction, validation, error paths, and option merging.

Important APIs/types/functions: `TestWebhook`, `TestWebhook_Failure`, `TestWebhook_InvalidURL`, `TestWebhook_InvalidURLScheme`, `TestWebhook_InvalidMethod`, and `TestMergeOptions`, using `httptest.Server`.

Control flow: the main test records two local HTTP requests: a POST with configured and message headers plus markdown-like body, and a PUT with HTML content type. It asserts method, subject, headers, body, summary content, and 404 error handling. Additional tests cover connection failure, bad endpoint syntax, bad scheme, and invalid method rejected during `Send`. Merge tests verify create and update modes.

State and persistence behavior: request slices and body buffers are local test state; no external webhook is contacted.

Dependencies/integration points: validates the sender registry, option validator, `http.NewRequestWithContext`, and message-header overriding behavior. Risks/test gaps include no context cancellation test, no malformed option-header line test, no multi-value header behavior, and no non-200 success variants such as 201/204. Exact body/header assertions provide good regression coverage for the current contract.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/notification/sender/webhook/webhook_sender_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/api_server_repository.go -->
# sources/sync-backup/kopia/repo/api_server_repository.go

Purpose: persists local configuration for connecting to a remote Kopia API server and verifies the connection.

Important APIs/types/functions: `APIServerInfo` and `ConnectAPIServer`. `APIServerInfo` stores base URL, trusted server certificate fingerprint, and local cache key-derivation algorithm.

Control flow: `ConnectAPIServer` builds a `LocalConfig` with API server info and client options after applying defaults labeled with the API server URL. It calls `setupCachingOptionsWithDefaults` using the config path, caching options, and API base URL as cache identity input. It writes the local config to disk, then calls `verifyConnect` with the config file and password.

State and persistence behavior: this file writes the local repository configuration file. The struct comment explicitly notes backward compatibility because the JSON may be read/written by different Kopia versions.

Dependencies/integration points: integrates with repository connect options, local config writing, cache setup, and connection verification. Risks include partial configuration write failures preventing verification, persistent schema compatibility constraints, and reliance on URL bytes for cache derivation uniqueness. Test signals are outside this subset; no direct tests are included here.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/api_server_repository.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/azure/azure_immu_test.go -->
# sources/sync-backup/kopia/repo/blob/azure/azure_immu_test.go

Purpose: integration test for Azure blob immutability retention behavior.

Important APIs/types/functions: `TestAzureStorageImmutabilityProtection`, `getBlobRetention`, and `getAzureCLI`. The test uses Azure CLI/service calls, Kopia's blob storage API, and environment-provided immutable container credentials.

Control flow: the test is skipped unless immutable Azure test variables and CLI support are available. It creates/opens Azure storage, writes blobs with retention options, verifies retention metadata through Azure APIs, extends retention, attempts deletion paths, and validates behavior expected for protected blobs.

State and persistence behavior: it mutates a real Azure container and blob retention state. Cleanup must account for immutable retention windows, so test data can persist until policies expire.

Dependencies/integration points: exercises `azure.PutBlob`, `ExtendBlobRetention`, delete-marker logic, Azure versioning/immutability APIs, and external credentials/CLI. Risks include flakiness from cloud policy propagation, clock skew around retention dates, and environment leakage. The test is a high-value signal for provider-specific retention semantics that unit tests cannot cover locally.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/azure/azure_immu_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/azure/azure_options.go -->
# sources/sync-backup/kopia/repo/blob/azure/azure_options.go

Purpose: defines JSON options for Azure Blob Storage-backed repositories.

Important APIs/types/functions: `Options` includes container, storage account/key, SAS token, prefix, TLS/storage-domain knobs, throttling limits, point-in-time view timestamp, and Azure AD credential variants: tenant/client secret, client certificate, and federated token file.

Control flow: this file has no functions; validation and client construction are in `azure_storage.go`. JSON tags and `kopia:"sensitive"` annotations drive persistent config shape and secret handling.

State and persistence behavior: the struct is serialized into `blob.ConnectionInfo` for local repository config. Fields such as `StorageKey`, `SASToken`, `ClientSecret`, `ClientCertificate`, and federated token path influence authentication without being persisted elsewhere by this file.

Dependencies/integration points: consumed by Azure storage creation, throttling wrappers, point-in-time wrappers, and CLI/config code. Risks include backward-compatibility pressure on field names, multiple mutually exclusive credential modes with validation deferred to `getAZService`, and `DoNotUseTLS` enabling insecure HTTP credentials only when client options permit it. Integration tests cover several credential variants.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/azure/azure_options.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/azure/azure_pit.go -->
# sources/sync-backup/kopia/repo/blob/azure/azure_pit.go

Purpose: implements point-in-time read-only views for Azure Blob Storage using blob version listings.

Important APIs/types/functions: `azPointInTimeStorage`, `ListBlobs`, `GetBlob`, `newestAtUnlessDeleted`, `getOlderThan`, `listBlobVersions`, `getVersionedMetadata`, `isAzureDeleteMarker`, and `maybePointInTimeStore`.

Control flow: `maybePointInTimeStore` returns the raw storage when no point-in-time is configured; otherwise it probes repository blob versions to require versioning and wraps the PIT storage in `readonly.NewWrapper`. `ListBlobs` streams all versions by prefix, groups consecutive entries by blob ID, and emits the newest version not after the PIT unless that version is a delete marker. `GetBlob` resolves version metadata at the PIT and delegates to `getBlobWithVersion`.

State and persistence behavior: the wrapper does not mutate Azure state and exposes a historical view over persisted versions. Delete-marker treatment is provider-specific: Azure may report root blobs with `HasVersionsOnly`, and the code also handles Kopia's immutability workaround marker.

Dependencies/integration points: depends on Azure list include flags for metadata, deleted versions, and versions; uses `readonly` to prevent mutation; and uses `format.KopiaRepositoryBlobID` as a versioning sanity probe. Risks include assuming Azure version listing order, parsing delete-marker version IDs as RFC3339Nano, and returning nil on parse failure. Versioned tests cover ordering and deletion cases.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/azure/azure_pit.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/azure/azure_storage.go -->
# sources/sync-backup/kopia/repo/blob/azure/azure_storage.go

Purpose: implements the Azure Blob Storage provider for Kopia's `blob.Storage` interface.

Important APIs/types/functions: `azStorage`, `GetBlob`, `getBlobWithVersion`, `GetMetadata`, `translateError`, `PutBlob`, `DeleteBlob`, `ExtendBlobRetention`, `ListBlobs`, `putBlob`, `retryDeleteBlob`, `New`, `getAZService`, and provider `init`.

Control flow: reads validate range, create a versioned blob client, issue `DownloadStream`, optionally perform a one-byte request for zero-length reads, copy data, and verify length. Metadata reads map Azure properties and Kopia timestamp metadata. Writes reject unsupported `DoNotRecreate`, normalize retention mode to Azure locked semantics, upload a block blob with metadata and optional immutability policy, and return server mod time. Deletes ignore not-found and, when immutability blocks deletion, create/delete an unlocked temporary version as a soft-delete marker workaround. `New` validates container, builds a client using SAS, shared key, client secret, certificate, or workload identity, optionally wraps PIT and retrying storage, and verifies listing.

State and persistence behavior: blob contents, metadata timestamps, versions, immutability policies, and delete markers live in Azure. The provider itself keeps client/container/options only.

Dependencies/integration points: uses Azure SDK clients, Kopia timestamp metadata, retrying wrapper, point-in-time/readonly wrapper, and storage registry. Risks include no `DoNotRecreate` support, provider-specific metadata key casing, immutable delete complexity, credential-mode ambiguity, and cloud propagation failures. Tests cover user agent, live storage operations, invalid credentials/container/blob, credential modes, immutability, and versioned PIT behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/azure/azure_storage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/azure/azure_storage_test.go -->
# sources/sync-backup/kopia/repo/blob/azure/azure_storage_test.go

Purpose: live integration tests for Azure storage construction, cleanup, credential modes, normal blob operations, and invalid configurations.

Important APIs/types/functions: environment constants for Azure credentials, `mustGetOptions`, `createContainer`, `TestCleanupOldData`, `TestAzureStorage`, `TestAzureStorageSASToken`, `TestAzureStorageClientSecret`, `TestAzureStorageClientCertificate`, `TestAzureFederatedIdentity`, `TestAzureStorageInvalidBlob`, `TestAzureStorageInvalidContainer`, `TestAzureStorageInvalidCreds`, and `getBlobCount`.

Control flow: helpers read environment or skip, optionally create containers, then invoke shared `blobtesting` suites against Azure-backed storage. Credential-specific tests construct `azure.Options` for account key, SAS, client secret, certificate, and federated identity. Invalid tests assert failures for bogus blob/container/credentials.

State and persistence behavior: tests create, list, and delete real Azure blobs under configured prefixes/containers. Cleanup tests remove old data according to test-suite rules.

Dependencies/integration points: validates Azure SDK integration, Kopia storage registry, throttling/retrying behavior through shared suites, and environment-managed cloud accounts. Risks include skips hiding coverage in local runs, cloud cost/quota/latency, and retained data after failures. These are the primary regression signals for provider compatibility with the generic blob contract.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/azure/azure_storage_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/azure/azure_test.go -->
# sources/sync-backup/kopia/repo/blob/azure/azure_test.go

Purpose: verifies Azure SDK telemetry/user-agent integration.

Important APIs/types/functions: `TestUserAgent`, `blob.ApplicationID`, and Azure client construction paths.

Control flow: the test creates an Azure service/client configuration and asserts Kopia's application ID is present in the configured telemetry/user-agent behavior. It focuses on client options rather than live storage calls.

State and persistence behavior: no Azure blobs are mutated. State is limited to constructed client options.

Dependencies/integration points: protects the integration between Kopia's blob package identity and Azure SDK telemetry. This matters for supportability and provider-side observability. Risks/test gaps include no validation of every credential mode's effective HTTP headers, and no live request inspection. It is a narrow but useful signal that the provider brands its requests as intended.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/azure/azure_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/azure/azure_versioned.go -->
# sources/sync-backup/kopia/repo/blob/azure/azure_versioned.go

Purpose: defines Azure version metadata helpers used by point-in-time storage.

Important APIs/types/functions: `versionMetadata`, `versionMetadataCallback`, `getVersionedBlobMeta`, and `getBlobVersions`. `versionMetadata` embeds `blob.Metadata` and adds `Version` plus `IsDeleteMarker`.

Control flow: `getVersionedBlobMeta` requires `BlobItem.VersionID`, converts the Azure list item into normal blob metadata, and annotates delete-marker status via `isAzureDeleteMarker`. `getBlobVersions` delegates to `listBlobVersions`, tracks whether any versions were found, calls the callback for each, and returns `blob.ErrBlobNotFound` when nothing matched.

State and persistence behavior: no mutation; it interprets Azure's persistent version list and metadata into Kopia's PIT model. The `Version` string is expected to follow Azure's RFC3339Nano-like version ID semantics used elsewhere for delete-marker filtering.

Dependencies/integration points: used by `azure_pit.go` and tested by versioned integration tests. Risks include hard failure when versioning is disabled because `VersionID` is nil, and relying on Azure list item fields included by the caller. Tests cover disabled versioning and version/deletion scenarios.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/azure/azure_versioned.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/azure/azure_versioned_test.go -->
# sources/sync-backup/kopia/repo/blob/azure/azure_versioned_test.go

Purpose: integration tests for Azure blob version listing and point-in-time selection behavior.

Important APIs/types/functions: `TestGetBlobVersionsFailsWhenVersioningDisabled`, `TestGetBlobVersions`, `TestGetBlobVersionsWithDeletion`, and `putBlobs`.

Control flow: tests set up Azure storage with versioning assumptions, write multiple blob versions, invoke PIT/version helper methods, and compare version metadata ordering and visibility. Deletion tests verify delete-marker handling so a point-in-time before or after deletion yields correct existence semantics.

State and persistence behavior: real Azure blob versions are created and may remain subject to cloud retention/versioning policies. The tests depend on server-side timestamps and version IDs.

Dependencies/integration points: exercises `azPointInTimeStorage`, `getBlobVersions`, `newestAtUnlessDeleted`, and Azure SDK listing flags. Risks include environment skips, cloud ordering/timestamp precision, and cleanup complexity. These tests are the strongest signal that Azure PIT views match Kopia's expected historical-read contract.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/azure/azure_versioned_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/b2/b2_options.go -->
# sources/sync-backup/kopia/repo/blob/b2/b2_options.go

Purpose: defines persistent JSON options for the deprecated Backblaze B2 storage provider.

Important APIs/types/functions: `Options` with bucket name, prefix, key ID, application key, and throttling limits. The file is behind `!no_extra_providers`.

Control flow: no functions are defined here; validation and client setup happen in `b2_storage.go`. JSON tags define repository config serialization and the key is marked sensitive.

State and persistence behavior: option values are stored through `blob.ConnectionInfo`. Credentials authorize access to a B2 bucket and prefix but this file does not mutate provider state.

Dependencies/integration points: consumed by B2 storage creation and config round-tripping. Risks include provider deprecation, backward compatibility of JSON field names, and no point-in-time or retention options. Live tests cover required bucket/credentials and invalid cases when environment variables are present.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/b2/b2_options.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/b2/b2_storage.go -->
# sources/sync-backup/kopia/repo/blob/b2/b2_storage.go

Purpose: implements the deprecated Backblaze B2 blob storage provider.

Important APIs/types/functions: `b2Storage`, `GetBlob`, `resolveFileID`, `GetMetadata`, `translateError`, `PutBlob`, `DeleteBlob`, `ListBlobs`, `ConnectionInfo`, `DisplayName`, `String`, `New`, and provider `init`.

Control flow: reads validate offset, set an optional B2 byte range, download by name, skip copying for zero-length reads, and enforce output length. Metadata resolves the latest upload file ID from versions, fetches file info, and maps upload timestamp or Kopia metadata timestamp. Writes reject retention and `DoNotRecreate`, handle zero-length bodies with `http.NoBody`, upload file data with metadata, and return server mod time. Deletes hide the file and ignore not-found-like errors. Listing pages through B2 names with a prefix and emits metadata for each file. `New` warns that B2 is deprecated, validates bucket name, authenticates, opens the bucket, and wraps storage in retrying.

State and persistence behavior: blob data, metadata, and hidden-file markers persist in B2. Local state is B2 client, bucket handle, and options.

Dependencies/integration points: depends on `go-backblaze`, Kopia timestamp metadata, retrying wrapper, throttling options, and storage registry. Risks include deprecation, no retention/DoNotRecreate support, `DeleteBlob` currently returning nil even for non-not-found errors after translation, B2 version/hide semantics, and reliance on live cloud tests. Tests cover shared storage behavior and invalid bucket/blob/credentials.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/b2/b2_storage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/b2/b2_storage_test.go -->
# sources/sync-backup/kopia/repo/blob/b2/b2_storage_test.go

Purpose: live integration tests for the B2 storage provider.

Important APIs/types/functions: B2 environment constants, `TestCleanupOldData`, `TestB2Storage`, `TestB2StorageInvalidBlob`, `TestB2StorageInvalidBucket`, and `TestB2StorageInvalidCreds`.

Control flow: tests read B2 bucket/key credentials from environment or skip, construct `b2.Options`, run shared blob storage test suites, clean old test data, and assert invalid configuration failures.

State and persistence behavior: tests create and hide/delete real B2 objects under the configured bucket/prefix. Cleanup relies on B2 listing/deletion behavior.

Dependencies/integration points: validates the B2 provider against Kopia's generic `blobtesting` contract and the external Backblaze API. Risks include provider deprecation, environment skips, cloud flakiness, and hidden versions accumulating. The tests are the only strong end-to-end signal for B2 because the provider has no local mock tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/b2/b2_storage_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/beforeop/beforeop.go -->
# sources/sync-backup/kopia/repo/blob/beforeop/beforeop.go

Purpose: provides a wrapper that invokes callbacks immediately before selected blob storage operations.

Important APIs/types/functions: callback types, `beforeOp`, `GetBlob`, `GetMetadata`, `PutBlob`, `DeleteBlob`, `NewWrapper`, and `NewUniformWrapper`. The `onPutBlob` callback receives a pointer to the operation's `PutOptions`, allowing mutation before forwarding.

Control flow: each overridden method checks whether its callback is configured. If present, callback errors short-circuit the underlying operation. Otherwise the operation delegates to the wrapped `blob.Storage`. Uniform wrapper adapts a single callback to all four operations.

State and persistence behavior: the wrapper has no persistence. It can alter write behavior by mutating `PutOptions`, and callbacks may introduce external state or side effects.

Dependencies/integration points: useful for instrumentation, gatekeeping, option injection, or repository-state checks before storage access. Risks include callback side effects, no callbacks for `ListBlobs`, `Close`, `GetCapacity`, or `FlushCaches`, and only value-copy `PutOptions` mutation scoped to that call. Tests cover negative short-circuiting and positive callback invocation/delegation.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/beforeop/beforeop.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/beforeop/beforeop_test.go -->
# sources/sync-backup/kopia/repo/blob/beforeop/beforeop_test.go

Purpose: validates `beforeop` wrapper callback behavior.

Important APIs/types/functions: `TestBeforeOpStorageNegative`, `TestBeforeOpStoragePositive`, `NewWrapper`, `NewUniformWrapper`, and blob operation methods against a test storage.

Control flow: negative tests configure callbacks that return errors and assert the wrapped storage operation is not allowed to proceed. Positive tests configure callbacks that record invocation and allow operations through, checking both operation-specific and uniform callback paths.

State and persistence behavior: tests use local/mock storage state and callback counters/errors. No external persistence is involved.

Dependencies/integration points: exercises wrapper composition with Kopia's blob interface. Risks/test gaps include no coverage for `onPutBlob` mutating options, no concurrent callback behavior, and no list/close behavior because those methods are not wrapped. The tests are useful to ensure pre-operation failures remain fail-fast.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/beforeop/beforeop_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/config.go -->
# sources/sync-backup/kopia/repo/blob/config.go

Purpose: defines JSON round-tripping for blob storage connection configuration.

Important APIs/types/functions: `ConnectionInfo`, `UnmarshalJSON`, and `MarshalJSON`. The JSON shape is `{type, config}`, where type selects a registered storage factory and config is decoded into that factory's default config type.

Control flow: unmarshal decodes raw type/config, looks up `factories[type]`, initializes `Config` via `defaultConfigFunc`, and unmarshals raw config into it. Marshal emits the stored type and config. Unknown storage type and malformed config return wrapped errors.

State and persistence behavior: this is a core persistent repository configuration boundary. It stores provider type and provider-specific options used later by `NewStorage`.

Dependencies/integration points: tightly coupled to `registry.go` and every provider's `init` registration. Risks include failure to decode configs if provider packages are not linked/imported, backward-compatibility constraints on provider option JSON, and `Config` being `any` requiring callers to know expected types. Registry tests cover connection info round-tripping.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/doc.go -->
# sources/sync-backup/kopia/repo/blob/doc.go

Purpose: package documentation stub for the `blob` package.

Important APIs/types/functions: no declarations beyond the package clause are present in this file.

Control flow: none.

State and persistence behavior: none.

Dependencies/integration points: establishes/participates in Go package documentation for the blob abstraction. Risks and test signals are minimal; all substantive behavior for this package is in other files such as config, registry, storage interfaces, and wrappers.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/filesystem/filesystem_options.go -->
# sources/sync-backup/kopia/repo/blob/filesystem/filesystem_options.go

Purpose: defines configuration for filesystem-backed blob storage and helpers for default permissions.

Important APIs/types/functions: `Options`, `fileMode`, and `dirMode`. Options include root path, file/dir modes, optional UID/GID ownership, sharding options, throttling limits, and an unexported OS interface override for tests.

Control flow: `fileMode` returns configured file mode or default `0600`; `dirMode` returns configured directory mode or default `0700`. Validation of path accessibility and directory creation occurs in `filesystem_storage.go`.

State and persistence behavior: exported fields form the persistent JSON config. UID/GID fields allow root-run processes to chown written blobs after atomic rename. The OS override is not serialized and exists for tests.

Dependencies/integration points: consumed by `fsImpl`, sharded storage, throttling wrappers, and repository config. Risks include permission defaults affecting interoperability, zero values meaning defaults so explicit mode `0` cannot be represented, and ownership changes only attempted as root. Tests cover validation, path creation, modes indirectly, and mock OS behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/filesystem/filesystem_options.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/filesystem/filesystem_storage.go -->
# sources/sync-backup/kopia/repo/blob/filesystem/filesystem_storage.go

Purpose: implements filesystem-backed blob storage through the sharded storage adapter.

Important APIs/types/functions: `fsStorage`, `fsImpl`, `isRetriable`, `GetBlobFromPath`, `GetMetadataFromPath`, `PutBlobInPath`, `createTempFileWithData`, `createTempFileAndDir`, `DeleteBlobInPath`, `ReadDir`, `TouchBlob`, `ConnectionInfo`, `DisplayName`, `New`, and provider `init`.

Control flow: reads retry retriable OS path/link errors, open the target file, seek/copy requested ranges, handle macOS zero-size transient reads specially, and enforce exact length. Metadata stats the path under retry. Writes reject unsupported retention/DoNotRecreate, create a unique temp file with random suffix, create missing shard directories, write/sync/close data, atomically rename, optionally chown, set mod time, and return server mod time. Deletes retry removes and ignore missing files. Listing converts directory entries to file infos while ignoring races where entries disappear. `TouchBlob` updates old mtimes through sharded path resolution. `New` optionally creates the root directory, verifies accessibility, and wraps `fsImpl` in `sharded.New`.

State and persistence behavior: blob data persists as files under a sharded directory tree. Temporary files are removed on write/sync/close errors. Atomic rename is the main consistency boundary.

Dependencies/integration points: uses `osInterface` for real/mocked OS calls, `dirutil.MkSubdirAll`, `retry`, `iocopy`, `clock`, and the blob registry. Risks include filesystem-specific stale/path errors, partial temp cleanup failures, chmod/chown limitations, exact-length races, and unsupported retention/DoNotRecreate. Tests cover shared storage behavior, concurrency, sharding, retries, error handling, temp file cleanup, sync-before-close, Unix stale errors, and capacity by platform.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/filesystem/filesystem_storage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/filesystem/filesystem_storage_capacity_openbsd.go -->
# sources/sync-backup/kopia/repo/blob/filesystem/filesystem_storage_capacity_openbsd.go

Purpose: OpenBSD-specific capacity reporting for filesystem storage.

Important APIs/types/functions: `(*fsStorage).GetCapacity`, using platform `statfs` fields appropriate for OpenBSD.

Control flow: the method queries filesystem statistics for the storage root and converts block counts/sizes into total and free byte counts, returning a `blob.Capacity`.

State and persistence behavior: read-only capacity inspection; it does not mutate files.

Dependencies/integration points: selected by Go build constraints for OpenBSD and used by generic repository capacity queries. Risks include platform-specific field semantics and overflow/conversion issues. Test coverage is likely indirect because capacity behavior is platform dependent and normal CI may not run OpenBSD.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/filesystem/filesystem_storage_capacity_openbsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/filesystem/filesystem_storage_capacity_unix.go -->
# sources/sync-backup/kopia/repo/blob/filesystem/filesystem_storage_capacity_unix.go

Purpose: Unix-specific capacity reporting for filesystem storage on non-OpenBSD Unix platforms.

Important APIs/types/functions: `(*fsStorage).GetCapacity`, using `syscall.Statfs` style filesystem statistics.

Control flow: the method stats the filesystem containing the storage root and computes total/free bytes from block counts and block size.

State and persistence behavior: read-only inspection of filesystem capacity; no blob state changes.

Dependencies/integration points: used by Kopia capacity reporting and selected via platform build tags. Risks include differences between available/free block fields, filesystem reporting quirks, and integer conversion assumptions. Coverage is mostly indirect through platform-specific builds and shared storage tests that may call capacity.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/filesystem/filesystem_storage_capacity_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/filesystem/filesystem_storage_capacity_windows.go -->
# sources/sync-backup/kopia/repo/blob/filesystem/filesystem_storage_capacity_windows.go

Purpose: Windows-specific capacity reporting for filesystem storage.

Important APIs/types/functions: `(*fsStorage).GetCapacity`, implemented with Windows disk-free-space APIs.

Control flow: the method queries capacity for the storage path and converts Windows values into Kopia's `blob.Capacity` result.

State and persistence behavior: read-only capacity query; no files are created or modified.

Dependencies/integration points: selected only on Windows builds and used by generic capacity reporting. Risks include path normalization/long-path behavior, drive/share reporting differences, and platform-specific API failures. Test coverage is likely indirect through Windows CI/shared filesystem storage tests rather than dedicated unit tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/filesystem/filesystem_storage_capacity_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/filesystem/filesystem_storage_sync_test.go -->
# sources/sync-backup/kopia/repo/blob/filesystem/filesystem_storage_sync_test.go

Purpose: tests that filesystem writes sync data before close and surface sync errors.

Important APIs/types/functions: `verifySyncBeforeCloseFile`, `mockOSForSyncTest`, `TestPutBlob_SyncBeforeClose`, and `TestPutBlob_FailsOnSyncError`.

Control flow: the custom write file tracks whether `Sync` happens before `Close` and can inject sync failures. The mock OS returns that file from `CreateNewFile`. Tests call `PutBlobInPath` and assert successful ordering or expected error behavior.

State and persistence behavior: state is held in mock file flags rather than real durable writes. The tested persistence invariant is important: data is flushed before a temp file is closed and renamed.

Dependencies/integration points: targets `fsImpl.createTempFileWithData` and write error cleanup paths. Risks/test gaps include no real fsync durability guarantee across filesystems and no directory fsync check after rename. The test strongly pins the current temp-file write/sync/close order.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/filesystem/filesystem_storage_sync_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/filesystem/filesystem_storage_test.go -->
# sources/sync-backup/kopia/repo/blob/filesystem/filesystem_storage_test.go

Purpose: broad unit and integration-style tests for filesystem blob storage.

Important APIs/types/functions: tests include `TestFileStorage`, `TestFileStorageLongPath`, `TestFileStorageValidate`, `TestFileStorageTouch`, `TestFileStorageConcurrency`, `TestFilesystemStorageDirectoryShards`, retry/error handling tests for get/metadata/put/delete/list/touch/new, temp-file creation tests, `verifyBlobTimestampOrder`, `newMockOS`, and `verifyEmptyDir`.

Control flow: shared `blobtesting` suites exercise normal storage operations against temp directories. Other tests use mock OS implementations to inject read/stat/write/sync/close/rename/remove/list errors, verify retry limits, assert path validation, inspect directory sharding behavior, test touch threshold semantics, and confirm temp files are removed on failures.

State and persistence behavior: tests create real temp-directory blob trees and mock OS state. They verify atomic-temp-file behavior, mtime persistence, shard layout, cleanup after errors, and concurrent access behavior.

Dependencies/integration points: covers `fsImpl`, `fsStorage`, sharded storage, retry policy, `osInterface`, and generic blob testing. Risks/test gaps include platform-specific behavior split into other files, no crash/power-loss simulation around rename, and limited real filesystem error coverage. This is the main regression suite for local storage correctness.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/filesystem/filesystem_storage_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/filesystem/filesystem_storage_unix_test.go -->
# sources/sync-backup/kopia/repo/blob/filesystem/filesystem_storage_unix_test.go

Purpose: Unix-specific test for stale file handle error handling in filesystem storage.

Important APIs/types/functions: `TestFileStorage_ESTALE_ErrorHandling`, Unix `ESTALE` behavior through mock OS/stat/open/remove/list paths, and filesystem retry classification.

Control flow: the test injects stale errors and verifies they are treated as non-retriable or handled according to filesystem provider expectations. It complements cross-platform mock tests with Unix errno-specific behavior.

State and persistence behavior: mock/local filesystem state only. No durable external state is used.

Dependencies/integration points: validates `realOS.IsStale`/`fsImpl.isRetriable` semantics on Unix. Risks include platform build constraints, errno differences across Unix variants, and limited coverage on non-Unix CI. The test protects against retry loops on stale handles, which can otherwise mask real filesystem invalidation.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/filesystem/filesystem_storage_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/filesystem/osinterface.go -->
# sources/sync-backup/kopia/repo/blob/filesystem/osinterface.go

Purpose: defines the filesystem provider's OS abstraction to make file operations mockable.

Important APIs/types/functions: `osInterface`, `osReadFile`, and `osWriteFile`. The interface covers open/stat/read-dir/create/remove/rename/mkdir/chown/chtimes/error classification and effective UID. Read files must support read/seek/close/stat; write files must support write/close/sync.

Control flow: no runtime logic is implemented here. `fsImpl` calls this interface for all OS interactions, and tests provide mock implementations.

State and persistence behavior: the interface abstracts persistent filesystem state but stores none itself.

Dependencies/integration points: implemented by `realOS` and `mockOS`. Risks include interface bloat making mocks tedious, provider behavior depending heavily on correct error classification, and missing operations such as directory fsync. Tests around mock and real OS implementations validate enough of the contract for filesystem storage error paths.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/filesystem/osinterface.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/filesystem/osinterface_mock_other_test.go -->
# sources/sync-backup/kopia/repo/blob/filesystem/osinterface_mock_other_test.go

Purpose: non-Unix test implementation detail for `mockOS.Stat`.

Important APIs/types/functions: platform-specific `(*mockOS).Stat`.

Control flow: provides the mock stat behavior for platforms that do not use the Unix-specific mock implementation. It returns configured stat results/errors used by filesystem storage tests.

State and persistence behavior: uses in-memory mock OS state; no real files are required for these paths.

Dependencies/integration points: selected by build tags to keep mock behavior compatible with platform-specific file info/error types. Risks are low but platform divergence can hide test gaps if Unix and non-Unix mocks behave differently. Its test signal is indirect through `filesystem_storage_test.go` on non-Unix builds.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/filesystem/osinterface_mock_other_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/filesystem/osinterface_mock_test.go -->
# sources/sync-backup/kopia/repo/blob/filesystem/osinterface_mock_test.go

Purpose: provides the central mock OS and mock file types for filesystem storage tests.

Important APIs/types/functions: `mockOS`, `errNonRetriable`, methods for `Open`, `Rename`, `ReadDir`, `Remove`, `Chtimes`, `Chown`, `CreateNewFile`, `Mkdir`, `MkdirAll`, `Geteuid`, plus failure file types `readFailureFile`, `writeFailureFile`, `syncFailureFile`, `writeCloseFailureFile`, and `mockDirEntryInfoError`.

Control flow: mock methods either delegate to configured functions/errors or simulate filesystem behavior needed by tests. Failure file wrappers inject read/write/sync/close errors. Directory-entry wrappers inject `Info` failures.

State and persistence behavior: all state is in mock fields and temporary test files. It enables deterministic testing of retry and cleanup paths that are hard to force with the real OS.

Dependencies/integration points: used by filesystem storage tests and sync tests. Risks include mock behavior diverging from real OS semantics, especially path/link error classification and file modes. The breadth of tests using this mock gives strong signals for `fsImpl` error paths, but it should not be treated as proof of crash durability.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/filesystem/osinterface_mock_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/filesystem/osinterface_mock_unix_test.go -->
# sources/sync-backup/kopia/repo/blob/filesystem/osinterface_mock_unix_test.go

Purpose: Unix-specific mock `Stat` behavior for filesystem storage tests.

Important APIs/types/functions: `(*mockOS).Stat`, using Unix-aware file info/stat behavior.

Control flow: selected on Unix-like builds, this method supplies stat results/errors to tests that need platform-specific metadata or errno handling.

State and persistence behavior: test-only mock state. No external persistence is involved.

Dependencies/integration points: complements `osinterface_mock_test.go` and Unix-specific stale error tests. Risks include platform-specific assumptions that may differ across Linux/macOS/BSD. Its effectiveness is indirect through the filesystem test suite.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/filesystem/osinterface_mock_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/filesystem/osinterface_realos.go -->
# sources/sync-backup/kopia/repo/blob/filesystem/osinterface_realos.go

Purpose: implements `osInterface` using real operating system calls.

Important APIs/types/functions: `realOS` and methods `Open`, `IsNotExist`, `IsExist`, `IsPathSeparator`, `Rename`, `ReadDir`, `IsPathError`, `IsLinkError`, `Remove`, `Stat`, `CreateNewFile`, `Mkdir`, `MkdirAll`, `Chtimes`, `Geteuid`, and `Chown`.

Control flow: methods mostly wrap standard `os` functions, passing paths through `ospath.SafeLongFilename` for long-path handling. Error classifiers use `os.IsNotExist`, `os.IsExist`, and `errors.As` for `os.PathError`/`os.LinkError`.

State and persistence behavior: this is the production bridge to filesystem state. Create uses `O_CREATE|O_EXCL|O_WRONLY`, rename is the atomic publish step, and chtimes/chown adjust persisted metadata/ownership.

Dependencies/integration points: used by `filesystem.New` unless tests inject an override. Risks include platform-specific long-path behavior, rename semantics across filesystems, and path/link error classification feeding retry decisions. Compile-time interface assertion ensures method coverage; behavior is tested indirectly through filesystem storage tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/filesystem/osinterface_realos.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/filesystem/osinterface_realos_other.go -->
# sources/sync-backup/kopia/repo/blob/filesystem/osinterface_realos_other.go

Purpose: default non-Unix implementation of stale-file-handle detection for `realOS`.

Important APIs/types/functions: `realOS.IsStale`.

Control flow: on platforms without Unix `ESTALE` handling, the method returns false, so stale-specific retry suppression does not apply.

State and persistence behavior: none; it only classifies errors.

Dependencies/integration points: selected by build tags and consumed by `fsImpl.isRetriable`. Risks include a platform that can produce stale-handle-like errors but is covered by this fallback, causing retry classification differences. Test signals are indirect on non-Unix builds.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/filesystem/osinterface_realos_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/filesystem/osinterface_realos_unix.go -->
# sources/sync-backup/kopia/repo/blob/filesystem/osinterface_realos_unix.go

Purpose: Unix implementation of stale file handle detection.

Important APIs/types/functions: `realOS.IsStale`, checking Unix `ESTALE` through error unwrapping/classification.

Control flow: the method detects stale filesystem handle errors so `fsImpl.isRetriable` can avoid retrying them indefinitely.

State and persistence behavior: no mutation; it only classifies OS errors that arise from filesystem state changes.

Dependencies/integration points: selected on Unix builds and validated by Unix filesystem tests. Risks include errno wrapping differences and NFS/filesystem-specific stale behavior. Correct classification matters because stale handles usually indicate an invalid descriptor/resource rather than a transient path operation.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/filesystem/osinterface_realos_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/gcs/gcs_immu_test.go -->
# sources/sync-backup/kopia/repo/blob/gcs/gcs_immu_test.go

Purpose: live integration test for Google Cloud Storage object retention/immutability behavior.

Important APIs/types/functions: `TestGoogleStorageImmutabilityProtection` and `getGcsClient`, using GCS client APIs, `gcs.Options`, and Kopia blob retention options.

Control flow: the test is skipped without immutable bucket environment/config. It creates GCS-backed storage, writes blobs with retention, verifies object retention metadata through the GCS API, extends retention, and checks deletion/immutability behavior.

State and persistence behavior: mutates real GCS bucket objects and retention settings. Objects may be undeletable until retention expires, so cleanup behavior is constrained by cloud policy.

Dependencies/integration points: exercises `gcs.PutBlob`, `ExtendBlobRetention`, GCS object retention, credentials, and shared blob semantics. Risks include cloud policy propagation delays, clock precision/truncation, environment skips, and retained test artifacts. It is the key signal for retention semantics beyond generic blob tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/gcs/gcs_immu_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/gcs/gcs_options.go -->
# sources/sync-backup/kopia/repo/blob/gcs/gcs_options.go

Purpose: defines persistent options for Google Cloud Storage-backed repositories.

Important APIs/types/functions: `Options` with bucket name, prefix, service account credentials file or raw JSON, read-only flag, throttling limits, and optional point-in-time timestamp.

Control flow: no functions are implemented in this file. `gcs_storage.go` performs validation/client creation and `gcs_pit.go` handles `PointInTime`.

State and persistence behavior: this struct is serialized in repository connection config. Raw credential JSON is marked sensitive; read-only changes OAuth scope during client creation.

Dependencies/integration points: consumed by GCS provider creation, throttling wrappers, PIT wrapper, and config serialization. Risks include backward-compatible JSON field pressure, mutually exclusive credential sources resolved elsewhere, and read-only scope preventing mutations only at the provider credential level. Tests cover normal/invalid storage, credentials from environment, cleanup, immutability, and versioned PIT.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/gcs/gcs_options.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/gcs/gcs_pit.go -->
# sources/sync-backup/kopia/repo/blob/gcs/gcs_pit.go

Purpose: implements read-only point-in-time views for versioned GCS buckets.

Important APIs/types/functions: `gcsPointInTimeStorage`, `ListBlobs`, `GetBlob`, `GetMetadata`, `getVersionedMetadata`, `newestAtUnlessDeleted`, `getOlderThan`, and `maybePointInTimeStore`.

Control flow: `maybePointInTimeStore` returns raw storage when no PIT is configured; otherwise it reads bucket attributes, requires versioning, and wraps a PIT storage in `readonly.NewWrapper`. PIT listing groups version metadata by blob ID and emits the newest version not after the PIT unless considered deleted. PIT reads resolve version metadata and pass the generation to `getBlobWithVersion`; metadata returns the resolved version metadata.

State and persistence behavior: no mutations are allowed through the PIT wrapper. Historical state comes from GCS object generations and deletion timestamps.

Dependencies/integration points: depends on `gcs_versioned.go`, GCS bucket versioning, and the readonly wrapper. Risks include assuming GCS version iteration order, interpreting deletion based on `Deleted` timestamp relative to PIT, and requiring bucket attribute permissions. Versioned tests cover disabled versioning, multiple versions, and deletion behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/gcs/gcs_pit.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/gcs/gcs_storage.go -->
# sources/sync-backup/kopia/repo/blob/gcs/gcs_storage.go

Purpose: implements Kopia blob storage on Google Cloud Storage.

Important APIs/types/functions: `gcsStorage`, `GetBlob`, `getBlobWithVersion`, `GetMetadata`, `getBlobMeta`, `translateError`, `PutBlob`, `DeleteBlob`, `ExtendBlobRetention`, `ListBlobs`, `ConnectionInfo`, `DisplayName`, `Close`, `toBlobID`, `New`, and provider `init`.

Control flow: reads validate offset, optionally select an object generation, open a range reader, copy contents, and verify exact length. Metadata reads object attributes and maps Kopia timestamp metadata. Writes apply `DoesNotExist` precondition for `DoNotRecreate`, set chunk size/content type/timestamp metadata, optionally set locked object retention, copy data to the writer, cancel/close correctly on copy errors, commit on close, and return writer update time. Deletes ignore not-found. Retention extension updates object retention with second-truncated retain-until time. Listing iterates bucket objects by prefix and emits metadata. `New` creates a client with credentials/defaults, opens a bucket handle, optionally wraps PIT/readonly and retrying, and verifies listing.

State and persistence behavior: object bytes, metadata, generations, and retention live in GCS. The provider stores client/bucket/options and closes the client on `Close`.

Dependencies/integration points: uses `cloud.google.com/go/storage`, Google API errors, timestamp metadata, retrying wrapper, PIT wrapper, and registry. Risks include exact length checks with GCS range semantics, precondition mapping, retention permission requirements, timestamp metadata key casing, and cloud environment skips. Tests cover shared storage behavior, invalid config, cleanup, immutability, and versioned PIT.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/gcs/gcs_storage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/gcs/gcs_storage_test.go -->
# sources/sync-backup/kopia/repo/blob/gcs/gcs_storage_test.go

Purpose: live integration tests for normal GCS storage behavior and invalid setup.

Important APIs/types/functions: GCS environment constants, `TestCleanupOldData`, `TestGCSStorage`, `TestGCSStorageInvalid`, `gunzip`, `getEnvVarOrSkip`, `getCredJSONFromEnv`, `mustGetOptionsOrSkip`, and `getBlobCount`.

Control flow: helpers read bucket/project/credential environment variables, decode gzipped credential JSON when present, build `gcs.Options`, and run shared blob testing suites. Cleanup removes old data from the configured bucket/prefix. Invalid tests assert failures for incorrect setup.

State and persistence behavior: tests create/list/delete real GCS objects. Cleanup and counts operate against the live bucket.

Dependencies/integration points: validates GCS provider integration with generic blob tests, credential handling, and cloud API behavior. Risks include skipped coverage when env vars are absent, cloud latency/quota, and retained objects after failures. It complements dedicated immutability and versioned tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/gcs/gcs_storage_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/gcs/gcs_versioned.go -->
# sources/sync-backup/kopia/repo/blob/gcs/gcs_versioned.go

Purpose: provides GCS object-generation metadata helpers for point-in-time storage.

Important APIs/types/functions: `versionMetadata`, `versionMetadataCallback`, `getBlobVersions`, `listBlobVersions`, `list`, and `getVersionMetadata`.

Control flow: `getBlobVersions` lists versions for one exact blob prefix and returns `blob.ErrBlobNotFound` if none appear. `listBlobVersions` lists versions for all blobs with a prefix. The shared `list` function sets `storage.Query{Prefix, Versions:true}`, iterates object attrs, optionally stops when exact matching no longer applies, converts attrs to version metadata, and invokes callbacks. `getVersionMetadata` embeds normal blob metadata, marks delete state based on GCS `Deleted` time before the configured PIT, and stores generation as a decimal string.

State and persistence behavior: read-only interpretation of persisted GCS generations/deletion timestamps. No object mutation occurs.

Dependencies/integration points: used by `gcs_pit.go` and versioned integration tests. Risks include exact-match early return depending on iterator ordering, deletion semantics differing from providers with explicit delete markers, and generation parsing in `getBlobWithVersion`. Tests cover versioning disabled, multiple versions, and deletion scenarios.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/gcs/gcs_versioned.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/gcs/gcs_versioned_test.go -->
# sources/sync-backup/kopia/repo/blob/gcs/gcs_versioned_test.go

Purpose: live integration tests for GCS versioned/PIT behavior.

Important APIs/types/functions: `bucketOpts`, `TestGetBlobVersionsFailsWhenVersioningDisabled`, `TestGetBlobVersions`, `TestGetBlobVersionsWithDeletion`, `putBlobs`, `createBucket`, `validateBucket`, and `getImmutableBucketNameOrSkip`.

Control flow: tests create or validate buckets with required versioning settings, write multiple versions of blobs, invoke version listing/PIT helpers, and assert correct version visibility and deletion handling. Disabled-versioning tests ensure PIT setup fails with the expected error.

State and persistence behavior: tests create real GCS buckets/objects/generations and may depend on project-level permissions. Versioned objects persist until cleanup.

Dependencies/integration points: exercises GCS bucket creation/validation, object generation listing, PIT read-only wrapping, and deletion timestamp logic. Risks include environment/project permissions, bucket naming conflicts, cloud timestamp precision, and cleanup after failures. These are the main signals for GCS historical view correctness.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/gcs/gcs_versioned_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/gdrive/file_id_cache.go -->
# sources/sync-backup/kopia/repo/blob/gdrive/file_id_cache.go

Purpose: implements a concurrency-safe cache mapping Kopia blob IDs to Google Drive file IDs, plus a small circular change log.

Important APIs/types/functions: `fileIDCache`, `cacheEntry`, `changeEntry`, `Lookup`, `getEntry`, `BlindPut`, `RecordBlobChange`, `VisitBlobChanges`, `Clear`, `circularBufferNext`, and `newFileIDCache`.

Control flow: `Lookup` fetches or creates a cache entry from `sync.Map`, locks that entry, and gives exclusive access to the callback. `BlindPut` uses `Lookup` to set a file ID. `RecordBlobChange` writes blob/fileID changes into a fixed circular buffer protected by `mu`. `VisitBlobChanges` iterates the buffer from oldest-ish to newest and skips empty entries. `Clear` resets both map and change log.

State and persistence behavior: all cache state is in memory. It is not persisted across process restarts. The change log helps `ListBlobs` compensate for Google Drive prefix-query limitations and eventual list omissions.

Dependencies/integration points: used exclusively by `gdrive_storage.go`. Risks include fixed 256-entry change log dropping older unvisited changes, no cleanup of per-blob map entries except `Clear`, and iteration order of the circular buffer being subtle. Tests cover behavior indirectly through GDrive storage integration tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/gdrive/file_id_cache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/gdrive/gdrive_options.go -->
# sources/sync-backup/kopia/repo/blob/gdrive/gdrive_options.go

Purpose: defines persistent options for Google Drive-backed blob storage.

Important APIs/types/functions: `Options` with folder ID, credentials file or raw JSON, read-only flag, and throttling limits. The file is behind `!no_extra_providers`.

Control flow: no functions are defined here. Client creation and validation occur in `gdrive_storage.go`.

State and persistence behavior: the struct is serialized in repository connection config. Raw credential JSON is marked sensitive. The folder ID is the persistent namespace root for blob files.

Dependencies/integration points: consumed by GDrive provider creation and config round-tripping. Risks include provider warning that it is not actively tested and may cause data loss, Drive API limitations around prefix search, and read-only being enforced through OAuth scope rather than wrapper-level mutation blocking. Live tests cover basic behavior when credentials/folder are configured.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/gdrive/gdrive_options.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/gdrive/gdrive_storage.go -->
# sources/sync-backup/kopia/repo/blob/gdrive/gdrive_storage.go

Purpose: implements Kopia blob storage on Google Drive files in a configured folder.

Important APIs/types/functions: `gdriveStorage`, `GetCapacity`, `GetBlob`, `GetMetadata`, `PutBlob`, `DeleteBlob`, `ListBlobs`, `FlushCaches`, file-ID lookup helpers, prefix/range/name helpers, metadata parsing, `translateError`, credential token-source helpers, `CreateDriveService`, `New`, and provider `init`.

Control flow: capacity reads Drive quota. Reads resolve blob ID to Drive file ID through the cache/API, set an HTTP Range header, download, copy non-zero bodies, and verify exact length. Metadata lookup uses cache, falls back to Drive queries, fetches full metadata when needed, and parses modified time. Writes reject retention, resolve existing file ID, enforce `DoNotRecreate`, create or update a Drive file with media upload and optional modified time, update cache/change log, and return mod time. Deletes resolve file ID, delete it, clear cache entry, and record deletion. Listing queries files in the folder by MIME type and optionally capped name `contains` prefix, updates cache, filters exact prefix client-side, and uses recent cache changes to include blobs the Drive list missed. `New` warns about risk, creates Drive service using raw/file/default credentials, verifies listing, and wraps in retrying.

State and persistence behavior: each blob is a Drive file with name equal to blob ID and MIME `application/x-kopia`. File ID cache is transient; blob contents/mtimes persist in Drive.

Dependencies/integration points: uses Google Drive v3 API, OAuth2/JWT credentials, retry helpers, file ID cache, and storage registry. Risks include Drive search not supporting long prefix matches, eventual consistency, duplicate files causing hard errors, no retention support, fixed upload chunk size, default HTTP client behavior, and provider not actively tested. Tests cover cleanup, shared behavior, and invalid setup with live Drive.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/gdrive/gdrive_storage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/gdrive/gdrive_storage_test.go -->
# sources/sync-backup/kopia/repo/blob/gdrive/gdrive_storage_test.go

Purpose: live integration tests for Google Drive storage behavior and invalid setup.

Important APIs/types/functions: `TestCleanupOldData`, `TestGDriveStorage`, `TestGdriveStorageInvalid`, `gunzip`, `mustGetOptionsOrSkip`, `createTestFolderOrSkip`, and `deleteTestFolder`.

Control flow: helpers read credentials from environment, create or locate a Drive folder, construct `gdrive.Options`, run shared blob storage tests, clean old data, and validate invalid configuration failures.

State and persistence behavior: tests create real Google Drive files/folders and delete them during cleanup. File IDs and Drive metadata are external persistent state.

Dependencies/integration points: exercises Drive service creation, file upload/download/list/delete, file ID cache, and generic blob behavior. Risks include skipped coverage without credentials, Drive eventual consistency, quota/rate limits, and leftover files after failures. Because the provider is warned as not actively tested, these integration tests are especially important but environment-dependent.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/gdrive/gdrive_storage_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/logging/logging_storage.go -->
# sources/sync-backup/kopia/repo/blob/logging/logging_storage.go

Purpose: wraps a `blob.Storage` to log operations, durations, errors, concurrency levels, and OpenTelemetry spans.

Important APIs/types/functions: `loggingStorage`, `beginConcurrency`, `endConcurrency`, operation wrappers for `GetBlob`, `GetCapacity`, `IsReadOnly`, `GetMetadata`, `PutBlob`, `DeleteBlob`, `ListBlobs`, `Close`, `ConnectionInfo`, `DisplayName`, `FlushCaches`, `ExtendBlobRetention`, `translateError`, and `NewWrapper`.

Control flow: most operations start an OTel span, increment concurrency, start a timer, delegate to the base storage, record structured debug logs and content-log entries, then return the original error. `beginConcurrency` tracks and logs new maximum concurrency using atomics. `ListBlobs` wraps the callback to count results. `translateError` shortens blob-not-found logging to a string while leaving other errors intact.

State and persistence behavior: wrapper state is in-memory counters and references to loggers/base storage. It does not alter blob persistence, except timing/log side effects. Content logs may be persisted depending on configured logger sinks.

Dependencies/integration points: integrates with OpenTelemetry, Kopia `contentlog`, `logging.Logger`, `blobparam`, `logparam`, and any underlying storage. Risks include logging sensitive blob IDs/metadata, content-log overhead, concurrency count imbalance if panics occur, and a duplicated `"ListBlobs"` argument in content logging. Tests cover basic delegation/logging behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/logging/logging_storage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/logging/logging_storage_test.go -->
# sources/sync-backup/kopia/repo/blob/logging/logging_storage_test.go

Purpose: tests the logging storage wrapper against a real underlying storage.

Important APIs/types/functions: `TestLoggingStorage`, `logging.NewWrapper`, generic blob operations, and test logging/content-log setup.

Control flow: the test wraps a base storage, performs representative blob operations, and verifies behavior still matches expected storage semantics while logging paths execute.

State and persistence behavior: blob state is held by the test storage; wrapper adds only logging/concurrency state.

Dependencies/integration points: validates wrapper composition with the blob interface and ensures logging does not break operation results. Risks/test gaps include limited assertions on actual log records, no max-concurrency race test, no OpenTelemetry span inspection, and no `ExtendBlobRetention` coverage. It is primarily a smoke/regression test for delegation.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/logging/logging_storage_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/rclone/rclone_options.go -->
# sources/sync-backup/kopia/repo/blob/rclone/rclone_options.go

Purpose: defines persistent options for the rclone-backed storage provider.

Important APIs/types/functions: `Options` with remote path, rclone executable, extra args/env, startup timeout, debug flag, close-transfer behavior flag, embedded config, atomic write flag, sharded options, and throttling limits.

Control flow: no functions are in this file. `rclone_storage.go` interprets these options to launch `rclone serve webdav` and connect through the WebDAV provider.

State and persistence behavior: options are serialized in repository config. `EmbeddedConfig` may contain credentials but is not marked sensitive in this file, which is a notable risk.

Dependencies/integration points: consumed by rclone provider creation, WebDAV options, sharding, throttling, and JSON duration handling. Risks include command-line/env injection through user-controlled options, provider warning about limited testing/data loss, and `NoWaitForTransfers` existing in options but not used in the shown close path. Tests cover invalid executable/flags, providers, cancel context, directory shards, and shared behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/rclone/rclone_options.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/rclone/rclone_storage.go -->
# sources/sync-backup/kopia/repo/blob/rclone/rclone_storage.go

Purpose: implements a storage provider by launching `rclone serve webdav` locally and delegating blob operations to Kopia's WebDAV storage.

Important APIs/types/functions: `rcloneStorage`, `ListBlobs`, `GetMetadata`, `GetBlob`, `ConnectionInfo`, `Kill`, `Close`, `DisplayName`, `processStderrStatus`, `remoteControl`, `forgetVFS`, `rcloneURLs`, `runRCloneAndWaitForServerAddress`, `New`, and provider `init`.

Control flow: `New` creates a temp dir, generates TLS cert/key and htpasswd credentials, optionally writes embedded rclone config, builds rclone arguments with mandatory local random WebDAV and RC addresses, starts rclone without inheriting cancellation, scans stderr until both WebDAV and remote-control URLs are detected, configures an HTTP client trusting the generated cert, builds an underlying WebDAV storage, and stores it. Read/list/metadata operations first call RC `vfs/forget` to flush rclone caches, then delegate. `Close` closes WebDAV storage, kills rclone, waits, and removes temp dir. `remoteControl` POSTs JSON with basic auth to the RC endpoint.

State and persistence behavior: temporary TLS/config/auth files live under a temp directory and are removed on close or failed construction. Blob persistence is in the rclone remote backend. A live child process is provider state.

Dependencies/integration points: depends on external `rclone`, WebDAV provider, TLS utilities, htpasswd, uuid, process management, and remote-control API. Risks include startup-log regex fragility, process cleanup on crashes, external binary/version differences, credentials in embedded config/temp files, cache invalidation overhead, and provider data-loss warning. Tests cover startup cancellation, storage behavior, shard behavior, invalid exe/flags, provider matrix, and cleanup.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/rclone/rclone_storage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/rclone/rclone_storage_test.go -->
# sources/sync-backup/kopia/repo/blob/rclone/rclone_storage_test.go

Purpose: integration tests for the rclone provider, including process startup/failure and provider-backed storage behavior.

Important APIs/types/functions: `mustGetRcloneExeOrSkip`, `TestRCloneStorageCancelContext`, `TestRCloneStorage`, `TestRCloneStorageDirectoryShards`, `Killable`, `TestRCloneStorageInvalidExe`, `TestRCloneStorageInvalidFlags`, `TestRCloneProviders`, and `cleanupOldData`.

Control flow: tests locate an rclone executable or skip, create temporary/local or external provider remotes, run shared blob storage tests through the rclone provider, test context cancellation during startup, verify invalid executable/flags fail, exercise directory sharding, and clean stale remote test data.

State and persistence behavior: tests launch real rclone processes, create temp dirs/configs, and mutate local or configured remote storage. Cleanup removes old blobs and provider temp state.

Dependencies/integration points: validates external process orchestration, WebDAV delegation, RC cache flushing, and generic blob behavior. Risks include environment-dependent skips, rclone version/output changes breaking regexes, process leaks on failures, and external provider flakiness. These tests are the main safety net for a provider with many moving external parts.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/rclone/rclone_storage_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/readonly/readonly_storage.go -->
# sources/sync-backup/kopia/repo/blob/readonly/readonly_storage.go

Purpose: wraps any blob storage to prevent mutations while allowing reads and metadata/list/capacity operations.

Important APIs/types/functions: `ErrReadonly`, `readonlyStorage`, `GetCapacity`, `IsReadOnly`, `GetBlob`, `GetMetadata`, `PutBlob`, `DeleteBlob`, `ListBlobs`, `Close`, `ConnectionInfo`, `DisplayName`, `FlushCaches`, and `NewWrapper`.

Control flow: read-like methods delegate directly to the base storage. `PutBlob` and `DeleteBlob` always return `ErrReadonly`. `IsReadOnly` returns true regardless of the base. Other lifecycle/introspection calls are delegated.

State and persistence behavior: the wrapper itself stores only the base storage reference and does not mutate blob state. It prevents write/delete through this interface, but cannot prevent mutation through other references to the base storage.

Dependencies/integration points: used by point-in-time wrappers for Azure/GCS and any read-only repository mode. Risks include `ExtendBlobRetention` not being overridden in this file; behavior depends on `DefaultProviderImplementation` or interface embedding for unsupported methods. There are no direct tests in this subset, but PIT tests exercise read-only wrapping indirectly.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/readonly/readonly_storage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/registry.go -->
# sources/sync-backup/kopia/repo/blob/registry.go

Purpose: provides the global registry from storage type names to provider factory functions.

Important APIs/types/functions: global `factories`, `storageFactory`, `AddSupportedStorage`, and `NewStorage`.

Control flow: provider packages call generic `AddSupportedStorage` from `init`, supplying a type name, default config value, and typed create function. The registry stores a default-config function and an untyped create wrapper with a type assertion. `NewStorage` looks up the config type and invokes the factory or returns an unknown type error.

State and persistence behavior: registry state is process-global and populated at package initialization. It is not persisted, but it interprets persisted `ConnectionInfo` types.

Dependencies/integration points: central to all blob providers and `ConnectionInfo.UnmarshalJSON`. Risks include no locking around registration, duplicate type names overwriting previous factories, type assertions panicking if config does not match, and unknown types when provider packages are excluded by build tags. Tests cover registering a custom storage and connection info behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/registry.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/registry_test.go -->
# sources/sync-backup/kopia/repo/blob/registry_test.go

Purpose: tests blob storage registration and connection info JSON behavior.

Important APIs/types/functions: `myConfig`, `myStorage`, `TestRegistry`, and `TestConnectionInfo`.

Control flow: tests register a fake storage type, create storage through `NewStorage`, and verify unknown types/error paths. Connection info tests marshal/unmarshal typed config and ensure the default config/factory registry participates correctly.

State and persistence behavior: tests mutate the global `factories` map by adding a test provider. JSON strings act as persistent config samples.

Dependencies/integration points: validates `registry.go` and `config.go` together. Risks/test gaps include global registry pollution across tests, no duplicate-registration behavior check, and no concurrent registration/use coverage. The tests protect the basic config-to-factory path used by every real provider.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/registry_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/retrying/retrying_storage.go -->
# sources/sync-backup/kopia/repo/blob/retrying/retrying_storage.go

Purpose: wraps blob storage operations in exponential backoff for transient/unexpected errors.

Important APIs/types/functions: `retryingStorage`, `GetBlob`, `GetMetadata`, `PutBlob`, `DeleteBlob`, `NewWrapper`, and `isRetriable`.

Control flow: each wrapped data operation calls `retry.WithExponentialBackoff` or `WithExponentialBackoffNoValue`, delegates to the base storage, and retries only when `isRetriable` returns true. `GetBlob` resets the output buffer before every attempt to avoid mixed partial data. Non-retriable errors include not found, invalid range, set-time unsupported, invalid credentials, unsupported put option, already exists, and repository unavailable due to upgrade.

State and persistence behavior: wrapper state is only the embedded storage reference. Retried `PutBlob`/`DeleteBlob` can repeat external side effects, so underlying operations must be idempotent or translate permanent errors correctly.

Dependencies/integration points: used by cloud providers and other adapters to smooth transient failures. Risks include retrying non-idempotent operations when providers return unexpected errors, hiding latency, and not wrapping list/capacity/close operations. Tests cover retry behavior and non-retriable classification in representative paths.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/retrying/retrying_storage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/retrying/retrying_storage_test.go -->
# sources/sync-backup/kopia/repo/blob/retrying/retrying_storage_test.go

Purpose: validates retry wrapper behavior.

Important APIs/types/functions: `TestRetrying`, `retrying.NewWrapper`, and a test storage that injects errors before success or permanent errors.

Control flow: the test configures operations to fail transiently and then succeed, ensuring the wrapper retries and returns success. It also exercises permanent errors that should not be retried according to `isRetriable`.

State and persistence behavior: state is in test counters and buffers. The test confirms output buffers are reset between read attempts.

Dependencies/integration points: validates integration with `internal/retry` and blob error sentinels. Risks/test gaps include no timing/backoff assertion, no context cancellation coverage, and no list/capacity retries because the wrapper does not implement those. The test is still important because cloud providers rely on this wrapper for transient resilience.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/retrying/retrying_storage_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/s3/s3_options.go -->
# sources/sync-backup/kopia/repo/blob/s3/s3_options.go

Purpose: defines persistent options for S3-compatible storage.

Important APIs/types/functions: `Options` with endpoint, bucket, access key/secret/session token, prefix, region, TLS/path-style/hostname/flat-mode flags, storage class, ACL, point-in-time timestamp, user agent prefix, and throttling limits.

Control flow: no functions are implemented here. S3 client construction, validation, PIT behavior, and normal operations live in neighboring S3 files outside this subset plus `s3_pit.go`.

State and persistence behavior: the struct is serialized in repository connection config. Secret access key and session token are marked sensitive. Point-in-time config enables a historical read-only view when versioning is available.

Dependencies/integration points: consumed by S3 provider factory, AWS/S3-compatible clients, throttling, and PIT wrapper. Risks include many provider-specific flags interacting, backward-compatible JSON pressure, credentials/session token handling, and differences between AWS S3 and compatible services. Tests for the full provider are mostly outside this subset; PIT helper behavior is represented here through `s3_pit.go`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/s3/s3_options.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/s3/s3_pit.go -->
# sources/sync-backup/kopia/repo/blob/s3/s3_pit.go

Purpose: implements point-in-time read-only views for S3-compatible versioned buckets.

Important APIs/types/functions: `s3PointInTimeStorage`, `ListBlobs`, `GetBlob`, `GetMetadata`, `getMetadata`, `newestAtUnlessDeleted`, `getOlderThan`, and `maybePointInTimeStore`.

Control flow: PIT listing requests object versions by prefix, groups versions by blob ID, and emits the newest version at or before the configured time unless it is a delete marker. PIT `GetBlob` and `GetMetadata` resolve version metadata through `getMetadata` and delegate to version-specific reads/metadata. `getOlderThan` filters version slices by timestamp; comments note S3 ordering differs from Azure/GCS. `maybePointInTimeStore` wraps only when a non-zero point-in-time is configured and returns a readonly wrapper after validating version access.

State and persistence behavior: the wrapper is read-only and interprets persisted S3 object versions/delete markers. No mutation occurs through the PIT view.

Dependencies/integration points: depends on S3 storage/versioned helpers defined in neighboring files, `readonly.NewWrapper`, and S3 versioning/list-object-versions semantics. Risks include provider-compatible services with non-AWS ordering or delete-marker behavior, timestamp precision around the PIT boundary, and versioning disabled/missing repository probes. Full tests for S3 PIT are outside the supplied file list, so this section relies on code-level inspection rather than local test signals.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/s3/s3_pit.go -->
