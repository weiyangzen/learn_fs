# sources/cloud-native/containerd/docs/user-namespaces/config.json

## Purpose
This JSON file is an OCI runtime configuration fixture/documentation example for running a container with a user namespace.

## Important APIs, Types, and Functions
Key fields include `ociVersion`, process settings, root path, hostname, standard mounts, Linux UID/GID mappings, device deny resources, namespace list including `user`, masked paths, and readonly paths.

## Control Flow
No executable flow. The runtime would interpret this as an OCI spec.

## State and Persistence
The spec references `/tmp/userns-test/rootfs` as rootfs and maps container ID 0 to host ID 65536 for both UID and GID over size 65536.

## Dependencies and Integration Points
Used by user-namespace documentation or manual runtime testing. It follows OCI runtime-spec shape and Linux namespace/mount conventions.

## Risks
It is a static example: host subuid/subgid availability, rootfs existence, cgroup version, and runtime support must match the environment. Formatting has unusual indentation but valid JSON.

## Test Signals
No direct automated tests in this subset; serves as a configuration example.
