# sources/control-plane/rook/pkg/operator/ceph/object/admin_mock.go

## Purpose
`admin_mock.go` defines a minimal mock HTTP client for tests that need to drive go-ceph RGW Admin Ops behavior without a live RGW endpoint.

## Important APIs, Types, and Functions
`MockClient` contains a single `MockDo MockDoType` field. `MockDoType` is a function type matching the `Do(*http.Request) (*http.Response, error)` method required by go-ceph's `admin.HTTPClient`. `(*MockClient).Do()` delegates every request to `MockDo`.

## Control Flow, State, and Persistence
The mock has no internal state beyond whatever the closure assigned to `MockDo` captures. Tests use that closure to inspect request methods, paths, and query strings and to return synthetic HTTP responses. No persistent state is written.

## Dependencies and Integration Points
The file depends only on `net/http`. It is used throughout the object account and bucket tests to construct `admin.New(endpoint, accessKey, secretKey, mockClient)`, letting tests exercise go-ceph request and error handling while controlling RGW responses.

## Risks
If `MockDo` is nil, calling `Do()` panics. The mock does not enforce response-body closing or thread safety. Because request assertions live in each test closure, missed paths can either panic or return nil responses depending on the test implementation.

## Test Signals
The mock is indirectly validated by many account and bucket tests that depend on it for account, user, quota, and bucket Admin Ops behavior. It has no standalone test, which is reasonable given its tiny surface.
