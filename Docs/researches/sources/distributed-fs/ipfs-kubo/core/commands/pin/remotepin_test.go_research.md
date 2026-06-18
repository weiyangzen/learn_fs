# sources/distributed-fs/ipfs-kubo/core/commands/pin/remotepin_test.go

## Purpose

`pin/remotepin_test.go` validates `normalizeEndpoint`, the helper that canonicalizes and rejects invalid remote pinning service API endpoints before they are stored in repo config.

## Important APIs, Types, and Functions

The file defines `TestNormalizeEndpoint`, a table-driven test calling unexported `normalizeEndpoint` from `remotepin.go`.

## Control Flow

Each case supplies an input endpoint, expected error text, and expected normalized output. Covered cases include bare HTTPS, trailing slash removal, rejecting `/pins` and `/pins/`, cleaning redundant path elements and slashes, rejecting query parameters, accepting HTTP with host/port, and rejecting unsupported schemes.

## State and Persistence Behavior

The test is pure. It does not create services, write config, or contact remote endpoints.

## Dependencies and Integration Points

It depends only on Go `testing` and the implementation helper. The test protects `pin remote service add` because that command persists normalized endpoints to `Pinning.RemoteServices`.

## Risks and Test Signals

The test gives direct signal on endpoint canonicalization and common user mistakes. Remaining gaps include uppercase schemes/hosts, credentials in URLs, fragments, empty hosts, IPv6 literals, percent-encoded paths, duplicate slashes immediately after host, and asserting that a nil error is required when `tc.err` is empty.
