# sources/cloud-native/cri-o/cmd/crio/main.go

Purpose: CRI-O daemon entrypoint. It defines CLI setup, logging, profiling, config validation, server construction, CRI registration, readiness notification, signal handling, and graceful shutdown.

Important APIs and control flow: `writeCrioGoroutineStacks` writes a timestamped stack dump to temp. `catchShutdown` subscribes to SIGINT, SIGTERM, SIGHUP, SIGUSR1, SIGUSR2, and SIGPIPE; SIGUSR1 dumps stacks, SIGUSR2 forces GC, SIGPIPE is ignored, and termination gracefully shuts down tracing, gRPC, HTTP, streaming server, monitors, and main server. `main` initializes klog shim and reexec, builds a urfave/cli app from `criocli`, sorts flags/commands, merges config in `Before`, sets log formatting/hooks/filter/output, and in `Action` handles CPU/HTTP profiling, rejects extra args, checks mount namespace status, validates config, logs flags/config, listens on the Unix socket, optionally initializes OpenTelemetry, creates the gRPC server with interceptors and message-size limits, creates `server.New`, writes temporary and persistent version files, manages clean-shutdown marker files, sets default runtime metrics, garbage-collects storage, registers CRI runtime/image services, notifies systemd, starts exit monitors and hook monitors, splits one listener into gRPC and HTTP via cmux, waits for server/monitor closure, shuts down, and optionally writes a heap profile.

State and persistence: writes log files, profile files, version files, clean-shutdown support files, Unix socket permissions, and storage GC side effects.

Dependencies and integration: integrates CLI/config packages, server package, Kubernetes CRI API, gRPC, cmux, OpenTelemetry, logrus hooks, system signals, kubensmnt, storage, metrics, and systemd notification.

Risks: multiple goroutines coordinate shutdown; missed channel closure can hang. `logrus.Fatal` exits immediately on several startup failures. Socket chmod assumes filesystem permissions are applicable. Clean-shutdown marker logic must remain compatible with `crio wipe`.

Test signals: unit tests likely cover subpackages; end-to-end CI validates daemon startup, CRI service behavior, signal/shutdown paths, generated docs/completions, and profile/status commands.
