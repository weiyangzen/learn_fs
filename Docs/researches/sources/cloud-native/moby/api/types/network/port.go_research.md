<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/types/network/port.go -->
# sources/cloud-native/moby/api/types/network/port.go

## Purpose
Defines port and port-binding primitives, parsing, sorting, and conversion helpers for NAT mappings
and exposed ports.

## Important APIs, Types, And Functions
- Exported types: IPProtocol, Port, PortSet, PortBinding, PortMap, PortRange.
- Exported functions/methods: ParsePort, MustParsePort, PortFrom, Num, Port, Proto, IsZero, IsValid, String, AppendText, AppendTo, MarshalText, UnmarshalText, Range, and others.
- Constants: TCP, UDP, SCTP.
- `PortBinding` fields include HostIP, HostPort.
- Wire JSON fields include HostIp, HostPort.
- Source comments highlight: IPProtocol represents a network protocol for a port. Port is a type representing a single port number and protocol in the format "<portnum>/[<proto>]". ParsePort parses s as a [Port].
- Its parser and collection helpers are used by container/network config code and are heavily tested for wire compatibility.

## Control Flow
- Runtime behavior is limited to helper methods such as validators, stringers, comparison functions, sort methods, or error adapters.
- Predicate/validation methods compare string modes or enum values against known constants and return booleans or formatted errors.
- String/error methods expose compact human-readable representations without mutating receiver state.

## State And Persistence
- The file stores no process-local mutable state; structs represent serialized daemon state, request options, or response bodies.
- Persistence is external: Docker daemon stores the actual objects, while these types preserve the wire representation exposed to clients.

## Dependencies And Integration Points
- Imports: `errors`, `fmt`, `iter`, `net/netip`, `strconv`, `strings`, `unique`.
- Integrates as a public `api/types` wire contract used by daemon handlers, client decoding, CLI output, and downstream Go consumers.
- Uses `net/netip` typed IP/prefix values, preserving validated address semantics instead of raw strings.

## Risks And Edge Cases
- Public API compatibility risk: field names, JSON tags, enum strings, and zero-value behavior are consumed by external clients.
- Address parsing and JSON behavior depend on `netip` semantics; invalid or legacy textual addresses need explicit handling upstream.

## Test Signals
- Adjacent test file `sources/cloud-native/moby/api/types/network/port_test.go` exercises related behavior.
- Package-level tests include `hwaddr_test.go`, `port_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/types/network/port.go -->
