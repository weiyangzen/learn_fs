# sources/cloud-native/moby/daemon/cluster/executor/container/adapter.go

## Purpose
Implements the swarm executor's container adapter, translating swarmkit task operations into Docker daemon container, image, network, volume, event, and log backend calls.

## Important APIs, Types, And Functions
Defines `containerAdapter`, `newContainerAdapter`, and methods `pullImage`, `waitNodeAttachments`, `createNetworks`, `removeNetworks`, `networkAttach`, `waitForDetach`, `create`, `checkMounts`, `start`, `inspect`, `events`, `wait`, `shutdown`, `terminate`, `remove`, `createVolumes`, `waitClusterVolumes`, `activateServiceBinding`, `deactivateServiceBinding`, and `logs`.

## Control Flow
Image pull skips digest IDs and already-present canonical references, decodes registry auth, streams daemon pull JSON, and rate-limits progress logs. Network setup creates managed networks, ignores already-existing/predefined errors, waits for overlay node attachments by polling the daemon attachment store, and updates/detaches unmanaged attachments. Container creation normalizes default network mode, creates the container, stores dependencies, secrets/config refs, and service config. Runtime methods start, stop, kill, remove, wait, inspect, stream events, create plugin volumes, wait for cluster volume paths, and translate log subscription options.

## State And Persistence
Adapter holds backends, task-derived `containerConfig`, and dependency getter. Persistent effects are delegated to daemon state: images, containers, networks, volumes, service binding, and attachment stores.

## Dependencies And Integration Points
Central executor bridge among swarmkit agent `exec`, daemon backend interfaces, image backend, volume backend, libnetwork, container API, registry auth, and Docker event/log APIs.

## Risks And Test Signals
`waitClusterVolumes` busy-spins until context cancellation or path availability. Bind mount validation differs from normal container API by requiring existing host paths. Pull progress depends on daemon JSON stream format. `adapter_test.go` covers overlay attachment waiting; broader executor tests should cover pull/create/log/shutdown paths.
