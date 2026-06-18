<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portallocator/portallocator_freebsd.go -->
## sources/cloud-native/moby/daemon/libnetwork/portallocator/portallocator_freebsd.go

Purpose: FreeBSD platform implementation for discovering the system ephemeral port range.

Important APIs/functions: `getDynamicPortRange` runs `/sbin/sysctl` for `net.inet.ip.portrange.hifirst` and `net.ip.portrange.hilast`, parses integer output, and returns start/end. `getReservedPorts` returns nil because no reserved-port integration is implemented here.

Control flow: the function executes the low and high sysctl commands separately, parsing each buffer with `fmt.Sscanf`. Any command failure or parse count mismatch becomes a descriptive error, which the shared allocator catches and replaces with default range values.

State and persistence: reads OS sysctl state only; does not write or persist allocator state.

Dependencies and integration points: depends on `/sbin/sysctl`, command execution, and the shared `dynamicPortRange` fallback behavior in `portallocator.go`.

Risks and test signals: parsing assumes sysctl output format can be scanned directly as an integer, which may depend on FreeBSD command formatting. If it fails, Docker falls back to defaults. No FreeBSD-specific tests are in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portallocator/portallocator_freebsd.go -->
