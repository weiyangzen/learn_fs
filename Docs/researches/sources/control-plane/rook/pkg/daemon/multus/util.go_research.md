# sources/control-plane/rook/pkg/daemon/multus/util.go

Purpose: supplies logging abstraction and low-level pod/network utility functions for Multus validation.

Important APIs/types/functions: `Logger` is a minimal interface with info/debug/warning formatting methods. `SimpleStderrLogger` implements it to stderr. `getNetworksFromPod()` extracts desired public/cluster IP addresses from a pod's Multus network status. `podIsRunning()`, `podIsReady()`, and `networkNamespacedName()` are status/parsing helpers.

Control flow: `getNetworksFromPod()` calls the network-attachment-definition client utility to parse pod network status, validates that attached networks and IPs exist, parses each network name relative to the pod namespace, matches desired public/cluster `NamespacedName`s, accumulates debugging suggestions for missing or malformed data, and returns addresses only when all desired networks are present. `networkNamespacedName()` reuses `ParseNetworkAnnotation()` because the desired private parser is not exported.

State and persistence behavior: no persistence. Suggestions are returned as slices for accumulation in validation results.

Dependencies and integration points: uses `github.com/k8snetworkplumbingwg/network-attachment-definition-client/pkg/utils`, Kubernetes Pod status, and `types.NamespacedName`. It is central to `getWebServerInfoState`, because web server network discovery gates later validation phases.

Risks: `getNetworksFromPod()` reads `net.IPs[0]` after appending a suggestion for no IP but without continuing, so a network attachment with zero IPs can panic. If `networkNamespacedName()` returns an error, `nsName` remains zero-value but code still compares it after adding a suggestion. The helper treats any IP as sufficient and does not distinguish IPv4/IPv6 preferences.

Test signals: no direct tests in this subset for network parsing, no-IP behavior, or readiness helpers.
