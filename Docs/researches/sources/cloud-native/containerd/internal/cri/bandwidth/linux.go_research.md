# sources/cloud-native/containerd/internal/cri/bandwidth/linux.go

## Purpose

`linux.go` implements the `Shaper` interface with Linux `tc` hierarchical token bucket classes and u32 filters.

## Important APIs, Types, and Functions

- `tcShaper` stores an exec interface and network interface name.
- `NewTCShaper` constructs a `tcShaper`.
- `execAndLog` runs `tc` commands and logs command/output.
- `nextClassID` parses `tc class show` output to find an unused `1:<n>` class ID below 10000.
- `hexCIDR` and `asciiCIDR` convert CIDRs between text and `tc` filter hex representation.
- `findCIDRClass` parses `tc filter show` output to find class/handle pairs for a CIDR.
- `Limit` creates HTB classes and dst/src filters for download/upload limits.
- `ReconcileInterface`, `initializeInterface`, `deleteInterface`, `ReconcileCIDR`, `Reset`, and `GetCIDRs` maintain and inspect shaping state.

## Control Flow

Callers normally call `ReconcileInterface` to ensure root qdisc `1:` exists, then `ReconcileCIDR` or `Limit` for each pod CIDR. `Limit` allocates classes and adds filters for non-nil ingress/download and egress/upload quantities. `Reset` finds all classes/handles for a CIDR and deletes filters then classes. `GetCIDRs` scans filter match lines and decodes CIDR values.

## State and Persistence Behavior

State lives in kernel traffic-control qdisc/class/filter configuration on the target interface. The Go struct only stores the interface name and exec handle. Reconciliation reads OS state and repairs missing or unexpected qdisc configuration.

## Dependencies and Integration Points

It depends on the `tc` userspace command, Linux networking, containerd lazy regex helpers and logging, Kubernetes resource quantities/sets, and `k8s.io/utils/exec`. CRI networking code uses it for pod bandwidth annotations.

## Risks and Edge Cases

Parsing `tc` output is fragile across versions; regexes attempt to handle old and new filter output but unexpected formats return errors. `hexCIDR` uses `[]byte(ip)`, so IPv4 may encode as 16-byte mapped addresses depending on `net.ParseCIDR` behavior. Partial failures in `Limit` can leave classes without filters. `ReconcileInterface` assumes enough fields in qdisc output before deleting an unexpected qdisc.

## Test Signals

No direct tests appear in this subset. Behavior is typically covered by CRI networking integration or platform-specific tests that exercise bandwidth annotations.
