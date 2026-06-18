<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/hosts_test.go -->
# sources/cloud-native/moby/daemon/hosts_test.go

Purpose: unit tests for converting legacy Docker registry mirrors into containerd registry host entries.

Important APIs and control flow: `TestMirrorsToHosts` builds a default Docker Hub host and checks `mirrorsToRegistryHosts` for HTTPS, HTTP, bare host, trailing slash, custom base path, `/v2`, and embedded `/v2/base` inputs. `testRegistryHost` is a compact fixture constructor.

State and persistence: no persisted state. Tests are table-driven and compare pure values.

Dependencies and integration: uses containerd `docker.HostCapabilities` plus `gotest.tools` assertions. It validates behavior expected by `Daemon.mergeLegacyConfig`.

Risks: tests focus on mirror conversion only, not TLS certificate loading or insecure transport mutation. The table encodes legacy `/v2` path quirks, so intentional behavior changes require updating expected paths carefully.

Test signals: direct coverage for pull/resolve/referrers-only mirror capabilities and preservation of the default registry host as the fallback entry.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/hosts_test.go -->
