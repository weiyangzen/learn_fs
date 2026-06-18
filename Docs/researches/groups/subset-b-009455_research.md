# subset-b-009455

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/gcs/gcs.go -->
# sources/test-tools/syzkaller/pkg/gcs/gcs.go

## Purpose
`gcs.go` wraps Google Cloud Storage for syzkaller code that needs to upload, read, publish, delete, test, and list bucket objects. It hides the `cloud.google.com/go/storage` client behind a small `Client` interface and assumes Application Default Credentials when constructing a real client.

## Important APIs, Types, And Functions
`Client` defines the storage surface: `Close`, `FileReader`, `FileWriter`, `DeleteFile`, `FileExists`, `ListObjects`, and `Publish`. `UploadOptions` controls optional public ACL publishing, content encoding, and test injection via `GCSClientMock`. `UploadFile` is the high-level upload helper. `NewClient` returns the concrete `client` wrapper. `Object` is the minimal listing record with path and creation time. `GetDownloadURL` maps bucket/object paths to either public or authenticated Cloud Storage URLs. `ErrFileNotFound` normalizes delete misses. The private `split` helper parses `bucket/object` paths.

## Control Flow
`UploadFile` strips a leading `gs://`, creates or uses an injected client, defers `Close`, obtains a writer, streams all input via `io.Copy`, closes the writer, and optionally calls `Publish`. Read operations call `split`, fetch object attributes, reject deleted objects, then create a conditional reader pinned to the observed generation and metageneration. Writes create a GCS object writer and set content type or encoding only when provided. Listing parses bucket plus optional prefix, iterates `Objects`, converts iterator completion to a normal break, and wraps query errors.

## State And Persistence Behavior
The concrete client holds a `storage.Client` and context; persistent state lives remotely in GCS buckets and object metadata. `FileReader` uses generation preconditions to avoid racing a changing object after attributes are read. `FileWriter` persists data only once the returned writer is closed successfully. `Publish` mutates the object ACL by granting `AllUsers` reader access. `DeleteFile` maps `storage.ErrObjectNotExist` to package-local `ErrFileNotFound`.

## Dependencies And Integration Points
This package depends on `cloud.google.com/go/storage`, `google.golang.org/api/iterator`, `context`, and Go I/O primitives. Callers can mock through the `Client` interface; the generated mock in `pkg/gcs/mocks` is built against this contract. Public URL construction assumes the Cloud Storage HTTP hostnames used by syzkaller dashboards or reports.

## Risks And Edge Cases
`split` rejects paths without a slash; `ListObjects` treats that error as a bucket-only listing, but other methods return it. `UploadFile` ignores `Close` errors from the client itself because it is deferred without checking. If `io.Copy` fails, it attempts to close the writer but returns only the copy error. Publishing after upload is a second operation, so upload success with ACL failure is possible. `GetDownloadURL` only trims leading slash, not `gs://`, so callers must pass normalized `bucket/object` strings.

## Test Signals
Useful coverage would verify mocked `UploadFile` call ordering, `gs://` trimming, writer close failure propagation, publish-on-demand behavior, delete miss normalization, bucket-only `ListObjects`, and URL prefix selection. The presence of a generated testify mock indicates downstream tests are expected to isolate this package from live GCS.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/gcs/gcs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/gcs/mocks/Client.go -->
# sources/test-tools/syzkaller/pkg/gcs/mocks/Client.go

## Purpose
`Client.go` is a generated testify/mock implementation of `pkg/gcs.Client`. It supports unit tests for code that depends on GCS without using the real Cloud Storage service.

## Important APIs, Types, And Functions
`NewClient(t)` constructs a `*Client`, registers the test object, and adds a cleanup hook that asserts expectations. `Client` embeds `mock.Mock`. `EXPECT` returns a typed `Client_Expecter`. Each GCS interface method has a mock implementation plus a typed call wrapper: `Close`, `DeleteFile`, `FileExists`, `FileReader`, `FileWriter`, `ListObjects`, and `Publish`. Call wrappers expose typed `Run`, `Return`, and `RunAndReturn` helpers.

## Control Flow
Each mock method calls `_mock.Called(...)`, panics if no return value was configured, then resolves return values either from static mock return slots or typed callback functions. The expecter helpers call `_e.mock.On` with the method name and arguments, returning a typed wrapper around `*mock.Call`. `NewClient` uses `t.Cleanup` to assert all expectations when the test ends.

