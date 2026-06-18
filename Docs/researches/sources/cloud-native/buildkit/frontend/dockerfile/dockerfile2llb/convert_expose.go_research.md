# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/convert_expose.go

Purpose: converts Dockerfile `EXPOSE` instructions into image `ExposedPorts` metadata with validation and linting for protocol casing and unsupported host/IP formats.

Important APIs: `dispatchExpose`, `portSpecs`, options `withLocation`/`withLint`, and methods `parsePorts`, `parsePort`, `parsePortRange`, `parsePortNumber`, `splitProtoPort`, `splitParts`.

Control flow: variables are expanded into port words, parsed specs may include legacy `[ip:]host:container/proto` forms, protocol defaults to tcp and accepts tcp/udp/sctp, port ranges expand into individual `port/proto` strings, IPv6 forms are handled, and image config map is initialized/filled. Lints warn on non-lowercase protocol and host/IP/host-port format even while preserving legacy parsing.

State and persistence: mutates only image config and history; no filesystem layer.

Dependencies and integration: used by `dispatch` in `convert.go`; relies on shell env expansion, linter, parser ranges, and Go `net` parsing.

Risks and test signals: risks include IPv6 colon splitting, range mismatch semantics, allowing host mappings for backward compatibility, and out-of-range diagnostics. `convert_expose_test.go` covers empty ports, full forms, IPv6, protocol variants, and ranges.
