# sources/cloud-native/cri-o/server/sandbox_stop_linux.go

Purpose: Linux implementation for stopping pod sandboxes and cleaning associated resources.

Important APIs and functions: `stopPodSandbox`.

Control flow: locks the sandbox stop mutex, unmounts linked pod logs if configured, tears down network, returns if already stopped, splits timeout between workload containers and infra, stops workload containers in parallel, stops infra, removes managed namespaces, unmounts SHM, notifies NRI, marks stopped, and emits a stopped event for spoofed infra containers where no monitor exit will generate one.

State and persistence: mutates log-link mounts, CNI/hostport state, runtime container states, namespace resources, SHM mounts, NRI state, sandbox stopped flag, and possibly CRI event channel.

Dependencies and integration: linklogs annotations, Kubernetes pod UID label, networkStop, stopContainer, storage/OCI errors, `errgroup`, NRI, evented PLEG.

Risks: network teardown happens before checking `sb.Stopped`, so already-stopped sandboxes can still run network cleanup. Parallel stop failures abort infra cleanup. Timeout partitioning must be kept in sync with CRI request deadline behavior.

Test signals: `sandbox_stop_test.go` covers already-stopped/network-stopped success, missing sandbox idempotency, and empty ID errors; deep parallel stop and log unlink paths are not covered here.
