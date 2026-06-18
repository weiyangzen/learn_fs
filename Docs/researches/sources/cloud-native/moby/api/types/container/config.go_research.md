<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/types/container/config.go -->
# sources/cloud-native/moby/api/types/container/config.go

## Purpose
MinimumDuration puts a minimum on user configured duration.

## Important APIs, Types, And Functions
- Exported types: HealthConfig, Config.
- Constants: MinimumDuration.
- `Config` fields include Hostname, Domainname, User, AttachStdin, AttachStdout, AttachStderr, ExposedPorts, Tty, OpenStdin, StdinOnce, Env, Cmd, Healthcheck, ArgsEscaped, and others.
- Source comments highlight: MinimumDuration puts a minimum on user configured duration. HealthConfig holds configuration settings for the HEALTHCHECK feature. Config contains the configuration data about a container.

## Control Flow
- There is no active control flow; the file defines data contracts serialized by higher-level daemon/client code.

## State And Persistence
- The file stores no process-local mutable state; structs represent serialized daemon state, request options, or response bodies.
- Several fields use `omitempty`, so absent, zero, and explicitly empty values can carry different compatibility implications.
- Persistence is external: Docker daemon stores the actual objects, while these types preserve the wire representation exposed to clients.

## Dependencies And Integration Points
- Imports: `time`, `github.com/moby/docker-image-spec/specs-go/v1`, `github.com/moby/moby/api/types/network`.
- Integrates as a public `api/types` wire contract used by daemon handlers, client decoding, CLI output, and downstream Go consumers.
- Carries timestamp or duration fields that must remain JSON-compatible across daemon/client boundaries.

## Risks And Edge Cases
- Public API compatibility risk: field names, JSON tags, enum strings, and zero-value behavior are consumed by external clients.

## Test Signals
- Adjacent test file `sources/cloud-native/moby/api/types/container/config_test.go` exercises related behavior.
- Package-level tests include `config_test.go`, `health_test.go`, `hostconfig_test.go`, `hostconfig_unix_test.go`, `state_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/types/container/config.go -->