## State And Persistence Behavior
All state is in the embedded testify mock: expected calls, received calls, dynamic return functions, and assertion state. The file has no persistent storage behavior and no live GCS interaction. Returned `io.ReadCloser`, `io.WriteCloser`, and `[]*gcs.Object` values are supplied by tests.

## Dependencies And Integration Points
The mock imports `github.com/google/syzkaller/pkg/gcs` for `Object`, `io` for reader/writer types, and `github.com/stretchr/testify/mock`. It is generated by mockery and should be regenerated when the `gcs.Client` interface changes.

## Risks And Edge Cases
Because the file is generated, manual edits are likely to be overwritten. Missing `Return` or `RunAndReturn` setup causes panics at call time, which is useful but can obscure higher-level failures. Type assertions on returned values require tests to provide exact compatible types. The cleanup assertion means unexpected call count mismatches surface at test cleanup, not necessarily at the call site.

## Test Signals
Tests using `mocks.NewClient(t)` should configure every expected `Client` method and rely on cleanup assertions. Changes to `gcs.Client` should be accompanied by mock regeneration and compilation of users to catch drift.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/gcs/mocks/Client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/gerrit/gerrit.go -->
# sources/test-tools/syzkaller/pkg/gerrit/gerrit.go

## Purpose
`gerrit.go` provides a small authenticated client for creating Linux Gerrit code-review changes, specifically against `https://linux-review.googlesource.com`.

## Important APIs, Types, And Functions
`CreateChange(ctx, repo, branch, baseCommit, description, diff)` maps a repository URL to a Gerrit project, builds a change creation request, posts it, and returns the Gerrit change number plus browser link. The private `request` helper performs authenticated JSON POSTs to Gerrit REST endpoints and decodes JSON responses after stripping Gerrit's XSSI prefix. `host` is the fixed Gerrit base URL.

## Control Flow
`CreateChange` calls `projectForRepo`, builds a request map with project, branch, subject, base commit, and inline patch content, then asks `request` to post to `changes/`. It constructs the returned link from the fixed host, project, and response `_number` regardless of whether `request` returns an error. `request` obtains a Google default token source with the Gerrit code review scope, JSON-marshals the request map, creates a context-bound `POST` to `/a/<api>`, executes it through an OAuth2 HTTP client, reads the response body, checks status, trims the `)]}'\n` XSSI prefix, and unmarshals into the caller-supplied response.

## State And Persistence Behavior
There is no local persistence. Remote state is created in Gerrit when the POST succeeds. Authentication state comes from Application Default Credentials and OAuth2 token handling. The request body is fully buffered in memory.

## Dependencies And Integration Points
The file depends on `golang.org/x/oauth2`, `golang.org/x/oauth2/google`, `net/http`, and JSON encoding. It integrates with `repos.go` for supported repository mapping and likely with syzkaller automation that creates kernel review changes from generated diffs.

## Risks And Edge Cases
The package has a hard-coded Gerrit host and scope. `CreateChange` computes a link even when posting fails, which may give callers a non-empty link with `changeID` zero. `request` reports response bodies on non-2xx errors, useful for diagnostics but potentially verbose. JSON marshal failures are unlikely because the request map contains simple types. There is no retry or rate-limit handling.

## Test Signals
Direct tests would need to inject HTTP or token sources, but the current code has fixed construction, so unit testing `request` is awkward without refactoring. Existing test coverage is focused on repository mapping in `repos_test.go`; integration testing would require real or fake Gerrit credentials.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/gerrit/gerrit.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/gerrit/repos.go -->
# sources/test-tools/syzkaller/pkg/gerrit/repos.go

## Purpose
`repos.go` defines the whitelist mapping from Linux kernel repository clone URLs to Linux Gerrit project names accepted by `CreateChange`.

## Important APIs, Types, And Functions
`projectForRepo(repo)` returns the Gerrit project string or an unsupported-repository error. The package-level `projects` map is initialized by a function that enumerates supported kernel.org repository suffixes and emits URL variants for `git://git.kernel.org`, `https://git.kernel.org`, and `https://kernel.googlesource.com`.

## Control Flow
At package initialization, `kernelOrgRepos` is iterated. For every repo suffix, `project` is set to `linux/kernel/git/<repo>`, and three canonical clone URL forms are inserted into the map. `projectForRepo` performs an exact string lookup and returns an error if the lookup yields the zero string.

## State And Persistence Behavior
The only state is immutable in-process package data after init. There is no persistence, network access, or dynamic discovery of Gerrit projects.

