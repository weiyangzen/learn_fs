<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portmapper/proxy_linux.go -->
## sources/cloud-native/moby/daemon/libnetwork/portmapper/proxy_linux.go

Purpose: starts and stops the Linux `docker-proxy` userland proxy for a port binding.

Important APIs/functions: `StartProxy(pb types.PortBinding, proxyPath string, listenSock *os.File)` returns a stop function. It builds proxy arguments, optionally passes `-use-listen-fd`, and uses an extra pipe for startup status.

Control flow: validates proxy path, creates a pipe, configures `exec.Cmd` with `Pdeathsig`, rootless `nsenter` wrapping if needed, starts the proxy on a locked OS thread, waits for startup status or a 16-second timeout, then returns a stop function that sends interrupt and waits. If an old proxy cannot handle passed listen fd, startup error is made explicit.

State and persistence: owns a child process and pipe/file descriptors. Stop state is tracked by `atomic.Bool`.

Dependencies and integration points: integrates with rootless detached netns, Linux process death signaling, and NAT port bindings that pass pre-bound sockets from `OSAllocator`.

Risks and test signals: thread locking is critical because `Pdeathsig` is tied to the creating thread. Startup pipe protocol and proxy binary version mismatch are operational risks. Tests are not in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portmapper/proxy_linux.go -->
