<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/internal/testutils/networking/l3_segment_linux.go -->
# sources/cloud-native/moby/integration/internal/testutils/networking/l3_segment_linux.go

Purpose: creates disposable Linux layer-3 network segments for integration tests, with isolated network namespaces, a bridge, veth peers, and helpers to run commands inside namespace context.

Important APIs/types/functions: `CurrentNetns` names the current namespace sentinel. `L3Segment` owns a bridge `Host` and a map of named `Host`s. `NewL3Segment` creates a bridge namespace/link with addresses. `AddHost` creates a host namespace and veth pair attached to the bridge. `Destroy` tears down hosts and bridge. `Host.Run`, `MustRun`, `Do`, and `Destroy` execute commands, enter namespaces with `netns.Set`, and clean up links/namespaces.

Control flow: `newHost` creates the namespace unless `nsName == CurrentNetns`; `Host.Run` wraps commands in `ip netns exec` when needed. `Host.Do` locks the OS thread, switches into the target namespace, runs a callback, and defers restoration of the original namespace. `AddHost` validates interface-name length, creates a veth pair, enslaves the bridge side, brings interfaces and loopback up, enables IPv4/IPv6 forwarding, and assigns requested addresses.

State/persistence: mutates host network namespace state, veth links, bridge links, sysctls, and named netns objects. Cleanup explicitly deletes veth links before namespaces to avoid delayed kernel peer cleanup causing `EEXIST` in later tests.

Dependencies/integration: depends on Linux `ip` and `sysctl`, `github.com/vishvananda/netns`, `runtime.LockOSThread`, and `syscall.IFNAMSIZ`. Bridge and firewall documentation tests use it to run Docker daemons and firewall commands in isolated namespaces.

Risks: privileged Linux-only helper; failures can leak namespaces or leave sysctl/firewall state until cleanup. Namespace switching must stay thread-locked or unrelated goroutines can observe wrong network context. `Destroy` is fatal on cleanup command failures, which may obscure original test failures.

Test signals: indirect coverage comes from bridge FORWARD-policy, backend-switch, and iptables/nftables documentation tests that depend on isolated daemons and firewall state. There is no direct unit coverage for namespace switching or partial cleanup.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/internal/testutils/networking/l3_segment_linux.go -->