## Dependencies And Integration Points
The file imports only `fmt`. It is consumed by `gerrit.go` before change creation. The supported set encodes syzkaller policy about which kernel.org repositories are mirrored in Linux Gerrit.

## Risks And Edge Cases
The lookup is exact and does not normalize trailing slashes, missing `.git`, SSH URLs, or alternate mirrors. Unsupported but valid kernel.org repos are rejected intentionally. Adding a repository requires code change and test updates. A repo with an empty project string would be indistinguishable from missing, though this initializer never creates such entries.

## Test Signals
`repos_test.go` verifies three accepted URL forms and one unsupported valid repo. Additional tests could cover every suffix, missing `.git`, and future URL forms if support expands.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/gerrit/repos.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/gerrit/repos_test.go -->
# sources/test-tools/syzkaller/pkg/gerrit/repos_test.go

## Purpose
`repos_test.go` validates the Gerrit repository URL mapping used before change creation.

## Important APIs, Types, And Functions
The file defines `TestProjectForRepo`, using `github.com/stretchr/testify/require` to assert `projectForRepo` behavior for accepted and rejected inputs.

## Control Flow
The test runs four sub-blocks inside one test function. It checks `git://git.kernel.org/.../torvalds/linux.git`, `https://git.kernel.org/.../bpf/bpf-next.git`, and `https://kernel.googlesource.com/.../davem/net.git`, then asserts that `ast/bpf.git` returns an error because it is valid upstream but not mirrored by this package's whitelist.

## State And Persistence Behavior
The test uses only in-memory package initialization state. It does not mutate files, call Gerrit, or require credentials.

## Dependencies And Integration Points
It depends on `testing` and testify `require`. It directly exercises the package-private `projectForRepo` because the test is in package `gerrit`, not `gerrit_test`.

## Risks And Edge Cases
The test samples representative URL forms but does not exhaustively verify the whitelist. Because all cases are inside one function without `t.Run`, failure messages rely on line numbers rather than named cases. It does not test malformed URLs, missing `.git`, or future supported hosts.

## Test Signals
This is the primary unit signal for repository mapping. If new repositories or URL forms are added, this test should be extended to demonstrate both accepted and intentionally rejected inputs.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/gerrit/repos_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/hash/hash.go -->
# sources/test-tools/syzkaller/pkg/hash/hash.go

## Purpose
`hash.go` provides syzkaller's compact SHA-1 based signature helpers for hashing arbitrary typed pieces into deterministic identifiers.

## Important APIs, Types, And Functions
`Sig` is a fixed `[sha1.Size]byte` digest. `Hash(pieces ...any)` produces a `Sig`. `String(pieces ...any)` returns the hex digest string. `(*Sig).String()` hex-encodes an existing signature. `(*Sig).Truncate64()` interprets the first eight digest bytes as a little-endian `int64`.

## Control Flow
`Hash` creates a SHA-1 hasher and processes each piece. Strings are converted to byte slices before writing. It first attempts `binary.Write` with little-endian encoding. If binary writing is unsupported, it JSON-marshals the value, assigns the marshalled bytes back to `data`, and retries the binary write through a `goto`. Finally it copies the SHA-1 sum into a `Sig`. `Truncate64` reads the digest prefix into an `int64` and panics on the impossible read error.

## State And Persistence Behavior
The package is stateless and deterministic for the same inputs and Go JSON encoding behavior. It persists nothing. Hash output depends on the order and binary or JSON representation of each piece.

## Dependencies And Integration Points
It uses `crypto/sha1`, `encoding/binary`, `encoding/hex`, `encoding/json`, and `bytes`. It likely feeds IDs, signatures, and deduplication keys across syzkaller components where stable compact strings are needed.

## Risks And Edge Cases
There is no explicit separator or type tag between pieces, so callers must avoid ambiguous concatenations where binary encodings can collide semantically. For unsupported data, JSON marshalling can fail and panic. SHA-1 is not collision-resistant for adversarial security use; this helper should be treated as a stable content signature, not a cryptographic trust boundary. `String` has a pointer receiver on `Sig`, but calling it on addressable values is handled by Go method rules.

## Test Signals
`hash_test.go` checks basic inequality for empty versus non-empty bytes, different strings, and different struct field values. Stronger tests could pin exact digest outputs for compatibility and exercise `Truncate64`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/hash/hash.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/hash/hash_test.go -->
# sources/test-tools/syzkaller/pkg/hash/hash_test.go

