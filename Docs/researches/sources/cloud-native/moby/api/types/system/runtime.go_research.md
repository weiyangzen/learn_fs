<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/types/system/runtime.go -->
# sources/cloud-native/moby/api/types/system/runtime.go

## Purpose
Runtime describes an OCI runtime

## Important APIs, Types, And Functions
- Exported types: Runtime, RuntimeWithStatus.
- `Runtime` fields include Path, Args, Type, Options.
- `RuntimeWithStatus` fields include Status.
- Wire JSON fields include options, path, runtimeArgs, runtimeType, status.
- Source comments highlight: Runtime describes an OCI runtime RuntimeWithStatus extends [Runtime] to hold [RuntimeStatus].

## Control Flow
- There is no active control flow; the file defines data contracts serialized by higher-level daemon/client code.

## State And Persistence
- The file stores no process-local mutable state; structs represent serialized daemon state, request options, or response bodies.
- Several fields use `omitempty`, so absent, zero, and explicitly empty values can carry different compatibility implications.
- Persistence is external: Docker daemon stores the actual objects, while these types preserve the wire representation exposed to clients.

## Dependencies And Integration Points
- Integrates as a public `api/types` wire contract used by daemon handlers, client decoding, CLI output, and downstream Go consumers.

## Risks And Edge Cases
- Public API compatibility risk: field names, JSON tags, enum strings, and zero-value behavior are consumed by external clients.

## Test Signals
- No direct test file is paired with this source; coverage is mostly integration-level through daemon/client API tests and compile-time use by downstream packages.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/types/system/runtime.go -->
