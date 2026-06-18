<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/types/swarm/container.go -->
# sources/cloud-native/moby/api/types/swarm/container.go

## Purpose
DNSConfig specifies DNS related configurations in resolver configuration file (resolv.conf) Detailed
documentation is available in: http://man7.org/linux/man-pages/man5/resolv.conf.5.html `nameserver`,
`search`, `options` have been supported.

## Important APIs, Types, And Functions
- Exported types: DNSConfig, SELinuxContext, SeccompMode, SeccompOpts, AppArmorMode, AppArmorOpts, CredentialSpec, Privileges, ContainerSpec.
- Constants: SeccompModeDefault, SeccompModeUnconfined, SeccompModeCustom, AppArmorModeDefault, AppArmorModeDisabled.
- `DNSConfig` fields include Nameservers, Search, Options.
- `SELinuxContext` fields include Disable, User, Role, Type, Level.
- `SeccompOpts` fields include Mode, Profile.
- `AppArmorOpts` fields include Mode.
- `CredentialSpec` fields include Config, File, Registry.
- Source comments highlight: DNSConfig specifies DNS related configurations in resolver configuration file (resolv.conf) Detailed documentation is available in: http://man7.org/linux/man-pages/man5/resolv.conf.5.html `nameserver`, `search`, `options` have been supported. SELinuxContext contains the SELinux labels of the container. SeccompMode is the type used for the enumeration of possible seccomp modes in SeccompOpts

## Control Flow
- There is no active control flow; the file defines data contracts serialized by higher-level daemon/client code.

## State And Persistence
- The file stores no process-local mutable state; structs represent serialized daemon state, request options, or response bodies.
- Several fields use `omitempty`, so absent, zero, and explicitly empty values can carry different compatibility implications.
- Persistence is external: Docker daemon stores the actual objects, while these types preserve the wire representation exposed to clients.

## Dependencies And Integration Points
- Imports: `net/netip`, `time`, `github.com/moby/moby/api/types/container`, `github.com/moby/moby/api/types/mount`.
- Integrates as a public `api/types` wire contract used by daemon handlers, client decoding, CLI output, and downstream Go consumers.
- Uses `net/netip` typed IP/prefix values, preserving validated address semantics instead of raw strings.
- Carries timestamp or duration fields that must remain JSON-compatible across daemon/client boundaries.

## Risks And Edge Cases
- Public API compatibility risk: field names, JSON tags, enum strings, and zero-value behavior are consumed by external clients.
- Address parsing and JSON behavior depend on `netip` semantics; invalid or legacy textual addresses need explicit handling upstream.
- Duration and timestamp fields need stable units and timezone/zero-value behavior across API versions.

## Test Signals
- Package-level tests include `network_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/types/swarm/container.go -->
