<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/runconfig/hostconfig.go -->
# sources/cloud-native/moby/daemon/internal/runconfig/hostconfig.go

Purpose: validates network-mode conflicts common to all platforms, focused on container network mode.

Important APIs and types: `validateNetContainerMode`.

Control flow: returns nil unless `NetworkMode` is exactly container mode or container-like. It then requires a target container ID/name and rejects conflicts with hostname, links, DNS, extra hosts, port publishing, publish-all, and exposed ports.

State and persistence: none.

Dependencies and integration: called by platform-specific `validateNetMode` functions in create request validation.

Risks: FIXME notes a network named `container` without colon is not treated as container-mode by one check. Conflict messages are API-visible.

Test signals: no direct tests in this subset for this helper.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/runconfig/hostconfig.go -->
