<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/network/helpers_windows.go -->
# sources/cloud-native/moby/integration/network/helpers_windows.go

Purpose: Windows build of shared network availability comparison helpers.

Important APIs/types/functions: `IsNetworkAvailable` and `IsNetworkNotAvailable` return `gotest.tools/v3/assert/cmp.Comparison` closures that list Docker networks and check whether a network name is present or absent.

Control flow: each closure calls `NetworkList`, propagates API errors as comparison errors, scans returned items by `Name`, and returns success/failure with a formatted message.

State/persistence: read-only; no network creation or host interface mutation.

Dependencies/integration: Docker `client.NetworkAPIClient`, context, and gotest `cmp`. It mirrors the portable subset of the Linux helper file without `ip`/`iptables` functions.

Risks: checks only by name, so duplicate names or ambiguous IDs are outside scope. Network-list API failures become assertion failures in callers.

Test signals: Windows network tests use these comparisons for default network availability and create/delete assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/network/helpers_windows.go -->