## Purpose
`hash_test.go` provides basic regression coverage for the `hash` package's ability to distinguish different input values.

## Important APIs, Types, And Functions
`TestHash` calls `String` on byte slices, strings, and a small struct type `X{Int int}`.

## Control Flow
The test compares `String([]byte{})` with `String([]byte{0})`, `String("foo")` with `String("bar")`, and `String(X{0})` with `String(X{1})`. Any equality triggers `t.Fatal("equal hashes")`.

## State And Persistence Behavior
The test is pure and in-memory. It relies on deterministic hashing and JSON encoding for the struct case.

## Dependencies And Integration Points
It imports only `testing` and runs in package `hash`, giving direct access to exported helpers. It is a lightweight signal for package consumers that values are not trivially collapsed.

## Risks And Edge Cases
The test does not pin exact hashes, so accidental output format changes could go unnoticed if inequality remains. It does not test multi-piece ambiguity, panic behavior, nil values, or `Truncate64`.

## Test Signals
A failure means `Hash` or `String` is seriously broken for common input classes. Passing does not prove cross-version stability or collision resistance.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/hash/hash_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/html/html.go -->
# sources/test-tools/syzkaller/pkg/html/html.go

## Purpose
`html.go` centralizes syzkaller dashboard template creation and formatting helpers shared by HTML and text templates.

## Important APIs, Types, And Functions
`SetGlobSearchPath`, `CreateGlob`, and `CreateTextGlob` manage template loading. `Funcs` exports template functions including link generation, time/date/duration formatting, repro-level rendering, hash truncation, list formatting, pointer dereference, bisect selection, and commit links. Exported `FormatTime` and `FormatDate` provide reusable date strings. Private helpers include `link`, `optlink`, `formatKernelTime`, `formatJSTime`, `formatClock`, `formatDuration`, `formatLateness`, `formatReproLevel`, `formatStat`, `formatShortHash`, `formatTagHash`, `formatCommitTableTitle`, `formatStringList`, `selectBisect`, `dereferencePointer`, and `commitLink`.

## Control Flow
At package load, `globSearchPath` is selected based on `appengine.IsAppEngine()`. `CreateGlob` and `CreateTextGlob` reject path-like globs, join the glob with the configured search path, attach `Funcs`, and parse matching templates. Formatting helpers generally return an empty string for zero values. `formatDuration` emits compact day/hour/minute strings with different precision depending on magnitude. `selectBisect` prefers fix bisection over cause bisection. `dereferencePointer` unwraps a non-nil pointer if the pointed value can be interfaced.

## State And Persistence Behavior
The mutable package-level `globSearchPath` controls future template parsing and can be overridden by tests or callers. No persistent state is written. Template parsing reads files from disk. `runtime.KeepAlive(SetGlobSearchPath)` preserves the externally used setter from dead-code removal assumptions.

## Dependencies And Integration Points
The file depends on Go `html/template` and `text/template`, `appengine`, `dashboard/dashapi` repro and bisect types, and `pkg/vcs` for commit links. It is a foundational dependency for dashboard pages and email/text template rendering.

## Risks And Edge Cases
`link` escapes link text but interpolates the URL directly into an HTML attribute, so callers must avoid untrusted unsafe URLs. `dereferencePointer` calls `IsNil` before checking kind; passing a non-nilable non-pointer interface would panic, so template use must pass pointers or nilable kinds. Template parse failures panic via `template.Must`, appropriate for startup but not for dynamic user input. The global search path is mutable and not synchronized.

## Test Signals
Expected tests should cover formatting edge cases, AppEngine versus local template paths, template helper registration, link escaping, and pointer dereference behavior. This source set does not include direct tests for `html.go`, but `pages/stats_test.go` indirectly exercises embedded template creation and helpers.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/html/html.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/html/pages/common.js -->
# sources/test-tools/syzkaller/pkg/html/pages/common.js

## Purpose
`common.js` supplies client-side behaviors embedded into syzkaller HTML pages: sortable tables, dynamic repeated input groups, collapsible sections, and AI/manual workflow form visibility.

## Important APIs, Types, And Functions
Sorting helpers include `sortTable`, `findColumnByName`, `isSorted`, and converters `textSort`, `numSort`, `floatSort`, `reproSort`, `patchedSort`, `lineSort`, and `timeSort`. Form helpers include `findAncestorByClass`, `deleteInputGroup`, `addInputGroup`, `displayAICreateJobArgs`, and `showManualWorkflowFields`. DOM event handlers are registered for `DOMContentLoaded` collapsible clicks and `load` initialization.

