# sources/distributed-fs/juicefs/pkg/object/swift.go

Purpose: implements an OpenStack Swift object backend behind `swift`.

Important APIs and types: `swiftOSS` holds a Swift connection, region, storage URL, and container. It implements `Create`, `Get`, `Put`, `Delete`, `List`, `Head`, and `newSwiftOSS`.

Control flow and state: `newSwiftOSS` parses `container.host`, builds a v1 auth URL at `/auth/v1.0`, uses username/API key/token, and authenticates with the shared HTTP transport. `Get` uses Range headers for partial reads. `Put` guesses MIME type. `Delete` treats `swift.ObjectNotFound` as success. `List` validates a single-rune delimiter, maps Swift pseudo directories to directory objects, and uses `generateListResult`. `Head` maps object-not-found to `os.ErrNotExist`.

Persistence and integration: objects persist in the configured Swift container. This backend embeds `DefaultObjectStorage`, so unsupported operations fall back to default behavior.

Risks and test signals: only v1 auth is supported. Delimiter must be one rune. The transport type assertion assumes the shared HTTP client uses `*http.Transport`. No Swift-specific tests are included.
