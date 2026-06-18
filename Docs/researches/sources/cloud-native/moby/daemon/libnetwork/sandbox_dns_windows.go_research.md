<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/sandbox_dns_windows.go -->
## sources/cloud-native/moby/daemon/libnetwork/sandbox_dns_windows.go

Purpose: Windows stubs for Unix-style sandbox DNS and hosts file management.

Important APIs/functions: `setupResolutionFiles`, `restoreHostsPath`, `restoreResolvConfPath`, and `deleteHostsEntries`.

Control flow: all functions are no-ops or return nil.

State and persistence: no Unix-style `/etc/hosts` or `resolv.conf` file state is managed here.

Dependencies and integration points: selected for Windows builds so shared sandbox code compiles. Windows endpoint resolver population is handled in `sandbox_windows.go`.

Risks and test signals: platform divergence is intentional; callers must not expect Unix file behavior on Windows. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/sandbox_dns_windows.go -->