## Control Flow
`sortTable` climbs from the clicked element to the containing table, finds the named header column, extracts text or `sort-value` attributes from body rows, converts values, toggles sort direction based on current ordering, sorts rows, and appends them back to the table body. Input group deletion clears the only remaining group or removes the selected group; addition clones the last group and clears its input. Collapsible handling delegates clicks and toggles show/hide classes when the header is clicked. AI job helpers show or hide base-commit and workflow-specific fields while disabling inputs in hidden groups.

## State And Persistence Behavior
State is entirely in the browser DOM: row order, class lists, input values, inline `style.display`, and input disabled flags. There is no local storage or network access.

## Dependencies And Integration Points
The script is embedded by `pkg/html/pages/pages.go` into dashboard pages. It assumes table header text matches sort calls, forms use classes such as `input-group`, `input-values`, `collapsible`, and `manual-workflow-fields`, and workflow field containers use IDs derived from workflow names.

## Risks And Edge Cases
Many variables are assigned without `let` or `var`, creating globals and possible collisions. `sortTable` depends on a fixed ancestor depth and may break if markup changes. Numeric converters return `NaN` for empty or malformed values except where special cases are handled. `findAncestorByClass` returns `null` if no ancestor matches, and callers do not always guard every subsequent use. Dynamic IDs built from workflow names require safe name characters.

## Test Signals
There are no JS tests in this source set. Practical coverage would use browser or DOM tests for table sort direction toggling, form clone/delete behavior, collapsible event delegation, and workflow field enable/disable transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/html/pages/common.js -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/html/pages/pages.go -->
# sources/test-tools/syzkaller/pkg/html/pages/pages.go

## Purpose
`pages.go` builds self-contained HTML templates by embedding shared CSS and JavaScript into a reusable head template.

## Important APIs, Types, And Functions
`Create(page string)` replaces the first `{{HEAD}}` placeholder with the generated head block and parses the page using `html.Funcs`. `CreateFromFS(fs, patterns...)` creates a base template named `syz-head` from the embedded head block and parses template files from an `fs.FS`. `getHeadTemplate` formats embedded `style.css` and `common.js` into `<style>` and `<script>` tags. `style` and `js` are populated by `go:embed`.

## Control Flow
For string templates, `Create` performs a single placeholder replacement before parsing. For filesystem templates, `CreateFromFS` first parses the head template, then parses all requested patterns into the same template set. Both paths panic on parse errors through `template.Must`.

## State And Persistence Behavior
The embedded CSS and JS are compile-time assets. Template creation is in-memory and has no persistence. The returned templates can later execute with caller-provided data.

## Dependencies And Integration Points
The file depends on Go embedding, `html/template`, `io/fs`, and `pkg/html` for shared template functions. It integrates directly with page-specific files such as `stats.go`, which calls `Create` for an embedded template.

## Risks And Edge Cases
`Create` replaces only the first `{{HEAD}}`; missing placeholders still produce a valid template without the shared head. Embedding raw CSS and JS means any syntax or escaping problem affects every generated page. Parse failures panic, which is suitable for static templates but requires tests to catch bad template edits.

## Test Signals
`stats_test.go` indirectly confirms that `Create` can parse the embedded stats template with shared head assets. Additional tests could verify `CreateFromFS`, missing or repeated head placeholders, and helper availability.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/html/pages/pages.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/html/pages/stats.go -->
# sources/test-tools/syzkaller/pkg/html/pages/stats.go

## Purpose
`stats.go` renders syzkaller statistics graphs as embeddable HTML.

## Important APIs, Types, And Functions
`StatsHTML() (template.HTML, error)` renders the embedded `stats.html` template using graph data from `stat.RenderGraphs`. `statsTemplate` is initialized with `Create(statsHTML)`. `statsHTML` is embedded at compile time.

## Control Flow
`StatsHTML` creates a buffer, obtains render data from `stat.RenderGraphs`, executes the pre-parsed template into the buffer, wraps execution errors with context, and returns the rendered string as `template.HTML`.

## State And Persistence Behavior
The template is parsed at package initialization and retained globally. Rendering is in-memory. Returning `template.HTML` marks the output as trusted to callers, so escaping responsibility lies in template construction and data safety.

## Dependencies And Integration Points
The file imports `pkg/stat` for graph data, `html/template` for the trusted HTML type, and uses `pages.Create` to include common CSS/JS and template functions. It is likely consumed by dashboard pages that embed stats blocks.

