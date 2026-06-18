# Research: sources/cloud-native/nydus-snapshotter/pkg/metrics/data/auth.go

This file declares Prometheus metrics for credential renewal behavior. `CredentialRenewals` is a counter vector labeled by image ref and result, intended to count renewal attempts as success or failure. `CredentialStoreEntries` is a gauge vector labeled by image ref, intended to show how many credentials are currently tracked in the renewal store.

There is no control flow or persistence in this file. The metric objects are registered by `pkg/metrics/registry/registry.go` and updated by auth/credential renewal code elsewhere. The labels reuse shared label-name constants from `metrics/data/labels.go`.

Risks are mostly integration-level: label cardinality can grow with image references, callers must use consistent result values, and gauges must be maintained when credentials expire or are deleted. There are no tests in this subset that assert registration or update behavior for these metrics.
