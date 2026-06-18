# Research: sources/cloud-native/buildkit/cmd/buildkitd/config/gcpolicy_test.go

Purpose: validates that default GC policy filters remain compatible with containerd-style filter parsing and target the intended cache record types.

Important function and flow: `TestDefaultGCPolicyFiltersMatch` builds default policies with a 1 TB disk stat, parses the first rule's filters, adapts selected `client.UsageRecordType` values into filter fields, and asserts local source, exec cache mount, and git checkout records match while regular cache does not.

State and dependencies: no persistence; it depends on containerd filters, BuildKit client usage record constants, disk stats, and testify assertions.

Risks and test signals: this protects the most subtle part of the default policy, where filter strings must match worker usage record typing. It does not verify byte thresholds, policy ordering beyond first-rule selection, or OS-specific percentage constants.