## Risks And Edge Cases
Package initialization panics if the embedded template cannot parse. Because output is marked trusted, any unescaped unsafe data in `stats.html` or `stat.RenderGraphs` would bypass downstream escaping. Errors are only possible during execution, not parse, because parse already happened globally.

## Test Signals
`stats_test.go` calls `StatsHTML` and fails on execution error, catching template/data mismatches and parse-time issues during test startup.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/html/pages/stats.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/html/pages/stats_test.go -->
# sources/test-tools/syzkaller/pkg/html/pages/stats_test.go

## Purpose
`stats_test.go` verifies that the embedded stats page can render successfully.

## Important APIs, Types, And Functions
`TestStatsHTML` calls `StatsHTML` and reports any returned error through `t.Fatal`.

## Control Flow
The test invokes the render path once. Any package init parse panic or template execution error fails the test.

## State And Persistence Behavior
The test is in-memory and uses whatever graph data `stat.RenderGraphs` returns. It writes no files and performs no network calls.

## Dependencies And Integration Points
It depends only on Go `testing` directly, while indirectly covering `pages.Create`, embedded CSS/JS, `stats.html`, and `pkg/stat` graph rendering.

## Risks And Edge Cases
The test does not inspect rendered output, so missing sections, unsafe HTML, or broken client-side scripts can pass as long as template execution succeeds. It does not exercise `CreateFromFS`.

## Test Signals
This is a smoke test for stats template validity. It should fail quickly after incompatible changes to template fields or helper functions.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/html/pages/stats_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/html/urlutil/urls.go -->
# sources/test-tools/syzkaller/pkg/html/urlutil/urls.go

## Purpose
`urls.go` provides small helpers for manipulating query parameters in dashboard URLs.

## Important APIs, Types, And Functions
`SetParam(baseURL, key, value)` sets a query parameter to a single value or removes it when `value` is empty. `DropParam(baseURL, key, value)` removes either all values for a key or only matching key-value pairs. `TransformParam(baseURL, key, f)` is the generic primitive that passes existing values to a transformer and writes the returned values back.

## Control Flow
`SetParam` delegates to `TransformParam` with a transformer that returns nil for empty values or a one-element slice otherwise. `DropParam` delegates with a transformer that returns nil for remove-all or filters out values equal to the requested value. `TransformParam` returns empty string for empty or unparsable URLs, parses the URL, obtains `url.Values`, transforms `values[key]`, deletes the key if the returned slice is empty, otherwise assigns the returned slice, re-encodes the query, and returns the serialized URL.

## State And Persistence Behavior
All behavior is pure string transformation. There is no persistent state. Query encoding may normalize parameter ordering and escaping according to `net/url.Values.Encode`.

## Dependencies And Integration Points
The file depends only on Go `net/url`. It is intended for HTML/dashboard code that needs to build filter, toggle, or navigation URLs.

## Risks And Edge Cases
The helper treats empty output from the transformer as deletion, so callers cannot intentionally keep a key with zero values. Parse errors and empty input collapse to an empty string, which may hide bad caller input. `SetParam` overwrites duplicate values by design. Query parameter order is canonicalized by `Encode`, which can change visual URL ordering.

## Test Signals
`urls_test.go` covers `DropParam` for all-values and single-value removal with duplicate keys. Additional useful tests would cover `SetParam`, invalid URLs, encoding behavior, and transformer functions that preserve multiple values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/html/urlutil/urls.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/html/urlutil/urls_test.go -->
# sources/test-tools/syzkaller/pkg/html/urlutil/urls_test.go

## Purpose
`urls_test.go` verifies query-parameter removal behavior for URL helper functions.

## Important APIs, Types, And Functions
`TestDropParam` defines table-driven cases for `DropParam` and uses testify `assert.Equal` for comparisons.

## Control Flow
The test iterates four cases: removing a key entirely, removing a second key while preserving duplicate first keys, removing all duplicates for a key, and removing only a specific duplicate value. Each case calls `DropParam` and compares to the expected URL string.

## State And Persistence Behavior
The test is pure and in-memory. It relies on deterministic `net/url` query encoding order for the provided keys.

## Dependencies And Integration Points
It imports `testing` and `github.com/stretchr/testify/assert`. It exercises only `DropParam`, indirectly covering `TransformParam`.

## Risks And Edge Cases
There are no cases for `SetParam`, invalid URLs, encoded characters, fragments, absolute URLs, or retaining a key with an empty value. Because `assert` continues after failures, multiple mismatches can be reported in one run.

