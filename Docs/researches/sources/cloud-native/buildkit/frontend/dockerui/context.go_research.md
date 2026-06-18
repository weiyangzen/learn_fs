<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerui/context.go -->
# sources/cloud-native/buildkit/frontend/dockerui/context.go

## Purpose
dockerui build context detection for local, Git, HTTP, frontend inputs, source date epoch metadata, archive unpacking, and subdirectory scoping. The file has 361 lines and belongs to package `dockerui`.

## Important APIs, Types, and Functions
Important symbols: `httpPrefix`, `buildContext`, `marshalOpts`, `initContext`, `ResolveMainContextSourceDateEpoch`, `archiveMaxTimeFromHTTPArchive`, `cloneSourceOp`, `sourceOpFromState`, `DetectGitContext`, `DetectHTTPContext`, `isArchive`, `scopeToSubDir`.

## Control Flow
initContext resolves local option names, then chooses Git, HTTP, frontend input, or local context paths; remote states are marshaled to SourceOp metadata, optional subdirectories are scoped with LLB Copy, and source-date-epoch helpers query metadata or scan archive mtimes.

## State and Persistence
buildContext holds selected context/dockerfile LLB states, source op metadata, HTTP reference details, and archive flags in memory. Remote context content is read through gateway references, not persisted by this package.

## Dependencies and Integration Points
Dependencies: BuildKit LLB state/options; BuildKit gateway client/result APIs; wrapped error reporting.
Integrated with gateway/client BuildOpts, LLB source construction, exporter metadata, frontend inputs, named contexts, .dockerignore, and source-date-epoch behavior.

## Risks and Edge Cases
Risks include misdetecting HTTP archives from short headers, remote metadata errors affecting reproducibility, Git ref option parsing, multiple source ops from composed states, and subdirectory scoping changing source roots.

## Test Signals
Covered by adjacent tests such as `sources/cloud-native/buildkit/frontend/dockerui/build_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerui/context.go -->
