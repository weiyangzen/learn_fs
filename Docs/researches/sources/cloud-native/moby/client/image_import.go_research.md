<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/image_import.go -->
# sources/cloud-native/moby/client/image_import.go

Purpose: imports an image from a source stream or named source and returns the daemon progress stream.

Important APIs/types/functions: `ImageImportResult` interface, `Client.ImageImport`, and private `imageImportResult`.

Control flow: validates non-empty `ref` with distribution reference parsing, builds query values for `fromSrc`, `repo`, `tag`, `message`, platform, and repeated `changes`, posts the raw source reader to `/images/create`, and returns a context-cancel-aware response body stream to the caller.

State and integration behavior: no local persistence; daemon creates image state. The caller owns source input and returned output stream lifecycle.

Dependencies: distribution reference parser, OCI platform formatting via `formatPlatform`, raw post helper, and `newCancelReadCloser`.

Risks and test signals: risks include invalid reference handling, ambiguous source stream ownership, platform formatting limitations, and leaked progress streams. `image_import_test.go` is outside the requested output set but exists in the package; within this subset, option type docs provide compile-time signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/image_import.go -->
