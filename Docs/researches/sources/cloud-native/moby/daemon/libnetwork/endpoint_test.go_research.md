# Research: sources/cloud-native/moby/daemon/libnetwork/endpoint_test.go

Purpose: tests endpoint sorting by network type for DNS/service name resolution priority. Important test is `TestSortByNetworkType`.

Control flow: the test creates local, dynamic overlay-like, and ingress networks, wraps each in an endpoint, sorts using `ByNetworkType`, and compares the endpoint names to the expected ordering: dynamic networks first, ingress next, local networks last. It uses `sort.Sort`, so equal categories may preserve no guaranteed stable order beyond this sample.

State/dependencies: no persistence or external network driver state is involved; the test directly sets `Network.dynamic` and `Network.ingress` fields. Integration point is `Sandbox.ResolveName` behavior in swarm mode, where endpoints attached to user overlay, ingress, and local gateway networks should prefer user overlay VIP/IPs. Risk covered is priority regression; gaps include stable sorting behavior, nil network handling, and mixed service aliases.
