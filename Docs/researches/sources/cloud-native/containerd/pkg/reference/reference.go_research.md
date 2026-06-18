<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/reference/reference.go -->
# sources/cloud-native/containerd/pkg/reference/reference.go

## Purpose
Parses schema-less containerd reference specifications into locator/object components while keeping digest and hostname helpers.

## Important APIs, Types, And Functions
Spec contains Locator and Object. Parse rejects explicit schemes, uses url.Parse with a dummy scheme, requires a host, splits object at the first path colon or at-sign, and normalizes with path.Join. Hostname, Digest, and String expose derived views.

## Control Flow
Parse builds a dummy URL, validates scheme/host, cuts object from the path with lazy regexp, strips leading colon from tag objects, and returns a normalized Spec. String reconstructs locator plus :object or @digest-only object.

## State And Persistence
No persistent state; splitRe is a lazily compiled package regexp.

## Dependencies And Integration Points
Depends on net/url, path, strings, lazyregexp, and opencontainers/go-digest. Used by remote/reference handling that accepts looser-than-Docker references.

## Risks And Edge Cases
It intentionally permits partial or invalid digest strings in Object; validation belongs to callers. path.Join cleans paths and may normalize duplicate separators.

## Test Signals
reference_test.go covers tags, digest-only refs, host ports, missing hostname, subdomains, punycode, and explicit-scheme rejection.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/reference/reference.go -->
