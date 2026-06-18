# Research: sources/cloud-native/moby/daemon/cluster/executor/container/controller.go

## sources/cloud-native/moby/daemon/cluster/executor/container/controller.go

Purpose: implements SwarmKit `exec.Controller` for Docker container tasks. The `controller` owns task lifecycle orchestration through a `containerAdapter`: prepare, start, wait, log streaming, shutdown, terminate, removal, status, and close.

Important APIs are `newController`, `Task`, `ContainerStatus`, `PortStatus`, `Prepare`, `Start`, `Wait`, `Shutdown`, `Terminate`, `Remove`, `Logs`, `Close`, `parseContainerStatus`, `parsePortStatus`, `parsePortMap`, `exitError`, and `checkHealth`. `Prepare` waits for node network attachments and cluster volumes, creates networks and volumes, optionally pulls the image asynchronously, handles pull cancellation/re-entry, and creates the container. `Start` refuses already-started containers, retries missing-network failures by recreating networks, and activates service bindings immediately for containers without healthchecks or after healthy events.

State lives in controller fields: `closed`, `err`, `pulled`, `cancelPull`, and `pullErr`. Shutdown and removal cancel any in-flight pull, deactivate service bindings, wait a gossip convergence delay, stop/remove containers, and clean managed networks. `Wait` races container exit status with health events to annotate non-zero exit errors with `ErrContainerUnhealthy` when known. Logs use a 10 MB/s token bucket and publish SwarmKit log messages with node/service/task context.

Dependencies include containerd errdefs, Engine event/container/network types, libnetwork errors, SwarmKit exec/log APIs, gogo protobuf timestamps, and `golang.org/x/time/rate`. Integration points are the adapter backend, daemon event stream, SwarmKit agent status reporting, service binding activation, and log subscription path.

Risks include event-channel reads that assume the channel keeps yielding, races between inspect and start, intentional background pull context not tied to task context, fixed waits for node attachments/cluster volumes/gossip convergence, health activation depending on event ordering, and log streams blocking if publisher context is not managed correctly. Tests in this subset cover health-event detection and mount/controller creation, but lifecycle integration mostly depends on higher-level daemon/swarm tests.
