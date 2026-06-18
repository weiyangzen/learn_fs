# sources/cloud-native/nydus-snapshotter/pkg/stargz/resolver.go

## Purpose
Resolves remote stargz blobs and reads their table-of-contents data via HTTP range requests.

## Important APIs, Types, And Functions
`Resolver`, `NewResolver`, `Blob`, `Blob.GetTocOffset`, `Blob.ReadToc`, `GetDigest`, `GetImageReference`, `Resolver.GetBlob`, `parseFooter`, `resolve`, and `getSize`.

## Control Flow
`GetBlob` resolves a reference/digest/keychain into a `Blob`. `resolve` parses the Docker reference, obtains a URL and authenticated round tripper from the transport pool, determines blob size by requesting `Range: bytes=0-0` and parsing `Content-Range`, and returns a `SectionReader` backed by range GETs. `ReadToc` opens the stargz footer to find TOC offset, reads the compressed TOC region, creates a gzip reader with multistream disabled, expects the first tar entry to be `stargz.index.json`, and returns its contents.

## State And Persistence
No local persistence. The `Blob` holds image ref, digest, and a section reader that issues network range requests.

## Dependencies And Integration Points
Uses go-containerregistry auth/name, distribution reference parsing, Nydus transport resolver, `estargz.OpenFooter`, gzip/tar, and package logging. It supports lazy stargz metadata extraction for Nydus workflows.

## Risks And Edge Cases
`getSize` assumes `Content-Range` contains a slash and valid total size. Range requests accept any 2xx status, not specifically 206. Error messages say HEAD even though GET is used. Each range read creates a new request with a 15-second timeout.

## Test Signals
`resolver_test.go` uses a mock transport to validate size lookup, footer parsing, TOC range read, gzip/tar extraction, and expected TOC filename.