## Test Signals
A failure indicates a regression in duplicate-value filtering or query deletion. Passing gives confidence for common dashboard filter-removal links.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/html/urlutil/urls_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifaceprobe/ifaceprobe.go -->
# sources/test-tools/syzkaller/pkg/ifaceprobe/ifaceprobe.go

## Purpose
`ifaceprobe.go` implements the dynamic phase of automatic kernel interface extraction. It discovers filesystem interface paths under `/dev`, `/sys`, `/proc`, `/selinux`, and the executor working directory, probes operations on those files, collects coverage, and maps PCs back to kernel source locations.

## Important APIs, Types, And Functions
`Info` is the top-level result with `Files []FileInfo` and `PCs []PCInfo`. `FileInfo` stores a file name and indexes into the shared PC table. `PCInfo` stores function and source-file names. `Run(ctx, cfg, features, exec)` creates a `prober` and runs it. Key methods are `run`, `submitGlob`, `onGlobDone`, `submitFile`, `constVal`, `noteError`, plus helpers `globList` and `extractFileFilter`.

## Control Flow
`Run` initializes a prober with work channels and delegates to `run`. `run` creates a symbolizer, submits all generated glob requests, starts a goroutine to close `done` after the wait group drains, then consumes completed file descriptors. For each file it combines coverage from the first two calls in every result, deduplicates PCs per file, symbolizes unseen PCs against the configured kernel object, appends non-inline frame metadata to `Info.PCs`, records PC indexes in the file, sorts coverage and files, and finally returns any asynchronously noted error. `submitGlob` sends an important executor glob request. `onGlobDone` logs expansion count, reports glob failures, filters discovered paths, and submits per-file probes. `submitFile` builds six small syzkaller programs around `openat` plus read, write, ioctl, and mmap variants, submits them, waits for each result in a goroutine, records successful results, and sends the descriptor to `done`.

## State And Persistence Behavior
All state is runtime-only: outstanding queue requests, wait-group counts, a buffered `done` channel, a single-error channel, local PC de-dup maps, and the returned `Info`. It does not persist results itself. It depends on executor-side kernel state and coverage collection; probing may interact with real device/sysfs/proc files in a sandbox-disabled environment.

## Dependencies And Integration Points
The package integrates tightly with syzkaller manager config, target constants, program deserialization, executor queue requests/results, feature flags, coverage collection, symbolization, and logging. It uses `csource.FeaturesToFlags`, `flatrpc` request and execution flags, `queue.Executor`, `symbolizer.Make`, and `prog.StrictUnsafe`.

## Risks And Edge Cases
`submitFile` assumes every successful result has at least two calls in `res.Info.Calls`; malformed executor results could panic. Probing runs with `ExecEnvSandboxNone`, so the target environment must be controlled. `extractFileFilter` panics on paths outside expected roots. Glob generation is intentionally broad and can create many requests; filters reduce but do not eliminate scale risk. Only the last non-inline frame is recorded, which may hide inline context. `noteError` records only the first error, while work continues.

## Test Signals
This file has no direct tests in the provided set. High-value tests would fake `queue.Executor` for glob and probe result ordering, verify filtering for `/proc` and `/sys` scale controls, validate PC de-duplication and sorting, and cover error propagation from glob, program execution, and symbolization.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifaceprobe/ifaceprobe.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/arm64/arm64.go -->
# sources/test-tools/syzkaller/pkg/ifuzz/arm64/arm64.go

## Purpose
`arm64.go` implements the ARM64 architecture backend for syzkaller's instruction fuzzer. It registers generated and pseudo instruction templates, encodes instructions to machine-code bytes, and decodes four-byte ARM64 instructions against known opcode masks.

## Important APIs, Types, And Functions
`InsnField` describes a named bit field with little-endian bit position and length. `Insn` stores instruction metadata: name, opcode mask and value, fields, concrete encoded value, extracted operands, pseudo/privileged flags, and optional pseudo generator. `InsnSet` stores mode-indexed instruction lists plus all instructions. `Register` installs ARM64 instructions into `iset.Arches`. `GetInsns`, `Info`, `Encode`, `Decode`, and `DecodeExt` implement `iset.InsnSet` and `iset.Insn`. `ParseInsn` matches a `uint32` against generated templates. Private helpers include `initFromValue` and `matchesValue`.

