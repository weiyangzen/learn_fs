# sources/cloud-native/moby/daemon/start_linux.go

## Purpose
`start_linux.go` performs Linux-specific initialization after a containerd task is created but before it starts.

## Important APIs, Types, And Functions
`initializeCreatedTask` receives daemon config, task, container, and OCI spec. It sets the libnetwork sandbox key to `/proc/<pid>/ns/net` when the runtime created a new network namespace, then allocates network resources inside the daemon network namespace.

## Control Flow
If networking is disabled, it returns. Otherwise it checks the OCI spec network namespace; when the namespace path is empty, it fetches the sandbox by container ID and sets its key from the task PID. It then calls `allocateNetwork` through `runInNetNS`.

## State And Persistence
Updates libnetwork sandbox namespace key and allocates network endpoint state for the running container.

## Dependencies And Integration Points
Integrates OCI namespace inspection, libcontainerd task PID, daemon network controller, `runInNetNS`, and daemon networking allocation.

## Risks
Failure after task creation but before task start must propagate so `containerStart` rollback deletes task/container and networking. Namespace-key correctness is required for network operations and stats.

## Test Signals
Linux container start/network integration tests cover this path.
