# Research: sources/cloud-native/moby/daemon/libnetwork/endpoint_unix_test.go

Purpose: Unix-only integration test for `/etc/hosts` entries generated when a sandbox joins a dual-stack network endpoint. Important test is `TestHostsEntries`.

Control flow: the test sets up an isolated OS network namespace context, creates an IPv4/IPv6-enabled test network with default IPAM pools, creates a temp hosts file, creates a sandbox with that hosts path and hostname `somehost.example.com`, creates and joins an endpoint, then reads the hosts file. Expected content includes default IPv4/IPv6 localhost lines plus the endpoint's IPv4 and IPv6 addresses mapped to FQDN and short hostname. It then deletes the sandbox and asserts controller sandbox cleanup.

State/dependencies: dependencies include default IPAM, `getTestEnv`, netns test utilities, sandbox hosts-file options, and real file IO. Risks covered include host entry ordering and dual-stack address inclusion. Gaps include multi-network deletion behavior and Windows behavior.
