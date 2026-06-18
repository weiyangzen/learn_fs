# Research: sources/cloud-native/moby/daemon/cluster/networks.go

## sources/cloud-native/moby/daemon/cluster/networks.go

Purpose: implements cluster-managed network inspection, listing, creation/removal, service network ID population, and attach/detach coordination for swarm network attachments.

Important APIs: `GetNetworks`, `GetNetworkSummaries`, `listNetworks`, `GetNetwork`, `GetNetworksByName`, `UpdateAttachment`, `WaitForDetachment`, `AttachNetwork`, `DetachNetwork`, `CreateNetwork`, `RemoveNetwork`, and `populateNetworkID`. Listing fetches from SwarmKit and applies daemon-side network filter semantics because SwarmKit filters are more limited. Optional status is requested through `netextra.GetNetworkExtraOptions` appdata. Attachment control uses the cluster `attachers` map with wait channels to bridge manager resource allocation and local network config delivery.

State includes remote SwarmKit networks and local `Cluster.attachers` entries keyed by target/container ID. Attach flow stores channels, requests allocation from the agent resource allocator, waits for `UpdateAttachment`, caches the returned `NetworkingConfig`, and releases allocation on timeout. Detach flow wakes waiters and calls `DetachNetwork`.

Dependencies include Engine network types, cluster convert/netextra packages, daemon network filters, SwarmKit control and agent resource allocator APIs, and daemon backend network lookup. Risks include channel deadlocks, timeout cleanup failures, duplicate attach notices, predefined network ID translation, and mismatch between Engine substring filter behavior and SwarmKit exact/prefix filters. Tests are indirect.
