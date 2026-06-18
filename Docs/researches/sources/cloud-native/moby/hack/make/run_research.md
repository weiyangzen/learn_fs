# sources/cloud-native/moby/hack/make/run

## Purpose
Convenience bundle for running a development daemon with selected flags.

## Important APIs and Types
Uses `DOCKER_GRAPHDRIVER`, `DOCKER_USERLANDPROXY`, `DOCKER_STORAGE_OPTS`, `DOCKER_PORT`, `DELVE_PORT`, `DOCKER_REMAP_ROOT`, `DOCKER_EXPERIMENTAL`, and `DOCKER_ROOTLESS`.

## Control Flow, State, and Persistence
The script resolves `dockerd`, builds a flag list for graphdriver, userland proxy, storage opts, TCP port, Delve debug port, remap, experimental, and rootless mode. It may wrap the daemon with Delve, choose rootless helpers, and finally exec/run the daemon.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on a built `dockerd`, optional Delve, and rootless prerequisites. It creates daemon runtime state and listens on configured sockets/ports. Risks include exposing TCP daemon ports, debug server exposure, and rootless setup drift. Manual developer use is the main signal.
