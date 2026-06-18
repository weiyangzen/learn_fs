# sources/distributed-fs/beegfs-go/watch/Dockerfile

## Purpose

This Dockerfile packages the `beegfs-watch` binary into a minimal container image. It uses `gcr.io/distroless/static:latest`, copies the prebuilt binary to `/beegfs-watch`, and sets that binary as the entrypoint.

## Important APIs, Types, And Functions

There is no application code here. The operational contract is `COPY beegfs-watch /beegfs-watch` followed by `ENTRYPOINT ["/beegfs-watch"]`. A commented `USER 1000` documents a desired non-root posture that is not enabled because the event log Unix socket may be bind-mounted with permissions requiring root.

## Control Flow

Build-time flow is a single-stage image assembly; runtime flow is direct execution of `/beegfs-watch` with all configuration expected through flags, environment variables, or mounted config files handled by the Go binary.

## State And Persistence

The image contains only the binary. Runtime state, certificates, authentication files, config files, log files, and the BeeGFS event socket must be provided by the container environment through bind mounts, secrets, or stdout/stderr logging.

## Dependencies And Integration Points

It depends on an externally built static `beegfs-watch` binary in the Docker build context and on the distroless static base. It integrates with Kubernetes or container runtimes through mounts for `/etc/beegfs`, `/var/log/beegfs`, and the configured `sysFileEventLogTarget` equivalent.

## Risks And Test Signals

Using `latest` makes the base image mutable and can reduce reproducibility. Running as root broadens container privilege, although the comment explains why that may be needed. There are no local tests; validation should include image build, binary startup, config/cert mount access, and ability to open the Unix packet socket.