## Control Flow
Generated code calls `Register` during init with parsed instruction templates. `Register` appends pseudo instructions, indexes each instruction through `modeInsns.Add`, stores the set under `iset.ArchArm64`, and saves generated templates for decoding. `Encode` returns pseudo-generated bytes when `Pseudo` is true, otherwise emits `AsUInt32` as four little-endian bytes. `Decode` requires at least four input bytes, reads one word little-endian, calls `ParseInsn`, and returns length four on success. `ParseInsn` scans templates in order, clones the first matching template, extracts operands from its fields, and returns an error with an `unknown` instruction if no mask matches.

## State And Persistence Behavior
Package-level `templates` and the global `iset.Arches` registry are initialized at runtime by generated package imports. There is no persistence. Instruction generation is deterministic for fixed template state except pseudo instructions, which use caller-provided randomness.

## Dependencies And Integration Points
The file depends on `encoding/binary`, `math/rand`, and `pkg/ifuzz/iset`. It is fed by `pkg/ifuzz/arm64/generated`, which is generated from `gen/gen.go`, and interacts with pseudo generation in `pseudo.go` and bit extraction in `util.go`. The top-level `pkg/ifuzz` imports generated packages for registration.

## Risks And Edge Cases
`Register` panics on an empty instruction list. `ParseInsn` is linear in template count and first-match wins, so generated template ordering matters for overlapping masks. `DecodeExt` is deliberately unsupported and returns an error, which tests must accept for ARM64. `Info` reports support only for `ModeLong64`. If generated registration is not imported, decoding has no templates.

## Test Signals
Expected tests should cover generation, mutation, decode success/failure, pseudo instruction generation, and operand extraction. Existing nearby tests under `pkg/ifuzz` and `arm64/util_test.go` likely provide broader package coverage, while this specific source set includes no direct ARM64 test file.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/arm64/arm64.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/arm64/gen/gen.go -->
# sources/test-tools/syzkaller/pkg/ifuzz/arm64/gen/gen.go

## Purpose
`gen.go` is the ARM64 instruction-table generator. It converts JSON instruction descriptions into Go source that registers `arm64.Insn` templates.

## Important APIs, Types, And Functions
`main` is the generator entry point used by `go:generate` in `arm64.go`. `insnDesc` mirrors the relevant JSON fields: `Name`, `Bits`, `Arch`, `Syntax`, `Code`, and `Alias`. `isPrivateInsn` marks privileged/system instructions. `JSONToInsns(jsonStr)` parses JSON descriptions into `[]*arm64.Insn`.

## Control Flow
`main` requires exactly input JSON and output file arguments, reads the JSON, calls `JSONToInsns`, writes a generated Go file header and package body that imports ARM64 types, emits an init function calling `Register(insns_arm64)`, serializes the instruction slice with `serializer.Write`, atomically writes the output file, and prints the handled count to stderr. `JSONToInsns` unmarshals descriptions, then for each `Bits` string splits fields by `|`, parses optional `pattern:size` suffixes, walks from bit 31 downward, and builds opcode and mask values. Binary patterns contribute fixed opcode and mask bits. Non-binary named regions become `InsnField` entries. Patterns starting with `(` are treated as opcode-updating zero bits. Each template is marked privileged when its name is in the system instruction switch.

## State And Persistence Behavior
The generator reads one JSON file and atomically writes one Go file. It does not persist intermediate state. The generated file becomes compile-time registration state for the ARM64 backend.

## Dependencies And Integration Points
It depends on `pkg/ifuzz/arm64`, `pkg/osutil` atomic file writing, `pkg/serializer` for Go literal emission, and `pkg/tool` for fatal errors. It is invoked by the `//go:generate` directive in `arm64.go` with `gen/json/arm64.json` and `generated/insns.go`.

## Risks And Edge Cases
`JSONToInsns` returns nil on unmarshal or parse errors instead of surfacing diagnostics, so `main` may generate an empty table without a clear parse failure except the handled count. The `pattern[0:1]` indexing assumes non-empty bit pieces. `curBit -= size` can underflow if the bit description exceeds 32 bits. Parenthesized patterns are not parsed as numeric masks and effectively update opcode/mask as zero-width fixed bits after shifting, so the JSON contract must match this behavior. Privileged classification is name-based and must be updated as instruction coverage grows.

## Test Signals
Generator tests should feed small JSON fixtures with fixed bits, named fields, sized regions, aliases, and invalid input. Downstream compile and ARM64 decode tests catch many generated-table regressions, but direct tests would make parse failures easier to diagnose.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/arm64/gen/gen.go -->
