# sources/distributed-fs/seaweedfs/weed/s3api/s3api_nextmarker_test.go

## Purpose
Tests marker construction for S3 list continuation when requests use nested prefixes. It guards a regression where `NextMarker` lost intermediate prefix components.

## Important APIs, Types, And Functions
`TestNextMarkerWithNestedPrefix` and `TestNextMarkerWithCommonPrefix` simulate the string-building logic used by list operations. They use `requestDir`, `prefix`, `nextMarkerFromDoList`, and `lastCommonPrefixName` inputs and compare against expected final markers via `testify/assert`.

## Control Flow
Object marker tests prepend `requestDir` and, when present, `prefix` before the marker returned by lower-level listing. Common-prefix tests perform the same reconstruction but add the trailing slash required for prefix markers. Cases cover requestDir plus prefix, requestDir only, prefix without requestDir, and deeper nesting.

## State And Persistence
No state is persisted. These are pure string construction regression tests.

## Dependencies And Integration Points
The behavior corresponds to marker assembly inside S3 list handling, particularly `listFilerEntries`/`doList` interactions where lower layers may return names relative to the listed directory.

## Risks And Test Signals
The tests catch continuation-token/marker drift that can cause clients to skip, repeat, or fail pages under nested prefixes. They are simulations, so a direct handler test with actual filer entries would provide stronger coverage for delimiter and encoding interactions.
