# sources/cloud-native/moby/daemon/archive.go

## Purpose
Provides public daemon methods for statting, archiving, and extracting paths in container filesystems with consistent error translation.

## APIs, Types, And Functions
The methods are `Daemon.ContainerStatPath`, `Daemon.ContainerArchivePath`, and `Daemon.ContainerExtractToDir`. They use `GetContainer`, platform-specific helpers, container `PathStat`, `io.Reader`/`ReadCloser`, container-file not-found errors, and Moby/containerd errdefs.

## Control Flow, State, And Integration
Each method resolves the container, delegates to lower-level filesystem helpers, maps `os.IsNotExist` to container-aware not-found errors, preserves invalid-argument errors, and wraps other failures as system errors. Extraction can mutate container filesystem state; stat and archive read it.

## Risks And Test Signals
Risks include incorrect error classification, path traversal or symlink behavior in lower helpers, archive stream lifetime, and destructive extraction. Integration is with Docker `cp`, archive API endpoints, event logging, and container filesystem mounts.
